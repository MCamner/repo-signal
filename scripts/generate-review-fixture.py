#!/usr/bin/env python3
"""Generate the public-safe `repo-review.v1` fixture under `examples/`.

The fixture is a release contract artifact: it shows consumers the exact shape
`repo-signal review-export` writes, without touching a real mqobsidian vault and
without carrying anything machine-specific.

Its input is deliberately synthetic and fixed — a real inspect run would embed
this machine's paths and this repo's current state, and the fixture would churn
on every commit. Run with `--check` to verify the committed file still matches.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from repo_signal.review_export import build_repo_review  # noqa: E402

FIXTURE = REPO_ROOT / "examples" / "review-export" / "repo-review.v1.md"
CREATED_AT = "2026-01-01T00:00:00Z"

SAMPLE_INSPECT = {
    "schema": "inspect.v1",
    "repo": {"name": "example-repo", "path": "example-repo", "exists": True},
    "git": {"branch": "main", "clean": True},
    "public_readiness": {"summary": "13/16 WARN", "status": "warn"},
    "issues": [
        {"level": "fail", "message": "CHANGELOG.md is missing"},
        {"level": "warn", "message": "README has no installation section"},
        {"level": "info", "message": "No demo output committed"},
    ],
    "recommended_next_commit": (
        "docs: add CHANGELOG.md and a README installation section"
    ),
}


def render() -> str:
    return build_repo_review(SAMPLE_INSPECT, created_at=CREATED_AT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed fixture matches, without writing",
    )
    args = parser.parse_args()

    content = render()

    if args.check:
        if not FIXTURE.exists():
            print(f"missing fixture: {FIXTURE.relative_to(REPO_ROOT)}")
            return 1
        current = FIXTURE.read_text(encoding="utf-8")
        if current != content:
            print(f"fixture is stale: {FIXTURE.relative_to(REPO_ROOT)}")
            print("regenerate with: scripts/generate-review-fixture.py")
            return 1
        print(f"fixture current: {FIXTURE.relative_to(REPO_ROOT)}")
        return 0

    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(content, encoding="utf-8")
    print(f"wrote {FIXTURE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
