from typing import List, Tuple, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from schemas.chunk import Chunk
from schemas.document import Document
from retrieval.chunking import chunk_documents

_lex_vectorizer: Optional[TfidfVectorizer] = None
_lex_matrix = None
_lex_chunks: List[Chunk] = []
_lex_index_built = False


def build_lexical_index(docs: List[Document], max_chars: int = 1200, overlap_chars: int = 150) -> int:
    """
    Build a simple TF-IDF index over chunk.text once per process.
    Returns number of chunks indexed on this call (0 if already built).
    """
    global _lex_vectorizer, _lex_matrix, _lex_chunks, _lex_index_built
    if _lex_index_built:
        return 0

    chunks = chunk_documents(docs, max_chars=max_chars, overlap_chars=overlap_chars)
    texts = [c.text for c in chunks]

    if not texts:
        _lex_vectorizer = None
        _lex_matrix = None
        _lex_chunks = []
        _lex_index_built = True
        return 0

    _lex_vectorizer = TfidfVectorizer()
    _lex_matrix = _lex_vectorizer.fit_transform(texts)
    _lex_chunks = chunks
    _lex_index_built = True
    return len(chunks)


def query_lexical(query: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
    """
    TF-IDF cosine similarity over chunk text.
    """
    if _lex_vectorizer is None or _lex_matrix is None or not _lex_chunks:
        return []

    q_vec = _lex_vectorizer.transform([query])
    sims = cosine_similarity(q_vec, _lex_matrix)[0]

    if top_k <= 0:
        top_k = 1

    top_indices = sims.argsort()[::-1][:top_k]
    return [(_lex_chunks[i], float(sims[i])) for i in top_indices]

