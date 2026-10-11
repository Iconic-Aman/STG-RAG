import sys
from pathlib import Path

# Support running directly from inside backend directory or root
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from api.ask import router as ask_router
    from api.ingest import router as ingest_router
except ImportError:
    from backend.api.ask import router as ask_router
    from backend.api.ingest import router as ingest_router

app = FastAPI(
    title="Edhac Clinical Guidelines Assistant API",
    description="Demo RAG system over Standard Treatment Guidelines with page-level citations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)
app.include_router(ingest_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "edhac-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
