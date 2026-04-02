import httpx
import json

POLLINATIONS_URL = "https://text.pollinations.ai"

async def generate_questions(resume_text: str, jd_text: str) -> list:

    prompt = f"""
You are an expert interview coach.

Based on this resume and job description, generate 12 interview questions.
Return a JSON object with a key "questions" containing an array.
Each item in the array must have exactly these keys:
- question: the interview question string
- category: one of Technical, Behavioural, Role-specific, Skill-gap
- difficulty: one of Easy, Medium, Hard

Resume:
{resume_text}

Job Description:
{jd_text}

Return only valid JSON. No markdown. No explanation.
Example format:
{{"questions": [{{"question": "...", "category": "Technical", "difficulty": "Medium"}}]}}
"""

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            POLLINATIONS_URL,
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "openai",
                "jsonMode": True
            }
        )

    print("RAW QUESTIONS RESPONSE:", response.text)

    try:
        data = json.loads(response.text)

        # Handle all possible shapes AI might return
        if isinstance(data, list):
            questions = data
        elif isinstance(data, dict):
            questions = (
                data.get("questions") or
                data.get("interview_questions") or
                data.get("interviewQuestions") or
                []
            )
        else:
            questions = []

        # Normalize each question
        normalized = []
        for q in questions:
            if isinstance(q, str):
                normalized.append({
                    "question": q,
                    "category": "General",
                    "difficulty": "Medium"
                })
            elif isinstance(q, dict):
                normalized.append({
                    "question": q.get("question") or q.get("text") or str(q),
                    "category": q.get("category") or q.get("type") or "General",
                    "difficulty": q.get("difficulty") or q.get("level") or "Medium"
                })

        return normalized

    except Exception as e:
        print("PARSE ERROR:", e)
        return [{
            "question": "Could not generate questions. Please try again.",
            "category": "General",
            "difficulty": "Medium"
        }]