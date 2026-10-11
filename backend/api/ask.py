from fastapi import APIRouter, HTTPException
try:
    from schemas import AskRequest, AskResponse, SourceItem
    from core.prompt import classify_query
    from core.embedder import embed_query
    from core.vector_store import search_chunks
    from core.generator import generate_answer
except ImportError:
    from backend.schemas import AskRequest, AskResponse, SourceItem
    from backend.core.prompt import classify_query
    from backend.core.embedder import embed_query
    from backend.core.vector_store import search_chunks
    from backend.core.generator import generate_answer

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(req: AskRequest):
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    intent = classify_query(query_text)

    # 1. Greeting — no search, no citation cards
    if intent == "GREETING":
        return AskResponse(
            answer="Hello! I am your Standard Treatment Guidelines Assistant. How can I help you with clinical guidelines or healthcare treatments today?",
            sources=[],
        )

    # 2. Off-topic — strictly decline, no search, no citation cards
    if intent == "OFF_TOPIC":
        return AskResponse(
            answer="I don't know anything about this. I only have data about healthcare and clinical treatment guidelines. Do you have any questions related to that?",
            sources=[],
        )

    # 3. Clinical question — vector search + grounded LLM generation
    query_vector = embed_query(query_text)
    chunks = search_chunks(query_vector=query_vector, top_k=req.top_k or 5)
    answer = generate_answer(query_text, chunks)

    # Check if answer wasn't found in guidelines
    if "Not found in the guidelines" in answer:
        sources = []
    else:
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
