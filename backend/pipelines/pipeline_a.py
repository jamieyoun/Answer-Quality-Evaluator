import time
import json
from typing import List, Tuple
from openai import OpenAI
from app.config import OPENAI_API_KEY
from retrieval.retrieve import retrieve, build_index
from schemas.run_result import RunResult, Citation, RetrievedChunk
from ingest.load_docs import load_all_documents

_client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a precise internal policy assistant.
You must answer ONLY using the provided sources.
If the sources do not contain the answer, say: "Not found in provided sources."
Always include citations for each claim using the required format.
Do NOT use outside knowledge.
"""

def _format_sources(retrieved: List[Tuple[object, float]]) -> str:
    # retrieved is list[(Chunk, score)]
    blocks = []
    for chunk, score in retrieved:
        blocks.append(
            f"[chunk_id={chunk.chunk_id} doc_id={chunk.doc_id} section={chunk.section} score={score:.4f}]\n"
            f"{chunk.text}\n"
        )
    return "\n---\n".join(blocks)

def run_pipeline_a(question: str, docs_dir, top_k: int = 6) -> RunResult:
    t0 = time.time()

    docs = load_all_documents(docs_dir)
    t_load = time.time()

    indexed_new = build_index(docs)  # no-op if already built
    t_index = time.time()

    retrieved = retrieve(question, top_k=top_k)
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

Rules:
- Answer ONLY from Sources.
- If not supported, answer exactly: "Not found in provided sources."
- Citations must reference the specific chunk(s) that support the answer.
- Prefer citing the smallest number of chunks that fully support the answer.
"""

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    t_llm = time.time()

    raw = resp.choices[0].message.content.strip()

    # Parse JSON safely (basic)
    try:
        parsed = json.loads(raw)
        answer = parsed.get("answer", "")
        citations = [Citation(**c) for c in parsed.get("citations", [])]
        notes = None
    except Exception as e:
        answer = raw
        citations = []
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

    return RunResult(
        question=question,
        pipeline_id="A_strict_citations_small_chunks",
        answer=answer,
        citations=citations,
        retrieved=retrieved_out,
        timings_ms={
            "load_docs": int((t_load - t0) * 1000),
            "index": int((t_index - t_load) * 1000),
            "retrieve": int((t_retrieve - t_index) * 1000),
            "llm": int((t_llm - t_retrieve) * 1000),
            "total": int((t_llm - t0) * 1000),
        },
        notes=notes if indexed_new == 0 else notes,
    )