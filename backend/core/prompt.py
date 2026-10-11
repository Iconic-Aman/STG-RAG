from typing import List, Dict

SYSTEM_PROMPT = """You are the Edhac Clinical Assistant for Standard Treatment Guidelines.
Your task is to answer the clinical question strictly using ONLY the provided context snippets.
Rules:
1. Every claim in your answer must cite the corresponding source snippet using [1], [2], etc.
2. If the answer cannot be found in the provided context, respond: "Not found in the guidelines."
3. Do not assume or hallucinate treatments not in the context. Keep answers concise and direct.
"""

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
