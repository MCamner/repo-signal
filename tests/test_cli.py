import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from repo_signal.ask import build_ask_prompt
from repo_signal.core.models import Repository
from repo_signal.core.scanner import scan_repository
from repo_signal.graph.graph_builder import build_repository_graph
from repo_signal.pipeline.ask import run_ask_pipeline
from repo_signal.pipeline.context import rank_files
from repo_signal.repoaware.context_builder import build_context, extract_keywords
from repo_signal.repoaware.ranking import rank_relevant_files, read_relevant_snippet
from repo_signal.readme_score import score_readme
from repo_signal.symbols.symbol_extractor import extract_symbols


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

    def test_analyze_command_reports_front_door_summary(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        (root / "pyproject.toml").write_text("[project]\nname = 'sample'\n", encoding="utf-8")
        (root / "repo_signal").mkdir()
        (root / "repo_signal" / "cli.py").write_text("def main():\n    pass\n", encoding="utf-8")

        result = run_repo_signal(["analyze"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Repo Signal Analyze Report", result.stdout)
        self.assertIn("Project type:", result.stdout)
        self.assertIn("Python", result.stdout)
        self.assertIn("Key Entry Points", result.stdout)
        self.assertIn("Detected Tooling", result.stdout)
        self.assertIn("Suggested Focus Areas", result.stdout)

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

        self.assertEqual(result, ["mqlaunch", "routing"])

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

        self.assertIn("<repoaware>", result)
        self.assertIn("<repo>", result)
        self.assertIn("<mode>", result)
        self.assertIn("explain", result)
        self.assertIn("<git>", result)
        self.assertIn("<question>", result)
        self.assertIn("<keywords>", result)
        self.assertIn("<tree>", result)
        self.assertIn("<relevant_files>", result)
        self.assertIn("README.md", result)
        self.assertIn("launcher.py", result)
        self.assertIn('file path="launcher.py"', result)
        self.assertIn("<summary>", result)
        self.assertIn("<score>", result)
        self.assertIn("def route_mqlaunch", result)

    def test_build_context_supports_modes_and_markdown_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terminal").mkdir()
            (root / "terminal" / "mqlaunch-router.py").write_text(
                "def dispatch_mqlaunch_route(command):\n"
                "    # routing routing routing\n"
                "    return command\n",
                encoding="utf-8",
            )

            result = build_context(
                root,
                "how does mqlaunch routing work",
                mode="debug",
                output_format="markdown",
            )

        self.assertIn("# RepoAware Context", result)
        self.assertIn("- Mode: `debug`", result)
        self.assertIn("Focus on errors", result)
        self.assertIn("terminal/mqlaunch-router.py", result)
        self.assertIn("Summary:", result)
        self.assertIn("score", result)

    def test_repoaware_command_runs_through_main_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "router.py").write_text(
                "def route_request():\n"
                "    return 'ok'\n",
                encoding="utf-8",
            )

            result = run_repo_signal(
                ["repoaware", "--mode", "review", "--format", "markdown", "route request"],
                root,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("# RepoAware Context", result.stdout)
        self.assertIn("- Mode: `review`", result.stdout)
        self.assertIn("router.py", result.stdout)
        self.assertIn("route_request", result.stdout)

    def test_ranking_prioritizes_routing_code_over_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "routing\n" * 12,
                encoding="utf-8",
            )
            (root / "terminal").mkdir()
            (root / "terminal" / "launchers").mkdir()
            (root / "terminal" / "launchers" / "mqlaunch-command-mode.sh").write_text(
                "#!/usr/bin/env bash\n"
                "dispatch_cli_command() {\n"
                "  case \"$1\" in\n"
                "    routing) echo route ;;\n"
                "  esac\n"
                "}\n",
                encoding="utf-8",
            )

            ranked = rank_relevant_files(root, ["dispatch", "routing"], mode="explain")

        self.assertGreater(len(ranked), 0)
        self.assertEqual(ranked[0]["path"], "terminal/launchers/mqlaunch-command-mode.sh")
        self.assertIn("path_priority", ranked[0]["signals"])
        self.assertIn("shell_entrypoint", ranked[0]["signals"])

    def test_relevant_snippet_prefers_matching_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "tool.py"
            path.write_text(
                "\n".join(
                    ["# boring setup"] * 80
                    + [
                        "def dispatch_cli_command(command):",
                        "    if command == 'routing':",
                        "        return 'route'",
                    ]
                    + ["# trailing noise"] * 80
                ),
                encoding="utf-8",
            )

            snippet = read_relevant_snippet(path, ["dispatch", "routing"], max_lines=30)

        self.assertIn("def dispatch_cli_command", snippet)
        self.assertIn("routing", snippet)
        self.assertNotIn("\n".join(["# boring setup"] * 40), snippet)


class CoreScannerTests(unittest.TestCase):
    def test_scan_repository_detects_shared_repo_signals(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        (root / "pyproject.toml").write_text("[project]\nname = 'sample'\n", encoding="utf-8")
        (root / "repo_signal").mkdir()
        (root / "repo_signal" / "cli.py").write_text(
            "class CommandRouter:\n"
            "    pass\n\n"
            "def main():\n"
            "    pass\n",
            encoding="utf-8",
        )
        (root / "bin").mkdir()
        (root / "bin" / "sample").write_text(
            "#!/usr/bin/env bash\n"
            "run_sample() { echo sample; }\n",
            encoding="utf-8",
        )

        repo = scan_repository(root)

        self.assertEqual(repo.project_type, "Python CLI / repo intelligence toolkit")
        self.assertEqual(repo.languages["Python"], 1)
        self.assertIn("repo_signal/cli.py", repo.entrypoints)
        self.assertIn("bin/sample", repo.entrypoints)
        self.assertIn("Python packaging", repo.detected_tooling)
        self.assertGreater(repo.repo_size_files, 0)
        symbol_names = {symbol.name for symbol in repo.symbols}
        self.assertIn("CommandRouter", symbol_names)
        self.assertIn("main", symbol_names)
        self.assertIn("run_sample", symbol_names)

    def test_repository_load_is_the_central_entrypoint(self):
        temp, root = make_sample_repo()
        self.addCleanup(temp.cleanup)

        repo = Repository.load(root)

        self.assertEqual(repo.name, root.name)
        self.assertTrue(repo.files)
        self.assertIn("Markdown", repo.languages)
        self.assertIn("docs", repo.top_directories)
        self.assertEqual(repo.git.is_repo, False)
        self.assertTrue(hasattr(repo, "symbols"))

    def test_repository_load_builds_graph_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "repo_signal").mkdir()
            (root / "repo_signal" / "__init__.py").write_text("", encoding="utf-8")
            (root / "repo_signal" / "scanner.py").write_text("def scan_repository():\n    pass\n", encoding="utf-8")
            (root / "repo_signal" / "ask.py").write_text(
                "from repo_signal.scanner import scan_repository\n",
                encoding="utf-8",
            )
            (root / "scripts").mkdir()
            (root / "scripts" / "main.sh").write_text(
                "#!/usr/bin/env bash\n"
                "source lib.sh\n",
                encoding="utf-8",
            )
            (root / "scripts" / "lib.sh").write_text("helper() { echo ok; }\n", encoding="utf-8")

            repo = Repository.load(root)

        edges = {(edge.source, edge.target, edge.relation) for edge in repo.graph.edges}
        self.assertIn(("repo_signal/ask.py", "repo_signal/scanner.py", "python_import"), edges)
        self.assertIn(("scripts/main.sh", "scripts/lib.sh", "shell_source"), edges)


class GraphBuilderTests(unittest.TestCase):
    def test_build_repository_graph_extracts_python_and_shell_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            (root / "pkg" / "scanner.py").write_text("def scan_repository():\n    pass\n", encoding="utf-8")
            (root / "pkg" / "ask.py").write_text(
                "from pkg.scanner import scan_repository\n"
                "import pkg.scanner\n",
                encoding="utf-8",
            )
            (root / "bin").mkdir()
            (root / "bin" / "run.sh").write_text(
                "#!/usr/bin/env bash\n"
                ". ../scripts/env.sh\n"
                "bash ../scripts/tool.sh\n",
                encoding="utf-8",
            )
            (root / "scripts").mkdir()
            (root / "scripts" / "env.sh").write_text("export DEMO=1\n", encoding="utf-8")
            (root / "scripts" / "tool.sh").write_text("echo tool\n", encoding="utf-8")

            repo = scan_repository(root)
            graph = build_repository_graph(repo)

        edges = {(edge.source, edge.target, edge.relation) for edge in graph.edges}
        self.assertIn(("pkg/ask.py", "pkg/scanner.py", "python_import"), edges)
        self.assertIn(("bin/run.sh", "scripts/env.sh", "shell_source"), edges)
        self.assertIn(("bin/run.sh", "scripts/tool.sh", "shell_exec"), edges)


class SymbolExtractorTests(unittest.TestCase):
    def test_extract_symbols_finds_python_classes_functions_and_shell_functions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            py_path = root / "tool.py"
            py_path.write_text(
                "class Runner:\n"
                "    pass\n\n"
                "async def run_async():\n"
                "    pass\n\n"
                "def scan_repository():\n"
                "    pass\n",
                encoding="utf-8",
            )
            sh_path = root / "tool.sh"
            sh_path.write_text(
                "#!/usr/bin/env bash\n"
                "dispatch_cli_command() {\n"
                "  echo ok\n"
                "}\n\n"
                "function mq_repoaware {\n"
                "  echo context\n"
                "}\n",
                encoding="utf-8",
            )

            py_symbols = extract_symbols(py_path, repo_path=root)
            sh_symbols = extract_symbols(sh_path, repo_path=root)

        by_name = {symbol.name: symbol for symbol in py_symbols + sh_symbols}
        self.assertEqual(by_name["Runner"].kind, "class")
        self.assertEqual(by_name["Runner"].file_path, "tool.py")
        self.assertEqual(by_name["run_async"].kind, "function")
        self.assertEqual(by_name["scan_repository"].line, 6)
        self.assertEqual(by_name["dispatch_cli_command"].kind, "shell_function")
        self.assertEqual(by_name["dispatch_cli_command"].file_path, "tool.sh")
        self.assertEqual(by_name["mq_repoaware"].kind, "shell_function")


class AskCommandTests(unittest.TestCase):
    def test_build_ask_prompt_uses_repoaware_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "router.py").write_text(
                "def route_request():\n"
                "    return 'ok'\n",
                encoding="utf-8",
            )

            prompt = build_ask_prompt(root, "how does routing work")

        self.assertIn("You are repo-signal", prompt)
        self.assertIn("<question>", prompt)
        self.assertIn("how does routing work", prompt)
        self.assertIn("# RepoAware Context", prompt)
        self.assertIn("router.py", prompt)

    def test_ask_command_dry_run_does_not_require_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "router.py").write_text(
                "def route_request():\n"
                "    return 'ok'\n",
                encoding="utf-8",
            )

            result = run_repo_signal(["ask", "--dry-run", "how does routing work"], root)

        self.assertEqual(result.returncode, 0)
        self.assertIn("You are repo-signal", result.stdout)
        self.assertIn("# RepoAware Context", result.stdout)
        self.assertIn("router.py", result.stdout)

    def test_pipeline_rank_files_populates_repository_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "router.py").write_text(
                "def dispatch_route(command):\n"
                "    if command == 'routing':\n"
                "        return 'ok'\n",
                encoding="utf-8",
            )

            repo = Repository.load(root)
            signals = rank_files(repo, "how does routing dispatch work")

        self.assertGreater(len(signals), 0)
        self.assertEqual(repo.signals, signals)
        self.assertEqual(signals[0].file_path, "router.py")
        self.assertGreater(signals[0].score, 0)
        self.assertTrue(signals[0].reasons)

    def test_ask_pipeline_runs_scan_rank_context_and_provider(self):
        class FakeProvider:
            def __init__(self):
                self.prompt = ""

            def generate(self, prompt):
                self.prompt = prompt
                return (
                    "Summary\n"
                    "Uses routing code.\n\n"
                    "Referenced files\n"
                    "- router.py\n\n"
                    "Architecture notes\n"
                    "- Small command surface.\n\n"
                    "Answer\n"
                    "The dispatch route function handles routing."
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "router.py").write_text(
                "def dispatch_route(command):\n"
                "    if command == 'routing':\n"
                "        return 'ok'\n",
                encoding="utf-8",
            )
            provider = FakeProvider()

            result = run_ask_pipeline(
                repo_path=root,
                question="how does routing work",
                mode="debug",
                provider=provider,
            )

        self.assertEqual(result.repo.name, root.name)
        self.assertIn("router.py", result.referenced_files)
        self.assertIn("# RepoAware Context", result.context)
        self.assertIn("routing and control flow", result.prompt)
        self.assertIn("router.py", provider.prompt)
        self.assertIn("The dispatch route function", result.answer)


if __name__ == "__main__":
    unittest.main()
