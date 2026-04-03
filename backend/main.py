from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas
from storage import extract_text
from screener import screen_resume
from question_gen import generate_questions
import uuid
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def root():
    return {"message": "HireIQ API is running"}


class UserAuth(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(data: UserAuth, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if user:
        return {"error": "exists"}
    new_user = models.User(username=data.username, password=data.password, token=str(uuid.uuid4()))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"token": new_user.token}


@app.post("/login")
def login(data: UserAuth, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.password == data.password).first()
    if not user:
        return {"error": "invalid"}
    return {"token": user.token}


@app.get("/history")
def history(token: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.token == token).first()
    if not user:
        return {"error": "unauthorized"}
    resumes = db.query(models.Resume).filter(models.Resume.user_id == user.id).all()
    results = []
    for r in resumes:
        scr = db.query(models.ScreenResult).filter(models.ScreenResult.resume_id == r.id).first()
        results.append({
            "filename": r.filename,
            "uploaded": r.uploaded_at,
            "score": scr.match_score if scr else None
        })
    return results


@app.post("/upload-resume")
async def upload_resume(
    token: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    file_bytes = await file.read()
    text = extract_text(file_bytes, file.filename)

    user = db.query(models.User).filter(models.User.token == token).first()
    if not user:
        return {"error": "unauthorized"}
    
    uid = user.id

    resume = models.Resume(user_id=uid, filename=file.filename, content=text)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {"resume_id": resume.id, "filename": resume.filename}


@app.post("/screen", response_model=schemas.ScreenResultOut)
async def screen(
    resume_id: int = Form(...),
    jd_text: str = Form(...),
    db: Session = Depends(database.get_db)
):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()

    result = await screen_resume(resume.content, jd_text)

    screen_result = models.ScreenResult(
        resume_id=resume_id,
        jd_text=jd_text,
        match_score=result["match_score"],
        strengths=result["strengths"],
        skill_gaps=result["skill_gaps"],
        suggestions=result["suggestions"]
    )
    db.add(screen_result)
    db.commit()
    db.refresh(screen_result)

    return screen_result


@app.post("/generate-questions")
async def questions(
    resume_id: int = Form(...),
    jd_text: str = Form(...),
    db: Session = Depends(database.get_db)
):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()

    questions_list = await generate_questions(resume.content, jd_text)

    saved = []
    for q in questions_list:
        item = models.InterviewQuestion(
            resume_id=resume_id,
            question=q["question"],
            category=q["category"],
            difficulty=q["difficulty"]
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        saved.append(item)

    return {
        "questions": [
            {
                "question": item.question,
                "category": item.category,
                "difficulty": item.difficulty
            }
            for item in saved
        ]
    }


@app.get("/history/{resume_id}")
def get_history(resume_id: int, db: Session = Depends(database.get_db)):
    results = db.query(models.ScreenResult).filter(
        models.ScreenResult.resume_id == resume_id
    ).all()

    questions = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.resume_id == resume_id
    ).all()

    return {"screen_results": results, "questions": questions}