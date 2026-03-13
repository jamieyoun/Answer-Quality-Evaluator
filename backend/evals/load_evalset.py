import json
from pathlib import Path
from typing import Dict, List, Any, Union


def _iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_questions(path: Union[str, Path]) -> List[dict]:
    """
    Load evaluation questions from a JSONL file.
    """
    p = Path(path)
    return list(_iter_jsonl(p))


def load_ground_truth(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load ground truth entries keyed by question_id from a JSONL file.
    """
    p = Path(path)
    out: Dict[str, Any] = {}
    for row in _iter_jsonl(p):
        qid = row.get("question_id")
        if qid:
            out[qid] = row
    return out

