# Command Surface

```text
repo-signal
├── actions init
├── analyze
├── inspect
├── ask
├── doctor
├── positioning
├── skill new
├── repoaware
├── readme
├── publish-checklist
├── semantic-upload
├── roadmap
├── wiki
└── hygiene
```

## Quick Commands

`inspect` is the fast status command. It summarizes repo type, Git state,
public readiness, detected signals, possible issues, and the next useful
commit.

```bash
repo-signal inspect
repo-signal inspect ~/some-repo
repo-signal inspect --json
repo-signal inspect --format json
```

`inspect --json` emits the stable `inspect.v1` JSON contract consumed by
mqlaunch, mq-mcp, Bridget, mq-hal, and CI helpers. See
[Inspect Schema](INSPECT_SCHEMA.md) for the full field reference.

`analyze` is the front door. It summarizes project type, languages, key
entrypoints, Git health, repo size, top directories, detected tooling, and
suggested focus areas.

```bash
repo-signal analyze
```

`positioning` turns README and repository signals into a concise product
positioning report:

```bash
repo-signal positioning .
repo-signal positioning . --json
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

## Skill Management

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

For a full list of commands and options, see the [Command Reference](COMMANDS.md).
