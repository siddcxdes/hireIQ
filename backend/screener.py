import httpx
import json

POLLINATIONS_URL = "https://text.pollinations.ai"

async def screen_resume(resume_text: str, jd_text: str) -> dict:
    
    prompt = f"""
You are an expert resume screener.

Compare this resume against the job description and return a JSON object with exactly these keys:
- match_score: a number between 0 and 100
- strengths: a string listing what matches well
- skill_gaps: a string listing what is missing
- suggestions: a string with specific improvements the candidate should make

Resume:
{resume_text}

Job Description:
{jd_text}

You MUST use exactly these key names: match_score, strengths, skill_gaps, suggestions
Return only valid JSON. No explanation. No markdown. No extra keys.
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

    print("RAW SCREEN RESPONSE:", response.text)

    try:
        data = json.loads(response.text)

        # Normalize keys in case AI returns different names
        normalized = {
            "match_score": data.get("match_score") or data.get("matchScore") or data.get("score") or 0,
            "strengths": data.get("strengths") or data.get("strength") or "N/A",
            "skill_gaps": data.get("skill_gaps") or data.get("skillGaps") or data.get("gaps") or "N/A",
            "suggestions": data.get("suggestions") or data.get("suggestion") or data.get("improvements") or "N/A"
        }
        return normalized

    except Exception as e:
        print("PARSE ERROR:", e)
        return {
            "match_score": 0,
            "strengths": "Could not parse response",
            "skill_gaps": "Could not parse response",
            "suggestions": "Could not parse response"
        }