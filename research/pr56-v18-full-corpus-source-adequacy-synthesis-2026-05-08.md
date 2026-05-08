# PR56 v18 Full-Corpus Source Adequacy Synthesis

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: full-corpus source-read synthesis; no affordance record rewrites; no runtime pickup

## Scope

This audit treats `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` as the canonical source corpus.

Coverage reviewed:

- canonical Markdown files: `222`;
- compiled v18 model records: `222`;
- local `data/model_sources/` files: `222`;
- canonical-to-local byte hash mismatch: `0`;
- v18 source metadata hash mismatch: `0`;
- source-to-individual-record-to-compiled-record drift found during tranche review: `0`.

The full-corpus pass read all canonical Markdown files and compared them to the corresponding individual `data/model_affordances/**/{model_id}.json` records and `data/compiled/model_affordances/affordances_v18.json`.

This means PR56 is no longer asking whether the corpus was physically present. It was. The question is semantic:

> Did v18 preserve source-supported cognition at the right runtime transaction granularity?

## Consolidation Spot Check

After the full-corpus tranche reviews, the consolidation pass re-read several high-impact controls directly:

- `commitment-bias`
  - Source supports both constructive commitment design and escalation-stop discipline.
  - v18 acknowledges under-follow-through, but the extracted transaction is still mainly recommitment / stop-rule review.
  - Keep as a positive split proof candidate.
- `redundancy`
  - Source explicitly separates systemic backup/resilience from cognitive redundancy for retention and communication clarity.
  - v18 mostly operationalizes single-point-failure backup plus drag checks.
  - Keep as a positive split proof candidate.
- `switching-costs`
  - Source supports both platform exit / reversibility decay and broader adoption lag / incumbent loyalty / lowering switching friction.
  - v18 strongly captures platform exit governance.
  - Keep as a positive split proof candidate.
- `chain-of-thought`
  - Source is rich in decomposition, prompting, business structure, and warning material.
  - v18 correctly keeps one review-only decomposition affordance and blocks transcript-as-truth overclaiming.
  - Keep as absence/misuse enrichment, not a positive split by default.

## Executive Verdict

v18 passes as dormant reviewed substrate, but should be revised before runtime usefulness testing.

The important finding is not "one affordance is bad." The important finding is:

> One affordance is usually correct when the source has one dominant receiver transaction, but a small set of records compressed different downstream actions into one card.

Counts from v18:

| Shape | Count |
| --- | ---: |
| Model records | 222 |
| Affordances | 258 |
| Absence records | 429 |
| One-affordance records | 194 |
| Two-affordance records | 21 |
| Three-affordance records | 6 |
| Four-affordance records | 1 |
| Zero-absence records | 11 |
| Supported records | 220 |
| Weak-support records | 2 |
| High-confidence affordances | 251 |
| Medium-confidence affordances | 7 |

Full-corpus read result:

- Most one-affordance records are source-faithful compressed transactions.
- High source-reference count usually means many passages support one transaction, not that the record is under-extracted.
- Weak/medium records should remain cautious; symmetry is not a reason to expand them.
- The strongest remaining quality gap is targeted transaction loss in selected records.
- The second strongest gap is absence/guard visibility, especially where the source contains a strong warning but not a separate positive runtime action.
- Packet flattening remains a separate PR55 blocker even if source adequacy improves.

## What Happened With The One-Affordance Rule

The one-affordance discipline appears to have functioned as coverage-phase medicine:

- it prevented schema filling;
- it reduced noisy over-extraction;
- it kept weak sources from being upgraded into confident doctrine;
- it forced each record to name a concrete operational use;
- it made v18 complete without turning it into a pile of decorative model language.

But after coverage is complete, the same discipline becomes risky when a source contains multiple source-backed moves that would lead a receiver to do different things.

The audit criterion is therefore not:

> Does the source contain more nuance?

Most sources do.

The audit criterion is:

> Would separating this material change downstream use, reject, defer, merge, absence-block, evidence-gate, treatment, misuse-guard, or final-answer behavior?

Only that standard justifies positive expansion.

## Firm Positive Split Review Candidates

These records have the strongest evidence of transaction-distinct cognition being compressed into one v18 card. This is not approval to edit them immediately. It is a PR57 proof queue.

| Model | v18 mainly preserves | Source-backed missing transaction | Why it matters downstream |
| --- | --- | --- | --- |
| `category-decisions` | category validation / precommitment | grouping, summarizing, and synthesis into a "so what" insight | listing categories is not the same as using categories to derive the logical point |
| `power-dynamics` | bilateral outside options and leverage inversion | multi-party weakest-link dependency | the constrained actor can set the floor for the whole negotiation, which is not the same as mapping each party's fallback |
| `mental-models-of-reality` | compare a map to territory | infer/adapt to another actor's mental model | stakeholder, sales, persona, or counterpart reasoning needs a different evidence gate than testing one's own map |
| `critical-thinking` | claim/evidence/assumption check | problem-structure discipline: disaggregation, hypothesis, WHTB, MECE | if not owned by separate cards, the method of structuring inquiry is lost behind generic evidence checking |
| `metacognitive-questioning` | next-question gate | ask-how-not-what expert elicitation, possibly variables -> next question -> consolidation loop | eliciting process/criteria/skills from an expert is not just asking the next discriminating question |
| `commitment-bias` | stop-rule / recommitment against escalation | constructive commitment architecture for follow-through | preventing bad escalation and designing useful commitment solve opposite problems |
| `conjunction-fallacy` | sequential success gates | disjunctive failure-risk aggregation | "all steps must succeed" and "any path can fail" produce different risk treatment |
| `emotional-intelligence` | stakeholder emotional adoption | self-awareness / self-management under emotional hijack | a user's own emotional state can be the decision hazard, not only audience adoption |
| `evolutionary-pressure` | selection-environment diagnosis | threat-response communication packaging | communicating under hot cognition or threat response is a different treatment from analyzing selection pressure |
| `feedback-loops` | measurement-to-action closure | reinforcing vs balancing loop polarity | the receiver may need to dampen, stabilize, amplify, or watch runaway dynamics differently |
| `international-negotiation-and-diplomacy-models` | durable settlement mapping | adversarial game/simulation, attack-defense teams, minmax/maxmin countermove reasoning | adversarial strategy review has a different treatment than stakeholder settlement design |
| `lock-in` | false reversibility / exit hardening | productive lock-in via standardization, trust, and compounding stability | sometimes the right action is to deliberately standardize, not unwind |
| `mental-simulation` | assumption-bound scenario rehearsal | skill rehearsal / anticipatory practice | training responses is not the same as evaluating decision scenarios |
| `path-dependence` | installed dependency unwind | cognitive, habit, or schema reproduction | reframing/habit redesign differs from dependency pricing or migration planning |
| `redundancy` | backup path / single-point-failure resilience | cognitive redundancy for retention, clarity, and communication reinforcement | reinforcement in learning/communication can be useful, not merely wasteful duplication |
| `switching-costs` | exit and reversibility decay | adoption friction / incumbent loyalty / lowering or exploiting switching friction | competitive adoption cases need different action than platform exit planning |

## Split Watch, Not Automatic Split

These records need proof review, but the current evidence suggests absence enrichment or packet treatment may be better than adding another positive affordance.

| Model | Current read |
| --- | --- |
| `theory-of-constraints` | stakeholder / decision-right bottlenecks may be a future split, but current two-affordance structure already carries constraint-first action and constraint-shift cadence; treat as watch plus absence review |
| `problem-framing-and-reframing` | organizational/social-context framing may need an absence or a fourth affordance; prove whether it changes receiver action beyond current frame comparison |
| `baseline-establishment` | goal-solution blur is a real loss, but likely a guard/absence unless a separate baseline-setting transaction is proven |
| `chain-of-thought` | early pilot marked split_candidate; full read downgraded it to absence/misuse enrichment because extra positive affordances risk promoting reasoning traces as proof |

## Absence And Guard Enrichment Queue

These are not primarily missing positive affordances. They are source-backed cautions that should be visible enough to affect use/reject/defer decisions.

| Model | Missing or under-visible guard |
| --- | --- |
| `active-listening` | do not probe vulnerability and then emotionally abandon or fail to act on what was disclosed |
| `agile-methodologies` | do not use agile iteration to deny fixed external commitments, interfaces, or regulatory constraints |
| `anchoring` | make system-risk / conjunctive-disjunctive stress boundaries explicit as non-anchor or route-to-risk material |
| `baseline-establishment` | avoid polluting baseline/goals with solution or execution thinking |
| `chain-of-thought` | no step-by-step prompting as runtime policy, no user-facing chain disclosure as evidence, no reasoning chain as proof, no structured reasoning without implementation path |
| `chaos-theory` | do not impose a preferred will on the system while ignoring observed system behavior |
| `constructive-feedback-models` | preserve machine/process-level diagnosis so feedback does not collapse into person-blame |
| `elasticity` | reject or defer low-quality, irrelevant, or skewing retrieved snippets |
| `game-theory-payoffs` | threats, promises, and commitments require credibility devices |
| `internal-locus-of-control` | high agency can become arrogance, selective perception, or illusion of control |
| `meta-cognitive-reflection` | rationalization dressed as reflection, plus cognitive-cost / quiet-window limits |
| `multi-criteria-decision-analysis` | post-outcome process review and communication simplification deserve explicit absence or treatment notes |
| `problem-framing-and-reframing` | organizational, political, fear, management-style, or social-system context should not be hidden by technical/content framing |
| `theory-of-constraints` | false bottleneck certainty, visible-work optimization, and stakeholder/ownership constraints need stronger absence pressure |

If a future PR chooses not to split a firm split candidate, it should usually add absence or guard material explaining why the omitted cluster is not being promoted.

## Weak-Support And Source-Thin Records

The audit confirms several records should not be made richer merely for symmetry.

| Model | Decision |
| --- | --- |
| `price-discrimination` | weak support confirmed; do not upgrade into full pricing doctrine |
| `devops-and-continuous-integration` | weak support confirmed; do not import external CI/CD doctrine |
| `markov-chains` | medium/weak support confirmed; state-transition logic is present, formal Markov doctrine is not |
| `six-thinking-hats` | weak support confirmed; role/mode separation is present, named framework support is limited |
| `adverse-selection` | weak support confirmed; narrow hidden-type/self-selection support only |
| `batna` | source too thin for textbook BATNA; current narrow walk-away support should remain cautious |
| `comparative-political-systems-analysis` | weak/proxy support; current narrow institutional-comparison shape is appropriate |
| `cultural-dimensions-theory` | weak/proxy support; keep probabilistic and non-deterministic |
| `tier-2-high-value` | synthesized label; keep as narrow pruning-to-leverage card |

This matters because "do not upgrade weak cards" is part of not dumbing down the corpus. Weakness should remain visible instead of being cosmetically filled.

## Broad And Meta Cards

Broad cards are mostly not under-extracted. Their danger is packet behavior.

Examples:

- `systems-thinking`
- `latticework-of-mental-models`
- `cognitive-biases`
- `reasoning-mode-router`
- `mental-models-of-reality`
- `critical-thinking`
- `meta-cognitive-reflection`

The audit found that many broad cards preserve the source as a compact runtime move. The failure mode is not semantic absence alone; it is that the packet can make broad model language feel like judgment.

PR55 packet work still needs:

- grouped per-affordance identity;
- confidence visibility;
- weak-support warnings;
- absence visibility;
- broad/meta caps;
- explicit receiver freedom to reject or defer cards.

## Reconciled Changes From The Early Pilot

The early PR56 pilot was intentionally provisional. The full-corpus read changes several labels:

- `chain-of-thought` moves from provisional `split_candidate` to `needs_absence_enrichment`.
- `systems-thinking`, `confidence-calibration`, and `inversion` look source-adequate as compressed multi-affordance records; their risk is packet display, zero-absence posture, and rewrite gating, not more positive extraction by default.
- `theory-of-constraints` remains a split watch item, not an automatic third affordance.
- High-source-ref one-affordance records such as `antifragility`, `base-rates`, `expected-value`, `flow`, `johari-window`, `pareto-principle`, `resilience`, and `risk-assessment` mostly pass as complete compressed transactions.

## Decision

Do not run live usefulness testing yet.

Do not start broad v19 enrichment.

Do start a targeted v19 preparation PR only after PR56 is merged, using the split and guard queues above.

The right next sequence is:

1. Merge PR56 as audit-only.
2. Open PR57 as targeted v19 candidate proof.
3. For each firm split candidate, require per-affordance proof: `use_when`, `case_evidence_needed`, `do_not_use_when`, treatment requirement, misuse guard, source refs, and receiver action difference.
4. Prefer absence enrichment over positive affordance expansion when the problem is overclaim or misuse risk.
5. Keep v19 dormant and `draft_review_only`.
6. Return to PR55 packet-shape blockers before any `/lolla` runtime pickup.

## Bottom Line

The one-affordance coverage mode did not dumb down most of the corpus. It kept the substrate disciplined.

But it did leave some knowledge on the table in specific places where the source supports a different downstream transaction. That is the sweet spot for the next work: not "more affordances," but fewer, sharper, source-proven expansions where the receiver would actually behave differently.
