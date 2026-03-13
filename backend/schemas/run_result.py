from pydantic import BaseModel
from typing import List, Dict, Optional
class Citation(BaseModel):
    doc_id: str
    section: str
    chunk_id: str

class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    section: str
    score: float
    text: str
    metadata: Dict[str, object]

class RunResult(BaseModel):
    question: str
    pipeline_id: str
    answer: str
    citations: List[Citation]
    retrieved: List[RetrievedChunk]
    timings_ms: Dict[str, int]
    notes: Optional[str] = None