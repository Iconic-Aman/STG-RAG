import json
import httpx
from typing import List, Dict
try:
    from core.config import settings
    from core.prompt import SYSTEM_PROMPT, build_prompt
except ImportError:
    from backend.core.config import settings
    from backend.core.prompt import SYSTEM_PROMPT, build_prompt

def call_openrouter(system_prompt: str, user_prompt: str) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.api_base_url,
        "X-Title": "Edhac Clinical Assistant",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
    }

    with httpx.Client(timeout=30.0) as client:
        res = client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()

def generate_answer(question: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "Not found in the guidelines."

    prompt_content = build_prompt(question, chunks)

    # 1. OpenRouter (Primary configured provider)
    if settings.openrouter_api_key:
        try:
            return call_openrouter(SYSTEM_PROMPT, prompt_content)
        except Exception as e:
            print(f"OpenRouter call failed: {e}")

    # 2. Groq fallback
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
        except Exception as e:
            print(f"Groq fallback failed: {e}")

    # 3. Grounded snippet fallback if API fails
    top_chunk = chunks[0]
    return f"According to the guidelines: {top_chunk['text'][:300]}... [1]"
