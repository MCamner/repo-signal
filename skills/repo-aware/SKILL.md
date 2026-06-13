---
name: repo-aware
description: Use when working inside a repo and needing repo-specific context from docs, tooling, tests, git state, repo-signal reports, and local conventions before acting.
---

# Repo Aware

Use this skill to make AI work repo-first instead of prompt-first.

The goal is to ground every answer or change in the repository's actual structure, conventions, risks, and current state.

## When to use

Use this skill when the user asks to:

- understand a repo
- inspect or explain code
- plan changes in an existing repo
- implement a feature or fix
- review repo quality or readiness
- prepare release, docs, README, Wiki, or GitHub Pages updates
- use repo-signal's own report output as context for AI work
- decide what Codex should inspect before acting

## When not to use

- When a narrower skill clearly owns the task — use `symbolic-intelligence-exporter` for JSON exports, `release-readiness` for release checks, `docs-maintainer` for docs, or `semantic-memory-maintainer` for vector store work
- Scoring README quality — use `repo-product-auditor`

## Evals

### Should trigger

* "what does repo-signal do?"
* "explain the repo-signal architecture and analysis flow"
* "I'm about to change repo-signal — what should I know first?"
* "what signals does repo-signal produce and how are they scored?"

### Should not trigger

* "update repo-signal docs" → use `docs-maintainer`
* "export symbol intelligence or the JSON schema" → use `symbolic-intelligence-exporter`
* "audit the product presentation" → use `repo-product-auditor`
* "is repo-signal ready to release?" → use `release-readiness`

## Core rule

Always let the repo teach you how to work.

Prefer evidence from:

1. README and docs
2. package/build metadata
3. scripts, tools, and CLI entrypoints
4. tests and CI
5. Git status
6. recent or relevant files
7. repo-signal reports, when available

Do not invent structure, commands, release flow, or project goals when the repo can answer them.

## Fast workflow

Start with a small inspection pass:

```bash
repo-signal doctor
repo-signal analyze
git status --short
```

If the task is about a specific area, build focused context:

```bash
repo-signal repoaware --mode explain "question"
repo-signal repoaware --mode debug "error or failing behavior"
repo-signal repoaware --mode review "change or risk"
repo-signal repoaware --mode architect "structure or coupling"
```

If `repo-signal` is unavailable, inspect manually with `rg --files`, README, package metadata, scripts, tests, and Git status.

## Inspection checklist

Check only what is relevant, but default to this order:

- `README.md`
- `AGENTS.md` or local instructions
- `pyproject.toml`, `package.json`, `requirements.txt`, or equivalent metadata
- `bin/`, `scripts/`, `tools/`, `Makefile`
- `tests/`
- `.github/workflows/`
- `docs/`
- main package or app directory
- `git status --short`

## How to think

Classify the repo before acting:

- project type
- main user workflow
- command surface
- docs surface
- release maturity
- test maturity
- AI readiness
- likely highest-risk area

Then choose the smallest useful action that improves correctness, clarity, or momentum.

## Priority model

Prioritize in this order:

1. correctness and safety
2. preserving user changes
3. matching existing naming and structure
4. improving discoverability
5. keeping output and commands easy to verify
6. avoiding broad rewrites unless requested

## Output style

Be practical and grounded.

For analysis, include:

- what the repo appears to be
- what evidence supports that
- highest-risk gaps
- recommended next action

For implementation, include:

- files changed
- behavior added or fixed
- verification run
- anything not verified

## Repo-signal integration

Use `repo-signal doctor` as the readiness summary.

Treat its suggested skills as routing hints:

- `repo-product-auditor` for README, launch, and product presentation
- `terminal-ui-polisher` for CLI and terminal UX
- architecture-oriented work when symbols and repo graph edges exist

Use `repo-signal repoaware` to generate compact task context for AI reasoning.

## Guardrails

Do not:

- assume the README is current without checking files
- assume tests exist or pass
- overwrite user changes
- recommend release work without checking Git state
- turn every task into a large audit
- add new abstractions before understanding local patterns

When uncertain, say what is known, what is inferred, and what should be checked next.
