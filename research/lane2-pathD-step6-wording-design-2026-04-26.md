# Path D D1 — Step 6 wording design

Date: 2026-04-26
Status: design doc, pre-`SKILL.md` edit. Review before implementation.
Companions:
- `research/lane2-pathD-step6-robustness-design-2026-04-26.md` — Path D scope + pre-registered gates
- `research/stability-runs/lane2-pathD-proxy-validation-2026-04-26/interpretation.md` — D0 result that routes us here
- `SKILL.md` Step 6 (the surface this doc proposes to revise)

## 1. Decision from D0

No single deterministic substrate fact on `main` predicts cross-run anchor stability above the AUROC ≥ 0.70 threshold. Both directional proxies (`final_rank`, `accepted_before_cap_position`) failed the Marcus stress test, swinging from AUROC 0.62 to 0.08 across cases — they are case-coupled, not conversation-independent. Per the pre-registered Path D scope: **D1 is wording-only. No tiered anchor metadata. No programmatic stability scores in `companion_cheat_sheet`.**

But "no metadata tier" ≠ "Step 6 should ignore evidence quality." Step 6 is an LLM consumer. It can read the actual evidence quote, the model's specificity, and the surrounding answer in a way the crude single-number proxy audit cannot. That reading is exactly where prompt-side guidance belongs.

## 2. New Step 6 contract

The product contract that emerges from the architecture-side investigation (v1/v2/v3/B) and the proxy-side investigation (D0) converging:

> **Lane 2 anchors are evidence-bearing hypotheses about the assistant answer's structure. They are not a canonical diagnosis. Step 6 may use them to apply structural pressure on the answer, but must not imply certainty that the named model is the one true explanation.**

Three operational consequences:

1. **The anchor-naming invariant stays.** Every anchor in `companion_cheat_sheet.anchors[]` must still be addressed in Step 6. We do not let weak anchors silently disappear.
2. **"Addressed" is no longer uniform.** What changes is *how* each anchor is addressed. The invariant becomes evidence-proportional rather than evidence-blind.
3. **No probability language.** "70% likely" or "high confidence" claims require multi-run sampling we don't have at production latency. Don't fake what we can't measure.

## 3. Anchor treatment vocabulary

Three rhetorical treatments. Step 6 picks one per anchor based on Claude's reading of the evidence quote + model + answer. This is qualitative judgment, not a programmatic tier.

### Primary pressure

The anchor directly explains a load-bearing reasoning move in the answer. Evidence is direct, specific, and central. The model named is specific enough to be the right structural read (not a broad overlay that could apply anywhere).

> *"The answer appears to rely on **opportunity cost** reasoning when it frames staying as the cost of giving up another path. The strongest reversal trigger is whether the alternative path is actually realizable on the user's stated timeline."*

Use stronger framing here. "Appears to rely on", "the structural pressure point is", "the answer instantiates" are appropriate.

### Secondary lens

The anchor is plausible and useful, but the evidence is weaker, broader, or adjacent. Could explain part of the structure but not the load-bearing move. Or several anchors compete for the same passage and this is one of them.

> *"A related lens is **loss aversion**: the answer may be overweighting what is already owned, though the evidence is less direct than for opportunity cost."*

Use softer framing. "A related lens", "a possible second read", "an adjacent risk", "may be overweighting", "could also apply" are appropriate.

### Set-aside caveat

The anchor appeared in Lane 2 but Step 6 reads the evidence as not load-bearing. Mention briefly to satisfy the invariant; do not rely on it heavily; explain why it's set aside.

> *"**Endowment effect** was surfaced as a possible companion lens, but the stronger issue here is the trade-off structure rather than ownership attachment, so I'm not centering it."*

Use acknowledging framing. "Was surfaced as a possible lens but...", "is not the load-bearing read here", "set aside in favor of...". This is the move that lets Step 6 honor the invariant without inflating a weak anchor.

## 4. Wording rules

These are reading instructions for Claude in Step 6, not programmatic gates. Phrased qualitatively to prevent smuggling D0-failed proxies back as hard rules.

### Use stronger (primary pressure) language only when ALL of these hold

- The evidence quote shows the assistant **using the model's mechanism**, not just adjacent vocabulary.
- The model is **specific enough** to explain *this passage* without applying to most answers.
- The anchor is **central** to the answer's reasoning, not a tangential framing.
- No competing anchor with stronger evidence claims the same passage.

### Use softer (secondary lens) language when

- The evidence quote is **short, generic, or compatible** rather than diagnostic.
- The model is **broad-overlay** or could plausibly explain many answers (systems-thinking, second-order-thinking, multi-criteria-decision-analysis are typical examples).
- Multiple anchors **compete for the same passage** and this anchor is not the strongest candidate.
- The model is **useful as a lens but not necessary** to explain the answer.

### Use set-aside framing when

- Step 6's reading of the actual answer says **a different anchor better explains the same passage**.
- The evidence quote was a **vocabulary mention** without the mechanism running.
- The anchor is plausible in general but **not load-bearing for this specific case**.

### What this is NOT

- Not "if quote_length < N, soften." That sneaks D0-failed proxies back in as hard rules.
- Not a programmatic confidence score on `companion_cheat_sheet.anchors[]`.
- Not a metadata tier the engine assigns.

It's three patterns Claude chooses among based on reading the actual content.

## 5. What not to do

- **No probability percentages.** "70% likely", "high confidence", "moderate confidence" require multi-run data we don't have.
- **No formal stability tier metadata** in `companion_cheat_sheet.anchors[]`. The cheat-sheet shape stays unchanged.
- **No "the answer is using X" for weak anchors.** That's overclaim. Use "appears to lean on", "a possible lens", or set-aside framing.
- **No hiding anchors.** The anchor-naming invariant requires every anchor to be addressed in some form. Set-aside framing satisfies the invariant; silent omission does not.
- **No "every reading is plausible" mush.** This is the failure mode the not-mushy gate catches. Step 6 still has to commit to a primary read where evidence supports one.

## 6. Acceptance gates

Sharpened from the Path D scoping doc:

### Anchor overclaim rate ≤ 10%

**Operational definition:** Step 6 *states or strongly implies* that an anchor is *definitely* the central mechanism when the evidence quote is generic, adjacent, broad, or competing with a better-supported anchor. Counted as one overclaim per anchor per audited Step 6 output.

### Primary-anchor preservation ≥ 75%

**Operational definition:** When an anchor has direct, specific evidence (a quote that shows the mechanism running) and appears central to the answer's reasoning, Step 6 still uses or names it as primary pressure. Counted as fraction of "primary-eligible" anchors that get primary treatment.

### Secondary framing ≥ 90%

**Operational definition:** Weak / broad / adjacent anchors are framed as possible lenses, adjacent risks, or set-aside caveats rather than canonical diagnoses. Counted as fraction of "non-primary-eligible" anchors that get secondary or set-aside treatment.

### Not-mushy review (qualitative)

**Operational definition:** The revised wording still helps the user see structural pressure. It does not collapse into "many things might apply." Specifically, every audited Step 6 output should:
- Identify at least one primary or strongly-named anchor where evidence supports it.
- Make a definite read on the load-bearing structural problem (not "could be X or Y or Z").
- Be at least as useful as the pre-revision Step 6 for the same case (human-judged).

If three or more audited cases collapse into hedging or fail to commit to a primary read where one is supported by evidence, the wording rules need tightening before merge.

## 7. Audit corpus

### Required (the 4 cases that exposed the problem)

Cases must be included so we don't risk overfitting the wording to Marcus alone:
- `marcus-equity` (3+ archived runs)
- `mid-level-consultant-decides`
- `third-year-phd-student`
- `mother-deciding-address-year`

### Wider (archived runs with `revised_answer` + `companion_cheat_sheet.anchors`)

From the PR #39 archive sanity check: 11 archived full skill runs qualified. All 11 should be in the audit corpus. Their existing Step 6 outputs (`revised_answer`) are the baseline; the proposed wording rules are evaluated against what they would produce instead.

### Audit method

Per audited run, fill in this structured review (one row per `companion_cheat_sheet.anchors[]` entry).

The row template separates BASELINE state (what the current `revised_answer` already does) from PROPOSED state (what the wording sketch under these rules would produce). Acceptance gates measure the proposed state. Baseline is reported as context to confirm the rules actually move the needle.

| Field | What to record |
|---|---|
| `case_id` | from archive |
| `run_id` | from archive |
| `model_id` | the anchor |
| `display_name` | from `companion_cheat_sheet.anchors[].display_name` (used by anchor-naming invariant check below) |
| `evidence_quote` | from `companion_cheat_sheet.anchors[].evidence_quote` |
| `current_revised_answer_quote` | the verbatim sentence in `revised_answer` that addresses this anchor. **No paraphrase.** Two valid record types: (1) a verbatim sentence quoted from `revised_answer`; (2) the literal sentinel `MISSING: no sentence names or addresses <display_name>` when the anchor was hidden — i.e., `current_classification=hidden`. The sentinel keeps hidden-anchor rows auditable so silent omission counts toward the baseline. "Not auditable" is reserved for malformed archive data only: missing `revised_answer`, missing anchor fields, or genuinely ambiguous extraction failures. |
| `current_classification` | overclaim / appropriate-primary / appropriate-secondary / appropriate-set-aside / hidden |
| `primary_eligible` | yes / no — does the anchor have direct, specific evidence + central role in the answer's reasoning? Decided BEFORE choosing `proposed_treatment`. |
| `proposed_treatment` | primary pressure / secondary lens / set aside with a reason |
| `proposed_wording_sketch` | one-sentence rewrite per the rules above. Must include the anchor's `display_name` verbatim (see anchor-naming invariant audit failure below). |
| `proposed_classification` | overclaim / appropriate-primary / appropriate-secondary / appropriate-set-aside — **judges the sketch as written, not the intention**. Answers: "if this one-sentence rewrite shipped, would it read as overclaim?" Prevents rows where `proposed_treatment=secondary lens` while the actual wording still overclaims. |
| `uncertain` | yes / no — flag for human review |
| `reviewer_notes` | edge cases, judgment calls |

#### Anchor-naming invariant audit failure

If `proposed_wording_sketch` omits the anchor's `display_name` verbatim, the row **fails the anchor-naming invariant** unless the anchor is genuinely absent from the run data (e.g., empty `companion_cheat_sheet.anchors[]`). Set-aside framing must still name the anchor; otherwise it becomes a vague unnamed caveat that hides the signal — exactly the failure mode the invariant exists to prevent.

Audit-failure rows are reported separately from the gate metrics and require row-level remediation (rewrite the sketch to include the `display_name`) before aggregate metrics are computed.

#### Aggregate metrics (per-run AND pooled across all runs)

Report metrics at two levels: per-run (so single-case failures are visible) and pooled (so we evaluate against gates on the full audit corpus). Acceptance gates apply to **pooled metrics**.

Exact label strings (must match the row template's `proposed_treatment` and `proposed_classification` vocabularies verbatim):

```
baseline_overclaim_rate    = count(current_classification == "overclaim")                / total_anchors
proposed_overclaim_rate    = count(proposed_classification == "overclaim")               / total_anchors    ← gate ≤ 10%
primary_preservation       = count(proposed_treatment == "primary pressure" AND
                                   primary_eligible == "yes")                            / count(primary_eligible == "yes")
secondary_framing          = count(proposed_treatment ∈ {"secondary lens",
                                   "set aside with a reason"} AND
                                   primary_eligible == "no")                             / count(primary_eligible == "no")
not_mushy                  = run-level qualitative judgment on the proposed-rewrite
                             sketches (per run; not per anchor)
anchor_naming_failures     = count(rows that fail the anchor-naming invariant audit)
```

**Zero-denominator handling:**
- If a run has zero `primary_eligible == yes` anchors, `primary_preservation` is **n/a for that run** (not pass, not fail). The pooled metric drops the run from the denominator.
- Symmetrically, if every anchor in a run is `primary_eligible == yes`, `secondary_framing` is **n/a for that run**. Pooled metric drops the run.
- `proposed_overclaim_rate` and `not_mushy` always have valid denominators (every anchor has a `proposed_classification`; every run has a not-mushy judgment).

Per-run metrics are reported as a table; pooled metrics are reported as a single column gated against the acceptance bars.

### No LLM calls for the design audit

The audit reviews existing archived `revised_answer` outputs against the proposed rules. We do not generate new Step 6 outputs in this phase — that comes after the rules are accepted, and live validation happens then.

If the audit shows the rules are sound and would not introduce mushiness, we proceed to:
- Implementation: edit `SKILL.md` Step 6 and `HOW_IT_WORKS.md` Step 6 prose **on an implementation branch** (not directly on main). The design docs live on main; the behavior-contract edits go through branch + live validation + PR so the prompt-contract change is reviewable before merge.
- Live validation: required pre-merge gate. 4 required cases (Marcus, consultant, PhD, mother), one live run each, score Step 6 outputs against D1 gates. ~$0.30 in OpenRouter, ~5-min wall.

## 8. What this design does NOT do

- Does not change `companion_cheat_sheet` shape or any audit field.
- Does not require any engine-side change.
- Does not promote v3/B work from the frozen research branch.
- Does not require a new measurement campaign.
- Does not touch Lane 1, Lane 3, Lane 4, or extraction.

It is a contract change at the Step 6 prompt boundary, validated against existing archived outputs.

## 9. Resolved review decisions

These were open questions in an earlier draft; resolved in design conversation 2026-04-26 and locked here so the audit and implementation work against settled framing.

a. **Anchor-treatment vocabulary names.** Resolved: **"primary pressure / secondary lens / set aside with a reason"** — the third category as a phrase, not "set-aside caveat." Reason: "caveat" can read as a buried hedge; the contract requires Claude to actively address the anchor without inflating it. These are rhetorical strength categories, NOT competing with the existing §1 / §2 / §3 section taxonomy at `SKILL.md:342`. A primary-pressure anchor can land in §1 or §3; a "set aside with a reason" anchor mostly lives in §2. The treatment vocabulary is an internal writing rule and does NOT appear as user-visible headings.

b. **Where the wording rules live in `SKILL.md`.** Resolved:
   - Short bridge sentence at the `CompanionCheatSheet` bullet around `SKILL.md:336`: "anchors are evidence-bearing hypotheses, not canonical diagnoses."
   - Full **Anchor treatment** sub-section immediately after the existing anchor-naming invariant at `SKILL.md:350`. Hard contract first ("every anchor must be addressed"), then "here is how strongly to address it."
   - Step 6's overall structure (§1 / §2 / §3) stays unchanged.

c. **Who runs the audit.** Resolved: implementer runs the initial pass with bias controls; reviewer audits the high-leverage subset.
   - Bias controls in the row template: `primary_eligible` decided BEFORE `proposed_treatment`; `current_classification` and `proposed_classification` scored independently; `proposed_classification` judges the sketch as written (not the intention); every row cites verbatim quotes (`evidence_quote` and `current_revised_answer_quote`).
   - Reviewer surface: all `uncertain == yes` rows + all Marcus rows + all rows where `proposed_treatment ∈ {"primary pressure", "set aside with a reason"}` + all `anchor_naming_failures`.

d. **Live validation as a hard pre-merge gate.** Resolved: yes, hard gate (not post-merge spot-check). Sequence:
   1. Run archive audit against proposed rules.
   2. If audit gates pass, edit `SKILL.md` + `HOW_IT_WORKS.md` **on an implementation branch** (not main).
   3. Run the 4 required cases (Marcus, consultant, PhD, mother) live once each. ~$0.30, ~5-min wall.
   4. Score Step 6 / `revised_answer` outputs against D1 gates.
   5. Merge only if no overclaim/mushiness regression appears.

Reason: the archive audit can answer "are these rules coherent against known outputs" but CANNOT answer "will Claude actually obey the edited `SKILL.md`." Prompt behavior is the thing being changed, so post-merge spot-check would be too late.

## 10. Pre-audit checklist

Before scoring rows, the implementer confirms:

- [x] Audit-template metric split (baseline vs proposed) is reflected in Section 7's row template.
- [x] Zero-denominator handling and pooled-vs-per-run reporting are specified.
- [x] Anchor-naming invariant audit failure is defined (sketch must include `display_name` verbatim).
- [x] Hidden anchors stay auditable via the `MISSING: ...` sentinel — Section 7's `current_revised_answer_quote` row.
- [x] Aggregate metric formulas use exact string labels matching the row template.
- [x] Resolved review decisions are captured in Section 9 (no stale open questions).
- [x] Implementation-branch + hard live-validation gate is captured in Section 7's "No LLM calls" subsection.

When all boxes are checked and the doc has had a second read, the audit is ready to run.
