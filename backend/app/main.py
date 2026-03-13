import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingest.load_docs import load_all_documents
from retrieval.chunking import chunk_documents
from retrieval.retrieve import build_index, retrieve
from pipelines.pipeline_a import run_pipeline_a
from pipelines.pipeline_b import run_pipeline_b
from pipelines.pipeline_c import run_pipeline_c
from evals.run_eval import run_eval

app = FastAPI(
    title="Sales/CS Answer Quality Evaluator",
    version="0.1",
)

# Allow local frontend (Next.js on port 3000) to call this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "data" / "kb" / "docs"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/docs/sample")
def get_sample_doc() -> dict:
    docs = load_all_documents(DOCS_DIR)
    doc = docs[0]

    return {
        "doc_id": doc.doc_id,
        "title": doc.title,
        "sections": [
            {"header": s.header, "preview": s.content[:200]}
            for s in doc.sections
        ],
    }


@app.get("/chunks/sample")
def sample_chunks(max_chars: int = 1200) -> dict:
    """
    Debug endpoint for inspecting section-aware chunking behavior.
    """
    docs = load_all_documents(DOCS_DIR)
    chunks = chunk_documents(docs, max_chars=max_chars, overlap_chars=150)

    section_counter: Counter[str] = Counter(c.section for c in chunks)
    top_sections = section_counter.most_common(10)

    # Section-aware chunking is critical so Exceptions & edge cases (and
    # similar sections) stay intact for evaluation and reliable citations.
    return {
        "total_docs": len(docs),
        "total_chunks": len(chunks),
        "sample": [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "section": c.section,
                "preview": c.text[:220],
                "metadata": c.metadata,
            }
            for c in chunks[:5]
        ],
        "section_stats": [
            {"section": name, "count": count} for name, count in top_sections
        ],
    }


@app.get("/chunks/validate")
def validate_chunks(max_chars: int = 1200) -> dict:
    """
    Lightweight validation for docs/sections without failing the app.
    """
    docs = load_all_documents(DOCS_DIR)
    chunks = chunk_documents(docs, max_chars=max_chars, overlap_chars=150)

    warnings = []

    # Docs with zero sections
    for doc in docs:
        if not doc.sections:
            warnings.append(
                {
                    "type": "no_sections",
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "message": "Document has no parsed sections.",
                }
            )

    # Docs missing explicit "Exceptions & edge cases" section
    for doc in docs:
        has_exceptions = any(
            s.header.strip() == "Exceptions & edge cases" for s in doc.sections
        )
        if not has_exceptions:
            warnings.append(
                {
                    "type": "missing_exceptions_section",
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "message": "Missing 'Exceptions & edge cases' section.",
                }
            )

    # Extremely large sections (may benefit from manual review)
    LARGE_SECTION_THRESHOLD = 4000
    for doc in docs:
        for section in doc.sections:
            if len(section.content) > LARGE_SECTION_THRESHOLD:
                warnings.append(
                    {
                        "type": "large_section",
                        "doc_id": doc.doc_id,
                        "title": doc.title,
                        "section": section.header,
                        "length": len(section.content),
                        "message": "Section is very large and may chunk poorly.",
                    }
                )

    return {
        "total_docs": len(docs),
        "total_chunks": len(chunks),
        "warnings": warnings,
    }

@app.get("/retrieve/sample")
def retrieve_sample(q: str, top_k: int = 5):
    docs = load_all_documents(DOCS_DIR)
    indexed = build_index(docs)
    results = retrieve(q, top_k=top_k)

    return {
        "indexed_new_chunks": indexed,
        "query": q,
        "top_k": top_k,
        "results": [
            {
                "score": score,
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "section": chunk.section,
                "preview": chunk.text[:240],
                "metadata": chunk.metadata,
            }
            for chunk, score in results
        ],
    }

@app.get("/run/pipeline_a")
def run_a(q: str, top_k: int = 6):
    result = run_pipeline_a(q, DOCS_DIR, top_k=top_k)
    return result.model_dump()


@app.get("/run/pipeline_b")
def run_b(q: str, top_k: int = 6):
    """
    Run the summary-first pipeline (Pipeline B).
    """
    result = run_pipeline_b(q, DOCS_DIR, top_k=top_k)
    return result.model_dump()


@app.get("/run/compare")
def run_compare(q: str, top_k: int = 6, include_c: bool = False, alpha: float = 0.5):
    """
    Run Pipeline A and B (and optionally C) and return results side-by-side.
    """
    result_a = run_pipeline_a(q, DOCS_DIR, top_k=top_k)
    result_b = run_pipeline_b(q, DOCS_DIR, top_k=top_k)

    payload: dict = {
        "question": q,
        "top_k": top_k,
        "pipeline_a": result_a.model_dump(),
        "pipeline_b": result_b.model_dump(),
    }

    if include_c:
        result_c = run_pipeline_c(q, DOCS_DIR, top_k=top_k, alpha=alpha)
        payload["pipeline_c"] = result_c.model_dump()

    return payload


@app.get("/run/compare_abc")
def run_compare_abc(q: str, top_k: int = 6, alpha: float = 0.5):
    """
    Convenience alias for /run/compare with include_c=true.
    """
    return run_compare(q=q, top_k=top_k, include_c=True, alpha=alpha)


@app.get("/run/pipeline_c")
def run_c(q: str, top_k: int = 8, alpha: float = 0.5):
    """
    Run the hybrid retrieval pipeline (Pipeline C).
    """
    result = run_pipeline_c(q, DOCS_DIR, top_k=top_k, alpha=alpha)
    return result.model_dump()


class EvalRunRequest(BaseModel):
    pipelines: list[str] = ["A", "B", "C"]
    limit: Optional[int] = None
    use_llm_judge: bool = False


@app.post("/eval/run")
def eval_run(body: EvalRunRequest):
    """
    Run one or more pipelines over the eval questions and persist results.
    """
    summary = run_eval(
        pipelines=body.pipelines,
        limit=body.limit,
        out_dir="eval_runs",
        use_llm_judge=body.use_llm_judge,
    )
    return summary


@app.get("/eval/results")
def eval_results(run_id: str) -> dict:
    """
    Summarize scores for a given eval run_id.
    """
    backend_dir = Path(__file__).resolve().parents[1]
    eval_runs_dir = backend_dir / "eval_runs"
    run_path = eval_runs_dir / f"{run_id}.jsonl"

    if not run_path.exists():
        raise HTTPException(status_code=404, detail="run_id not found")

    pipeline_stats: Dict[str, Dict[str, Any]] = {}
    judge_stats: Dict[str, Dict[str, Any]] = {}

    # Initialize structures lazily per pipeline
    with run_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            scores = row.get("scores", {})
            judge_scores = row.get("judge_scores", {})

            for pid, s in scores.items():
                if pid not in pipeline_stats:
                    pipeline_stats[pid] = {
                        "count": 0,
                        "accuracy_sum": 0,
                        "completeness_sum": 0,
                        "citation_quality_sum": 0,
                        "total_sum": 0,
                        "tag_counts": defaultdict(int),
                        "questions": [],
                    }

                ps = pipeline_stats[pid]
                ps["count"] += 1
                ps["accuracy_sum"] += int(s["accuracy"]["score_0_2"])
                ps["completeness_sum"] += int(s["completeness"]["score_0_2"])
                ps["citation_quality_sum"] += int(s["citation_quality"]["score_0_2"])
                ps["total_sum"] += int(s["total"])
                ps["questions"].append(
                    {
                        "question_id": row.get("question_id"),
                        "total": int(s["total"]),
                        "tags": s.get("tags", []),
                    }
                )

                for tag in s.get("tags", []):
                    # tag may be a string (legacy) or structured dict with type
                    if isinstance(tag, dict):
                        tag_name = tag.get("type")
                    else:
                        tag_name = str(tag)
                    if tag_name:
                        ps["tag_counts"][tag_name] += 1

            for pid, js in judge_scores.items():
                if pid not in judge_stats:
                    judge_stats[pid] = {
                        "count": 0,
                        "accuracy_sum": 0,
                        "completeness_sum": 0,
                        "citation_quality_sum": 0,
                    }

                js_acc = int(js.get("accuracy", {}).get("score_0_2", 0))
                js_comp = int(js.get("completeness", {}).get("score_0_2", 0))
                js_cq = int(js.get("citation_quality", {}).get("score_0_2", 0))

                jps = judge_stats[pid]
                jps["count"] += 1
                jps["accuracy_sum"] += js_acc
                jps["completeness_sum"] += js_comp
                jps["citation_quality_sum"] += js_cq

    # Compute averages and top missed questions
    heuristic_by_pipeline: Dict[str, Any] = {}
    for pid, ps in pipeline_stats.items():
        count = ps["count"] or 1
        # sort questions by lowest total score
        worst = sorted(ps["questions"], key=lambda q: q["total"])[:5]
        heuristic_by_pipeline[pid] = {
            "count": ps["count"],
            "avg_accuracy": ps["accuracy_sum"] / count,
            "avg_completeness": ps["completeness_sum"] / count,
            "avg_citation_quality": ps["citation_quality_sum"] / count,
            "avg_total": ps["total_sum"] / count,
            "tag_counts": dict(ps["tag_counts"]),
            "top_missed_questions": worst,
        }

    judge_by_pipeline: Dict[str, Any] = {}
    for pid, ps in judge_stats.items():
        count = ps["count"] or 1
        judge_by_pipeline[pid] = {
            "count": ps["count"],
            "avg_accuracy": ps["accuracy_sum"] / count,
            "avg_completeness": ps["completeness_sum"] / count,
            "avg_citation_quality": ps["citation_quality_sum"] / count,
            "note": "LLM-judged scores using rubric v1.",
        }

    return {
        "run_id": run_id,
        "heuristic": heuristic_by_pipeline,
        "llm_judge": judge_by_pipeline,
        "llm_judge_explicit": bool(judge_by_pipeline),
    }


@app.get("/eval/summary")
def eval_summary(run_id: str) -> dict:
    """
    Alias for /eval/results to match external docs.
    """
    return eval_results(run_id=run_id)