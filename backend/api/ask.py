from fastapi import APIRouter, HTTPException
from backend.schemas import AskRequest, AskResponse, SourceItem
from backend.core.embedder import embed_query
from backend.core.vector_store import search_chunks
from backend.core.generator import generate_answer

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(req: AskRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_vector = embed_query(req.query)
    chunks = search_chunks(query_vector=query_vector, top_k=req.top_k or 5)
    answer = generate_answer(req.query, chunks)

    sources = [
        SourceItem(
            id=idx + 1,
            page=c.get("page", ""),
            section=c.get("section", "General"),
            snippet=c.get("text", "")[:280] + "...",
            score=c.get("score"),
        )
        for idx, c in enumerate(chunks)
    ]

    return AskResponse(answer=answer, sources=sources)
