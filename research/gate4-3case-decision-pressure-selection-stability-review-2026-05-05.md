# Gate 4 3-Case Decision Pressure Selection Stability Review

**Date:** 2026-05-05
**Status:** Second-review result for PR14. Product-shaping evidence, not formal
Gate 4 proof and not runtime evidence.
**Reviewer:** Claude Code (`claude-sonnet-4-6`), narrow second-review pass.
**Execution:** No paid model calls, no judge calls, no runtime changes, no
prompt/validator/affordance-record changes, no Batch 3a extraction, no file
edits by the reviewer.

---

## 1. Blindness Caveat

The reviewer reported that `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
was not read before the first selection.

This should still be recorded as a **partially blinded / non-fully-blinded**
review, not a perfect blinded test, because the reviewer did read
`research/gate4-3case-decision-pressure-selection-stability-2026-05-05.md`, and
that PR14 planning artifact contains the PR13 reference selection later in the
file.

The result is still useful product evidence:

> A second narrow reviewer, working from the same packet and gates, converged
> 3/3 with PR13 at the pressure-cluster level.

Do not describe this as formal measurement proof.

---

## 2. Method

The reviewer used the existing artifacts only:

- `research/decision-pressure-surface-spec-2026-05-05.md`
- `research/gate4-3case-product-readout-2026-05-05.md`
- `research/gate4-3case-claude-code-review-2026-05-05.md`
- `research/gate4-3case-decision-pressure-selection-stability-2026-05-05.md`

They applied the six Decision Pressure gates:

1. Coverage Gate
2. Action-Delta Gate
3. Dismissal Gate
4. Bloat Gate
5. Compression Gate
6. Tone Gate

They selected `3` total pressures across the `12` routes.

---

## 3. Selected Pressures

### 3.1 Equity Governance Deadlock Before Vesting

**Source route/case:** `grant-equity-partnership-status / risk-response`

**Pressure:** The equity grant may create a governance deadlock before vesting
resolves commitment.

**What to verify:** Whether the operating agreement defines a tiebreaker for
founder-CTO platform strategy conflicts and a trigger that would activate a
buyback discussion.

**Why it matters:** Equity aligns incentives on paper, but if a deadlock occurs
within the first 18 months, before vesting anchors Marcus's commitment, the
structure can still fail when the platform bet is live.

**Dismiss if:** The agreement already specifies decision rights, a deadlock
resolution process, and a buyback trigger, and Marcus has accepted the
framework.

**Tripwire or next action:** Add a strategy-deadlock clause and early-warning
trigger before final terms are signed.

**Coverage:** `source_backed`

**Provenance:** `source_backed` from
`risk-assessment.thresholded-downside-governance`; dismissal and tripwire are
`case_grounded` plus `user_to_verify`.

**Why this survived compression:** It is a contractual gap that must be closed
before signing. It is hard to recover after the cap table changes.

### 3.2 Safety Plan Using A Gameable Signal

**Source route/case:** `mother-deciding-address-year / uncertainty-type`

**Pressure:** The safety plan relies on an instrument the daughter can route
around.

**What to verify:** Whether phone surveillance covers all realistic
communication channels, or whether the daughter could be using hidden apps, a
second device, or account-switching to communicate without detection.

**Why it matters:** If the mother's assessment of safety during the 3-4 week
delay depends on surveillance that misses the actual channel, the delay creates
exposure while producing false confidence.

**Dismiss if:** The surveillance has been confirmed to cover all known channels
the daughter uses, and there is no behavioral signal suggesting evasion.

**Tripwire or next action:** Before relying on the delay, add at least one
independent safety signal not controlled by the daughter's phone activity.

**Coverage:** `source_backed`

**Provenance:** `source_backed` from
`confidence-calibration.instrument-trust-before-precision`; dismissal is
`user_to_verify`; tripwire is `llm_synthesized` from case evidence.

**Why this survived compression:** It is safety-critical, time-sensitive,
non-blaming, and action-clear. It frames the problem as signal quality rather
than character judgment.

### 3.3 Shaping Phase Without A Stop Condition

**Source route/case:** `third-year-phd-student / resource-allocation`

**Pressure:** The shaping phase may become open-ended exploration without a
stop condition.

**What to verify:** Whether the 4-6 week shaping phase has a specific question
it must answer and what evidence would end it.

**Why it matters:** Without a stop condition, the first exploratory action can
consume the scarce time it was designed to protect, especially under an
advisor-retirement clock.

**Dismiss if:** The shaping phase already has explicit non-goals, a defined
question to answer, and a next-decision date with pre-committed action if the
question is not resolved.

**Tripwire or next action:** Write the shaping-phase stop condition before
starting the literature search.

**Coverage:** `source_backed`

**Provenance:** `source_backed` from
`optimization-theory.leverage-bounded-analysis` and
`prioritization.hypothesis-driven-end-product-execution`; dismissal is
`user_to_verify`; tripwire is `case_grounded`.

**Why this survived compression:** It is immediately actionable and converts a
conceptual resource-allocation concern into a concrete gate.

---

## 4. Comparison Against PR13

| PR13 pressure cluster | Second reviewer selection | Stability classification |
| --- | --- | --- |
| `grant-equity-partnership-status / risk-response`: governance deadlock before vesting | Same pressure cluster | `stable_same` |
| `mother-deciding-address-year / uncertainty-type`: safety plan relying on a gameable signal | Same pressure cluster | `stable_same` |
| `third-year-phd-student / resource-allocation`: shaping phase without a stop condition | Same pressure cluster | `stable_same` |

Overall comparison:

> 3/3 pressure-cluster convergence with the same gate rationale.

---

## 5. Suppressed Strong Candidates

- `third-year-phd-student / incentive-alignment`: contingent checkpoint on
  heuristic work. The reviewer considered this a legitimate `new_edge`, but it
  lost only to the Compression Gate. It should be reconsidered in later
  compression passes, especially after `principal-agent-problem` extraction.
- `grant-equity-partnership-status / stakeholder-alignment`: walk-away
  alternatives. Strong, but less irreversible than a missing deadlock clause.
- `grant-equity-partnership-status / resource-allocation`: 90-day sprint
  hypothesis and kill criteria. Strong, but partly overlaps the selected PhD
  stop-condition pressure.

---

## 6. Coverage Gaps

- `third-year-phd-student / competitive-dynamics`: Coverage Gate reject. All
  five routed models are missing from v3, and Arm C generated phantom traces.
  Correct output remains coverage transparency / zero-output.
- `mother-deciding-address-year / uncertainty-type` and
  `third-year-phd-student / uncertainty-type`: partial coverage only. Selected
  or suppressed pressures should claim support only from available v3 records.

---

## 7. Stability Verdict

`stable_enough_for_batch3a`

Interpretation:

Selection stability is strong enough to proceed toward Batch 3a **planning**.
It is not evidence for runtime promotion, memo promotion, Step 8 promotion, Step
6 promotion, or live Lane 4 integration.

The remaining gates before product promotion are different:

- Batch 3a must still extract source-backed operational constraints, not model
  summaries.
- The post-Batch-3a surface still needs dry-review evidence.
- User-facing integration still needs a separate product review.

---

## 8. Batch 3a Implication

Batch 3a may proceed to planning with the PR13 recommended set:

- `opportunity-cost`
- `true-uncertainty-navigation`
- `falsifiability`
- `principal-agent-problem`
- `probabilistic-thinking`

The reviewer added one important nuance:

> `third-year-phd-student / incentive-alignment` was the strongest suppressed
> latent pressure and lost only to Compression Gate. `principal-agent-problem`
> extraction should pay special attention to checkpoint design, hidden effort,
> delegated incentives, task-fit incentives, and when incentive framing becomes
> bad-faith theater.

---

## 9. Open Questions

- Should the normal cap remain `1-3` total pressures per run, or should some
  high-stakes cases allow `1` per major case cluster?
- Should cross-route confirmation, such as the mother instrument-trust pressure
  appearing in two routes, merge silently or become
  `source_backed_confirmation`?
- Should a future fully blinded review be required before user-facing memo
  integration, even though this partially blinded pass is sufficient for Batch
  3a planning?
