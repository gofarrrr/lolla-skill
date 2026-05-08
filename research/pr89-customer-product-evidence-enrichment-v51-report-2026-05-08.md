# PR89 Customer/Product Evidence Enrichment v51 Report

Date: 2026-05-08

Status: PASS as dormant reviewed substrate. REVISE before runtime pickup.

## Scope

PR89 reviewed the customer/product evidence ring after v50:

- `jobs-to-be-done`
- `user-centered-design`
- `user-experience-research-methods`
- `usability-heuristics`

Adjacent boundary checks included `lean-startup-methodology`, `empathy`, and `understanding-motivations` to avoid duplicating product discovery, empathy, or motivation material under softer names.

This PR does not alter runtime, prompt, lane, packet, product, or user-facing behavior. It only updates dormant reviewed affordance records and compiles `model_affordances_v51`.

## Contradicting Evidence First

The tempting failure mode was to expand every rich product/customer source into several attractive cards. The corpus supports many examples, stages, and related techniques, but not all of them deserve separate packet identity.

Two records did deserve positive splits:

- `user-centered-design`: the source separates reframing a flawed brief from testing prototypes with real users. Those are different downstream actions.
- `user-experience-research-methods`: the source separately supports digital twin screening, but only with persona source data, twin validation, live-boundary discipline, and privacy/bias/transparency controls.

Two records did not deserve positive splits:

- `jobs-to-be-done`: pivot strategy, messaging, and value proposition changes still flow through the same operational transaction: identify the real progress customers hire the product to make.
- `usability-heuristics`: the source supports broad checked shortcuts and decision aids, not a concrete Nielsen UI checklist card.

## Accepted Changes

### User-Centered Design

Added:

- `user-centered-design.reframe-flawed-brief-from-user-observation`

This card activates before solution ideation or prototyping. It asks whether the original design brief, product ask, or internal frame is wrong from the user's point of view.

Key source support:

- `observation and discovery of human needs at the core`
- `reframe the problem`
- `reframe and correct`
- `**reframe it** through a Point of View`

Retained and narrowed:

- `user-centered-design.prototype-user-evidence-loop`

The existing card now focuses on candidate solution/prototype validation with real-user reactions. It no longer carries the problem-reframing transaction.

Key source support:

- `evidence from users’ reactions to successful or failed prototypes`
- `**Build and Test** iteratively with real people`
- `test assumptions about solutions`
- `iterative prototyping and testing with users to **validate assumptions**`

Added absence rails:

- `average-user-confirmation-as-sufficient-discovery`
- `synthetic-persona-as-user-evidence-replacement`

Why:

- The source warns that average-user focus can merely `confirm what we already know`.
- The source includes digital twin personas for rapid pre-validation, but still grounds UCD in real-user observation, prototype reactions, and testing with real people.

### User Experience Research Methods

Added:

- `user-experience-research-methods.digital-twin-screening-before-live-commitment`

This card is deliberately narrow. It permits digital twin/persona screening only as provisional option screening before live commitment, not as market proof or as permission to inject runtime model calls.

Key source support:

- `AI Agents as Digital Twins`
- `computational representations of users or customer segments designed to mimic behavioral tendencies, personality, language, and decision-making processes`
- `validating twins for accuracy`
- `predict customer reactions to new features`
- `pre-validate decisions in silico`
- `transparency, privacy, and avoiding manipulation or bias must be discussed and addressed`

Added absence rail:

- `research-volume-as-rigor-affordance`

Why:

- The source explicitly rejects research volume for its own sake: `Gathering data for research's sake, or attempting to analyze every possible detail, wastes time and effort`.

### Usability Heuristics

Kept one positive affordance:

- `usability-heuristics.lower-friction-with-checked-shortcuts`

Added absence rail:

- `nielsen-checklist-as-source-supported-ui-audit`

Why:

- The source supports broad heuristics, rules of thumb, Occam's Razor, the Rule of Three, decision aids, interface conventions, and triage rules.
- It does not support promoting this record as a source-backed Nielsen-style ten-heuristic UI audit checklist.

### Jobs To Be Done

No record change.

Rationale:

- The source is rich, but the extra product strategy material does not create a separate downstream card transaction.
- Messaging, pivoting, positioning, and roadmap implications still depend on the same core move: separate real customer progress from feature preference, channel feedback, or internal strategy wish.

## Anti-Sycophancy Review

Verdict: PASS as dormant reviewed substrate. REVISE before runtime pickup.

What would have to be true for this PR to be good:

- The UCD reframing card must change downstream behavior differently from prototype validation. Status: SOLID.
- The UXRM digital twin card must remain provisional and guarded, not become synthetic certainty. Status: SOLID for substrate, UNTESTED for runtime.
- JTBD compression must not hide a distinct transaction. Status: SOLID after reread.
- Usability heuristics must not be inflated into a specific UI audit checklist without source support. Status: SOLID.
- Future packet display must preserve per-affordance identity. Status: UNTESTED.

Failure modes to watch later:

- Digital twin screening gets treated as proof of market demand.
- UCD and UXRM collapse into one generic "talk to users" card during packet rendering.
- Absence rails are hidden in display, losing the guard against synthetic persona replacement.
- Broad product discovery cards crowd out narrower evidence requirements.

What would falsify this enrichment:

- Static packet stress review shows the UCD reframe card and UXRM observed-user-evidence card are indistinguishable to receivers.
- A reviewer cannot tell whether the digital twin card was used, rejected, or deferred as a separate transaction.
- The LLM treats digital twin screening as enough to skip live evidence.
- JTBD cases repeatedly require a transaction not covered by real-progress job discovery.

## Compiled Artifact

Compiled with:

- Artifact: `model_affordances_v51`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `296`
- Absence records: `572`
- Schema-validation failures: `0`
- Source-quote rejections: `0`

Delta from v50:

- Positive affordances: `+2`
- Absence records: `+4`
- Model coverage: unchanged
- Runtime imports: unchanged

## Validation

Commands:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v51.json --quality-report-filename quality_report_v51.md --artifact-id model_affordances_v51 --report-title "Model Affordance Quality Report v51"
PYTHONPATH=. pytest tests/test_pr89_v51_customer_product_evidence_enrichment.py tests/test_pr88_v50_weak_support_pricing_enrichment.py tests/test_model_affordance_compiler.py
git diff --check
rg -n "affordances_v51|model_affordances_v51" engine scripts -g '*.py'
```

## Runtime Boundary

`affordances_v51.json` is a dormant reviewed artifact. There are no live runtime references to:

- `affordances_v51`
- `model_affordances_v51`

Future live pickup still requires explicit artifact selection, lane provenance preservation, grouped affordance identity, confidence visibility, absence visibility, and receiver-side use/reject/defer grammar.

## Bottom Line

PR89 does not dump richer product language into the system. It separates two places where the corpus supports genuinely different downstream decisions:

- Reframe the product/user problem before solution work.
- Use digital twins only as guarded, source-backed, provisional screening before live commitment.

It also adds four absence rails where overclaim risk is high. This improves substrate quality without moving the artifact closer to runtime by accident.
