---
name: release-readiness
description: Use when preparing a repo release, checking tests, docs, versioning, changelog, Git status, and publish readiness.
---

# Release Readiness

Goal:
Validate whether a repository is safe and complete enough for release.

## When to use

- Before tagging, publishing, or announcing a repo-signal release
- After completing a milestone to verify version, changelog, and publish checklist alignment

## When not to use

- Regular development or feature work
- Checking repo health — use `repo-health-brief` or `repo-aware`
- Symbolic export or schema changes — use `symbolic-intelligence-exporter`

## Evals

### Should trigger

* "is repo-signal ready to publish?"
* "run the repo-signal release checklist"
* "what checks need to pass before tagging the next repo-signal version?"
* "verify version, changelog, and docs before a repo-signal release"

### Should not trigger

* "update repo-signal docs" → use `docs-maintainer`
* "export symbol intelligence or schema" → use `symbolic-intelligence-exporter`
* "audit the product presentation" → use `repo-product-auditor`
* "regular repo-signal development work" → only needed at release boundaries

Always inspect:

- git status
- VERSION
- CHANGELOG.md
- README.md
- release scripts
- tags
- tests
- docs
- package metadata
- CI workflows

Check for:

- uncommitted changes
- missing changelog entries
- version mismatch
- missing release notes
- broken install instructions
- missing tests
- unpublished artifacts
- unsafe secrets
- inconsistent documentation
- missing rollback path

Prefer:

- concrete terminal commands
- actionable fixes
- minimal safe changes
- verification steps

Never:

- assume release safety
- invent missing files
- ignore failing tests
