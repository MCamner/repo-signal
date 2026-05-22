# Roadmap

`repo-signal` is an AI-native repository intelligence CLI for turning rough
local repositories into clear, documented, publishable GitHub projects.

This roadmap is intentionally practical. It tracks what is stable, what is
next, and what must be true before each release.

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

Focus: `v0.1.20 — TestPyPI publishing dry run`

Planned work:

- [x] Add `docs/PACKAGING.md`
- [x] Add `scripts/check-packaging.sh`
- [x] Add packaging CI workflow
- [x] Validate wheel build and clean virtual environment install
- [x] Verify console script from installed wheel
- [x] Document future pipx install path without claiming publication
- [x] Add `scripts/check-generated-examples.sh`
- [x] Add `scripts/generate-examples.sh`
- [x] Add CI workflow for generated examples
- [x] Add generated examples documentation
- [x] Verify `inspect.v1` and `doctor.v1` examples before release

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

- [ ] `repo-signal positioning`
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
v0.2.0  — stable local repo intelligence CLI
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
