# PR83 Decision/Action Enrichment v45 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr83-decision-action-v45`

Artifact: `model_affordances_v45`

Status: dormant review substrate only. No runtime, prompt, lane, packet, or product pickup is introduced.

## Verdict

REVISE/PASS as dormant substrate:

- PASS for source-custodied v45 enrichment.
- REVISE before runtime pickup remains true for the broader packet architecture, because grouped per-affordance identity and absence visibility still need packet stress review before `/lolla` can use these cards safely.

PR83 intentionally does not expand every decision/action model. The audit found that this ring is already comparatively mature: many records already have two affordances, strong `do_not_use_when` boundaries, and source-backed absence rails. The useful delta was narrower:

1. Split two records where one current card was carrying two different downstream receiver transactions.
2. Add first-class absence rails where the source warns against fake decision authority, fake action, or fake safety.
3. Keep everything dormant and compiled as a reviewed artifact only.

## Source Reading Scope

The audit focused on decision/action/execution records and their canonical Markdown sources under `MM_CANONICAL_216`, including:

- `Sunk_Cost_Fallacy_rag.md`
- `Status_Quo_Bias_rag.md`
- `Trade_Offs_rag.md`
- `Opportunity_Cost_rag.md`
- `Calculated_Risk_Taking_rag.md`
- `Risk_Assessment_rag.md`
- `Expected_Value_rag.md`
- `Multi_Criteria_Decision_Analysis_rag.md`
- `Prioritization_rag.md`
- plus adjacent read-only checks on lean startup, experimentation, iteration, feedback loops, input-vs-output goals, goal setting, constraints, bottlenecks, theory of constraints, commitment bias, and decision-tree records.

Subagent audits were used as independent read-only pressure checks, but the final changes were accepted only after local source review and exact source-quote compilation.

## Why This Is Not Another Broad Extraction Round

The operating question was:

> Would separating this material change the downstream card transaction?

Most proposed expansions failed that test. Many tempting source sections are examples, tools, or adjacent-model material:

- Pareto, Eisenhower, and MECE support prioritization, but do not require a new prioritization transaction.
- Cost-benefit analysis, decision trees, scenario analysis, and reference classes support expected value or calculated-risk reasoning, but are owned more cleanly by adjacent records.
- Digital twins, simulations, game workshops, and AI personas are implementation examples, not permission to add runtime behavior.
- Lean startup, experimentation, iteration, and feedback-loop records already contain strong fake-progress guards.

The audit therefore rejected “more material exists, therefore expand records.” It used the stricter rule: expand only where the future receiver needs a different use/reject/defer decision.

## Positive Splits Added

### `sunk-cost-fallacy.precommitment-exit-criteria`

Why split:

The old `sunk-cost-fallacy.future-value-recommitment` card bundled two different actions:

- reset an existing continuation decision after prior investment is already distorting judgment;
- predefine stop/change criteria before a new high-cost commitment creates sunk-cost pressure.

Those happen at different moments and require different evidence. v45 moves the before-starting material into a separate affordance.

Source custody anchors include:

- `Proactively define specific conditions (time, budget, performance metrics) under which the commitment will be stopped or changed *before* starting the project.`
- `"What specific performance criteria must be met to justify the next phase of investment?"`
- `"What evidence exists that would fundamentally prove our original hypothesis wrong?"`

Compression guard:

The new card does not turn project management gates into a generic sunk-cost affordance. Activation requires credible future sunk-cost pressure from high financial, time, identity, or emotional investment.

### `status-quo-bias.default-choice-architecture`

Why split:

The old `status-quo-bias.incumbent-option-inertia-test` diagnoses whether the current option is surviving because it is evidence-backed or inertia-protected. The source also supports a different transaction: deliberately designing defaults or reducing choice overload.

That requires different evidence:

- desired welfare or operating outcome;
- current default/opt-in/opt-out path;
- choice overload or cognitive-load evidence;
- opt-out, reversal, disclosure, or harm guard.

Source custody anchors include:

- `In the real world, the Status Quo Bias is applied—or exploited—most commonly in situations involving decision architecture and organizational inertia.`
- `If a company automatically enrolls employees in a 401(k) plan and requires them to actively opt-out, participation rates are significantly higher than if they must actively opt-in.`
- `To overcome this, the **Less Frame** should be applied, which involves reducing the number of choices offered.`
- `When decisions are repeatable, low-impact, or occur under time pressure, relying on the status quo or heuristics (fast, established thinking) is highly effective for reducing **cognitive load**.`

Compression guard:

The split keeps 401(k) defaulting and Less Frame together as one choice-architecture affordance. It does not split them into separate cards. The card includes explicit anti-exploitation guards.

## Absence Rails Added

v45 adds seven first-class absence records. These are not new positive cards. They are overclaim blockers for future packet/ledger use.

| Model | New absence | Purpose |
| --- | --- | --- |
| `expected-value` | `ev-without-verifiable-causal-links` | Blocks EV math when action, outcome, likelihood, and payoff are not tied by checkable causal links. |
| `multi-criteria-decision-analysis` | `criteria-chosen-after-option-review` | Blocks matrices that retrofit criteria/weights after the favored option is visible. |
| `prioritization` | `symptom-ranking-before-root-cause` | Blocks polished ranking of visible symptoms before root cause is diagnosed. |
| `trade-offs` | `rhetorical-tradeoff-without-reallocation` | Blocks trade-off talk when nothing is sacrificed, reallocated, killed, or ranked. |
| `opportunity-cost` | `default-continuation-as-costless` | Blocks staying-the-course approvals that do not name the next-best displaced use. |
| `calculated-risk-taking` | `calculated-label-with-unbounded-downside` | Blocks “calculated” as a rationalization label when assumptions are weak, downside is unbounded, or dissent is ignored. |
| `risk-assessment` | `risk-work-as-governance-optics` | Blocks risk checklists/matrices that satisfy governance optics without changing safeguards or decisions. |

These absence rails are deliberately first-class because a future receiver may need to say: “This nominated card is relevant, but this specific absence blocks promotion.”

## Compiled v45 Signals

Compiled output:

- `data/compiled/model_affordances/affordances_v45.json`
- `data/compiled/model_affordances/quality_report_v45.md`

Metadata:

- Records: `222`
- Affordances: `284`
- Absence records: `555`
- New affordances vs v44: `2`
- New absences vs v44: `7`
- Schema validation failures: `0`
- Source hash failures: `0`
- Source quote rejections: `0`

The artifact remains `draft_review_only`.

## Runtime Boundary

No live runtime pickup is introduced.

Guard checked:

- no `affordances_v45` or `model_affordances_v45` references were added to `engine/` or `scripts/` runtime paths;
- the compiled artifact is only a dormant reviewed substrate;
- no adapter, renderer, prompt, lane mapping, or `/lolla` behavior changed.

This matters because v45 improves the knowledge base, not the product surface. The broader PR55 concern still holds: runtime pickup needs packet stress testing before any live use.

## Rejected Expansion Notes

The audit explicitly rejected broad expansion in several places:

- `decision-trees`, `expected-value`, `multi-criteria-decision-analysis`, `prioritization`, `trade-offs`, and `opportunity-cost` remain compression-ok for positive affordance structure except for guard rails.
- `lean-startup-methodology`, `experimentation`, `iteration`, `feedback-loops`, `input-vs-output-goals`, and `goal-setting` did not earn new positive splits; their extra material mainly strengthens fake-progress guards.
- `theory-of-constraints`, `constraints`, `bottlenecks`, `calculated-risk-taking`, `risk-assessment`, and `commitment-bias` did not earn positive splits in this pass.
- `status-quo-bias` and `sunk-cost-fallacy` did earn splits because their source-supported extra material changes the receiver transaction.

The purpose is not to be cautious for its own sake. The purpose is to avoid turning the corpus into a pile of wise-sounding but transaction-ambiguous cards.

## Follow-Up Questions For Packet Stress

Before runtime pickup, packet review should specifically test:

1. Can the receiver distinguish `sunk-cost-fallacy.future-value-recommitment` from `sunk-cost-fallacy.precommitment-exit-criteria` when only compact snippets are shown?
2. Does `status-quo-bias.default-choice-architecture` preserve its opt-out/exploitation guard under truncation?
3. Do absence rails appear prominently enough to block false authority?
4. Do broad decision cards crowd out narrower execution cards under a 12-card or 16-card packet cap?
5. Can a future decoder ledger record whether each affordance was used, rejected, deferred, or blocked by absence?

## Bottom Line

v45 is a small but important quality pass. It does not chase coverage because coverage already exists. It improves transaction shape:

- two cards now have cleaner affordance identities;
- seven fake-authority/fake-action patterns are first-class absence rails;
- all changes are source-backed and compile cleanly;
- runtime remains untouched.

This is the right kind of enrichment for the current stage: more potential where the source supports a different action, and more restraint where extra material would only make the packet sound smarter without making it safer.
