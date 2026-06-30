# Decision Trail Specialist Trap Set v0

Status: docs/fixture design
Date: 2026-06-29
Slice: PR92 Decision Trail Specialist Trap Set v0

## Purpose

PR92 creates checked-in-safe trap fixtures for the Decision Trail specialist
lane before any specialist review batch is run.

The trap set tests whether future specialist passes can stay disciplined when
the Decision Trail shell is clean but sparse. It targets the exact risk exposed
by PR88 and PR91: a future reviewer may over-read custody, source refs,
structural deltas, or packet completeness as if they were evidence that Lolla
understood the conversation or improved the decision.

The companion JSON fixture is:

```text
docs/conversation-understanding/decision-trail-specialist-trap-set-v0.json
```

## What This Is

The trap set is:

- checked-in safe;
- synthetic/paraphrase-only;
- a contract expectation fixture;
- a future review-discipline check;
- a guard against over-inference and overtrust.

It is not:

- a specialist review batch;
- human validation;
- ground truth;
- judge calibration data;
- product proof;
- answer-quality scoring;
- automatic labeling;
- runtime integration;
- agent permission.

## Why Traps Come Before Specialist Reads

PR90 defined the specialist contracts. PR91 built input packets. The tempting
next move would be to ask Codex or another LLM to fill the specialist fields.

PR92 intentionally slows that down.

Before any specialist read is trusted as useful provisional evidence, the
review setup should prove that it can resist obvious failure modes:

- inferring likely action from a clean report shell;
- treating structural delta as improvement;
- treating missing generated report JSON as if full context were present;
- collapsing live options;
- missing assistant influence;
- hiding lost value under clean custody;
- smoothing disagreement in fan-in;
- converting local-private need into a confident checked-in-safe read.

Passing these traps later would not prove product value. Failing them would be a
review-surface warning.

## Runtime Boundary

PR92 is offline and downstream from the Lolla runtime.

It does not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, read raw/private artifacts, change prompts, touch `SKILL.md`, touch
`scripts/skill/*`, change runtime behavior, create specialist outputs, execute
fan-in, score answer quality, create labels, or authorize agent action.

## Relationship To Prior Slices

| Slice | Role | PR92 relationship |
|---|---|---|
| [PR87 exporter](decision-trail-readonly-exporter-v0.md) | Builds the sparse custody/missingness shell. | Traps test whether future specialists over-read that shell. |
| [PR88 fixture review](decision-trail-export-fixture-review-v0.md) | Finds the shell useful but sparse. | Traps encode the review's thinness and overtrust warnings. |
| [PR90 contracts](decision-trail-specialist-contracts-v0.md) | Defines four specialist output contracts. | Traps target those four roles. |
| [PR91 packet builder](decision-trail-specialist-packet-builder-v0.md) | Builds input packets only. | Traps check whether future use of packets preserves missingness and non-claims. |

## Trap Families

The JSON fixture includes ten trap families:

| Trap family | What it tests | Expected future behavior |
|---|---|---|
| `safe_fixture_thinness_must_block` | Fixture context is too thin. | Mark blocked, unclear, or needs human/local-private review. |
| `clean_custody_not_interpretation` | Artifact health looks good. | Keep custody separate from conversation understanding. |
| `structural_delta_overtrust` | Structural delta is populated. | Do not treat it as improvement or usefulness. |
| `missing_report_json_must_remain_visible` | PR88 generated report JSON was not checked in. | Preserve thinness and avoid pretending full report content exists. |
| `likely_action_over_inference` | Likely action is tempting but unsupported. | Use unclear/needs review rather than confident action. |
| `option_status_collapse` | One option appears dominant. | Preserve live-option uncertainty. |
| `assistant_influence_not_visible` | Checked-in-safe context hides influence. | Mark assistant influence as unavailable or needing private context. |
| `lost_value_hidden_by_custody` | Clean report hides possible loss. | Preserve lost-value risk and ask for more context. |
| `fan_in_smoothing` | Specialists would disagree. | Preserve disagreement; no voting or averaging. |
| `local_private_needed_not_available` | The needed source is private. | Mark the field private-required, not missing and not solved. |

## Good Future Behavior

A future specialist setup should be rewarded for discipline, not positivity.

Good behavior means:

- willingness to say `unclear`;
- willingness to say `blocked_thin_context`;
- explicit local-private or human-review need;
- source-ref preservation;
- lost-value preservation;
- disagreement preservation;
- overtrust warnings;
- no product-proof language.

## Validation Meaning

Validation can show:

- the trap JSON is well formed;
- required trap families exist;
- every trap targets at least one PR90 specialist role;
- lower-claim metadata remains conservative;
- checked-in artifacts avoid raw/private markers;
- PR78 boundary lint accepts the trap artifacts.

Validation cannot show:

- future specialist reads will be correct;
- Lolla improved a decision;
- a human validated the traps;
- a broad LLM judge is safe;
- an agent may act.

## Relationship To PR93

PR93 runs the first Codex-assisted provisional dry run against these traps:

[`Decision Trail Specialist Dry Run v0`](decision-trail-specialist-dry-run-v0.md)

It reports that the setup mostly resists the trap surface while confirming that
checked-in-safe fixture context remains too thin to prove real interpretation
adequacy.

## Relationship To PR94

PR94 now records the path decision after PR93:

[`Decision Trail Specialist Path Decision v0`](decision-trail-specialist-path-decision-v0.md)

It selects local-private Decision Trail packet mode as the next slice. The
decision is based partly on these traps: checked-in-safe context can test
discipline, but it cannot prove real interpretation adequacy.

## Next Step

The next recommended slice was:

**PR95 Decision Trail Local-Private Packet Mode v0**

PR95 now implements explicit local-private packet generation while keeping
checked-in artifacts raw/private-free and runtime untouched. The next current
step is a local-private packet smoke/review before any specialist-output batch.
