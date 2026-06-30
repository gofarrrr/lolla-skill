# Decision Work Receipt PRD v0

Status: actionable product/architecture PRD
Date: 2026-06-30

## Purpose

This PRD turns the missing product elements from the board product discussion
into an implementation path grounded in the current Lolla repo.

The product idea is:

> In AI-assisted knowledge work, the final answer is cheap. The valuable thing
> is the work trail behind it.

The Decision Work Receipt is the future artifact that travels with a serious
AI-assisted output and explains how the output was produced, challenged, and
changed.

It is not proof that the answer is correct. It is evidence about the process
behind the answer.

## Current Codebase Reality

The current repo already has the right foundations:

| Existing surface | Current file or artifact | What it gives us |
| --- | --- | --- |
| Live Lolla runtime | `SKILL.md`, `scripts/run_extract.py`, `scripts/run_pipeline.py`, `scripts/archive_run.py` | Captures a conversation, extracts a compact decision shape, runs audit lanes, writes revised answer and archives the run. |
| Conversation context | `engine/system_b/conversation_context.py` | Immutable turn, constraint, dropped-thread, extraction, and capture metadata structures. |
| Archived run artifacts | `conversation.txt`, `extraction.json`, `result.json`, `revised.txt`, `memo.md`, `agent_result.json`, `evaluation.json`, `reasoning_trace.json` | The raw and structured material a future work receipt can reference. |
| Decision Trail report | `engine/system_b/decision_trail_report.py`, `docs/conversation-understanding/decision-trail-report-v0.json` | Sparse custody-first report over completed runs, with explicit missingness and redaction/private availability. |
| Decision Trail packets | `engine/system_b/decision_trail_specialist_packets.py` | Checked-in-safe and local-private packet builder for bounded specialist interpretation. |
| Decision Trail specialist contracts | `docs/conversation-understanding/decision-trail-specialist-contracts-v0.md` and `.json` | Four current specialist roles: conversation shape, likely action, friction/lost value, conservative fan-in. |
| Product Delta eval lane | `docs/evals/*`, `engine/system_b/product_delta_*`, `reviews/codex-assisted/*` | Offline evaluation of whether Lolla changed the decision compared with vanilla strong-model advice. |
| Boundary lint | `engine/system_b/product_delta_boundary_lint.py` | Deterministic overclaim/privacy/non-claim lint for current evidence artifacts. |

The repo now has an early offline Decision Work Receipt artifact. PR105 defined
the schema, PR106 inventoried sources, PR107 added deterministic process-shape
metadata, PR108 added challenge coverage, and PR109 composes those pieces into
the first sparse receipt. It is still offline, checked-in-safe, and not runtime
integrated.

## Product Problem

When someone shares an AI-generated memo, plan, or recommendation, the receiver
usually sees only the final output.

That is not enough for serious work.

The receiver should be able to ask:

- Was this one prompt or a real conversation?
- What context was provided?
- Were PDFs, pasted notes, links, or prior artifacts involved?
- Did the system challenge the answer?
- Were multiple options explored?
- Was a premortem, counterframe, or stop rule used?
- Did the recommendation change after pressure?
- Did the final memo drop something important from the conversation?
- What remains missing or unresolved?

Today, Lolla has pieces of that answer, but not one product object that exposes
the work trail.

## Product Goal

Create an offline, reviewable Decision Work Receipt that can eventually sit
beside a final AI-assisted output.

The receipt should answer:

1. **What was the task or decision?**
2. **What inputs were available?**
3. **What happened in the conversation process?**
4. **What challenge did Lolla apply?**
5. **What changed between vanilla and revised output?**
6. **What was lost, dropped, or unresolved?**
7. **How review-ready is this work trail?**
8. **What must not be claimed?**

The receipt should make the process inspectable without pretending the answer
is correct.

## Non-Goals

This PRD does not authorize:

- running `$lolla` as part of offline receipt generation;
- invoking the Lolla skill;
- provider/model calls from deterministic exporters or validation;
- archive mutation;
- runtime behavior changes in the first implementation phase;
- prompt changes in the first implementation phase;
- `SKILL.md` changes in the first implementation phase;
- reading raw/private content into checked-in artifacts;
- PDF ingestion, OCR, embeddings, chunking, GraphRAG, memory, or graph DB work;
- answer-quality scoring;
- an LLM judge;
- automatic labels;
- agent action authorization;
- decision-improvement proof.

## Key Principle

The same Lolla doctrine applies:

```text
Messy interpretation belongs to LLMs or humans.
Deterministic code preserves custody, source refs, missingness, validation,
redaction/private availability, and non-claims.
```

The Decision Work Receipt may classify **process evidence**. It must not grade
answer correctness.

Good language:

```text
review-ready work trail
thin process evidence
challenged-and-revised output
source-supported but unvalidated
human review needed
```

Bad language:

```text
correct answer
approved decision
safe to act
quality score
Lolla won
```

## Missing Product Elements

The current system is missing three first-class product surfaces.

### 1. Source And Context Inventory

Question:

> What information went into the work?

The inventory should capture:

- conversation capture availability;
- structured runtime artifacts;
- raw/private artifacts present but redacted;
- pasted context candidates;
- file/PDF/link references if visible;
- private local artifacts available but not exported;
- missing or malformed artifacts;
- whether each source was read, not read, redacted, or unavailable.

Important constraint:

> PDFs and attachments are not first-class archived source objects today.

If PDF text was pasted into the conversation, it may exist inside
`conversation.txt`. If a PDF was referenced externally but not archived by the
runtime, the current system cannot reliably prove its contents were available
or used. The v0 receipt must make that explicit.

### 2. Conversation Process Map

Question:

> What happened over the turns?

The map should eventually show:

- turn count;
- user/assistant turn distribution;
- whether this was one-shot or multi-turn;
- where new context appeared;
- where the user corrected or redirected the AI;
- where options were introduced or abandoned;
- where the assistant challenged, agreed, or softened;
- where a premortem, postmortem, counterframe, or stop rule appeared;
- where final output diverged from earlier conversation.

Safe deterministic v0 can record turn/process metadata only when the content is
available in an allowed mode.

Messy fields such as "the assistant challenged the user" require LLM or human
interpretation.

### 3. Decision Work Receipt

Question:

> Can a reviewer see how much work stands behind the final output?

The receipt should combine:

- source/context inventory;
- conversation process map;
- Decision Trail report;
- challenge coverage;
- Product Delta read or reference;
- missingness and redaction status;
- process-evidence readiness;
- non-claims;
- human follow-up questions.

This is the future customer-facing wrapper.

## Proposed Receipt Shape

The future receipt should have a schema such as:

```json
{
  "schema_version": "lolla.decision_work_receipt.v0",
  "receipt_metadata": {},
  "source_context_inventory": {},
  "conversation_process_map": {},
  "challenge_coverage": {},
  "decision_trail_summary": {},
  "product_delta_summary": {},
  "process_evidence_readiness": {},
  "missingness_and_redaction": {},
  "human_review": {},
  "non_claims": [],
  "boundary": {}
}
```

This should be a new artifact family, not a replacement for
`lolla.decision_trail_report.v0`.

The Decision Work Receipt should reuse or reference the Decision Trail report
where possible.

PR105 now defines this contract at:

```text
docs/conversation-understanding/decision-work-receipt-v0.json
```

That schema is a contract only. It does not implement exporter behavior, read
archives, call models, change runtime behavior, or change the Lolla skill.

## Process Evidence Readiness

The receipt may classify the **work trail**, not the answer.

Suggested v0 values:

- `insufficient_process_evidence`
- `one_shot_or_thin_process`
- `multi_turn_unreviewed_process`
- `challenged_and_revised_process`
- `decision_trail_review_ready`
- `human_review_ready`
- `human_reviewed`

These values must be carefully scoped.

They mean:

> How inspectable is the process behind the output?

They do not mean:

> How good is the output?

Deterministic exporters may only assign values supported by artifact presence,
mode, and validation status. If semantic judgment is required, the field should
be `requires_llm_interpretation` or `requires_human_review`.

## Current Constraints And Trade-Offs

### Checked-In Safe Mode Is Honest But Thin

Checked-in safe mode cannot copy raw conversations, memos, revised answers,
provider text, private ledgers, or local absolute paths.

That means it can show source presence, status, and missingness, but not the
full decision story.

### Local-Private Mode Is Useful But Dangerous

Local-private mode can inspect richer artifacts from completed runs, including
raw/private text when explicitly allowed.

But local-private outputs must be unsafe-for-commit by default, and checked-in
summaries must remain paraphrase-only and privacy-safe.

### Attachments Are Not Currently First-Class

The current archive does not have a durable attachment/PDF manifest.

The v0 receipt should not pretend it can prove file usage. It can only record:

- file references visible in captured text;
- local/private artifacts that were archived;
- missing first-class attachment custody.

A future runtime change may be needed if attachment provenance becomes
product-critical.

### Turn Process Is Not The Same As Thought Quality

A longer conversation is not automatically better.

Five turns can be shallow. One turn can be precise. A premortem can be useful
or performative.

The process map must avoid rewarding length by itself.

### Challenge Coverage Is Not Correctness

If Lolla ran all audit lanes, the answer was challenged. That does not prove
the revised answer is good.

Challenge coverage is process evidence only.

### Do Not Start With Runtime Changes

The first phase should be offline and read-only, like the Decision Trail and
Product Delta lanes.

Only after offline review shows a specific missing source or process signal
should the project change `SKILL.md`, runtime prompts, archive behavior, or lane
preparation.

## Implementation Sequence

The sequence below assumes the current latest Decision Trail stop point is
PR104.

### PR105 Decision Work Receipt PRD And Schema v0

Type: docs/schema/tests.

Goal:

Define `lolla.decision_work_receipt.v0` without implementing an exporter.

Likely files:

- `docs/conversation-understanding/decision-work-receipt-prd-v0.md`
- `docs/conversation-understanding/decision-work-receipt-v0.json`
- `tests/test_decision_work_receipt_schema.py`

What to include:

- receipt metadata;
- source/context inventory shape;
- conversation process map shape;
- challenge coverage shape;
- Decision Trail and Product Delta refs;
- process evidence readiness vocabulary;
- missingness/redaction statuses;
- non-claims and boundary metadata.

Must not:

- implement exporter code;
- read archives;
- add model calls;
- change runtime;
- change prompts;
- touch `SKILL.md`;
- add answer-quality scoring.

Validation:

- JSON parses with `jq`;
- schema tests enforce boundary fields and forbidden authority fields;
- PR78 boundary lint passes on docs/schema;
- docs link checks pass.

Current state:

```text
Implemented in this docs/schema slice.
```

### PR106 Source And Context Inventory Exporter v0

Type: read-only code/tests/docs.

Goal:

Build the first deterministic source/context inventory over a completed run
directory.

Likely files:

- `engine/system_b/decision_work_receipt.py`
- `scripts/evals/build_decision_work_receipt.py`
- `tests/test_decision_work_receipt.py`
- `docs/conversation-understanding/decision-work-receipt-source-inventory-v0.md`

Implementation approach:

- Reuse the artifact knowledge already present in
  `engine/system_b/decision_trail_report.py`:
  `STRUCTURED_ARTIFACTS` and `RAW_ARTIFACTS_NOT_READ`.
- Record structured artifacts, raw/private artifacts, and generated artifacts.
- Distinguish `missing`, `malformed`, `available_but_redacted_in_safe_mode`,
  and `available_in_private_artifact_not_exported`.
- Output only outside the run directory.
- Checked-in safe mode only for the first exporter.

Known limitation:

This PR cannot reliably detect actual PDF/file usage unless that usage appears
in existing archived artifacts. It should record this as a source-custody gap,
not solve it.

Must not:

- parse raw conversation in checked-in safe mode;
- infer file usage from vague prose;
- read private content into checked-in fixtures;
- mutate archives;
- run `$lolla`.

Validation:

- fixture run directory smoke;
- output path guard;
- privacy scan;
- no local absolute paths in checked-in fixtures;
- tests for missing vs redacted/private statuses.

Current state:

```text
Implemented as a checked-in-safe read-only exporter.
```

Implementation note:

- [Decision Work Receipt Source Inventory v0](decision-work-receipt-source-inventory-v0.md)

### PR107 Conversation Process Map Shell v0

Type: read-only code/tests/docs.

Current state:

```text
Implemented as a checked-in-safe read-only exporter slice.
```

Goal:

Add deterministic conversation-process metadata to the receipt without semantic
interpretation.

Likely scope:

- turn count when structured turn data is available;
- user/assistant count;
- one-shot vs multi-turn evidence status;
- capture health;
- capture adequacy refs;
- whether raw conversation is redacted/private in checked-in mode;
- semantic process fields marked `requires_llm_interpretation`.

Likely code location:

- extend `engine/system_b/decision_work_receipt.py`;
- use `ConversationContext`/`extraction.json` only where already structured and
  safe;
- do not parse raw text in checked-in safe mode.

Semantic fields to leave unfilled:

- new context added;
- options explored;
- challenge moments;
- assistant agreement or pushback;
- premortem/postmortem usage;
- abandoned paths;
- final divergence.

Must not:

- classify conversation quality deterministically;
- reward turn count as quality;
- create process score;
- change runtime capture.

Validation:

- tests for one-turn and multi-turn fixture metadata;
- tests that semantic fields remain `requires_llm_interpretation`;
- lint and privacy checks.

Implementation note:

- [Decision Work Receipt Conversation Process Map v0](decision-work-receipt-conversation-process-map-v0.md)

### PR108 Challenge Coverage Map v0

Type: read-only code/tests/docs.

Current state:

```text
Implemented as a checked-in-safe read-only exporter slice.
```

Goal:

Represent which Lolla challenge surfaces exist for a completed run.

Inputs:

- `result.json`;
- `reasoning_trace.json`;
- `evaluation.json`;
- `agent_result.json`;
- optional audit artifacts already present in archive.

What to expose:

- whether expected audit artifacts exist;
- whether lane outputs are present or missing;
- whether run health/capture adequacy weakens challenge evidence;
- whether optional deeper pressure-check state is absent, rested, or present;
- refs to relevant artifacts.

Must not:

- decide whether the challenge was good;
- score lanes;
- infer that full lane coverage means good advice;
- change lane prompts.

Validation:

- fixture with all expected artifacts;
- fixture with missing lane artifact;
- fixture with degraded evaluation health;
- non-claim tests.

Implementation note:

- [Decision Work Receipt Challenge Coverage Map v0](decision-work-receipt-challenge-coverage-map-v0.md)

### PR109 Decision Work Receipt Exporter v0

Type: read-only code/tests/docs.

Status: implemented in PR109.

Goal:

Compose the first sparse `lolla.decision_work_receipt.v0` from:

- source/context inventory;
- conversation process map shell;
- challenge coverage map;
- optional reference to Decision Trail report;
- optional reference to Product Delta review artifacts;
- process evidence readiness;
- non-claims.

This should be a sparse, honest receipt. It does not need to be beautiful yet.

Suggested process readiness rules:

- If required archive artifacts are missing: `insufficient_process_evidence`.
- If only one prompt/conversation evidence is visible: `one_shot_or_thin_process`.
- If multi-turn evidence exists but no Lolla challenge refs exist:
  `multi_turn_unreviewed_process`.
- If Lolla challenge artifacts exist but semantic Decision Trail fields are
  mostly missing: `challenged_and_revised_process`.
- If Decision Trail/Product Delta review refs exist and missingness is legible:
  `decision_trail_review_ready`.
- Human review values remain unfilled unless a human review artifact exists.

The rules must be artifact-readiness rules, not answer-quality rules.

Must not:

- create a correctness grade;
- claim the work was good;
- claim the answer improved;
- approve agent action;
- integrate with runtime.

Validation:

- generated temp receipt;
- `jq` parse;
- focused pytest;
- PR78 or successor boundary lint;
- link/privacy/whitespace checks.

Implementation note:

- [Decision Work Receipt Exporter v0](decision-work-receipt-exporter-v0.md)

### PR110 Decision Work Receipt Fixture Review v0

Type: docs/review fixture/tests.

Status: implemented in PR110.

Goal:

Review whether the sparse receipt is useful, too thin, too confusing, or too
authoritative-looking.

Review questions:

- Can a reader tell what inputs existed?
- Can a reader distinguish missing from private/redacted?
- Can a reader tell whether this was one-shot, multi-turn, challenged, or
  review-ready?
- Can a reader see what was changed by Lolla?
- Can a reader see what still requires LLM or human interpretation?
- Does the receipt make the work more inspectable or merely more impressive?

Must not:

- add new semantic reads;
- run another local-private specialist pilot by default;
- call models;
- claim product proof.

Validation:

- review JSON has conservative metadata;
- no human validation unless actually performed;
- no score fields;
- source refs resolve;
- overclaim lint passes.

Implementation note:

- [Decision Work Receipt Fixture Review v0](decision-work-receipt-fixture-review-v0.md)

### PR111 Decision Work Receipt Decision Gate v0

Type: docs-only decision gate.

Status: implemented in PR111.

Goal:

Decide what kind of change is justified by PR105-PR110 evidence.

Possible outcomes:

1. **Outcome A: Receipt shell is enough for now**

   Use the sparse receipt as an internal/workflow artifact, no runtime changes.

2. **Outcome B: Improve runtime capture**

   Only if source/context inventory shows the archive fails to preserve
   load-bearing inputs such as attached files, pasted docs, or document refs.

3. **Outcome C: Improve prompts or `SKILL.md`**

   Only if review shows users/operators are not producing enough process
   evidence or the skill does not explain the receipt/report expectations.

4. **Outcome D: Improve deterministic lane preparation**

   Only if challenge coverage shows audit lanes are not receiving or preserving
   the right structured information.

5. **Outcome E: Add bounded specialist interpretation**

   Only if the receipt is structurally useful but too sparse without LLM
   interpretation of process events.

6. **Outcome F: Simplify**

   If the receipt feels like bureaucracy or creates overtrust.

PR111 should decide one path and stop.

Implementation note:

- [Decision Work Receipt Decision Gate v0](decision-work-receipt-decision-gate-v0.md)

## How This Feeds Back Into Lolla

The receipt should become a diagnostic tool for improving the system.

If it shows missing inputs:

> consider runtime/archive capture changes later.

If it shows weak challenge coverage:

> inspect lane preparation and prompts.

If it shows shallow conversations:

> consider `SKILL.md` or user guidance changes.

If it shows useful deltas are hard to see:

> improve Decision Trail and Product Delta report shape.

If it shows repeated lost-value risk:

> improve the Lolla audit prompts or specialist contracts to preserve momentum,
> simplicity, courage, and user-specific ambition.

But the receipt itself should remain a report surface, not the system that
judges the answer.

## Open Questions To Resolve During Implementation

1. Should source/context inventory live inside the Decision Trail exporter or a
   new Decision Work Receipt exporter?

   Initial recommendation: new exporter that reuses Decision Trail artifact
   constants or extracts them into a shared helper only when duplication becomes
   painful.

2. Should process evidence readiness be deterministic?

   Initial recommendation: only artifact-readiness tiers are deterministic.
   Semantic process interpretation requires LLM/human status.

3. Should attachment/PDF provenance be solved now?

   Initial recommendation: no. First expose the gap. Add runtime attachment
   custody only if PR110/PR111 prove it is product-critical.

4. Should the Product Delta boundary lint be generalized?

   Initial recommendation: not in PR105. Reuse it if it works. Generalize only
   if Work Receipt artifacts repeatedly need checks outside Product Delta.

5. Should this become part of `$lolla` runtime?

   Initial recommendation: no. Keep it offline until the receipt shape proves
   useful and not overtrust-inducing.

## Success Criteria

The Decision Work Receipt phase is successful if a reviewer can quickly answer:

- What information went into this work?
- Was this one-shot or multi-turn?
- Was it challenged by Lolla?
- What changed after challenge?
- What evidence is missing or private?
- What still needs LLM or human interpretation?
- What must not be claimed?

It fails if:

- it looks like an approval badge;
- it rewards long conversations over good work;
- it hides missing inputs;
- it treats clean artifacts as correctness;
- it becomes a parallel product disconnected from current Decision Trail and
  Product Delta code;
- it requires runtime changes before the offline report shape is understood.

## Recommended Next Step

Stop the Decision Work Receipt build lane here.

PR111 selects Outcome A:

> Keep the sparse receipt as a useful internal/workflow artifact. Do not add a
> separate Work Receipt interpretation system yet.

Future semantic interpretation should come through the existing Decision Trail
and Product Delta lanes when justified. The Work Receipt should wrap those
artifacts, not become a parallel judge or semantic pipeline.

## Post-Gate Bridge

PR112 implements one narrow bridge after the PR111 closure gate.

The trigger was a real-run smoke over completed archives: the receipt could
show challenged-and-revised process evidence, but Decision Trail and Product
Delta summaries remained `not_supplied` because those reports are usually
generated outside archive run folders.

PR112 keeps Outcome A intact. It does not add Work Receipt-specific
interpretation. It only lets the offline receipt CLI accept externally
generated checked-in-safe Decision Trail and Product Delta report JSON files:

```bash
python3 scripts/evals/build_decision_work_receipt.py \
  --run-dir <archive-run-dir> \
  --decision-trail-report /tmp/decision_trail_report.json \
  --product-delta-report /tmp/product_delta_report.json \
  --out /tmp/decision_work_receipt.json \
  --pretty
```

The receipt records only sanitized source metadata, hash/byte count, source
refs, and availability status. It does not copy report content, local absolute
paths, raw/private run content, or semantic conclusions into the receipt.

Read more:

- [Decision Work Receipt External Report Attachments v0](decision-work-receipt-external-report-attachments-v0.md)
