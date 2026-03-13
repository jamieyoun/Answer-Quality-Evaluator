from typing import Any, Dict, List, Tuple


def score_citation_quality(result: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple rubric for citation quality (0–2).
    """
    citations = result.get("citations", []) or []
    required = ground_truth.get("required_citations", []) or []

    reasons: List[str] = []

    if not citations:
        reasons.append("No citations provided.")
        return {"score_0_2": 0, "reasons": reasons}

    # Require at least one exact doc_id + section match
    required_pairs = {(c.get("doc_id"), c.get("section")) for c in required}
    cited_pairs = {(c.get("doc_id"), c.get("section")) for c in citations}

    if required_pairs & cited_pairs:
        reasons.append("At least one required doc_id+section cited.")
        return {"score_0_2": 2, "reasons": reasons}

    reasons.append("Citations present but none match required doc_id+section.")
    return {"score_0_2": 1, "reasons": reasons}


def _extract_keywords(text: str) -> List[str]:
    """
    Very simple keyword extractor: lowercase, split, filter short/common words.
    """
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "for",
        "in",
        "on",
        "at",
        "is",
        "are",
        "be",
        "we",
        "our",
        "this",
        "that",
        "it",
    }
    tokens = [t.strip(".,:;!?()[]\"'").lower() for t in text.split()]
    return [t for t in tokens if len(t) > 3 and t not in stop]


def score_completeness(result: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """
    Heuristic completeness score (0–2) based on overlap between
    expected answer bullets and the model's answer text.
    """
    answer = (result.get("answer") or "").lower()
    bullets = ground_truth.get("expected_answer_bullets", []) or []

    reasons: List[str] = []

    if not bullets:
        reasons.append("No expected_answer_bullets in ground truth; defaulting to score 2.")
        return {"score_0_2": 2, "reasons": reasons}

    answer_kw = set(_extract_keywords(answer))

    bullet_hits = 0
    for b in bullets:
        b_kw = set(_extract_keywords(b))
        if not b_kw:
            continue
        if b_kw & answer_kw:
            bullet_hits += 1

    total_bullets = len(bullets)
    coverage = bullet_hits / total_bullets if total_bullets else 0.0

    if coverage >= 0.66:
        score = 2
        reasons.append(f"High coverage: matched keywords for {bullet_hits}/{total_bullets} bullets.")
    elif coverage > 0:
        score = 1
        reasons.append(f"Partial coverage: matched keywords for {bullet_hits}/{total_bullets} bullets.")
    else:
        score = 0
        reasons.append("No noticeable keyword overlap with expected bullets.")

    return {"score_0_2": score, "reasons": reasons}


def score_accuracy(result: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very simple, conservative accuracy heuristic (0–2).
    """
    answer = (result.get("answer") or "").strip()
    bullets = ground_truth.get("expected_answer_bullets", []) or []

    reasons: List[str] = []

    if not bullets:
        reasons.append("No ground truth bullets; defaulting to score 2.")
        return {"score_0_2": 2, "reasons": reasons}

    nf_phrase = "not found in provided sources"
    if answer.lower().startswith(nf_phrase):
        reasons.append("Answer claims 'Not found...' but ground truth exists.")
        return {"score_0_2": 0, "reasons": reasons}

    if not answer:
        reasons.append("Empty answer despite ground truth existing.")
        return {"score_0_2": 0, "reasons": reasons}

    reasons.append("Heuristic baseline: treating grounded answer as accuracy 1.")
    return {"score_0_2": 1, "reasons": reasons}


def derive_tags(
    citation_score: int,
    completeness_score: int,
    accuracy_score: int,
    result: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Derive structured failure/signal tags for analysis.

    Supported tags:
      - retrieval_miss
      - weak_citations
      - missed_exception
      - outdated_policy
      - hallucination
      - overconfident_language
    """
    tags: List[Dict[str, str]] = []

    answer = (result.get("answer") or "").strip()
    citations = result.get("citations", []) or []

    # Weak or missing citations
    if citation_score <= 1:
        tags.append(
            {
                "type": "weak_citations",
                "reason": "Citations are missing or do not match required doc_id+section.",
            }
        )

    # Retrieval miss proxy: bad citations and low completeness
    if citation_score == 0 and completeness_score <= 1:
        tags.append(
            {
                "type": "retrieval_miss",
                "reason": "Low completeness and no useful citations; likely missing the right chunks.",
            }
        )

    # Missed exceptions: if ground truth requires an Exceptions section but citations don't hit it
    required = ground_truth.get("required_citations", []) or []
    requires_exceptions = any(
        (c.get("section") or "").lower().startswith("exceptions & edge cases".lower())
        for c in required
    )
    if requires_exceptions and citation_score < 2:
        tags.append(
            {
                "type": "missed_exception",
                "reason": "Ground truth expects 'Exceptions & edge cases' but citations do not hit it.",
            }
        )

    # Outdated policy: if required citations exist but answer cites only non-required docs.
    if required and citations and citation_score < 2:
        tags.append(
            {
                "type": "outdated_policy",
                "reason": "Answer cites docs/sections different from the required ones; may be relying on older or less authoritative policy.",
            }
        )

    # Overconfident language: strong guarantees in text.
    lower_answer = answer.lower()
    if any(
        kw in lower_answer
        for kw in ["guarantee", "guaranteed", "always", "never", "will 100%", "no exceptions"]
    ):
        tags.append(
            {
                "type": "overconfident_language",
                "reason": "Answer uses strong guarantee language (always/never/guarantee) that may not match policy nuance.",
            }
        )

    # Hallucination: very confident tone with poor citations/completeness.
    if (
        lower_answer
        and accuracy_score == 0
        and completeness_score == 0
        and citation_score == 0
    ):
        tags.append(
            {
                "type": "hallucination",
                "reason": "Answer appears confident but is unsupported by ground truth or citations.",
            }
        )

    return tags

