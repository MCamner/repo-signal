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
v0.2.1 — version sync, source readability and release hygiene
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
| v0.2.1  | Version sync, source readability and release hygiene | Next                 |
| v0.3.0  | Stable repo intelligence contracts                   | Planned              |
| v0.4.0  | mq ecosystem integration                             | Planned              |
| v0.5.0  | Semantic repository memory hardening                 | Planned              |
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
- [ ] Configure PyPI Trusted Publisher on pypi.org
- [ ] Create GitHub environment `pypi`
- [ ] Publish to real PyPI only after TestPyPI is proven
- [ ] Verify `pipx install repo-signal` in clean environment
- [x] Update README install section after real PyPI publishing
- [ ] Keep local editable install documented for development
- [ ] Keep TestPyPI workflow manual and gated

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
- [ ] Packaging smoke test passes
- [x] TestPyPI path is documented
- [x] PyPI path is documented
- [ ] GitHub Actions are green
- [x] GitHub release exists

---

## Next maintenance: v0.2.1 — Version sync, source readability and release hygiene

Goal:

Make repo-signal easier to review, maintain and release.

This release should reduce friction before v0.3.0 contract work.

### Scope

- [ ] Reformat raw README into normal markdown
- [ ] Reformat raw `pyproject.toml` into normal TOML
- [ ] Reformat long docs if needed
- [ ] Add source readability check
- [ ] Add version sync check
- [ ] Add release metadata check
- [ ] Ensure roadmap, README and CHANGELOG agree
- [ ] Ensure generated examples are current
- [ ] Ensure docs links are valid
- [ ] Add proof section for current version
- [ ] Add branch protection recommendation to docs

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

- [ ] README is readable in raw mode
- [ ] pyproject.toml is readable in raw mode
- [ ] VERSION and pyproject agree
- [ ] README and release badge agree
- [ ] CHANGELOG includes current release
- [ ] Generated examples are verified
- [ ] Release check passes
- [ ] GitHub Actions pass

---

## v0.3.0 — Stable repo intelligence contracts

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

- [ ] `repo-signal inspect --json` produces valid `inspect.v1`
- [ ] `repo-signal doctor --json` produces valid `doctor.v1`
- [ ] Add schema validation tests for generated examples
- [ ] Add `docs/INSPECT_SCHEMA.md` proof examples
- [ ] Add `docs/DOCTOR_SCHEMA.md` proof examples
- [ ] Add `docs/INTEGRATIONS.md` examples for consumers
- [ ] Add example shell wrappers for `inspect --json`
- [ ] Add integration examples for mqlaunch
- [ ] Add integration examples for mq-agent
- [ ] Add integration examples for mq-mcp
- [ ] Add integration examples for mq-hal
- [ ] Add failure behavior for unknown schema versions
- [ ] Add command reference coverage for all public commands
- [ ] Add generated examples verification to CI
- [ ] Add release checklist to CI or release script

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

- [ ] `inspect.v1` documented
- [ ] `doctor.v1` documented
- [ ] Generated examples validate against expected shape
- [ ] Integrations doc explains safe consumption
- [ ] Command reference is complete
- [ ] Release checklist passes
- [ ] Packaging check passes
- [ ] GitHub Actions pass
- [ ] GitHub release `v0.3.0` exists

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

- [ ] Add `docs/MQ_ECOSYSTEM.md`
- [ ] Add mqlaunch examples
- [ ] Add mq-agent examples
- [ ] Add mq-mcp examples
- [ ] Add mq-hal examples
- [ ] Add Bridget/persona workflow examples
- [ ] Add `examples/integrations/`
- [ ] Add JSON contract smoke tests for integration examples
- [ ] Add local workflow diagrams
- [ ] Add command-output examples for each consumer
- [ ] Add troubleshooting for missing repo-signal in PATH
- [ ] Add examples for CI/readiness gates

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

- [ ] Integration docs exist
- [ ] Integration examples exist
- [ ] All examples are generated or verified
- [ ] mq-agent can call repo-signal reliably
- [ ] mq-hal can summarize repo-signal reliably
- [ ] mqlaunch docs point to repo-signal flows
- [ ] GitHub Actions pass

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
v0.2.1 — version sync, source readability and release hygiene
```

Do not start v0.3.0 contract work until version sync, packaging truth and source
readability are clean.

The most efficient path is:

```text
1. Fix version/source/readability drift  ← current
2. Stabilize inspect.v1 and doctor.v1
3. Integrate with mq ecosystem
4. Harden semantic memory
```
