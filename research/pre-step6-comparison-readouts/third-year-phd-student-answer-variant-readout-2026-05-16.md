# Pre-Step-6 Answer-Variant Readout: Third-Year PhD Student

Date: 2026-05-16

Status: manual research comparison v0. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Template:

```text
research/pre-step6-comparison-readout-template-2026-05-16.md
```

Fixture:

```text
research/pre-step6-comparison-fixtures/third-year-phd-student-20260430T140800Z.md
```

## Readout Header

```text
case_id: third-year-phd-student
source_run_id: third-year-phd-student__20260430T140800Z
fixture_path: research/pre-step6-comparison-fixtures/third-year-phd-student-20260430T140800Z.md
readout_type: answer-variant comparison
date: 2026-05-16
reviewer: Codex manual research pass
```

## Case Shape

```text
primary reasoning shape: conflict / constraint / fallback viability
secondary reasoning shapes: pseudo-quantitative base-rate pressure, quiet option expansion
what makes this case high-clutter: option 3 is attractive, but the fallback may decay and the Silva/data constraint may remain unresolved
what would make this case a bad test: if all arms merely say "probe Silva" without testing fallback executability
```

## Inputs Checked

```text
current_control_summary_present: yes
raw_artifact_count: 4
bundle_index_present: yes
source_excerpt_count: 4
fixture_caps_respected: yes
public_machinery_terms_in_fixture_final_prompt: no
```

## Arm Expectations

```text
Arm A expected risk: preserves a good answer but leaves fallback executability under-integrated.
Arm B expected risk: may surface all gates but make the answer feel like stacked caveats.
Arm C expected risk: may preserve tension well, but primary labels could over-constrain the final answer.
```

## Final-Answer Variant Notes

These are compact answer cores, not full product responses.

### Arm A: Current Control

```text
The advisor-first sequence still holds: do not go to Silva or the committee
with a specific proposal your advisor has not seen. The live move is a low-cost
constraint probe, not a commitment. This weekend's work should test whether
the single-cell/evolution niche is crowded and whether another data modality
could give the same career upside with less external dependency. Then ask Silva
only whether her lab is in principle open to methods collaboration and what
data-sharing would look like.

Keep the 18-month reversal trigger, but make it evidence-specific: crowded
niche, thin collaboration, missing real-data analysis by month 6, and no
publishable result by month 18 should each trigger a pivot conversation.
```

Arm A is coherent, but the fallback target remains too assumed.

### Arm B: Raw Artifacts

```text
Do not treat the 18-month pivot as real unless option 1 will still exist when
you need it. The first advisor conversation should therefore do two things:
ask whether option 3 is politically supportable, and ask what would preserve a
modified option-1 fallback if the single-cell path stalls.

Silva is not a solved resource. Treat the probe as a constraint test: usable
data access, collaboration depth, co-advising or committee role, and timing.
If those do not become concrete, option 3 is still mostly a story.

Also, keep the 20-30% base-rate number private as humility. It is not a
calibrated estimate unless you can define the reference class. Option expansion
should widen the search frame, not become a fourth active dissertation track
unless the fourth path uses existing lab infrastructure and lowers dependency.
```

Arm B improves the fallback and Silva gates, but it reads as a sequence of
warnings.

### Arm C: Indexed Bundle

```text
The right next move is not "choose option 3 with safeguards." It is to protect
two gates before option 3 becomes your dissertation bet.

First gate: the fallback has to remain real. In the advisor conversation, ask
what would preserve a modified option-1 path if the hybrid direction stalls:
funding, supervision, dataset access, and a timeline that still works with his
retirement. A pivot trigger that fires after the fallback is gone is theater.

Second gate: Silva/data access has to become concrete. Before you spend
political capital on the committee, test whether there is usable data, a real
collaboration role, and enough support to carry a dissertation. Keep the
single-cell success-rate numbers as humility, not as a decision weight; the
reference class is too loose. Widen the literature search for nearby paths, but
do not let "more options" become parallel-prototyping drift under a 3-month
deadline.
```

Arm C preserves the conflict and turns the fallback into an explicit gate
without bloating the answer.

## Primary Criteria

| Criterion | Score | Evidence |
| --- | --- | --- |
| Source-grounded force survives | tie | All arms preserve advisor timing, Silva constraint, and 3-month deadline. |
| Unsupported precision decreases | C wins | Arm C explicitly keeps success-rate numbers as humility rather than decision weight. |
| Hard boundaries survive | C wins | Arm C makes fallback executability and concrete data access the two gates. |
| Conflicts remain visible when unresolved | C wins | Arm C preserves the attraction of option 3 while refusing to treat fallback and Silva as solved. |
| Duplicates are demoted | tie | Duplicate pressure is not the main shape here. |
| Quiet artifacts do not bloat answer | C wins | Option expansion stays as search-frame widening, not a new track. |
| Public prose has no machinery leakage | tie | None of the answer cores use internal machinery terms. |
| Answer is at least as clear as control | C wins | Arm C is clearer than Arm B and more boundary-aware than Arm A. |

## Secondary Criteria

| Criterion | Score | Evidence |
| --- | --- | --- |
| Private handoff is easier to audit | C wins | The bundle shows why fallback and Silva are primary, while base-rate and option expansion stay supporting/quiet. |
| Artifact IDs remain traceable | C wins | The bundle maps the answer pressure to fixture artifact IDs. |
| Overclaim risks visible before writing | C wins | The base-rate gate prevents pseudo-quantitative use. |
| Step 6 remains free to reject bundle | tie | The manual pass used the bundle structure but did not enumerate every artifact. |

## Bundle-Specific Check

```text
Did the bundle improve final prose, not just notes? yes
Did the bundle demote duplicates without deleting receipts? not central in this case
Did the bundle preserve conflict instead of hiding it? yes
Did the bundle prevent overclaim? yes
Did the bundle make the answer shorter or clearer? yes, compared with raw artifacts
Which bundle fields carried any lift? conflicts_or_tensions, hard_boundaries, rethinking_questions
```

## Kill-Condition Check

```text
raw artifacts tied bundle: no, but raw artifacts were close
bundle hid conflict: no
Step 6 obeyed index instead of arbitrating: no
answer got longer or more caveated: no
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

This is a narrow manual win. The raw artifacts contained the same ingredients,
but the bundle made the two controlling gates easier to see and prevented the
base-rate and option-expansion material from taking over the answer.
