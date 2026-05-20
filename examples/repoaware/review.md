# RepoAware Context

- Repo: `repo-signal`
- Path: `/Users/mansys/repo-signal`
- Mode: `review`
- Branch: `main`
- Question: what should I inspect first
- Keywords: `inspect`

## Instructions

- Focus on risks, maintainability, shell pitfalls, edge cases, and test gaps.
- Prioritize findings by severity and reference files directly.
- Avoid cosmetic suggestions unless they affect readability or correctness.

## Git Status

```text
?? uv.lock
```

## Relevant Files

- `skills/repo-aware/SKILL.md` - repo-first workflow and inspection checklist.
- `repo_signal/doctor.py` - readiness scoring and JSON/Markdown report generation.
- `README.md` - product positioning, command surface, and onboarding.
- `docs/index.html` - GitHub Pages landing page.
- `docs/wiki-export/Command-Reference.md` - exported command reference.

## Use This For

This fixture shows the shape of `repoaware --mode review --format markdown` without embedding the full generated context. Regenerate a full context sample with:

```bash
repo-signal repoaware --mode review --format markdown "what should I inspect first"
```
