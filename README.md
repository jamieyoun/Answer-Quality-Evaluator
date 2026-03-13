# Answer Quality Evaluator

## 1) One-line summary

Internal evaluation workbench for comparing retrieval-augmented QA pipelines on Sales/CS knowledge bases with section-aware provenance and rubric-based scoring.

## 2) Why this exists (problem framing)

- **Answer quality is hard to trust**: LLM assistants for Sales/CS often hallucinate policy details or miss edge-case exceptions buried in long docs.
- **Most evals ignore provenance**: Typical benchmarks focus on answer text only, not whether citations actually point to the right policy sections.
- **Teams need fast, inspectable iteration**: We want to ship better answer pipelines week over week, with a tight loop between retrieval, generation, and human review.

This repo exists to make answer quality evaluation **inspectable, repeatable, and grounded in real policy docs**, not just synthetic Q&A pairs.

## 3) What this does (capabilities)

- **Section-aware chunking** that preserves policy sections like “Exceptions & edge cases” and attaches stable `doc_id::section::chunk_idx` identifiers.
- **Three retrieval+generation pipelines**:
  - **Pipeline A** – vector-only retrieval, strict citation formatting.
  - **Pipeline B** – vector retrieval + summary-first prompting.
  - **Pipeline C** – hybrid TF‑IDF + vector retrieval with weighted scoring.
- **Evaluation harness** that:
  - Runs pipelines over an eval set (questions + ground truth bullets).
  - Computes rubric scores for Accuracy, Completeness, and Citation Quality.
  - Optionally runs an **LLM-as-judge** to provide richer, rubric-aligned scores.
- **Next.js workbench UI** to:
  - Browse questions.
  - Compare A/B/C answers side-by-side.
  - Inspect retrieved evidence chunks and citations.
  - View per-pipeline score summaries and failure patterns.

## 4) Demo (GIF placeholder + sample screenshots)

> **GIF placeholder:** `demo/answer-quality-evaluator-demo.gif`  
> (Insert a short screen recording of: selecting a question → running A/B/C → opening the evidence drawer → viewing the leaderboard.)

Sample views:

- **Pipeline comparison:**  
  Three columns (A/B/C) with answers, citation chips (`KB-019 — Exceptions & edge cases`), and per-dimension scores stacked at the top.
- **Evidence drawer:**  
  Right-hand panel listing retrieved chunks with `doc_id`, section header, similarity score, and expandable full text.
- **Run summary:**  
  Leaderboard table with average Accuracy / Completeness / Citation Quality, plus failure tag counts (e.g., `missed_exception`, `weak_citations`).

## 5) How it works (architecture diagram in ASCII + request flow)

### High-level architecture

```text
                         ┌────────────────────────┐
                         │   Next.js Frontend     │
                         │  (evaluation workbench)│
                         └───────────┬────────────┘
                                     │ HTTP (JSON)
                                     ▼
                         ┌────────────────────────┐
                         │   FastAPI Backend      │
                         │ - /run/pipeline_[abc]  │
                         │ - /run/compare_abc     │
                         │ - /eval/run            │
                         │ - /eval/summary        │
                         └───────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │   Ingestion       │   │ Retrieval stack  │   │ Evaluation stack │
   │ - load_docs.py    │   │ - chunking.py    │   │ - scoring.py     │
   │ - Document schema │   │ - embed.py       │   │ - judge.py (LLM) │
   │   + sections      │   │ - vectorstore.py │   │ - run_eval.py    │
   └──────────────────┘   │ - lexical.py      │   └──────────────────┘
                          │ - hybrid.py       │
                          └───────────────────┘
```

### Request flow (compare A/B/C)

1. **Frontend** calls:

   ```text
   GET /run/compare_abc?q=...&top_k=...&alpha=...
   ```

2. **Backend**:
   - Loads markdown policy docs and parses sections.
   - Builds or reuses chunk + embedding + TF‑IDF indexes.
   - Runs Pipelines A, B, and C on the question:
     - Retrieves top‑k chunks (vector / lexical / hybrid).
     - Calls OpenAI chat completions with prompts that enforce:
       - “Answer only from Sources.”
       - Explicit citation schema `{doc_id, section, chunk_id}`.
   - Returns structured `RunResult` per pipeline with:
     - Answer text.
     - Citations.
     - Retrieved chunks (id, section, score, text, metadata).

3. **Frontend**:
   - Renders answers side-by-side.
   - Shows citation chips.
   - Lets you open an evidence drawer with retrieved chunks.

### Request flow (eval run + summary)

1. **Trigger eval** (CLI or API) over the golden set:
   - CLI:

     ```bash
     cd backend
     python -m evals.run_eval --limit 50 --use_llm_judge
     ```

   - API:

     ```bash
     curl -X POST http://127.0.0.1:8000/eval/run \
       -H "Content-Type: application/json" \
       -d '{"pipelines": ["A","B","C"], "limit": 50, "use_llm_judge": true}'
     ```

   - Backend writes `backend/eval_runs/<run_id>.jsonl` with:
     - All pipeline outputs.
     - Heuristic scores.
     - Optional LLM-judge scores + rationales.

2. **Summarize results**:
   - `GET /eval/summary?run_id=...` aggregates:
     - Average scores per pipeline.
     - Tag counts (e.g., how often exceptions were missed).
   - Frontend leaderboard consumes this to show A/B/C deltas.

## 6) Evaluation methodology (golden set, rubric, pipelines)

- **Golden eval set (`data/evalset/`)**
  - `questions.jsonl` – synthetic but realistic Sales/CS questions with:
    - `question_id`, `question`, `primary_doc_hint`, `category`, `difficulty`.
  - `ground_truth.jsonl` – for each `question_id`:
    - `expected_answer_bullets`: bullet-level target content.
    - `required_citations`: `{doc_id, section}` pairs the answer should cite.
    - `common_failure_modes`: typical mistakes to watch for.
    - `scoring_notes`: hints for human graders.

- **Rubric v1 (heuristic, deterministic)**
  - Implemented in `backend/evals/scoring.py`.
  - **Accuracy (0–2)**:
    - 2 – aligned with ground truth, no unsupported commitments.
    - 1 – minor issues, mostly correct.
    - 0 – clearly wrong or contradicts policies.
  - **Completeness (0–2)**:
    - Keyword-overlap between answer and `expected_answer_bullets`.
  - **Citation Quality (0–2)**:
    - Checks presence and correctness of `{doc_id, section}` citations.

- **LLM-as-judge (optional)**
  - Implemented in `backend/evals/judge.py`.
  - Uses the same rubric but asks an LLM to:
    - Consider model answer, retrieved sources, and ground truth.
    - Emit structured scores + short rationale + confidence.
  - Stored separately from heuristic scores and clearly labeled `judge_type: "llm"`.

- **Pipelines**
  - **A – Vector, strict citations**
  - **B – Vector + summary-first**
  - **C – Hybrid (TF‑IDF + vector)**
  - All pipelines enforce the same citation schema and section-preserving chunk ids.

## 7) Key findings (3 concrete insights with examples)

1. **Hybrid retrieval improves edge-case coverage**
   - For questions targeting “Exceptions & edge cases” sections, Pipeline C (hybrid) surfaces at least one exception chunk more often than vector-only A.
   - Example: API limit exceptions question – C consistently cites `KB-019 — Exceptions & edge cases`, while A occasionally stays in general “Policy / Guidance”.

2. **Summary-first prompts help with completeness but can blur citations**
   - Pipeline B tends to produce more complete narrative answers, incorporating more of the expected bullets.
   - However, its citations sometimes drift to general policy sections instead of the most specific exception sections, lowering Citation Quality.

3. **Strict prompts reduce hallucinated commitments**
   - Pipeline A’s stricter prompt (“If not supported, answer exactly: 'Not found in provided sources.'”) materially reduces commitments that aren’t backed by docs.
   - In discount and SLA scenarios, A is more likely to decline with “Not found in provided sources.” instead of guessing contractual terms.

These findings are visible in `/eval/summary` (aggregate scores) and per-question inspection in the frontend workbench.

## 8) How to run locally (backend + frontend)

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present; otherwise install FastAPI, Uvicorn, openai, sklearn, numpy, pydantic, etc.

export OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload
# Backend runs on http://127.0.0.1:8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install

# Optional: point frontend at a non-default backend
export NEXT_PUBLIC_BACKEND_BASE_URL=http://127.0.0.1:8000

npm run dev
# Frontend runs on http://localhost:3000
```

Then open `http://localhost:3000`:

- Select a question in the left sidebar.
- Configure pipelines, `top_k`, and `alpha`.
- Run a comparison and inspect evidence.
- Optionally paste a `run_id` from `/eval/run` or the CLI to load scores.

## 9) Repo structure

```text
backend/
  app/
    main.py             # FastAPI app + endpoints (pipelines, eval, debug)
    config.py           # API keys and model config
  ingest/
    load_docs.py        # Markdown frontmatter parsing + section extraction
  retrieval/
    chunking.py         # Section-aware chunking with stable chunk_ids
    embed.py            # OpenAI embedding calls
    vectorstore.py      # In-memory vector store + cosine similarity
    retrieve.py         # Top-k retrieval over chunks
    lexical.py          # TF-IDF (scikit-learn) lexical retriever
    hybrid.py           # Hybrid (vector + lexical) retrieval
  pipelines/
    pipeline_a.py       # Strict citations, vector-only retrieval
    pipeline_b.py       # Summary-first answering style
    pipeline_c.py       # Hybrid retrieval pipeline
  schemas/
    document.py         # Document + DocumentSection models
    chunk.py            # Chunk model with metadata + provenance
    run_result.py       # RunResult, Citation, RetrievedChunk
  evals/
    load_evalset.py     # Load questions + ground truth JSONL
    scoring.py          # Heuristic rubric scoring (A/C/CQ)
    judge.py            # LLM-as-judge scoring (optional)
    run_eval.py         # Batch eval harness -> eval_runs/*.jsonl

frontend/
  app/
    layout.tsx          # Shell layout / header
    page.tsx            # Main evaluation workbench UI
    api/questions/      # Reads backend evalset questions.jsonl
  components/
    QuestionSidebar.tsx # Question list (left)
    RunControls.tsx     # Pipeline + params controls
    CompareView.tsx     # Side-by-side A/B/C answer view
    EvidenceDrawer.tsx  # Retrieved chunk inspector (right)
    Leaderboard.tsx     # Per-pipeline score summary view
  lib/
    api.ts              # Typed wrappers for backend HTTP calls

data/
  kb/docs/              # Synthetic policy markdown docs (with YAML frontmatter)
  evalset/
    questions.jsonl     # Golden questions
    ground_truth.jsonl  # Ground truth bullets + required citations
    README_EVALSET.md   # Additional context
```

## 10) Roadmap (production next steps)

- **Richer accuracy checks**
  - Add negation/entailment checks over answer vs. ground truth using smaller verifier models.
  - Flag potential contradictions (e.g., promising on-prem where docs say cloud-only).

- **Deeper retrieval analytics**
  - Per-section recall metrics (e.g., “Exceptions & edge cases” hit rate).
  - Heatmap of which docs/sections each pipeline leans on.

- **Human-in-the-loop review**
  - Lightweight UI to accept/reject LLM-judge scores and store human overrides.
  - Exportable CSV/JSON for offline analysis.

- **Production integration**
  - Wrap best-performing pipeline as a standalone API for downstream products.
  - Add feature flags to A/B test pipelines in real traffic before full rollout.

- **Scaling + robustness**
  - Swap in a persistent vector store (e.g., PostgreSQL + pgvector) for larger KBs.
  - Add caching + rate-limit-aware handling for LLM and embedding calls.

---

### Example API calls

#### Compare pipelines A/B/C on a single question

```bash
curl "http://127.0.0.1:8000/run/compare_abc" \
  --get \
  --data-urlencode "q=What approvals are required for a 25% discount?" \
  --data-urlencode "top_k=8" \
  --data-urlencode "alpha=0.5"
```

#### Summarize scores for an eval run

```bash
curl "http://127.0.0.1:8000/eval/summary" \
  --get \
  --data-urlencode "run_id=eval_20260312T120000"
```

