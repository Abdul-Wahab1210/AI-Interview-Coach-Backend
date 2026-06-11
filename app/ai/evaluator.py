import json
import re
from app.ai.ollama_client import ollama_client
from app.config import settings

STRICTNESS_PROMPTS = {
    "lenient": "Be generous.",
    "moderate": "Be fair.",
    "strict": "Be critical.",
}

STRICTNESS_ADJUSTMENT = {
    "lenient": 0.5,
    "moderate": 0.0,
    "strict": -0.5,
}

WEAK_ANSWER_KEYWORDS = [
    "empty", "irrelevant", "no experience", "no content", "no useful",
    "nothing", "does not answer", "did not answer", "not answering",
    "no information", "does not provide", "no relevant", "completely empty",
]


def _detect_weak_answer(answer: str, feedback: str) -> bool:
    word_count = len(answer.strip().split())
    if word_count < 5:
        return True
    feedback_lower = feedback.lower()
    for kw in WEAK_ANSWER_KEYWORDS:
        if kw in feedback_lower:
            return True
    return False


def _clamp_scores_for_weak_answer(result: dict) -> dict:
    for key in ["correctness", "completeness", "depth", "clarity", "score"]:
        if key in result:
            result[key] = min(result[key] or 0, 3)
    return result


def evaluate_answer(role: str, difficulty: str, question: str, answer: str, strictness: str = "moderate") -> dict:
    strictness_instruction = STRICTNESS_PROMPTS.get(strictness, STRICTNESS_PROMPTS["moderate"])
    adjustment = STRICTNESS_ADJUSTMENT.get(strictness, 0.0)

    system_prompt = "You are an expert technical interviewer. Score honestly. Return only valid JSON."

    prompt = f"""Evaluate this interview answer.

Role: {role}
Difficulty: {difficulty}
Question: {question}
Answer: {answer}

Score each criterion from 0-10 using this rubric:
0-3: Answer is empty, irrelevant, or fundamentally wrong.
4-5: Partial understanding but missing key points.
6-7: Solid answer with minor gaps.
8-9: Strong answer with depth.
10: Exceptional.

CRITICAL: Your numeric scores MUST match your feedback. If the answer is weak or empty, all scores must be 0-3.

Evaluation style: {strictness_instruction}

Return ONLY valid JSON:
{{
  "score": 0,
  "correctness": 0,
  "completeness": 0,
  "depth": 0,
  "clarity": 0,
  "feedback": "Explain what was good/bad and why the scores are what they are.",
  "ideal_answer": "Concise ideal answer.",
  "missing_points": ["point1", "point2"],
  "follow_up_question": "One follow-up question targeting a weak area."
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
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {
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

    if _detect_weak_answer(answer, result.get("feedback", "")):
        result = _clamp_scores_for_weak_answer(result)

    for key in ["correctness", "completeness", "depth", "clarity"]:
        if key in result and result[key] is not None:
            result[key] = round(max(0, min(10, result[key] + adjustment)), 1)

    sub_scores = [
        result.get("correctness", 0) or 0,
        result.get("completeness", 0) or 0,
        result.get("depth", 0) or 0,
        result.get("clarity", 0) or 0,
    ]
    result["score"] = round(sum(sub_scores) / len(sub_scores), 1)

    return result
