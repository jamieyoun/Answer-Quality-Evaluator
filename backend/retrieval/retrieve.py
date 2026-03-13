from typing import List, Tuple
from schemas.document import Document
from schemas.chunk import Chunk
from retrieval.chunking import chunk_documents
from retrieval.embed import embed_texts
from retrieval.vectorstore import InMemoryVectorStore
_store = InMemoryVectorStore()
_index_built = False

def build_index(docs: List[Document], max_chars: int = 1200, overlap_chars: int = 150) -> int:
    """
    Build the chunk+embedding index once per process.
    Returns number of chunks indexed on this call (0 if already built).
    """
    global _index_built
    if _index_built:
        return 0

    chunks = chunk_documents(docs, max_chars=max_chars, overlap_chars=overlap_chars)
    embeddings = embed_texts([c.text for c in chunks])
    _store.add(chunks, embeddings)
    _index_built = True
    return len(chunks)

def retrieve(question: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
    q_emb = embed_texts([question])[0]
    return _store.query(q_emb, top_k=top_k)