#!/usr/bin/env python3
"""Fail closed when a release-check/CI mapping changes without review.

Uses only the standard library and never runs workflow commands. CI-only work
must be listed with a written reason; release-check.sh remains read-only.
"""
from __future__ import annotations

import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI_ONLY = {
    "markdownlint.yml": "CI-only: Node markdownlint action; local READY does not attest Markdown style.",
    "packaging.yml": "CI-only: isolated build, install and uv tool smoke need fresh runner environments.",
    "pypi.yml": "CI-only: manual package publication and credentials, not a PR preflight.",
    "testpypi.yml": "CI-only: manual TestPyPI publication and credentials, not a PR preflight.",
    "release.yml": "CI-only: publishes tagged releases after preflight, not a PR assertion.",
}
STEPS = {
    "examples.yml": ["Check out repository", "Set up Python", "Install package",
                     "Check generated examples", "Check skills consistency"],
    "tests.yml": ["Check out repository", "Set up Python", "Install package", "Run tests",
                  "Check out repository under a different directory name", "Set up Python",
                  "Install package", "Run tests", "Check out repository", "Set up Python",
                  "Install package", "Docs and version consistency"],
    "publish-checklist.yml": ["Check out repository", "Set up Python", "Install repo-signal",
                              "Run publish checklist"],
    "gate-parity.yml": ["Checkout", "Validate gate parity", "Test gate parity failures"],
}
CI_COMMANDS = {
    "examples.yml": ["scripts/check-generated-examples.sh", "scripts/check-skills.sh"],
    "tests.yml": ["python -m pytest tests/ -v", "./scripts/check-docs-consistency.sh"],
    "publish-checklist.yml": ["pip install -e .", "repo-signal publish-checklist . --fail-under 14"],
    "gate-parity.yml": ["python3 scripts/check-gate-parity.py", "python3 scripts/check-gate-parity.py --self-test"],
}
LOCAL_COMMANDS = {
    "docs": 'run "check-docs-consistency.sh" bash scripts/check-docs-consistency.sh',
    "tests": 'run "pytest" "$PYTHON_BIN" -m pytest -q',
    "examples": 'run "check-generated-examples.sh" env PYTHON_BIN="$PYTHON_BIN" bash scripts/check-generated-examples.sh',
    "skills": 'run "check-skills.sh" bash scripts/check-skills.sh',
    "publish": 'run "publish-checklist" "$PYTHON_BIN" -m repo_signal.cli publish-checklist . --fail-under 14',
    "parity": 'run "check-gate-parity.py" "$PYTHON_BIN" scripts/check-gate-parity.py',
}


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    workflows = root / ".github" / "workflows"
    files = {p.name for p in workflows.glob("*.yml")} | {p.name for p in workflows.glob("*.yaml")}
    expected = set(STEPS) | set(CI_ONLY)
    for name in sorted(files - expected):
        errors.append(f"undeclared workflow: {name}")
    for name in sorted(expected - files):
        errors.append(f"declared workflow missing: {name}")
    for name, reason in CI_ONLY.items():
        if not reason.strip() or not reason.startswith("CI-only:"):
            errors.append(f"CI-only workflow lacks a written reason: {name}")
    for name, expected_steps in STEPS.items():
        path = workflows / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        actual = re.findall(r"^\s*- name:\s*(.+?)\s*$", text, re.M)
        if Counter(actual) != Counter(expected_steps):
            errors.append(f"workflow steps changed without parity review: {name}: {actual!r}")
        for command in CI_COMMANDS[name]:
            if command not in text:
                errors.append(f"workflow command missing: {name}: {command}")
    gate = root / "release-check.sh"
    if not gate.is_file():
        errors.append("release-check.sh missing")
    else:
        text = gate.read_text(encoding="utf-8")
        for name, command in LOCAL_COMMANDS.items():
            if command not in text:
                errors.append(f"local gate missing {name}: {command}")
    return errors


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (root / "release-check.sh").write_text("\n".join(LOCAL_COMMANDS.values()))
        for name, steps in STEPS.items():
            content = "\n".join(f"      - name: {step}" for step in steps)
            content += "\n" + "\n".join(CI_COMMANDS[name])
            (workflows / name).write_text(content)
        for name in CI_ONLY:
            (workflows / name).write_text("# CI-only\n")
        assert not verify(root), verify(root)
        gate = root / "release-check.sh"
        original = gate.read_text()
        gate.write_text(original.replace(LOCAL_COMMANDS["skills"], ""))
        assert any("local gate missing skills" in e for e in verify(root))
        gate.write_text(original)
        path = workflows / "examples.yml"
        original = path.read_text()
        path.write_text(original.replace("      - name: Check skills consistency", ""))
        assert any("workflow steps changed" in e for e in verify(root))
        path.write_text(original.replace("scripts/check-skills.sh", ""))
        assert any("workflow command missing" in e for e in verify(root))
        path.write_text(original)
        (workflows / "new.yml").write_text("on: push\n")
        assert any("undeclared workflow" in e for e in verify(root))
    print("PASS: baseline, missing local check, removed CI step/command, unknown workflow")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        raise SystemExit(self_test())
    if len(sys.argv) > 1:
        raise SystemExit("usage: check-gate-parity.py [--self-test]")
    failures = verify(ROOT)
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        raise SystemExit(1)
    print("PASS: release-check/CI gate parity; CI-only workflows explicitly documented")
