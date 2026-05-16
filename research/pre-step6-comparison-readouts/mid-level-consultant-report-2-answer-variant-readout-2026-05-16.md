# Pre-Step-6 Answer-Variant Readout: Mid-Level Consultant Report

Date: 2026-05-16

Status: manual research comparison v0. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output. This is not legal advice.

Template:

```text
research/pre-step6-comparison-readout-template-2026-05-16.md
```

Fixture:

```text
research/pre-step6-comparison-fixtures/mid-level-consultant-report-2-20260429T144611Z.md
```

## Readout Header

```text
case_id: mid-level-consultant-report-2
source_run_id: mid-level-consultant-report-2__20260429T144611Z
fixture_path: research/pre-step6-comparison-fixtures/mid-level-consultant-report-2-20260429T144611Z.md
readout_type: answer-variant comparison
date: 2026-05-16
reviewer: Codex manual research pass
```

## Case Shape

```text
primary reasoning shape: hard boundary / option expansion / misfit discard
secondary reasoning shapes: counsel-incentive testing, Wednesday protocol, internal-channel distinction
what makes this case high-clutter: useful channel nuance can accidentally weaken immediate safety rules
what would make this case a bad test: if variants become legal-channel advice instead of counsel-gated decision support
```

## Inputs Checked

```text
current_control_summary_present: yes
raw_artifact_count: 5
bundle_index_present: yes
source_excerpt_count: 4
fixture_caps_respected: yes
public_machinery_terms_in_fixture_final_prompt: no
```

## Arm Expectations

```text
Arm A expected risk: keeps the safety sequence but misses counsel-incentive and internal-channel distinctions.
Arm B expected risk: adds all useful cautions and may bury the first three actions.
Arm C expected risk: protects hard boundaries, but may over-structure an already stressful answer.
```

## Final-Answer Variant Notes

These are compact answer cores, not full product responses.

### Arm A: Current Control

```text
The sequence still holds: document what you saw tonight on a personal device,
contact 2-3 whistleblower attorneys this week, tell your wife in broad strokes,
attend Wednesday normally, do not confront the partner, do not investigate
privately, and do not access systems unusually. The commitment boundary is
counsel review: engaging counsel is reversible; choosing internal versus
external reporting is not something to decide before a lawyer has seen the
facts.

Treat your 60-65% confidence in general counsel as a gut signal, not a decision
standard. The lawyer's first job is evidence sufficiency and channel selection,
not just filing mechanics.
```

Arm A is strong on safety but misses two practical refinements.

### Arm B: Raw Artifacts

```text
Keep the safety sequence intact: document tonight, contact counsel, do not
confront, do not investigate, do not access systems unusually. But add four
checks. First, ask each attorney whether they have advised internal-first in
similar cases; contingency incentives may pull toward filing. Second, prepare a
Wednesday protocol: if the partner raises the encounter, do not deny, do not
elaborate, change subject, and avoid being alone with him if possible without a
memorable deviation. Third, ask counsel to distinguish general counsel, audit
committee, and external regulator as different channels. Fourth, define career
tripwires such as staffing exclusion, review changes, PIP, or client removal.

Do not use leverage or negotiation framing. This is a reporting sequence, not a
bargaining problem.
```

Arm B adds useful material but compresses several concerns into a checklist that
could crowd the immediate actions.

### Arm C: Indexed Bundle

```text
Keep the order simple: document tonight, call 2-3 whistleblower attorneys, tell
your wife the broad outline, and do nothing unusual at work. No confrontation,
no private investigation, no unusual system access, no channel choice before
counsel.

Two refinements make that sequence safer. First, choose counsel with one bias
test: ask, "In what kinds of cases have you advised internal-first or audit
committee-first, and why?" If the answer is never, that does not mean the lawyer
is wrong, but it tells you what incentive structure you are buying.

Second, make Wednesday boring on purpose. If the partner mentions the encounter,
do not deny and do not explain. Use a bland exit line, change the subject, and
avoid being alone with him if you can do that without creating a memorable
deviation. Save channel distinctions and retaliation tripwires for the lawyer
call; they are useful, but they must not displace tonight's documentation and
counsel step.
```

Arm C adds the highest-value refinements while keeping the first actions clear.

## Primary Criteria

| Criterion | Score | Evidence |
| --- | --- | --- |
| Source-grounded force survives | tie | All arms preserve documentation, counsel, and no-confrontation/no-investigation boundaries. |
| Unsupported precision decreases | tie | None of the arms invent legal probabilities or timelines. |
| Hard boundaries survive | C wins | Arm C foregrounds the boundaries before adding refinements. |
| Conflicts remain visible when unresolved | C wins | Arm C keeps counsel necessary while adding a counsel-incentive test. |
| Duplicates are demoted | tie | Duplicate pressure is not the central shape. |
| Quiet artifacts do not bloat answer | C wins | Power-dynamics discard stays private; tripwires are deferred to counsel rather than expanded. |
| Public prose has no machinery leakage | tie | None of the answer cores use internal machinery terms. |
| Answer is at least as clear as control | C wins | Arm C is slightly longer than A but gives a clearer Wednesday protocol and counsel-selection question. |

## Secondary Criteria

| Criterion | Score | Evidence |
| --- | --- | --- |
| Private handoff is easier to audit | C wins | The bundle identifies safety boundaries before supporting nuances. |
| Artifact IDs remain traceable | C wins | The bundle maps counsel, Wednesday, channel, tripwire, and discard pressure separately. |
| Overclaim risks visible before writing | C wins | The bundle blocks legal-channel advice without counsel and rejects negotiation framing. |
| Step 6 remains free to reject bundle | tie | Arm C uses only the highest-value refinements and keeps tripwires compact. |

## Bundle-Specific Check

```text
Did the bundle improve final prose, not just notes? yes
Did the bundle demote duplicates without deleting receipts? not central in this case
Did the bundle preserve conflict instead of hiding it? yes
Did the bundle prevent overclaim? yes
Did the bundle make the answer shorter or clearer? clearer than raw artifacts, slightly longer than control
Which bundle fields carried any lift? hard_boundaries, conflicts_or_tensions, quiet_or_discard_candidates, final_reasoner_instruction
```

## Kill-Condition Check

```text
raw artifacts tied bundle: no
bundle hid conflict: no
Step 6 obeyed index instead of arbitrating: no
answer got longer or more caveated: no compared with raw artifacts; slightly longer than control
bundle required broad context: no
benefit was only operator traceability: no
```

## Verdict

```text
C wins
```

## Decision

```text
proceed_to_next_fixture
```

## Notes

This is the highest-risk fixture because a bad bundle could soften the safety
sequence. The manual Arm C variant won only because it kept the first actions
and boundaries first, then added two refinements. If a real final reasoner made
the answer more legalistic or less direct, this should become a tie or loss.
