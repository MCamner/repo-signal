# repo-signal in the mq ecosystem

repo-signal is the shared repo intelligence layer for the mq ecosystem.

It turns local repository state into structured JSON contracts that all mq tools
can depend on without parsing terminal text.

---

## Architecture

```text
local repository
      ↓
repo-signal inspect --json .   →  inspect.v1
repo-signal doctor --json .    →  doctor.v1
      ↓
mqlaunch / mq-agent / mq-mcp / mq-hal
      ↓
release decisions / improvement plans / AI context
```

---

## Consumers

| Tool | How it uses repo-signal |
|---|---|
| `mqlaunch` | Menu system, repo picker, status display |
| `mq-agent` | Repo scoring, audit agent, semantic memory |
| `mq-mcp` | MCP tool exposing `inspect.v1` to Bridget and other clients |
| `mq-hal` | Repo health context injected into AI reasoning pipelines |

---

## Integration rule

Every consumer must:

1. Call `repo-signal inspect --json .` or `repo-signal doctor --json .`
2. Check the `schema` field before parsing any other field
3. Fail safely if the schema is unknown or repo-signal is missing

```bash
# Safe call pattern
repo-signal inspect --json . 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)
if d.get('schema') != 'inspect.v1':
    sys.exit(1)
print(d['repo']['name'])
"
```

---

## Troubleshooting

### repo-signal not found

```bash
which repo-signal || echo "not in PATH"
```

Fix:

```bash
pipx install repo-signal
# or
pip install repo-signal
```

### repo-signal returns non-JSON

repo-signal exits non-zero on errors and may write to stderr, not stdout.
Always redirect stderr and check the exit code:

```bash
if output=$(repo-signal inspect --json . 2>/dev/null); then
  echo "$output" | python3 -m json.tool
else
  echo "repo-signal failed"
fi
```

### Unknown schema version

```python
data = json.loads(output)
schema = data.get("schema", "unknown")
if schema not in ("inspect.v1", "doctor.v1"):
    raise ValueError(f"Unknown schema: {schema!r} — upgrade repo-signal")
```

---

## CI/readiness gate example

Use repo-signal as a publish-readiness gate in CI:

```yaml
# .github/workflows/readiness.yml
- name: Repo readiness check
  run: |
    pip install repo-signal
    repo-signal publish-checklist . --fail-under 14
```

Or as a JSON gate:

```bash
score=$(repo-signal inspect --json . | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d['public_readiness']['score'])
")
if [[ "$score" -lt 14 ]]; then
  echo "Readiness score $score/16 — below threshold"
  exit 1
fi
```

---

## Full field references

- [INSPECT_SCHEMA.md](INSPECT_SCHEMA.md) — `inspect.v1` field reference
- [DOCTOR_SCHEMA.md](DOCTOR_SCHEMA.md) — `doctor.v1` field reference
- [INTEGRATIONS.md](INTEGRATIONS.md) — consumer code examples
