#!/usr/bin/env python
import sys
from pathlib import Path


def main() -> int:
    backend_dir = Path(__file__).resolve().parents[1] / "backend"
    runs_dir = backend_dir / "eval_runs"
    if not runs_dir.exists():
        print("No eval_runs directory found.", file=sys.stderr)
        return 1

    candidates = sorted(runs_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print("No eval run files found.", file=sys.stderr)
        return 1

    latest = candidates[0].stem  # filename without extension = run_id
    print(latest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

