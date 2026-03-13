from typing import Any, Dict

from pydantic import BaseModel


class Chunk(BaseModel):
    """
    A single chunk of a document, preserving section-level provenance.

    chunk_id is deterministic and stable so we can reliably attach evaluation
    results and human annotations over time.
    """

    chunk_id: str
    doc_id: str
    title: str
    section: str
    text: str
    metadata: Dict[str, Any]