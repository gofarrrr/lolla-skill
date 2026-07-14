# Source-First User Counter-Pressure Review

Date: 2026-07-10  
Status: local contract prepared and paid Case 08 preflight completed; gate failed  
Decision: replace the broad experimental meaning of `user pressure` with a
narrower `reasoning counter-pressure` target for the next preflight

## Why the first SK4 target failed

The first focused reader returned 61 exact-source-valid pressure events across
nine artifacts. Those events reduced to 31 unique case/kind/quote selections.
The label distribution was:

| old label | selected events |
| --- | ---: |
| concern | 39 |
| correction | 13 |
| evidence request | 6 |
| timing pressure | 3 |
| value | 0 |

The reader became more repeatable, but generic concerns used 64% of its
capacity. In Case 08 it returned the same eight concerns in every repeat and
missed the locked household-conversation qualification every time. The model
was stable; the semantic job was too broad.

## Revised product target

The reader's job is now:

> Preserve user statements that materially correct a premise or frame,
> qualify evidence or feasibility, or object to the reasoning being used.

The operational inclusion test is:

> If omitting the statement would make a future reader misunderstand why the
> reasoning was revised, became less certain, became conditional, or was
> contested, include it.

This is intentionally narrower than collecting everything important to the
decision. Constraints, values, worries, questions, and evidence can be
important without being counter-pressure on the reasoning.

## Revised labels

| label | meaning |
| --- | --- |
| `premise_correction` | The user rejects or repairs a fact, interpretation, decision frame, or self-supplied assumption. |
| `material_qualification` | The user adds a fact or limitation that weakens evidence, conditions a recommendation, or changes feasibility. |
| `reasoning_objection` | The user directly disputes the sufficiency, applicability, or direction of the reasoning or advice. |

The old catch-all labels `concern`, `value`, `evidence_request`, and
`timing_pressure` are not accepted by the v2 validator. The old label
`correction` is also rejected so that a v1 artifact cannot silently satisfy the
v2 contract.

## Explicit exclusions

- Standalone questions and requests belong to the question-trajectory reader.
- Mere acknowledgement, agreement, gratitude, or repetition of the
  assistant's conclusion is not counter-pressure.
- A generic emotion, downside, worry, value, or background fact is excluded
  unless the probabilistic reader judges that it performs one of the three
  revised roles.
- Being important to the decision is not sufficient by itself.

These exclusions are semantic instructions to the LLM, not Python keyword
rules.

## Cross-family overlap

A user statement can simultaneously qualify reasoning and expose an evidence
boundary or constraint. The pressure reader must not omit it merely because
another family could also preserve it. The LLM assigns the counter-pressure
role; deterministic code only validates the declared label, exact source span,
turn, schema, cap, and event identity.

This resolves the Case 11 conflict. `None of them have committed to actual
engagements.` may be both an evidence boundary and a material qualification of
the user's implied pipeline. Cross-family overlap is allowed without asking
Python to infer either role.

## Locked gold mapping

| case | locked evidence | v2 role |
| --- | --- | --- |
| 02 | `This isn't my decision alone.` | `premise_correction` |
| 08 | `we haven't had the real conversation about what 3 nights a week away actually looks like for four-plus years` | `material_qualification` |
| 11 | `None of them have committed to actual engagements.` | `material_qualification` |

The labels above are the source-first research hypothesis for the next test.
They are not deterministic classification rules and are not added to the gold
files before evidence is collected.

## Review of the prior selections

### Case 02

The old reader mixed genuine counter-pressure with standalone questions and
acknowledgements. Statements about the structural promotion problem, the
startup base rate, the joint household decision, the startup role's limited
negotiability, and Option A's genuinely different scope plausibly meet the new
target. Questions about choosing Option C, spouse assent, and the seven-day
schedule are already represented by question, evidence, or constraint readers.
The user's repetition of the assistant's optionality conclusion is not itself
counter-pressure.

### Case 08

The initial `greedy or smart` statement is the opening question, not
counter-pressure. Removing that catch-all concern creates room for the missed
household-conversation qualification without increasing the eight-item cap.
Later statements about handoff feasibility, Chicago travel, negotiation risk,
Priya, the non-compete, and missing role diligence remain plausible
qualifications or objections. The LLM must select among them under the revised
definition; no deterministic salience rule is introduced.

### Case 11

The missing `None ... committed` span is a material qualification of the
pipeline premise. `You're pushing back on the basic premise` is a direct
reasoning objection, and `The conversations aren't a pipeline` is a
self-correction. The later LOI, fractional-bridge, and launch-timing questions
belong to question trajectory. `Ouch. You're right.` is acknowledgement, not a
reasoning event.

## Experimental isolation

The next preflight does not rebuild a six-reader artifact. It runs only the v2
counter-pressure reader and compares it with the locked SK3 pressure evidence.
The SK3 constraint, stance, dropped-thread, question, option, and evidence
artifacts remain byte-for-byte unchanged.

This changes the cost and causal clarity:

- first SK4 ablation: 54 successful calls plus retry calls;
- v2 one-case preflight: three successful calls plus bounded retries;
- later three-case v2 ablation, only if the preflight passes: nine successful
  calls plus bounded retries.

## One-case preflight

Case 08 remains the locked case because it produced the clearest stable-but-
wrong failure. The prepared contract is in `preflight-contract.json`.

The one-case gate requires:

1. The locked household-conversation qualification is recovered in all three
   repeats.
2. It is therefore stable across the three repeats.
3. Every returned candidate passes exact-source validation.
4. Each artifact contains exactly one semantic reader call.
5. No old catch-all kind is returned.

A pass authorizes only the pressure-only three-case ablation. It does not
promote SK4 or authorize the full corpus, SK5, graph integration, or live use.

## Local verification

The v2 reader has a separate prompt and artifact schema, preserving the failed
SK4 prompt for reproducibility. A deterministic Case 08 fixture confirmed that
the new path:

- makes exactly one reader call;
- accepts the locked household qualification as `material_qualification`;
- accepts the non-compete correction as `premise_correction`;
- rejects the old catch-all `concern` kind while preserving that rejected
  proposal in the candidate ledger;
- validates exact source spans and leaves graph/runtime behavior untouched.

This local check proves plumbing and evidence custody only. It supplies no
evidence that the model will follow the revised semantic target; that is the
purpose of the paid three-call preflight.

The focused v2 tests passed 29/29. After adding the deterministic temporal
scorer test, the complete non-network repository suite passed 3,869 tests with
one existing skip and 93 subtests when run under the
project's Python 3.12 runtime. `tests/test_stability_check.py` remains excluded
because it performs unmocked external embedding calls.

## Paid preflight update

The approved three-call Case 08 preflight failed the locked recall and
stability gates. It passed exact-source validity, one-call isolation, and the
new label contract. Full results are in `case08-paid-preflight-result.md`.

The reader selected 11 narrow material qualifications rather than filling the
eight-item cap with generic concerns. It nevertheless missed the locked turn-2
household-conversation quote in every repeat. Two repeats selected a later,
stronger husband-alignment qualification, which is a post-run concept-coverage
hypothesis but receives no locked recall credit.

Do not proceed to the three-case v2 ablation. The next work is a no-cost review
that separates first-introduction coverage from prospectively declared
alternative-span concept coverage.
