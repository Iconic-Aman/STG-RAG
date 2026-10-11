# STG-RAG — Design & Architecture

> Demo RAG system over **Standard Treatment Guidelines** (100 pages). Ask a clinical question → get a grounded answer with page-level citations. Vector store: **Qdrant**.

> ⚠️ **Demo scope.** Single document, single collection, no auth, no multi-tenancy. Not for real clinical use.

---

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph CLIENT["🖥️ Client"]
        UI["React.js\nChat UI"]
        CITE["Citation Panel\nSource + Page + Snippet"]
        UI --> CITE
    end

    subgraph API["🌐 API Layer"]
        FA["FastAPI\n/ingest  /ask"]
    end

    subgraph INGEST["📥 Ingestion Pipeline — run once"]
        PDF["STG PDF\n100 pages"]
        PARSE["PyMuPDF\nText + Page No."]
        CLEAN["Cleaner\nHeaders / Footers"]
        CHUNK["Chunker\n~500 tokens, 80 overlap"]
        PDF --> PARSE --> CLEAN --> CHUNK
    end

    subgraph RETRIEVAL["🔎 Query Pipeline"]
        QEMB["Query Embedding"]
        SEARCH["Qdrant Search\nTop-K = 5, cosine"]
        PROMPT["Prompt Builder\nContext + Citation IDs"]
        LLM["LLM\nAnswer + Cite"]
        QEMB --> SEARCH --> PROMPT --> LLM
    end

    subgraph MODELS["🧠 Models"]
        EMB["Embedding Model\nbge-small or OpenAI small"]
        GEN["Generation Model\nClaude / GPT"]
    end

    subgraph STORE["🗄️ Data Layer"]
        QD["Qdrant\nVectors + Payload"]
        PG["Supabase PostgreSQL\nDocs + Chat History + Logs"]
        FILES["Local Disk\nOriginal PDF"]
    end

    CLIENT -->|"REST"| API
    API --> INGEST
    API --> RETRIEVAL
    CHUNK --> EMB
    EMB --> QD
    QEMB --> EMB
    SEARCH --> QD
    LLM --> GEN
    PDF --> FILES
    API -->|"docs, chats, logs"| PG
    RETRIEVAL -->|"answer + sources"| API
```

---

## 2. Data Flow

### 2a. Ingestion (one-time)

```mermaid
sequenceDiagram
    actor Dev
    participant API as FastAPI
    participant Parser as PyMuPDF
    participant Chunker
    participant Emb as Embedding Model
    participant QD as Qdrant
    participant PG as Supabase PG

    Dev->>API: POST /ingest (STG PDF)
    API->>PG: Insert document record (status = processing)
    API->>Parser: Extract text per page
    Parser-->>API: [{page, text}]
    API->>Chunker: Clean + split
    Chunker-->>API: chunks with page, section
    loop Batch of 32 chunks
        API->>Emb: embed(chunk_text)
        Emb-->>API: vectors
        API->>QD: upsert(vector + payload)
    end
    API->>PG: Update document (status = ready, chunk_count)
    API-->>Dev: Done — N chunks indexed
```

### 2b. Question → Answer with Citations

```mermaid
sequenceDiagram
    actor User
    participant UI as Chat UI
    participant API as FastAPI
    participant Emb as Embedding Model
    participant QD as Qdrant
    participant LLM
    participant PG as Supabase PG

    User->>UI: "First-line treatment for uncomplicated malaria?"
    UI->>API: POST /ask
    API->>Emb: embed(question)
    Emb-->>API: query vector
    API->>QD: search top 5
    QD-->>API: chunks + payload + scores
    API->>API: Build prompt with [1] [2] [3] labelled context
    API->>LLM: Answer ONLY from context, cite as [n]
    LLM-->>API: Answer text with [n] markers
    API->>API: Map [n] to page / section / snippet
    API->>PG: Save question, answer, sources
    API-->>UI: answer + sources[]
    UI-->>User: Answer + clickable citations
```

---

## 3. Directory Structure

```
stg-rag/
├── data/
│   └── stg.pdf                  # 100-page subset
│
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── api/
│   │   ├── ingest.py            # POST /ingest
│   │   └── ask.py               # POST /ask
│   ├── db/
│   │   ├── session.py           # Supabase Postgres connection
│   │   └── models.py            # SQLAlchemy tables
│   ├── core/
│   │   ├── config.py            # env, model names, top_k
│   │   ├── parser.py            # PDF → pages
│   │   ├── chunker.py           # pages → chunks
│   │   ├── embedder.py          # text → vector
│   │   ├── vector_store.py      # Qdrant client wrapper
│   │   ├── retriever.py         # query → top-k chunks
│   │   ├── prompt.py            # context + citation prompt
│   │   └── generator.py         # LLM call + citation mapping
│   └── schemas.py               # Pydantic request/response
│
├── frontend/                    # React.js app
│   └── src/
│       ├── components/          # ChatWindow, CitationPanel
│       ├── pages/               # Chat
│       └── api.js               # calls FastAPI
├── docker-compose.yml           # qdrant + backend
└── .env.example
```

---

## 4. Tech Stack Reference

| Layer | Tech | Role | Notes |
|-------|------|------|-------|
| **UI** | React.js ✓ | Chat + citation panel | Vite for setup |
| **API** | FastAPI ✓ | `/ingest`, `/ask` | Python, async |
| **PDF parsing** | PyMuPDF ✓ | Text + page numbers | Alt: pdfplumber (better tables) |
| **Chunking** | Custom / LangChain splitter | ~500 tokens, 80 overlap | Split on headings first if possible |
| **Embeddings** | `bge-small-en-v1.5` ✓ | 384-dim, runs locally, free | Alt: OpenAI `text-embedding-3-small` |
| **Vector DB** | **Qdrant** ✓ | Vector search + payload filters | Docker, port 6333 |
| **Relational DB** | **Supabase PostgreSQL** ✓ | Document records, chat history, query logs | Managed Postgres, free tier |
| **ORM** | SQLAlchemy | DB access from FastAPI | Alt: supabase-py client |
| **LLM** | Claude / GPT | Grounded answer generation | Temperature 0 |
| **Orchestration** | Plain Python ✓ | Retrieve → prompt → generate | LangChain optional, not needed |
| **Infra** | Docker Compose | Qdrant + backend locally; Supabase is hosted | Deploy later if needed |

---

## 5. Qdrant Collection Design

One collection: `stg_chunks`

```
vector:   384-dim, cosine distance

payload:
  chunk_id     : int
  text         : str          -- the chunk text (shown as snippet)
  page_start   : int          -- for citation
  page_end     : int
  section      : str          -- nearest heading, e.g. "Malaria"
  source       : str          -- "stg.pdf"
```

Payload indexes on `section` and `page_start` so filters stay fast.

---

## 6. Supabase PostgreSQL Schema (Core Tables)

Postgres holds app data. Qdrant holds only vectors and chunk payload.

```sql
documents (
  id uuid PK, name, file_path,
  page_count int, chunk_count int,
  status,               -- processing | ready | failed
  created_at
)

chat_sessions (
  id uuid PK, created_at
)

messages (
  id uuid PK, session_id FK,
  role,                 -- user | assistant
  content text,
  sources jsonb,        -- [{id, page, section, snippet, score}]
  latency_ms int,
  created_at
)
```

---

## 7. Citation Strategy

1. Every chunk carries `page_start`, `page_end`, `section` from ingestion.
2. Retrieved chunks are numbered `[1]..[5]` in the prompt.
3. LLM is told: *answer only from the context, cite each claim as `[n]`, say "not found in the guidelines" if unsure.*
4. Backend maps `[n]` back to the chunk and returns:

```json
{
  "answer": "Artemether-lumefantrine is the first-line ... [1]",
  "sources": [
    { "id": 1, "page": "42", "section": "Malaria", "snippet": "...", "score": 0.81 }
  ]
}
```

5. UI shows the answer with clickable `[n]` → opens source snippet + page.

---

## 8. Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Vector DB | Qdrant | Fast setup in Docker, payload filtering, good Python client |
| Frontend | React.js | Chat UI with clickable citations |
| App database | Supabase PostgreSQL | Managed Postgres for docs and chat history, no setup |
| Parsing | PyMuPDF | Fast, keeps page numbers, easy for 100 pages |
| Chunk size | ~500 tokens, 80 overlap | Keeps one treatment section together |
| Embeddings | bge-small (local) | Free, no API key, good enough for demo |
| Top-K | 5 | Enough context, low noise |
| Citations | Page + section in payload | Cheap and reliable; no extra model needed |
| Hallucination guard | "Answer only from context" prompt | Simple; refuse when no match |
| Framework | Plain Python | Less moving parts for a demo |

---

## 9. Build Order (demo — ~2 days)

### Phase 1 — Ingestion
- [ ] Run Qdrant via Docker Compose; create Supabase project + tables
- [ ] Parse 100 pages with PyMuPDF (keep page numbers)
- [ ] Chunk + attach page / section metadata
- [ ] Embed and upsert into `stg_chunks`
- [ ] Save document record in Postgres

**Deliverable:** Collection has all chunks; a test search returns relevant text.

### Phase 2 — Query + Citations
- [ ] `/ask` endpoint: embed → search → prompt → LLM
- [ ] Citation mapping `[n]` → page / section / snippet
- [ ] "Not found in guidelines" fallback
- [ ] Save chat messages + sources in Postgres

**Deliverable:** Question returns an answer with correct page citations.

### Phase 3 — UI + Polish
- [ ] React chat UI with citation panel
- [ ] A few sample questions as buttons
- [ ] Small README

**Deliverable:** Working demo you can show end to end.

---

## 10. Later (out of demo scope)

- Hybrid search (BM25 + vector) and a reranker
- Table-aware parsing for dosage tables
- Eval set of 20 Q&A pairs to check retrieval quality
- Auth, multiple documents, streaming responses
