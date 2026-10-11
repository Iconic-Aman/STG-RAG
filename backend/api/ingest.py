import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.schemas import IngestResponse
from backend.core.parser import parse_pdf
from backend.core.chunker import chunk_pages
from backend.core.embedder import embed_texts
from backend.core.vector_store import upsert_chunks
from backend.core.config import settings

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    os.makedirs(settings.data_dir, exist_ok=True)
    save_path = os.path.join(settings.data_dir, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = parse_pdf(save_path, max_pages=100)
    if not pages:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks created from PDF")

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)
    upsert_chunks(chunks, vectors)

    return IngestResponse(
        filename=file.filename,
        chunks_count=len(chunks),
        message=f"Successfully indexed {len(chunks)} chunks into vector store"
    )
