# PR77 v39 Incentive Boundary Enrichment Report

Date: 2026-05-08

## Scope

PR77 continues the dormant knowledge-substrate enrichment sequence. It does not wire affordances into `/lolla`, runtime lanes, packet rendering, prompts, Observatory output, or product behavior.

The review focused on incentive, information, signaling, and strategic-interaction records where the source corpus may contain transaction-distinct material that v38 compressed too tightly.

Reviewed records:

- `information-asymmetry`
- `moral-hazard`
- `game-theory-payoffs`
- `prisoners-dilemma`
- `signaling`
- adjacent PASS checks from `incentives`, `adverse-selection`, `principal-agent-problem`, `nash-equilibrium`, and `price-discrimination`

## Verdict

PASS as dormant reviewed substrate.

The ring adds two positive affordances, two absence guards, and three hardening edits. It deliberately avoids turning every strategic or persuasion passage into a new affordance.

Compiled v39:

- Records: 222
- Affordances: 273
- Absence records: 514
- Schema failures: 0
- Source quote rejections: 0
- Status: `draft_review_only`

## What Changed

### Positive Affordance Splits

`information-asymmetry.knowledge-authority-risk-map`

This split was accepted because the source supports a distinct receiver transaction: map who knows, who bears risk, who approves, and whether apparent preference conflict is actually unequal fact sets or selective disclosure.

It is not an exploitative information-asymmetry tactic. The affordance explicitly rejects FUD, guru-positioning, and opportunistic knowledge-gap leverage. It only activates when the downstream decision changes after mapping knowledge, risk, authority, fact sets, or disclosure.

Key source support:

- `**Social cartography** (drawing a mental map of key players) ensures the strategist has a complete picture of stakeholder biases and preferences, preventing effort from being wasted on non-decision-makers.`
- `Works when the practical decision is whether to add diligence, require disclosure, redesign incentives, use signaling, or map the real decision-makers before committing.`
- `Best when the people who know the most, the people who bear the risk, and the people who approve the decision are not the same actors.`
- `Works when conflict is being misread as preference clash even though the real issue is that different parties are acting from different fact sets, hidden assumptions, or selective disclosure.`

New guard:

- `known-facts-without-authority-or-incentive-as-information-gap`

This blocks the model when the real blocker is incentive misalignment, governance, or authority rather than missing information.

`game-theory-payoffs.credible-sequencing-commitment-device`

This split was accepted because the source supports a transaction separate from static payoff mapping. The existing card maps players, moves, and counterparty responses. The new card asks whether the decision should change the game through sequencing, reveal/conceal moves, commitments, threats, promises, or forcing moves, and then tests the credibility device.

Key source support:

- `Works when the real leverage is not only choosing within a fixed game, but altering incentives, expectations, or credible constraints so the other side changes behavior.`
- `Works when the decision depends on whether to move first, wait, reveal information, conceal information, or create a forcing move that shifts the opponent into a worse response set.`
- `Actions intended to change the game (commitments, threats, promises) must be credible.`
- `This involves developing devices that make it in your interest to carry them out in the end, allowing you to change the game to your advantage.`

The existing absence guard `commitment-threat-or-promise-without-credibility-device` remains active. It now works as the misuse boundary for the new positive affordance.

### Hardening Without New Positive Cards

`signaling.costly-proof-of-intent-test`

No second signaling affordance was added. The source has broader communication material, but action-legible communication is likely better owned by communication, persuasion, or strategy-translation records. For this ring, the safer move was to harden the existing costly-proof card around low-cost commercial signals.

New guard:

- `low-cost-commercial-signal-as-actual-buying-intent`

This blocks references, pilots, diligence speed, sponsor enthusiasm, introductions, compliance-process access, and polished diligence from being treated as proof of authority, buying intent, or willingness to bear cost.

`prisoners-dilemma.defection-incentive-reframe-test`

No second prisoner’s-dilemma affordance was added. The source’s framing material is important, but it improves the current defection-incentive card rather than creating a separate runtime transaction.

Hardening added:

- `test-competitive-frame-before-defection-diagnosis`

The receiver must now test whether a competitive frame is being imposed, whether a cooperative frame is available, and whether negotiation, reputation, repeated interaction, norms, shared identity, or process repair change the payoff diagnosis.

`moral-hazard.proxy-hidden-effort-with-noisy-outcomes`

No standalone short-termism affordance was added. The record already had an absence saying short-termism is a duplicate of existing moral-hazard mechanisms. PR77 strengthens the existing proxy card instead.

Hardening added:

- `check-delayed-risk-externalization`

The receiver must test whether immediate observable outcome metrics create short-term gains by externalizing long-term stability, ethical, or systemic risk.

## PASS / No Change

`incentives`

Current two affordances are already clean: payoff-field diagnosis and task-fit reward redesign. No extra split is justified without duplicating moral hazard, principal-agent, or communication/persuasion records.

`adverse-selection`

Do not expand. The source remains intentionally narrow and partly source-thin. Hidden-type self-selection before commitment is the right boundary.

`principal-agent-problem`

No split in this ring. The current medium-confidence record already carries delegated alignment with clear absences around dashboard compliance, wicked-problem routing, bad-faith overreach, and micromanagement.

`nash-equilibrium`

No split. Stable best-response mapping, reachability, focal/default convention, and stability-versus-goodness remain one coherent transaction.

`price-discrimination`

No expansion. Keep weak-support posture. Buyer psychology, FUD, and formal economics material should not be promoted without stronger source support and trust/arbitrage boundaries.

## Why This Is Not Bloat

The positive additions passed the strict split test:

- They have different activation conditions.
- They require different evidence.
- They ask the receiver to perform a different treatment.
- They have different misuse guards.
- They could produce different use/reject/defer outcomes in a future packet ledger.

The rejected additions were handled as treatment hardening or absence guards when the source material sharpened an existing card but did not justify a new card identity.

## Runtime Safety

v39 remains dormant reviewed substrate.

The PR77 test suite asserts that `affordances_v39` and `model_affordances_v39` are not imported by the live runtime paths checked by previous PR rings:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

No runtime pickup is introduced here.

## Verification

Focused verification should include:

```bash
pytest tests/test_pr77_v39_incentive_boundary_enrichment.py tests/test_pr76_v38_risk_boundary_hardening.py tests/test_model_affordance_compiler.py
rg -n "affordances_v39|model_affordances_v39" engine scripts tests -g '*.py'
git diff --check
jq '.compile_metadata.validation' data/compiled/model_affordances/affordances_v39.json
```

Expected compiled metadata:

```json
{
  "schema_validation_failure_count": 0,
  "source_hash_failure_count": 0,
  "source_quote_rejection_count": 0
}
```

## Next Ring Candidates

The systems / complexity / leverage audit found likely future work, but it should be a separate PR ring:

- split `constraints` boundary-setting from constraint-validity stress testing;
- split `leverage-points` minimal fact threshold from focus-check and execution resistance;
- harden feedback loops against instrumentation theater;
- harden delays against delay-as-excuse;
- add complexity-family guards against abstract complexity without transmission path, monitor, or checkpoint.

That work should remain dormant and source-custodied, following the same strict transaction-distinct standard.
