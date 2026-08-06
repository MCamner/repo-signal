from pathlib import Path

from repo_signal.publish_checklist import build_publish_checklist


def _check(root: Path, name: str) -> dict:
    checklist = build_publish_checklist(str(root))
    for check in checklist["checks"]:
        if check["name"] == name:
            return check
    raise AssertionError(f"check not found: {name}")


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    return tmp_path


def test_empty_screenshots_folder_does_not_pass(tmp_path):
    """An empty folder is not a screenshot.

    The check used to test only that docs/screenshots/ existed, so `mkdir` was
    enough to score the point while the gallery stayed empty.
    """
    root = _repo(tmp_path)
    (root / "docs" / "screenshots").mkdir(parents=True)

    assert _check(root, "docs screenshots folder exists")["status"] == "warn"


def test_screenshots_folder_with_an_image_passes(tmp_path):
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "runtime.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    assert _check(root, "docs screenshots folder exists")["status"] == "ok"


def test_non_image_files_do_not_count_as_screenshots(tmp_path):
    root = _repo(tmp_path)
    shots = root / "docs" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "README.md").write_text("screenshots go here\n", encoding="utf-8")

    assert _check(root, "docs screenshots folder exists")["status"] == "warn"


def test_missing_screenshots_folder_still_warns(tmp_path):
    root = _repo(tmp_path)

    assert _check(root, "docs screenshots folder exists")["status"] == "warn"
