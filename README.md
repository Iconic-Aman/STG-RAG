# Edhac — Clinical Guidelines RAG System

Grounded clinical question-answering assistant over **Standard Treatment Guidelines (STG)** with page-level citations.

---

## 1. System Overview

- **Knowledge Base**: Standard Treatment Guidelines (`data/stg.pdf`)
- **Total Pages**: 90
- **Total Chunks**: 383
- **Chunk Granularity**: ~100 words per chunk with 30-word sliding overlap
- **Embedding Model**: `BAAI/bge-small-en-v1.5` (384 dimensions)
- **Vector Database**: Qdrant (`edhac_chunks` collection, cosine metric)
- **Backend API**: FastAPI (`POST /ask`, `POST /ingest`, `GET /health`)
- **Frontend UI**: React + Vite (Clinical assistant chat with clickable citations)

---

## 2. Ingestion & Embedding Benchmarks

- **Embedding & Upsert Duration**: 183.74s total
- **Model Warmup & Download**: ~148.82s (first batch)
- **Batch Processing Rate**: ~2.8s per 32 chunks (~0.088s / chunk post-warmup)
- **Total Points in Qdrant**: 383 vectors with page & section metadata

---

## 3. Quickstart

### Prerequisites
- Docker (for Qdrant)
- Python 3.10+ & `uv`
- Node.js 18+

### Step 1: Start Qdrant Vector DB
```powershell
docker compose up -d
```
Dashboard available at: `http://localhost:6333/dashboard`

### Step 2: Run Backend
```powershell
cd backend
uv run uvicorn main:app --reload --port 8000
```
Swagger API docs at: `http://localhost:8000/docs`

### Step 3: Run Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000`

---

## 4. Citation Strategy
- Retrieved chunks are numbered `[1]..[n]` in prompt.
- LLM is instructed to answer strictly from context and tag claims with `[n]`.
- API returns answers alongside source payload (`page`, `section`, `snippet`, `score`).
- UI highlights source card when clicking inline citation badge `[n]`.
