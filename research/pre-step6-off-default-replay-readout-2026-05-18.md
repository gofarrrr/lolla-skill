# Pre-Step-6 Off-Default Replay Readout

Date: 2026-05-18

Status: research-only replay gate. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-replay-records/third-year-phd-student.conflict.off-default-replay.v1.json
research/pre-step6-source-overclaim-audits/third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-semi-blind-comparisons/third-year-phd-student.conflict.semi-blind-comparison.v1.json
scripts/research/pre_step6_replay_ledger.py
tests/test_pre_step6_replay_ledger.py
```

## Question

After the semi-blind PhD comparison, can a rendered-hybrid win count only when
it survives a source/overclaim audit?

This slice does not solve live generation. It is a static off-default replay
record:

```text
load archived artifacts
load existing rendered hybrid handoff
load existing Step-6-style answer core
load semi-blind comparison
run source/overclaim audit on the rendered winner
record failure modes and naturalness debt
```

## Why This Exists

The semi-blind comparison was useful but not enough.

Rendered hybrid won aggregate judgment, but raw-only tied it on simple criterion
count and beat it on:

```text
overclaim risk
machinery/procedural feel
unforcedness
```

So the replay gate adds a sharper rule:

```text
a rendered-hybrid replay win counts only if source/overclaim audit passes
```

This prevents the handoff from winning merely because it is tidy, structured, or
persuasive.

## What Was Added

Two research-only schemas:

```text
pre_step6_source_overclaim_audit.v1
pre_step6_replay_record.v1
```

The source/overclaim audit checks:

```text
source grounding
probability overclaim
evidence-gate integrity
unsupported option expansion
naturalness debt
```

The replay record checks:

```text
archived refs exist and validate
semi-blind comparison still resolves to rendered_hybrid_wins
source/overclaim audit is recorded
source/overclaim audit passes when the replay decision is pass_to_next_replay
runtime wiring remains false
product promotion remains false
high naturalness debt blocks pass_to_next_replay
```

2026-05-18 cleanup: this surface should be called a replay ledger, not a strong
replay harness. It records and validates off-default replay evidence. It does
not generate answer variants.

The cleanup also makes failure evidence first-class:

```text
source_overclaim_audit_recorded: required true
source_overclaim_audit_passed: conditional
```

`pass_to_next_replay` requires the audit pass. `retest` and `stop` can record a
failed audit cleanly. The ledger also checks cross-ref custody between the
replay record, source/overclaim audit, and semi-blind comparison so refs cannot
quietly drift.

## Audit Result

The native source/overclaim auditor returned:

```text
audit_result: pass
decision: counts_as_replay_win
naturalness_debt_level: medium
```

Passes:

```text
source grounding
probability overclaim
evidence-gate integrity
unsupported option expansion
```

Watch:

```text
naturalness debt
```

No overclaim findings were recorded.

The audit did not find the answer laundering weak evidence into authority. It
stayed within the source constraints:

```text
three-month deadline
advisor retirement horizon
lab lacks single-cell experience
Silva/data access is the binding constraint
advisor-first sequencing
fallback may stop being executable
base-rate claims stay qualitative
no new dissertation options
```

## Naturalness Debt

The residual problem is style and cognitive feel.

The auditor marked medium naturalness debt because the rendered answer uses
terms like:

```text
identity-coherent
executability gates
stop-loss date
```

These terms are not materially wrong, but they make the answer feel more
engineered than raw-only. This matches the semi-blind comparison, where raw-only
won unforcedness and machinery/procedural feel.

This is now a first-class replay risk:

```text
rendered hybrid can win on structure while accumulating naturalness debt
```

## Result

Pass to next replay.

Not promotion.

The current replay record is:

```text
comparison_decision: rendered_hybrid_wins
replay_decision: pass_to_next_replay
product_promotion: blocked
naturalness_debt: medium
```

That means the rendered PhD conflict answer may count as a replay win because it
passed source/overclaim audit. It does not mean the surface is ready for runtime
or product docs.

## Decision

```text
first_static_replay_record_passes
source_overclaim_audit_required_for_rendered_winners
medium_naturalness_debt_is_watch_not_blocker
high_naturalness_debt_blocks_replay_win
runtime_wiring_still_blocked
product_promotion_still_blocked
bundle_still_not_earned
workers_still_not_earned
```

## Next Gate

Run the same off-default replay gate on at least two more shapes:

```text
mother quiet sentinel
founder high-clutter demotion
```

The mother replay should be hostile to overuse:

```text
rendered hybrid should not win by adding structure
quiet mode should tie or improve by staying smaller and safer
naturalness debt should be low
```

The founder replay should test whether quiet receipts help without creating a
private mini-index:

```text
duplicate/misfit receipts stay quiet
dependency pressure survives
exit math remains false-precision caution
answer does not bloat
naturalness debt does not rise
```

Only after multiple replay records pass source/overclaim audit should we discuss
whether a real replay generator is worth building. Live `/lolla` remains out of
scope.
