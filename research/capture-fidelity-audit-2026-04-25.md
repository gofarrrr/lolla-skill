# Phase 0.1 Capture Fidelity Audit

**Date:** 2026-04-25  
**Branch:** `feat/phase-0.1-capture-fidelity-audit`  
**Scope:** current `/lolla` Step 1 capture, `scripts/run_extract.py` capture validation, `engine/system_b/conversation_loader.py`, and `scripts/run_pipeline.py` run-health surfacing.  
**Status:** Draft for PM review at Task 6.10.

## PM-Review Summary

No open `blocker_for_ir_provenance` was observed in the sampled corpus cases. The current capture path is sufficient for Phase 1 provenance work if Phase 1 treats the captured transcript as the canonical artifact and limits provenance claims to the user/assistant prose turns that actually appear in that artifact.

Minimum capture contract for Phase 1:

- The raw conversation file must contain a parseable `CONVERSATION: N turns, X user messages, Y assistant responses` header.
- Every included message must use exact turn markers: `[Turn N] USER:` or `[Turn N] ASSISTANT:`.
- `capture_health` must be `good` or explicitly reviewed if `degraded` / `unknown`; `capture_critical` blocks the audit before OpenRouter spend.
- Provenance references must identify turns by at least `(turn_index, speaker)` or by a new sequence id; `turn_index` alone is not unique because each displayed turn usually has both a user and assistant message.
- Any omitted or truncated content must be carried as explicit capture metadata or a visible transcript marker. Provenance must not claim coverage over omitted middle turns, tool outputs, system/developer messages, or other excluded material.

Open fix plan: none required before Phase 0.5. Blocking failure classes exist in the model below, but the currently implemented capture-critical decline path already prevents those cases from silently entering the pipeline.

## What The Current Capture Path Records

### Step 1 transcript artifact

`SKILL.md` Step 1 instructs the orchestrator to write a plain text file:

```text
CONVERSATION: {N} turns, {X} user messages, {Y} assistant responses

[Turn 1] USER:
{user message text}

[Turn 1] ASSISTANT:
{assistant response text}
```

Recorded surfaces:

- speaker labels: `USER` and `ASSISTANT`
- displayed turn ids: numeric `[Turn N]` labels
- user prose
- assistant prose responses
- a header declaring total turns, user messages, and assistant responses
- file byte count and marker count printed by the shell snippet after writing

Important shape note: the displayed `turn_index` is not a unique message id. A normal exchange has `[Turn 1] USER:` and `[Turn 1] ASSISTANT:`. The current `ConversationContext.Turn` therefore needs `(turn_index, speaker)` or sequence position for unique drill-back.

### Extraction capture validation

`scripts/run_extract.py` reads the conversation file and runs `_validate_conversation_capture()` before any OpenRouter call.

Recorded `capture_manifest` fields:

- `actual_user_turns`
- `actual_assistant_turns`
- `char_length`
- `declared_turns`
- `declared_user`
- `declared_assistant`

Recorded `capture_health` statuses:

- `good`: header matches parsed body and assistant turns are present
- `degraded`: mismatch exists, but fewer than half of assistant turns are missing
- `critical`: zero assistant responses or more than half of declared assistant responses are missing
- `unknown`: no parseable header, so counts cannot be compared

Recorded `capture_warnings`:

- user-count mismatch
- assistant-count mismatch, including severity text for critical assistant loss
- no assistant responses
- extraction truncation warning
- quote-validation retry failure
- quote-validation fabricated passage drops
- invalid canonical keys when present in historical payloads

### Truncation records

`run_extract.py` truncates conversations over `MAX_CONVERSATION_CHARS = 80_000` after capture validation and before the extraction call.

If this truncation fires, `capture_manifest` also records:

- `truncation_applied`
- `truncation_reason`
- `original_char_length`
- `truncated_char_length`
- `total_turns`
- `kept_turns`
- `omitted_turns`

The truncated text keeps the first 3 turn blocks and the last 15 turn blocks, with a visible middle marker:

```text
[... N turns omitted for brevity ...]
```

### Quote-validation records

Extraction validates that each `reasoning_passages` item is a literal substring of the transcript text supplied to the extractor. If validation fails, extraction retries once with a correction prompt. Any still-fabricated passages are dropped.

Recorded `_quote_validation` fields:

- `total`
- `verified`
- `fabricated`
- `fabricated_passages`
- `retry_attempted`
- `retry_succeeded`

`run_pipeline.py` later turns surviving fabrication count into `run_health.issues[] = "quote_fabrication"`.

### Loader output

`engine/system_b/conversation_loader.py` converts the transcript into `ConversationContext`:

- `turns`: tuple of `Turn(turn_index, speaker, text)`
- `extraction`: typed `ExtractionPayload`
- `capture_manifest`: passthrough dict from extraction JSON
- `capture_health`: passthrough string
- `capture_warnings`: passthrough tuple

The loader preserves multi-line message bodies by buffering all text between turn markers and stripping leading/trailing whitespace from each message body. It lowercases speaker labels to `user` / `assistant`.

### Pipeline run-health surface

`scripts/run_pipeline.py` surfaces capture-derived issues in `run_health`:

- `capture_critical` when extraction JSON has `capture_health == "critical"`
- `capture_degraded` when extraction JSON has `capture_health == "degraded"`
- `quote_fabrication` when `_quote_validation.fabricated > 0`
- `capture_truncated` when `capture_manifest.truncation_applied` is true
- `warnings`: pipeline warnings plus upstream `capture_warnings`
- `capture_manifest`: passthrough into `run_health.capture_manifest`

## What The Current Capture Path Drops Or Excludes

By design, Step 1 excludes:

- tool call inputs
- tool call outputs
- code execution outputs
- file reads
- web/search results
- system messages
- developer messages
- model/system reminders
- meta-conversation about the skill itself

For very long conversations, Step 1 currently instructs the orchestrator to include only the first 3 turns and last 15 turns. This is an upstream manual capture reduction before `run_extract.py` sees the file. It should be treated as outside the current machine-validated truncation manifest unless the captured text itself includes an explicit omission marker.

Extraction-level truncation may also drop middle turns when the captured file exceeds 80,000 characters. This path is machine-recorded in `capture_manifest` and surfaced by `run_health.capture_truncated`.

Quote validation may drop non-literal `reasoning_passages` from the extraction payload. This does not drop raw transcript text; it drops untrusted extracted quote fields and surfaces `quote_fabrication`.

## What The Capture Path Trusts Implicitly

The path still relies on the orchestrator's Step 1 rendering for several high-value assumptions:

- Speaker attribution is trusted. Code validates counts, not whether the speaker labels are semantically correct.
- Turn-boundary detection is trusted once markers are present. Code parses marker lines; it does not infer missing markers inside a long body.
- Assistant/user alternation is not enforced. The loader accepts any sequence of valid markers.
- Displayed `turn_index` values are trusted. The loader does not reject duplicate numbers, skipped numbers, or repeated same-speaker markers with the same index.
- Declared counts are trusted only as a validation aid. `capture_health` can be `unknown` if the header is missing, and the pipeline can still proceed.
- Source text fidelity is trusted after file write. There is no cryptographic or API-level proof that the text is the complete original conversation.
- Truncation thresholds are trusted. The code records extraction-level truncation over 80,000 chars, but Step 1 manual long-conversation reduction is not automatically detectable.

## Corpus Sampling

I sampled four representative corpus captures and compared raw marker counts against loader output.

| Case | File | Declared header | Raw markers | Loader turns | Match | Notes |
|---|---|---:|---:|---:|---|---|
| Short startup decision | `research/test-cases/case_startup_pivot_conversation.txt` | 7 user / 7 assistant | 14 total | 14 total | yes | `capture_health=good`, no truncation |
| Multi-offer career decision | `research/test-cases/case_multi_offer_conversation.txt` | 15 user / 15 assistant | 30 total | 30 total | yes | `capture_health=good`, no truncation |
| Longest corpus case | `research/test-cases/case_phd_research_conversation.txt` | 22 user / 22 assistant | 44 total | 44 total | yes | `capture_health=good`, no truncation |
| Messy multi-problem case | `research/test-cases/case_messy_three_problems_conversation.txt` | 11 user / 11 assistant | 22 total | 22 total | yes | `capture_health=good`, no truncation |

Sample command used:

```bash
python3 -c 'import re, json; from pathlib import Path; from engine.system_b.conversation_loader import _parse_turns; ...'
```

Observed result across all four samples:

- raw marker sequence matched loader `(turn_index, speaker)` sequence exactly
- loader user/assistant counts matched raw marker counts exactly
- no empty loader turns
- capture validation returned `good`
- truncation did not apply

Live-smoke note from the runtime-default closeout:

- `case_startup_pivot_conversation.txt` also passed both default and `--legacy-contract` pipeline smokes.
- The extraction had `capture_health=good`.
- Run health was `degraded` only because quote validation dropped non-literal `reasoning_passages` (`quote_fabrication`), not because raw capture failed.

## Failure-Mode Classification

| Failure mode | Current detection / handling | Classification | Open fix needed before Phase 0.5? |
|---|---|---|---|
| More than half of assistant turns missing | `capture_health=critical`; extraction declines before OpenRouter spend | `blocker_for_ir_provenance` but already blocked | No |
| Zero assistant responses despite declared assistant count | `capture_health=critical`; extraction declines before OpenRouter spend | `blocker_for_ir_provenance` but already blocked | No |
| Minor declared-vs-actual assistant mismatch | `capture_health=degraded`; warning passed into run health | `acceptable_with_flag` | No |
| User-count mismatch | warning and `capture_health=degraded` | `acceptable_with_flag` | No |
| Missing or unparsable header | `capture_health=unknown`; loader can still parse markers | `acceptable_with_flag` for current lanes; should be tightened before hard provenance metrics | No for Phase 0.5; consider `capture_unknown` run-health issue later |
| Malformed turn marker | affected text may attach to previous turn or be skipped if before first marker | `blocker_for_ir_provenance` if observed silently | No observed blocker; add fixtures when IR builder lands |
| Speaker misattribution by orchestrator | not detectable mechanically | `blocker_for_ir_provenance` if observed | No observed blocker; requires human/provenance review discipline |
| Duplicate displayed turn number for same speaker | loader accepts it | `fix_later` | No; Phase 1 IR should assign sequence ids or use `(turn_index, speaker, ordinal)` |
| Normal duplicate displayed turn number across user and assistant | expected format | `acceptable_with_flag` | No; provenance refs must not use bare `turn_index` alone |
| Non-alternating valid markers | loader accepts sequence | `acceptable_with_flag` | No; some real chats may legitimately have uneven turns |
| Extraction-level truncation over 80,000 chars | explicit omission marker plus `capture_manifest.truncation_*`; run health includes `capture_truncated` | `acceptable_with_flag` | No |
| Step 1 manual long-conversation reduction (>100 turns) | instructed in `SKILL.md`; not automatically converted to structured truncation metadata | `fix_later` | No for sampled/current Phase 1 cases; later long-conversation provenance should add explicit manifest fields |
| Tool calls and tool outputs omitted | explicit Step 1 rule | `acceptable_with_flag` | No, as long as IR provenance claims exclude tool evidence |
| System/developer messages omitted | explicit Step 1 rule | `acceptable_with_flag` | No, as long as IR provenance claims exclude hidden instruction provenance |
| Meta-conversation about the skill omitted | explicit Step 1 rule | `acceptable_with_flag` | No |
| Quote fabrication in `reasoning_passages` | retry once, drop remaining fabricated passages, `_quote_validation`, `quote_fabrication` run-health issue | `acceptable_with_flag` | No; raw turn provenance remains intact |
| Invalid historical `canonical_key` | invalid keys blanked; warning emitted | `fix_later` | No; canonical keys are not part of v1 IR source-of-truth doctrine |
| Capture file exists but extraction JSON lacks capture metadata | loader defaults `capture_health="unknown"` and empty manifest | `acceptable_with_flag` for compatibility artifacts | No for Phase 0.5; Phase 1 fixtures should prefer artifacts with manifest |

## Phase 1 Provenance Implications

The current capture layer can support a first provenance-bearing IR if Phase 1 follows these rules:

- Treat the captured conversation file as the canonical source artifact, not the extraction JSON.
- Define IR `Turn` identity as a unique message sequence id, with display fields for `turn_index` and `speaker`.
- Use exact source spans only within message text that exists in the captured artifact.
- Carry capture status into IR build metadata: `good`, `degraded`, `critical`, `unknown`, and truncation fields.
- Do not assert provenance for excluded surfaces: tools, hidden system/developer instructions, omitted middle turns, or meta-conversation.
- Preserve degraded-mode flags in packet manifests so lanes know when source coverage is partial.

## Conclusion

Phase 0.1 may proceed to PM review. The sampled current corpus captures reconcile cleanly with loader output, and known severe capture breaks are already blocked by `capture_critical` before provider spend. The main design constraint for Phase 1 is not an immediate blocker: provenance identifiers must be more precise than the current displayed `turn_index`, and long-conversation omissions must remain explicit whenever provenance coverage matters.
