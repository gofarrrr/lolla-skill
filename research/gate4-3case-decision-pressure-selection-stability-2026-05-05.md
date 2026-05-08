# Gate 4 3-Case Decision Pressure Selection Stability

**Date:** 2026-05-05
**Status:** PR14 planning artifact plus recorded second-review result.
Docs/research-only. Not runtime evidence.

**Purpose:** Test whether a second narrow reviewer, using the same 12-route raw
packet and the same Decision Pressure gates, selects substantially the same
`1-3` pressures as PR13 or produces a gate-consistent improvement to the
selection doctrine.

**Inputs:**
- `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
- `research/gate4-3case-product-readout-2026-05-05.md`
- `research/gate4-3case-claude-code-review-2026-05-05.md`
- `research/decision-pressure-surface-spec-2026-05-05.md`
- `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/`

**Non-goals:**
- No paid model calls by default.
- No judge calls.
- No runtime behavior changes.
- No prompt, validator, or affordance-record changes.
- No Batch 3a extraction.
- No new lane.
- No second public Pressure Check.

**Doctrine line:** Surface pulls extraction. Extraction does not push the product.

## Execution Status

This artifact defines the PR14 selection-stability review. The second-review
pass has now been run and recorded in:

- `research/gate4-3case-decision-pressure-selection-stability-review-2026-05-05.md`

Reviewer result:

- Recommendation: `stable_enough_for_batch3a`
- Convergence: `3/3` pressure clusters matched PR13
- Selected clusters:
  - `grant-equity-partnership-status / risk-response`: governance deadlock
    before vesting
  - `mother-deciding-address-year / uncertainty-type`: safety plan relying on
    a gameable signal
  - `third-year-phd-student / resource-allocation`: shaping phase without a
    stop condition

Blindness caveat:

The reviewer reported that the PR13 dry-surface file was not read before first
selection. This should still be treated as a partially blinded / non-fully-
blinded review because the PR14 planning artifact itself includes the PR13
reference selection later in this file. The result is useful product evidence,
not formal measurement proof.

No paid external model, judge, live `/lolla`, runtime code, prompt, validator,
or affordance-record changes were used for this planning checkpoint.

## Product Question

PR13 is product-valid as a docs/research checkpoint, but it is not runtime
evidence. Its `better_than_raw_probes` verdict means the compressed dry surface
is more usable than raw Arm B/C probe lists in this packet. It does not mean
Decision Pressure should be promoted.

The next product uncertainty is selection stability:

> Given the same raw 12-route packet and the same gates, would another reviewer
> choose substantially the same `1-3` pressures?

If selection depends mostly on reviewer taste, the surface is not ready to pull
Batch 3a extraction or runtime work.

Execution result:

> A second narrow reviewer converged 3/3 with PR13 at the pressure-cluster
> level. This is stable enough for Batch 3a planning, but not runtime or
> user-facing promotion.

## Reviewer Instructions

The reviewer should act as a narrow product reviewer, not as a judge model and
not as a new generator. They should use only the existing artifacts.

Recommended procedure:

1. Read `research/decision-pressure-surface-spec-2026-05-05.md`, especially the
   accepted value modes, rejection modes, provenance classes, global compression
   cap, zero-output success mode, and red-team constraints.
2. Read `research/gate4-3case-product-readout-2026-05-05.md` and treat the
   12-route Arm B/C packet as the raw evidence.
3. Read `research/gate4-3case-claude-code-review-2026-05-05.md` as
   product-shaping reviewer evidence, not formal Gate 4 proof.
4. Read `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
   only after making an initial candidate inventory, or keep PR13 hidden until
   after the first selection if a blinded review is feasible.
5. Select `0-3` total Decision Pressures across the whole 3-case sample, not
   one per route.
6. For every selected pressure, state the required fields and provenance.
7. For every suppressed strong candidate, state which gate caused suppression.
8. Compare the final selection against PR13.

The reviewer must not produce new probes. They are compressing and selecting
from existing Arm B/C artifacts.

## Selection Gates

Apply these gates in order.

### 1. Coverage Gate

Reject source-backed pressure if:

- the route has no v3 records for the routed models;
- the pressure depends on a missing model record;
- Arm C generated phantom traces;
- the pressure would require pretending a missing model has reviewed support.

Allowed output:

> No substrate-backed pressure cleared this route because the required reviewed
> affordance records are missing.

### 2. Action-Delta Gate

Keep only pressures that change what the user should:

- verify;
- delay;
- test;
- document;
- monitor;
- sequence;
- dismiss;
- stop.

Better wording alone does not count.

### 3. Dismissal Gate

Every selected pressure needs a `Dismiss if` field that can be cleared by
evidence, action, or user verification.

Reject neat dismissal paths that are unsupported or invented only to make the
surface feel rigorous.

### 4. Bloat Gate

Suppress candidates that:

- require too much explanation to become useful;
- are merely more elaborate than Arm B;
- would turn the surface into a checklist;
- leak route, trace, affordance, or Arm B/C machinery.

### 5. Compression Gate

Select `0-3` total pressures across all 12 routes.

The reviewer may select zero if no pressure clears the gates. Zero-output can
be a premium result when it preserves coverage honesty.

### 6. Tone Gate

For relational or emotional material, select only pressures that are humane,
non-clinical, non-blaming, and action-clear.

Do not create case-type rules such as "relationship cases are weak" or
"business cases are strong."

## Expected Reviewer Output Format

If a second-review pass is approved, append the review result to this file or
create a sibling review artifact:

`research/gate4-3case-decision-pressure-selection-stability-review-2026-05-05.md`

Required sections:

1. Metadata and non-goals.
2. Reviewer method.
3. Candidate inventory or selection notes.
4. Selected pressures, `0-3` total.
5. Suppressed candidates and gate reasons.
6. Coverage gaps and zero-output candidates.
7. Comparison against PR13.
8. Stability verdict.
9. Recommendation for whether Batch 3a may proceed.
10. Open questions.

For each selected pressure, include:

- `Pressure`
- `What to verify`
- `Why it matters`
- `Dismiss if`
- `Tripwire or next action`
- `Coverage`
- `Provenance`
- `Source route/case`
- `Why this survived compression`
- `What was suppressed and why`

Allowed field-level provenance classes:

- `source_backed`
- `case_grounded`
- `llm_synthesized`
- `user_to_verify`

## PR13 Reference Selection

PR13 selected:

1. `grant-equity-partnership-status / risk-response`: governance deadlock before vesting.
2. `mother-deciding-address-year / uncertainty-type`: safety plan relying on a gameable signal.
3. `third-year-phd-student / resource-allocation`: shaping phase without a stop condition.

The reviewer should compare against these at the pressure-cluster level, not
only by exact wording.

Same pressure cluster means:

- same case and route, or a clearly merged adjacent route;
- same user action or verification target;
- same dismissal logic;
- same coverage status;
- same reason for surviving compression.

Different wording with the same action target counts as stable.

## Pass / Fail Criteria

### Stable Enough To Proceed To Batch 3a Planning

Selection is stable enough if either:

- the second reviewer selects at least `2` of the same `3` PR13 pressure
  clusters; or
- the second reviewer selects different pressures for stable, gate-consistent
  reasons that improve the doctrine.

Stable different-selection reasons may include:

- a PR13 pressure fails a gate that PR13 underweighted;
- another candidate has a clearer action delta and dismissal path;
- compression should merge two PR13 pressures differently;
- a zero-output decision is more honest than PR13's selected pressure.

If this happens, PR14 should specify exactly how doctrine should change before
Batch 3a extraction begins.

### Unstable / Downgrade Signal

Selection is unstable if:

- selections vary wildly across routes;
- the reviewer cannot apply the gates consistently;
- choices depend on taste, case familiarity, or rhetorical appeal;
- coverage gaps are ignored to preserve a nice surface;
- dismissal paths are invented;
- compression becomes "one per route" or a broad checklist;
- the reviewer prefers raw probes because compression loses too much signal.

Unstable selection should downgrade or revise Decision Pressure before any
Batch 3a extraction.

## Comparison Method

Use a simple comparison table:

| PR13 pressure | Reviewer pressure | Same cluster? | Gate agreement | Notes |
| --- | --- | --- | --- | --- |

Then classify:

- `stable_same`: same pressure cluster and same gate rationale.
- `stable_variant`: different wording or merged route, same action target and
  gate rationale.
- `doctrine_improving_difference`: different selection that identifies a better
  stable gate rule.
- `unstable_difference`: different selection due to taste, bloat, coverage
  leakage, or unclear action delta.

## Batch 3a Sequencing Rule

Batch 3a remains conditional.

Proceed toward targeted Batch 3a only if PR14 finds selection stability or a
doctrine-improving difference. The recommended Batch 3a set from PR13 remains:

- `opportunity-cost`
- `true-uncertainty-navigation`
- `falsifiability`
- `principal-agent-problem`
- `probabilistic-thinking`

Do not extract before PR14 unless the product owner explicitly accepts the
product risk of extracting before selection stability is known.

Coverage math and missing-frequency counts are evidence. They do not override
product sequencing.

## Outcomes

PR14 should recommend one of:

- `stable_enough_for_batch3a`
- `revise_surface_before_extraction`
- `downgrade_decision_pressure`
- `inconclusive`

The default if evidence is mixed should be:

`inconclusive`

## Reviewer Prompt

Use this prompt only after approval to run a reviewer response.

```text
You are a narrow Decision Pressure selection-stability reviewer.

Your task is not to generate new probes, judge Gate 4, or improve the runtime.
Your task is to read the existing 12-route Gate 4 raw packet and decide which
0-3 compact Decision Pressures, if any, should survive the Decision Pressure
gates.

Inputs:
- research/decision-pressure-surface-spec-2026-05-05.md
- research/gate4-3case-product-readout-2026-05-05.md
- research/gate4-3case-claude-code-review-2026-05-05.md
- research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md
- .tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/

Read the Decision Pressure spec first. Use the product-readout packet as raw
evidence. Treat the Claude Code review as product-shaping evidence, not formal
Gate 4 proof. If a blinded pass is feasible, do not read the PR13 dry-surface
selection until after your first selection.

Hard constraints:
- No paid model calls.
- No judge calls.
- No runtime changes.
- No prompt, validator, or affordance-record changes.
- No Batch 3a extraction.
- No new lane.
- No second public Pressure Check.

Apply these gates in order:
1. Coverage Gate.
2. Action-Delta Gate.
3. Dismissal Gate.
4. Bloat Gate.
5. Compression Gate.
6. Tone Gate.

Select 0-3 total pressures across the 12 routes, not one per route.

For each selected pressure, provide:
- Pressure
- What to verify
- Why it matters
- Dismiss if
- Tripwire or next action
- Coverage
- Provenance
- Source route/case
- Why this survived compression
- What was suppressed and why

Use only these provenance classes:
- source_backed
- case_grounded
- llm_synthesized
- user_to_verify

Then compare your selection to PR13 at the pressure-cluster level:
1. grant-equity-partnership-status / risk-response: governance deadlock before vesting.
2. mother-deciding-address-year / uncertainty-type: safety plan relying on a gameable signal.
3. third-year-phd-student / resource-allocation: shaping phase without a stop condition.

Classify each comparison as:
- stable_same
- stable_variant
- doctrine_improving_difference
- unstable_difference

End with one recommendation:
- stable_enough_for_batch3a
- revise_surface_before_extraction
- downgrade_decision_pressure
- inconclusive

Explain whether Batch 3a extraction should remain blocked, proceed to planning,
or wait for another blinded review.
```

## Open Questions

- Should the second reviewer be blinded to PR13 selections until after their
  first pass?
- Should one reviewer be enough, or should PR14 require two independent
  reviewers before Batch 3a?
- Should exact overlap be required, or is pressure-cluster overlap sufficient?
- Should a zero-output selection count as stability if it is gate-consistent
  and clearer than PR13?
- Should PR14 use a separate branch after PR13 merges, or stay as a planning
  artifact until the next coding session starts?
