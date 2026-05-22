# Trusted Publishing

This document describes the safe setup path for publishing `repo-signal` to
TestPyPI using GitHub Actions Trusted Publishing.

Current status: **TestPyPI Trusted Publishing setup guidance only**.

This does not mean the package is published to PyPI.

## Why Trusted Publishing?

Trusted Publishing lets GitHub Actions publish to TestPyPI/PyPI without storing
long-lived API tokens in GitHub secrets.

The GitHub Actions workflow must use:

```yaml
permissions:
  id-token: write
```

and the PyPI/TestPyPI project must be configured with a matching Trusted
Publisher.

## TestPyPI Trusted Publisher values

Use these values on TestPyPI when creating the Trusted Publisher:

| Field            | Value          |
| ---------------- | -------------- |
| Owner            | `MCamner`      |
| Repository name  | `repo-signal`  |
| Workflow name    | `testpypi.yml` |
| Environment name | `testpypi`     |
| Package name     | `repo-signal`  |

## GitHub environment

Create a GitHub Actions environment named:

```text
testpypi
```

Recommended protection:

* require manual approval before deployment
* restrict who can approve
* do not add API tokens unless falling back from Trusted Publishing

## Safe publish flow

1. Run local checks.
2. Push code.
3. Confirm CI is green.
4. Create or verify TestPyPI Trusted Publisher.
5. Run the manual `TestPyPI dry run` workflow with:

```text
publish_to_testpypi = false
```

6. If readiness passes, run it again with:

```text
publish_to_testpypi = true
```

7. Install from TestPyPI in a clean environment.
8. Verify the installed CLI.

## Local readiness

```bash
scripts/check-trusted-publishing-setup.sh
scripts/check-testpypi-readiness.sh
scripts/check-packaging.sh
scripts/check-generated-examples.sh
python3 -m pytest -q
repo-signal publish-checklist . --fail-under 16
```

## TestPyPI install verification

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

## Do not publish to real PyPI yet

Real PyPI publishing should wait until:

* TestPyPI upload succeeds
* TestPyPI install succeeds
* installed CLI works
* `inspect --json` returns `inspect.v1`
* README install claims are updated honestly
* release notes are ready
* package metadata is confirmed
