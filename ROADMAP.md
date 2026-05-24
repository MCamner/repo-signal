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
v0.5.0 — semantic repository memory hardening
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
├── repoaware
└── demo
```

Additional documented commands include `positioning`, `semantic-upload`,
`ask`, `readme`, `roadmap`, `wiki`, `hygiene`, `actions init` and `skill new`.
The contract work below should separate stable integration commands from
experimental or helper commands.

Current stable contracts:

```text
inspect.v1
doctor.v1
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
| v0.5.0  | Semantic repository memory hardening                 | Next                 |
| v0.6.0  | Report/export and dashboard artifacts                | Planned              |
| v0.7.0  | Safe patch suggestion planning                       | Planned              |
| v1.0.0  | Stable repo intelligence platform                    | Future               |

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

## Current: v0.2.0 — Stable install story

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

## v0.4.0 — mq ecosystem integration

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

## v0.5.0 — Semantic repository memory hardening

Goal:

Make repo-signal the source of high-signal repo memory for AI assistants.

This should build on the existing semantic upload work, but make it safer,
clearer and easier to verify.

### Planned scope

- [ ] Stabilize `repo-signal semantic-upload --dry-run`
- [ ] Document required environment variables
- [ ] Document `OPENAI_VECTOR_STORE_ID`
- [ ] Add semantic memory status command or report
- [ ] Add stale memory detection
- [ ] Add symbol memory freshness metadata
- [ ] Add dry-run proof output
- [ ] Add upload approval guidance
- [ ] Add generated symbol memory example
- [ ] Add failure handling for missing vector store
- [ ] Add failure handling for missing API key
- [ ] Add docs for shared semantic repository memory store
- [ ] Add mq-agent memory integration example
- [ ] Add no-secret guarantee for uploaded files

### Safety rules

- No upload by default
- Dry-run first
- Never upload secrets
- Show file list before upload
- Show byte count before upload
- Show vector store target before upload
- Fail clearly when vector store is missing

### Definition of done

- [ ] Semantic upload dry-run is stable
- [ ] Upload behavior is explicitly gated
- [ ] Docs include real example output
- [ ] mq-agent can consume the memory workflow
- [ ] Tests cover missing env cases
- [ ] GitHub Actions pass

---

## v0.6.0 — Report/export and dashboard artifacts

Goal:

Make repo-signal outputs easier to share and compare.

### Planned scope

- [ ] Add markdown report export
- [ ] Add JSON report export
- [ ] Add dashboard-ready export
- [ ] Add repo health history format
- [ ] Add publish-readiness report
- [ ] Add portfolio report
- [ ] Add comparison-friendly output
- [ ] Add generated artifact examples
- [ ] Add GitHub Pages report demo

### Possible commands

```bash
repo-signal report .
repo-signal report . --format markdown
repo-signal report . --format json
repo-signal compare ./repo-a ./repo-b
```

---

## v0.7.0 — Safe patch suggestion planning

Goal:

Help users understand possible improvements without mutating repositories
automatically.

### Planned scope

- [ ] Add safe patch suggestion report
- [ ] Add no-write default
- [ ] Add diff preview format
- [ ] Add risk classification
- [ ] Add suggested commit grouping
- [ ] Add docs for human review
- [ ] Add tests for no-mutation behavior

### Non-goals

- No automatic code rewriting
- No remote repository mutation
- No automatic commit
- No automatic push
- No destructive file changes

---

## v1.0.0 — Stable repo intelligence platform

Goal:

Make repo-signal stable enough to be the default repo intelligence engine for
local AI-assisted development workflows.

### v1.0.0 requirements

- [ ] Stable CLI command surface
- [ ] Stable `inspect.v1`
- [ ] Stable `doctor.v1`
- [ ] Stable generated examples
- [ ] Stable install path
- [ ] Stable PyPI package
- [ ] Stable docs
- [ ] Stable release flow
- [ ] Stable semantic memory workflow
- [ ] Complete integration docs
- [ ] Complete command reference
- [ ] Complete troubleshooting docs
- [ ] Green CI
- [ ] Protected main branch
- [ ] GitHub release
- [ ] GitHub Pages documentation
- [ ] No known critical safety gaps

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

Work on:

```text
v0.5.0 — semantic repository memory hardening
```

Make repo-signal the reliable source of high-signal repo memory for AI assistants.

The most efficient path is:

```text
1. Harden semantic memory  ← current
2. Report/export artifacts
3. Safe patch suggestion planning
```
