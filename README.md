# Answer Quality Evaluator
An internal evaluation tool for comparing answer quality across retrieval and prompting strategies for Sales / CS knowledge bases.

This project focuses on **evaluation as a product** — surfacing how retrieval decisions (chunking, search strategy, prompts) impact accuracy, completeness, and citation quality in real-world internal search scenarios.


## Why this exists
AI-powered internal search tools often produce answers that sound correct but are incomplete, outdated, or poorly cited. In practice, the biggest driver of answer quality is not the model — it’s the retrieval strategy.

This project builds a structured evaluation workflow that runs the same question across multiple retrieval + prompt pipelines, shows answers side-by-side, and scores them against a human-readable rubric. The goal is to make retrieval quality visible, debuggable, and measurable.
