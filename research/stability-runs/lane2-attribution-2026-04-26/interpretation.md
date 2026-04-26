# Lane 2 attribution — campaign interpretation

Date: 2026-04-26
Status: post-campaign reading
Companion: `synthesis.md` (this directory) · `research/lane2-attribution-design-2026-04-26.md` (the pre-registration / contract)

> The memo is the contract; this note is the post-campaign reading.
> Do NOT edit the memo to reflect what we learned — that would dissolve the
> pre-registration value. New decisions live in
> `research/lane2-followup-tracking-2026-04-26.md`.

## Status

**21 of 24 planned pipeline runs completed.** 3 paired cases at N=3 each both modes (18 runs) plus mother-deciding-address-year ON only (3 runs).

| Case | ON | OFF | Paired |
|---|---|---|---|
| `marcus-equity` | ✅ N=3 | ✅ N=3 | yes |
| `mid-level-consultant-decides` | ✅ N=3 | ✅ N=3 | yes |
| `third-year-phd-student` | ✅ N=3 | ✅ N=3 | yes |
| `mother-deciding-address-year` | ✅ N=3 | ❌ blocked | no |

**Why mother-deciding-OFF is blocked.** Three independent attempts hit the same pre-existing engine invariant in `engine/system_b/companion.py:126` — "CompanionCard cannot contain more than 3 expansions per detected model." Diagnosis (after the campaign, not from it): the verifier sometimes accepts the same `model_id` more than once with slightly different evidence quotes; the pipeline builds two `DetectedModel` objects from one `model_id`, then `expand_detected_model` is called twice, producing >3 expansions per `source_model_id` at card-build time. This is an upstream duplicate-accepts bug, not a design constraint to lift. The fix lives in PR-A; see the tracking doc.

## Headline finding

**The verifier is the dominant observed amplifier.** Recall delivers a moderately stable candidate universe (Candidates Jaccard 0.68–0.76 across all cases and modes); the verifier collapses that to dramatically lower agreement (Accepted-pre Jaccard 0.06–0.39). A 30–60 point stability drop at the verify stage given a roughly identical 60-candidate input.

## The precision improvement that matters

Set Jaccard on Accepted-pre treats "candidate not present in run B" the same as "candidate present in B but rejected." Those are different failure modes. The candidate-conditional metric isolates the verifier's per-judgment instability:

```
shared_available_acceptance_agreement =
  | accepted_in_both_runs |
  / | (accepted_in_run_a ∪ accepted_in_run_b) ∩ candidate_present_in_both_runs |
```

Computed across the committed stability files (mean across the 3 pairwise comparisons within each case-mode group):

| Case-mode | Shared-available accept agreement |
|---|---|
| `marcus-equity-lane2-off` | 0.13 |
| `marcus-equity-lane2-on` | 0.33 |
| `mid-level-consultant-decides-lane2-off` | 0.17 |
| `mid-level-consultant-decides-lane2-on` | 0.25 |
| `mother-deciding-address-year-lane2-on` | 0.06 |
| `third-year-phd-student-lane2-off` | 0.58 |
| `third-year-phd-student-lane2-on` | 0.47 |
| **Overall mean** | **0.28** |

**Even controlling for candidate availability, the verifier flips the same model in different directions across runs.** This is the operational definition of "verifier overload": given the same candidate, the same assistant text, and the same fingerprint, the verifier sometimes accepts and sometimes rejects.

Direct evidence (from spot-checking `mother-deciding-address-year-lane2-on` per-run sets): the count of accepted models that were available in both candidate sets was 4/4, 3/3, 6/6 across the three pairwise comparisons — every accepted model was available in both runs. Yet accepted Jaccard stayed at 0.00, 0.00, 0.17. Pure verifier-side judgment instability.

## What we can rule out

- **Embeddings are not the recall variance source.** Paired ON-vs-OFF Candidates delta across the three paired cases: −0.02 (marcus), −0.04 (consultant), −0.01 (phd). Essentially zero. The embedding-recall path is not the noise we worried it might be when we added the cap-saturation guard before launching (see commit `275d57d`).
- **Top-5 truncation is not the amplifier.** `Capped` Jaccard is mostly 1.00 because Accepted-pre rarely exceeds the 5-model surfacing budget — the cap structurally doesn't fire, so it can't be the amplifier. The one exception (`third-year-phd-student-off` shows 0.00 Capped) is the result of the verifier producing different counts across runs, not the cap itself amplifying anything.
- **Fingerprint text instability is not a real signal here.** FP moves Jaccard 0.00–0.20 looks alarming but is paraphrase artifact: per-run move text inspection shows the same reasoning move described three different ways across runs (e.g. for marcus: "differentiate marcus's unique contributions" / "differentiating marcus from other employees" / "differentiate marcus like tom or the head of design"). The reading-guide caveat in `synthesis.md` predicted this. Right metric for fingerprint stability is embedding cosine, not text Jaccard. Out of scope for the immediate follow-up.

## Two decision-tree calls that need interpretation, not literal application

The pre-registered decision tree in the design memo is band-based on absolute thresholds. Two of its calls fired but the strict-band reading and the spirit reading diverge:

1. **`fix_fingerprint_or_query_construction`** (fired on `marcus-off`, `consultant-off`): false positive. Driven by FP moves Jaccard collapsing to ~0.00–0.05, but that's paraphrase drift, not semantic instability. The reading-guide caveat predicted this exactly.
2. **`inconclusive_widen_n_or_cases`** (fired on the four ON-mode rows): triggers because Candidates sits in 0.70–0.85 (above "fix recall first" but below "verifier is the only suspect"), while Accepted-pre crashes below 0.50. Strict bands say inconclusive; the band intent — "where does the variance enter?" — clearly says **the verifier is the amplifier**, even when recall isn't perfectly stable.

The honest read: the decision tree's absolute thresholds are too strict. A drop of ≥30 Jaccard points between Candidates and Accepted-pre is a stronger verifier-amplifier signal than any specific absolute threshold. We don't edit the memo (the contract) — but the next campaign should use the candidate-conditional metric above, which is sharper than band-Jaccard for this question.

## Cost

Boundary-only token total across 21 successful runs: ~2.4M tokens. At grok-4.1-fast pricing roughly $1.50–2.00. Within the predicted $3 envelope. Embedding/expansion calls are not in this number; see synthesis.md cost-table caveat.

## What the data implies for the next move

The dominant variance source is the verifier asking one LLM call to judge up to 60 candidates (each with executed/violated/neither + evidence quote + presence explanation) in a single response. This is the Sully-shaped "one prompt, too many obligations" pattern in our codebase. The remediation that follows from the data — and that the memo's allowed-fixes list explicitly authorizes when verification is the unstable stage — is **partition the verifier obligation into narrower per-bucket calls, preserving the full information per call.**

Two sequential follow-up PRs are scoped in `research/lane2-followup-tracking-2026-04-26.md`:

- **PR-A** (small, gating): dedupe verifier accepted entries by `model_id` (fixes the mother-OFF blocker) and add the candidate-conditional verifier-stability metric as first-class measurement.
- **PR-B** (architecture, after PR-A): reasoning-type partitioned verifier with deterministic fan-in.

Pre-registered acceptance gates for PR-B are in the tracking doc.
