from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
