# repo-signal

[![Tests](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml/badge.svg)](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml)
[![PyPI publish](https://github.com/MCamner/repo-signal/actions/workflows/pypi.yml/badge.svg)](https://github.com/MCamner/repo-signal/actions/workflows/pypi.yml)
[![Release](https://img.shields.io/github/v/release/MCamner/repo-signal?label=release)](https://github.com/MCamner/repo-signal/releases)

AI-native repository intelligence for structured reasoning systems.

`repo-signal` turns local repository state into clear analysis reports and
high-signal AI context exports. It helps you turn messy, undocumented
prototypes into clear, publishable GitHub projects.

---

## Install

From PyPI:

```bash
pipx install repo-signal
```

Current local development install:

```bash
git clone https://github.com/MCamner/repo-signal.git
cd repo-signal
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ai]"
```

See [PyPI publishing guide](docs/PYPI.md) for the release workflow.

---

## Try this in 60 seconds

```bash
# Get a high-level overview
repo-signal analyze

# Fast status report and next commit suggestion
repo-signal inspect

# Machine-readable status for integrations
repo-signal inspect --json

# Full readiness diagnosis
repo-signal doctor

# Check public-readiness signals
repo-signal publish-checklist .
```

---

## Command Surface

```text
repo-signal
├── analyze            # Front-door orientation
├── inspect            # Fast status and next commit
├── inspect --json     # Machine-readable inspect.v1 contract
├── doctor             # Full readiness diagnosis
├── positioning        # Product positioning report
├── publish-checklist  # Public signal quality gate
├── repoaware          # AI context export
└── demo               # Generate example reports
```

See the [Command Surface](docs/COMMAND_SURFACE.md), [Command Reference](docs/COMMANDS.md), and [Roadmap](ROADMAP.md) for full details.

---

## Screenshots

![inspect](docs/screenshots/inspect.png)

![publish-checklist](docs/screenshots/publish-checklist.png)

![inspect --json](docs/screenshots/inspect-json.png)

---

## Examples

- [Doctor Report (Markdown)](examples/doctor/doctor.txt)
- [Doctor Report (JSON)](examples/doctor/doctor.v1.json)
- [Analyze Report](examples/analyze/analyze.txt)
- [Inspect Report](examples/inspect/inspect.txt)
- [Inspect JSON (inspect.v1)](examples/inspect/inspect.v1.json)
- [Positioning Report](examples/positioning/positioning.txt)
- [RepoAware Review](examples/repoaware/review.md)

Generate your own local demo reports:

```bash
repo-signal demo --generate
```

---

## Deep Documentation

- [**Positioning**](docs/POSITIONING.md) — What repo-signal is, who it is for, and how it fits local AI-assisted development workflows
- [**Positioning Report**](docs/POSITIONING_REPORT.md) — CLI report for repo audience, problem statement, README angle, and one-sentence pitch
- [**Integrations**](docs/INTEGRATIONS.md) — How mqlaunch, mq-mcp, mq-hal, and Bridget consume `inspect.v1`
- [**RepoAware**](docs/REPOAWARE.md) — High-signal AI context ranking and export
- [**Semantic Memory**](docs/SEMANTIC_MEMORY.md) — Uploading symbol maps to vector stores
- [**Publish Checklist**](docs/PUBLISH_CHECKLIST.md) — CI quality gates and portfolio checks
- [**Command Reference**](docs/COMMANDS.md) — Detailed CLI usage and flags
- [**Roadmap**](ROADMAP.md) — Release direction, integration plan, and readiness checklist
- [**Generated Examples**](docs/GENERATED_EXAMPLES.md) — How examples are generated and verified before release
- [**Packaging**](docs/PACKAGING.md) — PyPI / pipx readiness plan and packaging smoke tests
- [**TestPyPI**](docs/TESTPYPI.md) — Safe dry-run path before real PyPI publishing
- [**Trusted Publishing**](docs/TRUSTED_PUBLISHING.md) — TestPyPI Trusted Publisher setup values and safety rules
- [**PyPI**](docs/PYPI.md) — Real PyPI publishing guide and Trusted Publisher values
- [**Inspect Schema**](docs/INSPECT_SCHEMA.md) — Machine-readable contract for `inspect --json`
- [**Doctor Schema**](docs/DOCTOR_SCHEMA.md) — Machine-readable contract for `doctor --json`
- [**Repo Structure**](docs/README_STRUCTURE.md) — Best practices for project layout

---

## Planned features

Not started:

- safe patch suggestions

Partially implemented:

- positioning report
- GitHub Pages detection
- project type detection
- script/tool discovery
- wiki suggestion generator
- roadmap suggestion generator

---

## v0.3.0 status

- [x] `repo-signal inspect --json .` returns `schema: "inspect.v1"`
- [x] `repo-signal doctor --json .` returns `schema: "doctor.v1"`
- [x] Schema contract tests — 14 tests covering required fields, JSON roundtrip and safe consumption
- [x] `docs/INSPECT_SCHEMA.md` — full field reference for `inspect.v1`
- [x] `docs/DOCTOR_SCHEMA.md` — full field reference for `doctor.v1`
- [x] `docs/INTEGRATIONS.md` — consumer examples for mqlaunch, mq-agent, mq-mcp, mq-hal
- [x] 95 tests pass — `python3 -m pytest -q`
- [x] GitHub Actions green

---

## v0.2.1 status

- [x] Version sync — VERSION, pyproject.toml, `__version__` all agree
- [x] CHANGELOG entry for v0.2.1
- [x] `scripts/check-docs-consistency.sh` — version and readability guards
- [x] `scripts/check-packaging.sh` passes
- [x] `pipx install repo-signal` installs v0.2.0 from PyPI
- [x] 81 tests pass — `python3 -m pytest -q`
- [x] GitHub Actions green (Tests, Packaging, Generated examples, Publish checklist)
- [x] `.markdownlint.json` configured

---

## Author

Mattias Camner

Infrastructure / Platform Architect  
Builder of command surfaces, endpoint readiness prototypes, and structured
workflow systems.

---

## License

MIT
