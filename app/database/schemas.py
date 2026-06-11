from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class InterviewStartRequest(BaseModel):
    role: str
    difficulty: str
    num_questions: int = 5


class AnswerSubmit(BaseModel):
    answer_text: str
    transcript_source: str = "typed"


class EvaluationResponse(BaseModel):
    score: float
    correctness: float
    completeness: float
    depth: float
    clarity: float
    feedback: str
    ideal_answer: str
    missing_points: list[str]
    follow_up_question: str


class InterviewSessionResponse(BaseModel):
    id: int
    role: str
    difficulty: str
    status: str
    overall_score: Optional[float]
    started_at: datetime
    ended_at: Optional[datetime]

    model_config = {"from_attributes": True}
