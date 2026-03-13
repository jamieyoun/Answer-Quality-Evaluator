from typing import List, Tuple

from schemas.chunk import Chunk
from schemas.document import Document
from retrieval.lexical import build_lexical_index, query_lexical
from retrieval.retrieve import build_index, retrieve


def build_hybrid_indexes(docs: List[Document], max_chars: int = 1200, overlap_chars: int = 150) -> None:
    """
    Ensure both vector and lexical indexes are built once per process.
    """
    build_index(docs, max_chars=max_chars, overlap_chars=overlap_chars)
    build_lexical_index(docs, max_chars=max_chars, overlap_chars=overlap_chars)


def _normalize(scores: List[float]) -> List[float]:
    if not scores:
        return []
    s_min = min(scores)
    s_max = max(scores)
    if s_max == s_min:
        return [1.0 for _ in scores]
    return [(s - s_min) / (s_max - s_min) for s in scores]


def hybrid_retrieve(query: str, top_k: int = 5, alpha: float = 0.5) -> List[Tuple[Chunk, float]]:
    """
    Hybrid retrieval: combine vector and lexical scores with a weighted sum.
    """
    if top_k <= 0:
        top_k = 1

    k_internal = top_k * 2

    vec_results = retrieve(query, top_k=k_internal)
    lex_results = query_lexical(query, top_k=k_internal)

    # Normalize scores separately to [0, 1]
    vec_scores = [s for _, s in vec_results]
    lex_scores = [s for _, s in lex_results]

    vec_norm = _normalize(vec_scores)
    lex_norm = _normalize(lex_scores)

    # Merge by chunk_id with weighted sum
    merged: dict[str, dict] = {}

    for (chunk, _), s in zip(vec_results, vec_norm):
        merged.setdefault(chunk.chunk_id, {"chunk": chunk, "vec": 0.0, "lex": 0.0})
        merged[chunk.chunk_id]["vec"] = max(merged[chunk.chunk_id]["vec"], s)

    for (chunk, _), s in zip(lex_results, lex_norm):
        merged.setdefault(chunk.chunk_id, {"chunk": chunk, "vec": 0.0, "lex": 0.0})
        merged[chunk.chunk_id]["lex"] = max(merged[chunk.chunk_id]["lex"], s)

    scored: List[Tuple[Chunk, float]] = []
    for item in merged.values():
        v = item["vec"]
        l = item["lex"]
        score = alpha * v + (1.0 - alpha) * l
        scored.append((item["chunk"], float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

