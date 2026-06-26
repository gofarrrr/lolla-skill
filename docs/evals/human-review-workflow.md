# Human Review Workflow v0

Status: v0 workflow for PR13 review-corpus records
Inputs: `scripts/export_review_corpus.py` JSONL records and archived Lolla run folders
Label schema: `lolla.human_review.v0`
Taxonomy: `docs/evals/lolla-failure-taxonomy.md`

This workflow turns archived Lolla runs into human-reviewed evidence. It is not
an LLM judge, not an approval workflow, and not a replacement for deterministic
checks. Its job is to create product-taste ground truth before any subjective
judge is attempted.

## 1. Export The Review Corpus

Run the local export:

```bash
python3 scripts/export_review_corpus.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_review_corpus.jsonl \
  --manifest-out /tmp/lolla_review_corpus_manifest.json
```

Treat the output as local-only. The records exclude raw transcript, memo,
revised-answer text, raw model message content, provider reasoning details, and
control argument values, but they still include local archive paths, case IDs,
run IDs, and operational metadata.

## 2. Check Review Readiness

Each corpus record includes deterministic readiness fields:

- `review_readiness_tier`
- `content_review`
- `custody_review`
- `batch_recommendation`

Use them to avoid treating legacy archive gaps as answer-quality failures.

| Tier | Meaning | Suggested use |
|---|---|---|
| `full_modern_reviewable` | Core content, modern custody artifacts, and capture adequacy are available. | Best target for first human review and synthetic rehearsal. |
| `modern_partial_reviewable` | Core content is available and at least some modern custody exists, but one or more modern sidecars are missing. | Good for review, but note the missing custody material. |
| `legacy_content_reviewable` | Conversation, extraction, result, revised answer, and memo exist, but modern sidecars are missing. | Useful for answer-level rehearsal, not full custody workflow. |
| `not_reviewable` | Core content needed for inspection is missing. | Exclude or backfill before review. |

`content_review.available` means the reviewer has enough core material to read
the conversation/result/memo path. `custody_review.available` means the modern
run envelope is present enough to inspect agent result, reasoning trace, run
events, evaluation, and capture adequacy.

## 3. Select Runs

For an initial pass, review 50 to 100 runs or fixtures when available.

Stratify the sample across:

- clean, warned, partial, degraded, and incomplete run health,
- short and long conversations,
- full and omitted capture,
- high and low advice-change cases,
- `full_modern_reviewable`, `modern_partial_reviewable`, and selected
  `legacy_content_reviewable` records,
- runs with and without `evaluation.json`,
- runs with and without control-plane sidecars,
- repeated runs of the same or similar conversation when available.

Do not review only the cleanest runs. The goal is to learn where Lolla fails.

## 4. Inspect The Trace

Use the corpus row to triage, then inspect the actual archived run.

Minimum inspection surface:

- `agent_result.json`
- `evaluation.json` when present
- `capture_adequacy`
- `reasoning_trace.json`
- `memo.md`
- `revised.txt`
- relevant run health and provider-boundary summaries
- Observatory custody panel when useful

When needed, read the captured conversation to check whether the revised answer
preserved the user's constraints. Do not judge from the memo alone.

## 5. Label The First Upstream Failure

Record one `primary_failure_mode`.

Use the first upstream failure, not every downstream symptom. For example:

- If the middle-turn constraint was omitted and the revised answer later drifted,
  use `capture_loss`, not `constraint_drift`.
- If artifacts are missing and the memo cannot be trusted, use
  `artifact_custody_failure` before judging answer quality.
- If the run envelope is healthy but the revision adds generic caution, use
  `unearned_noise` or `overcorrection`.

Use `none` only for reviewed runs where no material failure was found.

## 6. Label Friction

Fill the three friction fields separately:

- `useful_friction`: did Lolla add earned, actionable, proportionate pressure?
- `noisy_friction`: did Lolla add ungrounded or unhelpful caution?
- `missing_friction`: did Lolla miss pressure that should have changed the answer?

These can all matter at once. A run can add one useful gate while still missing
another constraint.

## 7. Label Agent Use

`safe_for_agent_use` is a human review label, not a policy action.

Use:

- `yes` only when the run envelope and revised answer are both fit for reliance.
- `with_human_review` when a human can use the run but an autonomous caller
  should not proceed without inspection.
- `no` when the run is misleading, degraded in an action-changing way, or unsafe.
- `unclear` when the reviewer cannot decide from the available artifacts.

This label does not override `agent_result.caller_action`.

`review_status: pass` can coexist with
`safe_for_agent_use: with_human_review` when the answer-level review passes but
the run envelope is not fit for autonomous reliance.

## 8. Separate Mixed Outcomes

Reviewers should separate four surfaces:

- answer-level review,
- run-envelope/custody review,
- live-output hygiene review,
- agent-readiness review.

A useful revised answer can pass answer-level review while the run still carries
custody, evaluation, live-output, or domain-risk caveats. Do not automatically
turn those caveats into answer-quality failures.

Use `private_public_leak` when the reviewed surface materially exposes private
machinery, provider reasoning details, internal lane IDs, ledger details, or
other operational internals. If `revised.txt` and `memo.md` are clean but the
live transcript leaks machinery, record that as a live-output hygiene caveat in
notes and decide whether it materially changes the candidate `review_status`.

## 9. Write Notes

Keep `reviewer_notes` short but traceable.

Good notes name the hinge:

- "Captured transcript omits the user's relocation constraint; revision recommends option B without checking it."
- "Useful friction present: added a stop rule before sending external email."
- "Noisy friction: raised generic legal risk without any conversation support."

Avoid polished essays. The goal is fast, repeatable error analysis.

## 10. Synthetic Review Rehearsal

Subagents or synthetic reviewers may help triage records. Their output must be
kept outside `human_review` unless a human reviewer inspects the trace and takes
responsibility for the final label.

Allowed synthetic outputs:

- `synthetic_review`
- `candidate_labels`
- `qa_notes`
- disagreement reports across multiple subagents

Synthetic outputs may suggest a `candidate_human_review`, but they do not own
`lolla.human_review.v0`. Store them as rehearsal notes, compare disagreements,
and use them to refine the taxonomy or workflow.

Do not call synthetic labels "human review." Do not use them as gold labels for
judge calibration. A tiny reference shape is documented in
`docs/evals/lolla-synthetic-review-v0.json`.
The reusable prompt template lives in
`docs/evals/synthetic-review-prompt-template.md`.

## 11. Use The Labels

After the first labeled sample:

- revise the taxonomy where real failures do not fit,
- identify high-frequency and high-severity failures,
- convert deterministic failures into code checks,
- design fixture cases for recurrent subjective failures,
- only then consider narrow calibrated LLM judges.

Do not use a generic helpfulness, coherence, or preference judge as a release
gate. Lolla is allowed to make an answer less smooth when that friction protects
the decision.
