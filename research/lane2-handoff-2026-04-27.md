# Lane 2 handoff: producer stability track

Date: 2026-04-27
Purpose: hand over the Lane 2 work if conversation context is lost.
Current strategic state: **measurement leads; do not pick architecture before the pre-registered experiments finish.**

## One-sentence next instruction

> Run E2: freeze fingerprint, rerun recall N=5, and score recall determinism against the pre-registered decision tree.

Do **not** start with "what should we build?" The next move is the experiment.

## Copy/paste instruction for coder

You are continuing the Lane 2 producer-stability investigation in `/Users/marcin/Desktop/Apps/lolla-skill`.

Start by reading these files, in order:

1. `research/lane2-producer-stability-design-2026-04-27.md`
2. `research/stability-runs/lane2-stability-experiments-2026-04-27/e5-consensus-simulation.md`
3. `research/stability-runs/lane2-stability-experiments-2026-04-27/e4-broad-meta-sufficiency-rubric.md`
4. `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/characterization.md`
5. `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`

Then execute **E2 only**:

> Given the same frozen fingerprint moves and same source, does `recall_candidates` return the same candidate slate every time?

Use the existing branch if present:

`data/lane2-experiment-e2-recall-determinism-2026-04-27`

Important current-worktree caution: if `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism-runs.json` already exists in the branch, inspect it before overwriting. It may already be an in-progress or tracked E2 artifact.

E2 output should be:

- `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism.md`
- optional structured artifact: `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism-runs.json`

E2 must not call the verifier, must not call Step 6, and must not change product code unless a tiny helper script is needed for reproducibility.

E2 method:

1. Pick one post-fix run as the frozen input source, preferably one of:
   - `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/user-launch-independent-fintech-rerun4.json`
   - `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/user-launch-independent-fintech-rerun6.json`
2. Extract/freeze the validated fingerprint moves used by that run.
3. Call `recall_candidates` N=5 times with:
   - same frozen fingerprint payload
   - same source / packet context
   - same candidate cap
   - same embeddings mode
   - same model corpus
4. Compare:
   - candidate set equality across runs
   - candidate order equality across runs
   - final capped candidate list equality
   - any score / rationale differences if available
5. Report whether H3 is supported, partially supported, or falsified.

Relevant code references:

- `engine/system_b/companion_routing.py`
- `recall_candidates(...)`
- `retrieve_candidate_models(...)`
- `run_fingerprint_call_from_packet(...)`
- `run_verification_call_from_packet(...)` for later E1, not E2

E2 decision rule:

- If candidate set **and order** are identical across N=5, H3 is supported: recall is deterministic under fixed fingerprint. Proceed next to E1.
- If set is identical but order varies, H3 is partially supported: candidate identity is stable, but verifier context may vary. Fix or freeze ordering before E1.
- If candidate set varies, H3 is falsified: recall contributes to churn. Pause before E1 and update the decision tree / architecture conversation.

After E2:

- Open a PR with the E2 artifact.
- Do not implement Path A/B yet.
- Do not run paid verifier tests until E2 is reviewed.

## What has been checked

### PR #41: Step 6 wording contract

Commit: `204a657`

What changed:

- Step 6 now treats anchors evidence-proportionally.
- Three treatments: primary pressure / secondary lens / set aside with a reason.
- Anchor names must be used verbatim.
- No anchor parade.

What this fixed:

- The user-facing answer became more honest about uncertain or weak Lane 2 anchors.
- Weak anchors are not hidden, but also not inflated.

What this did **not** fix:

- It did not improve the upstream producer's ability to choose mental models.
- Step 6 can consume noisy anchors more honestly, but it cannot make Lane 2 select better anchors.

### PR #43: Producer audit

Commit: `06dc94b`

What it found on archived runs:

- Lane 2 was high-trust but uneven-friction on the archived sample.
- 0 false positives across 26 archived surfaced-anchor rows.
- Strict friction yield ranged from low to good depending on case.
- Leak modes included recall vocabulary gaps, quote-validation strictness, verifier interpretive rejection, run-to-run variance, and stochastic anchor identity.

Important post-script from later work:

- The 0-FP finding was true for archived rows.
- It is **not** a stable rerun-level property of Lane 2.

### PR #44: Quote-repair hardening

Commit: `42a60cf`

What changed:

- Verifier quote repair now requires both halves of ellipsis evidence to be reconstructed as a bounded literal span.
- Ellipsis quotes do not fall back to token-overlap repair.
- Token-overlap repair now uses symmetric negation checks.

What this fixed:

- Blocked the Reasoning Mode Router single-fragment ellipsis trust breach.
- Prevented inverse polarity quote repair such as verifier quote dropping a source negation.

What this did **not** fix:

- It did not improve mental-model selection quality.
- It did not prevent noisy anchors that pass with direct literal verifier quotes.

### PR #45: Producer-audit post-script

Commit: `f9640b2`

What it corrected:

- The PR #43 synthesis now says the trust axis passed on archived rows but does **not** pass as a stable rerun-level property.

Why this matters:

- Future readers should not overread "0 false positives" as "Lane 2 reliably has no false positives."

### PR #46: Producer-stability design memo

Commit: `4cc03ed`

What it established:

- Five hypotheses:
  - H1: verifier stochasticity is main churn driver
  - H2: fingerprint variance is upstream driver
  - H3: recall is deterministic; only fingerprint + verifier are stochastic
  - H4: broad/meta models over-accepted because verifier lacks sufficiency checking
  - H5: some variance is honest hypothesis diversity
- Five experiments:
  - E5: consensus simulation
  - E4: broad/meta sufficiency rubric
  - E2: freeze fingerprint, rerun recall
  - E1: freeze candidate slate, rerun verifier
  - E3: rerun fingerprint only
- Binding experiment order:
  - E5 -> E4 -> E2 -> E1 -> E3
- Binding discipline:
  - no cap tuning first
  - no full Sully decomposition first
  - no DSPy first
  - no more single-run audits expecting trust to be stable
  - no fix because it sounds elegant

### PR #47: E5 consensus simulation

Commit: `5900d7c`

Sample:

- Post-fix only, rerun4-rerun7.
- Excludes rerun3 because rerun3 was pre-fix and contains the removed RMR trust breach.

Result:

| k | Anchors | Noisy rate | Friction yield strict / any-honest |
|---:|---:|---:|---:|
| 1 | 13 | 31% | 33% / 67% |
| 2 | 4 | 50% | 33% / 33% |
| 3 | 1 | 0% | 17% / 17% |
| 4 | 0 | n/a | 0% |

Interpretation:

- Consensus at k=2 makes trust worse because noisy anchors recur.
- k=3 cleans trust but leaves only one cluster yielding.
- k=4 yields nothing.
- Path C, consensus, is ruled out as the first lever on this case.
- Rare acceptable anchors look like honest diverse reads; suppressing them for stability would degrade product value.

### PR #48: E4 broad/meta sufficiency rubric

Commit: `df801b3`

Result:

- H4 strongly supported.
- Recurring noisy anchors are rubric-detectable:
  - Cognitive Dissonance fails because the quote has no two-belief structure or motivated reframing.
  - Checklists fails because a one-time numbered plan is not omission-risk discipline in a repeated process.
  - Feedback Loops fails because a pre-registered decision rule is not circular causality.
- Hybrid Path A + Path B is leading, but not authorized for implementation yet.

Rubric tally:

- Gate-buildable / sufficiency-test specifiable:
  - high confidence: cognitive-dissonance, checklists, feedback-loops
  - medium / medium-high confidence: time-tested-validation, probabilistic-thinking
- Prompt-only / needs model metadata:
  - step-back
  - wysiati
  - representativeness-heuristic
- Clean control:
  - optimism-bias-and-planning-fallacy passes

Critical caveat:

- `gate_buildable` means a local quote-level sufficiency test can be specified.
- It does **not** mean "build regex."
- Implementation form remains TBD: deterministic markers, narrow LLM sufficiency check, or model metadata are all candidates.
- E4 makes the hybrid track plausible and concrete enough to test on more cases. It does **not** authorize implementation yet.

## What has not been checked

### E2: recall determinism

Not complete unless an in-progress branch/artifact says otherwise.

Question:

> Given the same frozen fingerprint moves and same source, does recall return the same candidate slate and order?

Why it matters:

- If recall is deterministic, E1 can cleanly isolate verifier stochasticity.
- If recall is not deterministic, the architecture conversation changes before paid verifier tests.

### E1: verifier stochasticity

Not run yet.

Question:

> Given the same frozen candidate slate and same source, does verifier accept/reject the same models?

Why it matters:

- If verifier is unstable on identical input, H1 is supported.
- If verifier is stable but whole pipeline churns, variance is upstream.

### E3: fingerprint variance

Not run yet.

Question:

> Given the same conversation, does fingerprint extract the same reasoning moves and evidence quotes?

Why it matters:

- If fingerprint is unstable, Sully-style decomposition starting at fingerprint becomes more plausible.
- If fingerprint is stable, focus stays downstream.

### E4 rubric on more cases

Not done.

The E4 rubric is anchored on one conversation. Before implementing the hybrid Path A/B:

- test the gate-buildable models on more conversations
- check whether the same models can surface acceptable anchors elsewhere
- verify the rubric does not over-reject useful friction

Recommended additional cases:

- `mid-level-consultant-decides`
- `mother-deciding-address-year`
- `marcus-equity`
- `third-year-phd-student`

## What we have to deal with

### 1. Producer stability, not quote validation

Quote validation is now hardened. The active problem is direct literal verifier acceptance of weak/broad/meta anchors.

### 2. Broad/meta sufficiency

Models like Checklists, Cognitive Dissonance, Feedback Loops, Step Back, WYSIATI, and RH can look locally plausible because they are broad. The system needs a way to distinguish:

- actual mechanism present in the quote
- topical adjacency or surface resemblance

### 3. Honest diversity vs noise

Some variance is good:

- Step Back, Optionality, Premortem, RH appeared as rare but defensible reads.

Some variance is bad:

- Cognitive Dissonance and Checklists recurred as noisy anchors.

The product wants useful friction, not canonical sameness. Do not optimize for stability by deleting rare defensible reads.

### 4. Implementation form for Path A

Path A is "anchor-sufficiency gate," but its implementation form is undecided:

- deterministic marker checks
- narrow LLM sufficiency call
- model metadata-driven rules
- hybrid of the above

Do not assume regex. E4 proves rubric buildability, not regex buildability.

### 5. Path B prompt restructuring

For fuzzy models, the verifier likely needs better mechanism-marker instructions.

Examples:

- Step Back vs Problem Framing And Reframing
- WYSIATI vs generic clarifying questions
- RH vs Base Rates / OB+PF

This should be scoped after E2/E1/E3, not before.

## What to double-check

1. **Branch state before editing.**
   - Current branch may already be `data/lane2-experiment-e2-recall-determinism-2026-04-27`.
   - There may already be an `e2-recall-determinism-runs.json` artifact in the branch.
   - Inspect before overwriting.

2. **No sample contamination.**
   - For current-system behavior, use post-fix runs only.
   - Do not include rerun3 as current-system evidence; it predates PR #44 and includes the removed RMR trust breach.

3. **E2 must not accidentally run verifier.**
   - E2 is recall-only.
   - Do not produce accepted anchors.
   - Do not judge trust.

4. **Candidate order matters.**
   - Same set but different order is not fully deterministic because verifier context order may influence acceptance.

5. **Embeddings mode.**
   - Document whether embeddings are off or on.
   - If embeddings are on and recall varies, isolate whether embedding retrieval caused variance.

6. **Cap behavior.**
   - Candidate cap is 60 in the current Lane 2 path.
   - If ordering changes near the cap boundary, the verifier slate can change even when the broader candidate universe is similar.

7. **Do not overclaim from one case.**
   - E5/E4 are strong but case-1 only.
   - They justify the next experiments and a leading hypothesis, not implementation.

8. **Keep PRs and commits explanatory.**
   - Every PR should say what it proves and what it does not prove.
   - Every experiment should map back to the pre-registered decision tree.

## How to think about Lane 2 now

Lane 2 has three layers:

1. **Evidence safety**: improved.
   - Quote repair hardened.
   - Literal evidence discipline is much better.

2. **User-facing honesty**: improved.
   - Step 6 wording now handles anchors proportionally.

3. **Producer selection**: still unstable.
   - Same source produced many different anchors.
   - Noisy broad/meta anchors can recur.
   - This is the active frontier.

The current system is not "bad" and not "done." It is now observable enough to improve without guessing.

The most important lesson:

> We have made the system more honest, safer, and more measurable. We have not yet made Lane 2 reliably good at choosing mental models.

Another important lesson:

> Stability alone is not the goal. Stable noisy anchors are bad; rare defensible anchors are valuable.

And the governing discipline:

> The prior is verifier/sufficiency. The memo outranks the prior.

## How to finish this Lane 2 task

Do not declare Lane 2 "fixed" after E2/E1/E3. The finish line is a verified architectural change that improves producer selection without destroying useful friction.

### Phase 1: finish the stage-isolation experiments

1. E2: recall determinism
2. E1: verifier stochasticity, if E2 supports clean verifier isolation
3. E3: fingerprint variance, especially if E1 does not explain churn

Each experiment needs:

- artifact in `research/stability-runs/lane2-stability-experiments-2026-04-27/`
- hypothesis update
- decision-tree implication
- "what this did not prove" section

### Phase 2: apply the pre-registered decision tree

Use `research/lane2-producer-stability-design-2026-04-27.md` §7.

Likely current path, pending E2/E1/E3:

- Path C: ruled out as first lever by E5.
- Path D: premature unless fingerprint/upstream instability dominates.
- Hybrid Path A+B: leading after E4 but needs more evidence.

### Phase 3: validate hybrid Path A+B on more cases before implementation

Before writing code:

1. Apply E4 rubric to at least 2-3 additional cases.
2. Include at least one case where broad/meta models should pass, if available.
3. Check over-rejection risk.
4. Decide implementation form:
   - deterministic marker gate
   - narrow LLM sufficiency gate
   - verifier prompt restructure
   - model metadata additions
   - hybrid

### Phase 4: implementation design memo

Only after the experiments:

- write an implementation memo for the chosen path
- specify exact behavior
- specify tests
- specify live validation
- specify rollback / stop conditions

Do not jump from E4 directly into code.

### Phase 5: implement smallest validated fix

Possible candidate if evidence keeps pointing the same way:

- Add a narrow broad/meta sufficiency layer for high-confidence models:
  - cognitive-dissonance
  - checklists
  - feedback-loops
  - maybe time-tested-validation
  - maybe probabilistic-thinking
- Update verifier prompt for fuzzy overlap models:
  - step-back
  - wysiati
  - representativeness-heuristic

But this is not authorized yet.

### Phase 6: validation after implementation

Validation must include:

- repair-local vs whole-run reporting if quote repair touched anything
- trust classification of all surfaced anchors
- friction yield strict / any-honest
- noisy_adjacent / false_positive rate
- hidden / omitted anchor behavior if Step 6 is involved
- multi-run behavior, not single-run only
- at least the case-1 rerun set and 2-3 additional cases

### Phase 7: satisfaction criteria

We are ready to say this Lane 2 part is satisfactory when:

1. The stage-isolation experiments identify the main variance source(s).
2. The chosen fix follows the decision tree rather than taste.
3. The fix is validated on more than one conversation.
4. Trust improves or stays within an explicit acceptable bound.
5. Useful friction yield is preserved or improved.
6. Broad/meta noisy anchors are reduced, especially the recurring E5 class.
7. Rare defensible reads are not erased by over-stabilization.
8. Step 6 still treats anchors proportionally.
9. HOW_IT_WORKS / SKILL / research docs do not overclaim.
10. We can honestly say:

> Lane 2 is not just wired and observable; it is measurably better at surfacing useful mental-model pressure while preserving trust.

Until then, the correct statement remains:

> Lane 2 is safer and more measurable, but producer selection is still under active investigation.

## Do-not-do list

- Do not start with candidate-cap tuning.
- Do not start with full Sully decomposition.
- Do not start with DSPy.
- Do not run more single-run audits and treat them as stable trust evidence.
- Do not change Step 6 wording while the producer is the active problem.
- Do not loosen quote validation.
- Do not build regex gates just because E4 says `gate_buildable`.
- Do not optimize for stability if it suppresses rare defensible friction.
- Do not pick a fix because it sounds elegant.

## Suggested next PR sequence

1. `data(lane2): E2 recall determinism`
   - artifact: `e2-recall-determinism.md`
   - optional structured data: `e2-recall-determinism-runs.json`

2. If E2 supports recall determinism:
   - `data(lane2): E1 verifier stochasticity`

3. Then:
   - `data(lane2): E3 fingerprint variance`
   - or skip/postpone E3 only if the decision tree explicitly says E1/E2 already resolved the lever

4. After E2/E1/E3:
   - `docs(lane2): choose producer-stability architecture track`

5. Then implementation PR, if authorized:
   - title TBD based on decision tree

## Current known branch/worktree note

At the time this handoff was written, the working tree was on:

`data/lane2-experiment-e2-recall-determinism-2026-04-27`

and had unrelated untracked files:

- `.claude/`
- `research/conversation-first-extraction-evaluation-2026-04-24.md`

and an existing E2-looking artifact in the branch:

- `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism-runs.json`

Treat the E2 artifact as in-progress unless verified otherwise. Do not overwrite it blindly.

## Final reminder

The system has been made more honest by refusing to let each local win become a global claim. Keep that discipline.

The measurement leads.
