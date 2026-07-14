# Lolla simulated reliability corpus V1

Status: calibration complete; transfer runtime sealing in progress  
Date: 2026-07-12

## Goal

Build the first balanced, naturalistic corpus that can test whether Lolla's
complete reasoning-pressure loop behaves reliably across important simulated
conversations.

V1 is a reliability corpus, not user evidence. It may expose omissions,
misplacement, instability, false pressure, forced absorption, unsupported
precision, and transfer failures. It cannot show that real people find Lolla
useful or make better decisions with it.

## Product question

Across consequential, ambiguous, multi-turn conversations, can Lolla:

1. preserve what actually happened and how the position changed;
2. abstract reasoning patterns without letting deterministic code interpret
   messy language;
3. preserve broad deterministic pressure, including strange candidates;
4. give a fresh reasoner useful possibilities without forcing agreement;
5. stand down when the original reasoning is already adequate;
6. turn unknown unknowns into questions rather than invented facts; and
7. leave a receipt from which a cold reader can reconstruct both the work and
   its limits?

## Corpus shape

V1 contains 20 simulated conversations.

### Calibration set: 8 existing cases

The calibration cases were already used during system development. They may be
used to repair prompts, schemas, validators, and review instructions. They may
not support generalization claims.

- five cases from `research/designed-ambiguous-pool-v1-2026-07-10/`;
- three cases from `research/stance-object-v41-fresh-corpus-2026-07-12/`.

The retailer and library minimum-loop cases remain separate mechanistic
fixtures. They are excluded because their dialogue states the intended issue
and, in the quiet cases, the desired stand-down too directly.

### Prospective transfer set: 12 new cases

The transfer cases are authored after this contract is fixed but before any V1
pipeline call. They must not be used to change prompts, architecture, model
choice, candidate policy, or evaluator instructions after the set is frozen.
If a transfer case exposes a defect, preserve the result and repair only a
future corpus version.

The set is balanced by intended public behavior:

| behavior | count | meaning |
| --- | ---: | --- |
| pressure expected | 6 | at least one material question, lens, or test should add something the strong baseline did not already operationalize |
| stand-down expected | 4 | the conversation already contains proportionate safeguards; novelty alone must not create public friction |
| park expected | 2 | the useful result is a bounded unresolved question or evidence request, not a directional recommendation |

These are source-review strata, not answer keys. No exact mental-model identity,
wording, recommendation, or answer delta is required.

## Importance and realism contract

Every new transfer case must:

- concern a decision with meaningful human, organizational, financial,
  scientific, or public-service consequences;
- contain twelve user/assistant turn pairs, so a provisional view can be tested
  by later evidence rather than serving as the ending;
- introduce consequential information after an initial view has formed;
- include at least two genuine user corrections, resistances, or narrowing
  moves;
- preserve at least two legitimate values or options;
- contain a strong, useful assistant rather than a strawman;
- end with a position that is actionable, conditional, or genuinely unresolved;
- avoid planted mental-model names, Lolla vocabulary, evaluation language, and
  conspicuous descriptions of the intended blind spot;
- avoid invented expert statistics and avoid asking the system to supply
  medical, legal, political-persuasion, emergency, or investment advice; and
- remain understandable without external factual research.

The twelve pairs must not be twelve repetitions of one dilemma. Each case must
include at least three distinct conversation movements: initial framing,
material complication or resistance, a provisional position, later evidence
or consequence that reopens the reasoning, and a final position that shows
what changed and what did not. At least one earlier thread must be dropped and
later recovered naturally.

Quiet cases must not announce that nothing remains unresolved. Their adequacy
must be inferred from the reasoning itself. Pressure cases must not name the
desired challenge in the final turn. Park cases must contain a real decision
boundary rather than generic uncertainty.

## Transfer scenario mix

The fixed mix covers:

1. municipal flood-infrastructure procurement;
2. hospital discharge-transport operations;
3. hiring a high-status senior executive;
4. single-sourcing a critical manufacturing component;
5. a university AI tutoring pilot;
6. industry funding for a research laboratory;
7. a worker-cooperative scheduling trial;
8. a museum timed-entry trial;
9. a staged enterprise software migration;
10. a nonprofit restricted-funding renewal;
11. a family elder-care relocation decision; and
12. a newsroom distribution partnership.

The source-review disposition for each case is stored outside the conversation
and is never supplied to Lolla or either fresh reasoner.

## Evaluation contract

V1 uses a scorecard, never a composite score or quality badge.

For each case record:

- raw-capture and quote validity;
- material-concept coverage across the packet;
- semantic role and temporal placement;
- abstraction traceability;
- deterministic replay and candidate custody;
- candidate dispositions: adopted, useful question, already covered,
  irrelevant, deferred, or technical non-consideration;
- control-only contribution, pressure-only contribution, overlap, and harm;
- unsupported factual or numeric specificity;
- false stand-down and forced-absorption findings;
- cold-reader reconstruction;
- calls, retries, model, tokens, cost, latency, and preserved failures.

The paired comparison uses the same full conversation and same fresh-reasoner
contract:

- control: conversation without Lolla pressure;
- pressure: conversation plus the complete candidate packet permitted by the
  current constitution.

Order is randomized and review is blinded. A useful pressure result may leave
the recommendation unchanged if it adds a material falsifier, boundary,
question, contingency, or accountable rejection. A changed answer is not
automatically an improvement.

## Experiment ladder

1. Author and validate all 12 transfer sources locally with zero provider calls.
2. Freeze source bytes, source-review notes, prompts, schemas, validators,
   model/provider routing, budgets, stop rules, and scorer instructions.
3. Use calibration cases to repair only defects visible before transfer.
4. Seal the runtime contract.
5. Run a small calibration sentinel set before authorizing the transfer calls.
6. Run the 12 transfer cases without tuning between cases.
7. Repeat a predeclared cross-stratum sentinel subset to measure variance.
8. Perform blinded model review calibrated against human review, plus cold-reader
   reconstruction.
9. Publish results and failures together. Any repair becomes V2 work.

## Stop rules

Stop and preserve the result when:

- source custody or provider-call evidence is incomplete;
- a validator contradicts the frozen prompt or schema;
- a failed call is indistinguishable from a valid empty result;
- the same semantic failure survives two prompt variants on calibration;
- a transfer failure tempts a prompt, scorer, model, or architecture change;
- unsupported precision or fabricated external facts enter the public answer;
- provider cost or activation surface exceeds the frozen budget; or
- the pressure arm forces candidates rather than considering and dispositioning
  them.

## Promotion boundary

V1 passes as a reliability experiment only if its artifacts make system
behavior inspectable across all three public-behavior strata. It does not pass
because most outputs sound thoughtful. No product integration or usefulness
claim follows automatically.

## Pre-call source correction

The first source draft used seven user/assistant pairs, matching the older
minimum for designed ambiguous fixtures. Founder review correctly found that
the cases were still too compressed to resemble the advanced conversations
Lolla is meant to preserve. No pipeline, reasoner, scorer, or provider call had
used the transfer set. The draft manifest is therefore not an evaluation
artifact. V1 source authoring was reopened once to expand every transfer case
to twelve pairs before the actual freeze.

## Frozen source result

- 8 existing calibration cases;
- 12 prospective simulated transfer cases;
- 24 messages and 12 user/assistant pairs per transfer case;
- 288 transfer messages and 21,938 words in total after naturalization;
- individual transfer cases range from 1,692 to 2,011 words;
- 6 pressure-expected, 4 stand-down-expected, and 2 park-expected
  source-review strata;
- 0 provider-authored outputs admitted and 0 reasoner, evaluator, or Lolla
  pipeline calls used on the corpus;
- 12 rejected source-editor calls preserved separately at a provider-reported
  cost of $0.0476685; and
- 10 focused provider-free tests passing at final source freeze.

This was the structurally expanded checkpoint, not the final V1 freeze. Founder
review then identified a remaining source-quality defect: turn lengths and
voices were still unusually uniform and polished. The manifest was reopened
before any pipeline use for a naturalism correction.

## Naturalism correction

Synthetic does not mean benchmark-like. V1 should approximate a real user/LLM
conversation as closely as its authored-source limitation permits.

The expanded checkpoint had suspiciously uniform messages: per-case user-turn
length variation was only 0.07–0.14 coefficient of variation and assistant-turn
variation was 0.07–0.16. Most user turns were 54–107 words and most assistant
turns were 45–81 words. That regularity is itself a source defect.

Before final freeze, every transfer case must receive a qualitative naturalism
pass that introduces:

- meaningful short, medium, and long turns rather than mechanically equal
  paragraphs;
- partial answers, clarifications, and occasional delayed responses;
- at least one useful assistant overreach or incomplete framing followed by a
  grounded repair;
- a user voice distinguishable from the assistant voice;
- uneven pacing and a naturally recovered thread;
- no fake spelling mistakes, artificial incompetence, planted blind spots, or
  loss of the consequential decision structure.

Length variation is a diagnostic, not a quality score. Final admission still
requires human-style source review of the whole conversation.

The naturalism correction is complete. A frozen 12-call Gemini-through-
OpenRouter source-editor attempt produced 11 structured proposals, zero shape
passes, one invalid response, and zero admitted outputs at a provider-reported
cost of $0.0476685. The failure is preserved without retry or a lowered gate.

Provider-free editing then produced twelve separate naturalized variants while
leaving the semantic skeletons immutable. All twelve pass deterministic shape,
anti-leakage, semantic-preservation, and whole-conversation naturalism review.
Each contains a grounded assistant repair and a naturally recovered thread.
The admitted sources remain synthetic and same-project-reviewed.

After that correction, the next boundary is the runtime experiment contract.
The constitutional gap audit requires three arms: transcript-only, direct
pressure, and graph-expanded pressure. Prompts, schemas, provider/model routing,
call budgets, repetitions, three-arm instructions, blinded review, and stop
rules must be frozen before the first calibration sentinel call. Transfer
sources may not be used for tuning after this point.

## Calibration status — 2026-07-12

Provider-free work now preserves all 20 corpus inputs plus one explicit quiet
control, supports bounded multi-record role portfolios, creates direct and
three-slot graph ledgers without semantic filtering, packages transcript-only,
direct-pressure, and graph-expanded arms, and records deterministic stand-down.

Current-practice review selected Gemini 3.5 Flash through OpenRouter's exact
Google Vertex/ZDR route. Calibration then found and prospectively repaired:

1. Google rejection of the paired strict schema by using JSON-object transport
   with the unchanged schema in the prompt and unchanged local validation;
2. a mechanism token ceiling that truncated JSON after mandatory reasoning;
3. missing assistant-side evidence in joint-mechanism interpretation;
4. a role-only evidence contract that could not cite assistant repairs; and
5. an inherited join that discarded valid multiple starting threads.

Those repairs are preserved in separate contracts and runs rather than hidden
as retries. The current A6 boundary remains failed. Even with every assistant
message visible and separately citable, the mechanism interpreter classifies
`counterpressure_acknowledged_not_integrated` as unresolved while citing the
final assistant turn that already operationalizes the concern. The interface
conflates an unresolved user concern with whether the vanilla answer covers it.

The mechanism-state conflation was repaired by preserving separate user-process
status, vanilla-answer coverage, and routing disposition. Calibration then
passed source-defensible product-scope and quiet-control stand-downs and a
creative-partnership pressure route. A task-specific low-reasoning mechanism
call repaired malformed JSON without changing semantics. The first graph arm
converted lenses into unsupported risk confidence; the probabilistic pressure
contract was corrected so mental models generate questions, alternatives, and
tests rather than case evidence. A two-call replay passed that targeted gate
while preserving graph noise and verbosity as evaluation findings.

Calibration is now sealed in
`research/simulated-reliability-v1-calibration-2026-07-12/a13/terminal-review.json`.
The next boundary is the untouched 12-case transfer run with no tuning between
cases. V1 is still a reliability experiment, not product authorization or a
usefulness claim.
