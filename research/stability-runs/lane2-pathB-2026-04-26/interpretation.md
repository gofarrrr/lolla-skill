# Path B — interpretation

Date: 2026-04-26
Status: post-campaign reading; gates failed; **architecture iteration on Lane 2 stops here per pre-registration**
Companions:
- `research/lane2-followup-tracking-2026-04-26.md` — original PR-A/PR-B scopes
- `research/stability-runs/lane2-prb-v3-2026-04-26/interpretation.md` — v3 reading + the design conversation that produced Path B
- `research/stability-runs/lane2-pathB-2026-04-26/synthesis.md` — campaign data

## Headline

**Path B failed gates and uncovered a structural architectural problem the calibrator can't solve: the calibrator itself becomes a new probabilistic stage that adds variance on top of verifier variance.** Per pre-registration: stop architecture iteration on Lane 2. Pivot to Path D (Step 6 robustness).

## Pre-registered B gates vs. observed

| Gate | Target | Observed | Pass? |
|---|---|---|---|
| Calibrated anchor Jaccard mean | ≥ 0.50 | **0.40** | ❌ |
| Calibrated anchor Jaccard worst | ≥ 0.30 | **0.08** (marcus) | ❌ (off by 0.22) |
| Calibrated anchor count mean | 2–5 | 2.9 | ✅ |
| Calibrated anchor count max | ≤ 5 | 5.0 | ✅ |
| No all-zero calibrated unless raw=0 | required | **violated** (mother 0/0/0 with 6–9 strong accepts) | ❌ |
| Verifier + calibrator token share | ≤ 30% | mean 24%, worst **34.1%** (mother) | ❌ on worst case |
| Calibration input mean | ≤ 10 | 6.0 | ✅ |

## Two distinct failure modes uncovered

### Failure mode 1: Calibrator empty-completion fragility

**4 of 7 calibrator LLM calls returned 0 completion tokens** (status="ok", just no output):
- mother-deciding all 3 runs
- marcus-equity 1 run

The other 3 calibrator calls (consultant 1, phd 2) succeeded and produced sensible output. So the calibrator does the right thing **when it produces output**, but its operational reliability is roughly 43% on this case mix. Mother-deciding's perfect 1.00 calibrated_J is metric-corruption: empty/empty Jaccard = 1.0 vacuously, not stability.

I did not deliberately re-tune the calibrator prompt or add retry logic — per pre-registration this was a one-shot architecture experiment. But the failure mode itself is a finding: a single-LLM-call calibration stage on top of partitioned verifiers is not robust to provider/model glitches in this case mix.

### Failure mode 2: Calibrator adds new variance instead of stabilizing

The deeper architectural finding. PhD-on under v3 had anchor Jaccard 0.51. Under Path B the same case landed at calibrated Jaccard **0.16**. Per-case progression:

| Case | v3 anchors | B calibrated | Δ |
|---|---|---|---|
| marcus-equity | 0.13 | **0.08** | −0.05 |
| mid-level-consultant | 0.18 | 0.37 | +0.19 |
| mother-deciding | 0.26 | (vacuous 1.00 from empties) | metric-corrupt |
| third-year-phd | **0.51** | **0.16** | **−0.35** |

Path B improved one case (consultant), regressed two (marcus, phd), and corrupted the metric on mother. PhD's regression is the load-bearing observation: when v3 produced 5+ stable strong accepts, the calibrator's top-5 selection from those 5+ strong candidates introduced **new** run-to-run variance. The ranking step itself is probabilistic. We added a probabilistic stage where there had been a deterministic top-5 selector (`accepted[:5]`).

This contradicts the Path B hypothesis. The hypothesis was: calibrator stabilizes the product despite per-shard verifier noise. The reality: calibrator IS another noise source. The "competitive calibration" job the monolithic verifier did silently was not actually stabilizable as a separate LLM call — it interacted with the per-shard verifier output to produce more variance, not less.

## What this tells us about Lane 2

The progression v1 → v2 → v3 → B has now mapped the architecture-side fixes:

| Architecture | Token cost | Accept count | Verifier judgment | Final anchor stability |
|---|---|---|---|---|
| Monolithic | low | 3–5 | unstable (~0.21) | unstable |
| v1 (reasoning-type partition) | high | 14.6 | improved per-bucket | over-acceptance |
| v2 (+ strict rubric) | high | 10.8 | improved | per-bucket floor remains |
| v3 (rank-stratified, 3 shards) | low ✓ | 6.5 ✓ | partial (0.36/0.44) | mixed (PhD strong) |
| B (+ global calibrator) | low | 2.9 ✓ | unchanged | **regressed; calibrator adds noise** |

**The conclusion the data supports:** Lane 2's per-candidate verifier judgment has a probabilistic floor that no architecture-side change has cleared. v3 found the architectural sweet spot (cost passes, count passes); B's attempt to stabilize the final anchor selection through additional LLM calibration added noise rather than removed it. That's the empirical answer to the granularity-vs-floor question.

## What I'd recommend now

**Per pre-registration: stop architecture iteration on Lane 2. Pivot to Path D (Step 6 robustness).**

Path D scope (deferred from this branch):
- Lane 2 stays at v3 architecture (no calibrator). v3 passes structural gates (cost, count, recall stability); the per-judgment Jaccard miss is acknowledged as the irreducible probabilistic floor.
- Step 6 (in `SKILL.md`) is redesigned to be **robust to anchor variance** rather than assuming Lane 2 produces a deterministic anchor set:
  - Display anchors with cross-run frequency when multi-run data exists (e.g. "Endowment Effect appeared in 3/3 runs; Loss Aversion in 1/3").
  - The anchor-naming invariant from `SKILL.md:336` could route differently: stable-core anchors (≥2/3 runs) get §1/§3 weight; run-specific anchors get §2 (set aside, with reason "appeared in 1/3 runs").
  - Or: render Lane 2 output as a probability-of-relevance distribution rather than a top-5 list.

Path D is a real surface area to redesign. It needs its own scoping conversation. But the architecture-side answer is in: **v3 is the substrate, anchor variance is real, the consumer must adapt.**

## What we're keeping vs. dropping from this branch

The current branch has v1/v2/v3/B all stacked. For the next merge decision:

**Keeping (substrate):**
- Recall changes: per-candidate `reasoning_type` tag, `final_rank` audit metadata, `recall_source` distribution (PR #39 / PR-A foundation).
- Verifier dedupe by model_id (PR-A — fixes mother-deciding-OFF blocker, prevents CompanionCard expansion invariant trips).
- Strict shared rubric + weak_matches (v2 — actively sorts candidates with `42 weak_matches per run` evidence).
- Rank-stratified 3-shard verifier (v3 — clears cost gate at 22.4%, accept count gate at 6.5).
- All audit fields: companion_candidates, companion_verification_accepted_before_cap, companion_verification_capped_models, companion_verification_duplicate_accepts, companion_verification_weak_matches, companion_verification_shard_breakdown.

**Dropping (the calibrator):**
- The Path B global anchor calibrator was tested and rejected per pre-registered gates. Removing the calibrator call from `_run_companion` and the calibrated audit fields would land the branch as v3-only.

**Open question:** does the user want to merge the branch as v3-only (drop calibrator), or keep the calibrator code + data committed as a documented failed experiment but not enabled?

## Branch state

- v1 → v2 → v3 → B all committed.
- 377 tests passing.
- All 4 campaigns + interpretations committed.
- Branch pushed but **NOT a PR**. Per pre-registered "if B fails, do not merge."

Decision belongs to you:
1. **Land v3-only** (revert the calibrator, leave B as a documented failed experiment in research notes), open the PR, then start Path D as a separate branch.
2. **Keep B in code but disabled** (gate it behind a feature flag that defaults off), so the experiment is recoverable but doesn't ship.
3. **Pivot directly to Path D** without merging this branch first — but that means v3's architectural improvements stay unmerged, which is a real loss.

I lean (1). The branch has done its job: it found the architecture sweet spot (v3) and demonstrated that Lane 2 stability has a probabilistic floor that calibration can't fix. We should ship v3 and move to product-side work for the rest.
