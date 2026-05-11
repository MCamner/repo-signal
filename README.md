# repo-signal

[![Tests](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml/badge.svg)](https://github.com/MCamner/repo-signal/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/MCamner/repo-signal?label=release)](https://github.com/MCamner/repo-signal/releases)

AI-native repository intelligence for structured reasoning systems.

`repo-signal` turns local repository state into clear analysis reports and
high-signal AI context exports.

`repo-signal` scans a local repository and produces a practical signal report:

- what the repo is
- what is missing
- what looks broken
- what should be documented
- what should be cleaned up
- what the next useful commit should be

The goal is simple:

```text
turn messy repos into clear public systems
```

---

## Why this exists

Most repositories do not fail because the code is useless.

They fail because the project is hard to understand.

Common problems:

- unclear README
- no quick start
- no project structure
- no screenshots
- no roadmap
- weak positioning
- missing `.gitignore`
- tracked `.DS_Store`
- unclear GitHub Pages setup
- no wiki or docs
- scattered scripts
- no obvious next step

`repo-signal` helps turn those problems into a visible checklist.

---

## Core idea

```text
local repo → analyze → shared signals → focused next action
```

The tool helps answer:

```text
What is this repo?
What does it demonstrate?
What is missing?
What is confusing?
What should I fix first?
How do I make it easier for others to understand?
```

---

## Current status

Early MVP.

The first version can run a local scan and print a Markdown report.

```bash
repo-signal analyze
repo-signal doctor
```

```bash
repo-signal publish-checklist .
repo-signal readme-score .
```

```bash
repo-signal repoaware --mode debug "how does routing work"
```

---

## Quick start

Analyze this repo:

```bash
cd ~/repo-signal
repo-signal analyze
repo-signal doctor
```

Run it against another local repo:

```bash
cd ~/coolThing
repo-signal analyze
```

---

## Example output

```text
# Repo Signal Report

Repo: `coolThing`

## Checks

- [OK] README exists: `README.md`
- [OK] License exists: `LICENSE`
- [OK] .gitignore exists: `.gitignore`
- [OK] docs folder exists: `docs`

## Hygiene

- [WARN] Found `.DS_Store` files: 2

## Suggested next actions

1. Improve README clarity
2. Add or verify GitHub Pages docs
3. Remove tracked system files
4. Add project screenshots
5. Create or update Wiki pages
```

---

## Current features

- local repo scan
- front door analyze report
- doctor report for repo health, release maturity, docs quality,
  AI readiness, and suggested skills
- README detection
- README quality scoring
- publish checklist command for checking README, docs, screenshots, roadmap,
  GitHub Pages, and release readiness
- RepoAware context export for AI-assisted code questions
- RepoAware modes for debug, explain, architect, and review workflows
- ranked relevant files with summaries and focused snippets
- Signal Ranking Engine for higher-quality context selection
- LICENSE detection
- `.gitignore` detection
- `docs/` detection
- `.DS_Store` detection
- Markdown report output

---

## Planned features

- GitHub Pages detection
- project type detection
- script/tool discovery
- wiki suggestion generator
- roadmap suggestion generator
- safe patch suggestions
- positioning report

---

## Planned commands

```bash
repo-signal scan
repo-signal analyze
repo-signal doctor
```

```bash
repo-signal skill new repo-aware
repo-signal readme
repo-signal readme-score .
```

```bash
repo-signal wiki
repo-signal wiki plan .
repo-signal wiki export . --output docs/wiki-export
repo-signal roadmap
repo-signal hygiene
```

```bash
repo-signal repoaware --mode debug "how does routing work"
repo-signal repoaware --mode review --format markdown "what should I inspect first"
```

```bash
repo-signal patch
repo-signal positioning
```

---

## Publish Checklist

See real outputs:
[Publish checklist examples](examples/publish-checklist/README.md)

`publish-checklist` checks whether a repository has the public-facing basics
needed to look understandable and publishable:

- README
- LICENSE
- CHANGELOG
- VERSION
- docs folder
- GitHub Pages landing page
- screenshots or demo gallery
- roadmap
- issue templates
- safe sharing/security notes

```bash
repo-signal publish-checklist .
repo-signal publish-checklist ~/Design-Prototype
```

```bash
repo-signal publish-checklist . --format markdown
repo-signal publish-checklist . --format json
repo-signal publish-checklist . --fail-under 14
```

`publish-checklist` is the public readiness check before polishing or
releasing a repo. The default output is plain text; Markdown and JSON formats
are available for reports, CI checks, GitHub Actions, and automated audits.

## Command Surface

```text
repo-signal
├── analyze
├── ask
├── doctor
├── skill new
├── repoaware
├── readme
├── publish-checklist
├── roadmap
├── wiki
└── hygiene
```

`analyze` is the front door. It summarizes project type, languages, key
entrypoints, Git health, repo size, top directories, detected tooling, and
suggested focus areas.

```bash
repo-signal analyze
```

`doctor` is the readiness report. It connects the scanner, README scoring,
repo graph, and RepoAware priorities into one diagnosis:

```bash
repo-signal doctor
```

It reports:

- project type
- repo health
- release maturity
- docs quality
- AI readiness
- suggested skills
- RepoAware priority context

`skill new` creates a repo-local Codex skill scaffold:

```bash
repo-signal skill new repo-aware
repo-signal skill new release-readiness \
  --description "Use when preparing a repo release."
```

It writes:

```text
skills/<name>/SKILL.md
```

Then export it into Codex skill storage:

```bash
repo-signal export-codex <name>
```

---

## Core Model

The shared intelligence layer starts with one repository model:

```python
from repo_signal.core.models import Repository

repo = Repository.load(".")

repo.files
repo.languages
repo.entrypoints
repo.git.branch
repo.top_directories
repo.signals
repo.graph
```

`analyze` already uses this model. RepoAware, roadmap, wiki, and hygiene can
move onto the same foundation incrementally.

---

## RepoAware

RepoAware builds high-signal context exports for AI systems by combining:

- repo structure
- git state
- semantic relevance
- file ranking
- focused snippets

The important part is not more context. It is better context.

RepoAware ranks files with a small transparent signal model:

| Signal | Purpose |
| --- | --- |
| filename and path matches | favor files that are likely about the question |
| keyword frequency | keep obvious textual relevance |
| git modified and recent commit signals | surface active work when useful |
| launcher/menu/core path bonuses | prioritize operational entry points |
| shell entrypoint detection | find runnable command surfaces |
| docs and file-size penalties | reduce low-signal bulk |

<!-- markdownlint-disable MD013 -->
```bash
repo-signal repoaware --mode explain "how does dispatch work"
repo-signal repoaware --mode architect --format markdown "where is this coupled"
repo-signal repoaware --mode review --format claude "what are the risks"
repo-signal repoaware --copy "how does routing work"
```
<!-- markdownlint-enable MD013 -->

Modes tune the context instructions without adding agent complexity:

| Mode | Focus |
| --- | --- |
| `debug` | errors, routing, stack flow, modified files |
| `explain` | clear grounded explanation |
| `architect` | structure, modularity, coupling, roadmap |
| `review` | risks, maintainability, shell pitfalls, test gaps |

---

## Ask

`ask` is the first AI-backed workflow:

```text
repo scan
→ ranking
→ signal selection
→ context shrinking
→ AI answer
```

```bash
repo-signal ask "how does routing work"
repo-signal ask --dry-run "how does routing work"
```

AI providers are optional adapters. The core architecture still works without
API keys, embeddings, or a vector database. Vector stores should accelerate
semantic recall later, not replace ranking and signal selection.

Install optional AI dependencies when needed:

```bash
pip install "repo-signal[ai]"
```

`repo-signal ask` reads `OPENAI_API_KEY` from the process environment or an
ignored local env file if `python-dotenv` is installed. Do not commit API keys.

---

## What it scans

`repo-signal` should inspect:

```text
README.md
LICENSE
.gitignore
docs/
index.html
package.json
requirements.txt
pyproject.toml
scripts/
tools/
assets/
Git status
GitHub Pages structure
tracked system files
large obvious assets
project links
```

---

## Scoring model

Future reports should include simple scores:

| Area | Meaning |
| --- | --- |
| README clarity | Can someone understand the repo quickly? |
| Project structure | Are files organized clearly? |
| Demo readiness | Is there a working demo or clear run path? |
| Repo hygiene | Are junk files, ignores, and structure handled? |
| Positioning | Does the repo explain why it matters? |
| Maintenance | Is it easy to continue working on? |

Scores are not the point.

The point is to expose what to improve next.

---

## Suggested repo structure

```text
repo-signal/
├── README.md
├── LICENSE
├── .gitignore
├── bin/
│   └── repo-signal
├── repo_signal/
│   ├── __init__.py
│   ├── cli.py
│   ├── scanner.py
│   ├── rules.py
│   ├── report.py
│   ├── prompts.py
│   └── patcher.py
├── examples/
│   └── sample-report.md
└── docs/
    └── index.html
```

---

## Design principles

| Principle | Meaning |
| --- | --- |
| Local first | Run against the repo on your machine |
| Safe by default | Do not change files unless explicitly requested |
| Explain before patching | Show findings before suggesting edits |
| Copy-paste friendly | Generate clear terminal commands |
| No magic | Make recommendations understandable |
| Useful for real repos | Focus on practical repo improvement |

---

## What this is not

`repo-signal` is not:

- a generic linter
- a CI replacement
- a code quality oracle
- an automatic refactoring bot
- a tool that blindly rewrites projects

It is a repo intelligence assistant.

It helps improve the public shape of a project.

---

## Related projects

This project fits into the broader `MCamner` system:

| Project | Relationship |
| --- | --- |
| `macos-scripts` | Command surfaces and repeatable local workflows |
| `design-prototyp` | Dashboards, helper agents, endpoint readiness |
| `atlas-one` | Prompt routing and structured reasoning |
| `mcamner-journal` | Command surface for thinking |
| `coolThing` | Retro web experiments and local tool prototypes |

`repo-signal` connects them by improving how repos are explained, cleaned, and
positioned.

---

## Roadmap

See also: [docs/ROADMAP.md](docs/ROADMAP.md)

### Phase 1 — Static scanner

- detect key files
- detect project type
- detect GitHub Pages layout
- detect missing README sections
- detect `.DS_Store`
- detect missing `.gitignore`
- generate Markdown report

### Phase 2 — README Doctor

- suggest README structure
- generate README outline
- detect missing quick start
- detect missing live demo
- detect missing roadmap
- detect missing screenshots

### Phase 3 — Wiki Generator (mostly done)

- suggest wiki pages
- generate Home page
- generate Project Map
- generate Architecture page
- generate Roadmap page

### Phase 4 — Safe patch mode

- generate copy-paste `cat` commands
- generate Python patch scripts
- avoid destructive edits
- require explicit confirmation before changes

### Phase 5 — AI-assisted analysis

- optional prompt export
- optional local LLM / API integration
- summarize repo intent
- suggest positioning
- generate social posts or release notes

---

## Author

Mattias Camner

Infrastructure / Platform Architect  
Builder of command surfaces, endpoint readiness prototypes, and structured
workflow systems.

---

## License

MIT
