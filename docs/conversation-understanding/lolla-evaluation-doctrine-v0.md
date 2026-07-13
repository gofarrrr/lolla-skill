# Lolla Evaluation Doctrine v0

Status: active development doctrine  
Date: 2026-07-10

## North-star question

Lolla should eventually answer this question:

> Does the system preserve the conversation, expose both direct and off-frame
> structural pressure, require accountable consideration without forcing
> agreement, and preserve enough process evidence for a later reader to
> understand what happened?

No single metric answers that question. Lolla is a chain of capabilities, and
a polished reconsideration cannot compensate for missing source custody or a
misrepresented conversation.

## Product capabilities

| capability | question | current evaluation unit |
| --- | --- | --- |
| C0 — capture and custody | Do we possess the complete conversation and exact evidence? | transcript hash, source-span validity, candidate ledger, failure artifacts |
| C1 — system semantic coverage | Did the packet preserve the material concept somewhere? | exact source recovery across all semantic families |
| C2 — semantic placement | Did the LLM assign the concept to a useful role or family? | family-aligned recovery, cross-family overlap, source review |
| C3 — temporal fidelity | Did we preserve first introduction, revision, strengthening, and unresolved state? | first-introduction and later-event coverage, trajectory stability |
| C4 — reasoning abstraction | Did we derive useful reasoning patterns without letting facts determine graph traversal? | reasoning-pattern packet coverage and source traceability |
| C5 — deterministic pressure | Did the graph reproducibly recall direct and off-frame candidate lenses without claiming final relevance? | deterministic replay, graph coverage, protected-edge survival, selection rationale |
| C6 — reconsideration utility | Did the consumer seriously consider the portfolio, expose novel pressure, and improve, preserve, or explicitly reject the prior reasoning without forced absorption? | blinded comparison, novelty exposure, disposition quality, decision-relevant delta, false-stand-down and over-absorption review |
| C7 — receipt and transfer | Can a fresh session reconstruct the conversation, transformations, choices, and uncertainty? | receipt completeness, self-explanation test, source-to-output trace |
| C8 — operability | Is the gain worth its calls, tokens, latency, and failure surface? | successful calls, retries, token totals, wall time, artifact completeness |

The current semantic-kernel work evaluates C0-C3. It does not prove C4-C7.

## Probabilistic and deterministic boundary

LLMs should perform the semantic work:

- interpret messy conversation language;
- decide whether two spans express the same material concept;
- identify corrections, qualifications, questions, stances, options, unknowns,
  dropped threads, and temporal relationships;
- decide which reasoning patterns should enter the fact-stripped packet;
- preserve ambiguity when more than one reading is plausible.

Deterministic code should perform custody and replay work:

- validate exact source quotes, speakers, turns, schemas, and allowed labels;
- preserve every returned candidate and terminal reason;
- quarantine exact duplicate identities without merging semantic roles;
- verify hashes, references, call counts, retries, budgets, and artifact chains;
- traverse the mental-model graph reproducibly after semantic patterns exist;
- score only against evidence or alternatives declared before a future run.

Python must not use keywords, hand-built rules, or layered gates to infer the
meaning that the LLM failed to return.

## What good looks like at the current stage

### Non-negotiable custody

- The authoritative conversation remains available one-to-one.
- Every accepted semantic event is traceable to exact source evidence.
- Invalid, overflow, duplicate, unsupported, and failed candidates remain
  observable rather than disappearing.
- A failed provider or schema call cannot masquerade as a valid empty result.
- Reused controls and scoring contracts are hash-locked before paid calls.

Any custody failure blocks promotion regardless of semantic recall.

### Semantic adequacy

- Material concepts are recovered across the complete packet, not merely in
  one preferred reader.
- Family placement is measured separately because a concept can be present but
  unusable for a particular consumer.
- Important cases and dimensions have explicit floors; a high average cannot
  hide a zero in a critical stratum.
- Noise and selection pressure are visible. Raising a cap or returning more
  events is not automatically an improvement.

### Temporal adequacy

- Concept coverage for downstream reasoning and chronology for the receipt are
  separate measures.
- A later, stronger statement can supply the concept but cannot retroactively
  replace where the issue first entered the conversation.
- First introduction, later strengthening, reversal, and unresolved state are
  kept distinct when the product needs the process history.

### Stability

- Three repeats are an initial variance signal, not production reliability.
- Stable wrong output is failure, not quality.
- Stable system-level coverage can coexist with unstable family placement;
  both facts should remain visible.

### Downstream usefulness

This is not yet established. Before claiming reasoning quality, Lolla will need
a blinded test showing that its packet and graph pressure produce a useful,
non-echoing reconsideration without inventing certainty or simply adding prose.

Evaluation must keep three stages separate:

- **candidate discovery:** source-valid, structurally different possibilities
  may remain noisy and low-fit;
- **private consideration:** the consumer uses, rejects, defers, or guards with
  a concrete reason;
- **public revision:** visible friction must be earned, actionable, and
  proportionate.

The public actionability rule must not become an upstream relevance filter.
Most edge candidates may be rejected after inspection without making their
preservation a failure.

## Scorecard, not score

Every experiment should report a vector:

1. exact-source validity and custody completeness;
2. system-level concept coverage;
3. family-aligned semantic placement;
4. temporal first-introduction and later-change coverage;
5. repeatability and case/dimension floors;
6. noise, candidate counts, and cap pressure;
7. downstream utility when that stage is reached;
8. calls, retries, tokens, latency, and preserved failures.

Lolla must not issue a single quality badge or “proof of reasoning” number.
The receipt is evidence of process, not proof that the reasoning was good.

## Failure taxonomy

| code | failure | typical response |
| --- | --- | --- |
| F0 | conversation capture or archive loss | stop; repair custody before semantic work |
| F1 | fabricated, invalid, or untraceable evidence | stop; repair deterministic validation or prompt quoting |
| F2 | material concept omitted everywhere | review semantic target; use a focused LLM job only if the gap generalizes |
| F3 | first introduction, revision, or strengthening lost | review temporal prompt/representation; do not substitute a later span silently |
| F4 | concept present in another valid family | fix evaluation or consumer mapping before adding a reader |
| F5 | selection unstable across repeats | inspect prompt ambiguity, model capability, and cap pressure |
| F6 | stable but wrong selection | repair the semantic target or ontology; do not celebrate repeatability |
| F7 | cap saturation or verbosity crowding | narrow the semantic job before raising limits |
| F8 | gold/scorer mismatch | freeze the run as failed; repair future evaluation prospectively |
| F9 | packet does not improve reconsideration | stop upstream optimization and test consumer needs directly |
| F10 | cost or architecture exceeds demonstrated value | simplify, reuse controls, or stop the path |
| F11 | provider/schema failure or missing call evidence | stop; persist terminal call evidence, mark cost unknown, and repair operability before semantic claims |

After the same semantic miss survives two prompt-only variants on the same
case, prompt tuning stops. The failure must be reclassified before another paid
call. The Case 08 pressure work reached that stop rule.

## Evaluation evils to avoid

- **Goodharting one metric:** optimizing exact-span recall while losing
  chronology, signal-to-noise, or usefulness.
- **Family tunnel vision:** treating a reader miss as a product miss when the
  concept exists elsewhere—or treating cross-family presence as correct role
  assignment.
- **Retroactive gold repair:** adding a model-selected span after a run and
  then declaring the run passed.
- **Case-specific prompting:** naming the expected spouse, pipeline, deadline,
  or other fixture detail in a supposedly general prompt.
- **Deterministic semantic gates:** using keywords or brittle state machines to
  decide meaning in messy conversation.
- **Verbosity as coverage:** increasing caps or event counts until recall rises
  while utility and precision decline.
- **Repeated tuning on the same three cases:** converting diagnostics into the
  training set and losing any estimate of generalization.
- **Composite luck:** pairing independent repeats post hoc so complementary
  misses appear stable.
- **False quality badges:** presenting token counts, call counts, or receipt
  completeness as proof of deep reasoning.
- **Architecture before evidence:** adding agents, correction loops, readers,
  or graph stages before a bounded failure requires them.
- **Premature relevance pruning:** deleting strange or low-fit pressure before
  the final reasoner can inspect and disposition it.
- **Context dumping:** injecting all source-valid material at equal weight and
  mistaking custody for attention-neutrality.
- **Compactness Goodhart:** optimizing packet size while losing protected
  off-frame possibility.
- **Answer-delta monoculture:** treating unchanged advice as failure even when
  the system adds a new falsifier, verification target, frame, or accountable
  rejection.
- **False stand-down:** allowing an active-surface or complexity gate to hide a
  rare but decisive edge lens.
- **Unknown-unknown fabrication:** turning a useful break-scenario question
  into an unsupported claim about the external world.
- **Semantic non-consideration laundering:** recording a readable duplicate,
  already-covered, or irrelevant candidate as `not_considered` instead of a
  grounded rejection; `not_considered` is reserved for technical custody
  failure.

## Experiment and spending ladder

1. State one falsifiable hypothesis and lock the source, prompt hash, scorer,
   controls, and stop rule.
2. Validate plumbing locally with deterministic fixtures; make zero paid calls.
3. Run one diagnostic case, normally three repeats and one focused call per
   repeat.
4. If the locked product and custody gates pass, test a small multi-case set
   without changing gold or prompts.
5. Use a holdout case before a full-corpus call budget.
6. Run the full corpus only when the result can change an integration decision.
7. Stop paid work when the same failure survives two prompt variants, when the
   scorer is wrong, or when the product consumer is not yet defined.

Paid calls answer empirical questions. They must not be used to compensate for
an unclear ontology, missing scorer, or undocumented definition of quality.

## Current evidence

### Twelve-case SK3 corpus

| measure | family-aligned | system-level |
| --- | ---: | ---: |
| weighted exact-span recall | 0.552 | 0.716 |
| stable observations | 46 / 102 | 63 / 102 |

Fifty observation/run opportunities were recovered only through a family not
mapped to the gold dimension. This does not prove correct semantic placement.
It proves that the old family-aligned score understated how much source
material the packet preserved.

The largest deltas were:

- dropped-thread source material: 0.242 family-aligned versus 0.697 anywhere;
- user correction/pressure source material: 0.521 versus 0.813;
- evidence boundaries: 0.389 versus 0.528.

For dropped threads especially, “span exists elsewhere” does not mean the
system recognized that the thread was dropped. C1 improved; C2 remains a real
gap.

### Three-case SK3 repair versus broad SK4

| arm | family recall | system recall | family stable | system stable |
| --- | ---: | ---: | ---: | ---: |
| SK3 repair | 0.547 | 0.760 | 13 / 25 | 19 / 25 |
| broad SK4 | 0.493 | 0.747 | 11 / 25 | 17 / 25 |

Broad SK4 does not beat the retained SK3 base at either product or placement
level. The pressure prompt variants also failed their temporal gates. Therefore
the evidence does not support another pressure prompt, a new reader, or SK4
promotion.

### Source-reviewed pressure subset

The prospective observation contract currently contains 16 source-reviewed
pressure observations across all 12 cases; the other 86 legacy observations
remain pending and cannot be used for promotion.

On that reviewed pressure subset, retained SK3 achieved:

- reasoning concept anywhere: 0.833 weighted recall, 12 / 16 stable;
- concept in an acceptable semantic role: 0.792, 11 / 16 stable;
- first introduction: 0.750, 10 / 16 stable;
- later strengthening: 0.889 across the three eligible observations, 2 / 3
  stable;
- complete temporal requirement: 0.750, 10 / 16 stable.

The clearest total concept omission is an unresolved-decision self-correction
in Case 07. The raw transcript remains complete, but the semantic packet never
captures the user's admission that they keep claiming to have decided when
they have not. This is a semantic-index and source-attribution gap, not a C0
capture failure.

### First strong-control downstream pilot

The first downstream pilot used the enterprise-beta case and exactly two fresh
`openai/gpt-5.1-chat` calls: a strong neutral reconsideration control and the
same prompt plus Lolla's source-grounded pressure packet. Both calls passed the
source/schema red lines.

Blind provisional review found no material winner. Both answers produced the
same likely next action and the same four structural changes: firmer
participation/publicity commitment, capacity validation, private-before-public
sequencing, and success or stop criteria before launch. The treatment was
slightly more explicit about reversibility and stop conditions but added no
unique decision-relevant delta. It also used more completion tokens.

The positive-case success rule therefore failed. Do not repeat or retune this
case. The result shows that conspicuously weak original advice can be repaired
by a strong fresh reconsideration without Lolla-specific leverage. It does not
show that Lolla lacks value on harder or quiet cases.

The complementary quiet pilot used an independent-consulting conversation
whose existing answer already carried the main launch pressure. Both arms
preserved the same likely action and stayed compact. The Lolla treatment was
better calibrated: it retracted unsupported conversion, timing, and retainer
precision, kept fractional work as an option to test rather than an expected
fallback, and used only 13 more completion tokens than control. Blind
provisional review preferred treatment for calibration, not for action change.

This quiet-case success is provisional and human review remains pending. It
shows one example of responsible smallness, not a reliable stand-down rate.
Across both pilots, four generation calls used 8,007 tokens and an estimated
$0.02594 under the repository's 2026-05-25 pricing table; no evaluator calls
were made.

The Case 07 semantic-overlay counterfactual then compared three fresh arms:
transcript-only control, all 27 actual SK3 selected events, and those events
plus the one reviewed missing self-correction. All arms recovered that Seattle
was undecided because the full transcript remained available. Blind
provisional ranking was control approximately equal to oracle, both better
than actual overlay.

The actual overlay failed to explicitly take back the assistant's “Seattle is
the root decision” frame. Restoring the omitted user correction repaired that
weakness but did not beat the transcript-only control. Therefore a full
semantic-event overlay is blocked for reconsideration. The semantic inventory
remains potentially useful for audit, navigation, and receipt fidelity. A
smaller consumer-specific pressure projection must earn downstream value
against the strong control.

The counterfactual used three generation calls, 13,077 tokens, and an estimated
$0.03330; it used no evaluator calls or retries.

## Current development decision

1. Retain the five-reader SK3 repair as the offline base and keep the live graph
   and runtime unchanged.
2. Stop paid extraction/pressure-prompt tuning and do not add another reader,
   correction loop, or deterministic semantic gate.
3. Keep the full semantic overlay, expanded portfolio handoff, and pattern-only
   routing in shadow.
4. Record Batch 1 as directional treatment value with a failed shared
   unsupported-claim red line; do not rerun it.
5. Record Batch 2 as correct protected-edge stand-down with failed exact
   pressure identity and disposition-effect consistency; do not rerun it.
6. Record Batch 3 as a successful mechanical fact boundary and failed semantic
   invariance/target test; do not retune its fixtures.
7. Harden exact pressure IDs, references, and disposition custody before a new
   downstream case. Deterministic code may enforce structure; effect
   consistency requires semantic review against the actual output.
8. Treat unresolved weakness in the joint conversation trajectory as the next
   consumer-specific reasoning target. Actor-specific observations remain
   audit evidence and do not automatically become graph seeds.
9. Run the next paired downstream test only on a new case with both arms frozen
   before either call, using a strong fresh reconsideration control.
10. Retest the clarified pattern target on new invariance pairs and preserve
    the original Batch 3 failure.
11. Measure novel exposure and consideration integrity separately from answer
    delta; a grounded rejection or private guardrail may be useful without
    changing the public action.
12. Permit minimal promotion only when exact custody, source fidelity,
    non-forced consideration value, boundary stability, operability, and exact
    run review pass together.

### Accountability-cycle update

The next cycle produced three separate reads:

1. Structural pressure custody improved and is retained. Exact treatment IDs,
   control isolation, full ledger-skeleton identity, output-path preflight,
   quote-delimiter-only literal recovery, and transitive hash locks are
   mechanical responsibilities.
2. Joint-process routing passed the new fact-invariance and repair-sensitivity
   product surfaces, but the frozen experiment remains failed because one
   non-active audit-history label missed its exact prospective gold. Treat this
   as F8 and separate routing status from history-label scoring next time.
3. No paired downstream result exists. Case 02 failed artifact persistence and
   Case 08 failed the frozen quote gate after its one allowed repair. Neither
   entered the pipeline or was rerun.

The prospectively frozen Case 12 non-holdout smoke then passed output-parent
preflight and complete 2/2-turn capture, but failed admission. The provider
boundary returned an empty parsed object after approximately 207 seconds; the
extractor rejected the missing required fields and persisted an error artifact.
Its early-return path did not persist the call sidecar, so calls, tokens, model
attribution, and cost are unknown. The aggregator's numeric zero is not evidence
of zero cost. Classify this as F11, do not rerun Case 12, and do not authorize
another holdout.

The next engineering gate is transactional call custody on every terminal
extraction path, honest unknown-cost semantics, and a frozen outer wall-clock
ceiling. After provider-free failure-path tests pass, one different designated
non-holdout may receive a new frozen smoke contract. Only a clean smoke may
authorize another paired holdout.

That deterministic repair is now implemented and provider-free verified.
Extraction call evidence is atomically persisted before semantic early exits;
call attempt, record persistence, and admissible extraction are separate
states; missing usage becomes null/unknown; and smoke contract v1 freezes both
provider and outer wall-clock timeouts. No prompt, semantic gate, graph path,
or Step 6 behavior changed. This closes the engineering repair gate only. It
does not retroactively pass Case 12 or authorize a paired holdout; the next
separate goal is one newly frozen non-holdout smoke.

The newly frozen Case 01 contract-v1 smoke subsequently passed every admission
gate in one call: full 6/6 capture, three exact quotes, complete transactional
call custody, compatible served-model attribution, 2,087 tokens, `$0.001190`
estimated cost, 2.618 seconds wall time, no repair, and no retry. Because Case
01 is heavily reused, this is operability evidence only. It authorizes planning
and freezing one untouched Stage A extraction-plus-pipeline contract; it does
not authorize a paired downstream call, graph promotion, or runtime change.

The first such Stage A attempt used a hash-selected Case 05 and remains failed.
The actual extraction and pipeline executions completed inside all observed
resource and custody envelopes, but the frozen runner and sealer disagreed on
the field name for extraction exit success. Classify this as F8, not provider
failure and not semantic evidence. Preserve the failed gate, prohibit a same-
case rerun or reseal, and repair the field contract prospectively with a real
runner-to-sealer integration fixture.

The run also preserved `lane3_all_dropped` and zero main delta findings. These
are unresolved diagnostics, not proof of correct stand-down or false stand-
down, because the failed Stage A contract blocks preliminary semantic review.
The next work remains custody repair followed by downstream discrimination and
ontology gardening, not architecture growth.

The repair now imports one shared execution-gate schema into runner and sealer,
rejects the legacy field, and passes a provider-free integration test using the
runner's actual envelope. The next mechanically ranked Case 10 then passed all
Stage A gates with complete capture, quote, provider, embedding, usage, cost,
private-table, and V60 evidence.

Its preliminary pressure review passes on three trace-supported questions, not
on volume. The review gives no novelty credit to regret, buffer, risk, or spouse
alignment labels already present in the original conversation. It admits only
an evidence-sized rather than invented buffer, a separation of regret framing
from probability/economics, and a clean-sheet all-in acquisition test. Unsafe,
forcing, duplicate, and unsupported candidates remain explicit rejections.

Gate 4 contract construction is now authorized. Both calls remain blocked
until one contract freezes both arms before either output exists.
