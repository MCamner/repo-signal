"""`release.sh --publish-wiki` publishes the wiki Command-Reference after a tag.

Releases land through pull requests, and the wiki push lived only inside
`--publish`, which tags and pushes main itself. So 1.4.2 through 1.7.1 shipped
without one wiki commit: the published page listed 16 commands while the code
had 26. The post-merge step is its own command, gated on the tag.

The proof is the state of a bare wiki remote, not a log of commands.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

GENERATOR_STUB = """\
from pathlib import Path
out = Path.home() / "repo-signal.wiki" / "Command-Reference.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("stub for " + Path("VERSION").read_text().strip() + "\\n")
"""


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _setup(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    env = {
        **os.environ,
        "HOME": str(tmp_path / "home"),
        "GIT_CONFIG_GLOBAL": str(tmp_path / "gitconfig"),
        "GIT_AUTHOR_NAME": "Smoke",
        "GIT_AUTHOR_EMAIL": "smoke@example.invalid",
        "GIT_COMMITTER_NAME": "Smoke",
        "GIT_COMMITTER_EMAIL": "smoke@example.invalid",
    }
    (tmp_path / "gitconfig").write_text("")

    remote = tmp_path / "wiki.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True, env=env)
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/master")
    seed = tmp_path / "seed"
    seed.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=seed, check=True, env=env)
    _git(seed, "symbolic-ref", "HEAD", "refs/heads/master")
    (seed / "Command-Reference.md").write_text("old\n")
    subprocess.run(["git", "add", "-A"], cwd=seed, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=seed, check=True, env=env)
    subprocess.run(["git", "push", "-q", str(remote), "master"], cwd=seed, check=True, env=env)

    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "release.sh", repo / "release.sh")
    (repo / "VERSION").write_text("1.0.0\n")
    (repo / "tools" / "generate_wiki_command_ref.py").write_text(GENERATOR_STUB)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True, env=env)

    env["REPO_SIGNAL_WIKI_REMOTE"] = str(remote)
    env["PYTHON_BIN"] = "python3"
    return repo, remote, env


def _run(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "release.sh", "--publish-wiki"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )


def test_publish_wiki_refuses_without_tag(tmp_path: Path) -> None:
    repo, remote, env = _setup(tmp_path)
    before = _git(remote, "rev-parse", "refs/heads/master")

    result = _run(repo, env)

    assert result.returncode != 0
    assert "Tag v1.0.0 does not exist" in result.stdout + result.stderr
    assert _git(remote, "rev-parse", "refs/heads/master") == before


def test_publish_wiki_refuses_when_head_is_not_the_tag(tmp_path: Path) -> None:
    # The 1.8.0 attempt: the bump was skipped, VERSION still said 1.7.1, and
    # v1.7.1 existed — on an older commit. The gate only asked whether the tag
    # existed, so it published HEAD's page labelled as v1.7.1.
    repo, remote, env = _setup(tmp_path)
    subprocess.run(["git", "tag", "-a", "v1.0.0", "-m", "v1.0.0"], cwd=repo, check=True, env=env)
    (repo / "later.txt").write_text("later\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "later"], cwd=repo, check=True, env=env)
    before = _git(remote, "rev-parse", "refs/heads/master")

    result = _run(repo, env)

    assert result.returncode != 0
    assert "HEAD is not v1.0.0" in result.stdout + result.stderr
    assert _git(remote, "rev-parse", "refs/heads/master") == before


def test_publish_wiki_pushes_after_tag(tmp_path: Path) -> None:
    repo, remote, env = _setup(tmp_path)
    subprocess.run(["git", "tag", "-a", "v1.0.0", "-m", "v1.0.0"], cwd=repo, check=True, env=env)

    result = _run(repo, env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(remote, "log", "-1", "--format=%s", "refs/heads/master") == (
        "Update Command-Reference for v1.0.0"
    )
    assert "stub for 1.0.0" in _git(remote, "show", "refs/heads/master:Command-Reference.md")
    assert _git(repo, "status", "--porcelain") == ""
