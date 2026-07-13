# Canonical model selector comparison result — 2026-07-12

## Decision

Canonical custody and compact cards are now operational, but neither direct-all-corpus nor graph-shortlist selection is ready for integration. In the frozen comparison, both modes rejected every candidate in every arm. The result is stable and safe but semantically inert.

No retry is authorized. The next design must preserve *why* deterministic graph recall produced a candidate and improve card pressure semantics before another call.

## Canonical migration

The historical `commitment-and-consistency-bias` identity was explicitly migrated to canonical `commitment-bias` in the three selection-facing curated artifacts. The migration manifest records before/after hashes, source provenance, occurrence counts, and the prohibition on runtime aliasing. Historical research outputs were not rewritten.

The migration initially exposed that `reasoning_signals.json` already contained a canonical `commitment-bias` key. The two signal lists were merged into one key rather than leaving duplicate JSON keys. The post-migration audit now resolves every chunk, signal, and subpattern model ID against the 222-model registry.

## Compact cards

All 222 canonical models now have deterministic compact cards derived from existing proprietary metadata:

- canonical ID and display name;
- one bounded `use_when` statement;
- one bounded `avoid_when` statement;
- input type;
- output type.

Every field is populated and distinct across the corpus; every serialized card is below 650 bytes. Direct and graph arms receive byte-identical cards for shared candidates. Unknown response IDs, invented IDs, duplicate selections, unknown role-record evidence, and inconsistent abstention envelopes fail closed.

The comparison corpus contains twelve provider-free packets. The executed registry case used six: source, provider, and reversal-ablation records crossed with direct-all-222 and graph-recalled candidate menus. Direct prompts were about 23.5k tokens; graph prompts were 1.8k–2.3k tokens.

## Frozen result

- six calls completed and compiled;
- no retry, fallback, evaluator, embedding, graph execution, or runtime effect;
- estimated cost: `$0.00540253`;
- canonical custody: passed 6/6;
- source/provider selected-ID invariance: passed trivially in both modes;
- protected reversal selection: failed in both modes;
- counterpressure survival: failed in both modes;
- all calls returned an empty selection.

Source-first arms returned `all_not_applicable`; provider and ablation arms returned `insufficient_evidence`. This difference does not affect routing but shows the model noticed information-quality variation.

## Diagnosis

The result does **not** show that no mental model applies. It exposes two contract defects.

First, graph-recalled cards lost recall provenance. The selector saw eight canonical cards but not the fact-free mechanisms that pulled them, such as `missing_reversal_condition → premortem`. Deterministic recall became an unexplained shortlist, discarding the very external pressure signal the graph contributes.

Second, compact cards were produced by taking the first `select_when` and first `danger_when` entry. Those fields were written as general model guidance, not as paired positive/negative applicability tests for this selector. For example, the `commitment-bias` card's first use describes beneficial persistence, while its first avoid condition describes the exact harmful lock-in that should trigger scrutiny. The labels therefore invert or blur challenge semantics for some models.

The direct arm adds a third effect: 222 cards create a 23.5k-token search task. It obeyed canonical identity but chose safe abstention. This supports the concern that “show all names” solves naming variation without automatically creating reliable applicability selection.

## What remains valid

- Canonical IDs only is the correct rule.
- Explicit curation-time migration is preferable to runtime alias repair.
- Direct and graph arms can use the same canonical card format.
- Abstention must remain valid; the remedy is not to force a minimum selection.
- Graph recall remains promising because it reduces the menu from 222 to 5–8 candidates and preserves deterministic external pressure in principle.

## Next bounded goal

Create challenge-oriented canonical cards and a graph-provenance handoff:

1. derive a compact `challenge_when`, `do_not_apply_when`, and `pressure_question` from curated failure modes, selection guidance, and premortem material;
2. attach controlled `recalled_by_mechanism_ids` to graph candidates;
3. keep role records and graph provenance fact-free and source-linked;
4. test that misleading polarity, unsupported recall provenance, invented IDs, and forced non-abstention fail locally;
5. run a new transfer case, not a retry, only after source review confirms that at least one candidate card expresses the protected pressure without leaking the expected answer.

## Evidence

- migration: `data/curated/canonical_id_migrations.json`
- cards and packets: `research/canonical-model-selector-comparison-corpus-2026-07-12/`
- frozen target and contract: `docs/evals/canonical-model-selector-comparison-target-v1.json`, `docs/evals/canonical-model-selector-comparison-probe-contract-v1.json`
- preserved calls: `research/canonical-model-selector-comparison-probe-2026-07-12/`

