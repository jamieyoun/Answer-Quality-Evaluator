from typing import List, Tuple, Optional
import numpy as np
from schemas.chunk import Chunk
class InMemoryVectorStore:
    def __init__(self):
        self._chunks: List[Chunk] = []
        self._embeddings: Optional[np.ndarray] = None

    def add(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must be same length")

        emb = np.array(embeddings, dtype=np.float32)

        if self._embeddings is None:
            self._embeddings = emb
        else:
            self._embeddings = np.vstack([self._embeddings, emb])

        self._chunks.extend(chunks)

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        if self._embeddings is None or not self._chunks:
            return []

        q = np.array(query_embedding, dtype=np.float32)

        emb = self._embeddings
        emb_norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
        q_norm = q / (np.linalg.norm(q) + 1e-10)

        sims = emb_norm @ q_norm
        idxs = np.argsort(-sims)[:top_k]
        return [(self._chunks[i], float(sims[i])) for i in idxs]