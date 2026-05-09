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
        "landing",
        "docs",
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
        return None

    return best


def main():
    if len(sys.argv) < 2:
        print("Usage: skill_router.py '<question>'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    skill = detect_skill(question)

    print()
    print("QUESTION")
    print("────────")
    print(question)
    print()

    if skill:
        print(f"ROUTED SKILL: {skill}")
        print()

        skill_path = Path.home() / ".codex" / "skills" / skill / "SKILL.md"

        if skill_path.exists():
            print("SKILL PATH")
            print("──────────")
            print(skill_path)
        else:
            print("Skill exported but not installed in ~/.codex/skills")
    else:
        print("No matching skill.")
        print("Fallback: generic repo-aware reasoning.")


if __name__ == "__main__":
    main()
