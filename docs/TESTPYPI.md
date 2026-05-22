# TestPyPI Publishing Dry Run

This document describes the safe path for testing package publication before
publishing `repo-signal` to the real PyPI index.

Current status: **TestPyPI dry-run planning only**.

Do not claim public `pipx install repo-signal` support until the package has
actually been published and tested from the real PyPI index.

## Why TestPyPI first?

TestPyPI is the package index test environment used to verify packaging,
metadata, distribution files, and install behavior before publishing to PyPI.

The goal is to prove:

* the package builds cleanly
* the wheel and sdist are valid
* metadata renders correctly
* the console script installs correctly
* `repo-signal inspect --json` works after install
* the package can be installed from a package index

## Required local checks

Before any TestPyPI upload attempt:

```bash
scripts/check-packaging.sh
scripts/check-generated-examples.sh
python3 -m pytest -q
repo-signal inspect --json . | python3 -m json.tool
repo-signal publish-checklist . --fail-under 16
```

## Local build

```bash
rm -rf dist
python3 -m build
python3 -m twine check dist/*
```

## Manual TestPyPI upload

Only after local checks pass:

```bash
python3 -m twine upload --repository testpypi dist/*
```

This requires a TestPyPI account and credentials.

## Safer future path: Trusted Publishing

For GitHub Actions publishing, prefer Trusted Publishing / OIDC over
long-lived API tokens.

Expected future setup:

1. Create project on TestPyPI or configure pending trusted publisher.
2. Configure the GitHub repository as a trusted publisher.
3. Use a manual GitHub Actions workflow.
4. Require explicit approval through an environment such as `testpypi`.
5. Verify installation from TestPyPI before real PyPI publishing.

## Manual install test from TestPyPI

After a successful TestPyPI upload:

```bash
python3 -m venv /tmp/repo-signal-testpypi
source /tmp/repo-signal-testpypi/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  repo-signal

repo-signal --help
repo-signal inspect .
repo-signal inspect --json . | python3 -m json.tool
```

Expected JSON contract:

```json
{
  "schema": "inspect.v1"
}
```

## Rule

Real PyPI publishing is not allowed until:

* TestPyPI upload succeeds
* TestPyPI install succeeds in a clean environment
* installed `repo-signal` CLI works
* `inspect --json` returns `inspect.v1`
* README install claims are updated honestly
* release notes are ready
* package name, metadata, license, and README rendering are verified
