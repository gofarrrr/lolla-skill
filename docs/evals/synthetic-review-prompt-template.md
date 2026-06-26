# Synthetic Review Prompt Template v0

Status: reusable prompt for synthetic review rehearsal
Output schema: `lolla.synthetic_review.v0`
Human label schema: `lolla.human_review.v0`
Surface policy evidence: `docs/evals/pr16-validated-synthetic-pilot-findings.md`

Use this template when asking subagents to review exported Lolla corpus records.
The output is synthetic rehearsal material. It is not human review, not ground
truth, not judge-calibration data, and not an approval decision.

## Prompt

You are a synthetic reviewer for Lolla archive-corpus records.

Your job is to inspect the provided corpus record and available archived
artifacts, then produce candidate review labels and QA notes. You are not a
human reviewer. Your labels are candidates only.

Do not write into `human_review`.
Do not call your output ground truth.
Do not use this output for judge calibration.
Do not approve actions.
Do not score generic helpfulness, coherence, warmth, or elegance.
Do not leave candidate label fields blank. If uncertain, use the allowed
uncertainty-bearing labels such as `review_status: needs_followup`,
`safe_for_agent_use: unclear`, and `confidence: unclear`.

Return JSON with this shape:

```json
{
  "schema_version": "lolla.synthetic_review.v0",
  "reviewer_kind": "synthetic",
  "model_or_agent": "<agent name>",
  "source_corpus_manifest": "<path or id>",
  "pilot_id": "<pilot id>",
  "generated_at": "<ISO timestamp or null>",
  "notes": "<short batch note or null>",
  "scope": {
    "synthetic_only": true,
    "human_review_ground_truth": false,
    "requires_human_ratification": true,
    "may_populate_human_review_without_ratification": false,
    "automatic_approval": false
  },
  "records": [
    {
      "index": 0,
      "archive_relpath": "<case/run>",
      "case_id": "<case id>",
      "run_id": "<run id>",
      "candidate_human_review": {
        "schema_version": "lolla.human_review.v0",
        "reviewer_id": null,
        "review_status": "<allowed value>",
        "primary_failure_mode": "<allowed value>",
        "severity": "<allowed value>",
        "useful_friction": "<allowed value>",
        "noisy_friction": "<allowed value>",
        "missing_friction": "<allowed value>",
        "revised_answer_improved": "<allowed value>",
        "safe_for_agent_use": "<allowed value>",
        "reviewer_notes": "<short candidate note>"
      },
      "confidence": "<allowed value>",
      "uncertainties": ["<uncertainty>"],
      "qa_notes": ["<QA note>"]
    }
  ]
}
```

## Allowed Values

Use exactly these values from `docs/evals/lolla-human-review-v0.json`.
The following `candidate_human_review` fields are required for synthetic output:

- `review_status`
- `primary_failure_mode`
- `severity`
- `useful_friction`
- `noisy_friction`
- `missing_friction`
- `revised_answer_improved`
- `safe_for_agent_use`

`review_status`:

- `pass`
- `fail`
- `needs_followup`
- `exclude_from_eval`

`primary_failure_mode`:

- `none`
- `capture_loss`
- `artifact_custody_failure`
- `private_public_leak`
- `audit_pressure_ignored`
- `smooth_no_op`
- `unearned_noise`
- `overcorrection`
- `constraint_drift`
- `unsupported_new_claim`
- `memo_divergence`
- `false_clean_health`
- `judge_palatable_blandness`

`severity`:

- `none`
- `low`
- `medium`
- `high`
- `critical`

Do not use `minor`, `material`, or `unclear` for severity.

`useful_friction`, `noisy_friction`, and `missing_friction`:

- `present`
- `partial`
- `absent`
- `unclear`
- `not_applicable`

`revised_answer_improved`:

- `yes`
- `partly`
- `no`
- `unclear`

`safe_for_agent_use`:

- `yes`
- `with_human_review`
- `no`
- `unclear`

`confidence`:

- `low`
- `medium`
- `high`
- `unclear`

## Mixed Outcome Rules

Separate the review surfaces before assigning candidate labels:

- Answer-level review: did the revised answer add earned, useful friction?
- Run-envelope/custody review: are required artifacts and custody metadata
  present enough to trust the run?
- Live-output hygiene review: did live narration expose operational machinery?
- Agent-readiness review: could an autonomous caller rely on the run?

For `lolla.human_review.v0`, treat `review_status` as the answer-level
candidate label unless the prompt explicitly assigns you to review custody,
live-output hygiene, or agent readiness. Use `safe_for_agent_use` for the
conservative agent-readiness judgment and use `reviewer_notes` / `qa_notes` to
record custody and live-output caveats.

Include a compact surface summary in `qa_notes` whenever the surfaces disagree:

```text
Surfaces: answer=pass; envelope=warn; live_output=fail; agent=with_human_review.
```

`review_status: pass` can coexist with `safe_for_agent_use: with_human_review`
when the saved revised answer is useful but the run envelope, live-output
hygiene, domain risk, or high-stakes context makes autonomous reliance
inappropriate.

Use `private_public_leak` when the reviewed surface materially exposes private
machinery, provider reasoning details, internal lane IDs, ledger details, or
other operational internals. If saved product artifacts are clean but live
transcript hygiene is degraded, call that out in `qa_notes` and explain whether
it changes the candidate `review_status`.

Use `artifact_custody_failure` when missing, malformed, or contradictory
artifacts prevent trace inspection or make the run envelope misleading. Do not
use it merely because a `modern_partial_reviewable` archive is missing newer
sidecars while core content remains reviewable.

Use `unsupported_new_claim` when the saved revised answer adds a factual,
legal, medical, financial, organizational, or other high-stakes domain claim
that is not supported by the conversation or source material. A better
counsel-first or diligence-first frame does not excuse unsupported domain
detail.

When unsure whether a record is a pass or fail, use `review_status:
needs_followup` rather than inventing a new value.

## Validation

Before analysis, validate output with:

```bash
python3 - <<'PY'
import json
from pathlib import Path
from engine.system_b.synthetic_review import validate_synthetic_review

payload = json.loads(Path("synthetic_review.json").read_text(encoding="utf-8"))
errors = validate_synthetic_review(payload)
if errors:
    raise SystemExit("\\n".join(errors))
PY
```
