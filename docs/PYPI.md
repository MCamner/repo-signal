# PyPI Publishing

This document describes the path for publishing `repo-signal` to the real
PyPI index.

Current status: **PyPI publishing infrastructure ready. Pending first publish.**

Once published, the install path will be:

```bash
pipx install repo-signal
```

## Prerequisites

Before publishing to PyPI:

* TestPyPI publish must have succeeded.
* TestPyPI install must have verified that the CLI works.
* `inspect --json` must return `inspect.v1` from the installed package.
* README install claims must be updated to reflect the published state.

## PyPI Trusted Publisher values

Use these values on PyPI when creating the Trusted Publisher:

| Field            | Value       |
| ---------------- | ----------- |
| Owner            | `MCamner`   |
| Repository name  | `repo-signal` |
| Workflow name    | `pypi.yml`  |
| Environment name | `pypi`      |
| Package name     | `repo-signal` |

## GitHub environment

Create a GitHub Actions environment named:

```text
pypi
```

Recommended protection:

* require manual approval before deployment
* restrict who can approve
* do not add API tokens — use Trusted Publishing only

## Safe publish flow

1. Run local checks.
2. Confirm TestPyPI install is verified.
3. Push code and confirm CI is green.
4. Create or verify PyPI Trusted Publisher.
5. Run the manual `PyPI publish` workflow with:

```text
publish_to_pypi = false
```

6. If readiness passes, run it again with:

```text
publish_to_pypi = true
```

7. Verify installation in a clean environment.

## Local readiness

```bash
scripts/check-pypi-readiness.sh
```

This runs all packaging and TestPyPI readiness checks.

## Install verification after PyPI publish

```bash
pipx install repo-signal
repo-signal --help
repo-signal inspect .
repo-signal inspect --json . | python3 -m json.tool
```

Expected:

```json
{
  "schema": "inspect.v1"
}
```

## After first successful PyPI publish

Update README install section from:

```markdown
Current local development install:
...
Future target (after PyPI publish):
pipx install repo-signal
```

to:

````markdown
## Install

```bash
pipx install repo-signal
```

````

Then release the updated README as part of the next patch release.

## Rule

Do not claim `pipx install repo-signal` in README until the package has
actually been published to PyPI and verified in a clean install.
