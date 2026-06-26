# Semantic Extraction Review Pilot v0

This note records a small local review of four modern current-main Lolla
archives. It asks a different question from the PR20-PR24 extraction-mechanics
work:

> Do the current artifacts preserve the important reasoning work of the
> conversation, not just clean quote/capture/turn-reference mechanics?

This is an evidence note only. It does not implement a new IR, change runtime
behavior, change prompts, change quote validation, change provider-boundary
policy, add graph memory, add embeddings, add chunking, add an LLM judge, or
touch `SKILL.md`.

## Reviewed Runs

The review used the four modern baseline archives:

| case | run_id | extraction mechanics | agent readiness |
|---|---|---|---|
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` | good extraction, good/full capture, 0 quote fabrication, 0 turn-ref issues | partial: `vendor_boundary_reasoning_leak` |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` | good extraction, good/full capture, 0 quote fabrication, 0 turn-ref issues | partial: `vendor_boundary_reasoning_leak` |
| `implement-price-increase-three` | `20260626T132915Z_49172d` | good extraction, good/full capture, 0 quote fabrication, 0 turn-ref issues | partial: `vendor_boundary_reasoning_leak` |
| `five-person-saas-team` | `20260626T133147Z_99712f` | good extraction, good/full capture, 0 quote fabrication, 0 turn-ref issues | partial: `vendor_boundary_reasoning_leak` |

Artifacts inspected per run:

- `conversation.txt`
- `extraction.json`
- `extraction_adequacy_report.json`
- `result.json`
- `revised.txt`
- `memo.md`
- `reasoning_trace.json`
- `evaluation.json`
- `agent_result.json`

The checked-in review does not copy raw transcript text, revised-answer text,
memo prose, model messages, provider reasoning details, or absolute local
archive paths.

## Review Labels

Labels:

- `captured`: the current artifacts preserve enough evidence to inspect the
  element.
- `partially_captured`: the element is present, but compressed, spread across
  artifacts, weakly grounded, or not tied to the revised answer lineage.
- `missing`: the element matters for the run but is not preserved clearly enough
  for review.
- `not_applicable`: the element did not materially arise in the reviewed
  conversation.

## Semantic Element Matrix

| semantic element | beta workflow | coffee pre-sale | pricing renewal | five-person SaaS team |
|---|---|---|---|---|
| real decision / question | captured | captured | captured | captured |
| live constraints | captured | captured | partially_captured | captured |
| user values or stated priorities | partially_captured | partially_captured | partially_captured | partially_captured |
| changed constraints introduced mid-conversation | captured | captured | captured | captured |
| dropped or under-carried threads | captured | partially_captured | partially_captured | partially_captured |
| assistant overconfidence or too-clean closure | captured | captured | partially_captured | captured |
| main counter-pressure | captured | captured | captured | captured |
| why the revised answer changed | captured | captured | partially_captured | partially_captured |
| unanswered dimensions | partially_captured | captured | captured | partially_captured |
| actionability boundaries / do-not-act-before conditions | captured | captured | captured | captured |

## Compact Run Findings

| run | what current artifacts preserve well | semantic gaps or weak spots | primary source artifacts | likely gap type |
|---|---|---|---|---|
| `launch-limited-beta-workflow` | Decision, constraints, mid-conversation pressure, enforceable action boundaries, revised-answer change reason, and a dropped sales-momentum thread are inspectable. | User values are inferable rather than explicitly modeled. Several important elements live across result cards, revised answer, and memo rather than in extraction. | `extraction.json`, `result.json`, `revised.txt`, `memo.md`, `extraction_adequacy_report.json` | extraction plus lineage |
| `initiate-pre-sale-coffee` | Decision, constraints, demand-test logic, action gates, counter-pressure, unanswered questions, and revised-answer change reason are inspectable. | The cafe/wholesale thread is not classified as a dropped thread even though the memo later separates it. User priorities are partly implicit in constraints. | `extraction.json`, `result.json`, `revised.txt`, `memo.md` | extraction plus memo |
| `implement-price-increase-three` | Decision, renewal timing, support-load tension, mid-conversation pushback, counter-pressure, and action boundaries are inspectable. | The extraction misses a distinct customer-usage/quality constraint and does not represent user values beyond operational constraints. The memo/revised layer is intentionally thin, so the reason for revision is only generic. | `extraction.json`, `result.json`, `memo.md`, `structural_coverage_card` in `result.json` | extraction plus revised-answer |
| `five-person-saas-team` | Decision, resource constraints, partner commitment gate, counter-pressure, and action boundaries are inspectable. | The partner's refusal-to-commit thread changes the decision, but extraction keeps it mostly inside synthesized position/reasoning passages rather than as a changed constraint or stance event. The memo/revised layer is thin. | `extraction.json`, `result.json`, `revised.txt`, `memo.md` | extraction plus stance/lineage |

## What Current Extraction Already Does Well

The current artifact chain is stronger than the raw `extraction.json` shape
alone suggests.

The extraction pass reliably preserved:

- the headline decision,
- the main live constraints,
- original framing,
- quote-validated reasoning passages,
- dropped-thread detection when a thread is explicit enough,
- clean turn references in the reviewed modern runs.

The broader artifact set also preserved useful semantic pressure:

- `frame_pressure_card` captured option-space collapse or framing assumptions.
- `structural_coverage_card` surfaced covered and uncovered dimensions.
- `delta_card` and `audit_summary` sometimes exposed assistant overconfidence,
  contrast effects, incentive pressure, or too-clean closure.
- `revised.txt` and `memo.md` often explained what changed after pressure.
- `reasoning_trace.json` indexed the relevant artifacts for custody.

This means the next step should not be a broad replacement of the current
conversation pipeline.

## Recurring Semantic Gaps

The gaps are mostly about semantic coverage and lineage, not quote validation.

1. `synthesized_position` has no source grounding in all four modern adequacy
   reports. It is useful as a summary, but it is not directly inspectable as a
   source-grounded stance record.

2. Live constraints are turn-reference grounded, not span grounded. That is
   adequate for coarse review, but weak when the exact wording or changed
   constraint matters.

3. User values and priorities are usually inferred from constraints. The
   current extraction does not separately preserve "what the user appears to
   care about" versus "what operational constraint is present."

4. Changed constraints are visible to a human reviewer, but not consistently
   typed. A later user objection or partner/customer condition can change the
   decision without becoming an explicit changed-constraint record.

5. Dropped or under-carried threads are inconsistently represented. The beta
   workflow run caught an explicit dropped sales-momentum thread. The coffee,
   pricing, and partner runs had under-carried threads that were preserved
   elsewhere but not classified as dropped threads.

6. Assistant overconfidence and too-clean closure are usually present in
   `audit_summary`, `delta_card`, or `bullshit_profile`, not in extraction.
   That is acceptable for audit output, but it means semantic review has to
   inspect multiple artifacts.

7. Revised-answer lineage is uneven. The two richer runs preserve why the
   answer changed in `revised.txt` and `memo.md`; the two compact baseline runs
   preserve only a generic revision rationale.

8. Unanswered dimensions are better preserved by `structural_coverage_card` and
   memo questions than by extraction. Extraction itself does not provide a
   compact "semantic gaps" view.

## Source Artifact Coverage

| semantic need | current best source | evidence preservation | gap if any |
|---|---|---|---|
| headline decision | `extraction.json` | enough for review | none observed |
| live constraints | `extraction.json` plus `extraction_adequacy_report.json` | enough for coarse turn-level review | span grounding absent |
| user priorities | `conversation.txt`, `result.json`, `memo.md` | inspectable manually | not first-class extracted field |
| changed constraints | `conversation.txt`, `extraction.json`, `result.json` | inspectable manually | not consistently typed |
| dropped threads | `extraction.json`, `memo.md`, `structural_coverage_card` | uneven | extraction under-detects under-carried threads |
| assistant overconfidence | `audit_summary`, `delta_card`, `bullshit_profile` | often inspectable | scattered outside extraction |
| main counter-pressure | `result.json`, `revised.txt`, `memo.md` | enough for review | lineage not machine-compact |
| revised-answer change reason | `revised.txt`, `memo.md` | strong in richer runs, thin in compact smokes | uneven memo/revised detail |
| unanswered dimensions | `structural_coverage_card`, `memo.md` | often strong | not joined to extraction |
| actionability boundaries | `extraction.json`, `revised.txt`, `memo.md` | enough for review | no explicit boundary field |

## Decision Outcome

Outcome: **B. Current artifacts preserve mechanics but lose or scatter important
semantic hinges.**

The evidence does not justify building `conversation_understanding_ir.v0` yet.
It does justify a narrow semantic coverage report that reads the current
artifacts and says what is preserved, what is weakly grounded, and what is
missing.

There is also a small **C-shaped** signal: existing specialist work, especially
assistant stance extraction and live-constraint span grounding, may be relevant.
But the next step should evaluate whether those existing pieces fill the
observed gaps before adding a broader durable IR.

## Recommended Next Slice

Recommended next slice:

`semantic_coverage_report_v0`

Reason: the review found repeated semantic review gaps that are visible from
existing artifacts but not summarized in one deterministic place. A narrow
report can measure those gaps before Lolla adds new extraction prompts, new IR
schemas, graph memory, embeddings, or runtime cost.

The report should stay deterministic where possible and answer:

- Is the decision captured?
- Are live constraints present, turn-grounded, span-grounded, or missing?
- Is there any first-class user-values signal?
- Are changed constraints or later user pushback represented?
- Are dropped/under-carried threads represented?
- Is assistant stance or recommendation lineage represented?
- Where are unanswered dimensions preserved?
- Does the revised answer have an inspectable change reason?
- Which artifact currently owns each semantic element?

Only after that report shows repeated missing fields should Lolla consider an
offline conversation-understanding prototype.

## What Should Not Be Built Yet

- no `conversation_understanding_ir.v0`,
- no graph DB,
- no embeddings,
- no chunking work,
- no production extraction rewrite,
- no extraction prompt change,
- no quote-validation change,
- no provider-boundary policy change,
- no LLM judge,
- no answer-quality scoring,
- no automatic human-review labels,
- no `SKILL.md` change.

## Provider-Boundary Separation

All four runs remained agent-degraded because of
`vendor_boundary_reasoning_leak`. That is real, but it is separate from this
review. Provider-boundary policy affects whether an agent should automatically
use a run. It does not explain the semantic extraction gaps above.
