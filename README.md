# repo-signal

AI-assisted repo analysis for turning rough prototypes into clear, documented, publishable GitHub projects.

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
local repo → scan → signal report → safe improvement plan
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
./bin/repo-signal scan
```

---

## Quick start

Run the scanner against this repo:

```bash
cd ~/repo-signal
./bin/repo-signal scan
```

Run it against another local repo:

```bash
cd ~/coolThing
~/repo-signal/bin/repo-signal scan
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
- README detection
- LICENSE detection
- `.gitignore` detection
- `docs/` detection
- `.DS_Store` detection
- Markdown report output

---

## Planned features

- README quality scoring
- GitHub Pages detection
- project type detection
- script/tool discovery
- wiki suggestion generator
- roadmap suggestion generator
- safe patch suggestions
- positioning report
- screenshot/docs checklist

---

## Planned commands

```bash
repo-signal scan
repo-signal readme
repo-signal wiki
repo-signal roadmap
repo-signal hygiene
repo-signal patch
repo-signal positioning
```

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
|---|---|
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
|---|---|
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
|---|---|
| `macos-scripts` | Command surfaces and repeatable local workflows |
| `Design-Prototype` | Dashboards, helper agents, endpoint readiness |
| `atlas-one` | Prompt routing and structured reasoning |
| `mcamner-journal` | Command surface for thinking |
| `coolThing` | Retro web experiments and local tool prototypes |

`repo-signal` connects them by improving how repos are explained, cleaned, and positioned.

---

## Roadmap

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

### Phase 3 — Wiki Generator

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
Builder of command surfaces, endpoint readiness prototypes, and structured workflow systems.

---

## License

MIT
