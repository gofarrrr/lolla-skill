# PR16 Validated Synthetic Pilot Findings

Status: evidence note for review workflow
Date: 2026-06-26
Scope: 15 `recommended_modern_review_batch` records

This note summarizes the second synthetic-review pilot after PR16 added
`validate_synthetic_review()` and the corrected prompt template.

The pilot used subagents as synthetic reviewers. Their outputs were rehearsal
notes and candidate labels only. They were not `lolla.human_review.v0`, not gold
labels, not judge-calibration data, and not automatic approval decisions.

## What Passed

PR16 fixed the mechanical problem from the first pilot:

- invalid severity labels such as `minor`, `material`, and `unclear` did not
  recur,
- blank `candidate_human_review` labels were rejected,
- all three synthetic reviewers produced schema-valid outputs.

The substantive signal stayed stable: reviewers broadly found useful friction
across the batch. Common improvements included diligence gates, family or
stakeholder boundaries, counsel-first sequencing, stop-losses, and threshold
conditions. No reviewer treated the batch as ready for autonomous agent use.

## What Still Disagreed

The remaining disagreement was not schema drift. It was review-surface
ambiguity. Reviewers were implicitly answering different questions:

- Did the saved revised answer improve?
- Was the run envelope trustworthy?
- Was live output clean?
- Is this safe for an agent to use?

Four disagreement types recurred:

- **Live-output leakage versus saved-answer usefulness:** records with useful
  `revised.txt` and `memo.md` could still have live transcript machinery leaks.
- **Degraded or eval-fail envelope versus useful answer:** deterministic
  evaluation failure or degraded health can block agent readiness without
  proving the answer-level review failed.
- **Older or partial archives:** `modern_partial_reviewable` records can be
  content-reviewable while missing modern custody sidecars.
- **High-stakes unsupported detail:** legal or regulatory framing can improve
  while still introducing unsupported domain-specific claims.

## Policy Implication

PR17 should clarify review surfaces before adding judges, batch runners, or
capture changes.

For v0 review, `review_status` should usually represent answer-level review
unless the reviewer is explicitly assigned a custody, live-output, or
agent-readiness review. `safe_for_agent_use` should carry the conservative
agent-readiness judgment, and `reviewer_notes` / `qa_notes` should record
surface disagreements.

This keeps a useful revised answer from being mislabeled as bad advice solely
because the run envelope or live-output surface needs human inspection. It also
keeps serious live-output leaks, custody failures, and unsupported high-stakes
claims visible instead of smoothing them into a generic pass.
