from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import engine, Base
from app.auth.routes import public_router as auth_public_router, protected_router as auth_protected_router
from app.interviews.routes import router as interview_router
from app.reports.routes import router as report_router
from app.speech.routes import router as speech_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AI Interview Coach", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_public_router)
app.include_router(auth_protected_router)
app.include_router(interview_router)
app.include_router(report_router)
app.include_router(speech_router)


@app.get("/health")
def health():
    return {"status": "ok"}
