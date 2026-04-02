from pydantic import BaseModel
from datetime import datetime

class ScreenResultOut(BaseModel):
    resume_id: int
    match_score: float
    strengths: str
    skill_gaps: str
    suggestions: str

    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    id: int
    question: str
    category: str
    difficulty: str

    class Config:
        from_attributes = True

class ResumeOut(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True