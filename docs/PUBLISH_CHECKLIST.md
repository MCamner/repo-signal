# Publish Checklist

`publish-checklist` checks whether a repository has the public-facing basics
needed to look understandable and publishable:

- README
- LICENSE
- CHANGELOG
- VERSION
- docs folder
- GitHub Pages landing page
- screenshots or demo gallery
- roadmap
- issue templates
- safe sharing/security notes

## Usage

```bash
# basic usage
repo-signal publish-checklist .
repo-signal publish-checklist ~/Design-Prototype

# output formats
repo-signal publish-checklist . --format markdown
repo-signal publish-checklist . --format json

# ci enforcement
repo-signal publish-checklist . --fail-under 14
repo-signal publish-checklist . --format json --fail-under 14
```

`publish-checklist` is the public readiness check before polishing or
releasing a repo. The default output is plain text; Markdown and JSON formats
are available for reports, CI checks, GitHub Actions, and automated audits.

See real outputs:
[Publish checklist examples](../examples/publish-checklist/README.md)

---

## GitHub Actions quality gate

Create a workflow that runs the publish checklist in CI:

```bash
repo-signal actions init
repo-signal actions init . --fail-under 14
```

This writes:

```text
.github/workflows/publish-checklist.yml
```

The generated workflow runs:

```bash
repo-signal publish-checklist . --fail-under 14
```

Use this when you want a repository to fail CI if public readiness drops below
the required score.

---

## Portfolio check

Run publish-readiness checks across multiple local repositories from `repo-signal.yml`.

```bash
repo-signal portfolio check
repo-signal portfolio check --format markdown
repo-signal portfolio check --format json
```

Example output:

```text
PORTFOLIO CHECK
===============

repo-signal       16/16  OK       fail-under=16
macos-scripts     16/16  OK       fail-under=14
mcamner-journal    9/16  WARN     fail-under=12

Next action
-----------
mcamner-journal: Fix: README mentions demo
```

Configure repos in `repo-signal.yml`:

```yaml
portfolio:
  repos:
    - name: repo-signal
      path: ~/repo-signal
      fail_under: 16
    - name: macos-scripts
      path: ~/macos-scripts
      fail_under: 14
```
