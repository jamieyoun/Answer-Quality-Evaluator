import json
import time
from typing import List, Tuple, Optional

from openai import OpenAI

from app.config import OPENAI_API_KEY
from ingest.load_docs import load_all_documents
from retrieval.hybrid import build_hybrid_indexes, hybrid_retrieve
from schemas.chunk import Chunk
from schemas.run_result import Citation, RetrievedChunk, RunResult

_client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT_C = """You are an internal policy assistant.
Use the provided sources to give a helpful, precise answer.
If the sources do not contain the answer, say: "Not found in provided sources."
You may synthesize and explain, but must stay grounded in the sources.
Always include citations for each major claim.
"""


def _format_sources(retrieved: List[Tuple[Chunk, float]]) -> str:
    blocks = []
    for chunk, score in retrieved:
        blocks.append(
            f"[chunk_id={chunk.chunk_id} doc_id={chunk.doc_id} section={chunk.section} score={score:.4f}]\n"
            f"{chunk.text}\n"
        )
    return "\n---\n".join(blocks)


def run_pipeline_c(
    question: str,
    docs_dir,
    top_k: int = 8,
    alpha: float = 0.5,
) -> RunResult:
    """
    Pipeline C: hybrid retrieval (lexical + vector) with balanced answer style.
    """
    t0 = time.time()

    docs = load_all_documents(docs_dir)
    t_load = time.time()

    # Build / cache both indexes once per process.
    build_hybrid_indexes(docs)
    t_index = time.time()

    retrieved = hybrid_retrieve(question, top_k=top_k, alpha=alpha)
    t_retrieve = time.time()

    sources_text = _format_sources(retrieved)

    user_prompt = f"""
Question: {question}

Sources:
{sources_text}

Return JSON only with this exact schema:
{{
  "answer": "string",
  "citations": [
    {{"doc_id":"KB-###","section":"Section Header","chunk_id":"..."}}
  ]
}}

Guidance:
- Be clear and helpful, not overly terse.
- You may briefly explain reasoning, but it must stay grounded in the Sources.
- Answer ONLY from Sources.
- If not supported, answer exactly: "Not found in provided sources."
- Citations must reference the specific chunk(s) that support the answer.
- Prefer citing the smallest number of chunks that fully support the answer.
"""

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_C},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    t_llm = time.time()

    raw = resp.choices[0].message.content.strip()

    answer: str = ""
    citations: List[Citation] = []
    notes: Optional[str] = None

    try:
        parsed = json.loads(raw)
        answer = parsed.get("answer", "")
        citations = [Citation(**c) for c in parsed.get("citations", [])]
    except Exception as e:
        answer = raw
        notes = f"LLM returned non-JSON or invalid schema: {e}"

    retrieved_out = [
        RetrievedChunk(
            chunk_id=chunk.chunk_id,
            doc_id=chunk.doc_id,
            section=chunk.section,
            score=float(score),
            text=chunk.text,
            metadata=chunk.metadata,
        )
        for chunk, score in retrieved
    ]

    timings = {
        "load_docs": int((t_load - t0) * 1000),
        "index": int((t_index - t_load) * 1000),
        "retrieve": int((t_retrieve - t_index) * 1000),
        "llm": int((t_llm - t_retrieve) * 1000),
        "total": int((t_llm - t0) * 1000),
    }

    return RunResult(
        question=question,
        pipeline_id="C_hybrid_balanced",
        answer=answer,
        citations=citations,
        retrieved=retrieved_out,
        timings_ms=timings,
        notes=notes,
    )

