import json
import time
from typing import List, Tuple, Optional

from openai import OpenAI

from app.config import OPENAI_API_KEY
from ingest.load_docs import load_all_documents
from retrieval.retrieve import build_index, retrieve
from schemas.chunk import Chunk
from schemas.run_result import Citation, RetrievedChunk, RunResult

_client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT_B = """You are a precise internal policy assistant.
You must answer ONLY using the provided sources.
If the sources do not contain the answer, say: "Not found in provided sources."
First, summarize the key evidence from the sources, then answer the question.
Always include citations for each claim using the required format.
Do NOT use outside knowledge.
"""


def _format_sources(retrieved: List[Tuple[Chunk, float]]) -> str:
    blocks = []
    for chunk, score in retrieved:
        blocks.append(
            f"[chunk_id={chunk.chunk_id} doc_id={chunk.doc_id} section={chunk.section} score={score:.4f}]\n"
            f"{chunk.text}\n"
        )
    return "\n---\n".join(blocks)


def run_pipeline_b(question: str, docs_dir, top_k: int = 6) -> RunResult:
    """
    Summary-first pipeline: LLM summarizes evidence, then answers with citations.
    """
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
  "evidence_summary": "string",  // concise synthesis of the key evidence
  "answer": "string",
  "citations": [
    {{"doc_id":"KB-###","section":"Section Header","chunk_id":"..."}}
  ]
}}

Rules:
- First, summarize the most relevant evidence across sources in evidence_summary.
- Then provide the final answer, still grounded only in the sources.
- Answer ONLY from Sources.
- If not supported, answer exactly: "Not found in provided sources."
- Citations must reference the specific chunk(s) that support the answer.
- Prefer citing the smallest number of chunks that fully support the answer.
"""

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_B},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    t_llm = time.time()

    raw = resp.choices[0].message.content.strip()

    evidence_summary: str = ""
    answer: str = ""
    citations: List[Citation] = []
    notes: Optional[str] = None

    # Basic JSON parsing with a forgiving fallback
    try:
        parsed = json.loads(raw)
        evidence_summary = parsed.get("evidence_summary", "")
        answer = parsed.get("answer", "")
        citations = [Citation(**c) for c in parsed.get("citations", [])]
    except Exception as e:
        # Fall back to treating the raw content as the answer
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

    # We store evidence_summary inside notes for now to keep RunResult minimal.
    if evidence_summary:
        summary_note = f"evidence_summary: {evidence_summary}"
        notes = f"{notes} | {summary_note}" if notes else summary_note

    return RunResult(
        question=question,
        pipeline_id="B_summary_first",
        answer=answer,
        citations=citations,
        retrieved=retrieved_out,
        timings_ms=timings,
        notes=notes if indexed_new == 0 else notes,
    )

