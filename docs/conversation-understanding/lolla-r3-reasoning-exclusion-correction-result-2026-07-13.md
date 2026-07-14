# Lolla R3 reasoning-exclusion correction result

Status: provider-free prospective correction complete; paid R3 deferred

Date: 2026-07-13

Provider calls: zero

Provider cost: `$0.00`

## Plain-language result

We fixed the rule for future experiments without rewriting the experiment that
already failed.

The frozen R3 runner used one broad question: “Does either `reasoning` or
`reasoning_details` exist?” That made an opaque signature count as returned
reasoning content. The new prospective validator asks a narrower factual
question: “Did the provider return non-empty reasoning content, or did it
return only an empty or metadata-only envelope?”

For future R3 packages:

- non-empty plaintext, summary, encrypted data, or compatible reasoning
  content fails the exclusion gate;
- absent, null, empty, and whitespace-only content passes;
- a documented reasoning-detail record containing only type, format, ID,
  index, and signature metadata passes;
- unknown types, unknown fields, malformed containers, non-object list items,
  and invalid field types fail closed;
- the inspection result records paths and classifications, never provider
  values.

This is deterministic structure checking. It does not decide whether reasoning
is good, whether a response is useful, or whether a mental model applies.

## Important repository finding

The live provider boundary already had a June 2026 heuristic that ignored
signature-only Gemini metadata. R3's standalone experimental runners had
copied the older broad boolean instead of using a shared experimental
contract.

We did not simply import that live heuristic. It correctly handles the known
signature case, but it also accepts undocumented mapping containers, ignores
non-object list entries, does not inspect the documented
`reasoning_content` alias, and cannot distinguish malformed from clean. Those
properties are acceptable telemetry compromises but too loose for a frozen
experiment gate.

The new validator therefore lives at the prospective R3 boundary. It does not
change the live runtime, frozen runner, or historical result.

## Current-practice basis

OpenRouter's current documentation says:

- `reasoning.exclude: true` excludes returned reasoning tokens;
- plaintext reasoning appears in `message.reasoning`;
- `reasoning_content` is an alias;
- `reasoning_details` is an array of structured records;
- the documented content-bearing record types use `text`, `summary`, or
  `data`;
- detail records also carry metadata such as type, ID, format, index, and an
  optional signature.

Source:
[OpenRouter reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).

The documentation does not explicitly promise the exact signature-only
Gemini envelope we observed. Accepting that envelope is a bounded inference
from the exact payload plus the documented separation between content fields
and signatures. Unknown future shapes therefore fail closed until the
contract is deliberately updated.

## Fixture result

Thirty-five focused tests cover:

- no reasoning fields;
- null, empty, and whitespace-only message fields;
- the `reasoning_content` alias;
- null and empty detail arrays;
- one and multiple metadata-only records;
- plaintext, summary, encrypted data, and compatible content aliases;
- mixed metadata and content;
- wrong containers and non-object list items;
- missing and unknown detail types;
- unknown fields;
- invalid content, index, and signature types;
- content plus malformed conditions;
- output non-leakage;
- exact frozen-file hashes;
- self-hash and contract tampering;
- zero provider transport paths.

The focused correction plus existing R3/runtime boundary tests currently pass
72 tests provider-free.

## Historical experiment remains closed

Seven exact frozen files are checked on every correction build:

- collapsed-outcome execution contract;
- founder authorization;
- frozen runner;
- call result;
- redacted provider payload;
- failure closeout;
- terminal result.

The new diagnostic classifies the commit-safe copy of the exact provider
message as `reasoning_metadata_only`. That is useful for validating the new
rule. It does **not** change any historical field:

| Historical field | Preserved value |
| --- | --- |
| Frozen runner status | `pressure_response_valid_reasoning_exclusion_breached` |
| Frozen mechanical contract | failed |
| Frozen `reasoning_content_returned` | `true` |
| Semantic review | not performed |
| Result reclassified | no |
| Additional call authorized | no |

The model response remains semantically unevaluated. We still do not know
whether its nine dispositions were useful.

## Privacy and custody

The provider-free build:

- reads the checked-in redacted payload, not the raw private payload;
- verifies its self-hash and all frozen evidence hashes;
- does not copy the opaque signature;
- does not copy plaintext, summary, encrypted data, or compatible content
  values into inspection output;
- emits only statuses, counts, and JSON-pointer-like field locations;
- contains no provider transport, API-key lookup, retry, or execution flag.

## Decision

Further paid R3 work is deferred.

Another R3 call would require all of the following:

1. a genuinely new falsifiable question;
2. proof that existing artifacts and provider-free tests cannot answer it;
3. a newly frozen prospective case and contract;
4. separate founder authorization.

We should not spend another call merely to obtain a result that a corrected
validator would accept. That would retest the harness, not advance the product
question enough to justify the cost.

## R4 handoff

The next major stage is provider-free R4 corpus and sealed-output replay. Its
first goal is not to redesign extraction. It is to freeze an inventory and
measurement contract over the existing twelve naturalized 24-message V1
conversations, identify which sealed artifacts are replayable, and expose
missing surfaces before changing prompts, schemas, or architecture.

See the
[R4 provider-free corpus/replay plan](../../plans/lolla-r4-provider-free-corpus-replay-plan-2026-07-13.md).

## Evidence map

- Prospective contract:
  `docs/evals/lolla-r3-reasoning-exclusion-prospective-contract-v1.json`
- Prospective validator:
  `engine/system_b/r3_reasoning_exclusion.py`
- Provider-free builder:
  `scripts/evals/build_r3_reasoning_exclusion_correction.py`
- Machine-readable result:
  `research/lolla-r3-collapsed-outcome-case-2026-07-13/prospective-reasoning-validator/validation-result.json`
- Tests: `tests/test_r3_reasoning_exclusion_correction.py`
- Historical execution result:
  `docs/conversation-understanding/lolla-r3-collapsed-outcome-execution-result-2026-07-13.md`
