from typing import List
from openai import OpenAI
from app.config import OPENAI_API_KEY, EMBEDDING_MODEL
_client = OpenAI(api_key=OPENAI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts using OpenAI embeddings.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    resp = _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in resp.data]