"""Tests for brief.v1 — compact daily health summary."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def minimal_repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# test-repo\n\nA test repository.\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n\n- Initial.\n")
    (tmp_path / "VERSION").write_text("0.1.0")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test-repo"\nversion = "0.1.0"\n'
    )
    pkg = tmp_path / "test_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""test_pkg."""\n__version__ = "0.1.0"\n')
    (pkg / "core.py").write_text("def run():\n    pass\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_core.py").write_text("def test_placeholder():\n    pass\n")
    return tmp_path


# ── schema and required fields ────────────────────────────────────────────────

def test_brief_schema(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    assert data["schema"] == "brief.v1"


def test_brief_required_fields(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    for field in ["schema", "repo", "path", "generated_at", "last_commit", "health", "risks", "suggestions"]:
        assert field in data, f"missing field: {field}"


def test_brief_health_fields(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    health = data["health"]
    assert "score" in health
    assert "total" in health
    assert "label" in health
    assert health["label"] in {"good", "fair", "needs work", "unknown"}


def test_brief_risks_fields(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    risks = data["risks"]
    for field in ["high", "medium", "low", "total", "top"]:
        assert field in risks, f"risks missing field: {field}"
    assert isinstance(risks["top"], list)


def test_brief_suggestions_fields(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    suggs = data["suggestions"]
    for field in ["total", "by_risk", "top"]:
        assert field in suggs, f"suggestions missing field: {field}"
    assert isinstance(suggs["top"], list)


def test_brief_repo_name_matches_dir(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    assert data["repo"] == minimal_repo.name


def test_brief_is_json_serializable(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    serialized = json.dumps(data)
    assert json.loads(serialized)["schema"] == "brief.v1"


# ── health label ──────────────────────────────────────────────────────────────

def test_health_label_good():
    from repo_signal.brief import _health_label
    assert _health_label(18, 20) == "good"


def test_health_label_fair():
    from repo_signal.brief import _health_label
    assert _health_label(14, 20) == "fair"


def test_health_label_needs_work():
    from repo_signal.brief import _health_label
    assert _health_label(8, 20) == "needs work"


def test_health_label_unknown():
    from repo_signal.brief import _health_label
    assert _health_label(0, 0) == "unknown"


# ── format: text ──────────────────────────────────────────────────────────────

def test_format_text_contains_repo_name(minimal_repo: Path):
    from repo_signal.brief import build_brief, format_brief
    data = build_brief(minimal_repo)
    out = format_brief(data, output_format="text")
    assert minimal_repo.name in out


def test_format_text_contains_health(minimal_repo: Path):
    from repo_signal.brief import build_brief, format_brief
    data = build_brief(minimal_repo)
    out = format_brief(data, output_format="text")
    assert "Health" in out
    assert "brief.v1" in out


def test_format_text_contains_risks_section(minimal_repo: Path):
    from repo_signal.brief import build_brief, format_brief
    data = build_brief(minimal_repo)
    out = format_brief(data, output_format="text")
    assert "Risks" in out


# ── format: json ──────────────────────────────────────────────────────────────

def test_format_json_is_valid(minimal_repo: Path):
    from repo_signal.brief import build_brief, format_brief
    data = build_brief(minimal_repo)
    out = format_brief(data, output_format="json")
    parsed = json.loads(out)
    assert parsed["schema"] == "brief.v1"


# ── format: markdown ──────────────────────────────────────────────────────────

def test_format_markdown_has_heading(minimal_repo: Path):
    from repo_signal.brief import build_brief, format_brief
    data = build_brief(minimal_repo)
    out = format_brief(data, output_format="markdown")
    assert out.startswith("# Repo Brief")
    assert minimal_repo.name in out


# ── risks count consistency ───────────────────────────────────────────────────

def test_risks_total_equals_sum(minimal_repo: Path):
    from repo_signal.brief import build_brief
    data = build_brief(minimal_repo)
    r = data["risks"]
    assert r["total"] == r["high"] + r["medium"] + r["low"]


def test_top_risks_bounded(minimal_repo: Path):
    from repo_signal.brief import build_brief, MAX_RISKS
    data = build_brief(minimal_repo)
    assert len(data["risks"]["top"]) <= MAX_RISKS


def test_top_suggestions_bounded(minimal_repo: Path):
    from repo_signal.brief import build_brief, MAX_SUGGESTIONS
    data = build_brief(minimal_repo)
    assert len(data["suggestions"]["top"]) <= MAX_SUGGESTIONS
