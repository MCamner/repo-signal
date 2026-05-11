# Platform Skills Map

This file maps local repo-signal skills to OpenAI Platform skill IDs.

## Current Platform Skills

<!-- markdownlint-disable MD013 -->
| Local skill | Platform skill ID | Default version | Latest version | Status |
| --- | --- | ---: | ---: | --- |
| `terminal-ui-polisher` | `skill_69f9225cdd94819393103714b6b64471046c9073049eb029` | 1 | 1 | Uploaded |
| `repo-product-auditor` | `skill_69f921b3e19c8191821e7bdb3d0f9e620318497fc53862bf` | 1 | 1 | Uploaded |
| `release-readiness` | `TBD` | TBD | TBD | Not uploaded / verify |
| `repo-aware` | `TBD` | TBD | TBD | Not uploaded / verify |
<!-- markdownlint-enable MD013 -->

## Local Skill Folders

Expected local folders:

- `skills/terminal-ui-polisher/`
- `skills/repo-product-auditor/`
- `skills/release-readiness/`
- `skills/repo-aware/`

## Verify Platform Skills

Run:

```bash
curl -s https://api.openai.com/v1/skills \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | jq -r '.data[] | "\(.name)\t\(.id)\tdefault=\(.default_version)\tlatest=\(.latest_version)"'
```

## Upload Missing Skills

From the repository root:

```bash
cd ~/repo-signal/skills

zip -r /tmp/release-readiness.zip release-readiness
zip -r /tmp/repo-aware.zip repo-aware
```

Then upload:

```bash
curl -X POST "https://api.openai.com/v1/skills" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "files=@/tmp/release-readiness.zip;type=application/zip"

curl -X POST "https://api.openai.com/v1/skills" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "files=@/tmp/repo-aware.zip;type=application/zip"
```

After upload, run the verify command again and replace `TBD` values in this file.

## Notes

- Do not commit API keys.
- Do not commit temporary zip bundles unless intentionally needed.
- Update this file whenever a skill is uploaded, renamed, or versioned.
