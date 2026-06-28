# Live Output Hygiene Decision v0

Status: decision/design-only
Date: 2026-06-28
Review slice: `live_output_hygiene_decision_v0`

PR35 decides how Lolla should treat `live_output_health` in evaluation and
human review.

This is not an implementation PR. It does not run `$lolla`, call models, change
runtime behavior, change prompts, change `SKILL.md`, mutate archives, implement
trusted transcript capture, change `finalize_live_output_hygiene.py`, change
`archive_run.py`, change `evaluation.py`, change `agent_result.py`, relax
`caller_action`, add a judge, add answer-quality scoring, or populate labels
automatically.

The decision question is:

```text
Should live_output_health: not_checked remain an honest warning, or should
Lolla define a bounded path to live_output_health: clean for controlled runs?
```

## Decision

`live_output_health: not_checked` should remain the honest default for normal
runs.

It does not automatically mean the saved revised answer failed. It means Lolla
has not independently proven that every user-visible live terminal narration
line was captured and scanned as the user saw it.

A future bounded path to `live_output_health: clean` may exist only when a
complete trusted transcript is supplied, synchronized into the archived
`live_transcript.txt`, and scanned clean by the live-output hygiene finalizer.
A manually maintained transcript is not sufficient to claim `clean`.

Live-output hygiene is a product-surface and custody concern, not answer-quality
scoring. It should affect run-envelope caveats and human
`safe_for_agent_use` labels. It should not relax `caller_action`.

## Evidence From PR30-PR34

PR30 and PR33 repeatedly found useful saved answers with the same conservative
caveat:

- saved revised answers and memos were reviewable;
- deterministic run readiness could be `warn`;
- `live_output_health` remained `not_checked`;
- answer-level review could still pass;
- human reliance stayed `safe_for_agent_use: with_human_review`.

PR31 and PR32 focus on whether the revised answer changed action, evidence,
sequence, thresholds, scope, stop rules, written terms, or user questions. PR34
adds a design-only values/priorities review surface. None of those slices prove
live terminal narration was clean.

PR35 preserves that distinction instead of turning a missing live-surface proof
into either a false green check or an answer-quality failure.

## Surfaces

PR35 separates seven product and custody surfaces:

| surface | role | hygiene question |
|---|---|---|
| Saved revised answer | The persisted answer used for answer-level review. | Is the saved advice free of machinery/private/provider leakage? |
| Rendered memo | The portable decision note. | Is the memo product-clean and consistent with the revised answer? |
| Live terminal narration | The text the user saw during the run. | Did visible narration leak machinery, private reasoning, provider details, local paths, or operator internals? |
| `live_transcript.txt` artifact | The archived representation of live narration. | Is it complete and trusted, or only manually maintained/unverified? |
| `operator.log` | Operator diagnostics and helper output. | Did diagnostics stay out of user-visible prose? |
| Observatory surfaces | Local inspection UI and archived sidecars. | Did UI surfaces expose the right custody state without claiming unverified cleanliness? |
| Final receipt | The user-facing completion receipt. | Did the receipt accurately report health, archive, Observatory, and caveats? |

Saved revised answer and memo hygiene can be clean while live terminal hygiene
is `not_checked` or unsafe. Operator logs can contain diagnostics that would be
inappropriate in live narration; that is the point of separating operator and
product surfaces.

## Status Vocabulary

`live_output_health` should describe the live narration surface:

| status | meaning | policy |
|---|---|---|
| `clean` | A complete trusted transcript was supplied, synchronized, and scanned clean. | May remove the live-output caveat if other checks pass. |
| `not_checked` | A manual or unverified transcript may exist, but Lolla cannot prove it captures the full console surface. | Default for normal runs; warn/inspect-first, not answer failure. |
| `missing` | No live transcript artifact is available. | Do not infer cleanliness; treat as stronger custody caveat than `not_checked`. |
| `unsafe` | The available live transcript contains product-surface leakage. | Treat as live-output hygiene failure; do not use as a clean product example. |

Other words such as `warn`, `degraded`, and `fail` belong to run health,
evaluation readiness, or human review outcomes. They can be caused by
live-output status, but they are not themselves the preferred
`live_output_health` values.

## Policy Answers

Should `not_checked` remain the default for normal runs?

Yes. Normal runs should not claim live terminal cleanliness unless a complete
trusted transcript is supplied and scanned clean.

What evidence is required to call live output clean?

A complete trusted transcript of the user-visible session, synchronized into
the archived `live_transcript.txt`, plus a successful live-output hygiene scan.
The trusted transcript must include the same user-visible prose the user saw,
including the final receipt.

Is a manual transcript ever sufficient?

No. A manually maintained transcript can be scanned and can reveal leaks, but a
no-leak manual transcript should remain `not_checked`. It is useful evidence,
not proof of complete live surface capture.

What is the role of `--trusted-transcript`?

It is the existing bounded mechanism for controlled runs where the operator can
provide complete live-session capture. PR35 does not change its behavior; it
defines when its result may justify `live_output_health: clean`.

Should `live_output_health` affect `caller_action`?

Not in PR35. Do not relax `caller_action` because live output is clean. Do not
use this policy to change caller-action rules. Existing caller policy remains
owned by deterministic run readiness and product artifact availability.

Should `live_output_health` affect `safe_for_agent_use`?

Yes, through human review. `not_checked` should usually keep
`safe_for_agent_use: with_human_review` for review seeds. `unsafe` should push
toward `with_human_review` or `no`, depending on severity and whether the
review target includes live product surface.

Is live-output failure answer failure, run-envelope failure, or agent-readiness
failure?

Usually run-envelope and agent-readiness failure. It becomes answer-level
failure only when the reviewed answer surface itself includes the leak or the
evaluation question explicitly targets live narration.

What should human reviewers do when saved artifacts are clean but
`live_output_health` is `not_checked`?

They may pass answer-level review if the saved revised answer and memo are
good, but they should record the caveat and keep reliance conservative.

What should happen if live narration leaks machinery language but saved
artifacts are clean?

Answer-level review may still pass for saved artifacts. Live-output hygiene
should fail or warn, `safe_for_agent_use` should remain conservative, and the
run should not be used as a clean product-surface example until live narration
is fixed in a later runtime/prompt/conductor PR.

What if saved artifacts are degraded but live output is clean?

Live cleanliness does not rescue artifact or custody failure. The run remains
degraded or not eval-ready for the relevant envelope question.

## Decision Table

| case | condition | answer-level review | run envelope | `safe_for_agent_use` | caller action policy |
|---|---|---|---|---|---|
| A | Saved artifacts clean; `live_output_health: not_checked`. | Can pass. | Warn / inspect first. | Usually `with_human_review`. | No relaxation. |
| B | Saved artifacts clean; trusted live transcript clean. | Can pass. | Can be clean if all other checks pass. | Still a human label; not automatic approval. | Existing policy only. |
| C | Saved artifacts clean; live transcript leaks machinery. | May pass if saved answer/memo are clean. | Live-output warn/fail; product-surface caveat. | `with_human_review` or `no`, depending severity. | No relaxation; do not use as clean example. |
| D | Saved artifacts degraded; live output clean. | Depends on saved artifacts. | Remains degraded if saved envelope fails. | Conservative; often `no` or `with_human_review`. | Live cleanliness does not rescue failure. |
| E | No live transcript artifact. | Can pass if saved artifacts are reviewable. | `live_output_health: missing` or equivalent custody caveat. | Conservative. | Do not infer clean. |

## Human Review Guidance

Human review should keep four surfaces separate:

- answer-level quality of saved `revised.txt` and `memo.md`;
- deterministic run-envelope/custody readiness;
- live-output product-surface hygiene;
- agent-readiness / reliance.

Reviewer notes should name mixed outcomes plainly:

```text
Surfaces: answer=pass; envelope=warn; live_output=not_checked; agent=with_human_review.
```

Use `private_public_leak` when the reviewed surface materially exposes private
machinery, provider reasoning details, internal IDs, ledger details, local run
internals, or operator diagnostics. If only the live transcript leaks, do not
automatically fail the saved answer. If the review target is "clean product
surface," the leak is material.

Use `artifact_custody_failure` when missing or misleading live-output artifacts
prevent the run from answering the evaluation question. Do not use it merely
because a normal run honestly says `not_checked`.

## Future Implementation Gates

PR35 does not implement these gates. A later implementation PR would need:

- a trusted transcript source that is complete for the user-visible session;
- finalizer logic that compares or synchronizes the trusted transcript with
  archived `live_transcript.txt`;
- a rule that the final receipt is included in the checked transcript;
- a prohibition on rewriting user-visible transcript text to hide leaks;
- the same banned-language/product-output hygiene rules used for saved
  artifacts, adapted to live narration;
- persisted status in `evaluation.json` and `agent_result.json`;
- Observatory display only after the policy and statuses are stable;
- tests or fixtures showing `clean`, `not_checked`, `missing`, and `unsafe`
  outcomes;
- documentation for operators explaining when `--trusted-transcript` is valid;
- no caller-action relaxation unless a separate PR changes caller policy.

Implementation should be done only after a concrete user need appears, such as:

- merge-readiness proof for a public demo;
- product-surface regression testing;
- high-stakes/deep-mode reliance policy;
- repeated live-output leaks in reviewed runs.

## What This Does And Does Not Justify

This does justify:

- keeping `live_output_health: not_checked` as the normal honest default;
- treating `not_checked` as a run-envelope caveat, not answer failure;
- keeping human `safe_for_agent_use` conservative when live output is unproven;
- allowing a future trusted-transcript path to `clean`;
- using mixed-surface reviewer notes in PR30/PR33-style reviews.

This does not justify:

- runtime transcript-capture changes;
- `SKILL.md` changes;
- prompt changes;
- changes to `finalize_live_output_hygiene.py`;
- changes to `archive_run.py`;
- changes to `evaluation.py`;
- changes to `agent_result.py`;
- caller-action relaxation;
- treating manual transcripts as clean;
- hiding or rewriting live transcript leaks;
- answer-quality scoring;
- automatic human labels;
- an LLM judge;
- provider-boundary policy changes.

## Recommended Next Slice

PR36 defines risk-mode behavior policy, and PR37 now turns that policy into
fixtures. PR38 reviews the matrix and adds the missing high-stakes
values/priorities conflict fixture:

```text
docs/evals/risk-mode-fixture-matrix-v0.md
docs/evals/risk-mode-fixture-review-v0.md
```

The next slice should be:

```text
PR39 Risk Mode Implementation Plan v0
```

Why PR39: PR35 resolved the live product-surface caveat, PR36 defines how risk
mode should affect review and reliance without changing runtime behavior, PR37
gives concrete fixture cases, and PR38 checks those fixtures as a future gate.
The next move should still be pre-code planning, not runtime enforcement or
judge work.

## Review Receipt

- PR35 is docs/eval/design-only.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No trusted transcript capture implemented.
- No finalizer, archive, evaluation, or agent-result code changed.
- No caller-action relaxation.
- No judge or answer-quality score added.
- No automatic labels added.
