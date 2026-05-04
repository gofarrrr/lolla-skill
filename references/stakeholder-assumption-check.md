# Stakeholder Assumption Check

## What This Is

This is a narrow optional lens for cases where the advice depends on another actor's knowledge, cooperation, interpretation, power, silence, retaliation, or exit.

It is not a Theory-of-Mind product surface. It is not an empathy lane. It is not a stakeholder psychology profile.

The useful question:

> What did the advice assume about another actor, and what changes if that assumption is wrong?

## Runtime Field

When enabled, `scripts/run_pipeline.py` may persist:

- `stakeholder_assumption_check.status`: `skipped`, `completed`, or `skipped_error`
- `stakeholder_assumption_check.triggered`: boolean
- `stakeholder_assumption_check.surface`: boolean
- `stakeholder_assumption_check.summary`: one-sentence plan-change summary
- `stakeholder_assumption_check.critical_actors`: full actor-level inspection payload for Observatory
- `stakeholder_assumption_check.chat_actors`: actor-level corrections that passed deterministic gates for validation

The field is absent when `LOLLA_STAKEHOLDER_CHECK` is disabled.

`critical_actors` is the full inspection payload. It may include speculative
actors, duplicates, or open-question material for Observatory. `chat_actors`
records which actors passed deterministic surface gates, but it is not currently
a user-facing chat contract. Each actor also carries `surface_in_chat` and, when
false, `surface_block_reason`.

## Current Surface Rule

User-facing surfacing is disabled during validation.

Do not fold `chat_actors` or `critical_actors` into chat or memo output, even
when `surface` is true. The current use is Observatory/debugging only: compare
the checker payload against the existing Pressure Check baseline and look for
cases where the checker catches non-duplicative material the baseline misses.

Good current behavior:

> The user-facing Pressure Check is written from the existing Step 7/8 synthesis. The stakeholder check appears only in Observatory and result JSON for validation.

Bad:

> The Stakeholder Assumption Check found that the ex-husband likely feels defensive...

Why bad: machinery leak, speculative psychology, and a new section.

## Grounding Rule

Use the checker's grounding tier:

- `grounded`: safe to state as established by the transcript
- `plausible`: usable as a risk or condition, not as settled fact
- `speculative`: never appears in `chat_actors`; at most convert into an open question

Role or closeness is not enough for `grounded`. "Lina is close to Marcus" does not prove Lina knows Marcus's exact equity ask.

If the runtime downgrades a grounded-looking claim because the evidence is only
role/closeness, likely-access, or missing known-to-actor proof, treat the
`plausible` downgrade as authoritative. Do not upgrade it in prose.

Spouse/partner future-reaction assumptions based only on role closeness are
inspection material, not chat material. If the plan change depends on how a
spouse or partner will react, support, accept, or tolerate risk, the runtime may
mark `surface_block_reason: role_closeness_open_question`. Leave it in
Observatory; do not turn it into advice unless another surfaced input
independently grounds the same plan change.

## Pressure-Check Use

During validation, do not use this field as another Step 8 input. Instead, audit
it after the run:

1. Did the existing Pressure Check already cover the same actor dependency?
2. If not, did `chat_actors` identify a concrete non-duplicative plan change?
3. Would adding it improve the user-facing output without machinery leak, speculative psychology, or word-budget bloat?

Only future work may re-enable chat/memo surfacing, and only after production
evidence shows the checker adds value beyond the existing Pressure Check.

If `surface` is false but `critical_actors` is non-empty, the check may still be
useful for debugging in Observatory. It is not user-facing material.

If `status` is `skipped_error`, do not invent the missing check. Note the failure only in run health / Observatory, not in user-facing chat unless the degraded-run warning already requires it.
