# Lolla R4 provider-free corpus replay result

Status: complete; one bounded next design repair earned

Date: 2026-07-13

Provider calls: zero

Provider cost: `$0.00`

Runtime, graph, prompt, model, and semantic-schema changes: none

## Plain-language result

We now know exactly what the existing twelve-conversation V1 evidence can and
cannot tell us before changing the conversation-understanding system.

The current system is strong at preserving source identity, execution state,
failures, and receipts. It is not yet strong enough at preserving all of the
meaning needed before deterministic pressure routing. In two of the seven
completed and source-reviewed cases, an important challenge disappeared before
the deterministic mechanism and graph machinery could see it. The graph could
not recover information it never received.

This does not mean deterministic pressure is the wrong idea. It localizes the
problem one step earlier: complementary probabilistic readers need a clear,
missingness-aware way to hand their explicit interpretations forward without
one absent read becoming evidence that nothing is unresolved.

## What was replayed

The replay used the existing frozen evidence only:

- twelve naturalized conversations;
- 24 messages per conversation;
- exact corpus, source-review, preflight, transfer, receipt, failure, and later
  exposed-development artifacts;
- seven completed transfer executions;
- one preserved role-custody join failure;
- four preserved pre-inference provider-credit failures;
- seven same-project diagnostic source reviews.

The inventory contains 543 case-to-artifact links covering 400 unique
case-linked JSON files. Every record carries a path, SHA-256, byte count,
declared schema/status metadata, evidence partition, and custody
classification. Source text and both receipt formats have separate exact
hashes. Raw artifact content and private provider values are not copied into
the replay.

All source bytes reproduce the V1 manifest and both the naturalized review and
provider-free preflight. The replay itself has no network or API-key path.

## What is now measurable exactly

The deterministic replay can answer these questions without pretending to
understand prose:

- whether a source or artifact exists and whether its hash still matches;
- whether a required surface completed, partially completed, failed, is
  missing, returned zero explicit records, or was not applicable;
- which provider-authored role label an admitted record carries;
- how many starting, current, and qualification records reached the join;
- whether all 65 admitted role source references resolve to the frozen alias
  map with matching text hashes, speakers, and turn locators;
- how much material reached each available boundary, as separate byte, alias,
  record, source-reference, mechanism, candidate, and edge counts;
- whether direct or graph pressure activated;
- which evidence is transfer, diagnostic review, or exposed development work.

Across the corpus, the replay finds 1,285 exact source aliases, 18 admitted or
partially admitted role records, and 65 exact role source references. There are
seven admitted starting records, eight current records including the partial
Case 06 path, and three qualifications including the partial Case 06 path.
These are workload and custody facts, not semantic coverage scores.

## Case-level operational result

| state | cases | what it means |
| --- | ---: | --- |
| Sealed transfer complete | 7 | Starting/current/qualification production, mechanism coverage, stand-down ledgers, transcript consumer, and receipt completed. A completed zero-candidate ledger is preserved as an empty output, not called missing. |
| Role join failed | 1 | Case 06 produced current and qualification records, but the starting record was quarantined by its alias custody contract. Downstream semantic and pressure artifacts were not produced. |
| Starting transport failed | 4 | Cases 09–12 stopped at HTTP 402 before starting-position inference. Later semantic surfaces are missing, not empty. |

The seven completed cases all stood down. Frozen diagnostic review covers only
those seven:

- five stand-downs were judged proportionate;
- two, Cases 01 and 02, were judged false stand-downs;
- no transfer pressure arm or graph-expanded fresh consumer ran;
- no primary graph candidate became active.

The correct denominator for the false-stand-down finding is seven reviewed
completed cases, not the whole corpus, and even that review is diagnostic:
same-project, not independent, and not cleanly blinded.

## The repeated causal gap

Cases 01 and 02 share the first observable semantic failure:

```text
material source thread
  -> absent from the representation reaching controlled mechanisms
  -> zero unresolved controlled mechanisms
  -> deterministic stand-down
  -> graph never receives a seed to challenge
```

The replay does not use keywords or chronology to infer the missing meaning.
It relies on the already frozen source-first diagnostic review for that
semantic judgment and uses deterministic code only to trace the declared
artifacts and states.

The interface audit also finds no distinct primary contract surface for:

- unresolved matter;
- reopen condition;
- cross-thread relationship.

That is an interface fact across all twelve cases. It does not prove that all
twelve conversations contain those semantics. Qualification records are not
silently reclassified into any of the missing categories.

## What remains unknown

The replay cannot establish:

- genuine real-user usefulness;
- complete material-thread coverage;
- semantic correctness of a starting, current, or qualification label;
- whether source spans actually support an interpretation merely because the
  locators resolve;
- whether two records represent one thread or two related threads;
- over-fragmentation from record counts alone;
- graph value, because no primary graph pressure reached a fresh transfer
  consumer;
- whether a pressured answer would be better;
- receipt reconstruction by a fresh human or agent;
- production reliability or readiness.

There is deliberately no composite score, percentage, quality badge, or
automatic release gate.

## One next repair is earned

The next R4 task should design a **missingness-aware system-level
conversation-state fan-in contract**.

Its job is narrow: preserve complementary provider-authored records for
starting position, current position, qualification, unresolved matter, reopen
condition, and explicit thread relationships, together with exact source
locators and separate `complete`, `partial`, `failed`, `missing`, and completed
zero-record states.

Deterministic code may:

- validate identities, source hashes, labels, locators, and declared states;
- preserve overlapping readers without deleting one;
- measure fan-in load;
- expose disagreement and missingness to the next probabilistic consumer.

It may not:

- fill a missing semantic role;
- infer roles from words, chronology, or array order;
- merge prose because it appears similar;
- decide that an unresolved matter is relevant to a mental model;
- decide that pressure should be applied;
- turn coverage into a quality score.

The expected changed measurement is simple: a downstream consumer can inspect
every reader's explicit output and absence state, and one missing read can no
longer masquerade as stand-down evidence.

This result selects the contract-design task. It does not authorize a runtime
implementation or provider call. The contract must pass provider-free custody,
missingness, overlap, speaker, temporal-locator, fan-in, and adversarial tests
before any semantic experiment is proposed.

## Reproducible artifacts

- Measurement contract:
  `docs/evals/lolla-r4-measurement-contract-v1.json`
- Inventory:
  `research/lolla-r4-corpus-replay-2026-07-13/r4-corpus-replay-manifest.json`
- Gap matrix:
  `research/lolla-r4-corpus-replay-2026-07-13/r4-replay-gap-matrix.json`
- Machine-readable result:
  `research/lolla-r4-corpus-replay-2026-07-13/r4-replay-result.json`
- Builder/validator:
  `scripts/evals/build_r4_provider_free_corpus_replay.py`
- Contract tests:
  `tests/test_r4_provider_free_corpus_replay.py`

Rebuild and validate with:

```bash
python3 scripts/evals/build_r4_provider_free_corpus_replay.py
python3 scripts/evals/build_r4_provider_free_corpus_replay.py --validate-only
PYTHONPATH=. pytest -q tests/test_r4_provider_free_corpus_replay.py
```
