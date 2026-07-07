# Observatory Agent Memory Orientation Renderer Spike v0

Status: implemented renderer spike, locally validated.

Date: 2026-07-07

Decision gate: `proceed_to_agent_memory_verification_checklist_spike`

## Purpose

This slice tests whether the agent-memory Markdown export can include a small
cold-reader orientation layer without turning the file into a polished summary
that future agents over-trust.

The prior design doc named the core risk:

```text
summary_anchoring_or_artifact_poisoning
```

The implementation here intentionally avoids a top-level answer. The orientation
layer says where generated synthesis appears later, labels it as something to
verify, and pushes the reader toward transcript, memo, revised answer, custody,
and readiness warnings.

## Renderer Change

The Markdown renderer now emits:

```text
## Cold Reader Orientation
```

immediately after:

```text
# Conversation Memory
```

and before:

```text
## What This File Is
```

The section includes:

- `Orientation, not conclusion.`;
- a decision-situation line;
- a pointer that generated synthesis appears later in `Conversation
  Interpretation`, `What Changed`, `Memo`, and `Revised Answer`;
- `hypotheses to verify, not ground truth`;
- a reading order that starts with transcript inspection;
- reliance warnings for raw conversation, missing artifacts, evaluation,
  caller readiness, trace adequacy, and future review readiness;
- a reminder that empty structured open-question rows do not mean there is no
  remaining uncertainty;
- a short `Key Checks Before Trusting Any Interpretation` list.

The section does not include a top-level generated-answer bullet. The test suite
explicitly bans:

```text
- Generated synthesis:
```

## A/B Cold-Read Experiment

The spike generated two private local exports from the same completed run:

| Variant | Lines | Bytes | Purpose |
| --- | ---: | ---: | --- |
| baseline | 698 | 50,957 | Existing export without the orientation layer. |
| oriented v1 | 732 | 52,854 | First orientation attempt with a top generated-synthesis line. |
| oriented v2 | 740 | 52,914 | Final orientation attempt without a top generated-answer bullet. |

No model/provider calls were made by the renderer. The cold-read reports were
diagnostic subagent reads of local Markdown files, not human validation and not
product proof.

### Baseline Signal

Baseline readers understood the file as a generated conversation-memory export.
They recovered the decision structure and used the transcript heavily. They also
asked for a verification-oriented top layer:

- a cold-start verification checklist;
- a reliance checklist;
- clearer handling of missing artifacts;
- better explanation of readiness warnings;
- source pointers for claims that future agents may rely on.

### Oriented v1 Signal

The first orientation attempt helped readers orient, but it still included a
polished top-level generated synthesis. Oriented readers noticed the risk:

- the section could anchor a future reader before transcript inspection;
- the top synthesis could conflict subtly with later memo/revised-answer nuance;
- the artifact still needed a claim-verification table rather than a stronger
  summary.

This was a useful failure. The implementation was revised before commit.

### Oriented v2 Signal

The final implementation removes the top generated-answer bullet and keeps the
orientation layer as a source-inspection guide.

Final cold-read checks confirmed:

- readers still inspect transcript, memo, and revised answer;
- readers treat synthesis as something to verify;
- readers notice readiness and missingness warnings;
- readers do not treat the orientation as the answer.

Residual risk:

- readers still see the artifact as polished and formal;
- generated synthesis still appears early in later sections;
- the orientation creates less anchoring than v1, but not zero anchoring risk;
- future improvement should attach claims to evidence instead of adding a
  stronger summary.

## What This Proves And Does Not Prove

Useful signal:

- a small orientation layer can make the export easier to enter;
- putting verification prompts near the top is safer than putting a polished
  answer near the top;
- fresh readers consistently ask for claim-level verification support.

Non-claims:

- this is not human validation;
- this is not product proof;
- this does not prove the advice is correct;
- this does not prove the answer is correct;
- this does not authorize action;
- this does not authorize runtime integration;
- this does not prove the orientation layer is final UX.

## Recommended Next Slice

The next improvement should not add a stronger summary. It should add a compact
verification checklist or claim-evidence table.

Possible table:

| Claim | Best evidence in this file | Still verify |
| --- | --- | --- |
| Audit logs were brittle | transcript turn or source excerpt | current audit-log status |
| Support was overloaded | transcript turn or source excerpt | current staffing and load |
| Private proof program is recommended | memo and revised answer | current prospect state |
| 900-person prospect should not get default priority | memo and revised answer | payment/procurement terms |

Decision gate:

```text
proceed_to_agent_memory_verification_checklist_spike
```

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.
