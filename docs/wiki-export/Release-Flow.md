# Release Flow

## Recommended Release Check

```bash
git status --short
python3 -m pytest -q
repo-signal publish-checklist .
repo-signal publish-checklist . --format json
```

## Release Notes

Keep release notes short, public-facing, and focused on user-visible change.
