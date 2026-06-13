# Skills

repo-signal ships local skills for maintaining static repository analysis,
symbolic intelligence exports, semantic memory, docs, terminal UX and release
readiness.

The table below is generated from SKILL.md frontmatter by
`./scripts/check-skills.sh --fix`. Do not edit it by hand.

`skills/platform-skills.md` maps these local skills to OpenAI Platform skill
IDs; it is not a skill itself.

## Built-in skills

<!-- BEGIN GENERATED SKILLS TABLE -->
| Skill | Description |
| ----- | ----------- |
| [docs-maintainer](skills/docs-maintainer/SKILL.md) | Use when keeping repository documentation consistent after code, CLI, release, workflow, README, wiki, or GitHub Pages changes. Helps update docs surfaces without inventing behavior. |
| [release-readiness](skills/release-readiness/SKILL.md) | Use when preparing a repo release, checking tests, docs, versioning, changelog, Git status, and publish readiness. |
| [repo-aware](skills/repo-aware/SKILL.md) | Use when working inside a repo and needing repo-specific context from docs, tooling, tests, git state, repo-signal reports, and local conventions before acting. |
| [repo-product-auditor](skills/repo-product-auditor/SKILL.md) | Review GitHub repositories as products. Use when asked to improve a repo, README, GitHub profile, pinned repo strategy, discovery, case page, product positioning, or launch readiness. |
| [semantic-memory-maintainer](skills/semantic-memory-maintainer/SKILL.md) | Use when maintaining OpenAI vector stores, semantic repository memory, knowledge packs, indexed markdown, file_search sources, or repo memory freshness across projects. |
| [symbolic-intelligence-exporter](skills/symbolic-intelligence-exporter/SKILL.md) | Use when adding or changing repo-signal symbolic exports such as symbol_index.json, callgraph.json, repo_summary.json, risk_map.json, semantic packs, or schemas consumed by mq-mcp and mq-agent. |
| [terminal-ui-polisher](skills/terminal-ui-polisher/SKILL.md) | Improve terminal, CLI, TUI, ASCII, ANSI, and command-surface interfaces with focus on clarity, hierarchy, keyboard flow, spacing, status feedback, and product-level polish. |
<!-- END GENERATED SKILLS TABLE -->
