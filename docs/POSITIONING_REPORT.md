# Positioning Report

`repo-signal positioning` analyzes a repository front door and turns it into a
small product-positioning report.

It answers:

- What is this project?
- Who is it for?
- What problem does it solve?
- What is the strongest README angle?
- What is unclear?
- What should the repo say in one sentence?

## Usage

```bash
repo-signal positioning .
repo-signal positioning . --json
repo-signal positioning . --format json
```

## Output

Text output is meant for humans and README cleanup.

JSON output uses:

```json
{
  "schema": "positioning.v1"
}
```

The report is deterministic and local. It reads repository files and does not
call an AI provider.

## How To Use It

Run it before README or release work:

```bash
repo-signal positioning .
repo-signal publish-checklist .
repo-signal readme-score .
```

Use the `one_sentence` field as a candidate README pitch, and use
`what_is_unclear` as the next edit list.
