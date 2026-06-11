from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import InterviewSession, InterviewQuestion, User
from app.database.schemas import InterviewStartRequest, AnswerSubmit, InterviewSessionResponse
from app.auth.utils import get_current_user
from app.interviews.service import start_session, submit_answer, finish_session

router = APIRouter(prefix="/interviews", tags=["interviews"], dependencies=[Depends(get_current_user)])


@router.post("/start", response_model=dict)
def start(payload: InterviewStartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = start_session(db, user.id, payload.role, payload.difficulty, payload.strictness, payload.num_questions)
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.id).all()
    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "questions": [{"id": q.id, "text": q.question_text, "topic": q.topic} for q in questions],
    }


@router.get("/{session_id}")
def get_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.id).all()
    return {
        "session": InterviewSessionResponse.model_validate(session),
        "questions": [{"id": q.id, "text": q.question_text, "topic": q.topic} for q in questions],
    }


@router.post("/{session_id}/answer")
def submit(session_id: int, payload: AnswerSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    unanswered = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.session_id == session_id,
            ~InterviewQuestion.id.in_(
                db.query(InterviewQuestion.id).join(InterviewQuestion.answer)
            ),
        )
        .first()
    )

    if not unanswered:
        raise HTTPException(status_code=400, detail="All questions answered. Finish the session.")

    try:
        result = submit_answer(db, session_id, unanswered.id, payload.answer_text, payload.transcript_source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.post("/{session_id}/finish")
def finish(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        completed = finish_session(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return InterviewSessionResponse.model_validate(completed)
