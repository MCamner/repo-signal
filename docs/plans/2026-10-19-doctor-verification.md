# Doctor verification evidence implementation plan

Owner: repo-signal. mq-agent owns execution and receipt validation; repo-signal only consumes a bounded read-only CLI response. Durable learning belongs to mqobsidian/mq-mcp.

1. Add failing tests for default NOT_VERIFIED, opt-in delegation, stale/failing/partial evidence, malformed/unavailable providers, and CLI compatibility.
2. Add an additive doctor.v1 verification object, opt-in --verification flag, explicit structural-score wording and fixed, safe next actions.
3. Keep subprocess use shell-free, bounded by timeout, with no raw provider output in exported reports. No implicit tests, cloud calls, writes or score changes.
4. Update schema documentation, command reference, examples, changelog and agent-facing guidance where relevant.
5. Run focused and full existing tests, docs checks, public-safe diff scan; record an evidence-backed learning after validation.

Acceptance: current PASS/FAIL/STALE preserved; absent/partial/invalid evidence never PASS; both output formats distinguish structure from verification; old callers retain defaults and scores.

Rollback: revert the additive feature. Commit/push/merge are outside this implementation request.
