# Bounded chronological shard redesign v1

Status: provider-free representation passes; prompt/schema/custody design is next  
Date: 2026-07-11

## Problem being solved

The Phase-4 readers were mechanically reliable but semantically selective. A
whole-conversation reader could return several useful major themes and still
miss a small evidence boundary, reopen condition, or direct correction. The
same evidence-family failure appeared in both transfer cases.

The redesign cannot use deterministic rules to decide which conversational
detail matters. It also cannot solve recall by returning to the former
88–95-event flood or by adding another global semantic synthesizer.

## Proposed shape

The four former whole-conversation families each receive three source-complete
chronological shards:

- evidence, uncertainty, and challenge: turns 1–3, 4–5, and 6–7;
- position: a first-versus-final endpoint comparison, then turns 2–4 and 5–6;
- the immediately preceding pair is visible as context where applicable;
- context is not generally citable. A future role validator may allow it only
  as a challenge's prior frame or a position's starting state;
- every source sentence is focal exactly once per family;
- each shard may return at most two records;
- no auxiliary ledger, semantic prefilter, global synthesis, semantic merge,
  graph, or runtime consumer is present.

Exploration keeps its already passing seven pair-local windows. The resulting
ceiling for a fourteen-message case is:

| measure | failed transfer design | shard v1 ceiling |
| --- | ---: | ---: |
| semantic calls | 11 | 19 |
| maximum records | 30 | 38 |
| observed transfer records | 26 per complete case | unknown |
| largest model packet | about 17 KB for global readers | below 6.1 KB |
| global synthesis | none | none |

The cost increase is explicit. It is justified only if a small probe shows a
material minority-signal gain.

## Provider-free evidence

- 60 packets across five reviewed cases;
- 12 shards per case and three per family;
- every sentence alias focal exactly once within each family;
- all 20 protected full-reader targets co-located inside exactly one focal
  shard, including the first-versus-final position relationships;
- maximum packet size 6,013 bytes;
- maximum 24 new shard records plus 14 existing exploration records per case;
- 131 reasoning-process tests pass after the Phase-4 result and shard design;
- zero provider, evaluator, embedding, graph, pipeline, or runtime calls.

Co-location proves only that the model can see the relationship in one bounded
job. It does not prove that Gemini will select it or interpret it correctly.

## Rejected shortcuts

- increasing the global reader from four to eight records: Case 05's position
  reader returned only one record, so output capacity alone is not the failure;
- early/middle/late keyword quotas: that would be brittle deterministic
  semantic gating;
- sharding only the evidence reader: position, uncertainty, and challenge also
  lost protected Case-05 details;
- a larger model before decomposition: that changes cost and model behavior
  without testing the evidenced overload mechanism;
- one call per protected target: evaluation answers cannot enter production
  prompts;
- global consolidation after shards: this recreates the fan-in failure already
  observed.

## Next gate

Before any provider call, define family-specific shard prompts, strict provider
schemas, role-limited context validation, record-level custody, duplicate
telemetry, call/cost limits, and a target-blind smallest-probe contract. The
future prompt must place visible source context before the final task question,
following current Gemini guidance.

The first model-backed step should be the smallest failed transfer surface, not
a nineteen-call case: Case-05's early evidence shard, because the whole-reader
transfer omitted that protected principle-versus-action boundary and the same
family failed partially on Case 01. The target remains hidden. No call is
authorized by this document.
