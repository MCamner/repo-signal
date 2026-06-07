"""mq-agent safe consumer pattern for repo-signal inspect.v1 and doctor.v1."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_signal_command() -> list[str]:
    """Prefer the current Python environment, then fall back to PATH."""
    try:
        import repo_signal  # noqa: F401
    except ImportError:
        return ["repo-signal"]
    return [sys.executable, "-m", "repo_signal.cli"]


def inspect(repo_path: str | Path = ".") -> dict | None:
    """Return inspect.v1 dict or None if unavailable."""
    try:
        result = subprocess.run(
            [*_repo_signal_command(), "inspect", "--json", str(repo_path)],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "inspect.v1":
        return None
    return data


def doctor(repo_path: str | Path = ".") -> dict | None:
    """Return doctor.v1 dict or None if unavailable."""
    try:
        result = subprocess.run(
            [*_repo_signal_command(), "doctor", "--json", str(repo_path)],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "doctor.v1":
        return None
    return data


def repo_summary(repo_path: str | Path = ".") -> str:
    """Return a one-line repo summary for logging or display."""
    data = inspect(repo_path)
    if not data:
        return f"(repo-signal unavailable for {repo_path})"
    name = data["repo"]["name"]
    score = data.get("public_readiness", {}).get("score", "?")
    branch = data.get("git", {}).get("branch", "?")
    clean = data.get("git", {}).get("clean", None)
    state = "clean" if clean else "dirty"
    return f"{name}  score={score}  branch={branch}  {state}"


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(repo_summary(path))
