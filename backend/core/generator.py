from typing import List, Dict
from backend.core.config import settings
from backend.core.prompt import SYSTEM_PROMPT, build_prompt

def generate_answer(question: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "Not found in the guidelines."

    prompt_content = build_prompt(question, chunks)

    if settings.groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content},
                ],
                temperature=0.0,
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            pass

    # Grounded fallback if no LLM key is configured yet
    top_chunk = chunks[0]
    return f"According to the guidelines: {top_chunk['text'][:350]}... [1]"
