# Packaging

This document tracks the path from local editable installs to a future
PyPI / pipx-ready release.

`repo-signal` is a CLI tool. The intended future install path is:

```bash
pipx install repo-signal
```

That should eventually provide:

```bash
repo-signal analyze
repo-signal inspect
repo-signal inspect --json
repo-signal doctor
repo-signal publish-checklist .
```

## Current status

Current status: **packaging readiness only**.

This repository is not claiming that the package is published on PyPI yet.

Use local development install for now:

```bash
git clone https://github.com/MCamner/repo-signal.git
cd repo-signal
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ai]"
```

## Packaging goals

Before publishing to PyPI, the project should verify:

* package metadata is valid
* `VERSION` matches `pyproject.toml`
* `repo-signal` console script is defined
* source distribution builds
* wheel builds
* wheel installs into a clean virtual environment
* installed CLI can run outside editable mode
* `repo-signal inspect --json` returns `inspect.v1`
* release flow checks packaging before tagging

## Readiness check

Run:

```bash
scripts/check-packaging.sh
```

This performs a local packaging smoke test:

1. validates `pyproject.toml`
2. verifies version consistency
3. builds wheel and source distribution
4. installs the wheel into a clean virtual environment
5. runs CLI smoke tests from the installed wheel

## Release checklist addition

Before release:

```bash
scripts/check-generated-examples.sh
scripts/check-packaging.sh
python3 -m pytest -q
repo-signal inspect --json . | python3 -m json.tool
repo-signal publish-checklist . --fail-under 16
```

## Future PyPI path

The safe path should be:

```text
v0.1.19 — PyPI / pipx readiness plan
v0.1.20 — TestPyPI publishing dry run
v0.1.21 — PyPI publishing automation
v0.2.0  — stable install story
```

## TestPyPI dry run

Later, before real PyPI publishing:

```bash
python3 -m build
python3 -m twine upload --repository testpypi dist/*
```

Then test from TestPyPI in a clean environment.

Do not publish to real PyPI until:

* TestPyPI install works
* CLI smoke tests pass from installed package
* package name, metadata, README rendering, and license are correct
* release notes are ready

## pipx verification target

Future expected verification:

```bash
pipx install repo-signal
repo-signal --help
repo-signal inspect --json .
```

For now, `scripts/check-packaging.sh` simulates the important part by installing
the built wheel into a clean virtual environment and running CLI checks.

## Rule

Do not claim public `pipx install repo-signal` support until the package has
actually been published and tested.
