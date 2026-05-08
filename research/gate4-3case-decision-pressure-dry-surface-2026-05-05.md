# Gate 4 3-Case Decision Pressure Dry Surface

**Date:** 2026-05-05
**Status:** Docs-only dry surface from existing PR11/PR12 artifacts. Product judgment, not formal Gate 4 proof.

**Inputs:**
- `research/decision-pressure-surface-spec-2026-05-05.md`
- `research/gate4-3case-product-readout-2026-05-05.md`
- `research/gate4-3case-claude-code-review-2026-05-05.md`
- `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/summary.json`
- `data/compiled/model_affordances/affordances_v3.json`
- `plans/knowledge-substrate-roadmap-2026-05-04.md`
- `plans/knowledge-use-schema-2026-05-04.md`

**Non-goals:**
- No paid model calls.
- No judge calls.
- No live `/lolla`.
- No runtime, prompt, validator, or affordance-record changes.
- No broad Batch 3 extraction.
- No new lane and no second public Pressure Check.
- No case-type rules.

**Doctrine line:** Surface pulls extraction. Extraction does not push the product.

## Summary

The existing 12-route Arm B/C readout can compress into a small Decision
Pressure surface. The dry surface below selects `3` pressures total, not one per
route. They survived because each changes a next action, has a dismissal path,
can be traced to present v3 affordance coverage, and is compact enough to show
without leaking the Arm B/C machinery.

Selected pressures:

1. `grant-equity-partnership-status / risk-response`: governance deadlock before vesting.
2. `mother-deciding-address-year / uncertainty-type`: safety plan relying on a gameable signal.
3. `third-year-phd-student / resource-allocation`: shaping phase without a stop condition.

Dry-surface verdict: `better_than_raw_probes`.

This is a product-readout verdict only. It means the compressed artifact is more
usable than the raw probe lists in this 3-case packet. It does not prove that
the runtime should promote Decision Pressure yet.

Post-verification PM read:

- PR13 is product-valid as a docs/research checkpoint.
- It does not justify live runtime, Step 6, Step 8, memo, or Lane 4 promotion.
- It does not justify more paid Gate 4 judging by default.
- It does not by itself justify Batch 3a extraction.
- The next uncertainty is selection stability: would another reviewer, using
  the same packet and gates, choose substantially the same 1-3 pressures?

Recommended eventual receiving surface: **Observatory now**. Memo later is the
first likely user-facing home if a reviewed follow-up shows selection stability.
Step 8 Pressure Check later is plausible only if the pressure is integrated as
one clear safeguard, not as a second public block. Step 6 later is reserved for
cases where the pressure changes the updated position itself.

## Working Doctrine Notes

- Decision Pressure is a synthesis object for existing surfaces.
- It is not a fifth lane.
- It is not raw Arm B/C comparison.
- It is not a second public Pressure Check.
- It is not a reason to start broad Batch 3.
- Accepted value modes are `new_edge`, `grounded_double_down`, `confirmation`, and `coverage_transparency`.
- Rejection modes are fake coverage trace, bloat, duplicate without delta, clever but not actionable, and no dismissal path.
- Field-level provenance classes used below are only `source_backed`, `case_grounded`, `llm_synthesized`, and `user_to_verify`.
- A premium empty result is allowed: `No additional source-backed pressure cleared the bar.`

## Candidate Inventory

This inventory uses the Claude Code review labels as product-shaping evidence,
not formal measurement. Coverage status is about whether the route can support
the candidate without pretending that missing v3 records exist.

| Case | Route | Arm C candidate probe | Value mode | Show label | Coverage status | Why it might matter | Gate outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `grant-equity-partnership-status` | `stakeholder-alignment` | Credible walk-away alternative if Marcus rejects the offer. | `new_edge` | `yes` | `source_backed` | Could reduce panic and change negotiation leverage. | Suppressed by compression; useful Observatory material, but less irreversible than the governance clause. |
| `grant-equity-partnership-status` | `resource-allocation` | Specific 90-day sprint hypothesis and evidence that would kill it. | `grounded_double_down` | `yes` | `source_backed` with route missing `opportunity-cost` | Turns platform sprint into a test instead of a hope. | Suppressed by compression; overlaps the selected PhD stop-condition pressure and is second-best within equity. |
| `grant-equity-partnership-status` | `risk-response` | Governance tiebreaker and buyback trigger before vesting. | `new_edge` | `yes` | `source_backed` | Adds a concrete operating-agreement safeguard B did not surface. | Selected. |
| `grant-equity-partnership-status` | `information-quality` | Test whether equity, not platform funding, is the causal intervention. | `grounded_double_down` | `yes` | `source_backed` with route missing `falsifiability` | Could prevent over-treating disengagement with cap-table change. | Suppressed by Bloat Gate; real signal is buried in a large overlapping probe set. |
| `mother-deciding-address-year` | `incentive-alignment` | Party-controlled phone evidence may be a gameable safety signal. | `grounded_double_down` | `maybe` | `source_backed` with route missing `principal-agent-problem` | Reframes monitoring from reassurance to an evidence-quality problem. | Merged into selected mother uncertainty pressure. |
| `mother-deciding-address-year` | `stakeholder-alignment` | Ex-husband custody leverage may make factual looping risky. | `confirmation` | `maybe` | `source_backed` | Could affect co-parent communication sequence. | Suppressed; B is cleaner and C adds only one thin point. |
| `mother-deciding-address-year` | `uncertainty-type` | Surveillance may not be a reliable instrument if the daughter can evade it. | `grounded_double_down` | `yes` | `source_backed` with route missing `true-uncertainty-navigation` and `probabilistic-thinking` | Safety-critical check before relying on a 3-4 week delay. | Selected. |
| `third-year-phd-student` | `competitive-dynamics` | None. C generated probes with missing model traces. | `coverage_gap` | `no` | `coverage_gap` | Honest no-output protects trust. | Zero-output candidate; hard reject any phantom source-backed pressure. |
| `third-year-phd-student` | `incentive-alignment` | If-then checkpoint may stifle heuristic PhD work. | `new_edge` | `yes` | `source_backed` with route missing `principal-agent-problem` | Changes checkpoint design, not just content. | Suppressed by compression; strong Observatory candidate but less immediately installable than the shaping stop condition. |
| `third-year-phd-student` | `information-quality` | Literature search needs a falsifiable hypothesis before it starts. | `grounded_double_down` | `yes` | `source_backed` | Converts broad research advice into a bounded information task. | Merged into selected PhD resource-allocation pressure. |
| `third-year-phd-student` | `resource-allocation` | 4-6 week shaping phase needs a specific question and stop condition. | `grounded_double_down` | `yes` | `source_backed` with route missing `opportunity-cost` | Protects scarce advisor-retirement time from open-ended exploration. | Selected. |
| `third-year-phd-student` | `uncertainty-type` | 18-month checkpoint may be calibrated to an optimistic center story. | `grounded_double_down` | `maybe` | `source_backed` with route missing `true-uncertainty-navigation` and `probabilistic-thinking` | Could resize the commitment or add intermediate reviews. | Suppressed; close to B and less action-clear than the shaping-phase gate. |

## Gate Application

### Coverage Gate

Selected pressures only use present v3 records and known case context. No
selected pressure claims source-backed support from a missing model. Partial
route gaps are stated explicitly where present.

Hard exclusion:

- `third-year-phd-student / competitive-dynamics` is a full coverage gap. Arm C
  referenced `game-theory-payoffs`, `nash-equilibrium`, `prisoners-dilemma`,
  `batna`, and `red-queen-effect` without v3 records. The correct product
  behavior is coverage transparency, not a source-backed pressure.

### Action-Delta Gate

The selected pressures change what the user should do:

- add a governance tiebreaker before signing;
- audit the safety signal before relying on delay;
- define the shaping-phase hypothesis and stop condition before beginning.

### Dismissal Gate

Each selected pressure can be cleared by evidence or action. Candidates without
a clean dismissal path were kept in Observatory or suppressed.

### Bloat Gate

The dry surface suppresses full raw probe lists. The equity
information-quality route is the warning example: it contains real signal, but
the signal arrives inside too many overlapping probes.

### Compression Gate

The final surface selects `3` pressures across `12` routes. The selection did
not allocate one pressure per route, and it did not preserve every strong
reviewer label.

## Selected Pressure 1: Governance Deadlock Before Vesting

**Pressure:** The equity grant may create a platform-strategy deadlock before vesting resolves whether Marcus is truly committed.

**What to verify:** Before signing, confirm that the operating agreement names the final decision right, conflict-resolution path, and early-warning signal that starts mediation or buyback discussion.

**Why it matters:** Equity can align incentives on paper while leaving the exact platform decision that caused the conflict unresolved. If the founder and Marcus deadlock before vesting milestones, the structure may retain the cap-table risk without retaining strategic commitment.

**Dismiss if:** The agreement already defines final decision rights, a consultation process, repurchase conditions for unresolved strategic conflict, and Marcus has accepted those rules.

**Tripwire or next action:** Add a strategy-deadlock clause and quarterly platform-alignment review before final terms are signed.

**Coverage:** `source_backed`. The selected pressure comes from a fully covered route: `risk-assessment`, `black-swan-events`, `antifragility`, `margin-of-safety`, `calculated-risk-taking`, and `resilience` all have v3 records in the packet. The direct Arm C trace is `misuse_guard` / `risk-assessment` / `risk-assessment.thresholded-downside-governance`.

**Provenance:**

| Field | Provenance class |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `source_backed`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage | `source_backed` |

**Source route/case:** `grant-equity-partnership-status / risk-response`, Arm C probe 1; Claude Code review label `new_edge`, `would_show_user: yes`.

**Why this survived compression:** It is a C-only product edge in the review, has full route coverage, names a specific pre-signing artifact, and would change legal or governance sequencing before an irreversible equity move.

**What was suppressed and why:** Equity walk-away and platform-sprint probes were useful but less distinctive at the global surface level. Equity information-quality probes were suppressed because the route was bloated and partly dependent on the missing `falsifiability` record.

## Selected Pressure 2: Safety Plan Using A Gameable Signal

**Pressure:** The safety plan may be relying on phone surveillance as if it proves safety, even though the daughter may be able to move risk to unmonitored channels.

**What to verify:** Before relying on the 3-4 week delay, check whether phone activity captures the relevant risk channel and whether there is an independent, non-coercive safety signal beyond the monitored device.

**Why it matters:** If the signal is gameable, "nothing detected" can preserve false confidence while the real risk moves elsewhere.

**Dismiss if:** There are credible independent safety signals beyond phone activity, or the mother can verify that the monitored channels cover the plausible contact paths without escalating the trust rupture.

**Tripwire or next action:** If surveillance coverage is uncertain, stop treating absence of detected contact as proof of safety; add an independent check and reconsider the disclosure or blocking timeline with professional safety guidance.

**Coverage:** `source_backed`. The pressure is grounded in present v3 records from `confidence-calibration` and `information-asymmetry` style field sources. The primary source route is `mother-deciding-address-year / uncertainty-type`, Arm C probe 4: `misuse_guard` / `confidence-calibration` / `confidence-calibration.instrument-trust-before-precision`. The same pressure is reinforced by `mother-deciding-address-year / incentive-alignment`, Arm C probe 5, but the selected surface does not claim support from the missing `principal-agent-problem`, `true-uncertainty-navigation`, or `probabilistic-thinking` records.

**Provenance:**

| Field | Provenance class |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `llm_synthesized`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage | `source_backed` |

**Source route/case:** `mother-deciding-address-year / uncertainty-type`, Arm C probe 4; supported by `mother-deciding-address-year / incentive-alignment`, Arm C probe 5. Claude Code review label `grounded_double_down`, `would_show_user: yes` for the uncertainty route.

**Why this survived compression:** It changes the next action before a safety-relevant delay, has a humane dismissal path, and can be written without diagnosing or blaming the daughter. It is not "relationship case" doctrine; it survived because the gate found a concrete evidence-quality failure.

**What was suppressed and why:** Other mother-case probes around therapist readiness, the ex-husband, and moral hazard were suppressed because B often stated them more cleanly or because they would require more explanation than the final user surface should carry.

## Selected Pressure 3: Shaping Phase Without A Stop Condition

**Pressure:** The 4-6 week shaping phase may become open-ended exploration under a hard advisor-retirement clock.

**What to verify:** Name the specific question the shaping phase must answer and the evidence that would end the phase.

**Why it matters:** Without a stop condition, the first action can consume the scarce time it is supposed to protect.

**Dismiss if:** The shaping phase already has explicit non-goals, a decision-relevant deliverable, a hard stop date, and success or failure criteria for the next committee decision.

**Tripwire or next action:** Write a one-page shaping contract before the literature search begins: question, non-goals, stop date, evidence threshold, and next decision.

**Coverage:** `source_backed`. The selected pressure traces to present v3 records in `prioritization` and `optimization-theory`, especially `prioritization.hypothesis-driven-end-product-execution` and `optimization-theory.leverage-bounded-analysis`. The route is missing `opportunity-cost`; this pressure does not claim source support from that missing record.

**Provenance:**

| Field | Provenance class |
| --- | --- |
| Pressure | `llm_synthesized`, `case_grounded` |
| What to verify | `source_backed`, `user_to_verify` |
| Why it matters | `llm_synthesized`, `case_grounded` |
| Dismiss if | `source_backed`, `user_to_verify` |
| Tripwire or next action | `llm_synthesized`, `user_to_verify` |
| Coverage | `source_backed` |

**Source route/case:** `third-year-phd-student / resource-allocation`, Arm C probe 7; reinforced by `third-year-phd-student / information-quality`, Arm C probe 5. Claude Code review label `grounded_double_down`, `would_show_user: yes`.

**Why this survived compression:** It converts a broad "be strategic" concern into an immediate execution gate before the user's next move. It also absorbs adjacent PhD information-quality signal without showing a second pressure.

**What was suppressed and why:** The PhD incentive-alignment checkpoint-design probe is strong, but it is less immediately installable than the shaping contract. The uncertainty-type lower-bound checkpoint probe is useful but close to B and better kept as Observatory material.

## Tone Range

A relational/emotional candidate was selected: the mother safety-signal
pressure. The surface deliberately names the decision instrument, not the
daughter as a problem. It avoids clinical language, blame, and covert certainty.
The user-visible form should feel like: "Before relying on this plan, check
whether the signal you are using can actually carry the decision." That is a
product finding about evidence quality, not a case-type rule.

## Evaluation Against Raw Arm B/C Probe Lists

**Verdict:** `better_than_raw_probes`.

The compressed surface beats the raw probe lists in this dry readout because it:

- reduces the working set from `126` raw Arm B/C probes to `3` decision safeguards;
- preserves the strongest action-changing pressure in each selected cluster;
- adds dismissal paths and tripwires that raw lists scatter across probes;
- states coverage limits instead of implying all routed models are grounded;
- hides route IDs, affordance IDs, and Arm B/C machinery from the user surface.

This verdict is not a formal Gate 4 pass. It is a reviewer-eye product judgment
that the compressed surface is easier to use before acting than reading the raw
Arm B/C outputs.

### Coverage Honesty And Machinery Leaks

The selected surface does not show raw route IDs, trace IDs, field counts, or
validator errors as user-facing content. The research artifact records them for
custody. A future product surface should expose coverage status in plain words,
with details staying in Observatory unless the user asks for trace detail.

The PhD competitive-dynamics route is a hard boundary: no source-backed pressure
should be produced from the missing game-theory cluster until reviewed records
exist.

### Generic Prompt Check

A strong generic prompt could likely generate versions of these concerns. The
substrate value in this dry surface is not magical novelty. It is:

- traceable selection from reviewed route evidence;
- pressure compression rather than probe sprawl;
- dismissal and tripwire discipline;
- explicit coverage honesty;
- confirmation that some attractive candidates should be suppressed.

If a future blinded reviewer cannot distinguish this surface from "ask a strong
LLM to make the advice more actionable," the Decision Pressure direction should
be downgraded.

### Zero-Output Success

A premium empty result would say:

> No additional source-backed pressure cleared the bar.

That output should be used when all candidates fail Coverage, Action-Delta,
Dismissal, or Bloat gates. It is better than padding a run with weak pressure.

## Appendix

### Selected Pressures

| Selected | Case | Route | Receiving surface now |
| --- | --- | --- | --- |
| Governance deadlock before vesting | `grant-equity-partnership-status` | `risk-response` | Observatory |
| Safety plan using a gameable signal | `mother-deciding-address-year` | `uncertainty-type` | Observatory |
| Shaping phase without a stop condition | `third-year-phd-student` | `resource-allocation` | Observatory |

### Suppressed Candidates

| Candidate | Reason suppressed |
| --- | --- |
| Equity walk-away alternative | Useful, but lower immediate irreversibility than governance deadlock. Keep in Observatory. |
| Equity 90-day sprint hypothesis | Useful, but overlaps the selected PhD stop-condition pattern and loses global compression priority. |
| Equity platform-funding alternative | Real signal, but route is bloated and partly missing `falsifiability`. |
| Mother therapist-readiness and therapist-fit probes | Actionable but secondary; showing them would turn the surface into a checklist. |
| Mother ex-husband custody leverage | B is cleaner; C is confirmation or a thin add. |
| Mother moral-hazard/graduated-consequence probes | Risk of over-explaining and moralizing; not the best humane pressure. |
| PhD contingent deadline on heuristic work | Strong Observatory candidate, but less concrete than the shaping contract. |
| PhD literature-search hypothesis | Merged into the shaping stop-condition pressure. |
| PhD lower-confidence-bound checkpoint | Useful but close to B; keep for Observatory. |
| PhD competitive-dynamics probes | Hard coverage rejection because all five routed models were missing from v3. |

### Coverage Gaps

3-case missing v3 model IDs:

- `opportunity-cost`: 2 route appearances.
- `principal-agent-problem`: 2 route appearances.
- `true-uncertainty-navigation`: 2 route appearances.
- `probabilistic-thinking`: 2 route appearances.
- `falsifiability`: 1 route appearance.
- `game-theory-payoffs`: 1 route appearance and part of a full-route gap.
- `nash-equilibrium`: 1 route appearance and part of a full-route gap.
- `prisoners-dilemma`: 1 route appearance and part of a full-route gap.
- `batna`: 1 route appearance and part of a full-route gap.
- `red-queen-effect`: 1 route appearance and part of a full-route gap.

Selected pressures avoid claiming source support from missing models. Partial
route gaps remain important for Batch 3a prioritization, but they do not block
the three selected pressures.

### Zero-Output Candidates

`third-year-phd-student / competitive-dynamics` is the clean zero-output
candidate:

> No substrate-backed competitive-dynamics pressure is available for this route
> because all selected models are missing reviewed affordance records.

This is better than showing probes with phantom traces.

### Recommended Receiving Surface

Recommendation: **Observatory now**.

Rationale:

- The surface appears better than raw probes, but selection stability is not yet tested.
- User-facing Step 8 integration risks creating a second public Pressure Check.
- Memo integration is plausible later because the object is compact and action-oriented.
- Step 6 integration should wait until a pressure clearly changes the updated position.

### Next Review

Recommended next research checkpoint:

> PR14 - Decision Pressure Selection Stability Review

Give the same 12-route raw packet and Decision Pressure gates to another
narrow reviewer. Ask for 1-3 total selected pressures, suppressed candidates,
and a receiving-surface recommendation.

Pass signal:

- another reviewer selects at least 2 of the same 3 pressures; or
- selects different pressures for stable, gate-consistent reasons that improve
  the doctrine.

Failure signal:

- selections vary wildly;
- reviewer cannot apply the gates consistently;
- the best pressures depend on taste rather than observable action delta,
  coverage honesty, dismissal, compression, and bloat suppression.

Only after this review should Batch 3a extraction or memo/Pressure Check
promotion be treated as a product-next move.
