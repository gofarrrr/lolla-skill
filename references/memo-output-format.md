# Memo Output Format

## What This File Is

This is the contract for the Claude-written decision-note layer that appears at the top of the standalone Lolla memo.

The Python renderer stays deterministic. Claude writes a small set of memo fields after the pressure check is persisted; `scripts/render_memo.py` then renders those fields into a product-clean decision note by default. The full deterministic audit appendix can still be rendered explicitly with `--include-audit-appendix`, but it is not the default user-facing memo.

The memo's job is not to replay the run. It is a portable decision note:

- first screen: what changed in the advice and why it matters
- middle: what still holds, what was taken back or set aside, and any final pressure-check divergence
- end: the highest-priority unanswered questions, with any overflow preserved in a small question appendix

The Observatory remains the instrument panel and audit trace. Chat remains the live product surface. The memo is the artifact someone can reopen later and understand in under a minute.

## Core Rule

The memo's first screen must answer: what changed in the advice?

Do not start with counts, model names, lane names, process sections, severity labels, or a table of contents. The user opened the memo to recover the improved decision, not to watch the audit run again.

## Required Fields

Persist these fields to `result.json` before running `scripts/render_memo.py`:

- `memo_substantive_title`
- `memo_orientation_note`
- `memo_what_changed`
- `memo_what_still_holds`
- `memo_take_back_or_set_aside`
- `memo_pressure_check`
- `memo_note_written_at`

`memo_pressure_check` may be an empty string when no material divergence survived.

## Title Rules

The title is a structural observation, not a recommendation.

Good:

- `# The reporting path should be staged before it becomes irreversible`
- `# The equity decision turned on an untested tail outcome`
- `# The slow-repair plan needs tripwires before it is safe`

Bad:

- `# Reasoning Audit: Mother deciding how to address...`
- `# Do not give Marcus equity`
- `# Report the partner externally`
- `# Key Findings From the Lolla Audit`

Rules:

- Use a verb or implied action.
- Name the pressure in the reasoning.
- Do not prescribe the user's final decision.
- Do not use category labels.
- Do not use product language (`Lolla`, `audit`, `memo`, `Observatory`) in the title unless unavoidable.

## Orientation Note Rules

Length: 180-260 words.

Purpose: the first screen should tell the user what changed in the advice and why the memo exists.

Structure:

1. Start with the user's decision tension in concrete terms.
2. Name what the original advice leaned toward.
3. Name the pressure that changed or sharpened the advice.
4. State the revised direction without overclaiming.
5. Point toward the useful material below without writing a table of contents.

Good pattern:

> You were not asking whether the document destruction was serious. You had already crossed that line. The live question was whether reporting externally first was safer than testing a protected internal channel through counsel.
>
> My original answer leaned external-first because the firm had handled prior issues quietly. The weak point was that I converted your "60-65%" read on the GC into a decision gate, even though that number was not evidence. The revised advice is not "trust the GC." It is: retain whistleblower counsel first, then use counsel to choose the channel with more information than you have today.
>
> The useful part of the memo is the change in sequence, not the count of findings: counsel first, channel second; evidence before commitment; tripwires before the risk becomes irreversible.

Avoid:

- `This memo presents...`
- `Below you will find...`
- `The audit identified...`
- Counts and severities in the opener.
- New claims not present in Step 6, Step 8, or the persisted audit artifacts.

## Decision-Note Sections

### What changed in the advice

Source: Step 6 `What actually shifted`.

Rules:

- Render 1-4 shifts.
- Preserve the operational definition of a shift: a different action, threshold, sequence, condition, risk treatment, or decision question.
- Keep each shift scannable.
- Prefer short subheadings with verbs.
- Do not add tail notes that change advice outside the cap.
- If a shift changes sequencing, state the boundary precisely. Example: *formal proposal after advisor buy-in; low-cost availability probe before the meeting*. Do not leave the reader with two conflicting orders.

### What still holds

Source: Step 6 `What survived`.

Rules:

- Compress.
- Preserve only what the user should remember later.
- Use 1-3 bullets or 1-2 short paragraphs.
- Do not preserve unverified numbers as if they are settled facts. If a base rate, market number, deadline, or probability was flagged as ungrounded, either omit it or label it as an illustrative placeholder whose direction may survive while the precision does not.

### What I'd take back or set aside

Source: Step 6 `What I'd take back or set aside`.

Rules:

- Include self-corrections and audit-grounded set-asides.
- Do not perform fake resistance.
- If the section is thin, keep it thin.
- The purpose is judgment, not artificial balance.

### One more pressure check

Source: Step 8 pressure check.

Rules:

- Include only if a material divergence exists.
- Do not group by lane.
- Do not mention sub-agents, isolated review, independent review, or reviewer/source alignment.
- Scan all pressure-check divergences before writing. A materially different decision path, fallback, channel, commitment shape, or instrument is not optional just because another concern is easier to summarize. Include it or explicitly set it aside.
- If no divergence survives, leave `memo_pressure_check` empty.
- Optional stakeholder-assumption material is currently Observatory-only validation data. Do not include `stakeholder_assumption_check.chat_actors` or `critical_actors` in the memo, even when `surface` is true. Memo surfacing remains disabled until production evidence shows the checker adds non-duplicative value beyond the existing Pressure Check.

## Questions Still Unanswered

Python renders this section deterministically from structural gap questions.

Rules for Claude:

- Do not answer these questions in the memo note fields.
- Do not invent new gap questions.
- If you reference one in the orientation, quote or paraphrase it as a question the user still has to settle.

Renderer behavior:

- The decision-note layer shows only the first three unique structural gap questions.
- Any remaining questions are preserved under `Appendix: Additional unresolved questions` so the memo stays scannable instead of becoming a backlog dump.
- The full audit trace is Observatory-first. It appears in a markdown memo only when `scripts/render_memo.py --include-audit-appendix` is used.

## Banned Language

Never use these in the memo decision-note layer:

- Internal machinery: `Beat`, `Step`, `Lane`, `sub-agent`, `card`, `pipeline`, `DeltaCard`, `CompanionCheatSheet`, `FramePressureCard`, `StructuralCoverageCard`, JSON field names.
- Report throat-clearing: `This memo presents`, `This report summarizes`, `The following sections`.
- Sales or AI register: `compelling`, `powerful`, `unlock`, `deep dive`, `transform`, `valuable insights`, `complex and nuanced`, `it is important to consider`.
- Verdict overreach: `therefore you should`, unless the same advice already exists in Step 6 or Step 8 and is phrased as advice, not command.
- Private enrichment vocabulary: `V60`, `affordance`, `chunk`, `packet`, `ledger`, internal IDs, `selected_cards`, `selected_chunk_ids`.
- Model-name parade: do not list mental-model labels in the memo decision-note layer. Use a familiar model name only when it is the clearest human-language handle for the mechanism; otherwise translate the mechanism into ordinary language.

Archive finalization runs the same product-surface principle as a deterministic hygiene gate. The memo markdown and memo-note fields are scanned for internal machinery terms; leaks are recorded under `product_output_hygiene` and degrade `run_health.product_output_health` to `unsafe`. Operator appendices and Observatory may contain machinery, but the default memo decision-note layer should not.

Allowed product language, used sparingly:

- `audit`
- `memo`
- `Observatory`
- `pressure check`
- `updated position`
- `full breakdown`

## Good Shape

```md
# The reporting path should be staged before it becomes irreversible

[180-260 word orientation note]

## What changed in the advice

### Retain counsel first; choose the channel second

[2-4 sentences]

## What still holds

[Compressed survival section]

## What I'd take back or set aside

[Compressed correction/set-aside section]

## One more pressure check

[Only if material]

## Questions still unanswered

- [Gap question]
```

## Bad Shape

```md
# Reasoning Audit: Mid-level consultant report

This memo presents the key findings from the Lolla audit. The audit identified 3 high-severity findings, 4 mental model connections, 2 frame alternatives, and 6 structural gaps.

## Key Findings
...
```

Why it fails: category title, counts before meaning, process language, and no first-screen answer to what changed in the advice.
