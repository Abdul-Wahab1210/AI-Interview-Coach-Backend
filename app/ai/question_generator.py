import json
from app.ai.ollama_client import ollama_client
from app.config import settings


def generate_question(role: str, difficulty: str, previous_topics: list[str] | None = None) -> dict:
    system_prompt = "You are a senior technical interviewer. Return only valid JSON."

    topics_str = ", ".join(previous_topics) if previous_topics else "None"

    prompt = f"""Generate one interview question.

Role: {role}
Difficulty: {difficulty}
Previous topics already asked: {topics_str}

Rules:
- Ask only one question.
- The question should be realistic and specific.
- Do not include the answer.
- Avoid repeating previous topics.
- Make it suitable for a real technical interview.

Return only valid JSON:
{{
  "question": "...",
  "topic": "...",
  "difficulty": "{difficulty}",
  "expected_concepts": ["...", "..."]
}}"""

    raw = ollama_client.generate(
        prompt=prompt,
        model=settings.OLLAMA_QUESTION_MODEL,
        system_prompt=system_prompt,
        temperature=0.8,
        max_tokens=1024,
    )

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "question": f"Explain a key concept in {role}.",
            "topic": "general",
            "difficulty": difficulty,
            "expected_concepts": [],
        }
