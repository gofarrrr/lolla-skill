# E5 — Consensus simulation (post-fix only, N=4)

Date: 2026-04-27
Branch: `data/lane2-experiment-e5-consensus-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Sample: `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/user-launch-independent-fintech-rerun{4,5,6,7}.json`

## Sample discipline

Per the design memo §5 sample-contamination guard: this experiment uses **post-fix only** reruns. `rerun3` is excluded because it predates the both-halves ellipsis rule (PR #44, commit `42a60cf`) and contains the Reasoning Mode Router single-fragment trust breach the current system can no longer produce. Mixing pre- and post-fix samples would muddy the consensus result.

Default sample is N=4 (rerun4 + rerun5 + rerun6 + rerun7). No additional fresh rerun was run; k=1–4 thresholds are sufficient for the first decision read.

The historical N=5 (mixed pre/post-fix) is reported only as context in the parent characterization at `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/characterization.md`.

## Method

For each unique surfaced `model_id` across rerun4–rerun7, count the number of reruns it appears in. Apply consensus thresholds k = 1, 2, 3, 4. At each threshold, score:

- **Total anchors** that pass.
- **Trust composition**: acceptable (strict / with quote drift), borderline, noisy_adjacent, per the PR #43 §7.2 schema as applied in `characterization.md`.
- **Friction yield** at the cluster level: how many of the 6 anchor-worthy case-1 clusters (C1, C2, C3, C4, C6, C7; C5 excluded as `no_clean_primary`) have ≥1 acceptable anchor pass the threshold.
- **Lost-but-honest** anchors: acceptable at k=1, absent at k=2.

Trust classifications and cluster mappings are taken from the prior characterization (cross-checked here, not re-judged). All five clusters appear in source-first order C1–C7.

## Results

### Per-anchor consensus table

| `model_id` | Count (of 4) | Reruns |
|---|---:|---|
| `optimism-bias-and-planning-fallacy` | 3 | r5, r6, r7 |
| `checklists` | 2 | r4, r5 |
| `cognitive-dissonance` | 2 | r4, r6 |
| `wysiati` | 2 | r4, r7 |
| `commitment-bias` | 1 | r6 |
| `feedback-loops` | 1 | r7 |
| `information-asymmetry` | 1 | r7 |
| `optionality` | 1 | r5 |
| `premortem` | 1 | r6 |
| `probabilistic-thinking` | 1 | r6 |
| `representativeness-heuristic` | 1 | r7 |
| `step-back` | 1 | r4 |
| `time-tested-validation` | 1 | r4 |

13 unique anchors. 18 anchor-instances across 4 reruns.

### Trust composition per consensus threshold

| k | Total anchors | Acceptable (strict + drift) | Borderline | Noisy | Noisy rate |
|---:|---:|---|---:|---:|---:|
| 1 | 13 | 4 strict + 2 drift = 6 | 3 | 4 | 31% |
| 2 | 4 | 2 strict + 0 drift = 2 | 0 | 2 | **50%** |
| 3 | 1 | 1 strict + 0 drift = 1 | 0 | 0 | 0% |
| 4 | 0 | 0 | 0 | 0 | — |

The k=2 column is the headline. **Consensus at k=2 increases the noisy rate from 31% to 50%.** The noisy anchors (`cognitive-dissonance`, `checklists`) recur stably across runs while the rare-but-acceptable anchors (`step-back`, `optionality`, `premortem`, `representativeness-heuristic`) each surface only once.

### Friction yield per consensus threshold

Anchor-worthy denominator: 6 clusters (C1, C2, C3, C4, C6, C7). C5 excluded as `no_clean_primary`.

| k | Anchors qualifying | `friction_yield_strict` (clean cluster + no drift) | `friction_yield_any_honest` (allows drift) | Clusters yielding strict-acceptable |
|---:|---:|---|---|---|
| 1 | 13 | 2/6 = 33% | 4/6 = 67% | C1, C2 |
| 2 | 4 | 2/6 = 33% | 2/6 = 33% | C1, C2 |
| 3 | 1 | 1/6 = 17% | 1/6 = 17% | C2 |
| 4 | 0 | 0/6 = 0% | 0/6 = 0% | — |

`friction_yield_strict` is identical at k=1 and k=2 (C1 yields via `wysiati`; C2 yields via `optimism-bias-and-planning-fallacy`). What changes between k=1 and k=2 is the **drift-yield**: at k=1, C4 (Optionality) and C7 (Premortem) yield acceptable-with-drift anchors; at k=2 those drop because Optionality and Premortem each only surfaced once.

### Lost-but-honest at k=2

Anchors classified acceptable (strict or drift) at k=1 that DO NOT pass k=2:

- `step-back` — acceptable_secondary on C1 (r4 only)
- `optionality` — primary with quote drift on C4 (r5 only)
- `premortem` — primary with quote drift on C7 (r6 only)
- `representativeness-heuristic` — acceptable_secondary on C2 (r7 only)

4 acceptable anchors are pruned when going from k=1 to k=2. Three of those (Step Back, Optionality, Premortem) look like genuinely diverse defensible reads of the same source — different runs surfaced different valid readings. RH on C2 is similar (same cluster as Optimism Bias, different defensible secondary read).

## E5 decision rule application

Design memo §5 specified two decision rules for E5:

- "If consensus at k≥2 substantially improves trust without killing friction → multi-run product shape becomes a real architecture candidate."
- "If consensus at k≥2 kills friction yield to single digits → consensus is a dead-end."

Applied to the data:

- **k=2 does NOT improve trust.** Noisy rate goes from 31% to 50% (worse). The trust improvement promise is falsified — consensus does not reliably select for acceptable anchors here.
- **k=2 leaves friction_yield_strict unchanged at 33% but loses drift-yield** (drops from 67% any-honest at k=1 to 33% any-honest at k=2). 4 acceptable anchors are pruned. The "kills friction" promise partially holds at k=2.
- **k=3 improves trust to 0% noisy but collapses friction** (17%, single cluster yielding). The single-digit-friction outcome holds at k=3.
- **k=4 yields nothing.**

**Verdict: Consensus is not the first architecture lever.**

The k=2 path fails the "improves trust" condition. The k=3 path satisfies the "kills friction" dead-end condition. Neither threshold offers a viable consensus product shape on this case.

## Mapping to §7 decision tree

The §7 entry that most closely matches this evidence is:

> **H5 supported strongly (most variance is honest hypothesis diversity)** → accept variance as a product property; surface hypothesis diversity in Step 6 rather than chasing single-canonical-anchor stability.

But the data **only partially supports H5**. The rare acceptable anchors (Step Back, Optionality, Premortem, RH) ARE diverse defensible reads — H5 is consistent with their pattern. But the noisy anchors (Cognitive Dissonance, Checklists) recur stably across runs — that is NOT honest hypothesis diversity, that is the verifier being stably wrong on a specific class of broad/meta models. Two patterns coexist.

Refined reading:

- **H5 partially supported** for the rare-acceptable diversity (Step Back / Optionality / Premortem / RH).
- A **verifier-stably-wrong-on-broad/meta** pattern is also live — the noisy anchors recur predictably. This is closest to **H4** (verifier doesn't check mechanism sufficiency for broad/meta models).

The §7 entry implied by H5+H4 mixed evidence is:

- Path C (consensus) is **ruled out as the first lever** — k=2 worsens trust because noise is the recurring component, not the rare-acceptable diversity.
- Path A (anchor-sufficiency gate) and Path B (verifier prompt restructure) remain in play, both targeting the noisy-recurrence pattern.
- The next experiment to discriminate between A and B is **E4 (broad/meta anchor sufficiency rubric)** — design memo §9 next in order.

## Updated hypothesis state after E5

| Hypothesis | E5 evidence | Status |
|---|---|---|
| H1 — verifier stochasticity is main churn driver | not directly tested; consistent with rare-acceptable diversity | open; tested next by E1 |
| H2 — fingerprint variance is upstream driver | not directly tested | open; tested last by E3 |
| H3 — recall is deterministic | not directly tested | open; tested next by E2 |
| **H4 — broad/meta models over-accepted (sufficiency blind spot)** | **strongly supported** by recurrence of noisy anchors (CD, Checklists) at k=2 | **leading hypothesis after E5; tested next by E4** |
| H5 — some variance is honest hypothesis diversity | partially supported by rare-acceptable diversity (Step Back / Optionality / Premortem / RH) | partial; coexists with H4 |

The hypothesis ordering after E5: **H4 > H5 partial > H1/H2/H3 untested**.

## Implications for architecture

- **Consensus (Path C) is not the first lever.** k=2 makes trust worse because the wrong things recur. Even at k=3 where trust is clean, friction collapses. Multi-run consensus over-prunes good diversity and reinforces bad recurrence on this case.
- **Path A (sufficiency gate) and Path B (verifier prompt restructure) remain the live candidates.** Both directly address the noisy-recurrence pattern E5 surfaced.
- **E4 (sufficiency rubric audit) is the next experiment**. If a per-model sufficiency rubric can be specified for the recurring noisy anchors (Cognitive Dissonance, Checklists, plus the borderline Step Back / TTV cases for stress-testing the rubric), Path A becomes concretely buildable. If the rubric is fuzzy or requires verifier-prompt changes to enforce, Path B becomes the natural lever.
- **The hypothesis-diversity finding (H5 partial) is product-relevant separately**: the rare-acceptable anchors that consensus would prune (Step Back / Optionality / Premortem / RH) are exactly the kind of curated friction the product is supposed to deliver. Architectures that suppress them in pursuit of "stability" would degrade the product. Any future producer-side change must preserve diversity-room for these single-run defensible reads, not just stabilize the loud noisy ones.

## Status

- E5: **complete**. Consensus ruled out as first architecture lever.
- E4 (sufficiency rubric audit): **next**, per design memo §9 ordering.
- E2 (recall determinism): zero-cost, runs before E1 per the patched ordering.
- E1 (verifier stochasticity): paid LLM test, runs after E2.
- E3 (fingerprint variance): last.
- §7 decision tree: not yet applied. Path C eliminated; A and B remain live; E4 will discriminate between them.

## What this experiment did NOT do

- Did not run new pipeline calls. Pure post-hoc analysis of existing JSONs.
- Did not test E5 against another case (only `user-launch-independent-fintech`). If a future case shows the inverse pattern (noisy anchors don't recur, rare-acceptable anchors do), consensus might re-enter as a candidate. Out of scope here.
- Did not pick architecture. The §7 decision tree is binding, but it requires E4 + (selectively) E1/E2/E3 outcomes to fully resolve.

The measurement leads. E5 says: not consensus. Move to E4.
