# Human Review Workflow v0

Status: v0 workflow for PR13 review-corpus records
Inputs: `scripts/export_review_corpus.py` JSONL records and archived Lolla run folders
Label schema: `lolla.human_review.v0`
Taxonomy: `docs/evals/lolla-failure-taxonomy.md`
Pilot evidence:
`docs/evals/pr16-validated-synthetic-pilot-findings.md`,
`docs/evals/pr17-disputed-surface-pilot-findings.md`

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
- `risk_mode_reliance`

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

`risk_mode_reliance` is a compact review-surface copy of PR41's deterministic
`risk_mode_reliance_policy` check when present. For standard, quick, deep, or
stability records without that check, it records `present: false`. For
high-stakes records, it exposes only custody-safe metadata: `risk_mode`,
`check_id`, check `status`, `caller_action`, `caller_readiness`, and whether
human/domain review remains required. It does not include raw transcript, memo,
revised-answer, provider, private-reasoning, or local path content.

Treat `risk_mode_reliance.present: true` as a reliance caveat, not an
answer-quality failure by itself. It means the deterministic run envelope says
high-stakes reliance remains conservative. It does not automatically set
`safe_for_agent_use`, does not approve domain use, and does not detect
unsupported domain claims.

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

PR49 now plans a future human-owned values/priorities worksheet:

```text
docs/evals/user-values-priorities-worksheet-plan-v0.md
```

Until that worksheet is implemented, treat it as note-taking guidance only. It
can help reviewers notice explicit values, inferred priorities, stakeholder
obligations, non-negotiables, tradeoffs, and unresolved conflicts, but it does
not populate `lolla.human_review.v0`, change `safe_for_agent_use`, or approve
agent reliance.

PR50 adds paraphrase-only examples for that worksheet:

```text
docs/evals/user-values-priorities-worksheet-fixtures-v0.md
docs/evals/user-values-priorities-worksheet-fixtures-v0.json
```

Use those fixtures to rehearse reviewer interpretation before any exporter,
validator, extraction, or automatic labels exist.

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

- `yes` only when the answer-level review passes and the run envelope is strong
  enough for reliance without additional human inspection.
- `with_human_review` when a human can use the run but an autonomous caller
  should not proceed without inspection.
- `no` when the run should not be treated as agent-usable evidence for the
  target action until rerun, backfilled, or materially repaired.
- `unclear` when the reviewer cannot decide from the available artifacts.

This label does not override `agent_result.caller_action`.

It also does not get set automatically by `risk_mode_reliance`. For high-stakes
runs, clean artifacts can still require `safe_for_agent_use: with_human_review`
or `safe_for_agent_use: no`, depending on domain risk, custody, unsupported
claims, unresolved values conflicts, and reviewer judgment. Treat
`safe_for_agent_use: yes` as rare in high-stakes contexts and always
human-owned.

`review_status: pass` can coexist with
`safe_for_agent_use: with_human_review` when the answer-level review passes but
the run envelope is not fit for autonomous reliance.

The key distinction is:

- `with_human_review` means the run can still support a human decision workflow
  after the reviewer inspects caveats.
- `no` means the run should not be used by an agent as evidence for the target
  action, even as a warning-bearing handoff, unless the run is rerun, backfilled,
  or materially repaired.

Apply these default rules:

| Case | Default `safe_for_agent_use` | Reason |
|---|---|---|
| Answer fails. | `no` | An autonomous caller should not rely on a failed answer-level review. |
| Answer passes, envelope fails. | Usually `no` | The content may be useful to a human, but the run cannot support agent reliance. |
| Answer passes, envelope warns but remains inspectable. | Often `with_human_review` | A human can inspect caveats; an autonomous caller should not proceed directly. |
| Answer passes, saved artifacts are clean, live output fails. | Usually `with_human_review` | The saved answer may be useful, but the live surface failed and needs inspection. |
| Reviewed target is the live product output and live output fails. | Usually `no` | The failed surface is the surface being reviewed. |
| High-stakes legal, regulatory, medical, financial, employment, safety, or credential-sensitive advice with degraded custody, incomplete capture, or unsupported domain claims. | Prefer `no` | Domain/action risk raises the reliance bar. |
| Reviewer cannot tell whether the run supports agent reliance. | `unclear` | Do not convert uncertainty into either approval or rejection. |

Use `with_human_review` for inspectable caveats. Use `no` when the caveat blocks
agent reliance for the target action. For example, a legal/regulatory run with a
useful counsel-first answer can still be `safe_for_agent_use: no` if custody is
degraded or the answer includes unsupported domain detail.

## 8. Separate Mixed Outcomes

Reviewers should separate four surfaces before choosing labels:

| Surface | Question | Where to record it in v0 |
|---|---|---|
| Answer-level review | Did the saved revised answer and memo add earned, decision-relevant friction without losing load-bearing constraints? | `review_status`, `primary_failure_mode`, friction fields, `revised_answer_improved` |
| Run-envelope/custody review | Are artifacts, schemas, health, trace, capture adequacy, and evaluation present enough to inspect the run? | `reviewer_notes`; use `artifact_custody_failure` only when the envelope prevents or materially undermines review |
| Live-output hygiene review | Did live narration expose operational machinery, private reasoning, provider details, or local run internals? | `reviewer_notes`; use `private_public_leak` when the reviewed surface materially exposes private machinery |
| Agent-readiness review | Could an autonomous caller rely on this result without additional human inspection? | `safe_for_agent_use` |

A useful revised answer can pass answer-level review while the run still carries
custody, evaluation, live-output, or domain-risk caveats. Do not automatically
turn those caveats into answer-quality failures.

For v0 review records, treat `review_status` as answer-level unless the review
assignment explicitly says the target is custody, live-output, or agent
readiness. Use `safe_for_agent_use` and `reviewer_notes` to carry the more
conservative run-level judgment. This keeps a useful saved answer from being
misclassified as bad advice solely because the surrounding run envelope needs
human inspection.

Write a compact surface summary in `reviewer_notes` when surfaces disagree:

```text
Surfaces: answer=pass; envelope=warn; live_output=fail; agent=with_human_review.
```

Use `needs_followup` when the available artifacts are too incomplete or
conflicted to decide the answer-level review. Use `exclude_from_eval` only when
the run is not reviewable for the current evaluation question.

Use `private_public_leak` when the reviewed surface materially exposes private
machinery, provider reasoning details, internal lane IDs, ledger details, or
other operational internals. If `revised.txt` and `memo.md` are clean but the
live transcript leaks machinery, record that as a live-output hygiene caveat in
notes and decide whether it materially changes the candidate `review_status`.

Use `artifact_custody_failure` when missing, malformed, or contradictory
artifacts prevent trace inspection or make the run envelope misleading. Do not
use it merely because a `modern_partial_reviewable` archive is missing newer
sidecars while core content remains reviewable.

Use `unsupported_new_claim` when the revised answer adds a new factual,
legal, medical, financial, organizational, or other high-stakes domain claim
that is not supported by the conversation or source material. A counsel-first
or diligence-first frame can still be useful, but unsupported domain detail can
still make the answer-level review fail.

### Pilot 2 Disagreement Rules

The validated PR16 synthetic pilot exposed four recurring mixed-outcome cases.
Apply these rules until the taxonomy is revised:

- **Live-output leakage versus saved-answer usefulness:** if `revised.txt` and
  `memo.md` are useful but `live_transcript.txt` leaks machinery, the answer can
  pass while live-output hygiene fails. Mark the leak in `reviewer_notes`; use
  `private_public_leak` as the primary failure only if the leak is material to
  the reviewed surface or makes the run unfit as positive evidence.
- **Degraded or eval-fail envelope versus useful answer:** deterministic
  `evaluation.json` failure, degraded health, or partial custody can block
  agent readiness without proving the revised answer failed. Prefer
  `safe_for_agent_use: with_human_review` or `no`; use `artifact_custody_failure`
  only when the envelope blocks review or misrepresents readiness.
- **Older or partial archives:** `modern_partial_reviewable` and
  `legacy_content_reviewable` are review-readiness facts, not automatic answer
  failures. Review answer-level content when core artifacts are present, and
  record custody limits separately.
- **High-stakes unsupported detail:** legal, regulatory, medical, financial,
  compliance, or employment-sensitive advice can improve at the strategy level
  and still fail answer-level review if it introduces unsupported details that
  could change action.

### Pilot 3 Agent-Readiness Rule

The PR17 disputed-record pilot showed one remaining split: an answer-level pass
with a warn/degraded envelope, unchecked live output, and high-stakes
legal/regulatory domain risk. In that case, reviewers should choose between
`with_human_review` and `no` by asking:

- Can the run still help a human reviewer after caveats are inspected?
- Would an autonomous caller have enough custody and domain support to act
  without rerun, backfill, or material repair?

If the first answer is yes and the second is no, use
`safe_for_agent_use: with_human_review`. If the domain risk, custody gap,
unsupported claim, or action sensitivity makes the run unfit even as
agent-usable evidence, use `safe_for_agent_use: no`.

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
