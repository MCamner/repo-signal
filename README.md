# repo-signal

[![Tests](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml/badge.svg)](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/MCamner/repo-signal?label=release)](https://github.com/MCamner/repo-signal/releases)

AI-native repository intelligence for structured reasoning systems.

`repo-signal` turns local repository state into clear analysis reports and
high-signal AI context exports. It helps you turn messy, undocumented
prototypes into clear, publishable GitHub projects.

---

## Install

Current local development install:

```bash
git clone https://github.com/MCamner/repo-signal.git
cd repo-signal
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ai]"
```

Future target:

```bash
pipx install repo-signal
```

`pipx` support is a packaging goal, not a published install path yet.
See [Packaging](docs/PACKAGING.md).

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
- [RepoAware Review](examples/repoaware/review.md)

Generate your own local demo reports:

```bash
repo-signal demo --generate
```

---

## Deep Documentation

- [**Integrations**](docs/INTEGRATIONS.md) — How mqlaunch, mq-mcp, mq-hal, and Bridget consume `inspect.v1`
- [**RepoAware**](docs/REPOAWARE.md) — High-signal AI context ranking and export
- [**Semantic Memory**](docs/SEMANTIC_MEMORY.md) — Uploading symbol maps to vector stores
- [**Publish Checklist**](docs/PUBLISH_CHECKLIST.md) — CI quality gates and portfolio checks
- [**Command Reference**](docs/COMMANDS.md) — Detailed CLI usage and flags
- [**Roadmap**](ROADMAP.md) — Release direction, integration plan, and readiness checklist
- [**Generated Examples**](docs/GENERATED_EXAMPLES.md) — How examples are generated and verified before release
- [**Packaging**](docs/PACKAGING.md) — PyPI / pipx readiness plan and packaging smoke tests
- [**TestPyPI**](docs/TESTPYPI.md) — Safe dry-run path before real PyPI publishing
- [**Inspect Schema**](docs/INSPECT_SCHEMA.md) — Machine-readable contract for `inspect --json`
- [**Doctor Schema**](docs/DOCTOR_SCHEMA.md) — Machine-readable contract for `doctor --json`
- [**Repo Structure**](docs/README_STRUCTURE.md) — Best practices for project layout

---

## Planned features

Not started:

- safe patch suggestions
- positioning report

Partially implemented:

- GitHub Pages detection
- project type detection
- script/tool discovery
- wiki suggestion generator
- roadmap suggestion generator

---

## Author

Mattias Camner

Infrastructure / Platform Architect  
Builder of command surfaces, endpoint readiness prototypes, and structured
workflow systems.

---

## License

MIT
