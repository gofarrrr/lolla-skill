# Complex Conversation Baseline v0

Status: local evidence checkpoint
Date: 2026-06-27

This note records the first clean six-case complex conversation baseline after
the provider-boundary signature-metadata filter and the conversation
understanding probe sequence.

The purpose was not to run another impressive demo. The purpose was to test
whether normal `$lolla` can handle longer, messier, multi-turn strategic
conversations where the value is not only the final answer, but the reasoning
work that happened along the way.

The baseline run-gathering phase was evidence gathering only. It did not change
runtime behavior, prompts, `SKILL.md`, archive integration, specialist
integration, semantic coverage archive artifacts,
`conversation_understanding_ir.v0`, graph memory, embeddings, chunking, LLM
judges, or automatic human-review labels.

PR30 later turned these six archived runs into a local human/product review
seed set:

`../evals/complex-baseline-human-review-v0.md`

## Sample

All six cases were run manually in fresh sessions from the local scenario pack:

`plans/lolla-complex-test-conversations-2026-06-27/`

Each scenario contains 12 user turns and 12 assistant turns. The runs were
intentionally more complex than the earlier short smokes: multiple stakeholders,
soft pressure, changing constraints, sycophancy/status temptations, operational
risk, and non-obvious tradeoffs.

| # | case | archive | capture | run health | provider boundary | quote validation | evaluation | caller action | cost |
|---|---|---|---:|---|---|---|---|---|---:|
| 01 | cofounder conflict / investor pressure | `ceo-remove-founding-cofounder/20260627T093131Z_59d153` | 12/12 | `healthy` | `clean` | 6/6 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.060 |
| 02 | career / family / status | `accept-operations-role-startup/20260627T132700Z_bae7f3` | 12/12 | `healthy` | `clean` | 7/7 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.067 |
| 03 | enterprise beta launch | `launch-public-enterprise-beta/20260627T104146Z_7bfe79` | 12/12 | `healthy` | `clean` | 7/7 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.079 |
| 04 | small business pre-sale | `pre-sell-undefined-consulting/20260627T133637Z_cad396` | 12/12 | `healthy` | `clean` | 5/5 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.068 |
| 05 | product pivot / customer harm | `pivot-company-product-strategy/20260627T110450Z_5d2da7` | 12/12 | `healthy` | `clean` | 6/6 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.149 |
| 06 | clinic AI deployment | `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb` | 12/12 | `healthy` | `clean` | 7/7 verified, 0 fabricated | `warn` | `use_revised_answer` | $0.075 |

The `evaluation: warn` state in all six cases came from the same conservative
condition:

```text
live_output_health: not_checked
```

The saved product artifacts were clean. The evaluator simply does not claim the
live chat surface was separately hygiene-checked.

## Aggregate Mechanical Result

Across the six complex runs:

- 144 conversation turns were captured.
- All six runs captured exactly 12 user turns and 12 assistant turns.
- All six runs started with `[Turn 1] USER` and ended with `[Turn 12] ASSISTANT`.
- All six runs produced the full modern artifact chain:
  - `conversation.txt`
  - `extraction.json`
  - `result.json`
  - `revised.txt`
  - `memo.md`
  - `agent_result.json`
  - `extraction_adequacy_report.json`
  - `evaluation.json`
  - `reasoning_trace.json`
- All six runs had `run_health.overall: healthy`.
- All six runs had `provider_boundary_health.status: clean`.
- All six runs had `product_output_health: clean`.
- All six runs had `capture_adequacy.status: good`.
- All six runs had `caller_action: use_revised_answer`.
- 38 quote-validation passages were verified.
- 0 quote-validation passages were fabricated.
- Total estimated cost was about $0.50, averaging about $0.083 per complex run.

The local extraction adequacy corpus after the six-case baseline showed:

| metric | value |
|---|---:|
| records | 80 |
| valid records | 80 |
| extraction adequacy `good` | 68 |
| extraction adequacy `warn` | 11 |
| extraction adequacy `critical` | 1 |
| capture adequacy `good` | 18 |
| report available | 17 |
| clean baseline sample | 17 |
| quote fabrication total | 22 |

The quote-fabrication total stayed historical. These complex modern runs did
not add fresh quote-validation failures.

## What Lolla Did Well

The strong signal is not merely that the runs completed. The strong signal is
that the revised answers repeatedly changed the operating shape of the advice.

### 01 Cofounder Conflict / Investor Pressure

Lolla moved the advice from a tidy reset conversation toward an authority-first
transition: move actual decision rights now, allow a constrained transition
only after authority has moved, protect customer continuity, and stop letting
the product lead / COO ambiguity remain invisible.

### 02 Career / Family / Status

Lolla moved the advice away from vague language about aliveness, dignity, and
startup energy. The revised position required written operating terms from both
options: the current-company platform role must become a concrete arena
contract by Friday, and the startup must provide a bounded six-month operating
agreement by Monday. Spouse consent became household-capacity evidence, not a
soft permission ritual.

### 03 Enterprise Beta Launch

Lolla stopped letting the 900-person prospect win by aura alone. Both prospects
must accept the same written pilot shape, and the choice should be scored by
payment, procurement clarity, scope tolerance, support burden, reference value,
and whether the public-launch thesis is falsifiable.

### 04 Small Business Pre-Sale

Lolla preserved the one-paid-pilot recommendation but corrected an overreach.
The desire for a professional surface was not dismissed as pure status. A
client-ready pilot brief is legitimate; the agency role should stay tiny and
limited to polish, not offer definition or premature buildout.

### 05 Product Pivot / Customer Harm

Lolla put capacity before market proof. The original higher-ACV workforce pivot
was tempting, but the revised position required a 14-day capacity and obligation
gate before the 60-day market gate. Existing nonprofit obligations became a
contractable maintenance product, not a comforting phrase.

### 06 Clinic AI Deployment

Lolla challenged checklist theater. The original nine-gate AI launch plan
looked responsible but was too heavy for exhausted admins. The revision
compressed the launch into four must-pass gates and added a 48-hour backlog
diagnosis so the AI pilot has to earn its place against non-AI operational
fixes.

## What Still Did Not Work Fully

The six-case baseline repeats the same semantic coverage frontier seen in PR26,
PR27, PR29B, and PR29D:

| semantic element | current state |
|---|---|
| `decision` | present, usually derivation-grounded |
| `counter_pressure` | present, artifact-level |
| `actionability_boundaries` | present in modern runs, artifact-level |
| `revised_answer_change_reason` | present, artifact-level |
| `live_constraints` | partial, turn-ref grounded |
| `dropped_or_under_carried_threads` | partial, turn-ref or artifact-level |
| `assistant_stance_or_recommendation_lineage` | partial, artifact-level |
| `user_values_or_priorities_signal` | not measured |

This is the important product read:

> Lolla can produce useful revised advice on complex conversations, but the
> deterministic semantic record does not yet fully explain why in a
> source-grounded way.

That means the next evaluation work should not be a generic LLM judge. PR30 has
made the human/product review of these traces explicit; PR31 defined the
actionable-delta rubric, PR32 defined adversarial fixtures, and PR33 broadened
the human-review batch before any judge prototype.

## Evaluation Implication

The six-case baseline is now the first small human-reviewed seed for
Lolla-specific evaluation. PR30 answered the review question:

```text
Can a reviewer, using the current artifacts, explain why the revised answer is
better or worse than the original answer without relying on vibe?
```

PR30 result:

- all six answer-level reviews passed;
- all six revised answers were labeled improved;
- all six remain `safe_for_agent_use: with_human_review`;
- the conservative reliance label is because saved artifacts are reviewable but
  `live_output_health` remains `not_checked`;
- `evaluation.json` remains deterministic run-readiness, not answer-quality
  scoring;
- `caller_action: use_revised_answer` is not human approval.

This is not large enough for judge calibration. It is large enough for:

- a human-reviewed "good Lolla run" reference set;
- open coding of what useful friction looked like;
- examples of actionable deltas versus smooth no-ops;
- examples of overcorrection risk;
- examples of semantic coverage gaps that explain what the archive cannot yet
  prove;
- a first pairwise/adversarial eval fixture set after the rubric exists.

Completed follow-on eval slices:

```text
PR31 Actionable Delta Rubric v0
PR32 Adversarial Pair Fixture Set v0
PR33 Human Review Corpus Batch v0
```

PR31 defined what counts as real Lolla improvement. PR32 turned the six complex
cases into paraphrase-only adversarial pair fixtures. PR33 expanded the review
batch beyond these six anchors while preserving the same boundary: no judge, no
automatic labels, no answer-quality score, no runtime change.

## Product Opportunities

The evidence points to several opportunities, in this order:

1. **Actionable-delta rubric from the six reviewed runs.**
   PR30 defined the first human-reviewed seed. PR31 turned those labels into a
   rubric for real improvement versus smooth no-op prose.

2. **Adversarial pair fixtures.**
   PR32 turned the six cases into pairs where the smoother original answer
   competes with the rougher but more protective revised answer.

3. **Broader human-review corpus batch.**
   PR33 reviewed a 14-record local batch with the PR30/PR31 label language:
   12 counted positives, one partial boundary record, and one degraded
   exclusion.

4. **First-class user-values/priorities design.**
   The repeated `user_values_or_priorities_signal: not_measured` gap is now
   visible across the corpus. Do not smuggle this into the existing specialist
   set; design it explicitly.

5. **Span-grounded semantic enrichment.**
   Existing specialists have evidence for live constraints, stance lineage, and
   dropped threads, but runtime/archive integration remains blocked until a
   clean 15-20 full-modern sample and provider-boundary behavior are settled.

6. **Live-output hygiene check.**
   The deterministic evaluator keeps warning that live-output health is
   `not_checked`. That is honest, but if we want clean evaluation receipts, we
   eventually need a bounded way to check the live surface or clearly define why
   it remains advisory.

7. **Calibrated binary judges later.**
   Only after human labels exist should Lolla prototype binary judges such as
   `actionable_delta`, `earned_friction`, `pressure_absorption`, and
   `overcorrection_absent`.

## Not Justified Yet

This baseline does not justify:

- runtime specialist integration;
- archive integration for specialist outputs;
- a broad `conversation_understanding_ir.v0`;
- graph DB integration;
- embeddings-first memory;
- prompt rewrites;
- quote-validation repair;
- automatic human-review labels;
- a generic LLM judge;
- answer-quality scoring;
- agent auto-approval.

The restraint matters. The six runs show product value, but they also show why
the harness must keep separating model judgment from deterministic custody and
human evaluation.
