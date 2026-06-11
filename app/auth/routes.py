import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.database.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth.utils import hash_password, verify_password, create_access_token, get_current_user

logger = logging.getLogger("auth")

public_router = APIRouter(prefix="/auth", tags=["auth"])
protected_router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(get_current_user)])


@public_router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered user: %s (id=%s)", user.email, user.id)
    return user


@public_router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        logger.warning("Login failed: email not found: %s", payload.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        logger.warning("Login failed: wrong password for: %s", payload.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Login OK: %s (id=%s)", user.email, user.id)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@protected_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
