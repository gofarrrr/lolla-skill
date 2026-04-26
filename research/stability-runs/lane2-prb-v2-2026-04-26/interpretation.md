# PR-B campaigns — interpretation

Date: 2026-04-26
Status: post-campaign reading, gate-evaluation, decision-pending
Companions:
- `research/lane2-followup-tracking-2026-04-26.md` — pre-registered scopes + gates
- `research/stability-runs/lane2-attribution-2026-04-26/synthesis.md` — PR #39 baseline (monolithic verifier)
- `research/stability-runs/lane2-prb-2026-04-26/synthesis.md` — PR-B v1 (partition only)
- `research/stability-runs/lane2-prb-v2-2026-04-26/synthesis.md` — PR-B v2 (partition + strict rubric)

> The pre-registered gates do not pass on either v1 or v2. This note records
> what the data tells us, what the gates were designed to catch, and what
> options the data leaves open. Decision is yours.

## Three-way comparison

| Metric | Baseline (monolithic) | PR-B v1 (partition) | PR-B v2 (+ rubric) | Gate |
|---|---|---|---|---|
| Accepted-pre Jaccard mean | 0.21 | 0.39 | 0.31 | ≥ 0.50 |
| Accepted-pre Jaccard worst | 0.06 | 0.30 | 0.21 | ≥ 0.30 |
| Cand-cond. mean | 0.28 | 0.44 | 0.35 | ≥ 0.60 |
| Cand-cond. worst | 0.06 | 0.32 | 0.23 | ≥ 0.35 |
| Candidates Jaccard mean | 0.72 | 0.75 | 0.80 | ±0.05 |
| **Accepted count mean** | **3–5** | **14.6** | **10.8** | **2–7** |
| Accepted count worst | ~5 | 17.7 | 18.0 | 2–7 |
| Anchors mean | ~0.20 | 0.30 | 0.28 | (informative) |
| Verifier token share | 9–16% | 38% | 41% | ≤ 30% |
| Weak matches mean | n/a | n/a | **42 per run** | (diagnostic) |

## What the v1 → v2 delta tells us

The strict rubric did its job *directionally*. weak_matches populated heavily (~42 per run), confirming the rubric IS sorting plausible-but-not-load-bearing candidates away from accepted. Accepted count dropped from 14.6 → 10.8. PhD's anchor stability jumped from 0.16 → 0.45 (the case where the verifier was most overloaded got the most help).

But it didn't clear the gates. **Reading the per-run accepted lists exposes a structural reason.**

## The structural finding

PhD-on run-0 accepted 17 distinct models, drawn from many reasoning-type buckets:

```
aleatory-epistemic-uncertainty-recognition (probabilistic)
anchoring                                   (cognitive bias)
base-rates                                  (probabilistic)
falsifiability                              (epistemic)
feedback-loops                              (systems)
game-theory-payoffs                         (game theory)
inversion                                   (counterfactual)
lean-startup-methodology                    (process)
meta-cognitive-reflection                   (metacognitive)
optimism-bias-and-planning-fallacy          (cognitive bias)
optionality                                 (decision)
premortem                                   (counterfactual)
problem-framing-and-reframing               (metacognitive)
regret-theory                               (counterfactual)
risk-assessment                             (probabilistic)
second-order-thinking                       (systems)
statistical-discipline                      (probabilistic)
```

Each bucket independently accepts ~2–3 strong-claimed candidates. With reasoning_types covering 4–9 buckets per case, the accepted count floor is 4–18 — *structurally*. The strict rubric narrows within each bucket but cannot reduce the bucket count.

This is the failure mode pre-registered in the tracking doc as: "If the monolithic verifier accepts 0–7 and the partitioned verifier accepts 25, we did not improve stability; we removed competition and created over-acceptance." We're at 10.8, not 25, but the same shape: per-bucket strong-claimed acceptance × N buckets > global product budget.

## What the rubric did NOT fix

The rubric operates at the per-bucket prompt+parser layer. It cannot:
1. See acceptances from other buckets in flight (parallel, no shared state).
2. Apply a global ranking step (the deterministic (final_rank, model_id) sort doesn't filter — it orders).
3. Reject a model at fan-in for "another bucket already has a stronger one."

The v1 → v2 improvement (14.6 → 10.8 accepts) shows the rubric CAN reduce per-bucket acceptance, but each bucket's floor is structurally non-zero on rich cases.

## Three honest paths

**A. Per-bucket cap at fan-in (1 or 2 per bucket).**
Adds one deterministic step in fan-in: keep at most N strong accepts per bucket (sorted by final_rank), the rest go to weak_matches with reason "per_bucket_cap". Forces global accept count toward `n_buckets × per_bucket_cap`. With 9 reasoning_types × cap=1 → ~4–9 accepted (close to the 2–7 gate). With cap=2 → 8–18 (still over).

Pros: deterministic, doesn't add an LLM call, doesn't introduce a new substrate.
Cons: arbitrary cap value; risks suppressing legitimate stronger candidate from a "weaker bucket" if that bucket's #2 is more load-bearing than another bucket's #1.

**B. Global cross-bucket reranker (one LLM call after fan-in).**
After per-bucket verifiers produce strong accepts, send the union (~10–18 items) to a single LLM call asking "rank these by structural load-bearing strength; we will surface only the top 5". This restores the competitive calibration job the monolithic verifier was doing.

Pros: principled — directly restores the missing job. Single call, narrow obligation (just rank).
Cons: another LLM call (cost). Reranker stability becomes a new variable to measure.

**C. Accept that 2–7 may be incompatible with deterministic partition; revise the gate.**
If the architecture is right, perhaps the gate's accept-count floor was wrong for partitioned shapes. The pre-registered rule said don't loosen gates; this would be loosening.

Pros: honest about the architectural floor.
Cons: violates the pre-registered discipline. The user explicitly warned against this.

**Not a path: revert.** v2 is a strict superset of v1's information (weak_matches is purely additive observability) and v1 substantially helped consultant + mother. Reverting throws away real progress.

## My read

Path A (per-bucket cap=1) is the smallest, most testable next step. It's deterministic, it directly targets the structural floor, and it will produce a clean signal: either accepted count drops to 2–7 and gates pass, or it doesn't and we know the issue is something deeper than bucket count. The risk (suppressing a stronger #2) is mitigated by the (final_rank, model_id) sort already keeping the highest-recall-rank within each bucket.

Path B is principled but adds latency, cost, and another stability variable. I'd hold it as the fallback if Path A doesn't clear gates.

Path C I'd not take without you explicitly authorizing it. The gate discipline kept us honest twice (it caught v1's over-acceptance, it caught v2's residual structural floor). Loosening it now would unwind that.

## What's already committed on this branch

- `ba731e1` — engine + harness for v1 (partition + parallel + dedupe + (final_rank, model_id) sort + audit threading) AND v2 (strict shared rubric + weak_matches + parser-level enforcement).
- This file + the per-case stability outputs for both campaigns.
- Tests: 372 passed, 9 new (partition + dedupe + ordering + 4 strict-rubric regressions).

The branch is pushed but **NOT yet a PR**. Per the pre-registered "if any gate fails, do not merge, decide whether to iterate or revert" — decision belongs to you.
