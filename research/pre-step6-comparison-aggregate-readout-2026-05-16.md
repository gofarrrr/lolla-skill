# Pre-Step-6 Comparison Aggregate Readout

Date: 2026-05-16

Status: manual research aggregate. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Readouts:

```text
research/pre-step6-comparison-readouts/third-year-phd-student-answer-variant-readout-2026-05-16.md
research/pre-step6-comparison-readouts/founder-grant-marcus-equity-answer-variant-readout-2026-05-16.md
research/pre-step6-comparison-readouts/mid-level-consultant-report-2-answer-variant-readout-2026-05-16.md
```

## Verdict

```text
manual comparison: bundle wins all three fixtures
promotion decision: no promotion
next decision: run a less-author-biased answer-variant comparison
```

This is a promising manual signal, not a promotion-grade result.

The bundle appeared useful in three different ways:

- PhD case: preserved unresolved tension and made the controlling gates visible.
- Founder case: demoted duplicate pressure and carried the marginal systems
  pressure.
- Consultant case: preserved hard safety boundaries while adding only the most
  useful refinements.

## Results Table

| Case | Main Shape | Manual Result | Bundle Fields That Carried Lift |
| --- | --- | --- | --- |
| Third-year PhD student | Conflict / fallback viability | C wins | `conflicts_or_tensions`, `hard_boundaries`, `rethinking_questions` |
| Founder grant Marcus equity | Duplicate demotion | C wins | `duplicate_or_lower_priority`, `quiet_or_discard_candidates`, `final_reasoner_instruction` |
| Mid-level consultant report | Hard-boundary preservation | C wins | `hard_boundaries`, `conflicts_or_tensions`, `quiet_or_discard_candidates`, `final_reasoner_instruction` |

## Contradicting Evidence First

The result is suspiciously clean.

Reasons not to over-trust it:

- the same author created fixtures, answer variants, and scores;
- Arm C was written with knowledge of the bundle's intended benefit;
- Arm B can be made worse by over-including raw artifacts;
- a strong final reasoner may naturally demote raw artifacts without needing a
  bundle index;
- the comparison uses compact answer cores, not full Step-6-style responses;
- there is no independent judge or blind scoring yet.

Therefore this aggregate does not authorize:

- worker implementation;
- `reasoning_workpack.v1` builder work;
- subagent prompt builders;
- `/lolla` runtime changes;
- product-doc changes;
- claims that bundles beat raw artifacts in real runs.

## What The Manual Result Actually Supports

The manual result supports only this narrower claim:

```text
When artifacts are already compact and the bundle index is well-authored,
the bundle shape can make it easier for a final reasoner to see what to use,
demote, preserve, or discard.
```

That is a handoff-shape hypothesis. It is not producer-quality evidence and not
runtime evidence.

## Strongest Alternative Explanation

Raw artifacts may be enough.

In all three cases, the raw artifacts already carried the important fields:

- hard boundary;
- relaxation condition;
- discard condition;
- risk if forced;
- risk if ignored.

A careful final reasoner might reach the same answer from raw artifacts alone.
If that holds in a less-author-biased run, the bundle should not be promoted.

## Next Evidence Tier

Run the same three fixtures through a less-author-biased comparison.

Minimum next method:

```text
1. Freeze the fixtures.
2. Generate Arm A / B / C answer variants in separate contexts or separate passes.
3. Hide the expected verdict from the variant writer.
4. Score with the readout template.
5. Record ties as wins for the simpler path.
```

Allowed:

- manual blind-ish pass in a fresh context;
- separate subagent or external model only as a research evaluator;
- strict source/overclaim audit after variants are written.

Still not allowed:

- runtime integration;
- worker orchestration;
- product docs;
- broad OpenRouter final synthesis;
- treating the manual C-wins as implementation approval.

## Decision

```text
run_less_author_biased_answer_variant_comparison
```

Do not build worker machinery yet.

## Promotion Bar After This Aggregate

The next comparison must preserve the same win standard from the decision note:

- indexed bundle beats raw artifacts in at least two high-clutter cases;
- indexed bundle does not lose the hard-boundary case;
- improvement is visible in final prose;
- answer does not become longer by default;
- exact bundle fields carrying lift are identifiable.

If raw artifacts tie in the next comparison, raw artifacts win.

## Stop Rule

If a less-author-biased pass produces mostly ties, stop the bundle path and
extract only the raw-artifact lessons:

```text
keep source grounding
keep hard_boundary
keep relaxation_condition
keep discard_condition
keep risk_if_forced / risk_if_ignored
skip the bundle index
```

That would still be a useful research outcome.
