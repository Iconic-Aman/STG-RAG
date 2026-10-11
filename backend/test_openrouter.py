import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from core.config import settings
from core.generator import call_openrouter, generate_answer
from core.embedder import embed_query
from core.vector_store import search_chunks

def test_simplest_openrouter():
    print("Testing OpenRouter connectivity...")
    print(f"Model: {settings.openrouter_model}")
    print(f"Base URL: {settings.openrouter_base_url}")
    print(f"Key loaded: {'Yes' if settings.openrouter_api_key else 'No'}")

    try:
        reply = call_openrouter(
            system_prompt="You are a helpful medical assistant.",
            user_prompt="Hello! In one short sentence, what is rational use of medicine?"
        )
        print("\n=== DIRECT OPENROUTER RESPONSE ===")
        print(reply)
        print("===================================\n")
    except Exception as e:
        print(f"Simple call error: {e}")
        return

    print("Testing End-to-End RAG retrieval + OpenRouter answering from Qdrant...")
    question = "What are the advantages of Essential Medicines?"
    q_vec = embed_query(question)
    chunks = search_chunks(query_vector=q_vec, top_k=3)
    print(f"Retrieved {len(chunks)} chunks from Qdrant.")
    for idx, c in enumerate(chunks, 1):
        print(f"[{idx}] Page: {c.get('page')}, Score: {c.get('score')}")

    rag_answer = generate_answer(question, chunks)
    print("\n=== RAG ANSWER WITH CITATIONS ===")
    print(rag_answer)
    print("===================================\n")

if __name__ == "__main__":
    test_simplest_openrouter()
