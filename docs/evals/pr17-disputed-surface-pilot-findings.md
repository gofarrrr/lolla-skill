# PR17 Disputed Surface Pilot Findings

Status: synthetic rehearsal evidence for PR18 agent-readiness label policy
Date: 2026-06-26
Input workflow: `docs/evals/human-review-workflow.md`
Input prompt: `docs/evals/synthetic-review-prompt-template.md`

This note summarizes the small Pilot 3 rehearsal that reran the five disputed
records from the validated synthetic-review pilot after PR17 clarified review
surfaces.

The pilot remained synthetic-only. It did not populate `human_review`, did not
create gold labels, did not call a model judge, and did not change runtime
behavior.

## Result

PR17's surface policy worked. The earlier broad disagreement around records 13
and 15 collapsed into a cleaner split:

```text
answer=pass; envelope=warn/degraded; live_output=fail; agent=with_human_review.
```

Reviewers could now say that the saved revised answer looked useful while the
live-output surface failed and autonomous use remained inappropriate.

## Remaining Ambiguity

The main remaining split was not about answer quality. It was about
`safe_for_agent_use`.

Record 7 had:

- answer-level review passed,
- run envelope was warn/degraded or custody-limited,
- live output was not checked,
- domain was high-stakes legal/regulatory.

One reviewer chose `safe_for_agent_use: no`; two chose
`safe_for_agent_use: with_human_review`.

That split is a label-policy issue, not a schema issue and not evidence that an
LLM judge is needed.

## PR18 Policy Direction

Clarify that:

- `with_human_review` means a human can still use the run after inspecting
  caveats, but an autonomous caller should not proceed directly.
- `no` means the run should not be treated as agent-usable evidence for the
  target action until rerun, backfilled, or materially repaired.

High-stakes domain risk should raise the bar for `yes` and often pushes
warn/degraded custody from `with_human_review` toward `no`, especially when
capture is incomplete or the answer includes unsupported domain claims.
