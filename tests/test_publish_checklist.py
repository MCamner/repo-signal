"""The screenshot check must require a screenshot, not a directory entry."""

from pathlib import Path

from repo_signal.publish_checklist import build_publish_checklist

CHECK = "docs screenshots folder exists"


def _check(root: Path, name: str) -> dict:
    checklist = build_publish_checklist(str(root))
    for check in checklist["checks"]:
        if check["name"] == name:
            return check
    raise AssertionError(f"check not found: {name}")


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    return tmp_path


def test_missing_screenshots_folder_does_not_pass(tmp_path):
    assert _check(_repo(tmp_path), CHECK)["status"] == "warn"


def test_empty_screenshots_folder_does_not_pass(tmp_path):
    """An empty folder is not a screenshot.

    The check used to test only that docs/screenshots/ existed, so `mkdir` was
    enough to score the point while the gallery stayed empty — and the fix plan
    handed the user that exact command.
    """
    root = _repo(tmp_path)
    (root / "docs" / "screenshots").mkdir(parents=True)

    assert _check(root, CHECK)["status"] == "warn"


def test_screenshots_folder_with_an_image_passes(tmp_path):
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "runtime.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    assert _check(root, CHECK)["status"] == "ok"


def test_non_image_files_do_not_count_as_screenshots(tmp_path):
    """A placeholder README is the most common way the folder looks non-empty."""
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "README.md").write_text("screenshots go here\n", encoding="utf-8")

    assert _check(root, CHECK)["status"] == "warn"


def test_image_in_a_subdirectory_counts(tmp_path):
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots" / "v2"
    shots.mkdir(parents=True)
    (shots / "runtime.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    assert _check(root, CHECK)["status"] == "ok"


def test_uppercase_extension_counts(tmp_path):
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "RUNTIME.PNG").write_bytes(b"\x89PNG\r\n\x1a\n")

    assert _check(root, CHECK)["status"] == "ok"


def test_a_file_named_screenshots_is_not_a_gallery(tmp_path):
    """`docs/screenshots` as a file used to satisfy an .exists() check."""
    root = _repo(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "screenshots").write_text("not a folder\n", encoding="utf-8")

    assert _check(root, CHECK)["status"] == "warn"


def test_fix_plan_asks_for_a_real_screenshot(tmp_path):
    """The old fix plan said `mkdir -p docs/screenshots`, which no longer passes."""
    from repo_signal.publish_checklist import build_fix_plan

    root = _repo(tmp_path)
    plan = build_fix_plan(build_publish_checklist(str(root)))
    screenshot_steps = [step for step in plan if "screenshots" in step]

    assert screenshot_steps
    assert not any(step.strip() == "mkdir -p docs/screenshots" for step in screenshot_steps)
