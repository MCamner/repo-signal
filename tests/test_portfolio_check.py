import json
from pathlib import Path


from repo_signal.portfolio_check import check_portfolio, load_portfolio_config


def _make_publish_ready_repo(path: Path) -> None:
    (path / "docs" / "screenshots").mkdir(parents=True)
    (path / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
    (path / "README.md").write_text(
        "# Demo\n\n## Quick Start\n\nDemo with screenshots and gallery.\n\n"
        "Roadmap and safe sharing notes included.\n\nGitHub Pages enabled.\n",
        encoding="utf-8",
    )
    (path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (path / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (path / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")
    (path / "docs" / "index.html").write_text("<h1>Demo</h1>\n", encoding="utf-8")
    (path / "docs" / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")


def _write_config(config: Path, repo: Path, fail_under: int = 14) -> None:
    config.write_text(
        f"portfolio:\n  repos:\n    - name: demo\n      path: {repo}\n      fail_under: {fail_under}\n",
        encoding="utf-8",
    )


def test_portfolio_text_ok(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _make_publish_ready_repo(repo)
    config = tmp_path / "repo-signal.yml"
    _write_config(config, repo)

    output = check_portfolio(str(config))

    assert "PORTFOLIO CHECK" in output
    assert "demo" in output
    assert "OK" in output


def test_portfolio_json_ok(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _make_publish_ready_repo(repo)
    config = tmp_path / "repo-signal.yml"
    _write_config(config, repo)

    data = json.loads(check_portfolio(str(config), output_format="json"))

    assert data["object"] == "portfolio_check"
    assert data["repos"][0]["name"] == "demo"
    assert data["repos"][0]["status"] == "OK"


def test_portfolio_markdown_ok(tmp_path: Path) -> None:
    repo = tmp_path / "demo"
    repo.mkdir()
    _make_publish_ready_repo(repo)
    config = tmp_path / "repo-signal.yml"
    _write_config(config, repo)

    output = check_portfolio(str(config), output_format="markdown")

    assert "# Portfolio Check" in output
    assert "| demo |" in output


def test_portfolio_warn_below_threshold(tmp_path: Path) -> None:
    repo = tmp_path / "bare"
    repo.mkdir()
    (repo / "README.md").write_text("# Bare\n", encoding="utf-8")
    config = tmp_path / "repo-signal.yml"
    _write_config(config, repo, fail_under=14)

    data = json.loads(check_portfolio(str(config), output_format="json"))

    assert data["repos"][0]["status"] == "WARN"
    assert data["repos"][0]["score"] < 14


def test_portfolio_missing_repo(tmp_path: Path) -> None:
    config = tmp_path / "repo-signal.yml"
    _write_config(config, tmp_path / "nonexistent")

    output = check_portfolio(str(config))

    assert "MISSING" in output


def test_portfolio_invalid_format(tmp_path: Path) -> None:
    config = tmp_path / "repo-signal.yml"
    _write_config(config, tmp_path / "x")

    with pytest.raises(ValueError, match="Unsupported format"):
        check_portfolio(str(config), output_format="xml")


def test_load_config_no_file(tmp_path: Path) -> None:
    repos = load_portfolio_config(str(tmp_path / "missing.yml"))
    assert len(repos) == 1
    assert repos[0].fail_under == 14


def test_load_config_multiple_repos(tmp_path: Path) -> None:
    config = tmp_path / "repo-signal.yml"
    config.write_text(
        "portfolio:\n  repos:\n"
        "    - name: a\n      path: ~/a\n      fail_under: 12\n"
        "    - name: b\n      path: ~/b\n      fail_under: 10\n",
        encoding="utf-8",
    )
    repos = load_portfolio_config(str(config))
    assert len(repos) == 2
    assert repos[0].name == "a"
    assert repos[0].fail_under == 12
    assert repos[1].name == "b"
    assert repos[1].fail_under == 10
