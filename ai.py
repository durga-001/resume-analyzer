import os
import json
from openai import OpenAI

# The OpenAI client reads OPENAI_API_KEY from the environment automatically.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_resume(resume_text, user_goal):
    """
    Sends the resume + target role to the LLM and returns a structured,
    goal-aware analysis including an ATS-style match score.
    """
    prompt = f"""
You are a senior technical recruiter and ATS (Applicant Tracking System) evaluator.

Evaluate the resume STRICTLY against the user's target role.

Target role: "{user_goal}"

Rules:
- ats_score: an integer 0-100 representing how well this resume would score
  against an ATS + recruiter screen for the target role (keyword match,
  relevant experience, clarity of impact).
- skills: only skills from the resume that are RELEVANT to the target role.
- missing_skills: important skills/keywords for the target role that are
  missing or weak in the resume.
- roadmap: a short personalized learning plan (3-6 items) to close the gaps
  in missing_skills. Do not repeat skills already present.
- interview_questions: 5 likely interview questions for this role given the
  resume's current strengths and gaps.

Return ONLY valid JSON in exactly this shape, no markdown, no commentary:
{{
  "ats_score": 0,
  "skills": [],
  "missing_skills": [],
  "roadmap": [],
  "interview_questions": []
}}

Resume:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a strict, precise ATS and hiring evaluator. Always return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )

        # NOTE: with the current openai python SDK, `message` is an object,
        # not a dict — use attribute access, not subscripting.
        content = response.choices[0].message.content.strip()

        # Defensive extraction in case the model wraps JSON in extra text.
        start = content.find("{")
        end = content.rfind("}") + 1
        json_str = content[start:end]

        data = json.loads(json_str)

        # Fill in any missing keys defensively so the template never KeyErrors.
        data.setdefault("ats_score", 0)
        data.setdefault("skills", [])
        data.setdefault("missing_skills", [])
        data.setdefault("roadmap", [])
        data.setdefault("interview_questions", [])
        return data

    except Exception as e:
        return {
            "ats_score": 0,
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e),
        }