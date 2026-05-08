# Gate 4 3-Case Decision Pressure Observatory Prototype

**Date:** 2026-05-05
**Status:** Static research artifact. No runtime integration, no UI
implementation, no user-facing promotion, no model calls, no judge calls, no
new extraction, no prompt changes, no validator changes, and no affordance
record rewrites.

**Branch:** `feature/decision-pressure-pr18-observatory-static-prototype`

**Doctrine:**

> Surface pulls extraction. Extraction does not push the product.

> Observatory before user surface.

> Coverage transparency is a feature, not an apology.

## Product Question

Would this Observatory trace help an operator trust and understand the Decision
Pressure result?

Short answer:

> Yes. A compact operator-facing trace is clearer than the raw Arm B/C probe
> lists because it shows the selected pressure, the support it rests on, the
> nearby candidates it suppresses, and the blank it refuses to fill.

Prototype verdict: `observatory_trace_clearer`

This verdict does not justify runtime integration, a UI build, memo promotion,
Step 8 promotion, Step 6 promotion, Lane 4 promotion, Batch 3b, or a paid Gate
4 rerun.

## Prototype Rules

This prototype uses exactly the same three selected pressure clusters from
PR13, confirmed by PR14, and sharpened by PR17:

1. Equity / risk-response: governance deadlock before vesting.
2. Mother / uncertainty-type: safety plan relying on a gameable signal.
3. PhD / resource-allocation: shaping phase without a stop condition.

Rules:

- Use PR17 v4-sharpened wording where it improves field quality.
- Do not add a fourth pressure.
- Do not turn suppressed candidates into public pressures.
- Do not hide coverage gaps.
- Do not claim actual Arm C output changed; PR18 is a manual static prototype.
- Do not treat this as a user-facing card design or implementation spec.

## Observatory Card Shape

Each operator-facing card uses these fields:

- Pressure
- What to verify
- Why it matters
- Dismiss if
- Tripwire or next action
- Coverage status
- Provenance
- Source routes
- Source affordances
- v4 contribution
- Suppressed nearby candidates
- Why suppressed
- Operator note
- User-facing readiness

Allowed provenance classes:

- `source_backed`
- `case_grounded`
- `llm_synthesized`
- `user_to_verify`

Allowed coverage status options:

- `fully_source_backed`
- `partially_source_backed`
- `coverage_transparency`
- `no_substrate_backed_pressure`

Allowed user-facing readiness values:

- `not_ready`
- `maybe_later`
- `candidate_after_review`

## Observatory Cards

### Card 1: Equity Governance Deadlock Before Vesting

**Pressure:** The equity grant may create a platform-strategy deadlock before
vesting resolves whether Marcus is truly committed.

**What to verify:** Before signing, confirm that the operating agreement names
final decision rights, a conflict-resolution path, and the early-warning signal
that starts mediation, repurchase, or buyback discussion.

**Why it matters:** Equity can align incentives on paper while leaving the
exact platform decision that caused the conflict unresolved. If the founder and
Marcus deadlock before vesting milestones, the structure may keep cap-table
risk without preserving strategic commitment.

**Dismiss if:** The agreement already defines final decision rights,
consultation or escalation process, repurchase conditions for unresolved
strategic conflict, and Marcus has accepted those rules.

**Tripwire or next action:** Add a strategy-deadlock clause and quarterly
platform-alignment review before final terms are signed.

**Coverage status:** `fully_source_backed`

**Provenance:**

| Field | Provenance |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `source_backed`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage status | `source_backed` |

**Source routes:**

- `grant-equity-partnership-status / risk-response`

**Source affordances:**

- `risk-assessment.thresholded-downside-governance`
- `calculated-risk-taking.pressure-tested-bounded-wager`
- `margin-of-safety.evidence-sized-operating-buffer`

**v4 contribution:** `minor`. The new
`opportunity-cost.displaced-alternative-commitment-gate` can lightly reinforce
that an equity grant is not free if it forecloses cap-table flexibility, but it
does not change the selected pressure. The pressure remains primarily a
risk-response and governance-design issue.

**Suppressed nearby candidates:**

- Equity / resource-allocation: 90-day sprint hypothesis and kill criteria.
- Equity / stakeholder-alignment: walk-away alternatives.
- Equity / information-quality: equity versus platform funding as causal
  intervention.

**Why suppressed:** The 90-day sprint and walk-away alternatives are useful
Observatory material, especially after v4, but the deadlock clause is more
irreversible and more directly tied to the equity signing decision. The
information-quality candidate remains too bloated for the compact surface.

**Operator note:** This is the cleanest candidate for eventual user-facing
readiness because the action is concrete and pre-signing. Keep the v4
opportunity-cost support in trace details, not in the main pressure wording.

**User-facing readiness:** `candidate_after_review`

### Card 2: Safety Plan Using A Gameable Signal

**Pressure:** The safety plan may be relying on phone surveillance as if it
proves safety, even though the daughter may be able to move risk to
unmonitored channels.

**What to verify:** Before relying on the 3-4 week delay, verify that the
safety signal is not controlled by the party whose behavior it is meant to
reveal. If the monitored channel is incomplete or gameable, add an independent,
non-coercive safety signal before treating absence of detection as evidence of
safety.

**Why it matters:** If the signal is gameable, "nothing detected" can preserve
false confidence while the real risk moves elsewhere. The decision needs signal
quality, not more certainty language.

**Dismiss if:** There are credible independent safety signals beyond phone
activity, or the mother can verify that monitored channels cover plausible
contact paths without escalating the trust rupture.

**Tripwire or next action:** If surveillance coverage is uncertain, stop
treating absence of detected contact as proof of safety; add an independent
check and reconsider the disclosure or blocking timeline with professional
safety guidance.

**Coverage status:** `partially_source_backed`

**Provenance:**

| Field | Provenance |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `llm_synthesized`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage status | `source_backed`, `case_grounded` |

**Source routes:**

- `mother-deciding-address-year / uncertainty-type`
- `mother-deciding-address-year / incentive-alignment`

**Source affordances:**

- `confidence-calibration.instrument-trust-before-precision`
- `information-asymmetry.redesign-party-controlled-evidence`
- `principal-agent-problem.delegated-alignment-drift-audit`
- `true-uncertainty-navigation.scenario-bound-robust-action`
- `probabilistic-thinking.range-and-sensitivity-decision-gate`

**v4 contribution:** `material`. v4 makes the pressure easier to support
without overclaiming: `true-uncertainty-navigation` keeps the action robust
under ambiguity, `probabilistic-thinking` warns against false certainty from an
incomplete signal, and `principal-agent-problem` helps name party-controlled
evidence while warning against bad-faith framing.

**Suppressed nearby candidates:**

- Mother / incentive-alignment: party-controlled evidence.
- Mother / stakeholder-alignment: ex-husband custody leverage.
- Mother / therapist-readiness and therapist-fit probes.
- Mother / moral-hazard or graduated-consequence probes.

**Why suppressed:** Party-controlled evidence is merged into the selected
pressure. Separate incentive or moral-hazard language risks blaming the
daughter and violating the Tone Gate. Therapist and custody probes may be
useful operator detail, but showing them as separate pressures would turn the
compact surface into a checklist.

**Operator note:** This card is useful in Observatory because it shows the
operator why the pressure is about signal quality, not character judgment. A
future user-facing version needs careful safety-sensitive wording and possibly
professional-guidance framing.

**User-facing readiness:** `maybe_later`

### Card 3: Shaping Phase Without A Stop Condition

**Pressure:** The 4-6 week shaping phase may become open-ended exploration
under a hard advisor-retirement clock.

**What to verify:** Before the literature search starts, write the shaping
contract: the question it must answer, the next-best use of the same advisor
time, the evidence that would end the phase, and the decision that follows if
the question is not resolved by the stop date.

**Why it matters:** Without a stop condition, the first exploratory action can
consume the scarce advisor time, committee attention, and thesis optionality it
was supposed to protect.

**Dismiss if:** The shaping phase already has explicit non-goals, a
decision-relevant deliverable, a hard stop date, and success or failure
criteria for the next committee decision.

**Tripwire or next action:** Write a one-page shaping contract before the
literature search begins: question, non-goals, stop date, evidence threshold,
next-best alternative use of advisor time, and next decision.

**Coverage status:** `partially_source_backed`

**Provenance:**

| Field | Provenance |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `source_backed`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage status | `source_backed`, `case_grounded` |

**Source routes:**

- `third-year-phd-student / resource-allocation`
- `third-year-phd-student / information-quality`

**Source affordances:**

- `prioritization.hypothesis-driven-end-product-execution`
- `prioritization.capacity-constrained-exclusion-and-sequencing`
- `optimization-theory.leverage-bounded-analysis`
- `opportunity-cost.displaced-alternative-commitment-gate`
- `falsifiability.disconfirming-reversal-gate`

**v4 contribution:** `material`. `opportunity-cost` turns advisor-retirement
time into a real displaced alternative, and `falsifiability` makes the shaping
contract more dismissible by requiring a completion or disconfirmation
condition.

**Suppressed nearby candidates:**

- PhD / incentive-alignment: contingent checkpoint on heuristic work.
- PhD / information-quality: falsifiable hypothesis before literature search.
- PhD / uncertainty-type: 18-month checkpoint calibrated to an optimistic
  center story.
- PhD / competitive-dynamics: game-theory cluster coverage gap.

**Why suppressed:** Information-quality support is merged into the shaping
contract. The incentive-alignment candidate is stronger after v4, but still
risks bloat as a fourth pressure and should stay merged or Observatory-only.
The uncertainty candidate needs a generated v4 pass before it can beat the
shaping stop condition. Competitive-dynamics remains zero-output.

**Operator note:** This card shows why v4 mattered: it did not change the
selected cluster, but it made the card more operational, more dismissible, and
more honest about scarce time.

**User-facing readiness:** `candidate_after_review`

## Coverage Transparency Panel

### PhD / Competitive-Dynamics

**Coverage status:** `no_substrate_backed_pressure`

No substrate-backed competitive-dynamics pressure is available because the
routed game-theory cluster still lacks reviewed affordance records.

Missing models:

- `game-theory-payoffs`
- `nash-equilibrium`
- `prisoners-dilemma`
- `batna`
- `red-queen-effect`

This is not a failure of the product surface. It is trust-preserving behavior.
The operator should see the blank because it prevents phantom traces and fake
confidence.

Operator trace copy:

> No reviewed affordance records exist for the routed competitive-dynamics
> cluster. The system can reason generically, but it cannot claim
> substrate-backed pressure for this route.

Do not smooth this over with `opportunity-cost`, `principal-agent-problem`, or
`probabilistic-thinking`. Those records are useful elsewhere, but they do not
cover the missing game-theory cluster.

## Suppression Panel

| Candidate | Suppression reason | Did v4 make it stronger? | Prototype disposition |
| --- | --- | --- | --- |
| PhD / incentive-alignment: contingent checkpoint on heuristic work | Strong but lost to Compression Gate; less immediately installable than the shaping contract. | Yes. `principal-agent-problem` adds delegated-alignment and metric-compliance discipline, with caution against suspicion and micromanagement. | `merged_support` |
| Equity / resource-allocation: 90-day sprint hypothesis and kill criteria | Useful, but overlaps the selected PhD stop-condition pattern and remains second-best behind governance deadlock. | Yes. `opportunity-cost` and `falsifiability` sharpen displaced work and kill criteria. | `observatory_only` |
| Equity / stakeholder-alignment: walk-away alternatives | Useful, but lower immediate irreversibility than the governance clause. Missing `batna` still limits negotiation substrate. | Somewhat. `opportunity-cost` makes the walk-away alternative more concrete, but does not replace BATNA. | `still_suppressed` |
| Mother / incentive-alignment: party-controlled evidence | Same pressure as selected safety-signal card when written humanely. Separate card risks blame. | Yes. `principal-agent-problem` adds the party-controlled evidence frame and its do-not-use cautions. | `merged_support` |
| PhD / information-quality: falsifiable hypothesis before literature search | Real signal, but best used inside the shaping contract. Separate pressure would duplicate the selected card. | Yes. `falsifiability` materially improves dismissal and stop-condition language. | `merged_support` |
| PhD / uncertainty-type: checkpoint calibrated to optimistic center story | Useful but close to B and less action-clear than the shaping gate. | Yes. `true-uncertainty-navigation` and `probabilistic-thinking` improve lower-bound and false-precision language. | `needs_generation_test` |

Suppression is part of the product surface. Observatory should show strong
near-misses so operators can audit why the system selected three pressures
instead of turning every good candidate into another user-visible block.

## Prototype Verdict

`observatory_trace_clearer`

Why:

- The operator can see why each pressure survived.
- The operator can see what v4 changed without assuming generated outputs
  changed.
- The operator can inspect provenance without exposing trace machinery to the
  user.
- The operator can see suppressed candidates and why they stayed suppressed.
- The operator can see the competitive-dynamics blank as an intentional trust
  signal.

Why it is not yet implementation:

- The card shape is still hand-authored.
- No runtime data shape exists.
- No UI behavior exists.
- No reviewer has evaluated whether this operator trace is too heavy in actual
  Observatory use.
- User-facing readiness remains blocked.

## Recommendation

PR18 should be accepted as a static prototype if reviewer agrees that the trace
is clearer than the PR17 review alone.

Recommended next step:

> PR19 should be a runtime-dormant data-shape spec for a
> `decision_pressure_trace` object, not live Observatory integration.

That spec should define the data contract needed to represent:

- selected pressure fields;
- coverage status;
- field-level provenance;
- source routes;
- source affordances;
- v4 contribution;
- suppressed candidates;
- coverage transparency panels;
- user-facing readiness;
- runtime dormancy.

What should remain blocked:

- memo promotion;
- Step 8 promotion;
- Step 6 promotion;
- Lane 4 live behavior;
- `/lolla` runtime changes;
- user-facing Decision Pressure blocks;
- Batch 3b;
- paid Gate 4 reruns by default.

Stop condition:

If a reviewer finds this Observatory trace too heavy, PR19 should not specify a
data shape yet. Instead, PR19 should do one more static compression pass and
ask which trace fields are actually necessary for operator trust.

## Open Questions

- Should `user-facing readiness` live in the trace object, or should it remain
  a review-only note until runtime work begins?
- Should `principal-agent-problem` medium confidence be shown as a visible
  badge in Observatory whenever it contributes to a pressure?
- Should coverage transparency panels be attached to the nearest case, nearest
  route, or the whole run?
- Should suppressed candidates be collapsed by default, or shown whenever a
  candidate had a `yes`/`maybe` showability label in PR13/PR14?
