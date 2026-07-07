# Observatory Agent Memory Cold Reader Layer Design v0

Status: design-only. No renderer change in this slice.

Date: 2026-07-07

Decision gate: `proceed_to_agent_memory_orientation_renderer_spike`

## Purpose

The agent-memory Markdown export is meant to help a future agent understand a
completed run without needing the original chat session. The latest cold-read
experiment showed that fresh agents can understand the file, recover the main
decision structure, and respect the non-claims.

The same experiment also exposed a real design risk: if we add a polished
summary at the top, the file may stop behaving like a run artifact and start
behaving like an answer. A future agent may anchor on the summary, skim the
source material, and agree with the generated interpretation instead of
challenging it.

This document defines a safer target: an orientation layer, not a conclusion
layer.

## Core Principle

The top layer must help a cold reader know how to read the artifact. It must not
replace the reader's own inspection of the transcript and source artifacts.
More plainly: the layer must not replace the reader's own inspection.

Preferred framing:

```text
Orientation, not conclusion.
```

The layer may say:

```text
The system's current synthesis appears to be X. Treat this as a hypothesis to
check against the transcript, memo, revised answer, custody map, and readiness
warnings below.
```

The layer must not say:

```text
The correct interpretation is X.
```

## Product Risk

Name: `summary_anchoring_or_artifact_poisoning`

Definition: the generated Markdown becomes less useful as run memory because a
top-level summary makes future readers too likely to accept the system's prior
interpretation.

Failure mode:

1. A future agent opens the export.
2. The top section gives a clean, plausible interpretation.
3. The agent treats the interpretation as the run's meaning.
4. The agent uses raw transcript and telemetry only to confirm the summary.
5. Weaknesses, contradictions, dropped threads, or missingness are under-read.

The design goal is to reduce that failure mode while still making the file
usable for future sessions.

## What The Layer May Do

The cold-reader layer may:

- identify the file as a generated reasoning-audit memory view;
- explain that the transcript is the primary source for what was said;
- explain that memo, revised answer, selected lenses, and telemetry are generated
  run outputs, not proof;
- provide a suggested reading order;
- list the system's synthesis only as a hypothesis to verify;
- point to the raw transcript, memo, revised answer, custody map, and readiness
  sections;
- name practical unresolved questions clearly as inferred from the transcript
  when they are not supplied by structured artifacts;
- explain why run-health labels can coexist, such as `healthy`, `warn`,
  `inspect_first`, `thin`, and `future_review_ready: false`;
- repeat privacy warnings before any raw transcript section.

## What The Layer Must Not Do

The cold-reader layer must not:

- declare the final interpretation as correct;
- label a recommendation as proven;
- hide, replace, or shorten the full transcript in private exports;
- move raw run material below a product conclusion without warning;
- collapse source, synthesis, inference, and telemetry into one voice;
- add new business facts not present in source artifacts;
- convert inferred open questions into system-supplied facts;
- treat selected mental models as proof;
- treat suppressed models as noise;
- claim product proof, human validation, answer correctness, advice correctness,
  or action authorization;
- authorize runtime behavior, provider calls, new runs, or automatic action.

## Proposed Shape

If implemented later, the layer should be compact and clearly labeled:

```text
## Cold Reader Orientation

This is a generated memory view over one completed reasoning-audit run. It
contains source material, generated run outputs, telemetry, custody, missingness,
and non-claims. The transcript is the primary source for what was said.

## How To Read Without Anchoring

1. Read this orientation only as a map.
2. Read the decision situation.
3. Inspect the transcript sections that contain the main correction or conflict.
4. Compare the memo and revised answer against the transcript.
5. Treat selected lenses as system behavior, not proof.
6. Check readiness warnings and missing artifacts before relying on the file.

## System Synthesis To Verify

The system's current synthesis appears to be:
...

Do not treat this as ground truth. Use it as a hypothesis to test against the
raw transcript and source artifacts below.

## Practical Questions To Recheck

These are inferred from the transcript, not supplied as structured final
questions:
...
```

The layer should remain short. It should orient the reader, then hand control
back to source material.

## Placement Rules

The orientation layer should appear after frontmatter and before detailed run
sections.

It should not remove existing sections:

- `What This File Is`;
- `What This File Is Not`;
- `How This File Was Produced`;
- `Source Artifact Map`;
- `Privacy And Non-Claims`;
- `Conversation Interpretation`;
- `Run Health And Readiness`;
- `Agent Instructions For Future Use`;
- `Full 1:1 Conversation Transcript`.

The transcript remains the primary source object in private exports.

## Evidence And Source Labeling Rules

Every item in the orientation layer needs an explicit evidence posture:

| Label | Meaning | Allowed wording |
| --- | --- | --- |
| `source` | copied or directly grounded in source text | "The transcript says..." |
| `summary` | compressed from one artifact | "The memo summarizes..." |
| `synthesis_to_verify` | generated cross-artifact orientation | "The system's synthesis appears to be..." |
| `inferred_question` | reader-useful question inferred from the transcript | "A future analyst should recheck..." |
| `missing_or_unknown` | known absence or insufficient evidence | "The file does not settle..." |

The renderer should avoid unlabeled statements that sound like authoritative
facts.

## Anti-Laziness Mechanisms

The layer should include small frictions that push a future agent back to the
raw material:

- use "hypothesis to verify" language;
- reference transcript turns or source sections for key claims when available;
- put "What this does not settle" near the top;
- include a verification checklist;
- label inferred questions as inferred;
- keep the orientation compact enough that it cannot become the whole artifact;
- repeat that the file is not proof of advice correctness.

These mechanisms are not decorative. They are the safety design.

## Cold-Read Experiment Signal

Three context-free agents were given the generated Markdown export and asked to
explain what it was, what it contained, how it could help, what options were
visible, and what was weak.

Consistent useful signal:

- they understood it as a private conversation-memory export;
- they recognized it as generated from a reasoning-audit run;
- they recovered the public-beta versus private-pilot decision;
- they recovered the 900-person versus 220-person prospect path;
- they noticed the reasoning shift after user correction;
- they recognized transcript, memo, revised answer, custody, lenses, missingness,
  and non-claims.

Consistent weakness:

- the current recommendation is spread across several sections;
- open questions are empty even when the transcript implies unresolved questions;
- run-health labels need plain-language interpretation;
- lens and suppressed-signal sections are too dense for a cold reader;
- missing artifact consequences are not explained;
- the file needs a clearer way to orient without replacing source inspection.

## Design Decision

Proceed only with an orientation layer that is explicitly anti-anchoring.

Do not proceed with a polished executive summary that presents the system's
interpretation as the run's meaning.

Decision gate for a future implementation slice:

`proceed_to_agent_memory_orientation_renderer_spike`

The implementation spike should update tests before renderer behavior changes.

## Boundary

This design:

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
