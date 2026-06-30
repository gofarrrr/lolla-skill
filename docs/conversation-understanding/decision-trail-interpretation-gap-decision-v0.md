# Decision Trail Interpretation Gap Decision v0

Status: PR89 docs-only decision gate
Date: 2026-06-29

## Decision

Selected outcome: **Outcome B: Add narrow offline LLM specialist enrichment**.

PR86 through PR88 show that the current artifact chain is enough for a useful
Decision Trail custody shell, but not enough for the full Decision Trail
product surface.

The PR87 exporter should stay. It makes source custody, missingness, redaction,
private-only availability, and non-claims inspectable. But PR88 shows that the
fields users care about most in an answer-plus-process report remain outside
deterministic reach.

The next work should therefore be narrow, offline, LLM-backed interpretation
under deterministic custody. It should not be runtime integration, a broad
conversation-understanding platform, a judge, or a graph/memory system.

## Contradicting Evidence First

There is a real argument for stopping at PR87/PR88 for now. The exported report
is readable enough to show:

- which structured artifacts exist;
- which raw/private artifacts were deliberately not read;
- which fields populated from safe structured sources;
- which fields are missing;
- which fields require LLM interpretation;
- what must not be claimed.

That is useful. It prevents the system from silently pretending to know more
than it knows.

There is also a real argument that PR88 is too weak as evidence. It used
checked-in safe fixtures only. No local-private shadow review was run. That
means PR88 can inspect report shape and missingness behavior, but it cannot
prove how useful a Decision Trail report would feel over a real private archive
with the raw conversation, revised answer, memo, and operator context available
locally.

Both points matter. They do not cancel each other.

The conclusion is narrower:

> The current report shell is worth keeping, but it is not enough to explain the
> decision story users care about.

## What PR88 Showed

The structured fixture populated six safe semantic sections:

- `conversation_understanding_summary`;
- `decision_question`;
- `constraints`;
- `audit_pressure_summary`;
- `structural_delta`;
- `unresolved_questions`.

The same report left eight product-load-bearing sections as requiring
interpretation:

- `vanilla_likely_next_action`;
- `revised_likely_next_action`;
- `option_map`;
- `stakeholders`;
- `values_or_priorities`;
- `assistant_influence`;
- `useful_noisy_friction`;
- `lost_value`.

That is the key evidence. The deterministic shell can show what exists and
what is missing. It cannot honestly fill the missing decision-story fields.

## Most Useful Fields

The most useful PR87/PR88 fields are custody and orientation fields:

- `source_artifacts`;
- `custody_flags`;
- `trace_context`;
- `decision_question`;
- `conversation_understanding_summary`;
- `constraints`;
- `audit_pressure_summary`;
- `structural_delta`;
- `unresolved_questions`;
- `field_population_policy`;
- `non_claims`.

These fields help a reader understand the process envelope. They do not decide
whether the revised answer improved the decision.

## Most Missing Fields

The most missing fields are the ones closest to the product claim:

- What was the user likely going to do before Lolla?
- What is the revised answer likely asking the user to do?
- Which options were live?
- Which option was dropped, downgraded, or preserved?
- Which stakeholders or obligations mattered?
- Which user values or priorities governed the answer?
- Did the assistant shape the user's framing?
- Was the friction useful or noisy?
- What value did the revised answer lose?

These are not artifact-health questions. They are messy interpretation
questions.

## Redacted Or Private-Available Fields

PR88 also showed that checked-in safe mode can distinguish missing from
private/redacted:

- raw conversation content can be present but redacted;
- memo text can be present but redacted;
- revised-answer text can be present but redacted;
- operator/private material can be present locally but not exported.

That distinction is valuable. It means a sparse checked-in report is not always
saying "the run lacked this material." Sometimes it is saying "this material
may exist, but this report mode did not expose it."

PR89 should preserve that distinction in all next work.

## Why Deterministic Rules Are Insufficient

Deterministic code can preserve:

- artifact presence;
- schema version;
- hashes;
- source refs;
- status;
- missingness;
- redaction/private availability;
- validation results;
- non-claims.

Deterministic code cannot interpret a messy strategic conversation without
becoming brittle or dishonest. It cannot safely decide:

- the user's likely action;
- the live option set;
- stakeholder obligations;
- values/priorities;
- assistant influence;
- useful versus noisy friction;
- lost value;
- whether the revised answer is better.

Trying to solve those with deterministic rules would turn Lolla into exactly
the wrong thing: a fake judge of messy conversation.

## Selected Path

The next phase should add **bounded offline LLM specialist enrichment** for the
missing Decision Trail fields.

This means:

- offline, after a run exists;
- no `$lolla` invocation;
- no runtime prompt changes;
- no archive mutation;
- no provider calls inside deterministic validation;
- no broad decision-quality judge;
- no answer-quality score;
- no automatic labels;
- no agent action authorization.

The LLM work should be narrow and typed. Deterministic code should then
preserve source refs, field status, uncertainty, disagreement, missingness, and
non-claims.

## First Specialist Family

The first specialist family should be limited to Decision Trail interpretation.
It should not become a general conversation memory, graph, or evaluation
platform.

Recommended roles:

1. **Conversation Shape Reader**
   Identify the decision question, live options, option status, constraints,
   stakeholders, values/priorities, assistant influence, dropped threads, and
   uncertainty.

2. **Likely Action Reader**
   Separately identify vanilla likely next action and revised likely next
   action, with source refs and uncertainty. It must be allowed to say
   `unclear`.

3. **Friction And Lost Value Reader**
   Identify useful friction, noisy friction, missing friction, and lost value.
   It must preserve cases where the revised answer became more cautious but
   not more decision-useful.

4. **Conservative Fan-In Reader**
   Preserve disagreement between the specialist reads. It must not vote,
   average, score, certify, approve, or turn agreement into correctness.

This family is narrow because it fills only the fields PR87/PR88 could not
honestly populate. It does not judge answer quality.

## Rejected Alternatives

### Outcome A: Exporter v0 Is Enough For Now

Rejected for the full product surface.

Accepted only as a custody shell. PR87/PR88 are enough to show artifact health
and missingness. They are not enough to explain the full decision process.

### Outcome C: Design `conversation_understanding_ir.v0`

Rejected for now.

A durable intermediate IR may be useful later, but PR88 does not prove that we
need a broad new conversation artifact. The narrower next question is whether
bounded specialist reads can populate the missing fields under custody.

### Outcome D: Strengthen Existing Extraction

Rejected for now.

Live extraction is already doing compact conversation understanding inside the
runtime. Expanding it before an offline specialist pass risks overloading the
live task, increasing runtime fragility, and moving too much interpretation
into the default skill path too early.

### Outcome E: Stop And Simplify

Rejected for now.

The report shell is not useless. It makes the right gaps visible. The better
move is to keep the shell and add narrow offline interpretation only where the
evidence shows deterministic custody must stop.

## What Would Falsify This Path

The specialist enrichment path should be stopped or simplified if:

- specialists mostly restate PR87 fields without adding usable interpretation;
- specialists over-infer from compressed safe context;
- specialists convert uncertainty into confident-looking prose;
- specialists cannot preserve live options, values, assistant influence, or
  lost value without raw/private context;
- fan-in smooths disagreement into a cleaner story;
- the report becomes more impressive without becoming more reviewable;
- PR78-style lint cannot prevent overclaim language;
- local-private review shows the report is too heavy or too confusing for real
  use.

## Work Explicitly Deferred

PR89 does not approve:

- runtime Decision Trail generation;
- `$lolla` integration;
- local-private exporter mode;
- a broad `conversation_understanding_ir.v0`;
- graph DB, memory, embeddings, chunking, or GraphRAG;
- answer-quality scoring;
- automatic labels;
- broad LLM judging;
- agent action authorization;
- dashboard or UI work;
- human validation claims.

## Recommended Next PR

Recommended next slice:

**PR90 Decision Trail Interpretation Specialist Contracts v0**

Type: docs/schema-only.

Purpose:

Define typed contracts for the four narrow offline specialist reads:

- conversation shape;
- likely actions;
- friction/lost value;
- conservative fan-in.

PR90 should define input modes, output fields, status vocabulary, source refs,
uncertainty, disagreement preservation, and non-claims. It should not build a
packet builder, run specialists, call models, change runtime, or mutate
archives.

Completion note: PR90 is implemented by
[`decision-trail-specialist-contracts-v0.md`](decision-trail-specialist-contracts-v0.md),
[`decision-trail-specialist-contracts-v0.json`](decision-trail-specialist-contracts-v0.json),
and focused tests in
[`test_decision_trail_specialist_contracts.py`](../../tests/test_decision_trail_specialist_contracts.py).

PR91 is implemented by
[`decision-trail-specialist-packet-builder-v0.md`](decision-trail-specialist-packet-builder-v0.md),
[`decision_trail_specialist_packets.py`](../../engine/system_b/decision_trail_specialist_packets.py),
[`build_decision_trail_specialist_packets.py`](../../scripts/evals/build_decision_trail_specialist_packets.py),
and focused tests in
[`test_decision_trail_specialist_packets.py`](../../tests/test_decision_trail_specialist_packets.py).

PR92 is implemented by
[`decision-trail-specialist-trap-set-v0.md`](decision-trail-specialist-trap-set-v0.md),
[`decision-trail-specialist-trap-set-v0.json`](decision-trail-specialist-trap-set-v0.json),
and focused tests in
[`test_decision_trail_specialist_trap_set.py`](../../tests/test_decision_trail_specialist_trap_set.py).

PR93 is implemented by
[`decision-trail-specialist-dry-run-v0.md`](decision-trail-specialist-dry-run-v0.md),
[`review.json`](../../reviews/codex-assisted/decision-trail-specialist-dry-run-v0/review.json),
and focused tests in
[`test_decision_trail_specialist_dry_run.py`](../../tests/test_decision_trail_specialist_dry_run.py).

PR94 is implemented by
[`decision-trail-specialist-path-decision-v0.md`](decision-trail-specialist-path-decision-v0.md)
and focused tests in
[`test_decision_trail_specialist_path_decision.py`](../../tests/test_decision_trail_specialist_path_decision.py).

PR94 selects PR95 Decision Trail Local-Private Packet Mode v0 as the next
recommended slice. It rejects a broader checked-in-safe specialist batch for
now because PR88, PR91, and PR93 already show the safe fixtures are too thin
for the product-load-bearing interpretation fields.

PR95 is implemented by
[`decision-trail-local-private-packet-mode-v0.md`](decision-trail-local-private-packet-mode-v0.md),
the local-private mode extension in
[`decision_trail_specialist_packets.py`](../../engine/system_b/decision_trail_specialist_packets.py),
the CLI update in
[`build_decision_trail_specialist_packets.py`](../../scripts/evals/build_decision_trail_specialist_packets.py),
and focused tests in
[`test_decision_trail_local_private_packets.py`](../../tests/test_decision_trail_local_private_packets.py).
It keeps the work offline and explicit: local-private packets require an
operator-selected run directory and a non-repo output path, record whether
private text was included, and still stop before specialist outputs or fan-in.
Post-review alignment clarifies the local-private source boundary: PR88
fixture review is lineage-only, selected run artifacts and the PR90 schema
define packet content, raw-content inclusion flags reflect actual included
artifacts, and repo-local fixture/schema inputs avoid local absolute path leaks.

## Final Read

PR86 through PR88 did the right thing: they made absence legible. PR89 decides
not to pretend that legible absence is enough.

The next product question is no longer "can deterministic code export a
Decision Trail shell?" It can.

The next product question is:

> Can bounded LLM interpretation fill the missing decision-story fields while
> deterministic custody keeps the output humble, inspectable, and unable to
> masquerade as proof?

After PR95, the immediate next question is narrower:

> Do local-private packets provide enough usable context, without unacceptable
> privacy or overclaim risk, to justify the first bounded specialist-output
> batch?

That should be answered by a local-private packet smoke/review before any
specialist outputs are generated.
