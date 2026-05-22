# repo-signal Positioning

`repo-signal` is a local repository intelligence CLI.

It helps builders, maintainers, and AI-assisted development workflows understand a repository quickly, decide what needs attention, and export high-signal context for downstream tools.

## One-line positioning

`repo-signal` turns local repository state into clear reports, readiness checks, and machine-readable contracts for AI-assisted development systems.

## Who it is for

- Developers turning prototypes into publishable GitHub projects.
- Builders maintaining many small tools and repos.
- AI-assisted workflows that need structured repository context.
- Local assistants such as `mqlaunch`, `mq-mcp`, `mq-hal`, and Bridget.
- Portfolio/project maintainers who want public-readiness checks before release.

## What problem it solves

Many repositories contain useful work but lack clear structure, documentation, release readiness, and machine-readable context.

`repo-signal` answers four practical questions:

1. What is this repo?
2. What state is it in?
3. What should happen next?
4. What should an AI assistant know before helping?

## Product pillars

### 1. Orientation

Commands such as `analyze` and `inspect` provide a quick front-door view of the repository.

### 2. Readiness

Commands such as `doctor` and `publish-checklist` identify missing public-quality signals.

### 3. Contracts

`inspect --json` provides the `inspect.v1` contract for integrations and automation.

### 4. AI context

`repoaware` and semantic-memory flows export compact, useful repository context for AI-assisted work.

## What repo-signal is not

`repo-signal` is not a full CI system, not a code generator, and not a tool that blindly edits repositories.

Its job is to make repository state visible, structured, and actionable.

## Integration direction

The most important long-term interface is the JSON contract layer:

- `inspect.v1` for fast repository state
- `doctor.v1` for deeper readiness diagnosis
- generated examples for stable downstream expectations

These contracts allow tools like `mqlaunch`, `mq-mcp`, `mq-hal`, and Bridget to reason about repositories without scraping terminal output.

## v0.3.0 positioning target

v0.3.0 should make `repo-signal` feel like a small but reliable repo intelligence layer:

```text
local repo
   ↓
repo-signal inspect / doctor / repoaware
   ↓
human report + JSON contract + AI context
   ↓
mqlaunch / mq-mcp / mq-hal / Bridget
```

The strongest next product move is to make `inspect.v1` and `doctor.v1` boring, stable, documented, and easy to consume.
