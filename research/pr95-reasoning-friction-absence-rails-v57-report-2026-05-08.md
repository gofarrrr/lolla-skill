# PR95 v57 Reasoning Friction Absence-Rail Enrichment

Status: dormant reviewed substrate only.

PR95 continues the post-coverage enrichment work after v56. It does not add runtime pickup, prompt behavior, packet behavior, lane behavior, or product integration. The goal was to test whether six reasoning-quality sources contained additional transaction-level affordances or whether their extra material should be preserved as first-class absence/owner-routing rails.

## Frame

The audit used the stricter post-v18 rule:

> Add a positive affordance only when the source supports a distinct downstream transaction with different activation conditions, evidence required, do-not-use boundaries, treatment/misuse guard, and receiver use/reject/defer behavior.

If material was real but would not change the receiver transaction, PR95 did not split it. If material was tempting but belonged to another owner, PR95 made that boundary explicit as an absence record.

This was especially important for reasoning-meta cards. These cards sound wise and can easily become broad vocabulary rather than sharper judgment. The PR95 choice was: no extra positive cards, stronger negative knowledge.

## Sources Reviewed

The following canonical Markdown sources were read fully and compared to current JSON records and adjacent ownership records:

- `Chain_Of_Thought_rag.md`
- `Reasoning_Mode_Router_rag.md`
- `Cognitive_Gaps_Assessment_rag.md`
- `Representativeness_Heuristic_rag.md`
- `Cognitive_Biases_rag.md`
- `False_Precision_Avoidance_rag.md`

Read-only subagent audits were also used as independent checks:

- Scope A: chain-of-thought, reasoning-mode-router, cognitive-gaps-assessment.
- Scope B: representativeness-heuristic, cognitive-biases, false-precision-avoidance.

Both audits converged with the local read: no new positive affordance splits should be added for these six records.

## Decision

Verdict: PASS as richer dormant substrate, with no positive expansion.

PR95 added 16 absence records and 0 positive affordances.

Compiled v57:

- Artifact: `model_affordances_v57`
- Records: `222`
- Affordances: `303`
- Absence records: `640`
- Delta from v56: `+0` affordances, `+16` absence records
- Schema failures: `0`
- Source quote rejections: `0`

## Why No Positive Splits

### Chain Of Thought

The current card already owns the useful transaction: use stepwise reasoning as an audit surface for hidden assumptions, weak links, evidence checks, pruning, and action path. Extra source material around LLM prompting, prompt chaining, logic trees, MECE, and hypothesis pyramids is real, but it does not justify separate chain-of-thought affordances.

Rejected positive splits:

- Prompt chaining / "let's think step-by-step": source-supported as an example, but too thin and too dangerous to promote into runtime prompt behavior.
- Logic-tree decomposition: better owned by `decomposition`, `chain-of-verification`, and `scientific-method-evidence-testing`.

Added rails:

- `prompt-chaining-as-runtime-prompt-affordance`
- `logic-tree-decomposition-as-chain-of-thought-split`

### Reasoning Mode Router

The current card already owns context-driven mode selection and switch evidence. The source's role-prompt and agent-persona material would become prompt or persona mechanics. The croc-brain/neocortex material is communication/adoption packaging, not reasoning-mode routing.

Rejected positive splits:

- Role prompts / expert persona routing.
- AI decision-rule hard-coding.
- Audience processing mode as a router split.

Added rails:

- `role-prompt-or-agent-persona-routing-affordance`
- `audience-processing-mode-as-reasoning-router-split`

### Cognitive Gaps Assessment

The current card owns missing-condition audit: name the knowledge, capability, perspective, or communication-transfer gap and state what changes in evidence, preparation, or decision exposure.

Several source passages are useful but not separate CGA transactions:

- Knowledge gap elasticity is mainly authority/deference risk.
- Unknown unknowns are only useful if converted into preparation or exposure.
- Communication-transfer gaps should route to communication/scaffolding records when the treatment becomes teach-back, analogy, novice observation, or audience packaging.

Added rails:

- `slight-knowledge-advantage-as-gap-closure`
- `generic-unknown-unknowns-without-exposure`
- `communication-transfer-as-standalone-gap-affordance`

### Representativeness Heuristic

The current card correctly owns the resemblance-vs-probability transaction: when a case feels obvious because it matches a prototype, force base-rate, reference-class, and structural-fit checks.

Rejected positive splits:

- Analogy as communication aid: better owned by association, analogies/metaphors, simplification, cognitive load, or curse of knowledge.
- Recent vividness without prototype match: related to availability/recency, not a separate representativeness transaction.
- Expert "I've seen this before" pattern match as proof: should trigger structural-fit and base-rate checks, not become evidence.

Added rails:

- `communication-analogy-as-probability-evidence`
- `recent-vividness-without-prototype-match`
- `expert-pattern-match-as-proof`

### Cognitive Biases

The current card is intentionally broad: use bias awareness as symmetric process discipline when the exact bias is not yet clear. The source contains many specific biases and mitigations, but those should route to narrower records when the active mechanism is identifiable.

Rejected positive splits:

- Specific bias list as separate general cognitive-bias affordances.
- Perspective taking as a general debiasing affordance when actor modeling or communication adaptation is the real transaction.
- Bias awareness as blanket intuition suppression.

Added rails:

- `exact-narrower-bias-available-as-general-bias-card`
- `perspective-taking-as-general-debiasing-affordance`
- `bias-awareness-overcorrects-calibrated-intuition`

### False Precision Avoidance

The current card owns decision-relevant precision boundaries: replace fake exactness with thresholds, ranges, or approximations only when precision does not change the decision.

Rejected positive splits:

- "Don't boil the ocean" as ordinary analysis stop rule.
- Communication brevity without a decision-relevant threshold or uncertainty boundary.
- Prompt concision as runtime prompt behavior.

Added rails:

- `analysis-stop-rule-without-false-precision`
- `communication-brevity-without-decision-threshold`
- `prompt-concision-as-runtime-prompt-affordance`

## Quality Interpretation

PR95 is a useful example of enriching the corpus without expanding positive affordances. The result is not less knowledge. It is more routing discipline:

- The LLM can still see the reviewed card.
- The substrate also tells it when the tempting nearby move should not be promoted.
- Adjacent owners are preserved instead of flattened into broad meta-cards.
- Runtime prompt and product-behavior examples stay dormant and non-operative.

This directly supports the larger context-engineering thesis: reasoning addenda should give the model extra angles and cautions without forcing mental-model theater.

## Runtime Boundary

No engine or script path imports `affordances_v57` or `model_affordances_v57`.

The compiled artifact remains draft-review-only. Future live pickup still needs separate packet, provenance, renderer, and receiver-ledger decisions.

## Validation

Commands used:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v57.json --quality-report-filename quality_report_v57.md --artifact-id model_affordances_v57 --report-title "Model Affordance Quality Report v57"
```

Focused validation target:

```bash
PYTHONPATH=. pytest tests/test_pr95_v57_reasoning_friction_absence_rails.py tests/test_pr94_v56_structured_reasoning_enrichment.py tests/test_model_affordance_compiler.py
```
