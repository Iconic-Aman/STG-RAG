import re
from typing import List, Dict, Optional

GREETING_WORDS = {
    "hi", "hello", "hey", "good morning", "good afternoon",
    "good evening", "greetings", "howdy", "hola", "namaste", "sup"
}

HEALTH_KEYWORDS = [
    "treatment", "medicine", "drug", "dose", "dosage", "clinical", "guideline",
    "fever", "malaria", "symptom", "disease", "patient", "diagnosis", "therapy",
    "syndrome", "emergency", "prescription", "essential", "adverse", "infection",
    "pain", "tablet", "pediatric", "child", "infant", "adult", "cough", "blood"
]

SYSTEM_PROMPT = """You are the Edhac Clinical Assistant for Standard Treatment Guidelines.
Your task is to answer the clinical question strictly using ONLY the provided context snippets.
Rules:
1. Every claim in your answer must cite the corresponding source snippet using [1], [2], etc.
2. If the clinical answer is not found in the provided context, respond: "Not found in the guidelines."
3. Do not assume or hallucinate treatments not in the context. Keep answers concise and direct.
"""

IDENTITY_PHRASES = [
    "what is your name", "whats your name", "what your name",
    "who are you", "what are you", "your name", "tell me your name"
]

def classify_query(query: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", query.strip().lower())
    words = cleaned.split()

    # 1. Check identity / name
    if any(phrase in cleaned for phrase in IDENTITY_PHRASES):
        return "IDENTITY"

    # 2. Check greeting
    if cleaned in GREETING_WORDS or (len(words) <= 2 and any(w in GREETING_WORDS for w in words)):
        return "GREETING"

    # 2. Check health relevance
    is_health = any(k in cleaned for k in HEALTH_KEYWORDS)
    if not is_health and len(words) > 1:
        # Check non-medical common prompts
        off_topic_hints = ["weather", "capital", "movie", "president", "code", "song", "python", "javascript", "sports", "football"]
        if any(h in cleaned for h in off_topic_hints) or len(words) >= 3 and not is_health:
            return "OFF_TOPIC"

    return "CLINICAL"

def build_prompt(question: str, retrieved_chunks: List[Dict]) -> str:
    context_blocks = []
    for idx, c in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"[{idx}] Page {c.get('page')}, Section: {c.get('section')}\n{c.get('text')}"
        )

    context_str = "\n\n".join(context_blocks)
    prompt = f"""CONTEXT:
{context_str}

QUESTION:
{question}

ANSWER:"""
    return prompt
