from pydantic import BaseModel
from typing import Dict, List, Optional

class DocumentSection(BaseModel):
    header: str
    content: str


class Document(BaseModel):
    doc_id: str
    title: str
    owner_team: str
    last_updated: str
    effective_date: str
    policy_type: str
    region_scope: List[str]
    source_of_truth: bool
    supersedes: Optional[str] = None

    sections: List[DocumentSection]
    raw_text: str
    file_path: str