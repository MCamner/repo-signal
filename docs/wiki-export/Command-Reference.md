# Command Reference

## analyze

Summarize repo type, stack, health, structure, tooling, and suggested focus areas.

```bash
repo-signal analyze
repo-signal analyze ~/other-repo
```

## doctor

Diagnose repo health, release maturity, docs quality, AI readiness, and suggested skills.

```bash
repo-signal doctor
repo-signal doctor ~/other-repo
```

## publish-checklist

Check public-facing basics: README, LICENSE, CHANGELOG, VERSION, docs, screenshots, roadmap, GitHub Pages, and issue templates.

```bash
repo-signal publish-checklist .
repo-signal publish-checklist ~/other-repo

# Output formats
repo-signal publish-checklist . --format text      # default
repo-signal publish-checklist . --format markdown
repo-signal publish-checklist . --format json

# CI quality gate — exit non-zero if score < threshold
repo-signal publish-checklist . --fail-under 14
repo-signal publish-checklist . --fail-under 16
repo-signal publish-checklist . --format json --fail-under 14
```

Exit code is `0` when score meets or exceeds `--fail-under`. Non-zero otherwise.

## portfolio check

Run publish-checklist across multiple local repos defined in `repo-signal.yml`.

```bash
repo-signal portfolio check
repo-signal portfolio check --format markdown
repo-signal portfolio check --format json
repo-signal portfolio check --config ~/repo-signal.yml
```

Configure repos in `repo-signal.yml`:

```yaml
portfolio:
  repos:
    - name: repo-signal
      path: ~/repo-signal
      fail_under: 16
    - name: macos-scripts
      path: ~/macos-scripts
      fail_under: 14
```

## actions init

Generate a GitHub Actions workflow that runs `publish-checklist` in CI.

```bash
repo-signal actions init
repo-signal actions init . --fail-under 14
repo-signal actions init . --fail-under 14 --force   # overwrite existing
```

Writes: `.github/workflows/publish-checklist.yml`

## wiki

Generate a suggested GitHub Wiki structure and Home draft.

```bash
repo-signal wiki plan .
repo-signal wiki export . --output docs/wiki-export
```

`wiki plan` prints a suggested page list. `wiki export` writes reviewable Markdown files to the output directory. Review them before copying to GitHub Wiki.

## readme-score

Score README quality with a 100-point checklist.

```bash
repo-signal readme-score .
repo-signal readme-score ~/other-repo
```

## hygiene

Check junk files, `.gitignore`, large files, and Git status.

```bash
repo-signal hygiene
```

## repoaware

Build high-signal repo context for AI-assisted code questions.

```bash
repo-signal repoaware --mode explain "how does routing work"
repo-signal repoaware --mode debug "why does this fail"
repo-signal repoaware --mode architect "where is coupling"
repo-signal repoaware --mode review "what are the risks"
repo-signal repoaware --mode review --format markdown "what should I inspect first"
repo-signal repoaware --copy "summarize the architecture"
```

Modes:

| Mode | Focus |
|---|---|
| `explain` | Clear grounded explanation |
| `debug` | Errors, routing, stack flow |
| `architect` | Structure, modularity, coupling |
| `review` | Risks, maintainability, test gaps |

## skill new

Create a repo-local Codex skill scaffold.

```bash
repo-signal skill new repo-aware
repo-signal skill new release-readiness --description "Use when preparing a release."
```

Writes: `skills/<name>/SKILL.md`

## roadmap

Generate a practical roadmap based on current repo state.

```bash
repo-signal roadmap
```

## scan

Scan repo structure and basic project signals.

```bash
repo-signal scan
```
