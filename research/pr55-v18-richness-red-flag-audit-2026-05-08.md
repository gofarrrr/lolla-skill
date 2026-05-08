# PR55 v18 Richness Red-Flag Audit

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Status: review-only audit artifact

Scope: `data/compiled/model_affordances/affordances_v18.json`, selected source Markdown files in `data/model_sources/`, and prior extraction/review notes.

## Verdict

`affordances_v18.json` should pass as dormant reviewed substrate, but it should not be treated as proof that every model has exactly the right runtime affordance granularity.

The main finding is selective:

- the one-affordance operating rule was a useful coverage-phase discipline;
- it was not evidence that every source contains only one runtime-relevant move;
- most one-affordance records are probably fine as compact operational cards;
- a small number of broad, meta, or high-source-reference records should be red-flagged for source recheck or packet hardening before live pickup.

This file is intentionally not a v19 rewrite plan. It is a red-flag map.

## Why This Audit Exists

The extraction doctrine repeatedly told reviewers to prefer one strong affordance over several weak ones. That was good medicine during the coverage phase. It reduced schema filling, over-interpretation, and completeness theater.

The danger now is different. Once every runtime model has a reviewed card, compression can become invisible. A card can be source-backed and still too coarse for downstream use/reject/defer decisions.

The test is not:

> Does the source contain more interesting material?

Most sources do.

The test is:

> Would separating the material change the downstream card transaction?

If yes, the record may need split review or grouped affordance identity. If no, keep it compressed.

## Red-Flag Labels

Use these labels for PR55 review only:

- `compression_ok`: the current record appears to express one dominant operational card well enough.
- `split_candidate`: source material may support multiple downstream-relevant affordances with distinct activation/evidence/guard/treatment behavior.
- `too_broad_for_runtime`: the card is broad enough to sound wise under many cases and needs stricter cap/label/display treatment.
- `grouped_affordance_required`: the model has multiple affordances or mixed blockers that must stay grouped by affordance ID before receiver use.
- `needs_source_recheck`: a reviewer should reread the source before deciding whether to split, tighten, or leave as-is.
- `display_hardening_needed`: the record may be fine, but the packet renderer/handoff can hide important cautionary material.
- `absence_first_handoff_required`: absence or do-not-use records may be more important than the positive affordance in runtime handoff.
- `runtime_do_not_promote_yet`: the card should stay dormant until the receiver grammar and packet shape are hardened.

## Strict Split Criteria

A record should become a `split_candidate` only if the source supports multiple operational moves with materially different:

- activation conditions;
- evidence required;
- do-not-use boundaries;
- misuse guards;
- treatment requirements;
- confidence level;
- use/reject/defer outcome.

Do not split merely because the source has nuance. Split only when the downstream receiver would need separate identities to decide what to use, reject, defer, or merge.

## Sample Findings

| Model | v18 shape | Labels | Audit read |
| --- | ---: | --- | --- |
| `systems-thinking` | 4 affordances, 0 absences | `too_broad_for_runtime`, `grouped_affordance_required`, `runtime_do_not_promote_yet` | This is the clearest broad-card risk. It already has multiple affordances, but no absence records, and the renderer only exposes one detail item per field. The card can sound globally applicable unless packet display makes boundaries and transaction identity visible. |
| `confidence-calibration` | 3 affordances, 0 absences | `needs_source_recheck`, `too_broad_for_runtime`, `display_hardening_needed` | Prior quality review already flagged `confidence-calibration.method-first-self-interrogation`. Because confidence language can easily become performance theater, this needs receiver-side caution and probably absence visibility. |
| `inversion` | 3 affordances, 0 absences | `needs_source_recheck`, `display_hardening_needed` | Prior quality review flagged `inversion.obstacle-removal-before-added-force`. The record may be rich enough, but zero absences means live use could over-authorize a familiar favorite model. |
| `chain-of-thought` | 1 affordance, 2 absences | `split_candidate`, `absence_first_handoff_required` | Source material includes auditable decomposition, anti-rationalization cautions, implementation-gap cautions, analysis-paralysis cautions, and map/territory warnings. These may not be the same runtime move. The strongest action is not immediate splitting; it is a source recheck against transaction behavior. |
| `latticework-of-mental-models` | 1 affordance, 2 absences | `compression_ok`, `too_broad_for_runtime`, `absence_first_handoff_required` | The current card's core move, cross-checking causal layers, appears coherent. But the source also warns about decorative model naming. Runtime display must prevent "model pile" behavior. |
| `mental-models-of-reality` | 1 affordance, 2 absences | `compression_ok`, `too_broad_for_runtime` | Likely acceptable as one high-level modeling card if kept away from automatic priority. It needs broad/meta cap treatment. |
| `meta-cognitive-reflection` | 1 affordance, 2 absences | `compression_ok`, `absence_first_handoff_required` | The positive card is plausible, but the anti-rumination/anti-self-soothing absence is probably the higher-value guard. |
| `reasoning-mode-router` | 1 affordance, 2 absences | `runtime_do_not_promote_yet`, `absence_first_handoff_required` | This card is especially sensitive because it talks about routing reasoning modes. It must not be allowed to masquerade as deterministic mode selection. Use only as reviewed handoff material until runtime grammar is explicit. |
| `algorithmic-thinking` | 1 affordance, 2 absences | `compression_ok`, `display_hardening_needed` | The compact card captures repeatable handoff design. The source has several pitfalls, but they mostly reinforce the same guard: avoid rigid procedure/proxy lock-in. |
| `trade-offs` | 1 affordance, 1 absence | `compression_ok` | This appears to be a good compact card. It is operationally narrow enough for packet use if absence remains visible. |
| `antifragility` | 1 affordance, 3 absences, 18 source refs | `needs_source_recheck`, `display_hardening_needed` | A one-affordance record with unusually many source references and three absences may be fine, but it deserves review because high source-ref density can hide compression. |
| `sunk-cost-fallacy` | 1 affordance, 0 absences, 18 source refs | `needs_source_recheck` | High source-ref count plus zero absences is a red flag. It may still be correct if the model is narrow, but runtime handoff should not assume absence discipline exists. |
| `base-rates` | 1 affordance, 1 absence, 16 source refs | `compression_ok` | Despite many source refs, this looks like a coherent single operational card: reference-class correction. |
| `expected-value` | 1 affordance, 1 absence, 16 source refs | `compression_ok` | Likely coherent as one card if do-not-use boundaries remain visible. |

## Broad/Meta Watchlist

These records deserve cap and display attention because they can sound useful in almost any reasoning task:

- `systems-thinking`
- `latticework-of-mental-models`
- `chain-of-thought`
- `meta-cognitive-reflection`
- `mental-models-of-reality`
- `reasoning-mode-router`
- `system-1`
- `system-2`
- `complexity-bias-resistance`
- `logical-fallacies`
- `circle-of-competence`
- `intellectual-humility`

The issue is not that these cards are bad. The issue is that broad language can crowd out narrower, case-specific cards under packet caps.

## Under-Extraction Risk

The under-extraction concern is real but not universal.

The strongest evidence is the historical shift:

- the pilot used 1-4 affordances per model;
- early reviewed batches accepted uneven affordance counts;
- later controlled batches moved toward "one compact operational affordance" for graph-only coverage;
- tests for later batches often enforced exactly one affordance and two absences.

That shift makes sense for coverage. It should not become permanent doctrine without a transaction-level audit.

## Over-Extraction Risk

The opposite risk is equally real.

If PR55 turns into "split every rich source," it will recreate extraction drift in a subtler form. The artifact would become larger, more authoritative-looking, and probably less useful.

The right posture is selective pressure:

- preserve compact cards where one operational bite is enough;
- split only where separate downstream decisions require separate affordance identities;
- prioritize packet shape before adding more records;
- keep all changes dormant until receiver behavior is tested.

## Working Conclusion

The richer question after v18 is not "how many affordances can we extract?"

It is:

> Which affordances need their own transaction identity so the receiver can use, reject, defer, merge, or block them without flattening evidence and guards?

For PR55, the highest-value output is a red-flag list and packet-shape decision, not a new extraction wave.
