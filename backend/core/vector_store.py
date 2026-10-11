from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
try:
    from core.config import settings
except ImportError:
    from backend.core.config import settings

_client: Optional[QdrantClient] = None
_in_memory_chunks: List[Dict] = []

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        try:
            _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=2.0)
            _client.get_collections()
        except Exception:
            _client = QdrantClient(location=":memory:")
    return _client

def init_collection(dim: int = 384):
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection_name not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )

def upsert_chunks(chunks: List[Dict], vectors: List[List[float]]):
    init_collection(len(vectors[0]))
    client = get_qdrant_client()
    points = [
        models.PointStruct(
            id=c["chunk_id"],
            vector=v,
            payload={
                "text": c["text"],
                "page_start": c["page_start"],
                "page_end": c["page_end"],
                "section": c["section"],
                "source": c.get("source", "stg.pdf"),
            },
        )
        for c, v in zip(chunks, vectors)
    ]
    client.upsert(collection_name=settings.qdrant_collection_name, points=points)

def search_chunks(query_vector: List[float], top_k: int = 5) -> List[Dict]:
    init_collection(len(query_vector))
    client = get_qdrant_client()
    hits = client.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    results = []
    for hit in hits:
        payload = hit.payload or {}
        results.append({
            "chunk_id": hit.id,
            "text": payload.get("text", ""),
            "page": str(payload.get("page_start", "")),
            "section": payload.get("section", "Standard Treatment Guidelines"),
            "score": round(hit.score, 4),
        })
    return results
