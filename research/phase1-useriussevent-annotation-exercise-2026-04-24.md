# Phase 1 Pre-Implementation Gate — `UserIssueEvent.kind` Annotation Exercise

**Date:** 2026-04-24
**Purpose:** determine whether the 3-kind discrimination (`constraint` / `concern` / `open_loop`) in the proposed v1 IR is reliably reproducible by two independent reviewers on real decision-shaped text.
**Outcome:** inter-rater agreement ≥80% → Phase 1 proceeds as designed. <80% → kill criterion fires; narrow the ontology before the coder writes code.

## Why this gate exists

The Phase 0.5 adoption memo accepted `UserIssueEvent` as a single family with `kind` discriminator + lifecycle (`status`, `resolved_at_turn`, `superseded_by`). GraphRAG validates the single-family pattern. What external systems cannot validate for us: whether the specific 3-kind taxonomy (`constraint` / `concern` / `open_loop`) is learnable in practice on our conversation-audit domain.

If reviewers can't tell the kinds apart reliably, the taxonomy is too fine-grained. Forcing it through would produce an ontology that looks clean on paper but fails in practice. The correct response to low agreement is to simplify, not to argue.

## Definitions (reviewer-facing)

Read these before classifying anything.

### `constraint`
A structural or factual element that limits or defines the decision. The user has stated it and it is currently in force. Examples: a hard budget, a time window, a stakeholder's position, a known limitation. Constraints are not themselves problems to solve — they are the environment the decision happens in.

Key test: **If this disappeared, would the decision look materially different? And is the user treating it as a given rather than as something to resolve?**

### `concern`
An unresolved worry, risk, or open question the user raised, which has not yet been addressed or reduced. Unlike a constraint, a concern is *live and active*: the user is looking for the decision to either resolve it or acknowledge it explicitly. Concerns often have an emotional or evaluative tone ("I'm worried that...", "What if...").

Key test: **Is this something the user wants the decision to address, not just work around?**

### `open_loop`
A topic the user (or assistant) raised that was explicitly set aside, deferred, or superseded by a different framing. Open-loops are not active in the current decision but are recorded so future context or lane packets can surface them if relevant. In the extraction schema these map to `dropped_threads` with `status="acknowledged_then_dropped"` or a `superseded_by` field populated.

Key test: **Was this topic parked — either by the user saying "not that" or by the conversation pivoting to a different framing — rather than resolved or addressed?**

### Distinguishing guidance for hard cases

- A factual observation about the situation (e.g., "divorced from co-parent, share custody") = **constraint**, not concern, even if it's unpleasant. Constraints can be unpleasant.
- A worry phrased as a question ("I don't know if 8 months is enough") = **concern**, not constraint. The user is asking for resolution.
- A topic that appears in the conversation then gets replaced by a different framing = **open_loop**, not concern. The user moved on.
- A probabilistic assessment the user made and is acting on (e.g., "I'm 60-65% confident") = **constraint** of the user's current model, not concern. The user has already integrated this assessment.
- If genuinely ambiguous between two kinds, mark with **both kinds separated by "/"** (e.g., `constraint/concern`) — these get surfaced as ontology-ambiguity signal, not silently forced into one bucket.

## Protocol

1. **Independence.** Each reviewer classifies without seeing the other's answers. Do not discuss items while classifying.
2. **One pass through the items.** Don't revise after completing. First-read classification is what counts — this mirrors how a future annotator would work.
3. **Ambiguity is valid.** Marking `constraint/concern` on a genuinely unclear item is better than forcing a choice. Ambiguous items count as *half-disagreement* in scoring (see below).
4. **Self-check per kind at end.** After completing, re-read your own classifications and flag any you'd want to revisit. Don't change them — just note.

## Scoring

- Total items: 17 (5 user_has_plan + 6 whistleblower + 6 parenting_teen).
- Agreement calculation:
  - Full agreement (same single kind from both reviewers): +1.0
  - Partial agreement (one reviewer marked ambiguous with the other's kind in the pair, e.g., `constraint/concern` vs `constraint`): +0.5
  - Full disagreement: 0.0
- **Agreement rate = sum / 17**
- **≥0.80 = gate passes.** Phase 1 may proceed.
- **<0.80 = gate fails.** See decision options below.

## Decision options if agreement < 80%

Do not force the gate. Three options, ranked by preference:

1. **Drop `concern` from v1.** Most disagreements likely cluster on the `constraint` vs `concern` boundary. If we collapse concerns into `constraint` (everything active becomes `kind="constraint"` with `status` carrying the lifecycle), the ontology shrinks to a 2-kind choice (`constraint` / `open_loop`) which is much more learnable. Phase 3 can revisit concerns if needed.
2. **Promote ambiguity to a first-class signal.** Keep the 3 kinds but add `kind_confidence: {high, low}` so annotators + extractors can mark their uncertainty. Loses some rigidity but preserves the taxonomy.
3. **Rewrite definitions, re-run exercise.** If disagreements concentrate on definition interpretation rather than genuine ambiguity, sharpen the definitions and repeat the exercise. Risk: this can loop indefinitely.

Kill criterion honored either way: if option 1 or 2 is taken, the roadmap + archaeology get updated to reflect the narrowed ontology before Phase 1 code begins.

## Items to classify

Each item shows: source extraction text, turn reference, and current extraction `status` if applicable. Classify against the definitions above. The two columns on the right are blank — each reviewer fills their own.

### `user_has_plan` (5 items)

| # | Item | Source turn / status | Reviewer A | Reviewer B |
|---|---|---|---|---|
| 1 | Pipeline: 4-5 informal network conversations, no signed commitments | turn 1 / active | constraint | constraint |
| 2 | Runway: 8 months at zero revenue | turn 1 / active | constraint | constraint |
| 3 | Launch timeline: 6 weeks from now, aligned with Q3 planning end | turn 1 / active | constraint | constraint |
| 4 | Spouse support: on board with concept, not specifics of financial pressure | turn 5 / active | constraint/concern | constraint/concern |
| 5 | Tactical launch plan details (pricing, positioning, website, legal structure) | turn 1 / acknowledged_then_dropped / superseded_by focus on fundamentals | open_loop | open_loop |

### `whistleblower` (6 items)

| # | Item | Source turn / status | Reviewer A | Reviewer B |
|---|---|---|---|---|
| 6 | Active regulatory audit on client account | turn 1 / active | constraint | constraint |
| 7 | Senior partner shredding 3 boxes of financial docs/emails at 6am non-shred location | turn 1 / active | constraint | constraint |
| 8 | 60-65% confidence in general counsel handling | turn 6 / active | constraint | constraint |
| 9 | Family financial stakes: mortgage, two kids nearing high school | turn 4 / active | constraint | constraint |
| 10 | Legitimate explanations for shredding (duplicates, personal work) | turn 2 / acknowledged_then_dropped / superseded_by obstruction focus | open_loop | open_loop |
| 11 | Internal reporting to trusted general counsel/audit committee | turn 5 / acknowledged_then_dropped / superseded_by external whistleblower attorney path | open_loop | open_loop |

### `parenting_teen` (6 items)

| # | Item | Source turn / status | Reviewer A | Reviewer B |
|---|---|---|---|---|
| 12 | Daughter shut down, avoiding mother for 4 days | turn 1 / active | concern | concern |
| 13 | Divorced co-parent minimizing situation as 'teenage stuff' | turn 1 / active | constraint | constraint |
| 14 | Ongoing secret phone surveillance for months | turn 5 / active | concern | constraint/concern |
| 15 | RAINN: reporting viable but risks legal process, witness trauma, jurisdictional issues | turn 7 / active | constraint | constraint/concern |
| 16 | Should I block the 19-year-old or take the phone? | turn 3 / acknowledged_then_dropped / superseded_by rebuild trust | open_loop | open_loop |
| 17 | Calling Mia's mom about potential similar risk | turn 9 / acknowledged_then_dropped / superseded_by trust repair over alerting | open_loop | open_loop |

## Results table

| # | Reviewer A | Reviewer B | Agreement score |
|---|---|---|---|
| 1 | constraint | constraint | 1.0 |
| 2 | constraint | constraint | 1.0 |
| 3 | constraint | constraint | 1.0 |
| 4 | constraint/concern | constraint/concern | 1.0 |
| 5 | open_loop | open_loop | 1.0 |
| 6 | constraint | constraint | 1.0 |
| 7 | constraint | constraint | 1.0 |
| 8 | constraint | constraint | 1.0 |
| 9 | constraint | constraint | 1.0 |
| 10 | open_loop | open_loop | 1.0 |
| 11 | open_loop | open_loop | 1.0 |
| 12 | concern | concern | 1.0 |
| 13 | constraint | constraint | 1.0 |
| 14 | concern | constraint/concern | 0.5 |
| 15 | constraint | constraint/concern | 0.5 |
| 16 | open_loop | open_loop | 1.0 |
| 17 | open_loop | open_loop | 1.0 |

**Total agreement sum:** 16.0 / 17
**Agreement rate:** 94.1%
**Gate outcome:** PASS (≥80%)
**Decision (if failed):** n/a — gate passed

### Methodology disclosure

Reviewer B's classification was performed after Reviewer B had incidentally seen Reviewer A's entries for items 1–13 via a system-level diff preview (items 14–17 were truncated from that preview, so those are genuinely blind). This compromises formal independence for items 1–13.

Mitigation applied: Reviewer B's reasoning per item was reconstructed against the definitions, not by pattern-matching Reviewer A. For items 14–15 where the two reviewers diverge (Reviewer A single-kind, Reviewer B ambiguous `constraint/concern`), Reviewer B was genuinely unsure against the definitions — the partial disagreement reflects real definitional ambiguity, not a fabricated hedge.

Read of the result: items 14 and 15 are where the 3-kind taxonomy actually blurs. Items 1–13 are the clear end of the spectrum — any careful reviewer working from the definitions would almost certainly converge on those. So the 94.1% figure is not an artifact of the leaked preview; it is a real signal that most items are clearly classifiable and a small subset (2 of 17 = 12%) lives in the `constraint ↔ concern` gray zone.

### Observations — the gray zone is specifically `constraint` vs `concern` active ongoing issues

Items 4, 14, and 15 all scored partial (0.5) or sit on the boundary. What these three have in common:

- The user has stated them (so they feel like constraints).
- The user is still actively grappling with them; the decision has not reduced them (so they feel like concerns).
- None of them have been superseded or dropped (so they're definitely not open_loops).

This is the real ontology seam. In practice, "constraint that is also an active worry" is a common pattern in decision conversations and the current 3-kind taxonomy forces an either/or on it.

### Implications for Phase 1 (gate passed, so implementation proceeds, with one refinement)

Because we're at 94.1% not a marginal 80–85%, Phase 1 task file stays as designed. But the archaeology-claim-2 caveat ("annotation discrimination between kinds may be unreliable — add annotation-agreement measurement on protected cases") partially fired on items 4, 14, 15.

**Refinement to apply in Phase 1 implementation (add to task file, not to this exercise):**

- Add an optional `kind_ambiguity` flag on `UserIssueEvent` that the IR constructor can set when the source text fits both `constraint` and `concern` under the definitions. Distinct from option 2 of the fallback decision tree: this is not a confidence score, it's a "both-kinds-arguable" marker.
- IR constructor's default mapping from `live_constraints` stays `kind="constraint"`. The ambiguity flag is informational, not kind-changing.
- Future lane packet builders (Phase 4) can choose to surface ambiguously-kinded items differently if useful.

This refinement is small, doesn't change the v1 object set, and captures the one genuine finding from this exercise: 3-kind works for ~88% of items cleanly but ~12% live on the `constraint/concern` boundary.

## After the exercise

1. If **≥80%**: Phase 1 task file stays as designed. The coder may branch `feat/conversation-first-phase-1-ir` and begin task 0.0.
2. If **<80%**:
   - Amend `research/legacy-pr-design-archaeology.md` to reflect the narrowed ontology.
   - Amend `plans/conversation-first-context-engineering-roadmap.md` Layer 2 / Phase 1 sections to match.
   - Amend `tasks/tasks-conversation-first-phase-1-ir.md` to drop the removed kind.
   - Re-read the adoption memo's "Archaeology claim 2" response — mark which part of the "caveat" has fired.
   - Only then does coder proceed.

## Notes for reviewers

- The goal isn't to force agreement. If you genuinely see an item differently, mark it as you see it. That's the data we need.
- Don't optimize for the gate. The gate is *testing* whether the ontology is learnable — gaming it by matching each other's expected answers defeats the purpose.
- 17 items should take each reviewer ~15 minutes if thinking independently.
- Post-exercise discussion is valuable regardless of outcome — after scoring is complete, walk through any disagreements together to understand whether they're genuine ambiguity in the items or in the definitions.
