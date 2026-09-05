# repo-signal Roadmap

repo-signal is an AI-native repository intelligence CLI.

It turns local repository state into clear analysis reports, publish-readiness
signals, JSON integration contracts and high-signal AI context exports.

The goal is simple:

```text
local repo
  ↓
repo-signal
  ↓
human report + JSON contract + AI context
  ↓
better release decisions
```

repo-signal should become the dependable repo-status engine for:

- developers cleaning up old prototypes
- portfolio projects
- release readiness checks
- AI-assisted repository reviews
- local assistant workflows
- mqlaunch command surfaces
- mq-agent semantic memory
- mq-mcp tool workflows
- mq-hal briefs

---

## Current project state

Current `main` target:

```text
v1.5.0 — TBD
```

Current highest-priority gate:

```text
VERSION, pyproject.toml, README, CHANGELOG and GitHub release state must stay aligned.
```

Current core command surface:

```text
repo-signal
├── analyze
├── inspect
├── inspect --json
├── doctor
├── publish-checklist
├── report
├── suggest
├── repoaware
└── demo
```

Additional documented commands include `positioning`, `semantic-upload`,
`ask`, `readme`, `roadmap`, `wiki`, `hygiene`, `actions init` and `skill new`.

Current stable contracts:

```text
inspect.v1
doctor.v1
report.v1
suggest.v1
```

Current strategic direction:

```text
repo-signal should remain small, scriptable and contract-driven.
```

---

## Release map

| Version | Theme                                                | Status               |
| ------- | ---------------------------------------------------- | -------------------- |
| v0.1.x  | Useful local repo intelligence CLI                   | Done                 |
| v0.1.19 | PyPI / pipx readiness plan                           | Done                 |
| v0.2.0  | Stable install story                                 | Done                 |
| v0.2.1  | Version sync, source readability and release hygiene | Done                 |
| v0.3.0  | Stable repo intelligence contracts                   | Done                 |
| v0.4.0  | mq ecosystem integration                             | Done                 |
| v0.5.0  | Semantic repository memory hardening                 | Done                 |
| v0.6.0  | Unified report and export                            | Done                 |
| v0.7.0  | Safe patch suggestion planning                       | Done                 |
| v0.7.1  | Contract proof and docs completeness                 | Done                 |
| v1.0.0  | Stable repo intelligence platform                    | Done                 |
| v1.1.0  | Symbolic intelligence exports                        | Done                 |
| v1.2.0  | mq-mcp pack merge integration                        | Done                 |
| v1.3.0  | repo-signal brief — daily health summary             | Done                 |
| v1.4.0  | Release/readiness export compatibility               | Done                 |
| v1.5.0  | Review and memory export contract hardening           | Planned              |

---

## Completed: v1.4.0 — Release/readiness export compatibility

Goal:

Make repo-signal the dependable repository readiness input for mq-agent release
status and mq-mcp Release Gate v2 without becoming the release gate engine.

Completed scope:

- [x] Define a stable `readiness.v1` export shape for MQ workflows
- [x] Include README, ROADMAP and CHANGELOG freshness signals
- [x] Include publish-readiness, docs hygiene and repo quality signals
- [x] Include version alignment and release metadata signals
- [x] Make the export easy for mq-agent and mq-mcp to consume as JSON
- [x] `docs/READINESS_SCHEMA.md` — full field reference and integration pattern
- [x] `examples/readiness/` — generated fixture outputs
- [x] 25 tests covering schema shape, version alignment, release gate logic

Boundary:

```text
repo-signal provides repo intelligence and readiness signals.
mq-mcp decides deterministic release gate status.
mq-agent presents operator workflow and next actions.
```

---

## Completed foundation

### v0.1.x — Useful local repo intelligence CLI

Goal:

Make repo-signal useful as a local CLI for inspecting and improving repositories.

Completed:

- [x] Add `repo-signal analyze`
- [x] Add `repo-signal inspect`
- [x] Add `repo-signal inspect --json`
- [x] Add `repo-signal doctor`
- [x] Add `repo-signal publish-checklist`
- [x] Add `repo-signal repoaware`
- [x] Add `repo-signal demo --generate`
- [x] Add README scoring
- [x] Add publish checklist
- [x] Add generated examples
- [x] Add GitHub Pages documentation
- [x] Add release script
- [x] Add packaging smoke tests
- [x] Add TestPyPI readiness docs
- [x] Add Trusted Publisher setup docs
- [x] Add PyPI publishing docs
- [x] Add semantic upload dry-run flow
- [x] Add integration docs for local assistant workflows

---

## Completed: v0.2.0 — Stable install story

Goal:

Make repo-signal installable, testable and believable as a daily CLI.

### Scope

- [x] Sync `VERSION`, `pyproject.toml`, README and CHANGELOG
- [x] Confirm latest GitHub release matches project version
- [x] Add `docs/PYPI.md`
- [x] Add `scripts/check-pypi-readiness.sh`
- [x] Add manual PyPI publish workflow
- [x] Configure PyPI Trusted Publisher on pypi.org
- [x] Create GitHub environment `pypi`
- [x] Publish to real PyPI
- [x] Verify `pipx install repo-signal` in clean environment — installs v0.2.0
- [x] Update README install section after real PyPI publishing
- [x] Keep local editable install documented for development
- [x] Keep TestPyPI workflow manual and gated

### Required verification

```bash
python3 -m pytest -q
repo-signal inspect .
repo-signal inspect --json . | python3 -m json.tool
repo-signal doctor
repo-signal publish-checklist . --fail-under 16
repo-signal demo --generate . --output examples/demo --force
scripts/check-generated-examples.sh
scripts/check-packaging.sh
scripts/check-testpypi-readiness.sh
scripts/check-trusted-publishing-setup.sh
scripts/check-pypi-readiness.sh
```

### Definition of done

- [x] `VERSION` matches release target
- [x] `pyproject.toml` matches release target
- [x] README install path is accurate
- [x] CHANGELOG has release entry
- [x] Packaging smoke test passes
- [x] TestPyPI path is documented
- [x] PyPI path is documented
- [x] GitHub Actions are green
- [x] GitHub release exists

---

## Completed: v0.2.1 — Version sync, source readability and release hygiene

Goal:

Make repo-signal easier to review, maintain and release.

This release should reduce friction before v0.3.0 contract work.

### Scope

- [x] Reformat raw README into normal markdown
- [x] Reformat raw `pyproject.toml` into normal TOML
- [x] Reformat long docs if needed
- [x] Add source readability check — `scripts/check-docs-consistency.sh`
- [x] Add version sync check — VERSION, pyproject, `__init__` agree
- [x] Add release metadata check — CHANGELOG guard in consistency check
- [x] Ensure roadmap, README and CHANGELOG agree
- [x] Ensure generated examples are current
- [x] Add proof section for current version — `## v0.2.1 status` in README
- [x] `.markdownlint.json` added

### Files to check

```text
README.md
CHANGELOG.md
ROADMAP.md
pyproject.toml
VERSION
release.sh
.github/workflows/*.yml
docs/*.md
examples/
```

### Definition of done

- [x] README is readable in raw mode
- [x] pyproject.toml is readable in raw mode
- [x] VERSION and pyproject agree
- [x] README and release badge agree
- [x] CHANGELOG includes current release
- [x] Generated examples are verified
- [x] Release check passes
- [x] GitHub Actions pass

---

## Completed: v0.3.0 — Stable repo intelligence contracts

Goal:

Make repo-signal the dependable backend contract for local AI-assisted
development workflows.

repo-signal should answer:

```text
What is this repo?
What state is it in?
What should happen next?
What context should an AI assistant receive?
```

### Primary focus

- Stabilize `inspect.v1`
- Stabilize `doctor.v1`
- Document JSON contracts clearly
- Keep CLI output human-readable
- Keep JSON output machine-readable
- Ensure generated examples match schemas
- Make downstream integrations fail safely on unknown schema versions

### Scope

- [x] `repo-signal inspect --json` produces valid `inspect.v1`
- [x] `repo-signal doctor --json` produces valid `doctor.v1`
- [x] Add schema validation tests — `tests/test_contracts.py` (14 tests)
- [x] `docs/INSPECT_SCHEMA.md` — full field reference
- [x] `docs/DOCTOR_SCHEMA.md` — full field reference, `schema` field added
- [x] `docs/INTEGRATIONS.md` — consumer examples for mqlaunch, mq-agent, mq-mcp, mq-hal
- [x] Integration examples for mqlaunch
- [x] Integration examples for mq-agent
- [x] Integration examples for mq-mcp
- [x] Integration examples for mq-hal
- [x] Failure behavior documented for unknown schema versions

### Integration contract rule

Consumers should not parse terminal text.

Consumers should prefer:

```bash
repo-signal inspect --json .
```

And check:

```json
{
  "schema": "inspect.v1"
}
```

Consumers must fail safely when the schema is unknown.

### Definition of done

- [x] `inspect.v1` documented
- [x] `doctor.v1` documented
- [x] Generated examples validate against expected shape
- [x] Integrations doc explains safe consumption
- [x] Release checklist passes
- [x] Packaging check passes
- [x] GitHub Actions pass
- [x] GitHub release `v0.3.0` exists

---

## Completed: v0.4.0 — mq ecosystem integration

Goal:

Make repo-signal useful as a shared repo intelligence layer for the mq ecosystem.

### Target consumers

```text
mqlaunch
mq-agent
mq-mcp
mq-hal
Bridget
```

### Planned scope

- [x] `docs/MQ_ECOSYSTEM.md` — architecture, consumer table, troubleshooting
- [x] `examples/integrations/inspect_safe.sh` — safe shell consumer
- [x] `examples/integrations/readiness_gate.sh` — CI gate script
- [x] `examples/integrations/mq_agent_consumer.py` — Python consumer for mq-agent
- [x] `tests/test_mq_ecosystem.py` — 10 integration smoke tests
- [x] Troubleshooting for missing repo-signal in PATH
- [x] CI/readiness gate examples

### Example target flow

```text
mqlaunch
  ↓
repo-signal inspect --json
  ↓
mq-agent / mq-hal
  ↓
release decision or improvement plan
```

### Definition of done

- [x] Integration docs exist
- [x] Integration examples exist and run
- [x] mq-agent safe consumer pattern documented and tested
- [x] CI/readiness gate example works
- [x] GitHub Actions pass

---

## Completed: v0.5.0 — Semantic repository memory hardening

Goal:

Make repo-signal the source of high-signal repo memory for AI assistants.

This should build on the existing semantic upload work, but make it safer,
clearer and easier to verify.

### Planned scope

- [x] Stabilize `repo-signal semantic-upload --dry-run` — verified output documented
- [x] Document required environment variables (`OPENAI_VECTOR_STORE_ID`, `OPENAI_API_KEY`)
- [x] Add dry-run proof output in `docs/SEMANTIC_MEMORY.md`
- [x] Add upload approval guidance — failure states and fix instructions
- [x] Add failure handling for missing vector store (exit 2, clear error)
- [x] Add failure handling for missing API key
- [x] Add mq-agent memory integration example
- [x] Add no-secret guarantee — documented and tested

### Safety rules

- No upload by default
- Dry-run first
- Never upload secrets
- Show file list before upload
- Show byte count before upload
- Show vector store target before upload
- Fail clearly when vector store is missing

### Definition of done

- [x] Semantic upload dry-run is stable
- [x] Upload behavior is explicitly gated (exits 2 if vector store missing)
- [x] Docs include real verified example output
- [x] mq-agent can consume the memory workflow
- [x] Tests cover missing env cases (12 tests)
- [x] GitHub Actions pass

---

## Completed: v0.6.0 — Unified report and export

Goal:

Make repo-signal outputs easier to share and compare.

### Completed scope

- [x] `repo-signal report [path] [--format text|markdown|json]` — unified report
- [x] `report.v1` JSON schema
- [x] `repo_signal/report.py` — `build_report`, `format_report`
- [x] `tests/test_report.py` — 17 tests
- [x] 134 tests total

### Possible commands

```bash
repo-signal report .
repo-signal report . --format markdown
repo-signal report . --format json
repo-signal compare ./repo-a ./repo-b
```

---

## Completed: v0.7.0 — Safe patch suggestion planning

Goal:

Help users understand possible improvements without mutating repositories
automatically.

### Completed scope

- [x] `repo-signal suggest [path] [--format text|markdown|json]` — safe patch suggestions
- [x] `suggest.v1` JSON schema for machine-readable integrations
- [x] `repo_signal/suggest.py` — `build_suggestions`, `format_suggestions`
- [x] No-write default — never touches the repository
- [x] Diff preview format per suggestion
- [x] Risk classification (low / medium / high)
- [x] Suggested commit grouping (docs / hygiene / release / testing / ci / pages)
- [x] `tests/test_suggest.py` — 23 tests including explicit no-mutation guarantees
- [x] `repo_suggest` tool registered in mq-agent TOOL_REGISTRY
- [x] `tasks/suggest.yaml` — mqlaunch task using 8 tools end-to-end
- [x] 157 tests pass

### Non-goals

- No automatic code rewriting
- No remote repository mutation
- No automatic commit
- No automatic push
- No destructive file changes

---

## Completed: v0.7.1 — Contract proof and docs completeness

Goal:

Prove that `report.v1` and `suggest.v1` contracts are documented, tested, and
verifiable — closing the gap between v0.7.0 and v1.0.0 stability.

### Completed scope

- [x] `docs/REPORT_SCHEMA.md` — full field reference for `report.v1`
- [x] `docs/SUGGEST_SCHEMA.md` — full field reference for `suggest.v1`, no-mutation guarantee
- [x] `docs/COMMANDS.md` — added `repo-signal report` and `repo-signal suggest` command entries
- [x] `examples/report/` — generated `report.v1.json`, `report.txt`, `report.md`
- [x] `examples/suggest/` — generated `suggest.v1.json`, `suggest.txt`, `suggest.md`
- [x] `release.sh` — added `report.v1` and `suggest.v1` schema checks
- [x] ROADMAP v0.6.0 title cleanup — "dashboard artifacts" → "unified report and export"
- [x] CHANGELOG v0.7.1

---

## v1.0.0 — Stable repo intelligence platform

Goal:

Lock CLI surface, contracts, docs, and release flow. No new commands until stable.

### What "stable" means for v1.0.0

```text
Stable CLI   = command names and flags do not change without major version bump
Stable JSON  = schema field names do not change without schema version bump
Stable docs  = every stable command has a schema doc, command doc, and example
Stable CI    = tests pass on every push, release.sh gates every release
Stable PyPI  = `pipx install repo-signal` installs a working version
```

### Stable commands (locked at v1.0.0)

```text
repo-signal analyze
repo-signal inspect / inspect --json    → inspect.v1
repo-signal doctor  / doctor --json     → doctor.v1
repo-signal publish-checklist
repo-signal report  / report --json     → report.v1
repo-signal suggest / suggest --json    → suggest.v1
repo-signal repoaware
repo-signal demo
```

### v1.0.0 checklist

**CLI freeze:**

- [x] No rename or removal of stable commands above before v2.0.0
- [x] `--help` output accurate for all stable commands
- [x] `--version` returns correct version

**Contract freeze:**

- [x] `inspect.v1` schema fields frozen
- [x] `doctor.v1` schema fields frozen
- [x] `report.v1` schema fields frozen
- [x] `suggest.v1` schema fields frozen
- [x] All four schemas documented in `docs/`

**Docs complete:**

- [x] Every stable command has an entry in `docs/COMMANDS.md`
- [x] `examples/` has generated output for all stable JSON commands
- [x] `docs/INTEGRATIONS.md` covers all four JSON contracts

**Release discipline:**

- [x] `release.sh` validates all four schema contracts
- [x] VERSION, pyproject.toml, `__init__.py` agree before every release
- [x] CHANGELOG has entry for every release
- [x] GitHub release exists for every tagged version
- [x] `pipx install repo-signal` works

**Quality gates:**

- [x] Full test suite passes on every push
- [x] Green CI on main
- [x] `repo-signal publish-checklist . --fail-under 16` passes

### Not in v1.0.0 scope

- New commands (wiki, roadmap, positioning, hygiene, ask, readme are not stable)
- Breaking changes to stable commands
- Dashboard export
- Repo comparison mode
- TUI or GUI

---

## v1.1.0 — Symbolic intelligence exports — Done

Goal:

Make repo-signal the preprocessing and repository-intelligence layer for the mq
ecosystem without becoming a review or cognition engine.

- [x] `symbol_index.v1` — public symbols, file inventory, ownership hints
- [x] `callgraph.v1` — import/source dependency graph, hub files, per-file maps
- [x] `repo_summary.v1` — compact repo context for AI consumer injection
- [x] `risk_map.v1` — structural risks (large files, no tests, high fan-in, missing docs)
- [x] `repo-signal export` CLI command with selective pack flags
- [x] `docs/EXPORT_SCHEMAS.md` — full field reference and mq-mcp integration pattern
- [x] `examples/exports/` — generated output for all four schema contracts
- [x] 31 tests in `tests/test_exports.py` (schema, fields, selective, CLI smoke)

### Non-goals (unchanged)

- No review generation
- No architecture reasoning runtime
- No prompt framework
- No repository mutation

---

## v1.2.0 — mq-mcp pack merge integration

Goal:

Verify and prove that mq-mcp correctly consumes the `.repo-signal/exports/`
packs produced by `repo-signal export`, and that the full pipeline from
repo-signal output to mq-mcp callgraph enrichment works end-to-end.

The integration hook already exists in mq-mcp
(`callgraph_builder._try_merge_repo_signal_packs`). This release closes the
loop on the v1.1.0 symbolic exports by proving they are actually consumed
downstream.

### Integration flow

```text
repo-signal export .
  ↓
.repo-signal/exports/
  ├── callgraph.json      (callgraph.v1)
  ├── symbol_index.json   (symbol_index.v1)
  ├── repo_summary.json   (repo_summary.v1)
  └── risk_map.json       (risk_map.v1)
  ↓
mq-mcp callgraph_builder._try_merge_repo_signal_packs()
  ↓
enriched callgraph data for review and architecture tools
```

### Planned scope

- [x] End-to-end smoke test: `repo-signal export` → `.repo-signal/exports/` → mq-mcp merge reads all four packs
- [x] Verify schema fields consumed by mq-mcp match what repo-signal emits
  - `callgraph.v1` edges `{source, target, relation}` and `hub_files`
  - `symbol_index.v1` flat symbols `{name, kind, file_path, is_public}`
  - `repo_summary.v1` compact context blob
  - `risk_map.v1` structural risks list
- [x] `docs/MQ_MCP_INTEGRATION.md` — step-by-step guide with verified example output
- [x] Add `examples/integrations/mq_mcp_pack_merge.sh` — runnable smoke script
- [x] Add `repo_signal_status` field to `docs/EXPORT_SCHEMAS.md`
- [x] Confirm graceful degradation when `.repo-signal/exports/` is absent

### Non-goals

- No changes to stable v1.1.0 export schemas
- No new export pack types in this release
- No mq-mcp internal refactoring

### Definition of done

- [x] All four v1 schema packs verified against mq-mcp consumer field expectations
- [x] End-to-end smoke script runs without error on at least one mq ecosystem repo
- [x] Integration guide exists in `docs/`
- [x] CHANGELOG has entry for v1.2.0
- [x] GitHub release `v1.2.0` exists
- [x] GitHub Actions status is tracked by the current release readiness checklist

---

## v1.5.0 — Review and memory export contract hardening

Goal:

Make the existing mqobsidian exports dependable integration contracts without
turning repo-signal into a durable memory store or review engine.

### Verified starting point

- [x] `repo-signal review-export` writes a fresh `inspect.v1` result as
  `repo-review.v1` below mqobsidian `reviews/`
- [x] Review export preserves `source_schema: inspect.v1`
- [x] Review export refuses accidental overwrite unless `--force` is explicit
- [x] Review export has focused unit and CLI tests
- [x] `memory-observation.v1` emission is opt-in and failure-isolated

### P0 — Lock the public contracts

- [x] Add `docs/REVIEW_EXPORT_SCHEMA.md` with fields, provenance, path rules and
  overwrite behavior for `repo-review.v1`
- [ ] Add a generated, public-safe `repo-review.v1` fixture under `examples/`
- [ ] Add `repo-review.v1` to `release.sh` contract checks
- [ ] Document `memory-observation.v1` producer fields and the explicit boundary:
  observations are proposals, not promoted memory
- [ ] Add focused tests for observation schema, no-issue behavior, opt-in gating
  and write-failure isolation
- [ ] Verify both exporters reject or redact machine-local paths and secret-like
  values in generated artifacts

### P1 — Keep CLI truth synchronized

- [ ] Define the command list once and reuse it for help, dispatch validation and
  command documentation checks
- [ ] Ensure `--help` includes `brief`, `export`, `readiness`, `review-export` and
  `suggest`
- [ ] Add a test that every dispatched top-level command is discoverable in
  `--help`
- [ ] Add a docs consistency check covering README examples and
  `docs/COMMANDS.md`
- [ ] Verify source execution and the installed `repo-signal` entrypoint on
  supported Python versions

### P2 — Prove the mqobsidian boundary end to end

- [ ] Add a temporary-vault smoke test for inspect → review export → schema read
- [ ] Add a temporary-vault smoke test for inspect → observation append without
  touching durable notes
- [ ] Document ownership: repo-signal produces signals; mqobsidian stores them;
  mq-agent owns scoring, promotion and workflow orchestration
- [ ] Document failure behavior for a missing vault, unwritable output and an
  unknown source schema
- [ ] Add one integration example that uses `MQ_OBSIDIAN_DIR` and contains no
  user-specific absolute path

### Definition of done

- [ ] Full test suite passes on supported Python versions
- [ ] `repo-signal --help` matches the live command surface
- [ ] Review and observation contracts have docs, tests and public-safe examples
- [ ] Release checks validate both mqobsidian export paths
- [ ] README, ROADMAP, CHANGELOG and VERSION agree on v1.5.0
- [ ] GitHub Actions are green before release

### Non-goals

- No memory scoring or promotion in repo-signal
- No review generation or architecture reasoning runtime
- No automatic commit, push or remote vault mutation
- No new export schema unless an existing contract cannot be extended safely

---

## Long-term ideas

These are intentionally not scheduled yet.

- repo comparison mode
- reusable GitHub Actions workflow
- dashboard export
- public portfolio report
- repo health history
- generated architecture diagrams
- mq ecosystem dashboard
- safe patch planning UI
- local TUI
- semantic memory comparison between releases
- repo quality trend analysis
- multi-repo morning brief
- integration with mq-ums
- integration with macos-scripts release-check
- generated demo videos or GIFs

---

## Design principles

repo-signal should remain:

- local-first
- script-friendly
- contract-driven
- safe by default
- useful without API keys
- helpful with AI context
- small enough to understand
- stable enough for other tools to consume
- readable in raw source form
- explicit about what it can and cannot do

repo-signal should produce signals.

It should not become an unsafe repo mutation engine.

---

## Safety principles

repo-signal must never:

- mutate repositories silently
- commit automatically
- push automatically
- upload memory silently
- hide generated changes
- require API keys for basic checks
- treat AI output as automatically trusted
- make downstream tools parse unstable terminal text

Every public-facing feature should have:

- command example
- docs link
- test or verification step
- changelog entry
- generated example when useful
- JSON contract when intended for integrations

---

## Release readiness checklist

Before creating a release, verify:

```bash
git status
python3 -m pytest -q
repo-signal inspect .
repo-signal inspect --json . | python3 -m json.tool
repo-signal doctor
repo-signal publish-checklist . --fail-under 16
repo-signal demo --generate . --output examples/demo --force
scripts/check-generated-examples.sh
scripts/check-packaging.sh
scripts/check-testpypi-readiness.sh
scripts/check-trusted-publishing-setup.sh
scripts/check-pypi-readiness.sh
```

A release should only be created when:

- tests pass
- `inspect` works
- `inspect --json` returns `schema: inspect.v1`
- `doctor` works
- `publish-checklist` passes
- generated examples are current
- README links to current docs
- CHANGELOG has an entry for the release
- VERSION and pyproject.toml agree
- GitHub Actions are green after push

---

## Current recommended next step

```text
v1.5.0 — Review and memory export contract hardening
```
