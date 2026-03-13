## Evals Spec – Answer Quality Evaluator

This doc explains how the eval set is structured, how scoring works, and how to extend it safely.

---

### 1. Eval set design

Location: `data/evalset/`

- **`questions.jsonl`**
  - Each line is a JSON object:
    - `question_id` – stable identifier (e.g., `"Q-001"`).
    - `question` – natural-language question.
    - `primary_doc_hint` – main `doc_id` expected to be cited (helps debugging, not required for scoring).
    - `category` – high-level area (e.g., `pricing_discounts_contracts`).
    - `difficulty` – `easy` / `medium` / `hard` (used for analysis, not scoring).

- **`ground_truth.jsonl`**
  - Each line is a JSON object with the same `question_id`:
    - `expected_answer_bullets: string[]`
      - Bullets that represent the *shape* of a good answer.
      - Example: “We do not offer on‑prem deployments as a standard option.”
    - `required_citations: {doc_id, section}[]`
      - Docs + sections that must be cited for full credit.
      - Example: `{ "doc_id": "KB-019", "section": "Exceptions & edge cases" }`.
    - `common_failure_modes: string[]`
      - Typical mistakes (e.g., “claims on‑prem is available”).
    - `scoring_notes: { accuracy, completeness, citation_quality }`
      - Free-text guidance to human reviewers.

Design principles:

- Cover “standard” and “edge case” flows, with emphasis on:
  - Exceptions and overrides.
  - Approvals/approvers.
  - Contractual commitments (SLA, data handling, discounts).
- Use **realistic** but synthetic content (no real customers or policies).
- Ensure each question:
  - Has at least one canonical doc + section.
  - Is answerable from the KB (or intentionally “not supported”).

---

### 2. Rubric definitions (heuristic)

Implemented in `backend/evals/scoring.py`.

For each pipeline result (`RunResult`) and ground truth row:

#### Accuracy (0–2)

- **2 – Correct**
  - Answer is consistent with expected bullets.
  - No unsupported commitments (e.g., promising features not in docs).
  - No direct contradictions.
- **1 – Mostly correct**
  - Minor omissions or imprecise phrasing.
  - Directionally aligned but could be clearer.
- **0 – Incorrect**
  - Contradicts policy.
  - Claims unsupported guarantees/terms.
  - Says “Not found in provided sources” when ground truth clearly exists.

Heuristic rule currently:

- If ground truth bullets exist and answer starts with `"Not found in provided sources"` → **0**.
- If bullets exist and answer is empty → **0**.
- If no bullets → **2** (no signal).
- Otherwise → **1** (“baseline accurate”).

#### Completeness (0–2)

- **2 – Good coverage**
  - Hits most key bullets.
- **1 – Partial**
  - Hits some bullets, misses others.
- **0 – Poor**
  - Misses most bullets or off-topic.

Heuristic rule:

- Extract simple keywords from `expected_answer_bullets` and `answer`.
- Count how many bullets share at least one keyword with the answer.
- Compute coverage = hits / total bullets:
  - ≥ 2/3 → **2**
  - > 0 and < 2/3 → **1**
  - 0 → **0**

#### Citation Quality (0–2)

- **2 – Strong**
  - At least one citation matches a required `{doc_id, section}` pair.
  - Citations look plausibly relevant.
- **1 – Weak**
  - Citations exist but don’t match required pairs (e.g., wrong section).
- **0 – None / bad**
  - No citations.
  - (Future: obviously wrong doc/section.)

Heuristic rule:

- If no citations → **0**.
- Else, if there is any overlap between cited `(doc_id, section)` and `required_citations` → **2**.
- Else → **1**.

#### Tags

Derived in `derive_tags`:

- `weak_citations` – Citation score ≤ 1.
- `retrieval_miss` – Citation score 0 **and** completeness ≤ 1.
- `missed_exception` – Ground truth expects an “Exceptions & edge cases” section but citation score < 2.

---

### 3. LLM-as-judge scoring

Implemented in `backend/evals/judge.py`.

- Uses the same rubric (Accuracy, Completeness, Citation Quality) but asks an LLM to:
  - Consider:
    - Question.
    - Model answer + citations.
    - Ground truth bullets + required citations.
    - A small preview of retrieved chunks (doc_id, section, score, first ~320 chars).
  - Emit JSON:

    ```json
    {
      "accuracy": { "score_0_2": 0, "reasons": ["..."] },
      "completeness": { "score_0_2": 0, "reasons": ["..."] },
      "citation_quality": { "score_0_2": 0, "reasons": ["..."] },
      "rationale": "overall explanation",
      "confidence": 0.0
    }
    ```

- Output is stored under `record["judge_scores"][pipeline_id]` in `eval_runs/*.jsonl`.
- `/eval/summary` surfaces LLM-judge averages separately from heuristic scores, with an explicit note that they are model opinions.

---

### 4. How scoring works end-to-end

1. **Run an eval**

   - CLI:

     ```bash
     cd backend
     python -m evals.run_eval --limit 50 --use_llm_judge
     ```

   - or API:

     ```bash
     curl -X POST http://127.0.0.1:8000/eval/run \
       -H "Content-Type: application/json" \
       -d '{"pipelines":["A","B","C"],"limit":50,"use_llm_judge":true}'
     ```

2. **For each question**:

   - Run pipelines A/B/C to get `RunResult`.
   - Compute heuristic scores via `scoring.py`.
   - If `use_llm_judge`, call `judge_result(...)`.
   - Write a line to `backend/eval_runs/<run_id>.jsonl`:

     ```json
     {
       "run_id": "eval_...",
       "question_id": "Q-001",
       "question": "...",
       "pipelines": {
         "A": { ... RunResult ... },
         "B": { ... },
         "C": { ... }
       },
       "scores": {
         "A": { "accuracy": {...}, "completeness": {...}, "citation_quality": {...}, "total": 5, "tags": [...] },
         "B": { ... },
         "C": { ... }
       },
       "judge_scores": {
         "A": { "accuracy": {...}, "completeness": {...}, "citation_quality": {...}, "rationale": "...", "confidence": 0.8 },
         "B": { ... },
         "C": { ... }
       }
     }
     ```

3. **Summarize**

   - `GET /eval/summary?run_id=...`:
     - Aggregates heuristic scores per pipeline (averages + tag counts).
     - Aggregates LLM-judge scores per pipeline if present.

4. **Inspect**

   - Next.js UI lets you:
     - Drill into any question’s answers and evidence.
     - See heuristic vs. LLM-judge scores side-by-side.

---

### 5. How to add new questions

1. **Append to `questions.jsonl`**

   - Choose a new `question_id` (e.g., `Q-051`).
   - Add a JSON line:

     ```json
     {
       "question_id": "Q-051",
       "question": "Can we extend Enterprise-only features for a 60-day pilot?",
       "primary_doc_hint": "KB-007",
       "category": "pricing_discounts_contracts",
       "difficulty": "medium"
     }
     ```

2. **Add ground truth in `ground_truth.jsonl` with the same `question_id`**

   - Include expected bullets and required citations:

     ```json
     {
       "question_id": "Q-051",
       "expected_answer_bullets": [
         "Enterprise-only features can be enabled only for time-bounded pilots.",
         "Pilot must have documented scope, duration, and success criteria."
       ],
       "required_citations": [
         { "doc_id": "KB-007", "section": "Policy / Guidance" },
         { "doc_id": "KB-024", "section": "Policy / Guidance" }
       ],
       "common_failure_modes": [
         "says 'yes' without time bounds",
         "does not require documentation"
       ],
       "scoring_notes": {
         "accuracy": "No open-ended entitlement.",
         "completeness": "Mention time bounds and documentation.",
         "citation_quality": "Must cite the Enterprise pilot policy."
       }
     }
     ```

3. **Rerun eval**

   - Use `evals.run_eval` or `/eval/run` and inspect results.

---

### 6. How to add new docs

1. Add a markdown file under `data/kb/docs/`:

   - Include YAML frontmatter with at least:

     ```yaml
     ---
     doc_id: KB-999
     title: "New Policy Area"
     owner_team: ...
     last_updated: 2026-03-10
     effective_date: 2026-03-10
     policy_type: binding
     source_of_truth: true
     region_scope:
       - US
       - EMEA
       - APAC
     ---
     ```

   - Use `##` section headers; especially for:
     - `## Policy / Guidance`
     - `## Exceptions & edge cases` (if relevant).

2. Restart the backend or let Uvicorn reload; ingestion will pick it up automatically.

3. Update any eval questions that should target the new doc via `primary_doc_hint` and `required_citations`.

---

### 7. Regression strategy

- **Per-run regression**
  - Keep `eval_runs/*.jsonl` under source control (or in object storage) for important runs.
  - Compare:
    - Average scores per pipeline.
    - Tag distributions (e.g., `missed_exception` count for pipeline C).

- **Before changing pipelines**
  - Re-run eval on the full golden set with the *old* and *new* pipelines.
  - Look for regressions:
    - Significant drop in Accuracy or Citation Quality.
    - New clusters of `retrieval_miss` or `missed_exception`.

- **Adding new questions/docs**
  - Treat new questions as “canary” tests:
    - Run eval with and without them and track how averages move.
  - For high-risk areas (e.g., legal commitments), spot-check LLM-judge rationales and override if necessary.

The goal is to make it cheap to run evals after *any* change to retrieval, chunking, prompting, or content—and to have enough signal to know when not to ship a pipeline change.

