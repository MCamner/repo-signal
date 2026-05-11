# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

## [0.1.6] - 2026-05-12

### Added

* Added `repo-signal wiki export . --output docs/wiki-export`.
* Added generated wiki export pages for review before publishing.
* Added wiki generator documentation and spec.
* Added tests and validation flow for the wiki export workflow.

### Changed

* Marked Phase 3 - Wiki Generator as mostly done.
* Improved README command rendering and wiki workflow documentation.

### Verified

* `repo-signal wiki plan .` works.
* `repo-signal wiki export . --output docs/wiki-export` works.
* `python3 -m pytest -q` passes.
* `repo-signal publish-checklist .` passes.
* GitHub Pages deployment is successful.

### Scope

This release makes the wiki generator workflow usable and reviewable without
pushing directly to GitHub Wiki.

---

## [0.1.5] - 2026-05-11

### Added

* Added `--format text`, `--format markdown`, and `--format json` for
  `repo-signal publish-checklist`.
* Added structured checklist data for CI, GitHub Actions, reports, and
  automated audit workflows.
* Added tests for JSON output, Markdown output, and invalid format handling.

### Changed

* Updated README and roadmap to document publish checklist output formats.

### Scope

This is a feature release for making `publish-checklist` machine-readable and
report-friendly.

---

## [0.1.4] - 2026-05-11

### Changed

* docs: add changelog section for 0.1.3
* docs: fix design-prototyp checklist example
* docs: add publish checklist examples
* docs: polish README command examples
* update documentation
* docs: add platform skills map
* update project files
* docs: add roadmap issue templates and screenshots folder
* feat: add publish checklist command
* add: wiki Command-Reference generator and auto-update on release check
* update project files
* update project files
* update project files
* update project files
* update documentation
* docs: add changelog section for 0.1.3

---

## [0.1.3] - 2026-05-11

### Changed

* docs: fix design-prototyp checklist example
* docs: add publish checklist examples
* docs: polish README command examples
* update documentation
* docs: add platform skills map
* update project files
* docs: add roadmap issue templates and screenshots folder
* feat: add publish checklist command
* add: wiki Command-Reference generator and auto-update on release check
* update project files
* update project files
* update project files
* update project files
* update documentation
* docs: add changelog section for 0.1.3

---

## [0.1.2] - 2026-05-10

### Added

* Added `repo-signal doctor` for repo health, release maturity, docs quality,
  AI readiness, suggested skills, and RepoAware priority context.
* Added repo-local skill creation with `repo-signal skill new <name>` and
  export support through `repo-signal export-codex`.
* Added `repo-aware` and `release-readiness` skills for repo-first reasoning
  and release validation workflows.
* Added `tools/skill_router.py` for keyword-based skill routing experiments.
* Added semantic, RepoAware, symbol extraction, graph, vector-store, and AI ask
  pipeline modules.
* Added `release.sh` as a safe release-check wrapper that runs status, tests,
  doctor, and README scoring without publishing.

### Changed

* Expanded README and GitHub Pages docs to reflect doctor, skill creation,
  RepoAware, semantic search, and Codex export workflows.
* Expanded CLI help and test coverage for the current command surface.
