from pathlib import Path


DEFAULT_WORKFLOW = """name: Publish Checklist

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  publish-checklist:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install repo-signal
        run: |
          python -m pip install --upgrade pip
          pip install git+https://github.com/MCamner/repo-signal.git

      - name: Run publish checklist
        run: |
          repo-signal publish-checklist . --fail-under 14
"""


def init_actions_workflow(
    repo_path: str = ".",
    fail_under: int = 14,
    force: bool = False,
) -> str:
    repo = Path(repo_path).resolve()
    workflow_dir = repo / ".github" / "workflows"
    workflow_file = workflow_dir / "publish-checklist.yml"

    workflow = DEFAULT_WORKFLOW.replace("--fail-under 14", f"--fail-under {fail_under}")

    if workflow_file.exists() and not force:
        return "\n".join(
            [
                "ACTIONS INIT",
                "============",
                f"Repo: {repo.name}",
                f"Workflow: {workflow_file.relative_to(repo)}",
                "",
                "Status",
                "------",
                "Workflow already exists.",
                "",
                "Next action",
                "-----------",
                "Use --force to overwrite it.",
            ]
        )

    workflow_dir.mkdir(parents=True, exist_ok=True)
    workflow_file.write_text(workflow, encoding="utf-8")

    return "\n".join(
        [
            "ACTIONS INIT",
            "============",
            f"Repo: {repo.name}",
            f"Workflow: {workflow_file.relative_to(repo)}",
            f"Fail-under: {fail_under}",
            "",
            "Written files",
            "-------------",
            f"- {workflow_file.relative_to(repo)}",
            "",
            "Next action",
            "-----------",
            "Review the workflow, then commit it if it matches your repo policy.",
        ]
    )
