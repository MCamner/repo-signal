# repo-signal 0.2.0 Roadmap

Goal: make repo-signal feel like a stable, reusable CLI for repository analysis,
publish readiness, and AI-assisted repo context.

## Definition of Done

- [ ] Tests pass on Python 3.11 and 3.12
- [ ] CI is green
- [ ] GitHub Pages deploys successfully
- [ ] publish-checklist remains 16/16
- [ ] semantic-upload dry-run works offline
- [ ] real semantic-upload requires vector store configuration
- [ ] command reference is clean and current
- [ ] README examples render cleanly
- [ ] clean-clone install path is verified
- [ ] CHANGELOG, VERSION, tag, and GitHub Release match

## Focus Areas

### 1. CLI polish

- [ ] `portfolio` missing from `--help` command list
- [ ] `portfolio check --help` returns "Unknown option" instead of usage
- [ ] `--help` exits with code 2 instead of 0
- [ ] Audit all subcommand help text for completeness
- [ ] Make command naming consistent

### 2. Command reference

- [ ] Generate or update command reference
- [ ] Link command reference from README
- [ ] Add examples for `ask`, `repoaware`, `semantic-upload`, `portfolio check`

### 3. Portfolio dashboard

- [ ] Improve `repo-signal portfolio check`
- [ ] Add Markdown output suitable for GitHub
- [ ] Add clearer recommended next actions per repo
- [ ] Add example portfolio config

### 4. Packaging readiness

- [ ] Verify install from clean clone
- [ ] Verify `pip install -e ".[ai]"`
- [ ] Check package metadata
- [ ] Decide whether PyPI is a 0.2.x or later goal

### 5. AI-assisted workflows

- [ ] Improve `ask --dry-run`
- [ ] Improve context export explainability
- [ ] Add tests for semantic memory document shape
- [ ] Keep AI optional and safe by default

## Non-goals

- No destructive auto-patching
- No mandatory OpenAI dependency
- No hidden vector-store magic
- No replacing static analysis with AI-only answers
