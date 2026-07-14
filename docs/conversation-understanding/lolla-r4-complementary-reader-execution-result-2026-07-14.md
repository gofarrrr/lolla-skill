# Lolla R4 complementary-reader execution and token-correction result

Status: first attempt closed on token-allocation failure; semantic question
unresolved; prospective correction prepared provider-free; new authorization
required

Date: 2026-07-14

Provider calls: 2

Exact provider-reported cost: `$0.009036`

Additional calls currently authorized: 0

## Plain-language result

The frozen R4 experiment reached the intended Gemini 3.1 Flash-Lite model and
Google provider twice, once for the known false-stand-down target and once for
the restraint control. Both calls failed for the same operational reason
before we could evaluate meaning: almost the whole 900-token completion budget
was consumed by hidden model reasoning, leaving only the beginning of the JSON
answer.

The runner behaved correctly. It preserved both failures, charged the exact
cost, did not repair the partial JSON, did not retry, and did not open either
dependent relationship call. We therefore learned something real about the
experimental boundary, but nothing yet about whether the new semantic readers
recover the missing pressure or preserve restraint.

## Exact execution result

| item | Case 02 target | Case 03 control |
| --- | ---: | ---: |
| served model | Gemini 3.1 Flash-Lite | Gemini 3.1 Flash-Lite |
| served provider | Google | Google |
| attribution | passed | passed |
| completion tokens | 885 | 886 |
| reasoning tokens | 865 | 861 |
| non-reasoning remainder | 20 | 25 |
| finish reason | `length` | `length` |
| parse result | unterminated JSON | unterminated JSON |
| locally admitted record | none | none |
| relationship call | not run | not run |
| exact cost | `$0.004387` | `$0.004649` |

Total cost was `$0.009036`, below the `$0.03` hard ceiling. There were no
fallbacks, retries, evaluators, embeddings, graph calls, pipeline calls,
runtime calls, or response healing.

## What this result means—and does not mean

The result is an operational negative, not a semantic negative.

We can say:

- the exact source packets, strict schema, provider route, and request bodies
  reached the intended operator;
- `low` thinking on this full-source task used more than 97% of the reported
  completion tokens for both cases;
- the 900-token completion boundary left too little room for the final JSON;
- dependency and budget stop rules worked.

We cannot say:

- whether the target pressure would have been recovered;
- whether the control would have remained quiet;
- whether either partial record was supported by evidence;
- whether the schema or prompt is semantically too difficult;
- whether the model is capable or incapable of the reader;
- whether the relationship reader works;
- whether the product improves reasoning or decisions.

The raw prefixes happen to begin records, including one on the control, but
neither contains a complete interpretation, evidence list, limitations, or
valid object. Treating those prefixes as semantic evidence would reward a
broken boundary and could create a false-positive story. The source-first
review therefore marks every semantic dimension not evaluable. Only operational
load and cost are evaluated.

## What we missed in preparation

The repository already knew that Gemini reasoning could crowd out short JSON:
a prior medium-reasoning microtask spent 909 of 984 completion tokens on
reasoning and truncated. The smaller task was repaired by factoring it and
using low reasoning.

R4 transferred only half of that lesson. We used low reasoning, but this reader
received 12–13k input tokens of full conversation and prior-role context. We
budgeted for a small output schema without separately accounting for the model's
task-dependent thinking allocation.

This does not justify a new deterministic semantic gate or another task split.
The observed failure is narrower: the transport allocation did not reserve
enough practical capacity for both thinking and the final object.

Current OpenRouter guidance says reasoning tokens count against output tokens
and that Gemini 3 effort maps to Google's thinking levels. Google describes
those levels as relative allowances, not exact budgets. The full practice check
is in
`docs/conversation-understanding/lolla-r4-token-allocation-current-practice-2026-07-14.md`.

## Prospective correction prepared

A new provider-free package changes exactly two uncertainty-request paths:

| field | first attempt | prospective attempt |
| --- | ---: | ---: |
| `/reasoning/effort` | `low` | `minimal` |
| `/max_tokens` | `900` | `1600` |

Everything semantic remains byte-identical: source, prior role records, prompt,
schema, aliases, model, provider, seed, source-first target, review dimensions,
and relationship contract. The relationship task remains `minimal` with a
700-token maximum.

The conservative four-call estimate rises from `$0.0160615` to `$0.0181615`,
still within `$0.015` per case and `$0.03` total. Minimal thinking is not a
guarantee; another length failure would be preserved and closed without rescue.

Local tests prove:

- the historical attempt and its hashes remain unchanged;
- the corrected request differs only at the two declared JSON paths;
- the full fake four-call path applies 1600/minimal to uncertainty and
  700/minimal to relationship;
- the task-limit override is restored after execution;
- authorization cannot expand calls or budget;
- no provider transport is reachable without a new exact authorization file.

The combined R4 closeout/correction slice passes 47 tests. Full repository
verification passes 4,834 tests with 1 skipped and all 93 subtests passing.

## Decision and next boundary

The first authorization is consumed and the historical attempt may not be
retried or reclassified.

The new prospective contract is ready, but it authorizes zero calls. The next
founder decision is whether to authorize one new bounded diagnostic with the
same two cases, a four-call maximum, no retries, and the unchanged `$0.03`
ceiling.

If authorized and mechanically successful, perform the original source-first
vector review. If uncertainty truncates or fails again, stop. Do not change the
schema, split the task, or switch model inside that run.

## Evidence map

- Original contract:
  `docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json`
- Consumed authorization:
  `docs/evals/lolla-r4-complementary-reader-experiment-authorization-a1.json`
- Exact first-run artifacts:
  `research/lolla-r4-complementary-reader-execution-2026-07-14-a1/`
- Hash-locked closeout:
  `research/lolla-r4-complementary-reader-execution-2026-07-14-a1/execution-closeout.json`
- Source-first review boundary:
  `research/lolla-r4-complementary-reader-execution-2026-07-14-a1/source-first-review.json`
- Current-practice check:
  `docs/conversation-understanding/lolla-r4-token-allocation-current-practice-2026-07-14.md`
- Prospective correction preflight:
  `research/lolla-r4-complementary-reader-token-correction-2026-07-14/preflight-result.json`
- New frozen contract:
  `docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json`
- Closeout and prospective runners:
  `scripts/evals/finalize_r4_complementary_reader_execution.py` and
  `scripts/evals/run_r4_complementary_reader_token_correction.py`
- Tests:
  `tests/test_r4_complementary_reader_execution_closeout.py` and
  `tests/test_r4_complementary_reader_token_correction.py`
