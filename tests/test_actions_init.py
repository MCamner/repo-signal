from pathlib import Path

from repo_signal.actions_init import init_actions_workflow


def test_actions_init_writes_workflow(tmp_path: Path):
    result = init_actions_workflow(str(tmp_path), fail_under=12)

    workflow = tmp_path / ".github" / "workflows" / "publish-checklist.yml"

    assert workflow.exists()
    workflow_text = workflow.read_text(encoding="utf-8")
    assert "pip install git+https://github.com/MCamner/repo-signal.git" in workflow_text
    assert "repo-signal publish-checklist . --fail-under 12" in workflow_text
    assert "ACTIONS INIT" in result


def test_actions_init_does_not_overwrite_without_force(tmp_path: Path):
    workflow = tmp_path / ".github" / "workflows" / "publish-checklist.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("custom workflow", encoding="utf-8")

    result = init_actions_workflow(str(tmp_path), fail_under=12, force=False)

    assert workflow.read_text(encoding="utf-8") == "custom workflow"
    assert "Workflow already exists" in result


def test_actions_init_overwrites_with_force(tmp_path: Path):
    workflow = tmp_path / ".github" / "workflows" / "publish-checklist.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("custom workflow", encoding="utf-8")

    init_actions_workflow(str(tmp_path), fail_under=10, force=True)

    assert "repo-signal publish-checklist . --fail-under 10" in workflow.read_text(
        encoding="utf-8"
    )
