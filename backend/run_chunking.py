import json
from pathlib import Path
from core.parser import parse_pdf
from core.chunker import chunk_pages_by_paragraph

def run_chunking_to_json(pdf_path: str, output_json: str, max_pages: int = 100):
    pages = parse_pdf(pdf_path, max_pages=max_pages)
    chunks = chunk_pages_by_paragraph(
        pages,
        max_chunk_words=100,
        overlap_words=30,
        source_name="stg.pdf"
    )

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(pages)} pages.")
    print(f"Generated {len(chunks)} chunks.")
    print(f"Saved to {output_json}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    pdf_file = str(base_dir / "data" / "stg.pdf")
    out_file = str(base_dir / "data" / "stg_chunks.json")
    run_chunking_to_json(pdf_file, out_file, max_pages=100)
