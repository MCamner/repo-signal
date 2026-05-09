import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from repo_signal.repoaware.context_builder import build_context, extract_keywords
from repo_signal.readme_score import score_readme


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_repo_signal(args, cwd):
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"

    return subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def make_sample_repo():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)

    readme = """# sample-repo

A small sample repo used for testing.

---

## Why this exists

To test repo-signal.

---

## Quick start

Run:

    echo hello

---

## Current features

- scan
- report

---

## Roadmap

- improve

---

## License

MIT
"""

    (root / "README.md").write_text(readme, encoding="utf-8")
    (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (root / ".gitignore").write_text(
        ".DS_Store\n__pycache__/\n*.pyc\n.venv/\n.env\nnode_modules/\n",
        encoding="utf-8",
    )

    (root / "docs").mkdir()
    (root / "docs" / "index.html").write_text("<h1>sample</h1>\n", encoding="utf-8")

    return temp, root


class RepoSignalCLITests(unittest.TestCase):
    def test_help_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_repo_signal(["--help"], tmp)

        self.assertEqual(result.returncode, 0)
        self.assertIn("repo-signal", result.stdout)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("scan", result.stdout)
        self.assertIn("readme", result.stdout)

    def test_version_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_repo_signal(["--version"], tmp)

        self.assertEqual(result.returncode, 0)
        self.assertIn("repo-signal", result.stdout)

    def test_scan_command_detects_core_files(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        result = run_repo_signal(["scan"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Repo Signal Report", result.stdout)
        self.assertIn("[OK] README exists", result.stdout)
        self.assertIn("[OK] License exists", result.stdout)
        self.assertIn("[OK] .gitignore exists", result.stdout)
        self.assertIn("[OK] docs folder exists", result.stdout)

    def test_readme_command_scores_readme(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        result = run_repo_signal(["readme"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# README Signal Report", result.stdout)
        self.assertIn("README score", result.stdout)
        self.assertIn("[OK] quick start", result.stdout)
        self.assertIn("[OK] roadmap", result.stdout)
        self.assertIn("[OK] license", result.stdout)

    def test_score_readme_returns_100_point_checklist(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        readme = """# sample-repo

[![Tests](https://example.com/tests.svg)](https://example.com)

A useful command-line helper for checking repository documentation health.

## Installation

Install with pipx.

## Usage

Run the CLI against a repo.

## Examples

```bash
repo-signal readme-score .
```

## Screenshots

![demo](docs/demo.png)

## License

MIT

## Roadmap

- Improve recommendations

## Contributing

Issues and patches are welcome.
"""
        (root / "README.md").write_text(readme, encoding="utf-8")

        result = score_readme(str(root))

        self.assertEqual(result["score"], 100)
        self.assertEqual(result["missing"], [])
        self.assertTrue(result["checks"]["title"])
        self.assertTrue(result["checks"]["short_pitch"])

    def test_readme_score_command_accepts_path(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        result = run_repo_signal(["readme-score", str(root)], REPO_ROOT)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# README Score Report", result.stdout)
        self.assertIn("README score:", result.stdout)
        self.assertIn("[OK] title", result.stdout)
        self.assertIn("Missing:", result.stdout)

    def test_hygiene_command_detects_ds_store(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        (root / ".DS_Store").write_text("finder junk\n", encoding="utf-8")

        result = run_repo_signal(["hygiene"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Hygiene Signal Report", result.stdout)
        self.assertIn(".DS_Store", result.stdout)

    def test_wiki_command_generates_wiki_plan(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        result = run_repo_signal(["wiki"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Wiki Signal Report", result.stdout)
        self.assertIn("Recommended wiki pages", result.stdout)
        self.assertIn("Wiki Home draft", result.stdout)

    def test_roadmap_command_generates_roadmap(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        result = run_repo_signal(["roadmap"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Roadmap Signal Report", result.stdout)
        self.assertIn("Suggested roadmap", result.stdout)
        self.assertIn("Recommended next commit", result.stdout)

    def test_unknown_command_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_repo_signal(["does-not-exist"], tmp)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown command", result.stdout)


class RepoAwareTests(unittest.TestCase):
    def test_extract_keywords_preserves_order_and_deduplicates(self):
        result = extract_keywords("How does mqlaunch routing routing work?")

        self.assertEqual(result, ["how", "does", "mqlaunch", "routing", "work"])

    def test_build_context_includes_repo_state_and_relevant_snippet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# demo\n\nRouting overview.\n", encoding="utf-8")
            (root / "launcher.py").write_text(
                "def route_mqlaunch(command):\n"
                "    return command\n",
                encoding="utf-8",
            )

            result = build_context(root, "how does mqlaunch routing work")

        self.assertIn("<repo>", result)
        self.assertIn("<git>", result)
        self.assertIn("<question>", result)
        self.assertIn("<tree>", result)
        self.assertIn("<relevant_files>", result)
        self.assertIn("README.md", result)
        self.assertIn("launcher.py", result)
        self.assertIn('file path="launcher.py"', result)
        self.assertIn("def route_mqlaunch", result)


if __name__ == "__main__":
    unittest.main()
