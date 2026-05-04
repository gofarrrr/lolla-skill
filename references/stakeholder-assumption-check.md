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
- `stakeholder_assumption_check.critical_actors`: actor-level assumptions

The field is absent when `LOLLA_STAKEHOLDER_CHECK` is disabled.

## Surface Rule

Chat receives no new heading and no new section.

If `surface` is true, fold the material into the existing `### Pressure Check` section as one concrete correction. Name the plan change, not the machinery.

Good:

> One stakeholder assumption changes the plan. I treated the ex conversation as evidence-backed persuasion, but evidence can also become ammunition if forwarded. Share the legal threshold and grooming-pattern summary; do not send screenshots or exact phrases.

Bad:

> The Stakeholder Assumption Check found that the ex-husband likely feels defensive...

Why bad: machinery leak, speculative psychology, and a new section.

## Grounding Rule

Use the checker's grounding tier:

- `grounded`: safe to state as established by the transcript
- `plausible`: usable as a risk or condition, not as settled fact
- `speculative`: never surface as advice; at most convert into an open question

Role or closeness is not enough for `grounded`. "Lina is close to Marcus" does not prove Lina knows Marcus's exact equity ask.

## Pressure-Check Use

At Step 8, ask:

1. Did the check identify an assumption Step 6 relied on?
2. Is the assumption grounded or plausible?
3. Does the risk-if-wrong require a different action, sequence, threshold, decision question, risk treatment, or communication boundary?

Only surface when all three are yes.

If `status` is `skipped_error`, do not invent the missing check. Note the failure only in run health / Observatory, not in user-facing chat unless the degraded-run warning already requires it.
