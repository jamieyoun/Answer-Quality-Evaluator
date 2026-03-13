# Eval Set v1 — Sales/CS Enablement QA (Synthetic)

This eval set is designed to mimic the kinds of questions that come up in a fast-growing B2B SaaS startup’s Sales & CS motion.

**What makes it realistic:**
- Mix of pricing/discounting/contract/renewal questions where mistakes have real revenue + legal risk
- Questions require **exceptions**, **approval chains**, and **time-bounded commitments**
- Ground truth is written as short bullets to support both human scoring and LLM-assisted scoring

## Files
- `questions.jsonl` — question text + lightweight metadata (category, difficulty, primary_doc_hint)
- `ground_truth.jsonl` — expected bullets + required citations + common failure modes

## Citation contract
Answers should cite **doc_id + section header** (e.g., `KB-003 — Policy / Guidance`).

## Usage
Load questions, run multiple pipelines, then score answers on:
- Accuracy
- Completeness
- Citation quality

