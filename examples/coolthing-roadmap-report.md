# Roadmap Signal Report

Repo: `coolThing`
Detected track: `GitHub Pages / static web project`

## Current signals

- README: `yes`
- LICENSE: `yes`
- .gitignore: `yes`
- docs/: `yes`
- docs/index.html: `yes`
- examples/: `no`
- bin/: `no`
- Python package folder: `no`
- tests/: `no`
- pyproject.toml: `no`
- requirements.txt: `no`
- README roadmap: `no`
- Working tree changes: `0`

## Immediate next actions

1. Add example reports or example usage output
2. Add a small tests/ folder for core scanner behavior
3. Add a Roadmap section to README.md

## Suggested roadmap

### Phase 1 — Stabilize the foundation

- keep CLI commands working from any directory
- keep README, LICENSE, docs, and examples in sync
- verify GitHub Pages deployment
- make output predictable and copy-paste friendly

### Phase 2 — Improve analysis depth

- improve project type detection
- detect GitHub Pages structure more accurately
- detect missing screenshots or preview assets
- detect broken obvious local links
- detect stale planned commands in README

### Phase 3 — Add installable CLI packaging

- add `pyproject.toml`
- expose `repo-signal` as a console script
- support `pipx install .`
- add version output
- add basic tests

### Phase 4 — Safe patch mode

- generate safe cleanup commands
- generate README section patches
- generate docs/README.md
- generate wiki drafts
- never modify files without explicit confirmation

### Phase 5 — AI-assisted handoff

- export structured prompts for deeper analysis
- generate positioning drafts
- generate release notes
- generate GitHub Wiki pages
- generate LinkedIn/GitHub launch posts

## Recommended next commit

```text
Add tests for repo-signal commands
```

## North star

```text
turn unclear project state into clear next actions
```
