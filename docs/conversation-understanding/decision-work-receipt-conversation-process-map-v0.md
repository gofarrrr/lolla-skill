# Decision Work Receipt Conversation Process Map v0

Status: PR107 read-only exporter slice
Date: 2026-06-30
Schema: `lolla.decision_work_receipt.v0`

## Purpose

PR107 adds the first deterministic conversation-process view to the Decision
Work Receipt exporter.

The slice answers a narrow product question:

> Was there structured evidence that this output came from a one-shot exchange
> or from a multi-turn captured conversation?

It does **not** answer whether the conversation was good, whether Lolla improved
the decision, whether the user explored enough options, or whether the final
answer should be trusted.

## What It Reads

The exporter still runs in `checked_in_safe_mode`.

It may read safe structured JSON fields from completed run artifacts, especially:

- `extraction.json` structured `turns`;
- `extraction.json` structured `capture_manifest`;
- embedded `capture_adequacy` metadata in `extraction.json`,
  `agent_result.json`, `evaluation.json`, `reasoning_trace.json`, or
  `result.json`;
- structured `capture_health` and `capture_warnings` metadata when present.

It does not read raw conversation text.

It does not read:

- `conversation.txt`;
- `live_transcript.txt`;
- `memo.md`;
- `revised.txt`;
- provider text;
- private ledgers;
- private tables.

## What It Emits

The exporter now populates `conversation_process_map` when structured metadata
exists:

- `turn_count`;
- `user_turn_count`;
- `assistant_turn_count`;
- `process_depth`;
- `deterministic_process_evidence`;
- `source_refs`.

`process_depth` currently means only:

- `one_shot_candidate`: structured metadata suggests a one-user / one-assistant
  exchange or no more than two turns;
- `multi_turn_evidence`: structured metadata suggests more than a one-shot
  exchange;
- `not_measured`: no safe structured turn or capture-count metadata was found;
- `unclear`: structured metadata existed but was too incomplete to classify.

This is a shape-of-process field, not a quality field.

## What Remains Interpretation Needed

The following fields remain explicitly marked
`requires_llm_interpretation`:

- `new_context_added`;
- `user_corrections_or_redirects`;
- `options_explored`;
- `assistant_challenge_or_pushback`;
- `premortem_or_counterframe_used`;
- `abandoned_paths`;
- `final_output_divergence`.

Those fields require a probabilistic reader or later human review because they
depend on messy conversation meaning. Deterministic code must not infer them
from prose.

## Product Meaning

PR107 gives the receipt a first useful process signal:

- this looks like a thin one-shot exchange;
- this looks like a multi-turn captured exchange;
- the capture metadata says middle turns may have been omitted;
- the raw conversation remains private/redacted in checked-in safe mode;
- semantic process events are still not measured.

That helps a future reviewer or agent avoid treating every AI-generated output
as the same kind of work.

But it is deliberately humble. Five turns can still be shallow. One turn can
still be precise. A long conversation can still miss the real issue.

## Readiness Label

PR107 also updates `process_evidence_readiness` conservatively:

- one-shot metadata can produce `one_shot_or_thin_process`;
- multi-turn metadata can produce `multi_turn_unreviewed_process`;
- missing process metadata stays `insufficient_process_evidence`.

These labels describe available process evidence only. They do not score answer
quality, correctness, diligence, or user readiness to act.

## Boundary

PR107 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- read raw conversation text in checked-in safe mode;
- infer user values, live options, likely next action, useful friction, noisy
  friction, lost value, or answer quality;
- score conversation quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Current Meaning

A clean PR107 receipt means:

- structured turn or capture metadata can be represented;
- one-shot versus multi-turn process evidence is visible when safe metadata
  supports it;
- capture adequacy and truncation hints can be surfaced without reading raw
  text;
- semantic process fields remain honest non-claims.

It does not mean:

- the work was thoughtful;
- the work was challenged enough;
- Lolla improved the answer;
- the final answer is safe or correct;
- an agent may act on the result.

## Next Slice

The next slice is now implemented:

```text
PR108 Challenge Coverage Map v0
```

- [Decision Work Receipt Challenge Coverage Map v0](decision-work-receipt-challenge-coverage-map-v0.md)

It represents which Lolla challenge surfaces and run-health caveats exist for a
completed run, without deciding whether those challenges were good.

The next slice is also implemented:

```text
PR109 Decision Work Receipt Exporter v0
```

- [Decision Work Receipt Exporter v0](decision-work-receipt-exporter-v0.md)

It composes source inventory, process metadata, challenge coverage, optional
Decision Trail references, optional Product Delta references, readiness labels,
missingness, non-claims, and boundary flags into the first sparse work-trail
receipt.
