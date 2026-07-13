# Lolla Core Reasoning Audit: Current-Stage Assessment and PRD v0

**Status:** working draft for founder discussion  
**Date:** 2026-07-09  
**Scope:** the core product only: conversation understanding, reasoning-pattern interpretation, deterministic pressure, reconsideration, and a portable run record.

## Binding Architecture Addendum — 2026-07-10

New core work under this PRD is governed by
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`.

The binding allocation is:

- LLMs/humans own semantic interpretation and applicability judgment;
- deterministic code owns custody, validation, declared graph candidate
  recall, packaging, observability, and evaluation;
- deterministic code must not compensate for semantic-reader weakness with
  keyword rules, case templates, or surface-level conversation gates;
- graph recall is not a claim that a model is applicable or correct.

Where wording in this working draft can be read as deterministic semantic
judgment, the hybrid boundary controls.

## Executive Assessment

Lolla is a mechanically substantial alpha, not yet a semantically validated reasoning-audit product.

The repository contains a real working system:

- verbatim conversation capture and archive custody;
- a compact extraction pass;
- a provenance-aware `ConversationIR`;
- four audit lanes;
- deterministic routing through a 222-model curated substrate;
- source-backed V60 enrichment;
- same-session Step 6 reconsideration;
- private consideration ledgers;
- a revised answer, memo, Observatory, archive, and private Markdown export.

The strongest current evidence says that Lolla can create useful reasoning friction and can materially improve some answers. The six-case complex baseline and the later human review seed are encouraging. They do not yet prove that Lolla consistently understands the conversation, selects the right reasoning patterns, or improves advice because of the deterministic graph.

The central gap is architectural as well as evaluative:

> The current system does not yet enforce a clean boundary in which deterministic model selection operates only on abstract, source-grounded reasoning patterns.

Today, full conversational and factual text influences multiple selection stages. Lane 2 extracts abstract reasoning moves, but candidate recall and embeddings mix those moves with the full assistant answer. Lane 1 relevance also combines the decision summary with the full assistant answer. Lanes 3 and 4 derive abstract labels from the full case, then route them deterministically. The result is a hybrid system, not yet the controlled decontextualization described in the product vision.

There is also a newer, separate Decision Work / sidecar path. It should not be confused with the live lane-input path:

- the live path automatically interprets every normal run before the four lanes;
- the Decision Work path defines a much richer conversation/process interpretation target and a post-archive sidecar chain;
- the Decision Work contract includes options, assistant influence, changed direction, useful or noisy friction, lost value, overcorrection, evidence limits, and handoff status;
- its deterministic packet, validation, rendering, resolver, runner, and sidecar-writing machinery is implemented;
- its semantic interpretation is not yet automatically generated for arbitrary new runs. It currently depends on explicitly supplied, operator/Codex-assisted generated reads and defers when that semantic read is missing.

These paths may eventually share a semantic kernel, remain separate, or partly replace one another. That is an evaluation question, not a decision this PRD assumes in advance.

The right next move is not more Observatory polish, a cross-run knowledge base, more substrate enrichment, or a broader agent-control contract. It is a small, falsifiable evidence program around the core semantic chain:

```text
verbatim conversation
-> source-grounded conversation interpretation
-> abstract reasoning-pattern packet
-> deterministic graph pressure
-> factual context reattached
-> reconsidered answer
-> self-explaining portable run record
```

## Product Thesis

Lolla is one product with several connected surfaces.

Its primary job is to pressure-test reasoning in a serious human–LLM conversation. Its accountability artifacts preserve how that pressure was produced and used. Its mental-model teaching surface can later help people understand the lenses, but it is downstream of proving the audit itself.

Within that one product, two different interpretation jobs currently exist:

1. **Operational pressure interpretation.** Understand enough of the conversation, before the audit, to identify reasoning patterns and select useful mental-model pressure with acceptable latency and cost.
2. **Decision Work interpretation.** Understand the conversation and completed audit process more fully, after or outside the live run, so a future reader can inspect the decision path, influence, alternatives, changes, losses, uncertainty, and custody.

The second job is broader. Broader does not automatically mean better for mental-model selection. Some information may be essential to the audit trail while being distracting, anchoring, or wasteful at the deterministic selection boundary.

The product is not trying to establish factual truth. It is trying to create a second line of reasoning defense:

1. Preserve what was actually said.
2. Interpret the reasoning structure without replacing the source.
3. Abstract the reasoning patterns away from case-specific facts.
4. Use deterministic graph machinery to select relevant, challenging, and adjacent mental models.
5. Reattach the real context and ask the reasoning agent to reconsider.
6. Preserve the source, interpretation, pressure, disposition, and revised position for a future reader.

The intended deterministic boundary is therefore:

> Probabilistic systems identify and contextualize reasoning patterns. Deterministic systems transport, connect, select, and account for curated pressure. Deterministic routing must not pretend to interpret the messy conversation itself.

## Evidence And Limitations Of This Assessment

This assessment inspected the current repository at commit `e428a33ccb431fb0e9f374571ea735e65c4311b0` and traced the live flow from `conversation.txt` through extraction, IR construction, four-lane routing, V60, Step 6, archive, and Markdown export.

It also reviewed the recent conversation-understanding baselines, post-run analyses, Product Delta reviews, graph/substrate audits, Decision Trail work, harness PRD, and July 2026 Observatory/agent-memory work.

Focused mechanical verification passed:

- 219 tests across conversation parsing, IR, the three specialist extractors, all four contextual lanes, graph routing, graph survival, and conversation-memory export;
- 86 additional tests across graph fields, routing/tiebreaker behavior, V60, affordance schemas, source custody, and decision-pressure trace structure;
- one test was intentionally skipped.

Important limits:

- The repository contains recent reports and reviews of earlier real runs, but not their underlying `conversation.txt`, `extraction.json`, `result.json`, and related archive files.
- A fresh controlled six-turn synthetic run was completed on 2026-07-09 and is now available locally. One controlled case cannot establish general semantic reliability or product usefulness.
- The reviser for that run had access to a source-first expected-observation document, so the run does not isolate how much of the final improvement came from Lolla rather than from the reviser's prior case analysis.
- No direct-critic, no-graph, labels-only, shuffled-edge, or blinded human-review arm was run for the fresh case.
- The test suite proves specified mechanics, not semantic correctness or product usefulness.
- The repository has no checked-in dependency manifest or CI configuration. The default system Python is 3.9.6, while current Observatory code requires Python 3.12 syntax despite documentation claiming Python 3.10+ support.

### Fresh Controlled Run 01

The first fresh controlled run is archived at:

`/Users/izabela/.local/share/lolla/runs/five-person-saas-company/20260709T201634Z_7a7930`

Its private portable export is:

`/Users/izabela/.local/share/lolla/exports/five-person-saas-company/20260709T201634Z_7a7930/conversation_memory.md`

Detailed source-first assessment:

`research/core-semantic-validation-2026-07-09/run-01-assessment.md`

Run 01 strengthens three conclusions in this PRD:

- Lolla can produce applicable pressure and support an action-level revision, not merely caveat inflation.
- The private Conversation Memory can already preserve a full one-run package with transcript, sources, selection trace, revision, open questions, custody, and non-claims.
- Semantic interpretation and the graph boundary remain the blockers. Two immediate extractions of the identical transcript disagreed about whether board excitement was a live constraint or the dropped thread, and the production extraction lost the user's explicit purchase-commitment challenge from that structured field.

Run 01 also showed that mechanical health must not be used as semantic health. The pipeline was `healthy`, quotes were exact, ledgers were complete, and artifact hashes passed, while the deterministic evaluation still said `warn` / `inspect_first`, trace adequacy was `thin`, future-review readiness was `false`, and the source-first review found material interpretation gaps.

Operationally, the run used 31 OpenRouter calls and 7 OpenAI embedding/query-expansion calls, with an estimated total cost of `$0.03065`. The low monetary cost is attractive; the 38-call architecture and 78,024 OpenRouter tokens still create reliability, latency, and complexity surfaces worth simplifying after semantic value is isolated.

## Current Product Maturity

| Layer | Current state | Assessment |
| --- | --- | --- |
| Raw conversation custody | Built | Strong when capture is complete. `conversation.txt` is archived and can be included verbatim in the private Markdown export. Long-conversation omission remains visible but not solved. |
| Compact extraction | Built and live | Useful for decision, framing, constraints, synthesized position, reasoning passages, and dropped threads. Too compressed to prove full conversation understanding. |
| Provenance-aware IR | Built and live in conservative mode | Good foundation. Default runtime maps several LLM paraphrases to whole-turn or all-user-turn provenance rather than exact supporting spans. |
| Specialist interpretation | Built and evaluated offline | Live constraints, dropped threads, and assistant stance extractors produce better span grounding. They are not wired into normal production runs. |
| Decision Work interpretation contract | Broad target designed; semantic supply only in prepared examples | Captures a much richer decision/process field set. Arbitrary new runs do not receive an automatically generated semantic read; the operator runner defers when it is absent. |
| Decision Work sidecar machinery | Built as internal operator pipeline | Intake validation, brief supply/rendering, triage, resolver packets, dry run, explicit writes, receipts, and blocked/deferred states are implemented. This proves custody and orchestration, not automatic nuanced conversation understanding. |
| Reasoning-pattern abstraction | Partial | Lane 2 explicitly extracts abstract reasoning moves. No complete cross-lane reasoning-pattern artifact exists. |
| Pattern/fact separation | Not enforced | Full factual conversation text and decision summaries influence detection, keyword recall, embedding recall, verification, and relevance ranking. |
| Deterministic graph routing | Built and mechanically tested | Fan correction, route traces, source-backed substrate, and a near-tie matcher exist. Routing remains one-hop, partly lexical, and semantically unvalidated on real cases. |
| Curated pressure substrate | Mature in coverage/custody | All 222 models have source custody; V60 has source-backed affordances and explicit absence records. Coverage does not prove case-level usefulness. |
| Step 6 reconsideration | Built and live | Same orchestrating agent reconsiders using full context plus selected pressure. This is the correct practical skill path for now, but it is exposed to self-anchoring and its ledgers are self-reported. |
| Product delta evidence | Promising but limited | Recent reviewed cases show meaningful shifts. Sample selection, compressed evidence, lack of raw archives here, and limited human validation prevent product proof. |
| Portable Markdown | Built | Includes the full transcript on explicit private download, memo, revised answer, interpretation summaries, lens IDs, survival states, health, and non-claims. It does not yet preserve a complete, source-grounded reasoning interpretation or the full pattern-to-pressure explanation. |
| Cross-run knowledge base | Not a current priority | Correctly deferred until individual run records prove useful. |

## What The Current System Actually Does

### 1. Capture And Extraction

The skill captures a speaker-labeled conversation and calls a monolithic extraction prompt. The live extraction produces:

- decision situation;
- live constraints;
- synthesized position;
- exact assistant reasoning passages;
- first-turn original framing;
- dropped threads.

Reasoning passages are mechanically quote-validated. Most other semantic fields are paraphrases. Their meaning is not independently validated beyond schema and coarse source references.

### 2. Conversation IR

`ConversationContext` preserves full turns and the extraction payload. `ConversationIR` can represent spans, derivations, frames, issues, and assistant stance events.

In the normal runtime, however:

- constraints and dropped threads come from the monolithic extraction;
- they usually carry turn-level rather than exact-span provenance;
- `original_framing` and `decision_situation` are linked to all user turns as synthesized derivations;
- assistant stance events are not populated.

The richer specialist extractors are injectable only in tests, evals, and probe tooling.

### 3. Four Audit Lanes

The four lanes do not all share one clean reasoning-pattern contract.

- Lane 1 uses full user and assistant turns to detect Munger tendencies, then maps a detected tendency and sub-pattern to a primary model and one-hop graph neighborhood.
- Lane 2 extracts abstract assistant reasoning moves, but keyword and embedding candidate recall use both the full assistant answer and those reasoning moves. A verifier then sees factual context, the answer, the moves, and up to 60 candidate models.
- Lane 3 extracts abstract user-frame patterns from the full case and maps those patterns deterministically to reframing models.
- Lane 4 classifies the question and identifies uncovered structural dimensions from the full case, then maps gaps deterministically to models.

The current architecture is therefore better described as:

```text
full conversation -> probabilistic labels -> deterministic mappings and graph expansion
```

not yet:

```text
full conversation -> source-grounded reasoning-pattern IR -> fact-free deterministic routing
```

### 4. Graph And Substrate

The substrate is a genuine asset:

- 222 models;
- 25 tendencies;
- 1,742 knowledge-graph edges;
- 1,358 relationship-graph edges;
- 2,496 precomputed embedding chunks;
- V60 records for all 222 models, including 306 source-backed affordances and 697 absence records.

The graph routing code has improved since the April audit:

- fan-adjusted affinities reduce hub dominance;
- candidate selection and rejection are traced;
- a near-tie activation matcher exists;
- graph-survival reporting preserves selected, suppressed, and unadjudicated signals.

Remaining limitations:

- neighborhoods are one-hop only;
- ally/compound and antagonist/tension semantics are collapsed into two buckets;
- primary tendency binding falls back to lexical matching and then first-list position;
- full-answer relevance scores usually prevent the near-tie activation matcher from running;
- embedding and keyword retrieval can be case-vocabulary-sensitive;
- graph-survival proves custody and uptake, not causal contribution or correctness.

### 5. Reconsideration And Handoff

The skill intentionally skips the pipeline's separate revision API call. The same orchestrating agent performs Step 6 after reading the full conversation and the private pressure table. That is a reasonable practical decision while operating through a subscription skill.

The agent records dispositions for selected private material. Those ledgers prove that every presented item received a declared disposition. They do not independently prove that the item was understood, seriously considered, or causally responsible for a revision.

The private Markdown export is a strong custody surface. On the explicit private route it includes the full archived transcript and labels it as the primary source. It also includes generated interpretation, memo, revised answer, selected model identities, survival states, health, missingness, and non-claims.

Its current limitation mirrors the upstream pipeline: it can only preserve the semantic interpretation that exists. It currently summarizes compact extraction fields and model-selection states; it does not contain a complete source-linked reasoning-pattern record or a transparent pattern-to-model-to-pressure chain.

### 6. Newer Decision Work / Sidecar Path

The newer path is not simply a prettier renderer. It defines a second and broader interpretation target with 46 fields across 11 groups.

Its conversation-interpretation contract groups fields into:

- decision shape;
- options and paths;
- conversation process;
- provided context and evidence;
- stakeholders and values;
- constraints and unknowns;
- audit pressure and change;
- losses and overcorrection;
- evidence and custody;
- brief and agent handoff.

Examples include `live_options`, `option_status`, `assistant_influence_on_user_framing`, `user_changed_mind_during_conversation`, `assistant_sycophancy_or_over-accommodation_risk`, `alternative_frames_considered`, `what_lolla_pressed_on`, `what_changed`, `useful_friction`, `noisy_friction`, `lost_value`, and `overcorrection_risk`.

The implemented chain can:

```text
accept an explicitly supplied generated interpretation read
-> validate its schema, source status, uncertainty, privacy, and non-claims
-> build and render a Decision Work Brief
-> accept or preserve a triage read
-> build resolver and sidecar packets
-> dry-run and explicitly write a decision_work/ sidecar
-> emit receipts and blocked/deferred states
```

It cannot yet:

```text
take an arbitrary newly completed run
-> automatically produce the nuanced semantic interpretation read
```

The offline operator runner explicitly records `semantic_interpretation_generated: false` and stops at `deferred_missing_semantic_read` when a generated read is not supplied. Therefore, the newer path proves a rich schema and safe transport pipeline, but not yet a generally operating second conversation analyzer.

This distinction is central to the next evaluation. We need to compare:

- the semantics the old live path actually produces;
- the richer fields the new path wants to preserve;
- the subset of richer fields already demonstrated in prepared reads;
- the fields that improve mental-model selection;
- the fields useful only after selection for reconsideration or accountability.

## Two-Path Comparison

| Dimension | Path 1: Live Operational Pressure | Path 2: Decision Work / Sidecar |
| --- | --- | --- |
| Primary question | What reasoning structure must the lanes pressure now? | What decision work and audit process should a future reader understand? |
| Timing | Before and during the four-lane audit. | Offline or post-archive, after the run can be inspected as a whole. |
| Normal trigger | Every normal strategic `$lolla` run. | Explicit operator/offline workflow; runtime attachment remains controlled and sidecar-oriented. |
| Semantic producer today | OpenRouter monolithic extraction plus lane-specific LLM calls. | Explicitly supplied operator/Codex-assisted generated interpretation reads for prepared cases. |
| Automatic on arbitrary runs? | Yes, subject to capture and provider availability. | No. Missing generated read produces `deferred_missing_semantic_read`. |
| Main semantic fields | Decision, framing, constraints, synthesized position, reasoning passages, dropped threads; lane-specific tendencies, reasoning moves, frames, and structural gaps. | Decision shape, options, process, assistant influence, values/obligations, constraints/unknowns, audit pressure/change, useful/noisy friction, lost value, overcorrection, evidence/custody, brief and agent handoff. |
| Current graph use | Direct. Full case text and probabilistic labels influence routing and retrieval. | None by default. The path was designed for brief, inspection, triage, resolver, and sidecar supply. |
| Source grounding | Mixed: exact turns and some validated quotes, but important monolithic fields remain paraphrases with coarse provenance. | Contract requires source refs, uncertainty, source status, privacy limits, and review requirements; prepared reads are provisional and often summary-limited. |
| Deterministic machinery | Routes labels, graph neighbors, chunks, thresholds, caps, traces, and health. | Builds packets, validates reads, renders briefs, routes custody states, resolves safe refs, dry-runs, writes sidecars, and emits receipts. |
| Main strength | Actually drives the live pressure product. | Richer interpretation target and unusually careful custody/non-claim boundary. |
| Main weakness | Semantic compression and factual/topic leakage into model selection. | Semantic generation is the missing link; implemented breadth is mostly transport around supplied reads. |
| Main optimization target | Selection quality per unit of latency, cost, and semantic error. | Completeness and intelligibility of the audit trail without overclaim or privacy leakage. |

### Timing Constraint

Some Path 2 fields can potentially improve Path 1 because their underlying meaning already exists before the audit—for example live options, assistant influence, stance lineage, unresolved threads, and alternative frames.

Other Path 2 fields are inherently retrospective and must not drive the original model selection:

- what Lolla pressed on;
- what changed after pressure;
- useful or noisy friction;
- lost value from revision;
- overcorrection caused by revision;
- momentum or ambition loss;
- final-answer non-claims and handoff status.

Those fields can evaluate and explain the pressure path. Feeding them back into the same run's pre-audit selection would create temporal leakage and a self-confirming trace.

### Working Architecture Hypothesis

The most plausible target, to be tested rather than assumed, is:

```text
verbatim conversation
-> small source-grounded pre-audit interpretation kernel
   -> narrow reasoning-pattern projection for deterministic selection
   -> full factual projection for contextual reconsideration
-> completed audit and revised answer
-> richer post-audit Decision Work interpretation
-> sidecar and portable Markdown
```

This shape shares only meaning that genuinely serves both paths. It does not force retrospective accountability fields into the live selection path, and it does not require the sidecar to recompute semantic fields already captured well upstream.

## The Audited Object: A Joint Reasoning Process

The core object is not the assistant answer alone. It is the joint process involving:

- what the user asked and how the question was framed;
- what context, evidence, priorities, doubts, and constraints the user introduced;
- what the assistant asked, assumed, inferred, recommended, challenged, or failed to challenge;
- how the user accepted, rejected, corrected, redirected, or deepened the assistant's contribution;
- which topics, options, and paths were opened, pursued, deferred, abandoned, resumed, or left unresolved;
- how user and assistant positions changed across time;
- what Lolla interpreted as reasoning patterns;
- what deterministic pressure was selected;
- how the revising agent used, rejected, deferred, or privately retained that pressure;
- what the final output preserved, changed, lost, or still left uncertain.

For long conversations, the interpretation must be temporal rather than a bag of extracted facts. It should support questions such as:

- Did a constraint remain active or was it superseded?
- Did the assistant's recommendation remain consistent?
- Did the user express doubt after apparent agreement?
- Did the conversation narrow prematurely around one path?
- Was an abandoned option later reopened?
- Did a late answer ignore an earlier condition?
- Did the assistant challenge the user's frame or reinforce it?
- Did the user's reasoning change because of evidence, persuasion, convenience, fatigue, or an unresolved ambiguity?

### Joint Process Event Model

A practical v0 should model a sequence of source-linked events rather than attempt a complete psychological reconstruction.

Candidate event fields:

- `event_id`;
- actor: `user`, `assistant`, `lolla_audit`, `revising_agent`, or `deterministic_system`;
- event type;
- topic, option, claim, constraint, question, or path affected;
- source turn/span or artifact refs;
- relation to prior events;
- status before and after the event;
- provisional interpretation and confidence;
- whether the event changed the decision frame, evidence state, option state, or recommendation;
- utility class and downstream consumer;
- ambiguity and human-review need.

Candidate event types include:

- question asked or clarified;
- context or evidence added;
- option introduced, compared, chosen, rejected, deferred, abandoned, or resumed;
- constraint introduced, modified, contradicted, or resolved;
- doubt, objection, correction, acceptance, or disagreement expressed;
- claim or recommendation made;
- condition, threshold, evidence gate, or stop rule introduced;
- frame adopted, challenged, or revised;
- topic or concern dropped;
- inconsistency or unresolved tension detected;
- reasoning pattern interpreted;
- mental-model pressure selected;
- pressure applied, rejected, deferred, or kept private;
- recommendation preserved, revised, or retracted;
- lost value or overcorrection flagged.

Absence, omission, sycophancy, influence, useful friction, and depth are not raw events. They are interpretations over event sequences and must carry evidence, uncertainty, and reviewer status.

## Product Object: Reasoning Work Receipt

The executive receiving a polished 30-page memo needs more than the memo. The memo should travel with a compact, inspectable account of the reasoning work behind it.

The repository already has the correct separation of concerns:

- **Decision Trail** should tell the source-linked semantic story of the joint process.
- **Decision Work Receipt** should inventory sources, process evidence, challenge surfaces, custody, health, missingness, and non-claims.
- **Product Delta** should evaluate what changed, whether the change was useful, what value was lost, and where reviewers disagree.
- **Portable Markdown** should compose those layers for a future reader.

The receipt should remain the wrapper. It should not become a third competing semantic interpreter.

### What Can Be Hard-Proven

Lolla can deterministically prove or verify that:

- a specific transcript was captured, with hashes and capture-adequacy status;
- specific source artifacts were present or missing;
- a versioned interpretation artifact was produced;
- emitted quotes and spans resolve to source turns;
- a versioned reasoning-pattern packet entered routing;
- declared deterministic graph rules selected specific candidates and pressure;
- thresholds, fallbacks, caps, suppression, and missingness were recorded;
- selected pressure was presented to the revising agent;
- every presented item received a declared disposition in the ledger;
- a revised answer and memo were persisted;
- the attached receipt refers to the same run and artifacts.

### What Remains Evidential Or Provisional

Lolla can provide evidence—but not automatic proof—that:

- the conversation explored the important option space;
- the user and assistant reasoned deeply;
- the assistant challenged rather than merely performed skepticism;
- selected mental models were appropriate;
- consideration was intellectually serious rather than ledger compliance;
- revision improved the decision;
- useful friction outweighed noise or lost value;
- the final memo is correct, complete, or safe to act on.

These claims require calibrated evaluation and, for serious use, human or domain review.

### Compact Attachment, Not A Single Quality Score

#### V0 Decision

Do not publish an aggregate process-quality grade, tier, score, or green badge in v0.

Publish a **Reasoning Work Receipt** with separate descriptive statuses and drill-down evidence. The receipt may state what was captured, interpreted, challenged, dispositioned, revised, and independently reviewed. It must not summarize those dimensions as `basic`, `good`, `deep`, `high quality`, or an equivalent ordinal judgment.

#### Pros And Cons Of A Grade

| Potential benefit | Corresponding risk |
| --- | --- |
| An executive can scan one label quickly. | The label hides which dimensions are complete, provisional, or missing. |
| Teams can compare work products. | Different decisions, stakes, and domains are not naturally comparable. |
| A grade could motivate people to use better process. | It creates Goodhart pressure to optimize turns, calls, lenses, caveats, or visible disagreement rather than reasoning quality. |
| A badge is easy to market and attach to a memo. | It can be mistaken for correctness, approval, compliance, or safety. |
| A score makes dashboards and thresholds simple. | We do not yet have justified weights or evidence that the score predicts better decisions. |
| A grade could help route review attention. | Descriptive missingness and review statuses can route attention without pretending to measure quality. |

The convenience benefits can be achieved with a compact status vector. The false-authority and metric-mining risks cannot yet be controlled.

The memo-facing summary should be multidimensional. A candidate compact receipt could show:

| Dimension | Example status | Meaning |
| --- | --- | --- |
| Source custody | complete / partial / degraded | Whether the conversation and required artifacts are present and internally consistent. |
| Joint-process interpretation | source-grounded / provisional / incomplete | Whether important process events have traceable evidence and what remains uncertain. |
| Challenge execution | present / partial / failed | Whether declared audit lanes and deterministic pressure actually ran. |
| Pressure accountability | complete / partial / self-reported-only | Whether selected pressure is accounted for and how strong the evidence of uptake is. |
| Revision lineage | traced / partial / unchanged | Whether substantive changes and preserved positions can be linked to pressure and source context. |
| Independent review | none / provisional / human-reviewed / domain-reviewed | Who, if anyone, evaluated usefulness or correctness beyond the producing system. |

Do not average these into one green badge. A single badge would invite the receiver to confuse process completeness with reasoning quality.

The compact claim should be closer to:

> This memo has a complete captured work trail, source-grounded process interpretation, recorded deterministic challenge, and traced revision. Usefulness has not been independently reviewed.

not:

> This memo contains high-quality reasoning.

#### Internal Metrics Policy

Internal evaluation may measure individual components, for example source-grounding precision, critical-event recall, fact leakage, route stability, actionable delta, lost value, reviewer disagreement, and cold-reader recovery.

Those measurements are diagnostics for improving the system. They must not be summed into a public process-quality score. A weak component should remain visible rather than being offset by stronger scores elsewhere.

#### Conditions For Reopening The Grade Question

Reconsider a user-facing grade only after all of the following exist:

- a diverse corpus of real, human-reviewed runs;
- a stable definition of process quality distinct from correctness and effort volume;
- acceptable reviewer agreement on that definition;
- adversarial evidence that long, fluent, or mechanically busy work does not score better merely because it looks expensive;
- evidence that the proposed grade adds decision value beyond the descriptive receipt;
- calibrated behavior across different stakes and domains;
- clear language preventing the grade from being read as approval, certification, or permission to act.

Failure to meet any condition keeps the descriptive receipt as the product boundary.

### Anti-Gaming Rules

The receipt must not reward superficial effort signals:

- more pages do not mean more thought;
- more turns do not mean a better conversation;
- more tokens or model calls do not mean deeper reasoning;
- more mental models do not mean better pressure;
- more caveats do not mean greater rigor;
- a complete self-reported ledger does not prove genuine consideration;
- fluent descriptions of doubt or debate do not prove the underlying process occurred well.

The strongest evidence comes from source-linked changes in the decision process: new evidence sought, an option genuinely tested, a frame revised, a condition added, a recommendation narrowed, a pressure explicitly rejected with a case-specific reason, or a consequential uncertainty kept open.

### V0 Audience Scope: One Run, Output Plus Receipt

Do not decide yet whether the eventual primary consumer is a continuation agent, an inspecting agent, a human executive, a governance reviewer, or a knowledge-base system.

The v0 product unit is one completed Lolla run:

```text
source conversation
-> interpretation and deterministic pressure
-> revised output or memo
-> reasoning-work receipt
```

The receipt should be machine-readable and human-readable because both properties are useful now. Machine readability does not imply a continuation protocol, and human readability does not imply that humans must inspect every detail.

Use one canonical structured record with two views:

1. **Structured view.** Typed, versioned, source-linked, and explicit about missingness, uncertainty, privacy, and non-claims.
2. **Human view.** Short, exception-first, plain-language, and expandable into the same underlying evidence.

The one-run record should include:

- run and schema identity;
- source inventory and hashes;
- complete conversation availability and capture limits;
- joint-process events and trajectory;
- source versus interpretation labels;
- reasoning patterns and deterministic route trace;
- selected pressure and disposition status;
- original-to-revised decision delta;
- unresolved questions and evidence gaps;
- process-health and independent-review status;
- `do_not_infer` non-claims;
- stable artifact locators for drill-down.

The human view should foreground:

- what decision was worked on;
- what materially changed;
- what remains uncertain or disputed;
- whether source custody or interpretation is incomplete;
- whether the process was challenged and revision traced;
- whether any independent human or domain review occurred;
- how to open the full trail when needed.

Humans may value the existence of a receipt even when they do not read the full trail. That creates a talisman risk: the receipt's mere presence can be mistaken for quality assurance. Therefore:

- `not independently reviewed` must be prominent, not buried;
- degraded capture or provisional interpretation must appear in the compact view;
- the receipt must never reduce to a logo, checkmark, color, or unlabeled badge;
- the human summary must link each positive status to the underlying evidence dimension;
- the structured view must not translate process completeness into action authorization.

Explicitly defer:

- how another agent should continue from the run;
- whether the receipt authorizes any downstream operation;
- cross-run comparison or aggregation;
- knowledge-base ingestion behavior;
- organizational review workflows;
- long-term memory or search semantics.

## Core Product Contract

The next version should make the following layers explicit and non-substitutable. This is a logical contract, not a decision that every layer needs its own model call or artifact.

### Layer A: Source Conversation

Canonical artifact: `conversation.txt`

Requirements:

- preserve the human–assistant conversation verbatim and in order;
- preserve stable turn IDs, speaker, hashes, and capture adequacy;
- never replace it with a summary;
- explicitly identify omissions or capture uncertainty;
- tool telemetry remains out of scope unless later cold-reader tests show that a missing tool event removes load-bearing reasoning evidence.

### Layer B1: Pre-Audit Operational Interpretation

Working artifact name: `operational_conversation_interpretation.json`

This is the narrow interpretation needed before the four lanes. It is a fallible, reviewable projection over the transcript and should reuse the existing `ConversationIR` and specialist work.

Candidate fields to test:

- decision question and decision state;
- live constraints, concerns, and open loops;
- assistant stance trajectory: initial position, commitments, conditions, qualifications, deferrals, and revisions;
- user corrections and counter-pressure;
- dropped or under-carried threads;
- reasoning moves and load-bearing claims;
- inference leaps, untested assumptions, tradeoff dismissals, premature closure, and omission candidates;
- original frame and later frame changes;
- unanswered questions and evidence gaps.

This list is deliberately a candidate set. A field belongs in the live path only if it improves selection, pressure contextualization, or health detection enough to justify its latency, cost, and error surface.

### Layer B2: Post-Audit Decision Work Interpretation

Existing contract family: `lolla.decision_work_conversation_interpretation_*`

This is the broader interpretation of the completed conversation and audit process. It can include pre-audit meaning plus fields that do not exist until after pressure and reconsideration:

- live, abandoned, rejected, and deferred options;
- assistant influence on user framing;
- whether the user changed direction;
- sycophancy or over-accommodation risk;
- decision thresholds, stop rules, and evidence gates;
- what Lolla pressed on;
- what changed for action;
- useful and noisy friction;
- lost value and momentum loss;
- overcorrection and generic-caution risk;
- what the final answer does not prove;
- privacy, missingness, human-review, and agent-inspection status.

This path should be allowed to remain richer and slower. Its purpose is not to choose mental models unless a specific field has demonstrated selection value.

Both B1 and B2 must attach, at the appropriate granularity:

- stable item or field ID;
- concise interpretation;
- exact span provenance, validated multi-turn derivation provenance, or explicit artifact refs;
- source speaker and turn references when the source is conversational;
- confidence and ambiguity;
- current, superseded, contradicted, unresolved, or unknown status when applicable;
- interpreter identity and prompt version;
- explicit `needs_review` or human-review requirement.

The raw transcript remains authoritative. Neither path may claim that an interpretation is true merely because it is structured.

### Semantic Field Utility Classes

Before merging, deleting, or reusing either path, classify every field into one of four jobs:

| Class | Consumer | Examples to test | Default policy |
| --- | --- | --- | --- |
| Selection-critical | Deterministic graph routing | reasoning moves, inherited frame, omission mechanism, stance revision, untested assumption | May enter the pattern packet only after abstraction and fact-leak lint. |
| Application-critical | Step 6 contextual reconsideration | actual constraints, user corrections, option state, unresolved question, evidence availability | Reattach after model selection; do not let raw facts drive graph recall. |
| Accountability-critical | Decision Work brief, sidecar, Markdown, future reviewer | what changed, useful/noisy friction, lost value, overcorrection, source limits, non-claims | Preserve after the run; do not feed selection by default. |
| Experimental or unnecessary | No production consumer yet | fields that are duplicative, unreliable, or do not change pressure/review quality | Do not collect in the live path merely because the schema can represent them. |

The desired outcome may be:

- two independent interpretation paths;
- one shared pre-audit semantic kernel with two projections;
- a narrow live path plus a separately generated post-audit enrichment;
- retirement of redundant old fields after the new path proves safer and cheaper;
- retirement of richer fields that do not create measurable value.

The evaluation should choose among these shapes.

### Layer C: Reasoning-Pattern Packet

Proposed artifact: `reasoning_pattern_packet.json`

This is the only case-derived input allowed to drive deterministic graph selection.

It should contain:

- abstract pattern IDs and descriptions;
- pattern family;
- reasoning actor: user, assistant, or interaction;
- reasoning relation: introduced, inherited, challenged, ignored, revised, or resolved;
- mechanism: commission, omission, uncritical acceptance, missed challenge, frame lock, etc.;
- confidence, materiality, and ambiguity;
- source semantic-item IDs;
- pattern relations, such as reinforces, conflicts_with, depends_on, or compounds_with.

It should not contain:

- personal or organization names;
- domain-specific entities;
- raw quotes;
- exact money, dates, quantities, or company facts;
- product/vendor labels;
- the desired outcome;
- persuasive case narrative.

Abstract structural features may remain when they are themselves reasoning-relevant, for example:

- hard deadline present;
- irreversible commitment;
- authority signal treated as evidence;
- missing denominator;
- stakeholder veto not tested;
- one-sided downside treatment;
- no reversal condition.

A deterministic linter should fail the packet if prohibited factual content leaks through.

### Layer D: Deterministic Pressure Trace

Proposed artifact: `pressure_trace.json`

The deterministic system should receive only Layer C and the curated substrate. It should record:

- which patterns entered routing;
- which tendency/model bindings fired and why;
- candidate models and graph paths;
- selected, suppressed, and unadjudicated models;
- relation type and source-backed substrate references;
- embedding use, if any, over pattern text only;
- every threshold, cap, fallback, and rejection reason;
- what was not evaluated because of budget or missing data.

The graph should not claim that a selected model is correct. It should prove only that the selection followed the declared deterministic rules from the supplied reasoning patterns.

### Layer E: Contextual Reconsideration

The full transcript, Layer B1, Layer D, and selected source-backed pressure are reassembled for Step 6. Layer B2 is produced only after the audit and revision exist.

For the current skill product, the same orchestrating agent remains the reviser. A future SDK may test a fresh-context synthesis agent, but that is not required for the next phase.

The revised output must distinguish:

- what survived;
- what was taken back;
- what pressure was considered and rejected;
- what changed in action, threshold, sequence, evidence gate, risk treatment, or decision question;
- what remains unresolved.

### Layer F: Portable One-Run Package

The primary artifact should be a canonical structured record over Layers A–E plus the post-audit Layer B2 interpretation. The private Markdown should be a human-readable projection over that same record, not a substitute or separate source of truth.

It should allow a future reader, human or machine, to recover:

- the complete conversation;
- the system's source-linked interpretation;
- the abstract reasoning patterns sent to the graph;
- the graph selection path and selected pressure;
- the reviser's dispositions;
- the revised answer;
- unresolved questions, missingness, health, and non-claims.

V0 does not specify what that reader should do next. The current structured handoff and Markdown renderer are useful bases, but continuation semantics remain out of scope. They should be strengthened only after Layers B1–D and the relationship between the two interpretation paths are validated.

## Validation Program

The immediate objective is to determine whether the core product works, not to maximize artifact count.

### Phase 0: Recover A Real Evidence Base

Before changing runtime behavior:

1. Import the freshest completed-run archives referenced by the June 26–27 baselines, or rerun equivalent cases.
2. Preserve at least:
   - the six complex baseline cases;
   - four modern extraction-baseline cases;
   - two negative or adversarial cases where Lolla should stay quiet or reject an attractive but irrelevant lens.
3. Freeze a 12-case local-private core corpus with exact artifact hashes.
4. Add a minimal reproducible development environment:
   - explicit supported Python version;
   - dependency manifest;
   - one command for the focused core tests;
   - CI or an equivalent repeatable local gate.

No semantic claim should rely only on checked-in summaries when the underlying run can be recovered.

### Experiment 1: Two-Path Semantic Inventory And Fidelity

For each case, compare the transcript with:

- current monolithic extraction;
- current default `ConversationIR`;
- the three existing specialist extractors;
- the richer Decision Work contract fields;
- any existing prepared generated interpretation read for the case;
- a proposed reasoning-pattern specialist or bounded set of specialists.

For every field in both paths, record:

- whether it exists before the audit, only after the audit, or at either time;
- current source artifact or extractor;
- whether it is actually populated on an arbitrary run;
- source-grounding quality;
- semantic reliability;
- latency and model-call cost;
- current consumer;
- proposed utility class: selection-critical, application-critical, accountability-critical, or unnecessary/experimental;
- whether an equivalent or conflicting field exists in the other path.

Human review should label:

- correctly captured;
- partially captured;
- missed;
- over-inferred;
- wrong speaker/turn;
- wrong current/superseded status;
- materially misleading.

Then test marginal utility rather than assuming richer is better:

- Does adding assistant stance lineage improve pattern detection or only explain the process later?
- Do live options and option status change selected pressure?
- Does assistant influence on user framing improve missed-challenge detection?
- Do thresholds and evidence gates improve selection, contextual application, or only the final trail?
- Are useful/noisy friction, lost value, and overcorrection inherently post-audit accountability fields?
- Which old extraction fields become redundant if a narrower source-grounded field performs better?

The first gate is source fidelity and a defensible consumer for each field, not schema breadth or answer improvement.

Pilot targets:

- zero fabricated quotes;
- 100% of emitted semantic items have valid span or derivation provenance;
- at least 90% of human-identified load-bearing constraints, stance changes, dropped threads, and reasoning moves are preserved;
- no materially misleading interpretation passes without `needs_review` or low-confidence marking.
- no field is promoted into the live path without evidence that it changes selection, contextual application, health detection, or required custody.

These are internal pilot thresholds, not public product claims.

### Experiment 2: Controlled Decontextualization

Create paired cases:

1. **Same reasoning, different facts/domain.** Change names, industry, money, and scenario details while preserving the reasoning structure.
2. **Same facts, different reasoning.** Preserve the scenario but change the assistant's inference, omission, frame handling, or uncertainty treatment.

Expected behavior:

- same-reasoning pairs should produce substantially stable reasoning patterns and graph candidates;
- different-reasoning pairs should produce meaningfully different patterns and pressure;
- prohibited factual tokens should not appear in the pattern packet;
- source provenance should still allow drill-back to the real conversation outside the graph boundary.

Pilot targets:

- zero prohibited factual-field leaks after lint;
- same-reasoning pairs achieve at least 0.70 Jaccard overlap among the top five graph-selected models;
- different-reasoning pairs change at least one primary pattern and one primary pressure route in at least 80% of pairs.

### Experiment 3: Does The Graph Add Value?

Run small, controlled ablations on the same cases:

- current Lolla routing;
- pattern-only deterministic routing;
- graph disabled, using only the directly detected model;
- deterministic random neighbor from the eligible graph neighborhood;
- generic critic prompt without the curated graph;
- embeddings off versus embeddings over pattern text only.

Reviewers should not see which arm produced which pressure. They should judge whether a pressure:

- identifies a real reasoning mechanism;
- challenges rather than restates the conversation;
- adds a non-obvious but applicable lens;
- names an actionable check, gate, alternative, or uncertainty;
- overfits the topic;
- creates noise or caveat theater.

The graph earns its place only if selected pressure beats reasonable non-graph baselines often enough to justify its complexity.

### Experiment 4: Pressure And Revision Quality

For each arm, preserve the original answer, pressure packet, revised answer, and disposition trail.

Use the existing actionable-delta rubric:

- changed action;
- changed threshold;
- changed sequence;
- added evidence gate;
- added stop rule;
- added written term;
- added user question;
- narrowed scope;
- retracted overclaim.

Also preserve:

- useful original value that was lost;
- unjustified overcorrection;
- rejected pressure that should have been used;
- adopted pressure that should have been rejected;
- no-change cases where the original answer appropriately survives.

Pilot targets across the 12-case seed corpus:

- at least 8 cases show material or partial action-relevant improvement;
- no more than 1 case is made materially worse;
- quiet/no-change behavior is accepted when the audit finds no useful pressure;
- every claimed shift is traceable to source conversation plus selected pressure;
- all lost-value disagreements remain visible rather than averaged away.

### Experiment 5: Portable Handoff

Give only the generated private Markdown to context-free reviewers or agents.

Ask them to recover:

- what decision was being discussed;
- what the original assistant recommended;
- which reasoning patterns Lolla identified;
- why each main pressure was selected;
- what changed and what did not;
- what remains unresolved;
- which statements are source, interpretation, selection trace, or revision.

Pilot target:

- at least 80% correct recovery on each required category;
- zero unsupported claims presented as source truth;
- a reviewer can locate the source transcript and relevant evidence without repository knowledge.

### Experiment 6: Reasoning Work Receipt Validity

Test whether the compact receipt communicates process evidence without becoming a quality badge.

Build adversarial pairs:

- long, fluent, many-turn conversation with little real challenge versus a shorter conversation with one decisive evidence test;
- many audit findings with caveat bloat versus one applicable pressure that changes action;
- complete self-reported ledgers with no substantive revision versus a partial but clearly traceable improvement;
- complete process custody with no independent review versus a human-reviewed but operationally thinner trail;
- polished final memo with missing source context versus rougher memo with complete source and revision lineage.

Ask reviewers:

- What is deterministically verified?
- What is provisional interpretation?
- What has been independently reviewed?
- What remains unknown?
- Does the receipt imply that the memo is correct, high quality, or safe to act on?
- Can the reviewer distinguish a complete process from a good process?

Pilot targets:

- at least 90% of reviewers correctly distinguish process completeness from reasoning quality;
- zero receipt fields or labels are interpreted as correctness, certification, or action approval by a majority of reviewers;
- long/shallow work does not receive a stronger summary than short/source-grounded/challenged work merely because of volume;
- every compact status drills down to exact source artifacts, interpretation fields, selection traces, or review records.

## Core-First PR Sequence

### PR-C0: Reproducible Core Evidence Environment

- Declare the supported Python version or restore true Python 3.10 compatibility.
- Add a dependency manifest and focused test command.
- Add a local-private core-corpus manifest with hashes and missing-data status.
- Recover or rerun the freshest 12 core cases.

Exit gate: another maintainer can run the focused mechanical checks and inspect the same real evidence package.

### PR-C1: Two-Path Semantic Utility Map And Shadow Interpretation

- Inventory the old live fields and the newer Decision Work contract fields.
- Classify each field by timing, source, consumer, grounding, cost, and proposed utility class.
- Reuse existing prepared Decision Work reads where available; do not mistake their schemas or validators for automatic semantic generation.
- Reuse `ConversationIR`.
- Run existing live-constraint, dropped-thread, and stance specialists in offline/shadow mode.
- Add reasoning-move and frame/omission items only where the existing IR cannot represent them.
- Persist a narrow pre-audit shadow interpretation plus a broader post-audit Decision Work comparison without changing live lane behavior.

Exit gate: Experiment 1 meets the source-grounding threshold, materially outperforms the monolithic extraction on critical-field coverage, and assigns every retained field a demonstrated consumer. The gate may recommend two paths, a shared kernel with two projections, or retirement of redundant fields.

### PR-C2: Reasoning-Pattern Packet And Fact-Leak Linter

- Define the minimal pattern schema.
- Project the shadow interpretation into abstract patterns.
- Add deterministic privacy/factual-content lint.
- Build same-reasoning/different-facts and same-facts/different-reasoning pairs.

Exit gate: Experiment 2 shows useful invariance and sensitivity without factual leakage.

### PR-C3: Pattern-Only Routing Shadow Mode

- Route graph candidate selection only from the reasoning-pattern packet.
- Keep current runtime output unchanged.
- Record side-by-side current versus pattern-only routes, fallbacks, embeddings, and graph paths.
- Do not yet add multi-hop graph algorithms; first test the boundary with existing routing.

Exit gate: pattern-only selection is at least as useful as current selection and is less topic-sensitive.

### PR-C4: Graph Contribution And Pressure Evaluation

- Run the ablations in Experiments 3 and 4.
- Use blinded review and preserve disagreement.
- Identify whether weaknesses come from pattern extraction, graph mapping, substrate content, contextualization, or Step 6 uptake.

Exit gate: the graph shows measurable incremental value over direct-model and generic-critic baselines. If it does not, simplify rather than adding graph sophistication.

### PR-C5: Gated Runtime Integration

- Integrate the smallest winning shadow path.
- Keep old artifacts for rollback and comparison.
- Add explicit run health for missing/failed pattern extraction, fact-leak lint, and route degradation.
- Continue using the same-agent Step 6 skill flow.

Exit gate: fresh live runs reproduce the offline result without unacceptable latency, cost, or regression.

### PR-C6: Joint-Process Trail And Reasoning Work Receipt

- Extend the Decision Trail with the source-linked joint-process event sequence.
- Keep the existing Decision Work Receipt as the custody/process-evidence wrapper rather than adding another interpreter.
- Link Product Delta status and reviewer disagreement without turning it into a score.
- Add reasoning patterns, route explanations, selected pressure, and revision lineage to the private Markdown.
- Add a compact multidimensional memo attachment covering custody, interpretation, challenge execution, pressure accountability, revision lineage, and independent-review status.
- Preserve the full transcript as canonical source.
- Keep public-safe and private export modes separate.
- Repeat the cold-reader test.

Exit gate: the Markdown and compact receipt are self-explaining and complete enough for a fresh session without implying correctness, quality certification, or approval.

## Explicitly Deferred

Until the core evidence gates pass, do not prioritize:

- cross-run knowledge base, search, comparison, or organizational memory;
- graph database or GraphRAG;
- teacher product expansion or broad mental-model visualization;
- fresh-context SDK synthesis;
- downstream agent continuation or action protocols;
- cross-run receipt aggregation or scoring;
- full tool-call telemetry;
- new risk modes or control-plane integrations;
- more broad accountability schemas;
- additional Observatory polish beyond what the core eval requires;
- more substrate coverage work unless a tested case exposes a specific missing model or source-backed pressure;
- multi-hop graph algorithms before pattern-only routing is proven useful.

## Main Product Risks

### Structured Misunderstanding

The system can create precise artifacts around a wrong interpretation. Source linkage and human-readable uncertainty are more important than schema completeness.

### Topic Leakage Masquerading As Reasoning

Embeddings and keyword overlap can select models because the case talks about markets, authority, risk, or systems—not because the reasoning actually exhibits the relevant pattern.

### Graph Theater

A large curated graph can look rigorous without adding more useful pressure than direct labels or a good critic prompt. Ablation is mandatory.

### Revision Theater

The same agent can absorb audit language, add caveats, and appear reflective without changing the user's decision quality. The actionable-delta and lost-value reviews must remain central.

### Custody Mistaken For Quality

Run health, hashes, complete ledgers, and clean Markdown prove that the process ran and artifacts survived. They do not prove that the advice is good.

### Building The Future Before Proving The Run

Cross-run memory, teacher surfaces, agent SDKs, and organizational comparison could all be valuable later. None is justified until one run reliably understands, pressures, revises, and explains a serious conversation.

## Current Decision

The project should enter a **Core Semantic Validation** phase.

V0 scope is locked to one run. One conversation enters Lolla; one revised output or memo and one reasoning-work receipt leave it. The receipt makes the work inspectable but does not define how a later agent, human, organization, or knowledge system must use it.

The phase is successful when Lolla can demonstrate, on a small fresh corpus, that it:

1. preserves the conversation;
2. produces a faithful, source-grounded temporal interpretation of the joint user–assistant process;
3. distinguishes live selection fields from reconsideration and retrospective accountability fields;
4. abstracts reasoning patterns without case-fact leakage;
5. routes those patterns deterministically into useful pressure;
6. improves or appropriately preserves the answer while retaining lost-value and disagreement evidence;
7. hands the whole process to a cold future reader;
8. attaches a reasoning-work receipt that proves observable work without claiming correctness or quality certification.

Only after that should the project decide how to package, scale, search, teach, or expose the accumulated run records.

## July 10 Evidence Addendum

The initial semantic-validation and downstream-control program is complete
enough to narrow the next step.

- SK3 remains the offline semantic base; SK4 pressure variants failed their
  locked gates and prompt-tuning stop rule.
- Sixteen pressure observations are source-reviewed. The rest of the 102-item
  legacy set remains pending and cannot promote runtime work.
- System-level concept coverage is materially higher than family-aligned
  placement, so future evaluation must keep C1 coverage, C2 role, and C3
  chronology separate.
- The first strong-control downstream pilot found no unique treatment advantage
  on the obvious enterprise-beta case.
- The quiet consulting pilot found a provisional treatment advantage in
  calibrating unsupported numeric authority without changing the action or
  adding public bloat.
- The Case 07 counterfactual blocked full semantic-overlay handoff: the actual
  27-event overlay was worse than transcript-only control; adding the reviewed
  omitted self-correction repaired the weakness but did not beat control.

The product architecture is therefore narrower:

```text
raw transcript = authoritative reasoning context
semantic inventory = audit/navigation/receipt substrate
reasoning-pattern packet = small fact-free graph input
graph output = candidate recall, not applicability judgment
case-local pressure = small probabilistic consumer projection
deterministic code = evidence, schema, caps, graph replay, hashes, custody
```

Do not integrate the semantic inventory into Step 6. Do not add another reader
or deterministic semantic gate. `reasoning-pressure-handoff-v0` now expresses
the active working-set slice: no more than four pressure items and four
preservation items beside the authoritative full conversation. It is not the
whole consumer. The complete research shape already exists in
`step6_attention_map.v1`: active pressure plus compact edge/latticework, weak,
negative-space, parked, and expansion-ref layers under delayed rejection.

The enterprise-beta active slice is materially smaller than the blocked
overlay and has real mechanical lineage. The next evidence question is whether
the restored portfolio preserves off-frame possibility without recreating a
context dump, and whether exact human review finds any false stand-down,
forced absorption, or missing edge pressure. A paid non-obvious downstream
test follows only after that no-call reconciliation.
