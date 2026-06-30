# Decision Trail Specialist Dry Run v0

Status: docs/review fixture
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR93 Decision Trail Specialist Dry Run v0

## Purpose

PR93 runs a conservative dry run over the Decision Trail specialist lane before
any full specialist-review batch is allowed.

The question is:

```text
Does the Decision Trail specialist setup resist obvious over-inference and
overtrust traps before it tries to fill messy interpretation fields?
```

This is not a product proof. It is a discipline check.

Machine-readable output:

```text
reviews/codex-assisted/decision-trail-specialist-dry-run-v0/review.json
```

## Inputs

PR93 uses only checked-in-safe artifacts:

- [Decision Trail Specialist Contracts v0](decision-trail-specialist-contracts-v0.md)
- [Decision Trail Specialist Packet Builder v0](decision-trail-specialist-packet-builder-v0.md)
- [PR91 packet fixture](../../reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json)
- [Decision Trail Specialist Trap Set v0](decision-trail-specialist-trap-set-v0.md)
- [Decision Trail Specialist Trap Set JSON v0](decision-trail-specialist-trap-set-v0.json)

It does not read raw transcripts, raw revised answers, raw memos, provider
text, private ledgers, or local private archive payloads.

## Boundary

PR93 is Codex-assisted provisional review. It is not human review, ground
truth, judge calibration data, product proof, answer-quality scoring,
automatic labeling, runtime integration, or agent approval.

This slice did not run `$lolla`, invoke the Lolla skill, call providers,
mutate archives, change prompts, touch `SKILL.md`, touch `scripts/skill/*`,
change runtime behavior, launch Observatory, persist revised answers, add a
judge, add a score, create automatic labels, or authorize agent action.

The output preserves:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls: 0`
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`

## Method

PR93 has two parts.

First, the trap discipline dry run checks all ten PR92 trap families. It asks
whether a future specialist setup should block, downgrade, preserve missingness,
or ask for local-private context instead of inventing confidence.

Second, the packet-surface dry run inspects the two PR91 checked-in-safe packet
targets:

- `structured_fixture_report`
- `sparse_missing_fixture_report`

This dry run does not fill specialist fields. It records whether each PR90 role
looks ready for a future bounded read, blocked by checked-in-safe thinness, or
only useful for preserving gaps.

## Trap Discipline Result

| discipline result | count |
|---|---:|
| `met_expected_behavior` | 7 |
| `partly_met_expected_behavior` | 3 |
| `missed_expected_behavior` | 0 |
| `inconclusive` | 0 |

The three partial trap results are useful warnings:

- `option_status_collapse`: the setup preserves option uncertainty, but safe
  fixtures still cannot tell whether an option was user-rejected or system-lost.
- `assistant_influence_not_visible`: the setup can mark assistant influence as
  private/context-needed, but checked-in-safe summaries cannot test detection.
- `local_private_needed_not_available`: the setup preserves private-needed
  status. PR95 now implements local-private packet mode, but PR93 did not test
  whether those local-private packets are usable for specialist outputs.

This means the trap surface is useful, but the safe-fixture mode remains too
thin for the full answer-plus-process product.

## Packet-Surface Result

The PR91 packet fixture contains two report targets and all four PR90 role
packets for each target.

The structured fixture is partially useful: it has populated custody fields and
some structural-delta material, but all load-bearing messy interpretation
fields still need bounded interpretation or private context.

The sparse fixture is mainly a diagnostic shell: it demonstrates missingness
and non-claims, but should not be used to fill likely actions, option status,
assistant influence, useful/noisy friction, or lost value.

## Strongest Useful Signal

The strongest useful signal is that the dry run does not make the PR91 packets
look more impressive than they are.

It preserves:

- `safe_fixture_only`
- `source_report_not_checked_in`
- `local_private_shadow_review:not_run`
- `requires_llm_interpretation_sections:8`
- overtrust risk around `structural_delta`

That is exactly the custody discipline this lane needs.

## Strongest Remaining Risk

The strongest remaining risk is that the dry run is still performed over
checked-in-safe fixture surfaces, not full local-private conversation context.

It can test discipline against traps. It cannot prove that future specialists
will correctly interpret real messy conversations.

## Non-Claims

PR93 does not claim:

- Lolla improves decisions;
- the Decision Trail report is product-ready;
- the specialist method is calibrated;
- trap expectations are human labels;
- future specialist reads will be correct;
- clean artifacts imply good advice;
- an agent may act.

## Relationship To PR94

PR94 makes the path decision after this dry run:

[`Decision Trail Specialist Path Decision v0`](decision-trail-specialist-path-decision-v0.md)

It selects local-private packet mode as the next slice and rejects a broader
checked-in-safe specialist batch for now.

## Relationship To PR95

PR95 implements the selected local-private packet mode:

[`Decision Trail Local-Private Packet Mode v0`](decision-trail-local-private-packet-mode-v0.md)

It keeps checked-in-safe packets as the default, but adds explicit local-only
packets for operator-selected completed run directories.

## Next Step

The next conservative move is a local-private packet smoke/review step before
any contract-conforming specialist output batch.

It should not jump straight to runtime integration, broad case expansion,
scoring, judging, or product-proof claims.
