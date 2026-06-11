import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database.db import Base


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="user")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    status = Column(String(20), default=SessionStatus.IN_PROGRESS.value)
    overall_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)
    question_type = Column(String(50), default="text")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("UserAnswer", back_populates="question", uselist=False)


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    transcript_source = Column(String(20), default="typed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="user_answers")
    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("Evaluation", back_populates="answer", uselist=False)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("user_answers.id"), unique=True, nullable=False)
    score = Column(Float, nullable=False)
    correctness = Column(Float, nullable=True)
    completeness = Column(Float, nullable=True)
    depth = Column(Float, nullable=True)
    clarity = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    ideal_answer = Column(Text, nullable=True)
    missing_points = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    answer = relationship("UserAnswer", back_populates="evaluation")
