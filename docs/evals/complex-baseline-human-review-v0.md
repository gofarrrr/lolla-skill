# Complex Baseline Human Review v0

Status: human/product review seed set
Date: 2026-06-27
Review slice: `complex_baseline_human_review_v0`

This note reviews the six clean complex baseline runs as the first
human-reviewed Lolla evaluation seed set.

The review question is not whether the runs completed. The deterministic
harness already showed full capture, healthy run health, clean provider-boundary
status, clean saved product output, zero quote fabrication, and
`caller_action: use_revised_answer`.

The review question is narrower and more important:

```text
Can a reviewer explain why the revised answer improved or failed the original
answer using current artifacts, without relying on vibe?
```

## Scope And Boundaries

This is human/product review, not an LLM judge. No model calls were made for
this review, and `$lolla` was not run.

This slice did not change runtime code, prompts, `SKILL.md`, archived runs,
specialist extractors, evaluation scripts, graph/memory behavior, embeddings,
chunking, quote validation, or corpus population.

This slice also did not automatically populate `lolla.human_review.v0` in
archive records. The labels below are review evidence for PR30. They are not an
answer-quality score, not generic helpfulness scoring, not agent approval, and
not a calibrated judge dataset yet.

## Method

Inputs were the six complex baseline archives, referenced by case id and run id:

| # | case id | run id |
|---|---|---|
| 1 | `ceo-remove-founding-cofounder` | `20260627T093131Z_59d153` |
| 2 | `accept-operations-role-startup` | `20260627T132700Z_bae7f3` |
| 3 | `launch-public-enterprise-beta` | `20260627T104146Z_7bfe79` |
| 4 | `pre-sell-undefined-consulting` | `20260627T133637Z_cad396` |
| 5 | `pivot-company-product-strategy` | `20260627T110450Z_5d2da7` |
| 6 | `deploy-assisted-intake-routing` | `20260627T130339Z_4cd3cb` |

For each run, I inspected:

- `conversation.txt`
- `extraction.json`
- `revised.txt`
- `memo.md`
- `agent_result.json`
- `evaluation.json`
- `extraction_adequacy_report.json`
- `reasoning_trace.json`
- `result.json` only for audit-pressure details

The labels map to `lolla.human_review.v0`:

- `review_status`: answer-level pass/fail for the saved revised answer and
  memo.
- `primary_failure_mode`: first upstream failure from
  `docs/evals/lolla-failure-taxonomy.md`, or `none`.
- `severity`: severity of that primary failure.
- `useful_friction`, `noisy_friction`, `missing_friction`: whether the revised
  answer added earned pressure, added unsupported/noisy pressure, or missed a
  pressure that should have changed action.
- `revised_answer_improved`: whether the revised answer improved the decision
  surface.
- `safe_for_agent_use`: human reliance label, not an approval action.

Answer-level review is separate from run-envelope and custody review. In all
six cases, the saved artifacts were enough to review the answer-level delta.
Each run still had `evaluation.overall: warn` because
`live_output_health: not_checked`. That is recorded as a caveat, not treated as
an answer failure by default.

## Review Table

| case / run | review_status | primary_failure_mode | severity | useful_friction | noisy_friction | missing_friction | revised_answer_improved | safe_for_agent_use | action-changing delta | artifact sufficiency | reviewer note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ceo-remove-founding-cofounder` / `20260627T093131Z_59d153` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Moves from a gated reset to immediate authority transfer, with a constrained transition role, explicit stop-loss rules, and boundaries for the product lead and COO. | Sufficient. Full transcript, extraction, revised answer, memo, agent result, evaluation, and reasoning trace explain the shift; span-grounded assistant stance would make future review easier but was not needed here. | The revised answer made the reset operationally falsifiable instead of leaving authority ambiguity alive. |
| `accept-operations-role-startup` / `20260627T132700Z_bae7f3` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Converts both offers into written operating-term tests: current role must prove authority by Friday; startup must provide a bounded six-month agreement by Monday; spouse consent becomes capacity evidence. | Sufficient. Artifacts make the original concern and revised symmetry clear; live-output health remains unchecked. | The revision prevented the current-company option from winning merely by seeming safer, while also refusing the startup title as evidence. |
| `launch-public-enterprise-beta` / `20260627T104146Z_7bfe79` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Removes default priority for the marquee buyer, gives both prospects the same paid pilot shape, scores buyer behavior, and turns gates into owner-threshold-stop tripwires. | Sufficient. The artifacts show the move from public enterprise posture toward private proof and from logo aura toward evidence; current semantic records remain artifact-level for stance lineage. | The revision made ambition conditional on cash, procurement clarity, support load, and diligence evidence. |
| `pre-sell-undefined-consulting` / `20260627T133637Z_cad396` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Keeps one paid pilot, but corrects the overread of polish as pure status: the Friday gate becomes a client-ready scoped brief, with only a tiny agency polish role and harder customer acceptance. | Sufficient. Revised answer and memo explain both what survived and what was taken back; artifacts are enough to distinguish credibility from scope expansion. | This is the cleanest evidence that useful friction is not always more skepticism; sometimes it means retracting an overconfident psychological read. |
| `pivot-company-product-strategy` / `20260627T110450Z_5d2da7` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Changes sequence from market proof first to a 14-day capacity and obligation gate before the 60-day market gate; turns the nonprofit core into a staffed, date-bounded maintenance promise. | Sufficient. The artifacts justify the sequencing change even though the delta-card signal was thinner than in other runs; frame pressure, memo, revised answer, and agent summary carry the rationale. | The revision protects current obligations and team capacity before letting the higher-ACV prospect consume the company. |
| `deploy-assisted-intake-routing` / `20260627T130339Z_4cd3cb` | `pass` | `none` | `none` | `present` | `absent` | `absent` | `yes` | `with_human_review` | Compresses nine gates into four must-pass operating controls, adds a 48-hour backlog diagnosis, requires stop conditions, and narrows what the pilot can prove. | Sufficient. The original checklist, revised answer, memo, and audit pressure make the action delta clear; healthcare-adjacent operational risk keeps agent reliance conservative. | The revision reduced checklist theater and asked whether the clinic could actually operate the controls under pressure. |

## Findings

All six answer-level reviews pass. The revised answers improved the decision
surface in ways that are explainable from current artifacts.

What Lolla consistently did well:

- Preserved the useful core of the original advice instead of reflexively
  reversing it.
- Turned smooth recommendations into operating controls: authority transfer,
  written terms, buyer behavior tests, client-ready scope, capacity gates, and
  rollback triggers.
- Challenged status and aura without flattening legitimate signals. The
  pre-sale case is especially useful because the revision corrected an
  overconfident status interpretation.
- Made gates more binding by adding owners, thresholds, stop actions, timing,
  or written acceptance.
- Kept deterministic run readiness separate from answer quality.

Where the revised answers materially changed action:

- Cofounder case: authority moves before cooperation is tested.
- Career case: both paths must produce written operating agreements under
  real deadlines.
- Enterprise beta case: buyer priority is earned by payment, procurement
  clarity, and tolerance for scope, not by company size.
- Consulting pre-sale case: the pilot must be customer-ready without letting
  polish define the offer.
- Product pivot case: capacity and existing obligations become the first gate.
- Clinic deployment case: the launch is judged by operable controls and a
  backlog diagnosis, not by a long checklist.

Useful friction appeared in every run. It was earned by the trace, actionable,
and proportionate. The strongest pattern was action-changing friction:
thresholds, sequence changes, stop rules, evidence gates, and bounded written
terms.

No material noisy friction appeared in the revised answers. Two cases are
especially informative: the consulting case removed a potentially noisy status
read, and the clinic case removed checklist excess rather than adding more
controls.

No material missing friction appeared at answer level. There are still artifact
caveats: live output was not independently checked; user values/priorities are
not first-class measured fields; assistant stance lineage is not span-grounded;
and live constraints/dropped threads are mostly turn-reference grounded rather
than span-grounded. Those caveats did not block review of these six answer
deltas, but they explain why automatic labels and judge calibration are still
premature.

Artifact sufficiency was strong enough for PR30's review question. For each
case, `conversation.txt`, `extraction.json`, `revised.txt`, `memo.md`,
`agent_result.json`, `evaluation.json`, `extraction_adequacy_report.json`, and
`reasoning_trace.json` were enough to explain why the revised answer improved
the original. The artifacts are not yet enough to remove human review from the
loop or to claim autonomous agent approval.

## Candidate Adversarial Pairs / Judge Traps

These six runs are good seeds for future adversarial pair fixtures:

- Smoother original versus rougher but safer revision. A judge that rewards
  fluency may prefer the original in several cases, even when the revision adds
  a binding gate.
- Long checklist versus usable operating controls. The clinic case is the
  clearest example: nine gates can look safer than four gates while being less
  operable.
- Emotional/status framing versus written operating terms. The career case
  tests whether a judge values concrete terms over more resonant identity
  language.
- Market excitement versus capacity/obligation gate. The pivot case tests
  whether a judge over-rewards a higher-ACV opportunity before checking current
  delivery obligations.
- Professional polish as legitimate signal versus status spending. The
  consulting case tests whether a judge can distinguish commercial credibility
  from premature brand theater.
- Broad AI launch language versus narrow operational pilot. The clinic case
  tests whether a judge can prefer constrained live learning over expansive
  automation language.
- Marquee customer aura versus buyer-behavior proof. The enterprise beta case
  tests whether a judge overweights the larger prospect.
- Founder loyalty versus authority ambiguity. The cofounder case tests whether
  a judge can reward a transition that preserves trust while moving real
  decision rights.

## What This Does And Does Not Justify

This does justify:

- using the six runs as a small human-reviewed seed set;
- building an actionable-delta rubric through PR31;
- extracting adversarial pair fixtures through PR32;
- using these examples to refine taxonomy language;
- using the table above as product-taste evidence for what useful Lolla
  friction looked like.

This does not justify:

- a generic LLM judge;
- a calibrated judge yet;
- runtime specialist integration;
- prompt rewrite;
- quote-validation repair;
- `conversation_understanding_ir.v0`;
- graph DB, embeddings, chunking, or memory layer;
- automatic human labels;
- agent approval;
- treating `evaluation.json` as answer-quality scoring;
- treating `caller_action: use_revised_answer` as human review.

## Recommended Next Slice

PR31 now defines the rubric that this note recommended:

```text
docs/evals/actionable-delta-rubric-v0.md
```

PR31 came before adversarial fixtures because the review table showed the
common unit of improvement: action, threshold, sequence, evidence gate, stop
rule, written term, user question, narrowed scope, and overclaim retraction.
The rubric defines those units before PR32 turns them into pairwise judge
traps.

The rubric should reject smoother prose, more warmth, longer answers, generic
comprehensiveness, more caveats without action change, and judge-palatable
blandness as improvement by themselves. It should let reviewers say exactly
what changed in the user's next action and should include no-op examples from
adjacent traces when available.

Next:

```text
docs/evals/adversarial-pair-fixtures-v0.md
```

PR32 uses the traps above as the first fixture candidates. The next evaluation
slice should expand beyond the six-case seed with a small human-reviewed corpus
batch, not a judge.

## Review Receipt

- Six of six runs reviewed.
- Six answer-level `pass` labels.
- Six `primary_failure_mode: none` labels.
- Six `revised_answer_improved: yes` labels.
- Six `safe_for_agent_use: with_human_review` labels because saved artifacts
  passed answer-level review but live-output health remained `not_checked`.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No `$lolla` run.
- No model calls.
