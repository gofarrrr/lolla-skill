# Lolla Stage 0.6 long-conversation truthfulness result

Date: 2026-07-15

Status: completed provider-free; local implementation result

Decision: `long_conversation_source_coverage_truth_restored_without_claiming_semantic_completeness`

Provider calls: 0

Provider cost: `$0.00`

## Executive result

Lolla did not delete or overwrite long conversations, but it did misreport how
much of them the initial extraction job saw. Above 80,000 characters,
`conversation.txt` remained complete and later conversation-native pressure
lanes loaded the full transcript, while the initial extraction call received a
first-3-plus-last-15 message view. The processing-view JSON recorded that
partial coverage, but the capture manifest used by run health and archived
reports did not. A long run could therefore preserve the full source and still
report full extraction coverage.

That deterministic custody defect is repaired. The authoritative source,
bounded extraction view, run health, agent result, extraction-adequacy report,
and reasoning trace now agree about the source boundary and exact omissions.
This is a truthfulness repair, not a long-context comprehension repair.

## What changed

### Exact message accounting

The transcript header is now parsed as preamble rather than counted as a
conversation message. Message blocks are recognized only from complete
`[Turn N] USER:` and `[Turn N] ASSISTANT:` markers. The existing bounded policy
therefore means exactly three opening message blocks plus fifteen recent
message blocks.

The development fixture contains 140 message blocks and exceeds 80,000
characters. Its exact bounded coverage is now:

- authoritative messages: 140;
- messages supplied to initial extraction: 18;
- omitted middle messages: 122;
- processed opening window: messages 1–3;
- omitted window: messages 4–125;
- processed recent window: messages 126–140.

Before this repair, the header was accidentally counted as one of the first
three message blocks. Metadata claimed 18 retained and 123 omitted even though
the provider-visible view contained only 17 actual messages.

### Metadata propagation

When bounding applies, the extraction manifest now carries:

- `truncation_applied`;
- original and bounded character lengths;
- total, retained, and omitted message counts;
- first and last retention bounds;
- a plain-language reason.

`capture_adequacy` is rebuilt from that exact manifest. Downstream run health
therefore cannot silently return `good/full/0 omitted` for the bounded initial
extraction.

### Truthful health language

New runs emit `extraction_processing_view_partial` as the degraded health
issue. Its axis is extraction, and its trust impact says that the complete
authoritative conversation is preserved while the initial extracted scaffold
may miss constraints or changes introduced in omitted middle messages.

`run_health.capture_truncated` remains as a deprecated compatibility boolean.
For new runs it means “the bounded initial extraction view was partial”; it
must not be rendered as “conversation.txt was truncated.” It is no longer the
issue code emitted in `run_health.issues`.

Run health also exposes:

- `authoritative_conversation_preserved`;
- `extraction_processing_view_status`;
- `processing_view_omitted_turns`.

### Archive-facing source coverage

`agent_result.json` now carries a separate `lolla.source_coverage.v1` object.
It distinguishes:

- whether the authoritative conversation was preserved;
- whether the initial extraction view was full or partial;
- the extraction processing strategy;
- authoritative, processed, and omitted message counts.

The agent-facing warning now says that the source is preserved and identifies
the bounded initial extraction limitation. Existing extraction-adequacy and
reasoning-trace builders reproduce the same exact counts because the corrected
manifest now reaches them.

## What this means in realistic terms

The threshold is 80,000 characters, not 80,000 words. Its word equivalent is
not fixed because language, formatting, code, links, and transcript markers
vary. It normally represents a substantial multi-turn conversation, but it is
reachable in serious working sessions and should not be dismissed as a purely
theoretical edge case.

The practical risk is narrower than “Lolla forgets everything after 80,000
characters” and broader than “nothing matters because the file is archived”:

- complete available user/assistant prose remains preserved;
- later conversation-native pressure lanes receive the full turn sequence;
- the initial decision-structure scaffold sees only the opening and recent
  messages;
- that scaffold can influence later pressure, so a decisive middle change may
  still be underrepresented;
- every current receipt now declares that limitation instead of presenting a
  clean full-coverage run.

## What did not change

- The 80,000-character policy and first-3-plus-last-15 task shape are
  unchanged.
- No prompt, provider-visible schema, model, route, seed, reasoning policy,
  retry, fallback, privacy, or budget behavior changed.
- No claim was made that first-plus-last is semantically adequate.
- No rolling summary, hierarchical memory, retrieval layer, multi-window
  reader, larger context request, or model comparison was added.
- No graph, pressure-lane, reconsideration, sidecar, Teacher, Observatory,
  R4, or R5 behavior changed.
- No frozen experiment evidence changed.
- No private archive was inspected.
- No real-user usefulness evidence was created.

## Evidence classification

The 140-message transcript is a generated development fixture. It proves exact
mechanical custody and propagation under a declared shape. It does not prove
that Lolla correctly interprets a real 140-message conversation, that the four
pressure lanes recover every meaningful middle turn, or that users find the
result valuable.

The remaining semantic question is therefore explicit: whether the current
bounded extraction scaffold materially harms pressure quality on real long
conversations. That is not answered here and should not be smuggled into Stage
1, whose job is checked-in-safe interface truthfulness.

## Product and roadmap consequence

Stage 0.6 closes a prerequisite defect discovered while preparing for the
Stage 1 truthfulness review. Stage 1 may now evaluate whether a cold reviewer
understands the authority and missingness labels, including this new source
coverage boundary. Stage 1 still makes no provider call and cannot establish
long-context semantic quality.

A later long-conversation architecture decision should begin only if Stage 1
or consent-bound real-run evidence shows that this partial initial scaffold is
a material user problem. That decision should compare bounded alternatives
from first principles; it should not begin by silently increasing the
threshold.

## Verification

The end-to-end regression invokes the real extraction and pipeline entrypoints
with local fake provider boundaries, then builds archive-facing agent result,
extraction adequacy, and reasoning trace objects. It requires all surfaces to
agree on `140 / 18 / 122` and requires zero network transport.

Final results:

- Stage 0.6 and current-handoff focused slice: 93 passed.
- Frozen R4 separated-surface and replay slice: 37 passed.
- Complete repository suite: 4,974 passed.
- Additional subtests: 93 passed.
- Failures: 0.
- Warning: one pre-existing `datetime.utcnow()` deprecation warning in
  `scripts/stability_check.py`.
- Stage 0 register: valid; 25 components, 24 connections, 17 Constitution
  rules, 26 Decision Trail field groups, and 636 assigned implementation
  files.
- Public cold-start handoff: valid; ten orientation questions and 78 checked
  current-entrypoint links.
- Changed Markdown links: 87 checked, zero missing.
- Changed Python compilation: passed.
- Changed register JSON parsing: passed.
- Frozen A2 custody tests: passed; no frozen evidence changed.
- Added-material secret-pattern scan: zero matches.
- Git object integrity: passed; three harmless dangling blobs were reported.
- Provider calls: 0.
- Provider cost: `$0.00`.

The first repository-wide invocation ran before the implementation checkpoint
and reported 20 failures. Every failure was the same historical Decision Work
guard checking that `git status -- SKILL.md scripts/skill` was empty; the
intentionally edited `SKILL.md` was still uncommitted. After the exact change
was committed, the full suite passed. This was a worktree-state assertion, not
a semantic, runtime, frozen-evidence, or test regression.
