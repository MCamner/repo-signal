---
name: scoring-contract-maintainer
description: Maintain repo-signal scoring rules, weights, thresholds and missing-data semantics. Use for "poängen blev fel", "ändra readiness-gränsen", or scoring changes that affect doctor/report results and downstream consumers; exclude presentation-only edits and symbolic exports.
---

# Scoring Contract Maintainer

repo-signal owns repository signals and scoring. mq-agent owns orchestration
and stack release decisions. Do not move scoring rules into consumers or lower
a threshold merely to make a release pass.

## Ground the change

Locate the rule and its callers before editing. Start with
`repo_signal/readme_score.py` for README scoring and `repo_signal/doctor.py`
for doctor/release-maturity scores; follow the affected report/CLI path and
its current schema. Use CodeGraph first when the repo is indexed.

Capture the input fixture, current score, denominator, component checks and
status. Distinguish a missing input from an observed failure using the actual
contract: do not silently replace unknown values with zero or change existing
missing-input behavior without declaring the compatibility impact.

## Change and verification

- Write a regression test that reproduces the incorrect score before fixing it.
  For an intentional rule change, record the expected old/new behavior first.
- Exercise values just below, at and above changed thresholds, plus relevant
  empty/missing inputs. Test weights or denominator changes with independently
  calculated expected values rather than calling the implementation as oracle.
- Keep component explanations, totals and human/JSON statuses consistent.
  Preserve public keys and meanings unless an explicit compatibility change
  includes consumer tests and migration guidance.
- Run the affected tests and CLI contract tests using the repo's configured
  environment. Inspect actual JSON output for the changed scenario.
- Identify downstream callers in mq-agent/mq-mcp when public scoring semantics
  change. Coordinate shared-schema changes through the canonical owner and
  the existing contract migration workflow, rather than editing vendored copies.
- Update scoring documentation/examples when results or meanings change.

Report the fixture, before/after result, compatibility impact and checks run.
Scoring indicates repository signals; it is not evidence that tests passed,
that a security review happened, or that a release was authorized.

## Routing examples

- "README score counts a missing section" → use this skill.
- "Change the readiness threshold" → use this skill.
- "Restyle terminal output" → terminal-ui-polisher.
- "Add a callgraph export field" → symbolic-intelligence-exporter.
