## Answer Quality Evaluator – Product Requirements

### 1. Goal

Build an internal evaluation workbench that lets PMs, eng, and GTM quickly compare multiple RAG pipelines for Sales/CS knowledge bases, understand *why* answers differ, and make data-backed decisions about which pipeline to ship.

### 2. Users

- **Primary**
  - **ML / Platform engineers** – iterate on retrieval, chunking, and prompting; need tight feedback loops.
  - **Product managers** – choose default pipelines and guardrails; communicate tradeoffs to leadership.
- **Secondary**
  - **Enablement / Sales / CS leads** – sanity-check behavior on real questions; spot risky failure modes.

### 3. Core workflows

1. **Pipeline comparison for a single question**
   - Select a question from the eval set.
   - Run pipelines A/B/C with configurable `top_k` and `alpha`.
   - Compare answers side-by-side, including:
     - Citations (doc_id + section).
     - Heuristic scores for Accuracy, Completeness, Citation Quality.
     - Optionally LLM-judge scores + rationale.
   - Inspect retrieved chunks in the evidence drawer to understand gaps.

2. **Batch evaluation on the golden set**
   - Trigger an eval run over N questions (CLI or `/eval/run`).
   - Wait for an `eval_runs/<run_id>.jsonl` file to be written.
   - Use `/eval/summary?run_id=...` and the UI leaderboard to:
     - Compare avg scores per pipeline.
     - See failure tags (e.g., `missed_exception`, `weak_citations`, `retrieval_miss`).

3. **Debugging specific failure cases**
   - From a run summary, identify low-scoring pipelines/questions.
   - Load that question in the UI.
   - Inspect:
     - Which sections were retrieved (and which weren’t).
     - Whether citations align with required sections.
     - LLM-judge rationale, if enabled.
   - Use this to decide whether to tweak retrieval, prompts, or documentation.

### 4. Non-goals

- **Not** a production-facing chat assistant.
- **Not** a full-featured annotation tool (no complex workflow, review queues, or multi-user state).
- **Not** a replacement for human review on high-risk/legal commitments; this is a *signal amplifier*, not a gatekeeper.

### 5. Success metrics

Short term (within this project):

- **Instrumentation-level**
  - Can run eval over the entire golden set in a single command/API call.
  - Can visualize A/B/C differences and evidence for any question in the UI.
- **Quality-level**
  - Pipeline C (hybrid) improves Citation Quality and Completeness on “Exceptions & edge cases” questions vs. pipeline A.
  - LLM-judge scores align with human judgment on a small spot-check set (e.g., ≥80% agreement on which pipeline is better).

Medium term (if adopted in a real startup):

- Number of **meaningful pipeline changes** evaluated per month (signals iteration speed).
- Reduction in **high-severity answer issues** (e.g., hallucinated contractual commitments) in manual QA before launches.

### 6. Risks & mitigations

- **Risk: Over-trusting LLM-as-judge.**
  - Mitigation: Keep heuristic rubric as the primary signal; clearly label LLM-judge scores in UI and API responses.

- **Risk: Eval set drift vs. real traffic.**
  - Mitigation: Make it easy to add new questions/docs and rerun evals; capture “interesting” production questions into the golden set over time.

- **Risk: Infra/latency for large KBs.**
  - Mitigation: Current design is in-memory and single-node; roadmap includes pluggable vector store and batch evaluation.

### 7. Milestones

1. **MVP (current)**
   - Section-aware chunking + stable chunk IDs.
   - Pipelines A/B/C wired to OpenAI.
   - Eval harness with heuristic scoring.
   - FastAPI endpoints and Next.js workbench.

2. **“Trust the findings”**
   - Golden set refined with PM/SME input.
   - LLM-judge calibrated against manual labels.
   - Docs for adding new questions/docs + regression strategy.

3. **“Ready for team-wide use”**
   - Basic auth / environment-specific config.
   - Shared dashboard / saved runs.
   - Integration hooks to feed best pipeline into production assistant experiments.

