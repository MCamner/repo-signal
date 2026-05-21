# Generated Examples

`repo-signal` uses generated examples as public proof that the CLI output,
JSON contracts, and documentation are still aligned.

These examples are linked from the README and should stay current before each
release.

## Canonical examples

| File | Purpose |
| --- | --- |
| `examples/analyze/analyze.txt` | High-level repository overview |
| `examples/inspect/inspect.txt` | Fast inspect text report |
| `examples/inspect/inspect.v1.json` | `inspect.v1` integration contract |
| `examples/doctor/doctor.txt` | Doctor/readiness text report |
| `examples/doctor/doctor.v1.json` | `doctor.v1` JSON contract |
| `examples/repoaware/review.md` | RepoAware review example |

## Check examples

```bash
scripts/check-generated-examples.sh
```

This validates:

- required example files exist and are non-empty
- JSON examples parse as valid JSON
- `inspect.v1` schema field is present and correct
- `doctor.v1` schema field is present and correct
- key README/docs links exist
- current CLI can still generate inspect, analyze, and doctor output

## Regenerate examples

```bash
scripts/generate-examples.sh
```

Then review the diff:

```bash
git diff -- examples docs README.md ROADMAP.md CHANGELOG.md
```

## Strict comparison

After regenerating examples on a clean tree, run:

```bash
scripts/check-generated-examples.sh --strict
```

Strict mode compares selected generated output with committed examples.

Use strict mode carefully — some report fields change with Git state,
version bumps, or local repository state.

## Release checklist

Before release:

```bash
scripts/generate-examples.sh
scripts/check-generated-examples.sh
python3 -m pytest -q
repo-signal inspect --json . | python3 -m json.tool
repo-signal publish-checklist . --fail-under 16
```

## Rule

If README links to an example, that example must be present, parseable, and
covered by `scripts/check-generated-examples.sh`.
