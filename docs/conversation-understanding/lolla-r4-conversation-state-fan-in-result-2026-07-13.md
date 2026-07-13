# R4 missingness-aware conversation-state fan-in result

Status: complete provider-free; bounded semantic-experiment preparation earned

Date: 2026-07-13

Provider calls: zero

Provider cost: `$0.00`

Runtime, graph, prompt, and model changes: none

## Plain-language result

We repaired the container that carries conversation interpretations forward.
We did not claim to make the interpretations smarter.

Before this change, a reader that returned nothing, a reader that failed, and
a reader that never existed could all look too similar at the system boundary.
Now every planned reader has one explicit result with one of five states:

- `complete`: the reader completed with at least one admitted record;
- `completed_zero`: the reader completed and returned zero records;
- `partial`: useful records survive, but that boundary did not complete;
- `failed`: the reader failed and has no admitted record;
- `missing`: the reader result or contract is unavailable.

Most importantly, `completed_zero` is not treated as proof that nothing matters,
and `missing` is not treated as a stand-down signal. Deterministic code can see
the difference without trying to understand the conversation itself.

## What the fan-in preserves

The handoff can carry complementary provider-authored records for:

- starting position;
- current position;
- qualification;
- unresolved matter;
- reopen condition;
- cross-thread relationship.

Each semantic record keeps the complete provider-authored payload, its
canonical hash, exact source aliases, speaker, turn index, and source text hash.
Relationship records use exact admitted record IDs. Two readers may return
overlapping or even byte-identical payloads; both survive. Python counts the
overlap but does not merge, rank, vote, or decide which record is correct.

The v1 boundary permits at most twelve readers, 48 total records, 24 source
locators per record, 256 KiB of semantic payloads, and a 1 MB handoff. These
limits are deliberately generous above the measured V1 load while still making
fan-in expansion an explicit versioned decision.

## Current-practice decisions

The contract uses an explicit state-tagged JSON Schema `oneOf`. This follows
current JSON Schema, OpenAPI, and maintained Pydantic guidance favoring explicit
tagged variants over ambiguous untagged matching. It also follows RFC 9457's
useful separation principle: machine behavior uses a stable code, while human
detail remains explanatory text that code must not parse.

We did not add Pydantic, an OpenAPI layer, or an HTTP Problem Details envelope.
The repository's standard-library validator is sufficient, and importing those
frameworks would not improve the semantic boundary. The dated source and
adoption record is in
`docs/conversation-understanding/lolla-r4-fan-in-current-practice-2026-07-13.md`.

## Exact replay result

Four existing V1 paths were replayed without a provider:

| V1 case | complete | completed zero | partial | failed | missing | admitted records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Case 01 flood infrastructure | 3 | 0 | 0 | 0 | 3 | 3 |
| Case 02 discharge transport | 2 | 1 | 0 | 0 | 3 | 2 |
| Case 06 industry-funded lab | 0 | 0 | 2 | 1 | 3 | 2 |
| Case 09 software migration | 0 | 0 | 0 | 1 | 5 | 0 |
| **Total** | **5** | **1** | **2** | **2** | **14** | **7** |

All 21 admitted source locators reproduce exactly. Every handoff stays within
the frozen bounds. Canonical handoff payloads range from 24,036 to 33,677 UTF-8
bytes. The Case 09 output retains the exact failure-artifact path and hash but
does not copy the private provider error or user identifier.

The decisive Case 02 check now says exactly what happened: the qualification
reader completed with zero records, while unresolved matter, reopen condition,
and relationship readers are missing because those distinct V1 contracts did
not exist. Those facts can no longer collapse into one empty semantic answer.

Case 06 likewise preserves the two admitted current/qualification records as
partial beside the failed starting-position custody result. No record is
invented to make the join look complete.

## What this solves—and what it does not

This solves an assembly and accountability defect:

- every planned reader is visible;
- zero, partial, failure, and missingness are distinct;
- complete provider-authored interpretations survive unchanged;
- complementary overlap survives;
- source, artifact, identity, relationship, count, and byte custody replay;
- downstream consumers can see gaps instead of receiving a false clean slate.

It does not solve the semantic gap found in Cases 01 and 02. The primary V1
system still has no distinct unresolved-matter, reopen-condition, or
cross-thread-relationship records to place in this container. The contract
cannot recover meaning that no probabilistic reader produced.

It also does not establish semantic correctness, complete coverage, graph
value, answer improvement, decision quality, trust, or real-user usefulness.
There is no score or quality badge.

## Constitutional check

The hybrid boundary remains intact:

```text
probabilistic readers interpret messy meaning
                    ↓
deterministic fan-in preserves IDs, hashes, states, locators, overlap, and bounds
                    ↓
future probabilistic/deterministic stages may inspect the evidence
```

The fan-in does not infer roles from keywords, chronology, turn count, or array
order. It does not infer semantic absence, relationship meaning, mental-model
relevance, pressure activation, or advice quality. The deterministic system is
used where it is strong, without becoming a brittle semantic state machine.

## Decision and next goal

The provider-free contract passed. A bounded semantic experiment is now worth
preparing, but no model call or runtime integration is authorized by this
result.

The next goal should freeze, provider-free:

1. one small paired reader for unresolved matter and reopen condition;
2. one subsequent exact-ID relationship reader over admitted records;
3. one already exposed false-stand-down case and one restraint control;
4. source-first targets, strict small schemas, prompts, source custody, model
   and provider policy, no-retry cost ceiling, and fan-in acceptance gates;
5. separate judgments for recovered material pressure, false positive pressure,
   evidence precision, role placement, relationship fidelity, and load.

This is a causal diagnostic, not a reliability claim. It asks whether adding
the missing probabilistic surfaces changes the specific upstream gap while the
new deterministic fan-in preserves every outcome honestly. A provider call
would require separate authorization after all preparation passes locally.

## Reproducible evidence

- Contract:
  `docs/evals/lolla-r4-conversation-state-fan-in-contract-v1.json`
- Structural fixture:
  `tests/fixtures/r4_conversation_state_fan_in/contract-fixture-v1.json`
- Core implementation:
  `engine/system_b/conversation_state_fan_in.py`
- Replay builder:
  `scripts/evals/build_r4_conversation_state_fan_in_replay.py`
- Machine result:
  `research/lolla-r4-conversation-state-fan-in-2026-07-13/replay-result.json`
- Focused tests:
  `tests/test_conversation_state_fan_in.py` and
  `tests/test_r4_conversation_state_fan_in_replay.py`

Rebuild and validate with:

```bash
python3 scripts/evals/build_r4_conversation_state_fan_in_replay.py
python3 scripts/evals/build_r4_conversation_state_fan_in_replay.py --validate-only
PYTHONPATH=. pytest -q tests/test_conversation_state_fan_in.py tests/test_r4_conversation_state_fan_in_replay.py
```
