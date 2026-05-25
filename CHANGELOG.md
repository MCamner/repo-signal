# Changelog

<!-- markdownlint-disable MD024 -->

## [Unreleased]

## [0.7.1] - 2026-05-25

### Added

* `docs/REPORT_SCHEMA.md` — full field reference for `report.v1` JSON contract
* `docs/SUGGEST_SCHEMA.md` — full field reference for `suggest.v1`, no-mutation guarantee documented
* `docs/COMMANDS.md` — added `repo-signal report` and `repo-signal suggest` command entries
* `examples/report/` — generated `report.v1.json`, `report.txt`, `report.md`
* `examples/suggest/` — generated `suggest.v1.json`, `suggest.txt`, `suggest.md`
* `release.sh` — `report.v1` and `suggest.v1` schema checks added

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.7.1
* ROADMAP: v0.7.1 marked done, v0.6.0 title cleaned up ("dashboard artifacts" → "unified report and export")

### Verified

* 157 tests pass
* `repo-signal report .` — text, markdown and JSON output verified
* `repo-signal suggest .` — text, markdown and JSON output verified
* `release.sh` — report.v1 and suggest.v1 schema checks pass

## [0.7.0] - 2026-05-24

### Added

* `repo-signal suggest [path] [--format text|markdown|json]` — safe patch suggestions, no mutations
* `suggest.v1` JSON schema for machine-readable suggestion output
* `repo_signal/suggest.py` — `build_suggestions`, `format_suggestions`
* `tests/test_suggest.py` — 23 tests including explicit no-mutation guarantees
* `repo_suggest` tool registered in mq-agent TOOL_REGISTRY
* `tasks/suggest.yaml` — mqlaunch task using 8 tools: `repo_scan`, `repo_publish_checklist`, `repo_readme_score`, `git_status`, `git_log`, `repo_signal_json`, `repo_suggest`

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.7.0
* ROADMAP: v0.7.0 marked done, v1.0.0 next

### Verified

* 157 tests pass
* `repo-signal suggest .` — text, markdown och JSON output verified
* `mq-agent task run suggest-patches` — all 8 steps pass
* No files created or modified during suggest run

## [0.6.0] - 2026-05-24

### Added

* `repo-signal report [path] [--format text|markdown|json]` — unified report combining inspect and publish-checklist
* `report.v1` JSON schema for machine-readable output
* `repo_signal/report.py` — `build_report`, `format_report`
* `tests/test_report.py` — 17 tests

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.6.0
* ROADMAP: v0.6.0 marked done, v0.7.0 next
* ROADMAP headers: corrected v0.2.0/v0.4.0/v0.5.0 to `## Completed:`

### Verified

* 134 tests pass
* `scripts/check-docs-consistency.sh` passes
* `repo-signal report .` verified text, markdown and JSON output

## [0.5.0] - 2026-05-24

### Added

* `tests/test_semantic_upload.py` — 12 tests covering dry-run, missing env, exit codes, no-secret guarantee and mq-agent integration
* `docs/SEMANTIC_MEMORY.md` — rewritten with verified dry-run output, safety rules table, no-secret guarantee, mq-agent integration and failure states

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.5.0
* ROADMAP: v0.5.0 marked done, v0.6.0 next

### Verified

* 117 tests pass
* `scripts/check-docs-consistency.sh` passes
* `repo-signal semantic-upload --dry-run` verified output documented
* `mq-agent memory status` and `mq-agent memory build` verified against this repo

## [0.4.0] - 2026-05-24

### Added

* `docs/MQ_ECOSYSTEM.md` — ecosystem overview, architecture diagram, troubleshooting and CI gate examples
* `examples/integrations/inspect_safe.sh` — safe shell consumer for `inspect.v1`
* `examples/integrations/readiness_gate.sh` — CI publish-readiness gate script
* `examples/integrations/mq_agent_consumer.py` — Python consumer pattern for `inspect.v1` and `doctor.v1`
* `tests/test_mq_ecosystem.py` — 10 integration smoke tests

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.4.0
* ROADMAP: v0.4.0 marked done, v0.5.0 next

### Verified

* 105 tests pass
* `scripts/check-docs-consistency.sh` passes
* Integration examples run against this repo

## [0.3.0] - 2026-05-24

### Added

* `tests/test_contracts.py` — 14 schema contract tests for `inspect.v1` and `doctor.v1`
* `schema: "doctor.v1"` field added to `doctor --json` output (alongside legacy `schema_version`)
* `docs/INTEGRATIONS.md` — mq-agent integration example added
* `docs/DOCTOR_SCHEMA.md` — updated to document `schema` field and safe consumption pattern

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.3.0
* ROADMAP: v0.3.0 marked as current, v0.4.0 as next

### Verified

* 95 tests pass
* `scripts/check-docs-consistency.sh` passes
* `scripts/check-packaging.sh` passes
* `repo-signal inspect --json .` returns `schema: inspect.v1`
* `repo-signal doctor --json .` returns `schema: doctor.v1`

## [0.2.1] - 2026-05-24

### Added

* `scripts/check-docs-consistency.sh` — version sync, CHANGELOG and readability guards
* `## v0.2.1 status` proof section in README
* `.markdownlint.json` with `siblings_only: true` to suppress expected duplicate heading warnings

### Changed

* Bumped VERSION, `pyproject.toml` and `repo_signal/__init__.py` to 0.2.1
* Updated ROADMAP: v0.2.0 fully done, v0.2.1 as current next step

### Verified

* 81 tests pass
* `scripts/check-docs-consistency.sh` passes
* `scripts/check-packaging.sh` passes
* `repo-signal publish-checklist . --fail-under 16` passes

## [0.2.0] - 2026-05-22

### Added

* Added `docs/PYPI.md` with PyPI Trusted Publisher values and install verification guidance.
* Added `scripts/check-pypi-readiness.sh` to run all checks before real PyPI publish.
* Added manual PyPI publish workflow (`.github/workflows/pypi.yml`).

### Changed

* Updated README install section to show `pipx install repo-signal` as v0.2.0 target.
* Updated roadmap to v0.2.0 stable install story focus.

### Verified

* `scripts/check-pypi-readiness.sh` passes.
* TestPyPI install verified — wheel, CLI, and `inspect.v1` all confirmed.
* 78 tests pass.
* `repo-signal publish-checklist . --fail-under 16` passes 16/16.

## [0.1.21] - 2026-05-22

### Added

* Added `docs/TRUSTED_PUBLISHING.md` with TestPyPI Trusted Publisher setup values.
* Added `scripts/check-trusted-publishing-setup.sh` to verify workflow and docs are correctly configured.
* Added `docs/TESTPYPI.md` with safe TestPyPI dry-run guidance.
* Added `scripts/check-testpypi-readiness.sh` to verify build artifacts with `twine check`.
* Added manual TestPyPI GitHub Actions workflow.
* Added TestPyPI and Trusted Publishing documentation links from README.

### Changed

* Updated TestPyPI workflow to run Trusted Publishing setup check in readiness job.
* Updated roadmap and release checklist with Trusted Publishing verification steps.

### Verified

* `scripts/check-trusted-publishing-setup.sh` passes.
* `scripts/check-testpypi-readiness.sh` passes — twine check PASSED for wheel and sdist.
* `scripts/check-packaging.sh` passes.
* `scripts/check-generated-examples.sh` passes.
* 78 tests pass.
* `repo-signal publish-checklist . --fail-under 16` passes 16/16.
* Tests, Packaging, Publish Checklist, Generated examples CI — all green.

## [0.1.19] - 2026-05-22

### Added

* Added `docs/PACKAGING.md` with PyPI / pipx readiness guidance.
* Added `scripts/check-packaging.sh` for local wheel-build and clean install smoke tests.
* Added packaging CI workflow.

### Changed

* Updated README install section to separate local development install from future pipx target.
* Updated roadmap release readiness checklist with packaging checks.

### Verified

* `scripts/check-packaging.sh` passes.
* `scripts/check-generated-examples.sh` passes.
* 78 tests pass.
* `repo-signal publish-checklist . --fail-under 16` passes 16/16.
* Packaging CI, Tests, Publish Checklist, Generated examples — all green.

## [0.1.18] - 2026-05-21

### Changed

* Rewrote `release.sh` as a full release workflow tool with structured checks and `--publish` flag.
* `release.sh` now verifies: version sync, CHANGELOG entry, clean git tree, tests, generated examples, `inspect --json` schema, publish-checklist score, README score, and wiki state.
* `release.sh --publish` tags, pushes, and creates a GitHub release with notes pulled from CHANGELOG.
* Dry run (`./release.sh`) blocks on failures and shows a summary table.

### Verified

* 78 tests pass.
* `scripts/check-generated-examples.sh` passes.
* `repo-signal publish-checklist . --fail-under 16` passes 16/16.
* `./release.sh` runs clean and shows all checks.

## [0.1.17] - 2026-05-21

### Added

* Added `scripts/check-generated-examples.sh` for generated example verification.
* Added `scripts/generate-examples.sh` for refreshing canonical examples.
* Added generated examples CI workflow (`.github/workflows/examples.yml`).
* Added `docs/GENERATED_EXAMPLES.md`.

### Changed

* Updated README and roadmap with generated example verification guidance.
* Strengthened release readiness workflow with example check step.

### Verified

* 78 tests pass.
* `scripts/check-generated-examples.sh` passes.
* `repo-signal publish-checklist . --fail-under 16` passes 16/16.
* Generated examples CI workflow is green.

## [0.1.16] - 2026-05-21

### Added

* Added root-level `ROADMAP.md` for clearer project direction and release readiness.
* Added roadmap links from README and GitHub Pages docs.
* Added `docs/INTEGRATIONS.md` — integration guide for mqlaunch, mq-mcp, mq-hal, and Bridget consuming `inspect.v1`.
* Added `inspect --json` to README quick-start and command surface.

### Changed

* Clarified release checklist, version milestones, and integration contract expectations in roadmap.
* Documented `inspect --json` and `inspect.v1` integration contract more prominently in `docs/COMMAND_SURFACE.md` and `docs/index.html`.

### Verified

* 78 tests pass.
* `repo-signal inspect --json` returns `schema: inspect.v1`.
* `repo-signal publish-checklist . --fail-under 16` passes with 16/16.
* `repo-signal doctor` reports 100/100 across all categories.
* GitHub Actions green after push.

## [0.1.15] - 2026-05-21

### Added

* `repo-signal inspect --json` and `repo-signal inspect --format json`.
* `inspect.v1` JSON integration contract for mqlaunch, mq-hal, mq-mcp, Bridget, CI helpers, and dashboards.
* `docs/INSPECT_SCHEMA.md`.
* `inspect.v1.json` generated as part of `repo-signal demo --generate`.

### Changed

* Updated command reference (`docs/COMMANDS.md`) to document the inspect JSON contract.

## [0.1.14] - 2026-05-21

### Changed

* Massive README split and documentation refactor for better discoverability.
* Modularized documentation moved to `docs/`: `REPOAWARE.md`, `SEMANTIC_MEMORY.md`, `PUBLISH_CHECKLIST.md`, `README_STRUCTURE.md`, and `COMMAND_SURFACE.md`.
* Streamlined `README.md` to focus on pitch, installation, and quick-start, linking to deeper docs.
* Updated "Planned features" in README with clear "Not started" vs "Partially implemented" status.

### Verified

* 75 tests pass.
* All new documentation links are verified.
* README score remains high with clearer structure.

## [0.1.13] - 2026-05-21

### Added

* `repo-signal inspect [path]` for fast repository status, detected signals, likely issues, and recommended next commit.
* Inspect output examples under `examples/inspect/` and `examples/demo/`.

### Changed

* Added `inspect` to CLI help, command reference, README command surface, roadmap, and tests.
* `repo-signal demo --generate` now includes `inspect.txt`.

### Verified

* 75 tests pass locally.
* `repo-signal inspect .` reports public readiness, detected signals, core files, possible issues, and recommended next commit.
* Smoke-tested `inspect` against `repo-signal`, `macos-scripts`, `mq-mcp`, and `coolThing`.
* GitHub Actions Tests, Publish Checklist, and Pages deployment are green for the inspect commit.

## [0.1.12] - 2026-05-21

### Added

* `repo-signal demo --generate` for creating local demo reports.
* Generated demo reports under `examples/demo/`.
* Golden output examples for doctor, analyze, and RepoAware workflows.
* Screenshot/output gallery documentation.
* Command reference and doctor schema links from README.

### Changed

* Improved README onboarding and public-facing positioning.
* Replaced "Early MVP" status with "Early but usable CLI tool".
* Split available commands from future command ideas.
* Refreshed doctor and analyze examples after demo generation.

### Verified

* 74 tests pass.
* `repo-signal doctor` reports 100/100 across repo health, release maturity, docs quality, and AI readiness.
* `repo-signal publish-checklist . --fail-under 16` passes with 16/16.
* GitHub Actions Tests, Publish Checklist, and Pages deployment are green.

## [0.1.11] - 2026-05-20

### Added

* `doctor --json` / `--format json` — machine-readable doctor output (schema version `doctor.v1`).
* `doctor --json` short flag as alias for `--format json`.
* `docs/DOCTOR_JSON.md` — JSON output documentation and schema reference.

### Changed

* `doctor_repo()` refactored into `build_doctor_result()` + `format_doctor_report_from_result()` for clean JSON/markdown separation.
* All previous callers of `format_doctor_report()` remain compatible via thin wrapper.

### Verified

* 71 tests pass on Python 3.11 and 3.12.
* `repo-signal doctor --json` produces valid `doctor.v1` JSON.
* `repo-signal doctor --format json` and `--json` short flag both work.
* `repo-signal doctor --format xml` exits with code 2.
* mq-hal `doctor_commands()` falls back to `repo-signal doctor --json` automatically.

## [0.1.10] - 2026-05-15

### Fixed

* `repo-signal semantic-upload --dry-run` now works fully offline without `OPENAI_VECTOR_STORE_ID`.
* Dry-run output shows `(not set)` for vector store when no target is configured.
* Real upload still requires `OPENAI_VECTOR_STORE_ID` or `--vector-store-id`.

### Added

* `semantic-upload` documented in README with full generation flow and command variants.
* `semantic-upload` added to the command surface tree.
* Install section added to README with copy-paste clone and setup instructions.
* Regression test: `test_openai_upload_dry_run_works_without_vector_store_id`.

### Changed

* CI switched from `python -m unittest discover` to `pytest` to support both unittest and pytest-style tests.

### Verified

* `repo-signal semantic-upload --dry-run` works without any env vars set.
* `repo-signal semantic-upload` fails clearly when `OPENAI_VECTOR_STORE_ID` is missing.
* 68 tests pass on Python 3.11 and 3.12.
* Publish checklist scores 16/16.

## [0.1.9] - 2026-05-12

### Added

* Added `repo-signal portfolio check`.
* Added portfolio-level publish-readiness checks across multiple local repositories.
* Added support for text, Markdown, and JSON portfolio reports.
* Added `repo-signal.yml` portfolio configuration.
* Added portfolio check tests and example reports.

### Changed

* Documented portfolio quality workflow in README.

### Verified

* `repo-signal portfolio check` works.
* `repo-signal portfolio check --format markdown` works.
* `repo-signal portfolio check --format json` works.
* Test suite passes.
* Publish checklist passes.

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
