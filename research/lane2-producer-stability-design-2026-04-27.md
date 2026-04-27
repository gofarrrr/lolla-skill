# Lane 2 producer-stability design memo

Date: 2026-04-27
Branch: `docs/lane2-producer-stability-design-2026-04-27`
Status: design memo, not code, not commitment to architecture
Inputs:
- `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md` (incl. §8 post-script)
- `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/characterization.md`
- `research/lane2-quote-repair-validation-amendment-2026-04-27.md`
- `research/lane2-next-track-decision-2026-04-27.md`

## Opening question

> Why does identical source produce 14 unique anchors across 5 reruns, with noisy anchors in every run?

This memo does not answer the question. It scopes the investigation that should answer it before any architectural change to Lane 2 is committed. The lesson of the last week is sharp: in this system, premature fixes create beautiful evidence and then betray us. **The measurement has to lead.**

## §1 Current system state

The system has matured through three maturity stages:

- **Stage 1: can it run?** Yes. Lane 2 pipeline works end-to-end.
- **Stage 2: can it explain itself?** Mostly yes. Audit artifacts, quote-repair logs, rejection reasons, characterization reports are all in place.
- **Stage 3: can it make stable, high-trust judgments?** Not yet. The producer's mental-model selection is observable but not reliable enough.

The honest one-sentence framing:

> Lane 2 is connected and evidence-aware, but the producer has unstable judgment about which mental models deserve to surface.

That distinction matters. The pipeline is no longer "vibes-based." It is wired, observable, and safer than before. But the **selector** layer — what models the verifier accepts — is unstable in a way that recent measurement has made visible.

The system has three layers, each at a different maturity:

1. **Evidence safety** — significantly improved (PR #44 quote-repair hardening: both-halves ellipsis rule, symmetric negation check). Remaining issue: a quote can be literal and still not sufficiently support the model (the Checklists / Cognitive Dissonance pattern).
2. **User-facing honesty** — meaningfully improved (PR #41 Step 6 wording contract: primary pressure / secondary lens / set aside with a reason / verbatim names / no anchor parade). Step 6 can soften bad inputs but cannot make the producer choose better anchors.
3. **Producer selection** — the live wound. Same source, five reruns, 14 unique anchors, noisy/borderline anchors in every rerun.

This memo targets layer 3.

## §2 Evidence from PR #43 and PR #44 / #45

### PR #43 (producer audit) — what we knew

The audit found Lane 2 was high-trust but uneven-friction across 7 archived runs:

- 0 false positives across 26 surfaced anchor rows (archived corpus)
- Strict friction yield 14% (Marcus) to 80% (case 3)
- 5 leak modes: recall vocabulary gaps, quote-validation strictness, verifier interpretive rejection, run-to-run variance, stochastic anchor identity within ambiguous clusters

The §6 decision-tree input said "trust axis: pass; do not loosen quote validation; friction yield: mixed/uneven."

### PR #44 / #45 (quote-repair + post-script) — what changed

Validating a producer-side change (quote-validation repair) on case 1 surfaced something the archived audit had not:

- **N=5 fresh reruns of identical source** produced 14 unique anchors (only Optimism Bias And Planning Fallacy in 4/5; rest churned).
- **23 surfaced anchors total. 7 (30%) classified `noisy_adjacent`. 3 (13%) borderline. 13 (57%) acceptable.**
- **Every rerun produced at least one noisy or borderline anchor.**
- **All 7 noisy anchors entered Step 6 via direct literal verifier acceptance** — they did not go through quote repair.

The PR #45 post-script narrowed the §2 audit headline accordingly. The trust axis was clean for the archived corpus but is **not** a stable rerun-level property of Lane 2.

The quote-repair branch (PR #44) is mechanical hardening and does what it promises; it is not a quality lift. The producer-side instability was hiding behind it.

## §3 What the instability could mean

The empirical fact: identical source → 14 unique anchors across 5 reruns, with noisy anchors in every run.

That fact is consistent with several different underlying causes:

- **The verifier is the main stochastic stage.** Same candidate slate, same source quotes, but the verifier's accept/reject judgment varies meaningfully across runs.
- **The fingerprint is unstable.** The reasoning moves extracted from the conversation differ across runs, leading to different downstream candidate slates and different verifier inputs.
- **Recall is unstable given variable fingerprint.** Even if recall is deterministic given fixed inputs, the fingerprint variance propagates as candidate-slate variance, and the verifier sees a different competition each time.
- **The verifier has a sufficiency blind spot for broad/meta models.** Models like Reasoning Mode Router, Checklists, Cognitive Dissonance, Step Back, Problem Framing, Decomposition can be accepted with literal quotes that show topical adjacency without the model's actual mechanism. This is the "noisy literal accept" pattern we observed.
- **The producer is doing something genuinely ambiguous and surfacing different defensible reads on different runs.** Like Marcus C6 in the audit. Some of the run-variance is honest hypothesis diversity, not failure.
- **Multiple of the above interact**, producing total stochasticity higher than any single stage's contribution.

We do not yet know which of these dominates. The N=5 characterization shows the symptom but does not isolate the stage. **Without isolation, picking architecture would repeat the single-evidence mistake.**

## §4 Competing hypotheses

Five testable hypotheses, deliberately framed so that each has a falsification path:

### H1 — Verifier stochasticity is the main churn driver

Same source quote, same model in the candidate slate → verifier accepts on some runs and rejects on others. Run-to-run variance comes mostly from the verifier prompt's nondeterminism (model temperature, prompt sensitivity, context window jitter).

**Falsified if**: when we freeze the candidate slate and rerun ONLY the verifier on a fixed conversation, accept/reject outcomes are stable across runs.

### H2 — Fingerprint variance is the upstream driver

The fingerprint extracts different reasoning moves on different runs. That changes the candidate slate that recall produces (since recall uses fingerprint moves as input). The verifier sees different competing models each time.

**Falsified if**: fingerprint output is highly consistent across runs (same moves, same evidence quotes, same span coverage), and downstream churn persists anyway.

### H3 — Recall is deterministic; only fingerprint and verifier are stochastic

Given fixed fingerprint moves and fixed conversation, recall always produces the same 60-candidate slate (deterministic keyword overlap + embeddings).

**Falsified if**: same fingerprint + same source produces different candidate slates (e.g., different keyword tie-breaking, embedding drift, ordering differences that affect cap behavior).

### H4 — Broad/meta models are over-accepted because the verifier doesn't check mechanism sufficiency

When a quote is literal and topically adjacent, the verifier accepts the model even if the model's specific mechanism isn't actually present in the quote. Examples from the N=5 characterization:

- *Checklists* on a numbered-list quote — surface match, missing the cluster's load-bearing pre-registration mechanism
- *Cognitive Dissonance* on a fundamentals-vs-tactics pushback — stretched fit, no clear CD mechanism
- *Reasoning Mode Router* on a clarifying-questions quote — meta-cognitive overlay, no specific RMR mechanism

**Falsified if**: an anchor-sufficiency check after verifier acceptance flags very few accepts, and those flags do not correlate with the noisy_adjacent classifications from human review.

### H5 — Some run-variance is honest hypothesis diversity, not failure

Like Marcus C6 in the audit (Sunk Cost / Endowment / Inversion / PFR all defensible). Different runs surface different defensible primaries on the same anchor-worthy cluster. That variance is genuine product behavior, not producer noise.

**Falsified if**: the N=5 reruns' anchors don't map cleanly to the audit's gold cluster table — i.e., the variance doesn't track ambiguity-cluster behavior, it tracks something else.

These hypotheses are not mutually exclusive. Multiple may hold simultaneously. The point of testing them is to identify which one the **first remediation lever** should target.

## §5 Stage-isolation experiments

Five controlled experiments. Each isolates one source of variance.

### Experiment 1 — Freeze candidate slate, rerun verifier (tests H1)

Take one case (`user-launch-independent-fintech`) and one fixed candidate slate (e.g., the one from rerun4). Run only the verifier N=5 times against that fixed slate + same source.

**Measures:** accept/reject churn at the verifier given identical input.

**Implementation:** mock the recall step to return the saved slate; call `run_verification_call_from_packet` repeatedly; record acceptance set per run.

**Cost:** N verifier calls only (~$0.50 each).

**Decision rule:** if churn is high → H1 is supported, verifier is the dominant stochastic layer. If churn is low → upstream variance dominates.

### Experiment 2 — Freeze fingerprint, rerun recall (tests H3)

Take one case, freeze fingerprint moves (use saved validated moves from a prior run). Run recall N=5 times against the same source + fingerprint.

**Measures:** candidate-slate churn given identical fingerprint + source.

**Implementation:** mock fingerprint, call `recall_candidates` repeatedly, compare slates.

**Cost:** zero (recall is non-LLM).

**Decision rule:** if recall is deterministic, the slate identity proves H3. If not, recall has its own stochasticity (likely from embedding fluctuation if `--embeddings on`, or from set-ordering issues).

### Experiment 3 — Rerun fingerprint only (tests H2)

Take one case, run fingerprint N=5 times against the same source.

**Measures:** fingerprint move churn — counts, identity, evidence quote stability.

**Implementation:** call `run_fingerprint_call_from_packet` repeatedly; compare validated moves across runs.

**Cost:** N fingerprint calls.

**Decision rule:** if fingerprint moves are stable across runs, H2 is falsified — extraction is not the variance source. If unstable (different moves, different quotes, different counts), the Sully-style decomposition argument strengthens.

### Experiment 4 — Broad/meta anchor sufficiency audit (tests H4)

Take the noisy anchors from the N=5 characterization (Reasoning Mode Router, Checklists, Cognitive Dissonance, possibly Time Tested Validation, Step Back) and ask, per anchor:

- What local quote-level mechanism would need to be present for this model to be load-bearing?
- Did the source actually contain that mechanism, or did the verifier accept on topical adjacency?

This is a manual audit, not a coding experiment. Output is a per-model "sufficiency rubric" — what the verifier should be checking for that it currently doesn't.

**Implementation:** Claude drafts the rubric per anchor; Marcin reviews. Then test the rubric against the N=5 acceptances.

**Cost:** session time, no LLM calls.

**Decision rule:** if a sufficiency rubric cleanly distinguishes noisy anchors from acceptable anchors → an anchor-sufficiency gate is the right next lever. If the rubric is hard to specify or the distinction is fuzzy → broad-model handling is harder than a gate, and prompt restructuring may be needed instead.

### Experiment 5 — Consensus simulation (tests H5 + product viability)

Compute "consensus anchors" at thresholds k=1, 2, 3, 4, 5: anchors that surface in at least k of N runs on the same source.

**Sample discipline (load-bearing).** The primary decision input for E5 must use **only post-fix reruns** generated after PR #44's both-halves ellipsis rule and symmetric negation check. The historical N=5 table from `characterization.md` may be reported as context, but `rerun3` is **pre-fix** and includes the trust-breaching single-fragment ellipsis repair (Reasoning Mode Router) that the current system cannot produce. Mixing pre- and post-fix samples would muddy the very thing E5 is supposed to clarify.

Concretely:

- **Default sample**: post-fix `rerun4`–`rerun7` from `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/`. That is N=4 of current-system behavior — sufficient for k=1–4 thresholds and a meaningful first read.
- **If k=5 thresholds are desired**: run one additional post-fix rerun on the same archived case-1 inputs to create a clean current-code N=5 sample. Do not synthesize this by including `rerun3`.
- **Reporting**: separate "historical N=5 (mixed pre/post-fix, including rerun3)" from "current-code consensus evidence (post-fix only)." The current-code sample is what feeds the §7 decision tree.

**Measures:**
- Friction yield at each threshold (how many anchor-worthy clusters yield at least one consensus anchor)
- Trust at each threshold (do consensus anchors have lower noisy_adjacent rate)
- Lost-but-honest yield (does requiring consensus kill rare-but-defensible anchors)

**Implementation:** post-hoc analysis of `rerun4`–`rerun7` JSONs. Optional: one additional fresh post-fix rerun if k=5 evidence is wanted.

**Cost:** zero for the N=4 default; one fresh pipeline call if N=5 is desired.

**Decision rule:** if consensus at k≥2 substantially improves trust without killing friction → multi-run product shape becomes a real architecture candidate. If consensus at k≥2 kills friction yield to single digits → consensus is a dead-end and the answer must be in single-run quality.

## §6 Candidate fixes

This memo does not commit to a fix. It scopes the candidate fixes that the experiments should be designed to discriminate between.

### Path A — Anchor-sufficiency gate

After the verifier accepts a model with a literal quote, run a stricter local check:

> Does this exact quote support this exact model mechanism, or is it merely topically adjacent?

Could be deterministic (using model metadata: required mechanism markers per model family) or another narrow LLM call (a "sufficiency" prompt that asks one model whether the quote literally exposes the model mechanism).

**Pros:** directly targets the noisy literal accepts (Experiment 4 maps to this). Doesn't redo architecture. Fits the trust-first discipline.

**Cons:** adds a stage / cost. May reduce friction yield. Could become another verifier loop if not tightly scoped.

**Test of fit:** Experiment 4. If a per-model sufficiency rubric exists and cleanly catches the noisy anchors, this path is real.

### Path B — Verifier prompt restructure

Make the verifier prompt itself stricter about mechanism evidence:

- Quote must contain the model's local mechanism markers, not just topical surface
- Broad/meta anchors require explicit local mechanism markers ("numbered list" does not imply Checklists; "tension" does not imply Cognitive Dissonance; "asking questions" does not imply Reasoning Mode Router)
- Verifier rejects with a new reason like `mechanism_topical_only` rather than accepting weak fits

**Pros:** cheaper than a new gate. Stays within the existing architecture. Directly addresses observed noisy patterns.

**Cons:** prompt tightening may reduce useful anchors. Stochasticity may persist if the underlying model judgment is the issue, not the prompt. We have prior verifier-prompt history (PR #43's v1/v2/v3 attempts) that should be reviewed for what's already been tried.

**Test of fit:** Experiment 1 (verifier stochasticity) + Experiment 4 (sufficiency rubric). If the verifier is stochastic AND a sufficiency rubric exists, prompt restructuring informed by the rubric becomes the natural lever.

### Path C — Deterministic constrained verification

Run the verifier multiple times on the same input and take the consensus. Or constrain the verifier with a more explicit per-model rejection schema.

**Pros:** addresses stochasticity directly.

**Cons:** N× cost. May over-prune if consensus threshold is too strict. Doesn't address sufficiency, only stability.

**Test of fit:** Experiment 5 (consensus simulation).

### Path D — Producer decomposition (Sully-style, full)

Replace the single fingerprint + single verifier with multiple narrower stages: span extraction, shape classification, type-scoped recall, per-shape verification, fan-in.

**Pros:** matches the broader architectural critique that has been around since the audit started.

**Cons:** large architectural commitment. Should not be undertaken without evidence the simpler fixes (A, B, C) won't work. Risk of building elegant architecture before knowing where the actual fault line is.

**Test of fit:** if Experiments 1–5 all show fundamental instability that can't be addressed at the verifier or sufficiency layer, decomposition becomes the architectural answer. Until then, it's premature.

## §7 Decision tree

After the five experiments, the architectural choice is determined by:

| Pattern of findings | Recommended first track |
|---|---|
| H1 supported, H4 supported (verifier stochastic AND sufficiency rubric exists) | **Path A or B** — anchor-sufficiency gate or verifier prompt restructure. Both are local fixes. Pick based on engineering cost and Path B's prior-attempt history. |
| H1 supported, H4 NOT supported (verifier stochastic but sufficiency rubric is fuzzy) | **Path C** — deterministic constrained verification (consensus). Stochasticity is the dominant problem. |
| H2 supported (fingerprint unstable) | **Path D variant** — Sully decomposition starting at the fingerprint stage. Span extraction needs to be more disciplined before downstream stages can stabilize. |
| H1 NOT supported (verifier is stable) AND H3 NOT supported (recall is unstable) | recall substrate work — vocabulary expansion, shape-scoped recall, embedding policy review. |
| H5 supported strongly (most variance is honest hypothesis diversity) | accept variance as a product property; surface hypothesis diversity in Step 6 rather than chasing single-canonical-anchor stability. |
| Mixed evidence with no clear primary lever | widen N to 10 reruns + add another case before architectural choice; current evidence isn't sufficient. |

The decision tree is pre-registered. The experiments should be run AND scored AND mapped to a branch BEFORE any code change is committed.

## §8 What not to do yet

To prevent the failure modes the last week revealed:

- **Do not start with candidate-cap tuning.** The audit found recall starvation on Marcus (13/60). Lowering the cap is dangerous; raising it might increase noise. Cap is a downstream lever, not a fix for stochasticity or sufficiency.
- **Do not start with full Sully decomposition.** It may be right eventually, but the evidence currently points to a more specific problem (verifier/sufficiency). Decomposition is a large commitment that should be earned with stage-isolation evidence (Experiments 1–3).
- **Do not start with DSPy / prompt optimization.** DSPy could become useful once the optimization target is clear (fingerprint? verifier? sufficiency? rejection criteria?). Until that's clear, DSPy would accelerate ambiguity. Run Experiments 1–4 first.
- **Do not run more single-run audits expecting trust to be stable.** PR #45 already established that single-run trust isn't stable. Future producer-side validation must use the two-layer reporting (repair-local vs whole-run) defined in `research/lane2-quote-repair-validation-amendment-2026-04-27.md`.
- **Do not change quote validation or Step 6 wording.** Both are working as intended. The current problem is upstream of both.
- **Do not pick a fix because it sounds elegant.** Pick the fix the experiments support.

## §9 Recommended first implementation track

This memo's stated hypothesis (not conclusion):

> First test verifier/sufficiency instability. The latest hard failure was direct verifier acceptance of noisy anchors with literal quotes. That suggests the immediate problem is sufficiency — the verifier accepts because the quote is topically adjacent, not because the quote actually carries the model's mechanism.

Pre-experiment ordering — **decision-priority order**, not strictly cheapest-first. Zero-cost upstream checks come before paid downstream tests so each test runs on cleaner inputs:

1. **Experiment 5 (consensus simulation) first** — zero cost, post-hoc on `rerun4`–`rerun7` (post-fix only). Tells us whether multi-run consensus is even a viable product shape before spending on new runs.
2. **Experiment 4 (sufficiency rubric audit) second** — session-level cost, no LLM calls. Tells us whether per-model sufficiency rules can be specified for the noisy-adjacent models we observed.
3. **Experiment 2 (recall determinism) third** — zero cost. Confirms H3 or surfaces unexpected recall variance. **Run before E1** so that if recall has hidden nondeterminism, we know it before designing E1's verifier-isolation test. If recall proves deterministic, E1's verifier read is cleaner; if not, E1's design must control for the recall variance.
4. **Experiment 1 (verifier stochasticity) fourth** — small LLM cost. Direct test of H1, the leading hypothesis.
5. **Experiment 3 (fingerprint variance) last** — small LLM cost. Tests H2; if E1 + E2 together don't fully explain churn, fingerprint is the next suspect.

After scoring all five, apply the §7 decision tree.

The implementation track that follows the experiments will be its own design memo, not this one. This memo's job is to design the investigation. The fix comes after the evidence.

## §10 What this memo commits to

- **Investigation, not architecture.** The next deliverable is experiment results, not code that changes the producer.
- **Pre-registered decision tree.** §7 is the binding rule for what evidence implies which architectural lever. Post-hoc rationalization is what got us here; pre-registration is what prevents it next time.
- **Two-layer reporting** (repair-local + whole-run) for any producer-side change tested against the audit corpus going forward. Per the methodology amendment.
- **Honest scope.** This memo does not claim Experiments 1–5 will resolve the producer-stability problem. It claims they will discriminate between candidate fixes. If they don't discriminate, that itself is information, and the memo's §7 mixed-evidence row says "widen N + add another case before architectural choice."

## §11 Status

- Memo: draft, awaiting review
- Experiments: not yet run
- Code changes: none
- Branch: `docs/lane2-producer-stability-design-2026-04-27`

The simple bottom line:

We have made the system more honest, safer, and more measurable. We have not yet made Lane 2 reliably good at choosing mental models. The next work is to stop treating Lane 2 as one black box and isolate where the instability enters. The hypothesis is verifier/sufficiency. The discipline is to test it before implementing it.

> In this system, premature fixes create beautiful evidence and then betray us. The measurement has to lead.
