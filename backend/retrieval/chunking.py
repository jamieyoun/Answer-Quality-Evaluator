from typing import List

from schemas.document import Document
from schemas.chunk import Chunk


def split_text(text: str, max_chars: int, overlap_chars: int) -> List[str]:
    """
    Split a block of text into character-based chunks with optional overlap.

    This is intentionally simple and deterministic; we will upgrade to
    token-aware chunking later once we have enough evaluation data.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = max(0, end - overlap_chars)

    return chunks


def _sanitize_section_for_id(section_header: str) -> str:
    """
    Make section headers safe to embed in chunk IDs.
    """
    import re

    normalized = section_header.strip().lower()
    # Replace whitespace with single underscores
    normalized = re.sub(r"\s+", "_", normalized)
    # Drop characters that are likely to cause ID issues
    normalized = re.sub(r"[^a-z0-9_]+", "", normalized)
    return normalized or "section"


def chunk_documents(
    docs: List[Document],
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> List[Chunk]:
    """
    Chunk documents by section so we never cross section boundaries.

    Section-aware chunking keeps exceptions and edge-case language grouped
    with their section headers, which is critical for trustworthy evaluation
    and citation provenance.
    """
    all_chunks: List[Chunk] = []

    # Ensure deterministic ordering: by doc_id, then section order, then chunk index.
    docs_sorted = sorted(docs, key=lambda d: d.doc_id)

    for doc in docs_sorted:
        for section in doc.sections:
            section_text = section.content.strip()
            if not section_text:
                continue

            # If the section is very short, keep it as a single chunk without overlap.
            if len(section_text) < 200:
                pieces = [section_text]
            else:
                pieces = split_text(
                    section_text,
                    max_chars=max_chars,
                    overlap_chars=overlap_chars,
                )

            safe_section = _sanitize_section_for_id(section.header)

            for i, piece in enumerate(pieces):
                if not piece.strip():
                    continue

                chunk_id = f"{doc.doc_id}::{safe_section}::{i}"
                all_chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        doc_id=doc.doc_id,
                        title=doc.title,
                        section=section.header,
                        text=piece,
                        metadata={
                            "owner_team": doc.owner_team,
                            "last_updated": doc.last_updated,
                            "effective_date": doc.effective_date,
                            "policy_type": doc.policy_type,
                            "region_scope": doc.region_scope,
                            "source_of_truth": doc.source_of_truth,
                            "supersedes": doc.supersedes,
                            "file_path": doc.file_path,
                        },
                    )
                )

    return all_chunks