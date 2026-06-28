# User Values / Priorities Worksheet Fixtures v0

Status: docs/eval-only fixture pack
Date: 2026-06-28
Slice: PR50

PR50 tests whether the PR49 user-values/priorities worksheet is understandable
through paraphrase-only human-review fixtures.

This slice does not run `$lolla`, call models, inspect raw archive transcripts,
change runtime behavior, change prompts, change `SKILL.md`, mutate archives,
implement extraction, add a blank worksheet exporter, add a validator, add
memory, populate labels automatically, score answer quality, add a judge, or
change `caller_action`.

Machine-readable fixtures live in:

```text
docs/evals/user-values-priorities-worksheet-fixtures-v0.json
```

## Why Fixtures Before Code

PR34 defined the `user_values_or_priorities_signal` surface. PR49 turned that
surface into a human-owned worksheet plan. PR50 keeps the next step small: use
paraphrase-only examples to see whether the worksheet shape is clear enough for
reviewers before any exporter, validator, extractor, runtime field, memory
layer, or `conversation_understanding_ir.v0` exists.

The point is not to prove that Lolla understands values. The point is to test
whether humans can record values, priorities, obligations, conflicts, and answer
treatment without overclaiming.

The fixtures are based on existing PR30 and PR33 review patterns, especially:

- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [Human Review Corpus Batch v0](human-review-corpus-batch-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [User Values / Priorities Worksheet Plan v0](user-values-priorities-worksheet-plan-v0.md)
- [User Values / Priorities Signal v0](../conversation-understanding/user-values-priorities-signal-v0.md)

They do not copy raw transcript text, memo text, revised-answer text,
model/provider text, private reasoning, local absolute paths, secrets, or
credentials.

## Fixture Table

| fixture_id | source pattern | main values/priorities tension | central failure trap | expected review read |
|---|---|---|---|---|
| `uvp_v0_001_cofounder_authority_transfer` | Cofounder authority transfer | Cooperation, fairness, legitimacy, authority clarity, and avoiding status theater. | Over-crediting warm cooperation language while missing unresolved authority ambiguity. | Worksheet is sufficient; supports existing PR31 labels; no automatic reliance change. |
| `uvp_v0_002_career_family_written_terms` | Career/family written terms | Ambition, household capacity, spouse impact, identity pressure, reversibility, and written terms. | Treating emotional salience as stable identity and missing the need for concrete terms. | Worksheet is sufficient; supports existing PR31 labels; no automatic reliance change. |
| `uvp_v0_003_enterprise_beta_buyer_proof` | Enterprise beta buyer proof | Learning speed, credibility, customer trust, revenue momentum, and reliability obligations. | Confusing enterprise aura with validated buyer priority. | Worksheet is sufficient; supports existing PR31 labels; no automatic reliance change. |
| `uvp_v0_004_consulting_presale_scoped_pilot` | Consulting pre-sale scoped pilot | Revenue, credibility, client trust, scope discipline, and premature scale. | Either dismissing all polish as status spending or over-crediting polish while missing scope. | Worksheet is sufficient; supports existing PR31 labels; no automatic reliance change. |
| `uvp_v0_005_product_pivot_capacity_gate` | Product pivot capacity gate | Market proof, current obligations, team capacity, and not abandoning commitments too early. | Rewarding market excitement while missing capacity and existing-obligation gates. | Worksheet is sufficient; supports existing PR31 labels; no automatic reliance change. |
| `uvp_v0_006_clinic_controls_high_risk_deployment` | Clinic controls high-risk deployment | Patient/client safety, adoption, compliance, operator accountability, and avoiding checklist theater. | Over-crediting a long checklist while missing whether controls can actually stop rollout. | Worksheet is sufficient; keeps reliance more conservative in high-stakes-like review. |

Six fixtures are enough for v0 because they cover the six PR30 anchor patterns
and the exact values/priorities tensions PR34 named as corpus-safe examples.
Adding more records now would mostly test breadth before the shape has been
reviewed.

## What The Fixtures Teach

Values can be explicit or inferred, but inferred values should usually carry
lower confidence and require user confirmation. Several fixtures use
`grounding: derivation` or `grounding: reviewer_inference` because PR50 is
paraphrase-only and does not cite raw turns or spans.

Stakeholder obligations are not the same as user preferences. Household load,
customer reliability, current-user obligations, client trust, and patient/client
safety are recorded as obligations or obligation-shaped constraints, not as
lightweight tastes.

Emotional salience is not automatically a non-negotiable. The career fixture
marks family stability and ambition-related tradeoffs as reviewable but keeps
the exact hard boundary uncertain unless the user confirms it.

Constraints should not be laundered into values. Team capacity, support load,
procurement clarity, and operating controls can imply values, but the worksheet
should preserve their operational role instead of making them sound profound.

Unresolved conflicts should stay visible rather than being flattened into a
confident recommendation. The fixtures intentionally preserve conflicts around
cooperation versus authority, ambition versus household stability, buyer aura
versus proof, cash versus trust, market upside versus current obligations, and
adoption versus safety.

Answer improvements may add questions, gates, thresholds, written terms, scope
limits, or stop rules because values are unresolved. The worksheet explains why
those PR31 deltas mattered; it does not replace the PR31 labels.

## Relationship To PR31

The fixture pack supports the PR31 actionable-delta rubric by giving reviewers
more explicit context for why a delta mattered.

Examples:

- `user_question_added`: an unresolved value or stakeholder conflict needs a
  user or stakeholder answer before action.
- `threshold_changed`: a value or obligation becomes a concrete gate.
- `stop_rule_added`: a safety, trust, or authority boundary needs a pause,
  reversal, or refusal condition.
- `written_term_added`: a value conflict needs written operating terms rather
  than verbal alignment.
- `scope_narrowed`: a priority or obligation makes the broader path dishonest
  or unsafe.
- `overclaim_retracted`: the revised answer stops pretending it knows the
  user's motives or permission to trade something away.

The worksheet does not replace PR31 labels. It is not a score, not a new
improvement label, and not a judge. More value items do not mean a better
answer. A single unresolved stakeholder obligation can matter more than several
weak inferred priorities.

## Relationship To High Stakes And Risk Mode

The clinic fixture is `high_stakes_like_paraphrase` because it tests safety,
compliance, and operational accountability without creating real high-stakes
archive evidence.

For high-stakes-like scenarios, unresolved values, stakeholder obligations, or
non-negotiables should make reliance more conservative. The fixture pack does
not change `risk_mode`, `caller_action`, review-corpus export, evaluation
logic, human-review labels, or `safe_for_agent_use`.

In particular, `safe_for_agent_use_impact: makes_more_conservative` means the
worksheet gives a human reviewer a reason to stay cautious. It does not prove
`safe_for_agent_use`, approve domain use, or authorize automatic reliance.

## Fixture Contract

The JSON fixture pack uses:

```text
lolla.user_values_priorities_worksheet_fixtures.v0
```

Each fixture includes:

- `fixture_id`;
- `source_pattern`;
- `risk_mode_context`;
- `review_scope`;
- `why_this_fixture_exists`;
- `values_items`;
- `conflicts`;
- `answer_treatment`;
- `expected_review_read`;
- `rubric_connections`;
- `failure_trap`;
- `custody_flags`.

The custody flags are deliberately repetitive. They make the privacy boundary
machine-checkable before any future exporter exists.

## Recommended PR51

Recommended next slice:

```text
PR51 User Values / Priorities Worksheet Fixture Review v0
```

PR51 should stay docs/eval-only. A human/product reviewer should inspect the
six fixtures and answer:

- Are the value items understandable?
- Are inferred priorities too confident?
- Are stakeholder obligations distinct from preferences?
- Are conflicts preserved instead of flattened?
- Does the worksheet help explain PR31 labels?
- Does the high-stakes-like fixture keep reliance conservative without changing
  runtime policy?

Do not jump directly to blank worksheet export. A blank exporter would make the
shape look more settled than it is. The next safer move is to review the
fixture pack, patch the worksheet shape if needed, and only then decide whether
exporter or validator code is justified.

## Review Receipt

- PR50 is docs/eval-only.
- Fixtures are paraphrase-only.
- No `$lolla` run.
- No model calls.
- No raw archive transcript inspection.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No extraction implemented.
- No blank worksheet exporter added.
- No validator added.
- No memory layer added.
- No `conversation_understanding_ir.v0` added.
- No judge or answer-quality score added.
- No automatic labels added.
- No high-stakes runs started.
- PR51 should be fixture review, not code.
