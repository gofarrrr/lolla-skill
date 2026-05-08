# PR56 v18 Source Adequacy Audit Brief

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: review-only knowledge-base audit; no runtime, prompt, memo, Observatory, `/lolla`, or user-facing behavior changed

Decision label: `v18_source_adequacy_before_runtime_testing`

## Verdict

PR56 should prove extraction sufficiency before any system usefulness test.

v18 completed coverage. PR55 showed pickup risks. PR56 asks the sharper knowledge-base question:

> Did each v18 record capture the source corpus at the right operational granularity, or did the one-affordance coverage discipline hide transaction-distinct cognition?

Current status:

- `PASS` for completed dormant coverage.
- `REVISE` for source adequacy before runtime usefulness testing.
- `BLOCK` live `/lolla` testing until high-risk records are classified as complete, split candidates, source-thin, or needing targeted enrichment.

## Canonical Corpus Custody

PR56 treats `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` as the canonical source corpus.

Deterministic custody check found:

- canonical Markdown files: `222`;
- local `data/model_sources/` Markdown files: `222`;
- v18 compiled source metadata entries: `222`;
- v18 model records: `222`;
- canonical/local filename mismatch: `0`;
- canonical/local SHA-256 mismatch: `0`;
- v18 metadata hash mismatch against canonical files: `0`.

Detailed custody artifact:

- `research/pr56-canonical-corpus-custody-check-2026-05-08.md`

This means the local source files used by v18 are byte-identical to the canonical corpus. The remaining audit question is semantic adequacy, not source custody.

## Why This Comes Before System Testing

Testing v18 inside the system now would mix too many unknowns:

- bad nomination;
- bad packet compression;
- under-extracted affordance;
- over-extracted broad card;
- hidden absence;
- weak-support card presented too strongly;
- broad/meta card crowding out narrow cards;
- receiver ignoring a card correctly;
- receiver ignoring a card lazily.

Before testing usefulness, we need to know whether the substrate itself is worthy of being tested.

## Operating Standard

Do not optimize for "as much as possible from the corpus."

Optimize for:

> as much as the source supports and as much as the downstream transaction needs.

The extraction unit is not an interesting idea. The extraction unit is a different reasoning transaction.

A source-supported cluster deserves its own affordance only if separating it would change downstream:

- use;
- rejection;
- deferral;
- merge behavior;
- blocking absence;
- evidence gate;
- treatment requirement;
- misuse guard;
- final-answer delta.

## PR56 Outputs

This audit adds:

- `scripts/audit_v18_source_adequacy_queue.py`
  - deterministic risk-queue generator for v18 adequacy review.
- `research/pr56-canonical-corpus-custody-check-2026-05-08.md`
  - proof that canonical Markdown, local source copy, and v18 source metadata align.
- `research/pr56-v18-full-corpus-source-adequacy-synthesis-2026-05-08.md`
  - full-corpus source-read synthesis across all 222 records.
- `research/pr56-v18-targeted-v19-candidate-queue-2026-05-08.md`
  - proof queue for later targeted v19 enrichment.
- `research/pr56-v18-source-adequacy-risk-queue-2026-05-08.md`
  - P0/P1/P2 prioritization for human source reads.
- `research/pr56-v18-granularity-decision-rubric-2026-05-08.md`
  - rules for deciding complete-as-compressed vs split/enrich/rewrite.
- `research/pr56-v18-source-adequacy-ledger-pilot-2026-05-08.md`
  - first source-read pilot across P0/P1/high-signal records.

## Deterministic Queue Findings

The queue is not a quality judgment. It is a triage map.

Priority distribution:

| Priority | Count |
| --- | ---: |
| `P0` | 4 |
| `P1` | 6 |
| `P2` | 43 |
| `P3` | 169 |

Flag distribution:

| Flag | Count |
| --- | ---: |
| `late_controlled_one_affordance` | 100 |
| `large_source_file` | 29 |
| `multi_affordance_grouping_needed` | 28 |
| `broad_meta_model` | 15 |
| `one_affordance_high_source_refs` | 14 |
| `absence_heavy` | 13 |
| `zero_absence_records` | 11 |
| `medium_confidence` | 7 |
| `do_not_promote_without_rewrite_review` | 3 |
| `weak_support` | 2 |

P0 records:

- `systems-thinking`
- `confidence-calibration`
- `inversion`
- `price-discrimination`

P1 records:

- `devops-and-continuous-integration`
- `theory-of-constraints`
- `lindy-effect`
- `premortem`
- `principal-agent-problem`
- `sunk-cost-fallacy`

These are the first records to review because they combine weak support, zero absence, broad/meta surface, do-not-promote flags, or one-affordance compression pressure.

## Pilot Ledger Findings

The first manual source-read pilot found a mixed picture:

- Some records really are well-compressed:
  - `base-rates`
  - `antifragility`
  - `sunk-cost-fallacy`
  - `premortem`
  - `lindy-effect`
- Some records are not under-extracted but need absence or display hardening:
  - `systems-thinking`
  - `confidence-calibration`
  - `inversion`
  - `theory-of-constraints`
- Some weak-support records should not be expanded just because the source is noisy:
  - `price-discrimination`
  - `devops-and-continuous-integration`
- `chain-of-thought` is the strongest provisional split candidate because source material may separate auditable decomposition from anti-rationalization / trace-as-proof controls.
- `reasoning-mode-router` is probably complete-as-compressed, but should remain runtime-sensitive because it can masquerade as deterministic mode selection.

This means one-affordance dominance is not automatically a failure. But it is also not automatically safe.

## Full-Corpus Audit Refinement

After the pilot, PR56 expanded to a full-corpus source-read pass across all 222 canonical Markdown files.

The full pass refined the pilot in important ways:

- `chain-of-thought` should not be treated as a positive split by default. The stronger action is absence/misuse enrichment so the system does not promote step-by-step traces, user-facing reasoning chains, or reasoning-as-proof theater.
- `systems-thinking`, `confidence-calibration`, and `inversion` look source-adequate as compressed multi-affordance records. Their risk is packet display, zero-absence posture, and rewrite gating, not more positive extraction by default.
- High-source-ref one-affordance records are usually not under-extracted. In many cases, many source passages support one operational transaction.
- Weak/proxy records should stay weak/proxy. Expanding them to look symmetrical would lower epistemic quality.
- The genuine remaining gaps are targeted: a small set of records compress different downstream receiver actions into one card.

Firm positive split review candidates from the full pass:

- `category-decisions`
- `power-dynamics`
- `mental-models-of-reality`
- `critical-thinking`
- `metacognitive-questioning`
- `commitment-bias`
- `conjunction-fallacy`
- `emotional-intelligence`
- `evolutionary-pressure`
- `feedback-loops`
- `international-negotiation-and-diplomacy-models`
- `lock-in`
- `mental-simulation`
- `path-dependence`
- `redundancy`
- `switching-costs`

These are not approved edits yet. They are a targeted v19 proof queue.

The governing rule remains:

> Add a positive affordance only when it changes downstream use/reject/defer/merge behavior. Otherwise, prefer absence enrichment, guard visibility, packet hardening, or no change.

## What Counts As PASS

A record can pass source adequacy when every operational source cluster is:

- represented by a current affordance;
- represented by current absence or misuse-guard material;
- intentionally dropped as supporting detail;
- intentionally dropped as a different model's job;
- rejected because the source is too thin;
- marked as a transaction-distinct split candidate.

## What Counts As Failure

PR56 fails if it merely says:

- one affordance is fine because the record validates;
- more affordances are better because the source is rich;
- broad models are good because they sound strategic;
- zero absence records are fine without source review;
- weak-support records should be expanded to look complete;
- packet testing can tell us whether extraction was adequate.

Packet testing cannot prove source adequacy. It can only test what the packet was given.

## Immediate Recommendation

Finish PR56 as a source-adequacy audit, not a v19 enrichment PR.

The next concrete step is to merge the audit-only PR, then open a separate targeted v19 preparation PR using the full-corpus synthesis and candidate queue.

Only after that should a targeted v19 PR update any records.

## Expected PR Sequence

1. PR55: pickup-quality audit and packet risk map.
2. PR56: source adequacy and affordance granularity audit.
3. PR57: targeted v19 enrichment only for proven gaps.
4. PR58: grouped packet shape and per-affordance transaction identity.
5. PR59: static replay packet review.
6. Later: carefully gated live `/lolla` experiment.

## Bottom Line

The knowledge base should not be judged by coverage count or affordance count.

It should be judged by whether source-supported cognition is represented at the right transaction granularity, with explicit evidence, absence pressure, and enough restraint to avoid decorative model language.
