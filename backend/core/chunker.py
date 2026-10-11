import re
from typing import List, Dict

def chunk_pages(pages: List[Dict], chunk_size: int = 500, overlap: int = 80) -> List[Dict]:
    chunks = []
    chunk_id = 1

    for item in pages:
        page_no = item["page"]
        text = item["text"]
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        current_section = "General Clinical Guideline"
        if lines:
            first_line = lines[0]
            if len(first_line) < 60 and not first_line.endswith("."):
                current_section = first_line

        words = text.split()
        if not words:
            continue

        step = max(1, chunk_size - overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()

            if len(chunk_text) < 40:
                continue

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "page_start": page_no,
                "page_end": page_no,
                "section": current_section,
                "source": "stg.pdf"
            })
            chunk_id += 1

    return chunks
