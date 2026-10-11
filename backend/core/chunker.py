import re
from typing import List, Dict

def split_text_into_paragraphs(text: str) -> List[str]:
    # Split on double line breaks or block boundaries
    raw_paras = re.split(r"\n\s*\n+", text)
    cleaned = []
    for p in raw_paras:
        clean_p = " ".join(p.split()).strip()
        if len(clean_p) > 25:  # Skip tiny noise fragments
            cleaned.append(clean_p)
    return cleaned

def chunk_pages_by_paragraph(
    pages: List[Dict],
    max_chunk_words: int = 400,
    min_chunk_words: int = 50,
    source_name: str = "stg.pdf"
) -> List[Dict]:
    chunks = []
    chunk_id = 1

    for page_item in pages:
        page_no = page_item["page"]
        page_text = page_item["text"]

        # 1. Identify section heading from top of page if present
        lines = [line.strip() for line in page_text.split("\n") if line.strip()]
        page_section = "Standard Treatment Guidelines"
        if lines:
            first_line = lines[0]
            if len(first_line) < 70 and not first_line.endswith("."):
                page_section = first_line

        # 2. Split page into paragraphs
        paragraphs = split_text_into_paragraphs(page_text)

        buffer_words = []
        for para in paragraphs:
            para_words = para.split()

            # Detect section sub-heading inside paragraph
            if len(para_words) <= 7 and not para.endswith("."):
                page_section = para
                continue

            # If adding paragraph exceeds max chunk size, flush buffer
            if len(buffer_words) + len(para_words) > max_chunk_words and len(buffer_words) >= min_chunk_words:
                chunk_text = " ".join(buffer_words)
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "page_start": page_no,
                    "page_end": page_no,
                    "section": page_section,
                    "source": source_name,
                })
                chunk_id += 1
                buffer_words = []

            buffer_words.extend(para_words)

        # Flush remaining words on this page
        if buffer_words:
            chunk_text = " ".join(buffer_words)
            if len(buffer_words) >= 15:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "page_start": page_no,
                    "page_end": page_no,
                    "section": page_section,
                    "source": source_name,
                })
                chunk_id += 1

    return chunks
