# Lolla Semantic Kernel v0.1 Plan

Status: SK1-SK3 offline base retained; live integration is blocked; exact
pressure custody and joint-process target gardening are the active next phase  
Date: 2026-07-10  
Governing boundary:
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`  
Evidence baseline:
`research/core-semantic-corpus-2026-07-09/core-semantic-corpus-result.md`

## Post-batch decision — 2026-07-10

The first fact-free reasoning-pattern shadow is complete. Its deterministic
sealer preserved source references, enforced the controlled vocabulary,
excluded case facts from routing, and replayed the declared seed mapping. Its
LLM interpreter failed same-reasoning/different-facts invariance and did not
reliably distinguish a locally present user pattern from an unresolved
weakness in the complete conversation.

Consequences:

- SK3, the pattern packet, and portfolio work remain offline/shadow;
- the failed fixtures are preserved and will not be prompt-tuned;
- the next ontology target is an unresolved weakness in the **joint
  conversation trajectory**;
- actor-specific semantic observations remain useful for audit and chronology
  but do not automatically become routing seeds;
- exact pressure identity and reference custody are hardened before another
  downstream call;
- no deterministic rule may infer whether an actor-local pattern remains
  unresolved after the complete conversation.

The first new-fixture retest is now complete. Fact-swapped conversations
produced identical active routing and repaired reasoning produced no active
seeds. The frozen contract nevertheless failed one exact history label:
`acknowledged_constraint_not_gated` was `not_observed` rather than
`resolved_in_conversation`. Both are non-active and source-defensible in that
fixture. No gold repair or rerun occurred.

Prospectively, evaluation separates routing surface (`active`, `edge`,
`non-active`) from audit-history exactness. Any allowed non-active history
labels must be frozen before calls. This does not promote SK3 or joint-process
routing into the live runtime.

## Objective

Improve Lolla's source-grounded understanding of a messy human–LLM
conversation without constructing a brittle deterministic conversation state
machine.

The v0.1 kernel should give LLMs better material, narrower semantic jobs, and
an ambiguity-preserving output contract. Deterministic code should make the
interpretations inspectable, reproducible, and safe to transport. It must not
infer the meaning that the semantic readers failed to produce.

## Why this is the next step

Across the 12-case corpus, the richer shadow reader beat compact extraction on
all 12 cases, but only 49 of 102 observations survived every repeat. The
weakest dimensions were:

- dropped or under-carried threads: 0.273 weighted recall;
- evidence boundaries: 0.472;
- user corrections and pressure: 0.479;
- assistant positions and revisions: 0.545.

The result validates the richer semantic representation but blocks graph
integration. The next task is to improve the probabilistic reading and its
structural harness, not to compensate with keyword rules or case-specific
gates.

## Product invariant

```text
semantic meaning       -> LLM/human judgment
evidence and custody   -> deterministic validation
graph candidates       -> deterministic recall/expansion
model applicability    -> LLM/human judgment
final decision         -> user/designated reasoning agent
```

Every implementation item below names both sides of this allocation.

## Non-goals

v0.1 will not:

- change live graph input or graph traversal;
- add case-specific rules, keyword classifiers, or topic templates;
- deterministically select the current question;
- deterministically assign stance or thread-treatment labels;
- build the reasoning-pattern projection or fact-leak linter beyond the
  existing design artifact;
- change Step 6 reconsideration;
- redesign the receipt, Teacher, SDK, or cross-run knowledge base;
- optimize model calls before semantic quality is demonstrated;
- treat corpus scores as runtime truth.

## Target architecture

The v0.1 semantic kernel is an append-oriented interpretation workflow:

```text
full source conversation
  -> semantic candidate ledger (LLM proposals, never silently pruned)
  -> mechanical validation and rejection records
  -> semantic interpreted view (LLM relations + ambiguity)
  -> pre-audit projection for future pattern work
  -> post-audit projection remains deferred
```

The ledger and interpreted view are different:

- The ledger preserves proposed source-linked observations, rejected
  candidates, competing labels, and reader/run identity.
- The interpreted view identifies the current best reading while retaining
  alternatives and uncertainty.

Deterministic reconciliation may join identical IDs, check chronology, and
record conflicts. It may not decide which interpretation is semantically best.

## Work sequence

### SK0 — Lock the hybrid boundary

Deliverables:

- canonical Markdown boundary;
- machine-readable boundary contract;
- regression test for allowed and forbidden deterministic responsibilities;
- links from the July core PRD, product blueprint, reasoning-pattern design,
  and corpus result.

LLM/human job:

- approve the semantic/structural allocation.

Deterministic job:

- validate that future plans and contracts retain the critical prohibitions.

Exit gate:

- there is one canonical rule and no active next-step document assigns
  semantic judgment to deterministic code.

### SK1 — Repair derivation provenance

Problem:

The live-constraint specialist validates multi-turn excerpts but the final IR
serializes only turn references and a synthesized label. A future reader
cannot inspect the exact components that justified the derivation.

LLM job:

- decide that several source excerpts jointly support a semantic item;
- state the derived interpretation and confidence.

Deterministic job:

- preserve every exact excerpt or start/end offset;
- verify each excerpt against the claimed turn and speaker;
- assign derivation and component IDs;
- reject routing eligibility when component evidence is missing;
- retain the rejected artifact and reason.

Implementation shape:

- extend derivation provenance rather than add a parallel evidence format;
- migrate shadow serialization only;
- keep old readers tolerant of turn-only historical events;
- give historical turn-only derivations an explicit
  `legacy_incomplete_provenance` status;
- do not regenerate semantic labels in Python.

Exit gate:

- 100% of new derivation components validate as exact source evidence;
- no synthesized derivation label can receive exact-span credit by itself;
- existing historical artifacts remain readable;
- graph and live runtime remain unchanged.

### SK2 — Introduce a lossless semantic candidate ledger

Problem:

Current specialist outputs jump directly from one model read to the current
event list. It is difficult to distinguish “not proposed,” “proposed but
invalid,” “valid but set aside,” and “selected as the current interpretation.”

LLM job:

- propose source-linked semantic candidates;
- provide primary and alternative interpretations where genuine ambiguity
  exists;
- state when evidence is too thin.

Deterministic job:

- preserve proposals, validation results, model/prompt identity, and rejection
  reasons;
- prevent invalid candidates from entering the current projection;
- retain them in the ledger;
- deduplicate only byte/identity-equivalent candidates;
- compute coverage and disagreement metrics.

Minimum candidate states:

- `proposed`;
- `validated`;
- `invalid_evidence`;
- `set_aside_semantically`;
- `selected_for_current_view`;
- `ambiguous_competing_read`;
- `not_supported_by_source`.

Exit gate:

- no proposed candidate disappears without a terminal state and reason;
- deterministic code does not merge candidates based on semantic similarity;
- the current view can be reconstructed from the ledger;
- the original source remains authoritative.

### SK3 — Repair question and stance trajectories

Problem:

The question reader often finds the initial question but selects an earlier
decision-choice question instead of a later operative implementation or
evidence question. The stance reader finds many valid spans but inconsistently
covers the decisive trajectory and relation labels.

LLM job:

- identify question events across the complete timeline;
- interpret each question's function and relationship to prior questions;
- propose the currently operative question or preserve multiple current
  questions when genuinely concurrent;
- identify assistant stance spans and interpret commitment, revision,
  qualification, condition, and deferral relations;
- explicitly mark relation ambiguity.

Deterministic job:

- verify all source spans;
- validate that relations reference existing events;
- check chronology without assigning semantic meaning;
- flag multiple `current` claims as disagreement, not automatically resolve
  them;
- measure span and label stability separately.

Prompt discipline:

- do not add rules such as “latest question mark wins”;
- do not privilege decision-choice questions over evidence or implementation
  questions mechanically;
- do not add per-case examples from the evaluation corpus;
- include full source turns and request exhaustive candidate reading before a
  bounded interpreted view.

Exit gate:

- operative-question corpus recall improves without deterministic question
  assignment;
- stance coverage improves without keyword relation rules;
- competing interpretations remain inspectable.

### SK4 — Repair user pressure, options, and evidence boundaries

Problem:

Material later corrections were often captured only as generic constraints or
missed as counter-pressure. Options, thresholds, and evidence boundaries had
high invalid-source rejection and inconsistent coverage.

LLM job:

- judge whether a source span acts as correction, concern, value, timing
  pressure, evidence request, option, condition, stop rule, weak evidence, or
  stated unknown;
- allow one source span to participate in more than one justified semantic
  role rather than forcing a single exclusive bucket;
- distinguish an explicit source fact from a derived relationship.

Deterministic job:

- validate source and allowed role vocabulary;
- preserve multi-role links;
- detect exact duplicate events;
- record invalid-source and overflow candidates;
- report which source turns received no semantic proposal, without inventing
  what they mean.

Exit gate:

- every source-invalid candidate is rejected with a reason;
- coverage rises across pressure, option/condition, and evidence-boundary gold;
- no regex, keyword, or case-type semantic inference is introduced.

### SK5 — Replace binary dropped-thread output with interpreted treatment

Problem:

Dropped-thread output was often repeatable but recovered the wrong thread. The
binary task asks for a conclusion before the system has represented the topic
and its later treatment.

LLM job:

- identify source-linked substantive topics;
- compare later treatment in context;
- interpret a topic as answered, active, superseded, contradicted,
  under-carried, unresolved, or ambiguous;
- explain the relationship with source-linked treatment evidence.

Deterministic job:

- validate topic and treatment sources;
- preserve the topic lifecycle and competing status judgments;
- check that `superseded_by` references an existing event;
- never infer under-carry from absence of string repetition.

Exit gate:

- the current view uses `thread_status_events`, not a standalone binary list;
- dropped/under-carried recall materially improves;
- status disagreement is visible rather than normalized away.

### SK6 — Rerun the locked corpus and decide

No source, gold annotation, case-specific example, or scoring implementation
may change after the v0.1 reader is frozen, except to fix a documented
mechanical evaluator defect that is reported separately.

Hard mechanical checks:

- all source hashes match;
- quote/offset validity is 100% for accepted span evidence;
- all derivations preserve exact components;
- all rejected candidates have reasons;
- no raw provider response or credential leakage;
- no graph or live runtime change.

Research promotion targets:

- weighted exact-span recall at least 0.75;
- every semantic dimension at least 0.60;
- every case at least 0.60;
- macro span and label repeatability at least 0.75;
- improvement is not concentrated in Case 01;
- source-first review finds no systematic ambiguity erasure.

These are evaluation targets, not runtime rules. Failure should produce a
diagnosis and another bounded semantic experiment, not deterministic patches
that force the score upward.

Exit decision:

- **pass:** freeze semantic-kernel v0.1 and proceed to reasoning-pattern
  invariance/fact-leak experiments;
- **partial:** preserve useful components and run one named repair experiment;
- **fail:** keep the current live path, archive v0.1 as research, and revisit
  the semantic representation.

Graph integration is not an exit option from this plan. Even a pass only
authorizes the pattern-projection experiment.

## Measurement contract

The corpus evaluation must report at least:

- exact-span and exact-derivation-component recall;
- stable and never-recovered gold observations;
- span repeatability and semantic-label repeatability separately;
- ambiguity preservation and disagreement rates;
- candidates proposed, invalidated, set aside, and selected;
- per-case floor, not only macro average;
- per-family invalid-source rate;
- model calls, tokens, retries, and wall time;
- source-first qualitative review of the largest failures.

No single measure may be presented as proof of reasoning quality.

## Anti-drift implementation review

Every pull request must include this table:

| Question | Required answer |
| --- | --- |
| What semantic judgment is made? | Name the LLM/human owner. |
| What deterministic operation is added? | Name its structural contract. |
| Can the code pass without understanding case prose? | Yes. |
| Are ambiguity and rejected candidates preserved? | Yes, with artifact refs. |
| Is any corpus example becoming a runtime rule? | No. |
| Does graph or live routing behavior change? | No for v0.1. |
| What falsifiable failure would cause rollback? | State it explicitly. |

## Risks and unknowns

- Narrower semantic calls may improve focus but increase cost and disagreement.
- An additive ledger may become bloated; compaction must remain a projection,
  not destructive history rewriting.
- Gold annotations may be incomplete or debatable.
- Exact-span evaluation may under-credit faithful synthesis.
- Multiple LLM readers may share the same blind spots and create false
  confidence through agreement.
- Better pre-audit semantics may still fail to produce better reasoning
  patterns or graph pressure.
- The controlled vocabulary itself may be too narrow for messy conversations.
- A polished audit or complete receipt may increase trust without improving
  calibration or decision quality; audit usefulness and trust inflation must
  be measured separately.
- Graph-of-thought, multi-agent, optimizer, memory, and broader neurosymbolic
  proposals remain research hypotheses. None enters v0.1 without a specific
  observed failure, a simpler baseline, an ablation, and a rollback path.

These are research questions. They are not reasons to replace semantic
judgment with deterministic approximation.

## Immediate first implementation slice

Begin with SK1 only:

1. extend derivation provenance to retain exact component excerpts/offsets;
2. keep historical turn-only derivations readable and explicitly incomplete;
3. update shadow serialization and the comparator;
4. add mechanical provenance tests;
5. rerun only the offline fixtures needed to verify custody;
6. stop for review before changing semantic prompts.

This first slice is intentionally structural. It repairs evidence custody
without trying to improve conversation meaning through deterministic code.

## SK1 implementation result — 2026-07-10

SK1 is complete in the offline shadow path:

- `DerivationProvenance` can retain stable derivation/component IDs, exact
  component quotes, and turn-relative offsets;
- the live-constraint specialist preserves every validated component instead
  of serializing only turn references and a synthesized label;
- incomplete component evidence remains inspectable with rejection reasons but
  is excluded from the decision-work routing projection;
- historical turn-reference-only derivations remain readable and are reported
  as `legacy_incomplete_provenance` by the shadow comparator;
- exact derivation components can receive exact-span evaluation credit, while
  the synthesized derivation label cannot;
- graph traversal, live lane input, runtime routing, and semantic prompts were
  not changed.

Verification:

- 131 focused IR, provenance, shadow, comparator, corpus, and boundary tests
  passed;
- 3,844 non-network repository tests passed, with 1 pre-existing skip;
- the legacy stability-check module remains outside that full run because
  several tests invoke OpenAI embeddings without mocking the client.

SK1 stopped here for review. After founder approval, work continued to the
lossless semantic candidate ledger described in SK2 below.

## SK2 implementation result — 2026-07-10

SK2 is complete in the offline shadow path:

- every raw semantic proposal receives a stable candidate ID, reader-call
  reference, raw-proposal hash, state history, terminal state, and reason;
- prompt identity, boundary-client identity, provider, and model are recorded
  when exposed, while prompt text is not persisted;
- semantic readers—not Python—declare whether a valid proposal is selected,
  ambiguous, set aside, or insufficiently supported;
- mechanical validators directly report exact evidence/contract outcomes to
  the ledger rather than asking a second deterministic layer to reinterpret
  the conversation;
- invalid and unsupported candidates remain in the ledger but cannot enter the
  current interpreted view;
- competing current-question candidates remain visible as ambiguity;
- the current semantic view is reconstructed entirely from terminal ledger
  records and carries a reproducible view hash;
- raw proposals missed by a validator are retained automatically and fail
  closed, so no list item silently disappears;
- source-turn-reference coverage and disagreement counts are diagnostics only,
  not quality measures.

The candidate-disposition prompt addendum is injected only by the offline
shadow wrapper. Shared specialist prompts, live lane input, graph traversal,
and runtime routing remain unchanged.

Verification:

- 181 focused semantic-kernel, specialist, provenance, corpus, and boundary
  tests passed;
- 3,851 non-network repository tests passed, with 1 pre-existing skip;
- the legacy stability-check module remains excluded because several of its
  tests make unmocked OpenAI embedding calls.

No paid model corpus rerun was performed in SK2. The structural custody
contract is verified with controlled readers; measuring whether the new reader
dispositions improve real semantic coverage belongs to the next evaluation
pass.

## SK3 implementation result — 2026-07-10

The SK3 reader and structural harness are implemented in the offline shadow
path, but the corpus promotion gate has not yet been run:

- the joint semantic reader now requests every material question across the
  trajectory, including intermediate questions, rather than reducing the read
  to an initial/current pair;
- the reader owns question-function and question-relation judgments, including
  alternative relations and explicit ambiguity;
- the shadow-only stance addendum asks the stance reader to identify the exact
  earlier stance that a later revision, qualification, condition, or deferral
  relates to;
- deterministic code resolves only reader-declared exact turn/quote references
  to existing candidate IDs and reports whether the reference is resolved,
  ambiguous, incomplete, or absent;
- chronology checks report a target that occurs after the referring event but
  do not reject, relabel, or repair the semantic interpretation;
- unresolved references and competing readings remain in the candidate ledger
  and current view instead of disappearing;
- trajectory-reference counts are explicitly mechanical diagnostics and are
  marked as unsuitable for use as reasoning-quality labels;
- shared specialist prompts, live lane input, graph traversal, and runtime
  routing remain unchanged.

Verification:

- 16 direct shadow/trajectory tests passed;
- 130 focused semantic-kernel, specialist, provenance, corpus, and boundary
  tests passed;
- 3,855 non-network repository tests passed, with 1 pre-existing skip;
- the legacy stability-check module remains excluded because several tests
  make unmocked OpenAI embedding calls.

This establishes the implementation contract, not semantic improvement. A
locked-corpus run with the real model is still required to measure operative
question recall, stance coverage, label stability, and ambiguity preservation.
SK4 should not be started merely because the local harness passes; the SK3
corpus result should first tell us whether this bounded reader change helped.

## SK3 locked-corpus evaluation result — 2026-07-10

The locked 12-case, three-repeat OpenRouter evaluation is complete. The full
result is in
`research/core-semantic-sk3-2026-07-10/sk3-corpus-result.md`.

Decision: **partial; do not promote and do not start SK4 yet**.

- weighted recall rose from 0.542 to 0.552;
- the case recall floor rose from 0.208 to 0.333;
- never-recovered observations fell from 41 to 36;
- stable observations fell from 49 to 46;
- macro span repeatability fell from 0.642 to 0.595;
- macro labeled repeatability fell from 0.628 to 0.566;
- operative-question recall fell slightly from 0.697 to 0.682, despite
  validated question volume increasing from 64 to 132;
- stance recall rose from 0.545 to 0.576, while stance span and label
  repeatability both fell;
- candidate custody was complete for all 895 proposals, but 516 proposals
  omitted the requested semantic disposition;
- only 1 of 186 stance events resolved its declared prior-event relationship.

The structural boundary held: no deterministic semantic assignment, graph
change, live routing change, or runtime change was introduced. The observed
failure is prompt/semantic-contract reliability, not evidence custody.

Before SK4, run one bounded three-case repair experiment on Cases 02, 08, and
11. Keep exhaustive question reading, simplify stance-to-prior-event linking,
measure missing dispositions explicitly, and add evaluation-only wall-clock
failure recording. Return to the full corpus only if the repair improves
stance stability without losing operative-question coverage.

## SK3 bounded repair implementation — 2026-07-10

The bounded repair is locally complete. It incorporates the useful part of the
founder's original context-engineering inspiration without introducing an
autonomous multi-agent architecture:

- question trajectory now has one focused reader, one array, and one semantic
  job instead of competing with pressure, options, and evidence boundaries in
  a four-array joint prompt;
- pressure, options, and evidence boundaries remain grouped in a narrower
  decision-context reader because they share the same decision-structure
  dependency; this grouping remains an empirical hypothesis;
- all readers keep the authoritative full conversation, while instructions and
  output schemas are scoped to the assigned job;
- mandatory `candidate_disposition` metadata was removed from extraction
  prompts because it added a second semantic task that 516 of 895 corpus
  candidates ignored;
- a validated emitted candidate enters the current view by reader emission,
  while explicit disposition remains optional and its observability is
  measured separately;
- the ledger explicitly states that it cannot observe hypotheses the reader
  did not return;
- later stance events now refer to the zero-based index of an earlier stance
  in the same returned array; deterministic code resolves that declared link,
  checks index order and source chronology, and never invents a relation;
- question source-quote references remain unchanged because they resolved well
  in the corpus;
- the corpus runner now applies an evaluation-only total wall-clock limit to
  each provider call, stops on recorded provider failure, preserves completed
  call metadata and the failed stage in an error artifact, and retries only
  the missing shadow artifact;
- the current five-call topology is still sequential. Parallel execution is
  deferred until semantic quality passes, so latency work cannot obscure the
  ablation result.

The source-first prompt rule is now also recorded in
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`.

Local verification:

- 17 direct shadow/trajectory tests passed;
- 4 evaluation-runner timeout, retry, stage, and failure-custody tests passed;
- 135 focused semantic-kernel, specialist, corpus, boundary, and runner tests
  passed;
- 3,860 non-network repository tests passed, with 1 pre-existing skip;
- no paid model call was made for the repair implementation.

The next decision remains empirical: run Cases 02, 08, and 11 three times with
the repaired five-call shadow path. Compare each case with the already-frozen
SK3 outputs. Do not run the full corpus unless stance stability improves
without losing operative-question coverage or creating a new cross-family
regression.

## SK3 repair Case 02 preflight — 2026-07-10

The paid repair preflight stopped after Case 02. Full details are in
`research/core-semantic-sk3-repair-2026-07-10/case-02-preflight-result.md`.

The result did not pass the gate:

- question span and label repeatability improved from 0.444 to 1.000;
- the due-diligence question became stable across all three repeats;
- stance span repeatability fell from 0.458 to 0.222;
- stance label repeatability fell from 0.348 to 0.143;
- one repeat lost all six stance proposals to incorrect turn attribution;
- exact-span recall fell from 0.375 to 0.208;
- none of ten validated stance events declared a prior-event index.

Two structural issues were also found. Provider-success responses can still
omit required top-level arrays, and item-level fields described only in prose
can disappear. The first issue is now caught by the harness, recorded, and
retried. The second caused two responses to omit every option/evidence
`speaker`, making those candidates mechanically invalid.

Paid execution stopped before Cases 08 and 11. Across the archived invalid
preflight, valid rerun, and one preserved missing-key attempt, Case 02 used 34
recorded calls and 180,624 tokens.

After stopping, the local prompt contracts were completed with explicit item
shapes, required speaker keys, explicit nullable stance indices, and a ban on
ellipsis inside exact quotes. Reference metrics now distinguish explicit null
from a missing link field. No case-specific corpus content was added.

Current verification: 3,862 non-network tests passed, with 1 pre-existing
skip. No further paid call should run without explicit approval for one more
Case 02-only schema preflight. Cases 08 and 11 remain blocked behind that gate.

## SK3 repair Case 02 explicit-schema v2 — 2026-07-10

The approved Case 02-only rerun is complete. It used three fresh five-reader
repeats plus one automatically preserved and retried missing-key attempt.

The explicit schemas fixed the mechanical and stance failures:

- exact-span recall improved to 0.583, versus 0.375 in frozen SK3;
- stance span repeatability improved to 0.602, versus 0.458 in frozen SK3 and
  0.222 in repair v1;
- stance labeled repeatability improved to 0.496;
- option repeatability reached 1.000;
- all stance, option, and evidence candidates carried valid source fields;
- 22 stance-link fields were explicitly null and 1 link resolved;
- required-key retry and failure custody worked as designed.

The result remains partial:

- question span repeatability fell from 0.444 to 0.208;
- all repeats recovered the due-diligence span, but only two labeled it
  current; one labeled the later seven-day-feasibility question current;
- question candidate volume varied from 8 to 5 to 4;
- only 3 of 17 question references resolved.

Source-first review found that the additional questions were genuine user
questions, not fabricated spans. The remaining failure is therefore semantic
trajectory selection, not quote custody or schema adherence.

Full result:
`research/core-semantic-sk3-repair-2026-07-10/case-02-preflight-result.md`.

The complete Case 02 repair sequence used 53 recorded calls and 281,594
tokens. Cases 08 and 11 were not run. Before further paid work, decide whether
to add a separate focused question-candidate extraction step followed by a
question-trajectory interpretation step. That would be a sixth, serial call
and must be justified against added cost and complexity.

## SK3 explicit-schema three-case decision — 2026-07-10

Cases 08 and 11 were subsequently approved and run without prompt, model,
source, gold, or scoring changes. The combined result for Cases 02, 08, and 11
is in
`research/core-semantic-sk3-repair-2026-07-10/three-case-repair-result.md`.

Compared with frozen SK3 on the same cases:

- weighted recall improved from 0.413 to 0.547;
- stable observations improved from 8 to 13;
- macro span repeatability improved from 0.450 to 0.628;
- macro labeled repeatability improved from 0.410 to 0.577;
- the case floor improved from 0.333 to 0.500;
- operative-question recall improved from 0.500 to 0.889;
- every event family's macro repeatability improved;
- assistant-position recall fell from 0.667 to 0.600 while stable stance gold
  remained 3; source-first review found both shorter-span under-credit and real
  final-condition misses;
- user-pressure recall remained 0.111 with no stable gold;
- dropped-thread recall remained 0 despite more repeatable outputs.

Decision: retain the five-reader explicit-schema path as the offline
experimental base. Do not add a sixth question-selection call based on Case 02
alone. Do not run the remaining nine corpus cases yet; SK4 and SK5 would still
block the locked promotion gate.

Begin SK4 with one bounded decomposition: give user pressure a focused
one-array reader and leave options plus evidence boundaries together for the
first ablation. This adds one narrow call but no autonomous agent, correction
loop, deterministic semantic rule, graph input, or live behavior. Test on the
same three diagnostic cases before deciding whether evidence also needs a
separate reader.

## SK4 focused user-pressure implementation — 2026-07-10

The bounded SK4 implementation is locally complete. No paid call has been
made for it.

Probabilistic allocation:

- a new user-pressure reader receives the authoritative full conversation but
  only one semantic job and one output array;
- it interprets corrections, evidence requests, concerns, timing pressure, and
  explicit values;
- it is instructed to cover multi-part corrections rather than selecting one
  representative item;
- the same exact span may carry more than one reader-assigned role when the
  model judges that both are genuine;
- options and evidence boundaries remain together in a narrowed two-array
  reader for the first ablation;
- question, stance, constraint, and dropped-thread prompts are unchanged.

Deterministic allocation:

- exact user quotes, turn references, allowed kinds, caps, and schema keys are
  validated;
- same-quote/different-kind pressure events remain distinct because Python
  does not decide which role is semantically correct;
- byte-identical event identities remain in the ledger, but later duplicates
  receive the structural `duplicate_identity` terminal state and do not enter
  the current view;
- overflow, invalid, unsupported, and duplicate candidates retain terminal
  reasons;
- the evaluation runner now requires six reader roles and the exact top-level
  keys for the user-pressure and option/evidence calls;
- artifact reuse from the five-reader experiment fails closed because its
  reader-role contract does not match the six-reader topology.

Non-changes:

- no keyword classifier, deterministic pressure label, current-question rule,
  graph input, lane input, live runtime, Step 6, receipt, or archive behavior
  changed;
- the six calls remain sequential until semantic quality is demonstrated;
- candidate disposition remains optional and unreturned hypotheses remain
  unobserved.

Local verification:

- 25 direct shadow and evaluation-runner tests passed;
- 139 focused semantic-kernel, specialist, corpus, boundary, and runner tests
  passed;
- 3,864 non-network repository tests passed, with 1 pre-existing skip;
- no paid model call was made.

The paid ablation, if approved, is locked to Cases 02, 08, and 11 with three
repeats, six shadow calls per repeat, unchanged model and scoring, and reused
compact artifacts: 54 successful calls plus bounded retries.

Promotion gate for that ablation:

- user-corrections-and-pressure weighted recall must exceed the current 0.111;
- at least one of the three pressure observations must become stable;
- accepted pressure candidates must remain exact-source valid;
- option/evidence recall and repeatability must not show a material regression;
- no improvement may come from a case-specific prompt phrase or deterministic
  semantic rule.

Failure keeps the five-reader SK3 repair as the offline base and triggers
source-first review of pressure representation before any further split. A
pass authorizes the SK4 offline contract, not the full corpus, SK5, graph, or
live integration.

## SK4 focused user-pressure ablation result — 2026-07-10

The approved paid ablation is complete. Full evidence and interpretation are
in
`research/core-semantic-sk4-pressure-2026-07-10/sk4-pressure-ablation-result.md`.

Decision: **fail the promotion gate and retain the five-reader SK3 repair as
the offline experimental base**.

The focused reader improved pressure-family repeatability but did not improve
locked pressure recall: weighted recall remained 0.111 and no pressure gold
observation became stable. All 61 accepted pressure candidates were exact
source-valid, confirming that deterministic custody worked while semantic
prioritization did not. Option/evidence measures regressed materially,
including evidence-boundary recall from 0.333 to 0.000.

The strongest diagnostic case was Case 08. The reader selected the same eight
valid concerns in all three repeats but missed the required household-
conversation qualification every time. The failure is therefore not general
reader instability. The current `user pressure` job is too broad, allowing
generic concerns to consume the cap before product-relevant corrections and
qualifications.

No full-corpus run, SK5 work, graph integration, or live change is authorized.
The next step is a source-first review of the pressure target and the 61
selected candidates. A future ablation must keep the SK3 decision-context call
unchanged for option/evidence output, so the focused pressure reader is the
only semantic variable.

## SK4 source-first counter-pressure revision — 2026-07-10

The source-first review is complete. The detailed review and revised contract
are in
`research/core-semantic-sk4-counterpressure-v2-preflight-2026-07-10/source-first-counterpressure-review.md`.

The failed SK4 prompt remains intact for reproducibility. A separate v2 reader
now targets only user statements that materially correct a premise or frame,
qualify evidence or feasibility, or object to the reasoning. Its three labels
are `premise_correction`, `material_qualification`, and
`reasoning_objection`. Standalone questions, acknowledgements, and generic
concerns or values are explicitly outside this reader unless a statement
independently performs one of the three reasoning roles.

Cross-family overlap remains a probabilistic judgment. A statement may be
both counter-pressure and an evidence boundary or constraint; Python validates
the LLM's declared role and exact source but does not infer the overlap.

The next experiment is now isolated to one reader and one case. Case 08 will
run three counter-pressure calls while all locked SK3 families remain
unchanged. The no-cost contract is in
`research/core-semantic-sk4-counterpressure-v2-preflight-2026-07-10/preflight-contract.json`.
No paid v2 call has been made.

The preflight must recover the household-conversation qualification in all
three repeats, keep exact-source validity at 1.0, use exactly one reader call
per artifact, and return no old catch-all kinds. A pass authorizes only a
nine-call pressure-only test across Cases 02, 08, and 11.

## SK4 counter-pressure v2 paid preflight result — 2026-07-10

The approved three-call Case 08 preflight is complete. Full evidence is in
`research/core-semantic-sk4-counterpressure-v2-preflight-2026-07-10/case08-paid-preflight-result.md`.

Decision: **fail the locked gate and do not run Cases 02 and 11**.

The reader missed the locked turn-2 household-conversation quote in all three
repeats, so strict pressure recall was 0.000 and no gold pressure observation
was stable. Mechanical and architectural controls passed: 11/11 returned
candidates were exact-source valid, all three artifacts used exactly one
reader call, no old catch-all label was returned, and no other semantic family
was rerun.

The narrower target reduced the original noise: Case 08 fell from eight broad
concerns per repeat to three or four material qualifications. The remaining
failure is temporal. The reader favored later facts that visibly changed
developed reasoning and failed to preserve the earlier introduction of the
husband-alignment issue. Two repeats selected a later, stronger husband quote,
but it receives no credit because it was not predeclared gold evidence.

The next step is no-cost evaluation design, not another reader or paid run.
Separate strict first-introduction coverage from deterministic scoring over
researcher-reviewed alternative source spans declared before the next test.
Do not use post-run LLM judging, embeddings, or retroactive gold edits to make
this preflight pass.

## SK4 temporal and concept coverage review — 2026-07-10

The approved no-cost review is complete. Full results are in
`research/core-semantic-sk4-counterpressure-v2-preflight-2026-07-10/temporal-concept-review-result.md`.

The evaluation now separates concept coverage for downstream reasoning from
first-introduction coverage for the audit trail. Later strengthening is a
third, separate observation. A later span may demonstrate that the reasoning
substrate received the concept, but it cannot substitute for chronology in the
audit metric.

The prospective source contract covers Cases 02, 08, and 11 and is stored in
`counterpressure-temporal-coverage-contract.json`. Because it was created after
the Case 08 v2 outputs were observed, rescoring current artifacts is diagnostic
only. It cannot change or promote the failed run. Future calls may use it only
while it remains frozen beforehand.

Case 08 diagnostic rescore:

- SK3 base: first introduction 0.000; concept 0.000;
- broad SK4: first introduction 0.000; concept 0.000;
- counter-pressure v2: first introduction 0.000; concept 0.667;
- no arm achieved stable recovery;
- all scored source events remained exact-valid.

The strict original metric hid partial v2 improvement, but not enough to alter
the decision. V2 captured a later husband-alignment statement in two repeats,
yet omitted it in one repeat and never preserved the earlier turn-2
introduction.

The next candidate change is prompt-only: ask the existing v2 reader to keep
the first source span where a material counter-pressure thread enters and a
later span only when it materially strengthens that thread. Keep the same
reader, labels, schema, cap, validation, and no-graph boundary. Test locally
before deciding whether another three-call Case 08 preflight is justified.

## SK4 counter-pressure temporal prompt v2.1 — 2026-07-10

The prompt-only temporal revision is locally complete. Full details are in
`research/core-semantic-sk4-counterpressure-v21-temporal-preflight-2026-07-10/temporal-prompt-local-result.md`.

The failed v2 prompt is unchanged. V2.1 appends one semantic instruction: keep
the first source span where each material counter-pressure thread enters, and
keep a later span separately only when it materially strengthens that thread.
The LLM decides thread identity, first introduction, and material
strengthening. Python continues to validate only the declared kind, source,
quote, cap, schema, and identity.

No label or event field changed. No new reader, relationship object, keyword
rule, graph input, live behavior, or paid call was added. A distinct artifact
schema version prevents old v2 artifacts from being reused as v2.1 evidence.

The Case 08 deterministic fixture preserved the turn-2 first introduction and
turn-4 strengthening in one call and source order. This is plumbing evidence,
not model-quality evidence.

The next paid contract is frozen at three Case 08 calls. Concept,
first-introduction, and later-strengthening coverage are reported separately
and each must be stable. The contract is in
`research/core-semantic-sk4-counterpressure-v21-temporal-preflight-2026-07-10/preflight-contract.json`.
A pass only authorizes discussion of the three-case temporal pressure-only
ablation.

## SK4 v2.1 paid result and system-level evaluation — 2026-07-10

The three-call v2.1 temporal preflight failed. It reproduced the v2 pattern:
concept and later-strengthening coverage were 0.667, first-introduction
coverage was 0.000, exact-source validity was 1.000, and no result was stable.
The stop rule now applies: do not run another pressure prompt on Case 08.

The subsequent no-cost ontology audit found that the old evaluation conflated
reader placement with total packet coverage. Full details are in
`research/core-semantic-sk4-counterpressure-v21-temporal-preflight-2026-07-10/system-level-evaluation-result.md`,
and the canonical doctrine is
`docs/conversation-understanding/lolla-evaluation-doctrine-v0.md`.

Across the full 12-case SK3 corpus, family-aligned exact-span recall is 0.552
with 46 stable observations, while system-level exact-span recall is 0.716
with 63 stable observations. Fifty observation/run opportunities were rescued
by another semantic family. This demonstrates useful packet coverage but does
not prove correct role assignment or temporal fidelity.

On the same three diagnostic cases, retained SK3 repair remains better than
broad SK4 at both levels:

- SK3: 0.547 family recall, 0.760 system recall, 13 family-stable and 19
  system-stable observations;
- broad SK4: 0.493 family recall, 0.747 system recall, 11 family-stable and 17
  system-stable observations.

Decision: retain SK3, stop pressure prompt tuning, and build a prospective
semantic-observation contract that separates concept coverage, family role,
temporal position, and consumer needs. No further paid call is justified until
that ontology and scorer are frozen.

## Reviewed observation contract and downstream gate — 2026-07-10

The prospective observation scaffold now covers all 102 legacy observations,
but only the 16 pressure observations have been source-reviewed. Pending
observations remain ineligible for promotion.

Retained SK3 on the reviewed pressure subset achieved 0.833 concept-anywhere
recall, 0.792 acceptable-role recall, and 0.750 first-introduction/complete
temporal recall. Twelve of sixteen concepts were stable anywhere and eleven
were stable in an acceptable role. The one total concept omission is Case 07's
unresolved-decision self-correction. The transcript preserved it; the semantic
packet did not.

A no-cost end-to-end bridge then connected the current enterprise-beta archive,
the SK3 reviewed subset, graph-survival telemetry, and an analogous human
review. It showed a healthy, cheap run with real decision delta, but also 38
vendor calls, 109 raw lane signals, 60 candidates, 8 selected cards, and 16
selected chunks. This motivated a strong-control downstream test.

The frozen two-call pilot compared a fresh strong reconsideration against the
same reconsideration plus Lolla pressure. Both arms produced the same likely
next action and the same four material shifts. Blind provisional review found
no material winner. The treatment added specificity, not a unique
decision-relevant delta, so the positive-case gate failed and the stop rule
applies.

Decision:

- do not repeat or retune the enterprise-beta case;
- do not infer semantic-kernel or runtime value from the good revised answer;
- do not integrate SK3 into graph input;
- package one quiet stand-down case next, where added public machinery is a
  failure;
- later select a non-obvious positive case only if its expected delta is not a
  correction any strong fresh model should recover directly.

## Quiet downstream pilot — 2026-07-10

The complementary quiet pilot is complete. It used the independent-consulting
case whose original conversation already carried the main pipeline, spouse,
checkpoint, and fractional-bridge pressure.

Both fresh arms preserved the same likely action and stayed compact. Blind
provisional review preferred the Lolla treatment for calibration: it removed
unsupported conversion, first-engagement timing, and retainer precision; kept
fractional work as an option to probe; and added only 13 completion tokens over
control. The control caught only the retainer range and introduced a small
external market-rate assertion.

Decision: provisional quiet-case pass, human review pending. Do not repeat or
tune the case. The result demonstrates one example of responsible smallness,
not a reliable stand-down rate and not semantic-kernel integration evidence.

Combined call budget for both downstream pilots: four generation calls, zero
evaluator calls, 8,007 tokens, estimated $0.02594 under the 2026-05-25 pricing
table.

The next high-information semantic test is Case 07's unresolved-decision gap.
Before any call, design an offline counterfactual that compares a strong fresh
reconsideration with the actual SK3 semantic overlay and, only if justified, a
source-reviewed overlay containing the omitted self-correction. This is an
integration-risk diagnostic, not a new reader or runtime proposal.

## Case 07 semantic-overlay counterfactual result — 2026-07-10

The three-call counterfactual is complete. Blind ranking was transcript-only
control approximately equal to reviewed oracle, both better than the actual
27-event SK3 overlay.

All arms recognized that Seattle remained undecided because the full
conversation stayed authoritative. The actual overlay nevertheless failed to
explicitly retract the assistant's “Seattle is the root decision” frame. The
oracle addition repaired that weakness and better preserved multiple value
dimensions, but did not beat the control. The control had already recovered
the user's self-correction directly from the transcript.

Decision:

- naive full-semantic-overlay handoff is blocked;
- source-valid context is not assumed attention-neutral;
- the semantic inventory remains useful for audit/navigation/receipt work;
- raw transcript remains mandatory for reconsideration;
- the small active working-set projection is defined and sealed in shadow
  mode, but it is not the whole consumer and is not runtime-integrated;
- paid calls stop until it is recomposed with the existing edge/weak/parked
  portfolio layers and exact human review accepts or repairs that portfolio.

The counterfactual used 13,077 tokens and an estimated $0.03330 with no
evaluator calls or retries. Across all three downstream experiments in this
program: seven generation calls, zero evaluator calls, 21,084 tokens, and an
estimated $0.05925.

## Case 07 full-surface portfolio diagnostic — 2026-07-10

The next bounded run used the frozen historical extraction and the current
live pipeline to generate a private Step 6 table and v2 V60 ledger skeleton for
Case 07. It reused the existing transcript-only strong control and authorized
no consumer call before a separate novelty gate.

The pipeline completed healthy with 22/22 turns, zero fabricated quotes, a
4,794-character private table, 12 table sources, eight V60 cards, and 16 V60
chunks. It nevertheless failed the frozen operability gate: 51 OpenRouter
calls exceeded the ceiling of 40. The Bullshit Index accounted for 34 calls.
Estimated total provider cost was $0.048731, demonstrating that low monetary
cost can still hide an unacceptable call topology.

The semantic novelty gate also failed. The private table mostly confirmed the
prior assistant's optionality, listening, constraints, and cognitive-load
organization. Regret, sunk cost, calculated risk, and endowment were not two
clearly unhandled pressures with a new decision consequence, and some could
wrongly discount genuine attachment to DC. The already-frozen strong control
had recovered the unresolved Seattle state, user preference gap, medical and
employer uncertainty, and underexplored DC attachment directly from the raw
conversation.

Decision:

- stop before a portfolio-consumer call;
- do not rerun or raise the Case 07 ceiling after seeing the result;
- retain the raw conversation as the defense against table-frame drift;
- keep the five-item active handoff separate from the whole live context;
- cap the peripheral Bullshit Index at 12 calls by deterministic adjacent
  passage merging, with no source passage dropped;
- expose source/evaluation passage counts and compaction state;
- use separate core-pressure and peripheral-postprocessing ceilings on the
  next untouched holdout.

The checked-in research artifacts preserve the frozen contract, failed-gate
receipt, review-safe table/V60 snapshots, and provisional review. The raw
pipeline output remains local-only because it contains a machine-specific
absolute substrate path.

Verification after the prospective repair: 68 focused tests passed; the full
non-network suite passed with 3,925 tests, 1 expected skip, and 93 subtests.
No Case 07 retry or consumer call was made.

## Case 09 untouched-holdout result — 2026-07-10

Case 09 tested the prospective operability repair on a 22-pair PhD
dissertation conversation. A fresh extraction preserved 44/44 messages and
verified all six selected reasoning passages with zero fabrication and no
repair. The pipeline then passed every frozen call and cost ceiling: 32
OpenRouter calls total, comprising one extraction, 19 core-pressure calls,
and 12 Bullshit Index calls; seven direct OpenAI embedding/query-expansion
calls; no revision or experiment retry; estimated cost $0.057738.

The Bullshit Index cap therefore repaired the Case 07 call-topology failure on
this holdout: all 66 source passages were retained through adjacent merging
into 12 evaluation passages. One evaluation returned an empty result, so run
health remained honestly `partial`; the frozen contract had not made a single
post-processing failure a stop condition.

A one-call transcript-only strong control independently recovered the largest
corrections: remove unsupported statistics and stakeholder motives, stop
calling Option 3 inherently smart, make it contingent on real access and
support, and withdraw the fixed 18-month checkpoint. This keeps the strong
fresh-context LLM as the proper baseline rather than a weak vanilla answer.

Two Lolla pressures remained absent or materially incomplete: a two-sided
regret test bound to downside and reversibility, and a durable collaboration
role/continuity design rather than simple data access. Both had plausible
guardrail consequences, so the semantic consumer gate passed provisionally.

No portfolio-consumer call was made. The pre-call Case 09 contract froze the
consumer threshold but not the treatment call's provider/model, prompt,
output cap, or typed output schema. Defining them after reading the control
would have violated its no-goalpost-change rule. Case 09 is therefore a
bounded inconclusive result with additive-pressure signal, not answer-
improvement evidence and not runtime integration authority.

Prospective repair: use a two-stage protocol. First freeze and run pipeline
admission. If it passes, freeze a paired downstream contract before either
downstream arm is called. Control and treatment must share model,
configuration, neutral task, typed output schema, and cap; only treatment
receives the hash-locked source-traceable pressure packet. Case 09 will not be
rerun. The paired runner now supports prospective typed fields, and the
two-stage protocol is documented without changing the live runtime.

Verification after Case 09 and the prospective harness repair: 37 focused
tests passed; the full non-network suite passed with 3,931 tests, 1 expected
skip, and 93 subtests. Python compilation, JSON parsing, package path/secret
scans, and `git diff --check` passed.

Verification after the complete July 10 program:

- 68 focused semantic, downstream, boundary, lineage, constitution, and
  counterfactual tests
  passed;
- 3,911 non-network repository tests passed, with 1 pre-existing skip and 93
  subtests;
- the legacy stability-check module remains excluded because several tests
  make unmocked OpenAI embedding calls;
- JSON parsing, Python compilation, and `git diff --check` passed for the new
  artifacts and scripts.

## Reasoning-pressure handoff shadow result — 2026-07-10

The blocked full semantic overlay has been replaced at the design boundary by
`lolla.reasoning_pressure_handoff.v0`: the authoritative full conversation plus
at most four pressure items and four preservation items. The enterprise-beta
shadow packet uses three pressures and two preservation items, versus 27 events
in the blocked overlay.

A dependency-free validator now checks only deterministic duties: schema
shape, caps, hashes, exact source-event and graph-reference membership,
boundary flags, and required non-claims. It explicitly returns false for
semantic-relevance validation, answer-quality validation, and runtime
authorization.

The packet was sealed without model calls against the saved conversation, the
Case 01 SK3 semantic shadow, its source-linked reasoning-pattern packet, its
fact-free routing projection, and the saved graph-survival report. All five
artifacts have real hashes. Eight of 21 known semantic events and three of 73
graph candidate rows enter the handoff.

Decision: compactness and mechanical lineage pass for the active slice in
shadow mode. Semantic selection and downstream usefulness do not. The active
slice must not become a premature relevance filter. Reuse the existing
research-only `step6_attention_map.v1` edge/latticework reserve, weak and
negative-space receipts, parked index, and expansion refs before human review.
A blank exact-human-review intake exists; it must not be filled by Codex as a
substitute for a human. No live graph input, Step 6 prompt, skill behavior, or
runtime path changes are authorized.

## Extraction-admission smoke result — 2026-07-10

The frozen Case 12 non-holdout smoke ran exactly once. Output-parent preflight
worked, the complete 2/2-turn conversation was captured, and a terminal error
artifact was preserved. The provider boundary returned an empty parsed object
after approximately 207 seconds, so the extractor correctly rejected missing
`decision_situation` and `synthesized_position` fields.

The error path did not persist the boundary client's call log. Provider status,
served model, token usage, call count from boundary telemetry, and cost are
unknown. The result therefore fails admission and does not authorize another
paired holdout. Case 12 is permanently excluded from holdout claims and will
not be rerun.

The next bounded engineering slice is transactional extraction-call custody:
write call evidence on every terminal path, represent missing usage after an
attempt as unknown rather than zero, record end-to-end duration, and enforce a
prospectively frozen outer wall-clock ceiling. These are deterministic custody
responsibilities; they do not justify Python rules for missing conversational
meaning. After provider-free tests pass, a different non-holdout may receive
one new frozen smoke contract.

Verification for this slice: 79 focused tests passed. The full non-network
suite passed with 3,972 tests and one expected skip under Python 3.12. The
legacy stability-check module remains excluded because six tests require an
unavailable OpenAI embedding client; no verification API call was made.

## Transactional extraction-call custody repair — 2026-07-10

The next no-provider slice implements the prospective F11 repair without
changing conversational meaning. `run_extract.py` now atomically persists its
list-shaped call sidecar immediately after the initial extraction boundary and
again after the one allowed quote-repair boundary. The extraction artifact
separately records whether a call was attempted, a record survived, and an
admissible extraction was produced. Unexpected boundary exceptions receive an
`unexpected_error` record before re-raise.

Smoke contract v1 freezes provider and outer wall-clock timeouts. If a process
crosses the outer ceiling, the harness terminates that one attempt, seals a
failed result, and does not retry. If a call may have happened but no record
survives, calls, tokens, and cost are null/unknown rather than zero.

The prompts, required semantic fields, quote semantics, graph, portfolio,
Step 6, and runtime integration status are unchanged. Provider-free tests cover
success, non-strategic decline, missing fields, provider exception, quote
repair, missing usage, and outer timeout. The canonical restart contract is
`docs/evals/extraction-call-custody-contract-v0.md`; cycle state is in
`research/extraction-call-custody-repair-2026-07-10/cycle-status.json`.

This repair does not pass the historical Case 12 smoke. After full non-network
verification, the next separate goal is to freeze one different non-holdout
smoke under contract v1. Another paired holdout remains blocked until that new
smoke passes.

Verification completed with 96 focused tests and 3,979 non-network repository
tests passing, plus one expected skip, under Python 3.12. No provider call was
made. The repair goal is complete; freezing the new smoke is the next separate
goal and remains distinct from running an untouched holdout.

## Case 01 contract-v1 extraction-admission result — 2026-07-10

The next separate goal used the heavily reused enterprise-logo-beta fixture,
permanently excluded it from holdout claims, froze nine transitive code and
pricing hashes plus exact prompts/model/calls/time/cost, and ran once.

All gates passed: full 6/6 capture, three source-exact reasoning passages, one
persisted extraction call, no quote repair, no experiment retry, compatible
served version alias, 2,087 tokens, `$0.001190` estimated cost, and 2.618
seconds wall time. Raw provider content stayed in the local call sidecar and
did not enter the review-safe result or extraction.

This is one short familiar-case operability pass, not semantic-quality or
reasoning-value evidence. It authorizes the next separate goal to select one
untouched case and freeze Stage A extraction-plus-pipeline before calls. It
does not authorize control/treatment generation, graph promotion, or runtime
integration.

Final verification after the sealed run and documentation update: 87 focused
tests and 3,980 non-network repository tests passed with one expected skip
under Python 3.12. The goal used exactly one frozen OpenRouter extraction call
and no embeddings, evaluators, graph pipeline, reconsideration, or retries.
