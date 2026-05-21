# Changelog

<!-- markdownlint-disable MD024 -->

## [Unreleased]

## [0.1.14] - 2026-05-21

### Changed

- Massive README split and documentation refactor for better discoverability.
- Modularized documentation moved to `docs/`: `REPOAWARE.md`, `SEMANTIC_MEMORY.md`, `PUBLISH_CHECKLIST.md`, `README_STRUCTURE.md`, and `COMMAND_SURFACE.md`.
- Streamlined `README.md` to focus on pitch, installation, and quick-start, linking to deeper docs.
- Updated "Planned features" in README with clear "Not started" vs "Partially implemented" status.

### Verified

- 75 tests pass.
- All new documentation links are verified.
- README score remains high with clearer structure.

## [0.1.13] - 2026-05-21

### Added

- `repo-signal inspect [path]` for fast repository status, detected signals, likely issues, and recommended next commit.
- Inspect output examples under `examples/inspect/` and `examples/demo/`.

### Changed

- Added `inspect` to CLI help, command reference, README command surface, roadmap, and tests.
- `repo-signal demo --generate` now includes `inspect.txt`.

### Verified

- 75 tests pass locally.
- `repo-signal inspect .` reports public readiness, detected signals, core files, possible issues, and recommended next commit.
- Smoke-tested `inspect` against `repo-signal`, `macos-scripts`, `mq-mcp`, and `coolThing`.
- GitHub Actions Tests, Publish Checklist, and Pages deployment are green for the inspect commit.

## [0.1.12] - 2026-05-21

### Added

- `repo-signal demo --generate` for creating local demo reports.
- Generated demo reports under `examples/demo/`.
- Golden output examples for doctor, analyze, and RepoAware workflows.
- Screenshot/output gallery documentation.
- Command reference and doctor schema links from README.

### Changed

- Improved README onboarding and public-facing positioning.
- Replaced "Early MVP" status with "Early but usable CLI tool".
- Split available commands from future command ideas.
- Refreshed doctor and analyze examples after demo generation.

### Verified

- 74 tests pass.
- `repo-signal doctor` reports 100/100 across repo health, release maturity, docs quality, and AI readiness.
- `repo-signal publish-checklist . --fail-under 16` passes with 16/16.
- GitHub Actions Tests, Publish Checklist, and Pages deployment are green.

## [0.1.11] - 2026-05-20

### Added

- `doctor --json` / `--format json` — machine-readable doctor output (schema version `doctor.v1`).
- `doctor --json` short flag as alias for `--format json`.
- `docs/DOCTOR_JSON.md` — JSON output documentation and schema reference.

### Changed

- `doctor_repo()` refactored into `build_doctor_result()` + `format_doctor_report_from_result()` for clean JSON/markdown separation.
- All previous callers of `format_doctor_report()` remain compatible via thin wrapper.

### Verified

- 71 tests pass on Python 3.11 and 3.12.
- `repo-signal doctor --json` produces valid `doctor.v1` JSON.
- `repo-signal doctor --format json` and `--json` short flag both work.
- `repo-signal doctor --format xml` exits with code 2.
- mq-hal `doctor_commands()` falls back to `repo-signal doctor --json` automatically.

## [0.1.10] - 2026-05-15

### Fixed

- `repo-signal semantic-upload --dry-run` now works fully offline without `OPENAI_VECTOR_STORE_ID`.
- Dry-run output shows `(not set)` for vector store when no target is configured.
- Real upload still requires `OPENAI_VECTOR_STORE_ID` or `--vector-store-id`.

### Added

- `semantic-upload` documented in README with full generation flow and command variants.
- `semantic-upload` added to the command surface tree.
- Install section added to README with copy-paste clone and setup instructions.
- Regression test: `test_openai_upload_dry_run_works_without_vector_store_id`.

### Changed

- CI switched from `python -m unittest discover` to `pytest` to support both unittest and pytest-style tests.

### Verified

- `repo-signal semantic-upload --dry-run` works without any env vars set.
- `repo-signal semantic-upload` fails clearly when `OPENAI_VECTOR_STORE_ID` is missing.
- 68 tests pass on Python 3.11 and 3.12.
- Publish checklist scores 16/16.

## [0.1.9] - 2026-05-12

### Added

- Added `repo-signal portfolio check`.
- Added portfolio-level publish-readiness checks across multiple local repositories.
- Added support for text, Markdown, and JSON portfolio reports.
- Added `repo-signal.yml` portfolio configuration.
- Added portfolio check tests and example reports.

### Changed

- Documented portfolio quality workflow in README.

### Verified

- `repo-signal portfolio check` works.
- `repo-signal portfolio check --format markdown` works.
- `repo-signal portfolio check --format json` works.
- Test suite passes.
- Publish checklist passes.

### Scope

This release turns repo-signal from a single-repo checker into a local portfolio quality tool.

All notable changes to this project will be documented in this file.

## [0.1.8] - 2026-05-12

### Added

* Added `repo-signal actions init`.
* Added GitHub Actions workflow generation for publish-checklist quality gates.
* Added `--fail-under` configuration for generated workflows.
* Added overwrite protection with `--force`.
* Added tests for workflow creation, overwrite protection, and forced overwrite behavior.

### Changed

* Documented GitHub Actions quality gate usage in README.
* Highlighted the CI quality gate workflow on GitHub Pages.

### Verified

* `repo-signal actions init . --fail-under 14` creates `.github/workflows/publish-checklist.yml`.
* Generated workflow runs `repo-signal publish-checklist . --fail-under 14`.
* Test suite passes.
* Publish checklist passes.

### Scope

This release makes repo-signal usable as a reusable GitHub Actions quality gate
initializer for other repositories.

---

## [0.1.7] - 2026-05-12

### Added

* Added `--fail-under` support for `repo-signal publish-checklist`.
* Added CI-friendly threshold behavior for publish-readiness scores.
* Added support for fail-under checks across text, Markdown, and JSON output modes.
* Added tests for pass and fail threshold behavior.

### Changed

* Documented `--fail-under` usage in README and roadmap.

### Verified

* `repo-signal publish-checklist . --fail-under 16` exits with `0`.
* `repo-signal publish-checklist . --fail-under 17` exits with non-zero.
* JSON output works with fail-under thresholds.
* Test suite passes.

### Scope

This release makes `publish-checklist` usable as an automated quality gate for
CI and GitHub Actions.

---

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
