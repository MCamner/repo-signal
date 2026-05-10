#!/usr/bin/env python3

from pathlib import Path
import re
import sys


ROUTES = {
    "release-readiness": [
        "release",
        "tag",
        "publish",
        "deploy",
        "version",
        "changelog",
        "ready",
    ],
    "repo-aware": [
        "repo",
        "architecture",
        "analyze",
        "debug",
        "structure",
        "workflow",
    ],
    "repo-product-auditor": [
        "readme",
        "positioning",
        "product",
        "onboarding",
        "docs",
        "landing",
    ],
    "terminal-ui-polisher": [
        "terminal",
        "ui",
        "menu",
        "dashboard",
        "mqlaunch",
        "ascii",
    ],
}


def detect_skill(text: str):
    text = text.lower()
    scores = {}

    for skill, keywords in ROUTES.items():
        score = 0

        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                score += 1

        scores[skill] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "repo-aware"

    return best


def load_skill(skill: str):
    candidates = [
        Path.home() / ".codex" / "skills" / skill / "SKILL.md",
        Path.cwd() / "skills" / skill / "SKILL.md",
    ]

    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8"), path

    return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: build_prompt.py '<question>'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    skill = detect_skill(question)
    skill_content, skill_path = load_skill(skill)

    if not skill_content:
        print(f"ERROR: skill not found: {skill}")
        sys.exit(1)

    final_prompt = f"""Use {skill}.

{skill_content}

User question:
{question}
"""

    print("SKILL")
    print("─────")
    print(skill)
    print()

    print("SOURCE")
    print("──────")
    print(skill_path)
    print()

    print("FINAL PROMPT")
    print("────────────")
    print(final_prompt)


if __name__ == "__main__":
    main()
