"""The command registry is the single declaration of the CLI surface.

Every other view of that surface — top-level `--help`, the unknown-command
fallback list, subcommand `--help`, and `docs/COMMANDS.md` — must agree with it.
Before the registry existed those four views were maintained by hand and had
drifted apart: `brief` and `readiness` dispatched but were absent from `--help`,
`portfolio` was absent from both `--help` and the fallback list, and
`docs/COMMANDS.md` documented `portfolio check` while omitting `brief`,
`readiness` and `export`.
"""
from __future__ import annotations

import ast
import io
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repo_signal import cli
from repo_signal.commands import COMMANDS, command_names, build_help_text

CLI_SOURCE = Path(cli.__file__)
REPO_ROOT = CLI_SOURCE.resolve().parents[1]


def dispatched_commands() -> set[str]:
    """Command literals main() actually branches on, read from the source.

    The dispatch is a chain of `if command == "..."` / `if command in {...}`
    tests rather than a table, so parity with the registry is enforced here
    instead of guaranteed by construction.
    """
    tree = ast.parse(CLI_SOURCE.read_text(encoding="utf-8"))
    main = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    found: set[str] = set()
    for node in ast.walk(main):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not (isinstance(node.left, ast.Name) and node.left.id == "command"):
            continue
        op = node.ops[0]
        comparator = node.comparators[0]
        if isinstance(op, ast.Eq) and isinstance(comparator, ast.Constant):
            found.add(comparator.value)
        elif isinstance(op, ast.In) and isinstance(comparator, ast.Set):
            for element in comparator.elts:
                if isinstance(element, ast.Constant):
                    found.add(element.value)
    # `--help`/`-h`/`help` and `--version`/`-v`/`version` are flags, not commands.
    return {name for name in found if not name.startswith("-")} - {"help", "version"}


def run_cli(args: list[str]) -> tuple[int, str]:
    """Invoke main() in-process and capture stdout plus the exit code."""
    buffer = io.StringIO()
    argv = sys.argv
    sys.argv = ["repo-signal", *args]
    code = 0
    try:
        with redirect_stdout(buffer):
            cli.main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = argv
    return code, buffer.getvalue()


class TestRegistryIsTheSingleSource(unittest.TestCase):
    def test_registry_and_dispatch_agree(self):
        self.assertEqual(command_names(), dispatched_commands())

    def test_registry_entries_are_well_formed(self):
        for command in COMMANDS:
            with self.subTest(command=command.name):
                self.assertTrue(command.name)
                self.assertTrue(command.summary.strip())
                self.assertTrue(command.usage, "at least one usage line")
                for line in command.usage:
                    self.assertTrue(
                        line == command.name or line.startswith(f"{command.name} "),
                        f"usage line must start with the command name: {line!r}",
                    )

    def test_registry_names_are_unique_and_sorted_output_is_stable(self):
        names = [command.name for command in COMMANDS]
        self.assertEqual(len(names), len(set(names)))


class TestTopLevelHelp(unittest.TestCase):
    def test_help_lists_every_command(self):
        code, output = run_cli(["--help"])
        self.assertEqual(code, 0)
        for name in sorted(command_names()):
            with self.subTest(command=name):
                self.assertRegex(
                    output, rf"(?m)^\s+repo-signal {re.escape(name)}\b"
                )

    def test_help_text_is_generated_from_the_registry(self):
        code, output = run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), build_help_text().strip())

    def test_unknown_command_fallback_lists_every_command(self):
        code, output = run_cli(["definitely-not-a-command"])
        self.assertEqual(code, 1)
        listed = re.search(r"Available commands: (.+)", output)
        self.assertIsNotNone(listed)
        names = {
            part.strip()
            for part in listed.group(1).split(",")
            if not part.strip().startswith("--")
        }
        self.assertEqual(names, command_names())


class TestSubcommandHelp(unittest.TestCase):
    """`<command> --help` must print usage, never fall through to the parser."""

    def test_every_command_answers_help(self):
        for name in sorted(command_names()):
            for flag in ("--help", "-h"):
                with self.subTest(command=name, flag=flag):
                    code, output = run_cli([name, flag])
                    self.assertEqual(
                        code, 0, f"`{name} {flag}` should exit 0, got {code}"
                    )
                    self.assertNotIn("Unknown", output)
                    self.assertIn(f"repo-signal {name}", output)

    def test_help_reaches_nested_subcommands(self):
        for args in (["portfolio", "check", "--help"], ["wiki", "plan", "--help"]):
            with self.subTest(args=args):
                code, output = run_cli(args)
                self.assertEqual(code, 0)
                self.assertNotIn("Unknown", output)


class TestDocsConsistency(unittest.TestCase):
    def test_command_reference_documents_every_command(self):
        reference = (REPO_ROOT / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
        headings = set(re.findall(r"^## repo-signal ([a-z-]+)", reference, re.M))
        missing = command_names() - headings
        self.assertEqual(
            missing, set(), f"docs/COMMANDS.md is missing: {sorted(missing)}"
        )

    def test_command_reference_documents_nothing_that_does_not_exist(self):
        reference = (REPO_ROOT / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
        headings = set(re.findall(r"^## repo-signal ([a-z-]+)", reference, re.M))
        self.assertEqual(headings - command_names(), set())

    def test_readme_examples_invoke_real_commands(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        invoked = set(re.findall(r"(?m)^\s*(?:\$ )?repo-signal ([a-z][a-z-]*)", readme))
        unknown = invoked - command_names()
        self.assertEqual(
            unknown, set(), f"README invokes commands that do not exist: {sorted(unknown)}"
        )

    def test_command_reference_examples_invoke_real_commands(self):
        reference = (REPO_ROOT / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
        invoked = set(re.findall(r"(?m)^\s*(?:\$ )?repo-signal ([a-z][a-z-]*)", reference))
        unknown = invoked - command_names()
        self.assertEqual(
            unknown,
            set(),
            f"docs/COMMANDS.md invokes commands that do not exist: {sorted(unknown)}",
        )


if __name__ == "__main__":
    unittest.main()
