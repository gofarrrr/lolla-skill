# R4 complementary-reader experiment preparation result

Status: provider-free preparation complete; explicit call authorization required

Date: 2026-07-13

Provider calls: zero

Provider cost: `$0.00`

Runtime, graph, live-skill, and production-model changes: none

## Plain-language result

The next R4 experiment is fully designed and locally tested. It is not yet run.

We will ask one small model reader two separate questions about a complete
conversation:

1. What important matter, if any, is still unresolved?
2. What specific evidence, event, or dependency failure, if any, should reopen
   the current position?

A second small reader will then receive the exact IDs of admitted conversation-
state records and may explain how they relate. It cannot silently merge or
rewrite them. Both readers may validly return zero, and ambiguity remains an
explicit record rather than being turned into certainty.

The experiment uses one conversation where V1 falsely stood down and one
closely matched conversation where standing down was proportionate. This means
we test both sides of the product claim: can the new surface discover a known
missing issue, and can it avoid manufacturing friction when the conversation
already contains a good reconsideration structure?

## Why these two cases

The discovery target is `v1-case02-discharge-transport`. V1 correctly preserved
the user's bounded two-ward pilot but did not separately preserve the question
of what generalizes from the only city with accessible vehicles, or which
safeguards depend on temporary coordination and attention.

The restraint control is `v1-case03-executive-hire`. Its final position already
contains a six-month review of results and decision travel, asks whether
unwelcome information still moves upward, and preserves evidence that can
distinguish executive ability, mandate, founder interference, resistance, and
changed conditions. The reader should not call those safeguards a new problem
merely because they discuss future uncertainty.

Both cases have 24 messages, one starting record, one current record, a
completed-zero qualification read, roughly 12 KB of authoritative source, and
complete V1 transfer artifacts. The principal changed variable is the known
false-stand-down versus restraint judgment.

The exact source-first expectations were frozen before the execution contract
in
`docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json`. They are
review-only and are absent from every provider request.

## Reader and fan-in design

The paired reader returns exactly one review for each semantic surface:

- `unresolved_matter`;
- `reopen_condition`.

Each review declares one of:

- `records_present`;
- `no_supported_record_observed`;
- `ambiguous_review`.

Every non-empty record carries a short interpretation, `supported` or
`ambiguous` status, exact evidence aliases, and limitations. Source-supported
inference is allowed; outside-fact invention is not. The complete source is
placed before compact existing position records, and those records are labeled
fallible prior interpretations rather than source truth.

The relationship reader receives unchanged admitted semantic payloads, exact
record IDs, and exact source evidence. It returns at most two relationships and
may complete with zero. Deterministic code checks only that endpoint IDs and
source aliases exist, the response shape is valid, hashes reproduce, and bounds
hold. It does not decide that co-occurrence, overlap, or particular prose means
a relationship exists.

The completed fan-in contract continues to distinguish operational
`complete`, `completed_zero`, `partial`, `failed`, and `missing`. A quiet
semantic result never hides a reader that failed or was never run.

## Current-practice and operator decision

Google's structured-output documentation was updated on 2026-07-07. It still
warns that only a JSON Schema subset is supported, large or deep schemas may be
rejected, and syntactic validity does not establish semantic validity.
OpenRouter recommends strict JSON Schema, property descriptions, and
`require_parameters: true`. Maintained Instructor and PydanticAI evidence also
supports typed, shallow native structured output while showing that retries and
transport modes materially change what is being measured.

The model-facing schemas therefore use only Google's documented object, array,
string, description, enum, required, additional-properties, items, and array-
bound features:

| Reader | Canonical schema bytes | Maximum records |
| --- | ---: | ---: |
| Paired unresolved/reopen | 1,653 | two per surface |
| Exact-ID relationship | 1,442 | two total |

Uniqueness, text lengths, source membership, outcome consistency, hashes, and
endpoint resolution are local checks. There is no silent JSON mode, healing,
fallback, or retry.

The fixed operator is `google/gemini-3.1-flash-lite` through OpenRouter's pinned
`google-vertex` route. The current endpoint and ZDR inventories list the route
with strict structured-output, seed, and reasoning controls at `$0.25` per
million prompt tokens and `$1.50` per million completion or internal-reasoning
tokens. Data collection is denied, ZDR is required, fallbacks are disabled, and
the provider is attribution-checked.

This is not a production-model selection. Gemini 3.1 Flash Lite is used because
the closed V1 investigation already observed 50 small decomposed calls for
`$0.076058862`. Gemini 3.5 remains an expensive preserved benchmark, not a
testing default. DeepSeek V4 Flash is cheaper but remains a later comparison:
changing both model family and semantic decomposition in the first diagnostic
would make causality less clear.

The dated source and adoption record is in
`docs/conversation-understanding/lolla-r4-complementary-reader-current-practice-2026-07-13.md`.

## Cost and execution boundary

The frozen experiment permits at most four calls:

```text
Case 02: paired uncertainty -> exact-ID relationship
Case 03: paired uncertainty -> exact-ID relationship
```

The uncertainty output cap is 900 tokens at low reasoning effort. The
relationship cap is 700 tokens at minimal effort. The conservative provider-
free estimate assumes only two input bytes per token and totals `$0.0160615`.
The hard ceiling is `$0.015` per case and `$0.03` total.

The runner writes a durable started marker before every network transport. It
stops a relationship call when uncertainty fails, stops future calls when exact
provider cost is unavailable, and stops at the case or total cost boundary.
Every first failure survives. There are no automatic or semantic retries,
fallback models, response healing, evaluators, embeddings, graph calls,
pipeline calls, or runtime calls.

## Local verification result

The provider-free package exercises:

- known-gap positive records on Case 02;
- completed-zero uncertainty and relationship results on Case 03;
- an explicit ambiguous record path;
- not-run, dependency-missing, failed, and completed-zero distinctions;
- exact alias text and hash custody across 102 and 113 source aliases;
- exact admitted relationship endpoints;
- reverse surface order without semantic dependence on array position;
- unknown aliases, unknown/duplicate endpoints, extra fields, inconsistent
  outcome/record combinations, and artifact drift failing closed;
- byte-exact preflight rebuild;
- a fake four-call execution proving dynamic relationship-packet construction,
  positive fan-in, quiet fan-in, and cost accounting without network access.

The structural Case 02 path ends with five complete readers, one completed-zero
reader, and five records. The structural Case 03 path ends with two complete
readers, four completed-zero readers, and only its two pre-existing position
records. These are contract fixtures, not provider results or semantic evidence.

Repository verification completed with `4,820 passed`, `1 skipped`, and all
`93` subtests passing. The focused complementary-reader and frozen-replay slice
completed with `33 passed`; the preflight rebuilt byte-for-byte and the frozen
runner contract completed its dry run with authorization absent. All of this
verification made zero provider calls and incurred zero provider cost.

## What the eventual result will tell us

The paid diagnostic will be reviewed as a vector, not a score:

- did it recover the known material gap?
- did it remain quiet on the control?
- did every record cite evidence that supports its own meaning?
- were unresolved matter and reopen condition placed separately?
- did the relationship use exact IDs and add meaning without rewriting its
  endpoints?
- what did the two-stage boundary cost and how large was its fan-in?

A schema-valid response can still fail source review. An ambiguous response is
preserved but is not automatically a pass. A completed-zero response is valid
behavior but does not prove universal semantic absence.

The result cannot establish product reliability, real-user usefulness, graph
value, answer improvement, decision quality, trust, or a production model. It
is a causal diagnostic of one missing representation surface.

## Decision

All provider-free gates pass. No further design choice is needed before the
experiment. The sole remaining decision is whether to authorize the frozen
four-call maximum diagnostic under its `$0.03` total ceiling.

The preparation itself authorizes zero calls. It also does not authorize
runtime or graph integration, a wider corpus, a model comparison, another R3
attempt, a revised answer, or public product claims.

## Reproducible evidence

- Source-first target:
  `docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json`
- Experiment contract:
  `docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json`
- Point-in-time model snapshot:
  `docs/evals/lolla-r4-complementary-reader-model-snapshot-2026-07-13.json`
- Reader contracts and compilers:
  `engine/system_b/r4_complementary_readers.py`
- Preflight builder:
  `scripts/evals/build_r4_complementary_reader_preflight.py`
- Authorization-gated runner:
  `scripts/evals/run_r4_complementary_reader_experiment.py`
- Machine preflight:
  `research/lolla-r4-complementary-reader-preflight-2026-07-13/preflight-result.json`
- Focused tests:
  `tests/test_r4_complementary_readers.py` and
  `tests/test_r4_complementary_reader_preflight.py`

Rebuild and validate without a provider:

```bash
PYTHONPATH=. python3 scripts/evals/build_r4_complementary_reader_preflight.py
PYTHONPATH=. python3 scripts/evals/build_r4_complementary_reader_preflight.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_complementary_reader_experiment.py \
  --contract docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json \
  --dry-run
PYTHONPATH=. pytest -q \
  tests/test_r4_complementary_readers.py \
  tests/test_r4_complementary_reader_preflight.py
```
