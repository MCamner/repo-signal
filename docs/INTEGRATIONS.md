# Integrations

This document shows how external tools should consume repo-signal's stable JSON
contracts.

---

## Stable JSON contracts

| Command | Schema | Purpose |
| --- | --- | --- |
| `repo-signal inspect --json` | `inspect.v1` | Fast repo status for tools and menus |
| `repo-signal doctor --json` | `doctor.v1` | Deeper readiness, docs, release, and AI-readiness diagnosis |
| `repo-signal report --format json` | `report.v1` | Unified report artifact for CI and assistant workflows |
| `repo-signal suggest --format json` | `suggest.v1` | Read-only improvement suggestions with no repository mutation |

Every consumer must check `schema` before reading fields. If the schema is
unknown, fail safely instead of parsing terminal text.

---

## Inspect integration

Always use the JSON output, not the terminal text:

```bash
repo-signal inspect --json
repo-signal inspect --json ~/some-repo
```

The first field to check is `schema`:

```json
{
  "schema": "inspect.v1"
}
```

If `schema` is not `"inspect.v1"`, treat the output as unknown and fail safely.

Full field reference: [INSPECT_SCHEMA.md](INSPECT_SCHEMA.md)

---

## Doctor integration

Use `doctor.v1` when a tool needs broader readiness context:

```bash
repo-signal doctor --json
repo-signal doctor . --format json
```

Safe consumption pattern:

```python
import json
import subprocess

def repo_doctor_json(path: str = ".") -> dict | None:
    result = subprocess.run(
        ["repo-signal", "doctor", "--json", path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "doctor.v1":
        return None
    return data
```

Useful fields:

- `scores.repo_health`
- `scores.release_maturity`
- `scores.docs_quality`
- `scores.ai_readiness`
- `repoaware_context.summary`
- `suggested_priorities`
- `suggested_skills`

Full field reference: [DOCTOR_SCHEMA.md](DOCTOR_SCHEMA.md)

---

## Report integration

Use `report.v1` when a CI job or assistant needs one combined artifact:

```bash
repo-signal report . --format json
```

Safe consumption pattern:

```python
import json
import subprocess

def repo_report_json(path: str = ".") -> dict | None:
    result = subprocess.run(
        ["repo-signal", "report", path, "--format", "json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "report.v1":
        return None
    return data
```

Useful fields:

- `repo`
- `git`
- `public_readiness`
- `issues`
- `recommended_next_commit`
- `sections`

Full field reference: [REPORT_SCHEMA.md](REPORT_SCHEMA.md)

---

## Suggest integration

Use `suggest.v1` when a tool needs next-step improvement suggestions without
letting repo-signal mutate files:

```bash
repo-signal suggest . --format json
```

Safe consumption pattern:

```python
import json
import subprocess

def repo_suggest_json(path: str = ".") -> dict | None:
    result = subprocess.run(
        ["repo-signal", "suggest", path, "--format", "json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "suggest.v1":
        return None
    return data
```

Useful fields:

- `suggestions`
- `suggestions[].risk`
- `suggestions[].commit_group`
- `suggestions[].diff_preview`
- `no_mutation_guarantee`

Full field reference: [SUGGEST_SCHEMA.md](SUGGEST_SCHEMA.md)

---

## mqlaunch

`mqlaunch` uses `inspect.v1` to show live repo status in the menu system and
to drive smart repo-picker actions.

### Shell function pattern

```bash
_inspect_json() {
  local repo="${1:-.}"
  repo-signal inspect --json "$repo" 2>/dev/null
}

_repo_name() {
  _inspect_json "$1" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('schema') != 'inspect.v1':
    sys.exit(1)
print(d['repo']['name'])
"
}

_repo_status() {
  _inspect_json "$1" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('schema') != 'inspect.v1':
    sys.exit(1)
score = d['public_readiness']['score']
total = d['public_readiness']['total']
branch = d['git']['branch']
clean = 'clean' if d['git']['clean'] else 'dirty'
print(f'{score}/{total}  {branch}  {clean}')
"
}
```

### fzf repo picker integration

```bash
run_repo_status_picker() {
  local repo
  repo=$(gh repo list --json name,url --jq '.[].name' | fzf --prompt "Repo > ")
  [ -z "$repo" ] && return

  local clone_path="$HOME/repos/$repo"
  if [ -d "$clone_path" ]; then
    repo-signal inspect --json "$clone_path" | python3 -m json.tool
  else
    echo "Not cloned: $clone_path"
  fi
}
```

---

## mq-mcp (Bridget / MCP tools)

`mq-mcp` exposes `inspect.v1` as an MCP tool so Bridget and other MCP clients
can query live repo status.

### MCP tool definition

```python
@mcp.tool()
def repo_inspect(repo_path: str = ".") -> dict:
    """Return inspect.v1 status for the given repository path."""
    import subprocess, json
    result = subprocess.run(
        ["repo-signal", "inspect", "--json", repo_path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "invalid JSON from repo-signal"}
    if data.get("schema") != "inspect.v1":
        return {"error": f"unknown schema: {data.get('schema')}"}
    return data
```

### Bridget usage example

When Bridget asks about repo status, the MCP tool returns the full `inspect.v1`
payload. Bridget should surface:

- `repo.name` — repo name
- `git.branch` + `git.clean` — current branch, working tree state
- `public_readiness.summary` — publish score
- `issues` — list of detected problems
- `recommended_next_commit` — what to do next

---

## mq-hal

`mq-hal` uses `inspect.v1` to drive repo-status commands and to populate
the repo health context sent to AI reasoning pipelines.

### doctor_commands pattern

```python
def doctor_commands(repo_path: str = ".") -> dict:
    import subprocess, json
    result = subprocess.run(
        ["repo-signal", "inspect", "--json", repo_path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    data = json.loads(result.stdout)
    if data.get("schema") != "inspect.v1":
        return {"error": f"unexpected schema: {data.get('schema')}"}
    return {
        "repo": data["repo"]["name"],
        "branch": data["git"]["branch"],
        "clean": data["git"]["clean"],
        "score": data["public_readiness"]["score"],
        "issues": data["issues"],
        "next": data["recommended_next_commit"],
        "next_commands": data["useful_next_commands"],
    }
```

### Prompt context injection

When injecting repo context into a prompt:

```python
def repo_context_block(repo_path: str = ".") -> str:
    status = doctor_commands(repo_path)
    if "error" in status:
        return f"[repo-signal error: {status['error']}]"
    lines = [
        f"repo: {status['repo']}",
        f"branch: {status['branch']} ({'clean' if status['clean'] else 'dirty'})",
        f"publish score: {status['score']}/16",
    ]
    if status["issues"]:
        lines.append("issues: " + ", ".join(i.get("label", str(i)) for i in status["issues"]))
    lines.append(f"next: {status['next']}")
    return "\n".join(lines)
```

---

## mq-agent

`mq-agent` uses `inspect.v1` for repo scoring, `doctor.v1` for semantic memory
context, `report.v1` for combined review artifacts, and `suggest.v1` for safe
improvement planning.

### Repo score command

```bash
mq-agent score .
```

Internally calls `repo-signal inspect --json .` and reads `public_readiness.score`.

### Semantic memory

```bash
mq-agent memory status
mq-agent memory build .
mq-agent memory refresh . --approve
```

Uses `repo-signal semantic-upload` to push repository context to a vector store.

### Safe consumption in mq-agent

```python
import subprocess, json

def repo_inspect_json(path: str = ".") -> dict | None:
    result = subprocess.run(
        ["repo-signal", "inspect", "--json", path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if data.get("schema") != "inspect.v1":
        return None
    return data
```

---

## Validation rule

Every consumer must check `schema` before using any fields:

```python
data = json.loads(output)
if data.get("schema") != "inspect.v1":
    raise ValueError(f"Unexpected schema: {data.get('schema')!r}")
```

This ensures consumers fail safely when `repo-signal` is missing, outdated,
or returns an error message instead of JSON.

---

## Inspect fields at a glance

| Field                          | Type    | Use                                  |
| ------------------------------ | ------- | ------------------------------------ |
| `schema`                       | string  | Always check first — must be `inspect.v1` |
| `repo.name`                    | string  | Display name                         |
| `repo.type`                    | string  | Project type label                   |
| `git.branch`                   | string  | Current branch                       |
| `git.clean`                    | boolean | True if working tree is clean        |
| `git.change_count`             | int     | Number of working tree changes       |
| `public_readiness.score`       | int     | Publish score (0–16)                 |
| `public_readiness.summary`     | string  | Human-readable score summary         |
| `issues`                       | array   | Detected problems                    |
| `recommended_next_commit`      | string  | Next action suggestion               |
| `useful_next_commands`         | array   | Suggested follow-up CLI commands     |
| `detected.languages`           | object  | Language → file count map            |
| `detected.tooling`             | array   | Detected tools/frameworks            |

Full schema: [INSPECT_SCHEMA.md](INSPECT_SCHEMA.md)
