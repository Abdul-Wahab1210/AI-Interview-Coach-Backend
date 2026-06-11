from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import InterviewSession, User
from app.auth.utils import get_current_user
from app.reports.report_generator import generate_report, get_progress

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


@router.get("/{session_id}")
def session_report(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        return generate_report(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/user/progress")
def user_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_progress(db, user.id)
