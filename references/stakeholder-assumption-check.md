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
- `stakeholder_assumption_check.chat_actors`: actor-level corrections allowed into user-facing chat

The field is absent when `LOLLA_STAKEHOLDER_CHECK` is disabled.

`critical_actors` is not a chat contract. It may include speculative actors,
duplicates, or open-question material for inspection. Step 8 and any downstream
agent must consume `chat_actors` only. Each actor also carries
`surface_in_chat` and, when false, `surface_block_reason`.

## Surface Rule

Chat receives no new heading and no new section.

If `surface` is true, fold only `chat_actors` material into the existing
`### Pressure Check` section as one concrete correction. Name the plan change,
not the machinery.

Good:

> One stakeholder assumption changes the plan. I treated the ex conversation as evidence-backed persuasion, but evidence can also become ammunition if forwarded. Share the legal threshold and grooming-pattern summary; do not send screenshots or exact phrases.

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

At Step 8, ask:

1. Is there at least one `chat_actors` entry?
2. Did the entry identify an assumption Step 6 relied on?
3. Does the risk-if-wrong require a different action, sequence, threshold, decision question, risk treatment, or communication boundary?

Only surface when all three are yes.

If `surface` is false but `critical_actors` is non-empty, the check may still be
useful for debugging in Observatory. It is not user-facing material.

If `status` is `skipped_error`, do not invent the missing check. Note the failure only in run health / Observatory, not in user-facing chat unless the degraded-run warning already requires it.
