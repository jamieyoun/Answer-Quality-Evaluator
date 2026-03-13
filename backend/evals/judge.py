import json
from typing import Any, Dict, List

from openai import OpenAI

from app.config import OPENAI_API_KEY

_client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """You are an internal policy evaluation assistant.
You act as a judge for model answers.

You MUST:
- Use ONLY the provided ground truth and sources.
- Follow the scoring rubric exactly.
- Penalize any unsupported claims or hallucinations.
- Return JSON ONLY with the required schema.

Scoring rubric (0–2 for each dimension):

1) Accuracy (0–2):
  - 2: Answer is factually consistent with ground truth bullets and does not contradict them.
  - 1: Minor issues, omissions, or slightly misleading phrasing; mostly aligned with ground truth.
  - 0: Clearly incorrect, makes unsupported commitments, or contradicts ground truth.

2) Completeness (0–2):
  - 2: Covers most or all key points from expected_answer_bullets (order/wording may differ).
  - 1: Covers some important points but misses others that a good answer should include.
  - 0: Misses most key points or is mostly irrelevant.

3) Citation Quality (0–2):
  - 2: Cites at least one of the required doc_id+section pairs and citations clearly support the answer.
  - 1: Citations exist but are weak, indirect, or do not match required doc_id+section pairs.
  - 0: No citations, or citations are clearly wrong/irrelevant.

You must explain your reasoning briefly for each dimension.
Confidence should be a number between 0.0 and 1.0.
"""


def judge_result(
    question: str,
    result: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Dict[str, Any]:
    """
    LLM-as-judge scoring for one (question, pipeline result, ground_truth) triple.
    """
    answer = result.get("answer", "")
    citations = result.get("citations", []) or []
    retrieved = result.get("retrieved", []) or []

    expected_bullets = ground_truth.get("expected_answer_bullets", []) or []
    required_citations = ground_truth.get("required_citations", []) or []

    # Prepare a compact view of retrieved chunks to keep prompt size reasonable.
    retrieved_summaries: List[str] = []
    for rc in retrieved[:6]:
        retrieved_summaries.append(
            f"[chunk_id={rc.get('chunk_id')} doc_id={rc.get('doc_id')} "
            f"section={rc.get('section')} score={rc.get('score')}]\n"
            f"{(rc.get('text') or '')[:320]}"
        )
    sources_block = "\n---\n".join(retrieved_summaries) if retrieved_summaries else "(no retrieved chunks available)"

    user_payload = {
        "question": question,
        "model_answer": answer,
        "model_citations": citations,
        "ground_truth": {
            "expected_answer_bullets": expected_bullets,
            "required_citations": required_citations,
        },
        "retrieved_sources_preview": sources_block,
    }

    user_prompt = (
        "You are given a question, a model answer with citations, ground truth hints, "
        "and previews of the retrieved sources.\n"
        "Evaluate the model answer according to the rubric.\n\n"
        "INPUT (JSON):\n"
        f"{json.dumps(user_payload, ensure_ascii=False, indent=2)}\n\n"
        "Return JSON ONLY with this exact schema:\n"
        "{\n"
        '  "accuracy": {"score_0_2": 0|1|2, "reasons": ["..."]},\n'
        '  "completeness": {"score_0_2": 0|1|2, "reasons": ["..."]},\n'
        '  "citation_quality": {"score_0_2": 0|1|2, "reasons": ["..."]},\n'
        '  "rationale": "overall short explanation",\n'
        '  "confidence": 0.0-1.0\n'
        "}\n"
        "Do NOT include any extra keys, text, or commentary outside this JSON.\n"
    )

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    raw = resp.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
        # Basic shape validation
        for key in ["accuracy", "completeness", "citation_quality"]:
            if key not in parsed:
                raise ValueError(f"Missing key: {key}")
        parsed.setdefault("rationale", "")
        parsed.setdefault("confidence", 0.5)
        return {
            "accuracy": parsed["accuracy"],
            "completeness": parsed["completeness"],
            "citation_quality": parsed["citation_quality"],
            "rationale": parsed["rationale"],
            "confidence": parsed["confidence"],
            "judge_type": "llm",
        }
    except Exception as e:
        # Fallback: mark as unusable but keep raw content for inspection.
        return {
            "accuracy": {"score_0_2": 0, "reasons": ["LLM judge output could not be parsed."]},
            "completeness": {"score_0_2": 0, "reasons": ["LLM judge output could not be parsed."]},
            "citation_quality": {"score_0_2": 0, "reasons": ["LLM judge output could not be parsed."]},
            "rationale": f"Parsing error: {e}",
            "confidence": 0.0,
            "judge_type": "llm",
            "raw": raw,
        }

