from sqlalchemy.orm import Session

from app.database.models import Evaluation, UserAnswer, InterviewSession, InterviewQuestion, SessionStatus


def generate_report(db: Session, session_id: int) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    evaluations = (
        db.query(Evaluation)
        .join(UserAnswer)
        .filter(UserAnswer.session_id == session_id)
        .all()
    )

    scores = [e.score for e in evaluations]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    strengths = []
    weaknesses = []
    best = max(evaluations, key=lambda e: e.score) if evaluations else None
    worst = min(evaluations, key=lambda e: e.score) if evaluations else None

    topics_to_revise = set()
    for ev in evaluations:
        if ev.score and ev.score < 6:
            answer = db.query(UserAnswer).filter(UserAnswer.id == ev.answer_id).first()
            if answer:
                q = db.query(InterviewQuestion).filter(InterviewQuestion.id == answer.question_id).first()
                if q and q.topic:
                    topics_to_revise.add(q.topic)
        if ev.score and ev.score >= 8:
            strengths.append(ev.feedback or "Good answer")
        elif ev.score and ev.score < 5:
            weaknesses.append(ev.feedback or "Needs improvement")

    total_score = session.overall_score or (avg_score * 10)

    return {
        "session_id": session.id,
        "overall_score": round(total_score, 1),
        "avg_answer_score": avg_score,
        "total_questions": len(evaluations),
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "best_answer_score": round(best.score, 1) if best else None,
        "worst_answer_score": round(worst.score, 1) if worst else None,
        "topics_to_revise": list(topics_to_revise),
        "recommendation": (
            "Keep practicing! Focus on weak areas."
            if weaknesses
            else "Great job! You're well prepared."
        ),
    }


def get_progress(db: Session, user_id: int) -> dict:
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id, InterviewSession.status == SessionStatus.COMPLETED.value)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )

    if not sessions:
        return {"total_interviews": 0, "average_score": 0, "best_score": 0, "sessions": []}

    scores = [s.overall_score or 0 for s in sessions]

    return {
        "total_interviews": len(sessions),
        "average_score": round(sum(scores) / len(scores), 1),
        "best_score": round(max(scores), 1),
        "worst_score": round(min(scores), 1),
        "sessions": [
            {
                "id": s.id,
                "role": s.role,
                "difficulty": s.difficulty,
                "score": s.overall_score,
                "date": s.started_at.isoformat(),
            }
            for s in sessions
        ],
    }
