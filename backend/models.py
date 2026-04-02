from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ScreenResult(Base):
    __tablename__ = "screen_results"

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer)
    jd_text = Column(Text)
    match_score = Column(Float)
    strengths = Column(Text)
    skill_gaps = Column(Text)
    suggestions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer)
    question = Column(Text)
    category = Column(String)
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)