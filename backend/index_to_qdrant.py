import json
import time
from pathlib import Path
from core.config import settings
from core.embedder import embed_texts
from core.vector_store import upsert_chunks, get_qdrant_client

def index_chunks_to_qdrant(json_path: str, batch_size: int = 32):
    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    total = len(chunks)
    print(f"Loaded {total} chunks from {json_path}")
    print(f"Collection: {settings.qdrant_collection_name}")
    print(f"Embedding Model: {settings.embedding_model_name}")
    print("-" * 50)

    start_total_time = time.time()
    processed = 0

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        batch_count = len(batch)

        batch_start = time.time()
        texts = [c["text"] for c in batch]
        vectors = embed_texts(texts)
        embed_time = time.time() - batch_start

        upsert_start = time.time()
        upsert_chunks(batch, vectors)
        upsert_time = time.time() - upsert_start

        processed += batch_count
        remaining = total - processed
        elapsed = time.time() - start_total_time

        print(
            f"[{processed}/{total}] embedded={processed} | remaining={remaining} | "
            f"batch_time={embed_time + upsert_time:.2f}s (embed: {embed_time:.2f}s, upsert: {upsert_time:.2f}s) | "
            f"elapsed={elapsed:.2f}s"
        )

    total_time = time.time() - start_total_time
    print("-" * 50)
    print(f"Finished: {total} chunks indexed in {total_time:.2f}s (avg: {(total_time/total):.3f}s/chunk)")

    client = get_qdrant_client()
    info = client.get_collection(settings.qdrant_collection_name)
    print(f"Qdrant points count: {info.points_count}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    chunks_file = str(base_dir / "data" / "stg_chunks.json")
    index_chunks_to_qdrant(chunks_file)
