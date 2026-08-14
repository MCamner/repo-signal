# Command Reference

`repo-signal` is a local-first CLI for turning repository state into readable reports, public-readiness checks, and compact AI context.

Run commands from the repository you want to inspect unless a command accepts an explicit path.

## repo-signal analyze

Purpose:
Summarizes repository type, language mix, key entrypoints, tooling, Git health, and suggested focus areas.

Usage:

```bash
repo-signal analyze
repo-signal analyze ~/some-repo
```

Good for:

- first-pass repo orientation
- deciding what to inspect next
- checking whether the repo has obvious entrypoints and tooling

## repo-signal inspect

Purpose:
Shows a fast repository status report: repo type, Git state, public readiness, detected entrypoints/tooling, core files, likely issues, and recommended next commit.

Usage:

```bash
repo-signal inspect
repo-signal inspect ~/some-repo
repo-signal inspect --json
repo-signal inspect --format json
```

Good for:

- integration with mqlaunch, mq-hal, mq-mcp, and Bridget via `inspect.v1` JSON
- quick orientation before running the deeper doctor report
- checking what looks missing at the front door
- deciding the next useful commit

See also: [Inspect JSON schema](INSPECT_SCHEMA.md).

## repo-signal review-export

Purpose:
Runs a fresh `inspect.v1` analysis and exports a compact `repo-review.v1`
Markdown note to mqobsidian. The export preserves source-schema provenance and
does not include the target repository's absolute path.

Usage:

```bash
repo-signal review-export .
repo-signal review-export ~/some-repo --vault "$MQ_OBSIDIAN_DIR"
repo-signal review-export . --force
```

The default vault is `$MQ_OBSIDIAN_DIR`, falling back to `~/mqobsidian` when
that directory exists. Reviews are written under `reviews/`. Existing same-day
exports are not replaced unless `--force` is explicit.

## repo-signal demo

Purpose:
Prints a short copy-paste flow for trying the main commands, or generates local demo reports.

Usage:

```bash
repo-signal demo
repo-signal demo --generate
repo-signal demo --generate . --output examples/demo
repo-signal demo --generate . --output examples/demo --force
```

Output includes:

- `repo-signal analyze`
- `repo-signal doctor`
- `repo-signal doctor --json`
- `repo-signal publish-checklist .`
- `repo-signal repoaware --mode review --format markdown "what should I inspect first"`

Generated files:

- `README.md`
- `analyze.txt`
- `inspect.txt`
- `doctor.txt`
- `doctor.v1.json`
- `publish-checklist.txt`

## repo-signal doctor

Purpose:
Runs a broader readiness diagnosis across repo health, release maturity, docs quality, AI readiness, suggested skills, and RepoAware priorities.

Usage:

```bash
repo-signal doctor
repo-signal doctor ~/some-repo
repo-signal doctor --json
repo-signal doctor . --format json
```

Output:

- Markdown by default
- JSON with schema version `doctor.v1`

See [DOCTOR_SCHEMA.md](DOCTOR_SCHEMA.md) for the machine-readable contract.

## repo-signal publish-checklist

Purpose:
Checks whether a repo has the public-facing basics needed to look understandable and publishable.

Usage:

```bash
repo-signal publish-checklist .
repo-signal publish-checklist ~/some-repo
repo-signal publish-checklist . --format markdown
repo-signal publish-checklist . --format json
repo-signal publish-checklist . --fail-under 14
```

Checks include:

- README
- LICENSE
- CHANGELOG
- VERSION
- docs folder
- GitHub Pages landing page
- screenshots or demo gallery
- roadmap
- issue templates
- safe sharing and security notes

## repo-signal positioning

Purpose:
Analyzes README and repository signals to produce a product-positioning report.

Usage:

```bash
repo-signal positioning .
repo-signal positioning ~/some-repo
repo-signal positioning . --json
repo-signal positioning . --format json
```

Answers:

- what the project is
- who it is for
- what problem it solves
- the strongest README angle
- what is unclear
- a one-sentence positioning draft

JSON output uses schema `positioning.v1`.

See [POSITIONING_REPORT.md](POSITIONING_REPORT.md).

## repo-signal readme-score

Purpose:
Scores README quality with a 100-point checklist.

Usage:

```bash
repo-signal readme-score .
repo-signal readme-score ~/some-repo
```

Good for:

- finding missing onboarding sections
- improving public repo presentation
- checking whether the README can orient a cold visitor

## repo-signal repoaware

Purpose:
Builds high-signal repository context for AI-assisted code questions.

Usage:

```bash
repo-signal repoaware --mode explain "how does dispatch work"
repo-signal repoaware --mode debug "why does this fail"
repo-signal repoaware --mode architect --format markdown "where is this coupled"
repo-signal repoaware --mode review --format markdown "what should I inspect first"
repo-signal repoaware --copy "summarize the architecture"
```

Modes:

| Mode | Focus |
| --- | --- |
| `explain` | Clear grounded explanation |
| `debug` | Errors, routing, stack flow, modified files |
| `architect` | Structure, modularity, coupling, roadmap |
| `review` | Risks, maintainability, shell pitfalls, test gaps |

## repo-signal ask

Purpose:
Asks an AI provider using ranked RepoAware context.

Usage:

```bash
repo-signal ask "how does routing work"
repo-signal ask --dry-run "how does routing work"
```

Notes:

- AI providers are optional adapters.
- `--dry-run` is useful for inspecting the prompt/context without making an API call.
- `OPENAI_API_KEY` is read from the process environment when using OpenAI-backed answering.

## repo-signal semantic

Purpose:
Searches smart symbol chunks for semantic repository recall.

Usage:

```bash
repo-signal semantic "routing system"
repo-signal semantic --limit 10 "doctor schema"
```

## repo-signal semantic-upload

Purpose:
Builds a compact symbol memory document and uploads it to a scoped OpenAI vector store.

Usage:

```bash
repo-signal semantic-upload --dry-run
repo-signal semantic-upload
repo-signal semantic-upload --include-tests
repo-signal semantic-upload --vector-store-id vs_abc123
```

Configure the target vector store with:

```bash
export OPENAI_VECTOR_STORE_ID="vs_abc123"
```

## repo-signal portfolio check

Purpose:
Runs publish-readiness checks across multiple local repositories configured in `repo-signal.yml`.

Usage:

```bash
repo-signal portfolio check
repo-signal portfolio check --format markdown
repo-signal portfolio check --format json
repo-signal portfolio check --config ~/repo-signal.yml
```

## repo-signal actions init

Purpose:
Creates a GitHub Actions workflow that runs `publish-checklist` as a CI quality gate.

Usage:

```bash
repo-signal actions init
repo-signal actions init . --fail-under 14
repo-signal actions init . --fail-under 16 --force
```

Writes:

```text
.github/workflows/publish-checklist.yml
```

## repo-signal skill new

Purpose:
Creates a repo-local Codex skill scaffold.

Usage:

```bash
repo-signal skill new repo-aware
repo-signal skill new release-readiness --description "Use when preparing a repo release."
```

Writes:

```text
skills/<name>/SKILL.md
```

## repo-signal export-codex

Purpose:
Exports a repo-local skill into Codex skill storage.

Usage:

```bash
repo-signal export-codex repo-product-auditor
repo-signal export-codex repo-aware --local
```

## repo-signal wiki

Purpose:
Generates suggested GitHub Wiki structure, Home draft, or export files.

Usage:

```bash
repo-signal wiki
repo-signal wiki plan .
repo-signal wiki export . --output docs/wiki-export
repo-signal wiki export --help
```

`wiki export` builds each page from the target repository's own tracked files:
`README.md`, `VERSION`, `CHANGELOG.md`, `ROADMAP.md`, `docs/architecture.md`,
`docs/COMMANDS.md`, and `skills/`. A page whose source is missing says so
instead of inventing content, and gitignored files are never read — exported
pages are meant to be copied into a public wiki.

## repo-signal hygiene

Purpose:
Checks junk files, `.gitignore`, large files, and Git status.

Usage:

```bash
repo-signal hygiene
```

## repo-signal roadmap

Purpose:
Generates a practical roadmap based on repository state.

Usage:

```bash
repo-signal roadmap
```

## repo-signal report

Purpose:
Unified report combining inspect, publish-checklist, and hygiene signals into one output.
Produces `report.v1` JSON for machine-readable integrations.

Usage:

```bash
repo-signal report
repo-signal report ~/some-repo
repo-signal report . --format text
repo-signal report . --format markdown
repo-signal report . --format json
```

Good for:

- single-command repo health overview
- CI report artifacts
- integration with mqlaunch, mq-agent, and mq-mcp via `report.v1` JSON

See also: [Report JSON schema](REPORT_SCHEMA.md).

## repo-signal suggest

Purpose:
Produces safe, human-reviewable patch suggestions based on publish-checklist signals.
Never writes to the repository. Read-only output only.

Usage:

```bash
repo-signal suggest
repo-signal suggest ~/some-repo
repo-signal suggest . --format text
repo-signal suggest . --format markdown
repo-signal suggest . --format json
```

Good for:

- identifying missing docs, hygiene, or release files
- planning the next batch of commits
- integration with mq-agent for automated improvement workflows

Output includes:

- suggestion title and explanation
- risk classification: `low`, `medium`, `high`
- commit group: `docs`, `hygiene`, `release`, `testing`, `ci`, `pages`, `examples`
- illustrative diff preview (not a real patch)
- shell command hint for applying the suggestion

See also: [Suggest JSON schema](SUGGEST_SCHEMA.md).

## See Also

- [Report JSON Schema](REPORT_SCHEMA.md)
- [Suggest JSON Schema](SUGGEST_SCHEMA.md)
- [Inspect JSON Schema](INSPECT_SCHEMA.md)
- [Doctor JSON Schema](DOCTOR_SCHEMA.md)
- [Doctor JSON Output](DOCTOR_JSON.md)
- [Screenshots and output gallery](screenshots/README.md)
- [Publish checklist examples](../examples/publish-checklist/README.md)
