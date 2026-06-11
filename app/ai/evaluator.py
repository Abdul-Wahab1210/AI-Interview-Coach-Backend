import json
from app.ai.ollama_client import ollama_client
from app.config import settings


def evaluate_answer(role: str, difficulty: str, question: str, answer: str) -> dict:
    system_prompt = "You are an expert technical interviewer. Return only valid JSON, no other text."

    prompt = f"""Evaluate the candidate's answer.

Interview Role: {role}
Difficulty: {difficulty}

Question:
{question}

Candidate Answer:
{answer}

Evaluate using these criteria:
1. Correctness (0-10)
2. Completeness (0-10)
3. Technical depth (0-10)
4. Clarity (0-10)
5. Practical understanding (0-10)

Return only valid JSON with this exact structure:
{{
  "score": 0-10,
  "correctness": 0-10,
  "completeness": 0-10,
  "depth": 0-10,
  "clarity": 0-10,
  "feedback": "...",
  "ideal_answer": "...",
  "missing_points": ["...", "..."],
  "follow_up_question": "..."
}}"""

    raw = ollama_client.generate(
        prompt=prompt,
        model=settings.OLLAMA_EVALUATION_MODEL,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=2048,
    )

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "score": 0,
            "correctness": 0,
            "completeness": 0,
            "depth": 0,
            "clarity": 0,
            "feedback": "Failed to parse evaluation.",
            "ideal_answer": "",
            "missing_points": [],
            "follow_up_question": "Could you elaborate on that?",
        }
