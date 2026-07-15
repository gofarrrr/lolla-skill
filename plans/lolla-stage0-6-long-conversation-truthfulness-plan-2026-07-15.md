# Lolla Stage 0.6 long-conversation truthfulness plan

Date: 2026-07-15

Status: completed provider-free prerequisite repair; no provider execution

Canonical parent: `7f427629822ba4b828a42d697ddb2df4e9bf4955`

## One falsifiable question

When the initial extraction job uses Lolla's existing bounded view for a long
conversation, do every downstream custody surface and cold-start document tell
the same exact truth: the authoritative conversation is preserved, the initial
extraction view is partial, and the omitted range is known?

The repair fails if a 140-message transcript can still produce any ordinary
result, health record, agent result, extraction-adequacy report, or reasoning
trace that implies full initial-extraction coverage or treats the source itself
as truncated.

## Scope

Allowed:

- correct deterministic turn accounting around the existing 80,000-character
  extraction-view threshold;
- propagate the existing omission metadata into capture adequacy and run
  health;
- distinguish authoritative source preservation from bounded extraction
  coverage in archive-facing artifacts;
- add one provider-free end-to-end regression using a local fake boundary;
- correct current handoff, skill, operations, and roadmap documentation;
- preserve a legacy `run_health.capture_truncated` boolean only as a documented
  compatibility alias.

Forbidden:

- raising or removing the threshold;
- changing prompts, schemas sent to providers, model, route, reasoning, retry,
  fallback, privacy, or cost behavior;
- adding a new semantic reader, summary hierarchy, retrieval strategy, rolling
  window, or long-context experiment;
- changing graph selection, pressure lanes, reconsideration, Decision Work,
  Teacher, Observatory, R4, or R5;
- reading private archives or making provider calls.

## Intended invariant

```text
authoritative conversation.txt
  = complete available user/assistant prose
  = never replaced by the bounded extraction view

initial extraction source coverage
  = full when <= 80,000 characters
  = first 3 + last 15 message blocks when > 80,000 characters
  = partial with exact omitted range when bounded

later conversation-native pressure input
  = authoritative full conversation turns

all receipts
  = distinguish these three statements
```

The threshold is measured in characters, not words or tokens. It is a local
engineering policy, not a provider context limit and not evidence that the
omitted material was irrelevant.

## Test-first sequence

1. Run the actual extraction CLI against a 140-message, over-threshold
   development fixture with a local fake boundary.
2. Require exact `140 total / 18 processed / 122 omitted` metadata and exact
   opening, omitted, and recent windows.
3. Require the actual pipeline entrypoint to degrade health under the truthful
   `extraction_processing_view_partial` issue while preserving the legacy
   boolean as a compatibility alias only.
4. Require agent result, extraction-adequacy report, and reasoning trace to
   reproduce the same omitted count.
5. Update current documentation and run focused, Stage 0, frozen R4, and full
   repository verification.

## Stop condition

Stop after truthful deterministic custody is restored. A materially different
long-conversation interpretation architecture requires a new founder decision,
its own falsifier, and—if provider-facing—a separately frozen authorization.

