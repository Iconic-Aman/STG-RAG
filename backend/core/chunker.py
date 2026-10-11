import re
from typing import List, Dict

def split_text_into_paragraphs(text: str) -> List[str]:
    raw_paras = re.split(r"\n\s*\n+", text)
    cleaned = []
    for p in raw_paras:
        clean_p = " ".join(p.split()).strip()
        if len(clean_p) > 20:
            cleaned.append(clean_p)
    return cleaned

def chunk_pages_by_paragraph(
    pages: List[Dict],
    max_chunk_words: int = 100,
    overlap_words: int = 30,
    source_name: str = "stg.pdf"
) -> List[Dict]:
    chunks = []
    chunk_id = 1
    step = max(1, max_chunk_words - overlap_words)

    for page_item in pages:
        page_no = page_item["page"]
        page_text = page_item["text"]

        lines = [line.strip() for line in page_text.split("\n") if line.strip()]
        page_section = "Standard Treatment Guidelines"
        if lines:
            first_line = lines[0]
            if len(first_line) < 70 and not first_line.endswith("."):
                page_section = first_line

        paragraphs = split_text_into_paragraphs(page_text)

        for para in paragraphs:
            para_words = para.split()
            if not para_words:
                continue

            # Check if this paragraph is a section header
            if len(para_words) <= 7 and not para.endswith("."):
                page_section = para
                continue

            # Slide window over paragraph words: 100 words with 30 words overlap
            if len(para_words) <= max_chunk_words:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": " ".join(para_words),
                    "page_start": page_no,
                    "page_end": page_no,
                    "section": page_section,
                    "source": source_name,
                })
                chunk_id += 1
            else:
                for i in range(0, len(para_words), step):
                    chunk_slice = para_words[i:i + max_chunk_words]
                    if len(chunk_slice) < 15:
                        continue

                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": " ".join(chunk_slice),
                        "page_start": page_no,
                        "page_end": page_no,
                        "section": page_section,
                        "source": source_name,
                    })
                    chunk_id += 1
                    if i + max_chunk_words >= len(para_words):
                        break

    return chunks
