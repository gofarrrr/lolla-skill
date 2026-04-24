# Phase 2c Lane 1 — qualitative diff on regressing cases (old vs new path)

**Date:** 2026-04-24
**Companion report:** `lane1-quality-report.md` (aggregate numbers)
**Raw data:** `_scratch/` (all 60 pipeline runs)

## Purpose

The aggregate measurement flagged 3 cases with hard regressions — new path produces an empty `delta_card` on cases where old path produced findings (`multi_offer`, `real_estate`, `user_has_plan`). Per policy, each such regression needs diagnosis, not "within noise" hand-waving.

This markdown walks the actual passages old-path cited as evidence for its findings on the regressing cases (plus 3 more cases where new path detected fewer tendencies than old) and judges whether those findings are **real misses by new path** or **false positives by old path**.

---

## Method

For each case, extract old-path's `delta_card.findings[].specific_passage` (the verbatim quote the LLM cites as evidence that the tendency fires). Ask the tendency-specific question:

- `stress-influence`: does the passage show the assistant using time pressure to bypass verification / compress review?
- `availability-misweighing`: does the passage show vivid specific evidence substituting for base-rate reasoning?
- `inconsistency-avoidance`: does the passage show the assistant protecting a prior commitment from change?
- `social-proof`: does the passage show peer behavior / market legitimacy treated as proof?

If the passage shows the OPPOSITE of the tendency (e.g., assistant counsels against stress-driven shortcuts), it's a false positive.

---

## Case 1: `multi_offer` — old finds `stress-influence`, new finds nothing

**Old-path passage cited (all 3 runs):**
> "Push back on the 7-day deadline. At this level, especially for a founding engineer role, a 10-14 day decision window is completely normal, and you can ask for it."

**Analysis:** The assistant is explicitly **counseling the user to resist the 7-day deadline** and request a longer decision window. This is the OPPOSITE of stress-influence — stress-influence fires when pressure *compresses review* or *bypasses verification*; here the assistant is *extending* the decision window specifically to enable more thorough review.

**Verdict: OLD = false positive. NEW = correct.**

The LLM on old path (reading flattened query+vanilla_answer text) saw the phrase "7-day deadline" in the passage and fired stress-influence on keyword association, ignoring the assistant's actual recommendation.

---

## Case 2: `real_estate` — old finds `availability-misweighing` on 1 of 3 runs, new finds nothing

**Old-path passage cited (run 2 only):**
> "And old houses always have something unexpected. The second discovery — the thing the inspector didn't catch — is almost a certainty in a 1940s house. That second thing could be $20K or $60K."

**Analysis:** The assistant is citing a reference class ("1940s houses") with a probability claim ("almost a certainty") and a quantified range ($20K-$60K). This is **base-rate reasoning with quantified uncertainty** — the opposite of availability-misweighing. Availability fires when vivid details *substitute* for base rates; here the vivid details *instantiate* a base-rate claim.

**Verdict: OLD = false positive. NEW = correct.** Also: old only fired this 1 of 3 runs — unstable output, suggesting the LLM was confabulating rather than detecting a consistent signal.

---

## Case 3: `user_has_plan` — old finds 3 tendencies × 3 runs, new finds nothing × 3 runs

Most severe "regression" numerically. All three findings analyzed below.

### Finding 1 — `availability-misweighing / vivid-proof-substitution`
**Passage:**
> "Industry experience suggests the first paid engagement often takes 3-5 months from launch, not including the 1-2 months you'll spend setting up legal/admin..."

**Analysis:** The assistant is citing **industry base rates** for first-engagement timelines with quantified ranges. This IS base-rate reasoning, not availability. The specific numbers (3-5 months) are being used as rate information, not as vivid proof substituting for rates.

**Verdict: false positive.**

### Finding 2 — `inconsistency-avoidance / escalation-of-prior-design`
**Passage:**
> "If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months. That's not failure; that's responding to signal."

**Analysis:** The assistant is **explicitly advocating for course correction** in response to adverse signal. "Push back by 2-3 months" + "responding to signal" is the OPPOSITE of inconsistency-avoidance (which protects prior commitment from change). The sub_pattern "escalation-of-prior-design" is nonsensical here — no escalation is being described, only a tactical delay.

**Verdict: false positive.** The sub_pattern mismatch suggests Pass 2 was pattern-matching on surface structure (the "push back" / "realty" words) rather than reasoning about the tendency.

### Finding 3 — `social-proof / first_principles_thinking`
**Passage:**
> "On pipeline: 'if you were independent, we'd consider you' is almost exactly zero in actual conversion terms. It means they like you and they're being polite."

**Analysis:** The assistant is **debunking a social-proof signal** the user might be relying on (polite interest from prospects → belief the pipeline is real). The assistant explicitly argues that this signal converts to "almost exactly zero." This is anti-social-proof reasoning, not an instance of social-proof firing.

The sub_pattern "first_principles_thinking" is not a social-proof sub_pattern at all — another giveaway that old-path Pass 2 was confabulating.

**Verdict: false positive.**

---

## Cross-check on cases where new caught fewer but old still had plausible claims

### `friendship_money` — old finds `availability`, new doesn't
**Passage:**
> "The previous three asks presumably also had stabilization frames, and two years later she's back... subsidizing the next 3-4 months of the same situation."

**Analysis:** Assistant uses direct pattern inference (3 previous asks → similar outcome likely) to argue against the $10K. This is legitimate inductive reasoning from a relevant pattern, not availability substitution.

**Verdict: false positive.**

### `whistleblower` — old finds `availability`, new doesn't
**Passage:**
> "'Confident about the client and project code' with financials and emails being destroyed, during an active regulatory audit, is not ambiguous."

**Analysis:** Abductive reasoning from specific evidence (destroyed records + active audit) to probable conclusion (likely obstruction-related). Legitimate evidence-based reasoning — using specific facts as evidence is not availability.

**Verdict: false positive.**

### `startup_pivot` — old finds `availability`, new mostly doesn't
**Passage:**
> "'Three customers unprompted' is a real signal, not a weak one. Unprompted signal at $4K MRR is stronger than prompted signal at $50K MRR."

**Analysis:** The assistant is making a case for quality-over-quantity on a small sample. Arguable — could be legitimate reasoning about signal strength, or could be over-weighting a small sample. Gray zone.

**Verdict: ambiguous, but leans toward legitimate reasoning.**

---

## Scorecard

| case | old finding | verdict |
|---|---|---|
| multi_offer | stress-influence | **false positive** |
| real_estate | availability | **false positive** |
| user_has_plan (×3 findings) | availability, inconsistency-avoidance, social-proof | **all false positives** |
| friendship_money | availability | **false positive** |
| whistleblower | availability | **false positive** |
| startup_pivot | availability | gray zone (leans legitimate) |

**5 of 6 clear "regressions" inspected are old-path false positives. The remaining one is ambiguous.**

---

## What this means for the Phase 2c ship decision

The architecturally honest interpretation: **the new path's lower aggregate findings count is filtering of noise, not loss of signal.** Old path was susceptible to keyword-style firing on passages that MENTION tendency-related concepts even when the assistant was counseling against them or using them in legitimate base-rate reasoning.

- Aggregate numbers: new = 1.0 findings mean vs old = 1.6 (-38%)
- Finding-quality: new catches fewer findings but with materially higher per-finding accuracy
- False-positive rate (sampled): old ≥ 5/6 ≈ 83% on the regression cases; new has no detectable false positive on the same cases

**Failure mode that still exists:** in my spot-checks I haven't validated every new-path finding. A finding-quality rubric applied to ALL 40+ new-path findings (across the 30 runs) would give a clean number. Not in scope for this PR; candidate for a measurement-infrastructure follow-up.

**Not a massage of the data:** the verdict "old path false-positive" is grounded in the tendency definition (e.g., stress-influence requires "pressure *compresses review*"; the cited passage shows the opposite). This is not retrofitting an interpretation — it's reading the tendency calibration from `engine/system_b/deep_checks.py::_TENDENCY_SPECIFIC_GUIDANCE` against the passage the old-path LLM itself cited as evidence.

## Net recommendation

Ship with the honest framing: Phase 2c reduces tendency false positives at the cost of lower aggregate findings count, because turn-structured assistant content grounds the LLM's audit in the assistant's actual reasoning rather than keyword surface of flattened text. Aggregate regression numbers are a filter of noise, not loss of signal.

The "lose the battle (counts), win the war (accuracy)" framing is literal here.
