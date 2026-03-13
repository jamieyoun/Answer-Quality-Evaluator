import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional, Union

from evals.load_evalset import load_questions, load_ground_truth
from evals.scoring import (
    score_accuracy,
    score_citation_quality,
    score_completeness,
    derive_tags,
)
from pipelines.pipeline_a import run_pipeline_a
from pipelines.pipeline_b import run_pipeline_b
from pipelines.pipeline_c import run_pipeline_c


def _now_run_id() -> str:
    return datetime.utcnow().strftime("eval_%Y%m%dT%H%M%S")


def _iter_questions(questions_path: Path, limit: Optional[int]) -> Iterable[Dict[str, Any]]:
    questions = load_questions(questions_path)
    if limit is not None:
        questions = questions[: limit]
    return questions


def run_eval(
    pipelines: Optional[List[str]] = None,
    limit: Optional[int] = None,
    out_dir: Union[str, Path] = "eval_runs",
    questions_path: Optional[Union[str, Path]] = None,
    use_llm_judge: bool = False,
) -> Dict[str, Any]:
    """
    Run one or more pipelines over the eval questions and persist results.
    """
    if pipelines is None:
        pipelines = ["A", "B", "C"]

    # Data lives at repo root (data/kb/docs, data/evalset/); eval output under backend/
    repo_root = Path(__file__).resolve().parents[2]
    backend_dir = Path(__file__).resolve().parents[1]
    q_path = Path(questions_path) if questions_path else repo_root / "data" / "evalset" / "questions.jsonl"
    gt_path = repo_root / "data" / "evalset" / "ground_truth.jsonl"
    docs_dir = repo_root / "data" / "kb" / "docs"

    ground_truth = load_ground_truth(gt_path)

    out_root = backend_dir / out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    run_id = _now_run_id()
    out_path = out_root / f"{run_id}.jsonl"

    total = 0
    t_start = time.time()

    with out_path.open("w", encoding="utf-8") as f:
        for row in _iter_questions(q_path, limit):
            total += 1
            qid = row.get("question_id")
            question = row.get("question")

            record: Dict[str, Any] = {
                "run_id": run_id,
                "question_id": qid,
                "question": question,
                "pipelines": {},
                "scores": {},
                "judge_scores": {},
            }

            gt_row = ground_truth.get(qid, {})

            if "A" in pipelines:
                res_a = run_pipeline_a(question, docs_dir)
                res_a_dict = res_a.model_dump()
                record["pipelines"]["A"] = res_a_dict

                cq = score_citation_quality(res_a_dict, gt_row)
                comp = score_completeness(res_a_dict, gt_row)
                acc = score_accuracy(res_a_dict, gt_row)
                total = cq["score_0_2"] + comp["score_0_2"] + acc["score_0_2"]
                tags = derive_tags(
                    cq["score_0_2"],
                    comp["score_0_2"],
                    acc["score_0_2"],
                    res_a_dict,
                    gt_row,
                )
                record["scores"]["A"] = {
                    "accuracy": acc,
                    "completeness": comp,
                    "citation_quality": cq,
                    "total": total,
                    "tags": tags,
                }

                if use_llm_judge:
                    from evals.judge import judge_result

                    j = judge_result(question, res_a_dict, gt_row)
                    record["judge_scores"]["A"] = j

            if "B" in pipelines:
                res_b = run_pipeline_b(question, docs_dir)
                res_b_dict = res_b.model_dump()
                record["pipelines"]["B"] = res_b_dict

                cq = score_citation_quality(res_b_dict, gt_row)
                comp = score_completeness(res_b_dict, gt_row)
                acc = score_accuracy(res_b_dict, gt_row)
                total = cq["score_0_2"] + comp["score_0_2"] + acc["score_0_2"]
                tags = derive_tags(
                    cq["score_0_2"],
                    comp["score_0_2"],
                    acc["score_0_2"],
                    res_b_dict,
                    gt_row,
                )
                record["scores"]["B"] = {
                    "accuracy": acc,
                    "completeness": comp,
                    "citation_quality": cq,
                    "total": total,
                    "tags": tags,
                }

                if use_llm_judge:
                    from evals.judge import judge_result

                    j = judge_result(question, res_b_dict, gt_row)
                    record["judge_scores"]["B"] = j

            if "C" in pipelines:
                res_c = run_pipeline_c(question, docs_dir)
                res_c_dict = res_c.model_dump()
                record["pipelines"]["C"] = res_c_dict

                cq = score_citation_quality(res_c_dict, gt_row)
                comp = score_completeness(res_c_dict, gt_row)
                acc = score_accuracy(res_c_dict, gt_row)
                total = cq["score_0_2"] + comp["score_0_2"] + acc["score_0_2"]
                tags = derive_tags(
                    cq["score_0_2"],
                    comp["score_0_2"],
                    acc["score_0_2"],
                    res_c_dict,
                    gt_row,
                )
                record["scores"]["C"] = {
                    "accuracy": acc,
                    "completeness": comp,
                    "citation_quality": cq,
                    "total": total,
                    "tags": tags,
                }

                if use_llm_judge:
                    from evals.judge import judge_result

                    j = judge_result(question, res_c_dict, gt_row)
                    record["judge_scores"]["C"] = j

            f.write(json.dumps(record) + "\n")

    elapsed = time.time() - t_start

    return {
        "run_id": run_id,
        "file": str(out_path),
        "question_count": total,
        "pipelines": pipelines,
        "elapsed_sec": elapsed,
        "use_llm_judge": use_llm_judge,
    }


def main():
    parser = argparse.ArgumentParser(description="Run eval pipelines over questions.jsonl")
    parser.add_argument("--pipelines", nargs="*", default=["A", "B", "C"], help="Subset of pipelines to run, e.g. A B")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions")
    parser.add_argument("--out_dir", type=str, default="eval_runs", help="Output directory under backend/")
    parser.add_argument(
        "--use_llm_judge",
        action="store_true",
        help="If set, also run LLM-as-judge scoring.",
    )

    args = parser.parse_args()

    result = run_eval(
        pipelines=args.pipelines,
        limit=args.limit,
        out_dir=args.out_dir,
        use_llm_judge=args.use_llm_judge,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

