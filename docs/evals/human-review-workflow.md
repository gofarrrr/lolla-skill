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

## 2. Select Runs

For an initial pass, review 50 to 100 runs or fixtures when available.

Stratify the sample across:

- clean, warned, partial, degraded, and incomplete run health,
- short and long conversations,
- full and omitted capture,
- high and low advice-change cases,
- runs with and without `evaluation.json`,
- runs with and without control-plane sidecars,
- repeated runs of the same or similar conversation when available.

Do not review only the cleanest runs. The goal is to learn where Lolla fails.

## 3. Inspect The Trace

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

## 4. Label The First Upstream Failure

Record one `primary_failure_mode`.

Use the first upstream failure, not every downstream symptom. For example:

- If the middle-turn constraint was omitted and the revised answer later drifted,
  use `capture_loss`, not `constraint_drift`.
- If artifacts are missing and the memo cannot be trusted, use
  `artifact_custody_failure` before judging answer quality.
- If the run envelope is healthy but the revision adds generic caution, use
  `unearned_noise` or `overcorrection`.

Use `none` only for reviewed runs where no material failure was found.

## 5. Label Friction

Fill the three friction fields separately:

- `useful_friction`: did Lolla add earned, actionable, proportionate pressure?
- `noisy_friction`: did Lolla add ungrounded or unhelpful caution?
- `missing_friction`: did Lolla miss pressure that should have changed the answer?

These can all matter at once. A run can add one useful gate while still missing
another constraint.

## 6. Label Agent Use

`safe_for_agent_use` is a human review label, not a policy action.

Use:

- `yes` only when the run envelope and revised answer are both fit for reliance.
- `with_human_review` when a human can use the run but an autonomous caller
  should not proceed without inspection.
- `no` when the run is misleading, degraded in an action-changing way, or unsafe.
- `unclear` when the reviewer cannot decide from the available artifacts.

This label does not override `agent_result.caller_action`.

## 7. Write Notes

Keep `reviewer_notes` short but traceable.

Good notes name the hinge:

- "Captured transcript omits the user's relocation constraint; revision recommends option B without checking it."
- "Useful friction present: added a stop rule before sending external email."
- "Noisy friction: raised generic legal risk without any conversation support."

Avoid polished essays. The goal is fast, repeatable error analysis.

## 8. Use The Labels

After the first labeled sample:

- revise the taxonomy where real failures do not fit,
- identify high-frequency and high-severity failures,
- convert deterministic failures into code checks,
- design fixture cases for recurrent subjective failures,
- only then consider narrow calibrated LLM judges.

Do not use a generic helpfulness, coherence, or preference judge as a release
gate. Lolla is allowed to make an answer less smooth when that friction protects
the decision.
