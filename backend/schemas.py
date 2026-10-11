from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    query: str
    top_k: Optional[int] = Field(default=5, ge=1, le=10)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class SourceItem(BaseModel):
    id: int
    page: str
    section: str
    snippet: str
    score: Optional[float] = None

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

class IngestResponse(BaseModel):
    filename: str
    chunks_count: int
    message: str
