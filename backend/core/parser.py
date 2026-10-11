import fitz  # PyMuPDF
from typing import List, Dict

def parse_pdf(file_path: str, max_pages: int = 100) -> List[Dict]:
    doc = fitz.open(file_path)
    pages_data = []

    for page_idx in range(min(len(doc), max_pages)):
        page = doc[page_idx]
        text = page.get_text("text").strip()
        if text:
            pages_data.append({
                "page": page_idx + 1,
                "text": text
            })

    doc.close()
    return pages_data
