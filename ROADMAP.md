# Roadmap

`repo-signal` is an AI-native repository intelligence CLI for turning rough
local repositories into clear, documented, publishable GitHub projects.

This roadmap is intentionally practical. It tracks what is stable, what is
next, and what must be true before each release.

## v0.3.0 Target — Integration Polish and Positioning

v0.3.0 should make `repo-signal` feel less like a collection of useful checks and more like a coherent repository intelligence layer for local AI-assisted development workflows.

### Goal

Make `repo-signal` the small, dependable CLI that answers:

> What is this repo, what state is it in, what should happen next, and what context should an AI assistant receive?

### Primary focus

- Strengthen `inspect.v1` as the stable integration contract.
- Improve positioning so the project is clearly understood as a repo intelligence and publish-readiness tool.
- Keep the CLI surface small, predictable, and script-friendly.
- Make generated examples and schemas reliable enough for downstream tools.
- Prepare cleaner integration paths for `mqlaunch`, `mq-mcp`, `mq-hal`, and Bridget.

### Scope

Planned for v0.3.0:

- `positioning` report for README/product clarity.
- `doctor --json` contract stabilization.
- Stronger command reference coverage.
- Clearer roadmap and positioning documentation.
- Integration examples for local assistant workflows.
- Packaging and install smoke tests kept in release readiness.
- Generated examples verified before release.

Not planned for v0.3.0:

- Automatic code rewriting.
- Risky patch application.
- Remote repository mutation.
- Release automation beyond existing safe checks.

### Readiness checklist

- [ ] `repo-signal inspect --json` produces valid `inspect.v1`.
- [ ] `repo-signal doctor` gives a clear human-readable readiness report.
- [ ] `repo-signal doctor --json` is documented or explicitly marked experimental.
- [ ] `repo-signal publish-checklist . --fail-under 16` passes.
- [ ] `repo-signal demo --generate` refreshes example outputs.
- [ ] Generated examples are verified by CI.
- [ ] Packaging smoke test passes.
- [x] README explains who the tool is for in one sentence.
- [ ] `repo-signal positioning . --json` produces valid `positioning.v1`.
- [ ] Integrations doc explains how `mqlaunch`, `mq-mcp`, `mq-hal`, and Bridget consume `inspect.v1`.
- [ ] CHANGELOG has a clear v0.3.0 section before release.

### Recommended v0.3.0 release theme

> Stable repo intelligence contracts for local AI-assisted development workflows.

## Current status

Current release: `v0.1.19 — PyPI / pipx readiness plan`

Stable enough to use:

- `repo-signal analyze`
- `repo-signal inspect`
- `repo-signal inspect --json`
- `repo-signal doctor`
- `repo-signal publish-checklist`
- `repo-signal repoaware`
- `repo-signal demo --generate`

Core contracts:

- `inspect.v1`
- `doctor.v1`

## Product direction

`repo-signal` should become the local repo-status engine for:

- developers cleaning up old prototypes
- portfolio projects
- release readiness checks
- AI-assisted repository reviews
- local assistant workflows
- command surfaces such as `mqlaunch`
- tool bridges such as `mq-mcp`
- assistant/persona layers such as `mq-hal` and Bridget

## Command surface

```text
repo-signal
├── analyze            # front-door orientation
├── inspect            # fast status and next commit
├── inspect --json     # inspect.v1 integration contract
├── doctor             # deeper readiness diagnosis
├── publish-checklist  # public quality gate
├── repoaware          # AI context export
└── demo               # generate example reports
```

## Now

Focus: `v0.2.0 — stable install story`

Planned work:

- [x] Add `docs/TESTPYPI.md`
- [x] Add `scripts/check-testpypi-readiness.sh`
- [x] Add manual GitHub Actions workflow for TestPyPI dry run
- [x] Verify build artifacts with `twine check`
- [x] Document TestPyPI install verification
- [x] Keep real PyPI publishing disabled until TestPyPI is proven
- [x] Add `docs/TRUSTED_PUBLISHING.md`
- [x] Add `scripts/check-trusted-publishing-setup.sh`
- [x] Document TestPyPI Trusted Publisher values
- [x] Verify GitHub Actions workflow uses `id-token: write`
- [x] Verify workflow uses `environment: testpypi`
- [x] Keep upload manual behind `publish_to_testpypi = true`
- [x] Verify TestPyPI install in clean venv — CLI and inspect.v1 OK
- [ ] Add `docs/PYPI.md`
- [ ] Add `scripts/check-pypi-readiness.sh`
- [ ] Add manual PyPI publish workflow
- [ ] Configure PyPI Trusted Publisher on pypi.org
- [ ] Create GitHub environment `pypi`
- [ ] Publish to real PyPI
- [ ] Verify `pipx install repo-signal` in clean environment
- [ ] Update README install section to `pipx install repo-signal`

## Next

Focus: stronger local automation and publishability.

Planned work:

- [ ] Add `docs/INTEGRATIONS.md`
- [ ] Add `examples/integrations/`
- [ ] Add sample shell wrappers for consuming `inspect --json`
- [ ] Add JSON contract smoke tests for generated examples
- [ ] Improve release notes template
- [ ] Add release checklist to CI or `release.sh`
- [ ] Prepare PyPI / pipx packaging plan

## Later

Longer-term ideas:

- [x] `repo-signal positioning`
- [ ] safe patch suggestions
- [ ] public portfolio report
- [ ] repo comparison mode
- [ ] GitHub Actions reusable workflow
- [ ] dashboard export
- [ ] package publishing to PyPI
- [ ] `pipx install repo-signal`

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
- VERSION and `pyproject.toml` are updated by the release flow
- GitHub Actions is green after push

## Release naming

Use short, visible release names.

Examples:

```text
v0.1.15 — inspect JSON integration contract
v0.1.16 — integration docs and release polish
v0.1.17 — generated examples verification
v0.1.19 — PyPI / pipx readiness plan
v0.1.20 — TestPyPI publishing dry run
v0.1.21 — TestPyPI trusted publishing setup
v0.2.0  — stable install story
```

## Version milestones

### v0.1.x

Goal: make the command surface useful, documented, and safe for local use.

Expected qualities:

- clear README
- strong docs
- stable text reports
- stable JSON contracts
- generated examples
- passing tests
- GitHub Pages
- release notes

### v0.2.0

Goal: make `repo-signal` feel like a stable daily CLI.

Expected qualities:

- clean install path
- stronger integration docs
- better generated examples
- stronger JSON contract tests
- cleaner release flow
- documented package publishing path

### v0.3.0

Goal: make `repo-signal` useful as a backend for local AI assistants.

Expected qualities:

- stable integration examples
- strong `mqlaunch`/`mq-mcp`/`mq-hal` workflows
- clearer automation hooks
- dashboard/report export options

## Integration contract rule

Tools should not parse terminal text.

Consumers should prefer:

```bash
repo-signal inspect --json
```

and check:

```json
{
  "schema": "inspect.v1"
}
```

Consumers should fail safely when the schema is unknown.

## Definition of done

A roadmap item is done when it has:

- implementation or documentation
- command example
- test or verification step
- README or docs link when public-facing
- changelog entry
- release note when shipped
