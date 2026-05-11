# Publish Checklist Examples

These examples show `repo-signal publish-checklist` running against real local
repositories.

The goal is to make repository quality visible:

- front-door clarity
- README quality
- release readiness
- GitHub Pages readiness
- docs/screenshots/roadmap coverage
- issue template coverage
- safe sharing/security notes

## Examples

| Repo | Output |
| --- | --- |
| repo-signal | [repo-signal.txt](repo-signal.txt) |
| Design-Prototype | [Design-Prototype.txt](Design-Prototype.txt) |
| macos-scripts | [macos-scripts.txt](macos-scripts.txt) |
| mcamner-journal | [mcamner-journal.txt](mcamner-journal.txt) |

Note: `Design-Prototype.txt` shows the missing-path behavior because that
repository was not available in the local workspace when these examples were
generated.

## Usage

```bash
repo-signal publish-checklist .
repo-signal publish-checklist ~/Design-Prototype
repo-signal publish-checklist ~/macos-scripts
```

## Why This Matters

The checklist turns vague repo polish work into a clear next action.

Instead of asking:

> Is this repo ready?

You get:

> Here is what is missing, and here is the next fix.
