import json
from sqlalchemy.orm import Session

from app.database.models import (
    InterviewSession,
    InterviewQuestion,
    UserAnswer,
    Evaluation,
    SessionStatus,
)
from app.interviews.question_bank import get_questions_for_role
from app.ai.evaluator import evaluate_answer
from app.ai.question_generator import generate_question


def start_session(
    db: Session,
    user_id: int,
    role: str,
    difficulty: str,
    num_questions: int = 5,
) -> InterviewSession:
    session = InterviewSession(
        user_id=user_id,
        role=role,
        difficulty=difficulty,
        status=SessionStatus.IN_PROGRESS.value,
    )
    db.add(session)
    db.flush()

    questions = get_questions_for_role(role, difficulty)
    selected = questions[:num_questions]

    for text in selected:
        q = InterviewQuestion(
            session_id=session.id,
            question_text=text,
            topic=role,
            difficulty=difficulty,
        )
        db.add(q)

    db.commit()
    db.refresh(session)
    return session


def submit_answer(
    db: Session,
    session_id: int,
    question_id: int,
    answer_text: str,
    transcript_source: str = "typed",
) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()

    if not session or not question:
        raise ValueError("Session or question not found")

    answer = UserAnswer(
        session_id=session_id,
        question_id=question_id,
        answer_text=answer_text,
        transcript_source=transcript_source,
    )
    db.add(answer)
    db.flush()

    eval_result = evaluate_answer(
        role=session.role,
        difficulty=session.difficulty,
        question=question.question_text,
        answer=answer_text,
    )

    evaluation = Evaluation(
        answer_id=answer.id,
        score=eval_result.get("score", 0),
        correctness=eval_result.get("correctness", 0),
        completeness=eval_result.get("completeness", 0),
        depth=eval_result.get("depth", 0),
        clarity=eval_result.get("clarity", 0),
        feedback=eval_result.get("feedback", ""),
        ideal_answer=eval_result.get("ideal_answer", ""),
        missing_points=json.dumps(eval_result.get("missing_points", [])),
        follow_up_question=eval_result.get("follow_up_question", ""),
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "answer_id": answer.id,
        "evaluation": {
            "score": evaluation.score,
            "correctness": evaluation.correctness,
            "completeness": evaluation.completeness,
            "depth": evaluation.depth,
            "clarity": evaluation.clarity,
            "feedback": evaluation.feedback,
            "ideal_answer": evaluation.ideal_answer,
            "missing_points": json.loads(evaluation.missing_points or "[]"),
            "follow_up_question": evaluation.follow_up_question,
        },
    }


def finish_session(db: Session, session_id: int) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    evaluations = (
        db.query(Evaluation)
        .join(UserAnswer)
        .filter(UserAnswer.session_id == session_id)
        .all()
    )

    if evaluations:
        weights = {"correctness": 0.35, "completeness": 0.20, "depth": 0.20, "clarity": 0.15}
        total_weight = 0
        weighted_sum = 0

        for ev in evaluations:
            weighted_sum += (
                (ev.correctness or 0) * weights["correctness"]
                + (ev.completeness or 0) * weights["completeness"]
                + (ev.depth or 0) * weights["depth"]
                + (ev.clarity or 0) * weights["clarity"]
            )
            total_weight += sum(weights.values())

        avg = weighted_sum / total_weight if total_weight else 0
        session.overall_score = round(avg * 10, 1)
    else:
        session.overall_score = 0

    session.status = SessionStatus.COMPLETED.value
    session.ended_at = __import__("datetime").datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session
