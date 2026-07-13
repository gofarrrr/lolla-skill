# Product Delta / Eval Docs Index

Status: GitHub-facing eval navigation

This directory contains the evidence and evaluation layer around Lolla. The
main thing to understand is the split between the live skill and the offline
eval lane.

```text
Lolla runtime:
  captures a serious conversation
  runs the reasoning audit
  produces a revised decision answer
  archives custody artifacts

Product Delta eval lane:
  reads existing safe artifacts later
  checks whether cases are reviewable
  prepares provisional review packets
  preserves uncertainty and disagreement
  lints against overclaiming
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies that object
later. The eval lane does not run `$lolla`, invoke the skill, call providers,
mutate archives, change prompts, change runtime behavior, score answer
quality, create automatic labels, or authorize agent action.

## Current reasoning-audit controls

The newer core reasoning-audit program has a separate, narrower reader path
from the historical Product Delta lane above:

1. [Product constitution v3](../conversation-understanding/lolla-product-constitution-v3.md)
2. [Evaluation doctrine](../conversation-understanding/lolla-evaluation-doctrine-v0.md)
3. [Product measurement map](lolla-product-measurement-map-v0.md)
4. [Extraction call custody contract](extraction-call-custody-contract-v0.md)
5. [Two-stage holdout protocol](reasoning-portfolio-two-stage-holdout-protocol-v0.md)
6. [Eight-gate evidence roadmap](lolla-eight-gate-roadmap-v0.md)
7. [Public revision / private receipt eval boundary](public-revision-private-receipt-boundary-v0.md)
8. [Graph pressure shadow custody](graph-pressure-shadow-custody-v0.md)
9. [Reasoning Run Receipt v2](reasoning-run-receipt-v2.md)
10. [Conversation-State Handoff v1](../conversation-understanding/conversation-state-handoff-v1.md)
11. [Structured extraction practices — July 2026](../conversation-understanding/structured-extraction-practices-july-2026.md)
12. [Conversation-state extraction recovery plan](../../plans/conversation-state-extraction-recovery-2026-07-11.md)
13. [OpenRouter/Gemini structured-extraction field note](../conversation-understanding/structured-extraction-field-note-2026-07-11.md)
14. [Structured-output problem-class research](../conversation-understanding/reasoning-process-structured-output-problem-class-research-2026-07-12.md)
15. [Ground-up reasoning-process evidence audit](../conversation-understanding/reasoning-process-ground-up-evidence-audit-2026-07-12.md)
16. [Position decomposition v1 result](../conversation-understanding/reasoning-process-position-decomposition-result-2026-07-12.md)
17. [Position role-first v2 result](../conversation-understanding/reasoning-process-position-role-first-v2-result-2026-07-12.md)
18. [Role-first fragmentation problem-class research](../conversation-understanding/reasoning-process-role-first-fragmentation-problem-class-2026-07-12.md)
19. [Role-first model-control result](../conversation-understanding/reasoning-process-role-first-model-control-result-2026-07-12.md)
20. [Position role-first v2.1 result](../conversation-understanding/reasoning-process-position-role-first-v21-result-2026-07-12.md)
21. [Affordable semantic operator selection](simulated-reliability-v1-affordable-model-selection-result-2026-07-13.md)
22. [Case 01 affordable full-nine source review](../../research/simulated-reliability-v1-lite-factored-case01-completion-2026-07-13/r1/source-review.json)
23. [Residual Challenge Representation v1](../conversation-understanding/residual-challenge-representation-v1.md)
24. [Affordable full-nine and residual-challenge result](affordable-full-nine-and-residual-result-2026-07-13.md)
25. [Corrected residual-seed fresh-consumer handoff](residual-seed-fresh-consumer-case01-result-2026-07-13.md)
26. [V1 final constitutional reassessment](simulated-reliability-v1-final-constitutional-reassessment-2026-07-13.md)
27. [R1/R2 constitutional hardening result](../conversation-understanding/lolla-r1-r2-constitutional-hardening-result-2026-07-13.md)
28. [R3 fresh-consumer result](../conversation-understanding/lolla-r3-fresh-consumer-result-2026-07-13.md)
29. [R3 provider-schema repair result](../conversation-understanding/lolla-r3-provider-schema-repair-result-2026-07-13.md)

Affordable-operator checkpoint, 2026-07-13: Gemini 3.1 Flash Lite on the pinned
Google Vertex OpenRouter endpoint is the current testing candidate for small,
decomposed semantic jobs. The initial operator-selection investigation used 21
calls and `$0.042771112`; the later two-case full-nine validation brought the
cumulative affordable campaign to 50 calls and `$0.076058862`, including every
preserved failure and both residual-discovery variants. Separate role work,
qualification review followed by bounded detail, factored user-mechanism
judgment, separate assistant coverage, and deterministic status/routing joins
are the current reference. Full-nine stand-down restraint passed on Case 07.
Case 01 then passed mechanism and evidence fidelity but falsely stood down
relative to the broader product review because the useful residual challenge
was absent from the role/mechanism representation. Two residual variants did
not cleanly recover the protected long-horizon opportunity; prompt tuning is
stopped. Coverage is now receipt metadata rather than a graph-admission gate,
and a provider-free deterministic correction preserves every valid seed for
direct and graph recall. This is not production selection. Gemini 3.5 artifacts
remain premium comparison evidence; no routine development call should use
Gemini 3.5. No further provider call is authorized until the corrected fresh-
consumer handoff passes locally.

That provider-free handoff now passes: the full conversation, three residual
seed questions, six direct candidates, three graph candidates, and an
inspectable 26-candidate reserve are preserved under exact custody. The active
consumer must apply, reject, or park all nine candidates; coverage metadata has
no suppression authority. No call was made. A future validation is limited to
one Gemini 3.1 Flash Lite call and `$0.01`; Gemini 3.5 remains a preserved
premium benchmark, not a routine testing model.

Newest checkpoint: the first provider-free decomposition passed locally but
failed its reserved agency-acquisition probe after one call. The role-trajectory
reader contradicted its own starting evidence, omitted a protected
qualification, and exposed a false-complete empty join. The prospective
role-first v2 repair now passes eight reviewed cases and adversarial custody
with a four-call ceiling, but it has no model-backed evidence. All existing
position cases are exposed, so no additional provider call is authorized until
a new ambiguous multi-turn case is frozen before execution. That case was then
created with a protected target. DeepSeek served four structurally successful
calls but fragmented all roles and lost the protected qualification; GLM 5.2
ran the unchanged stronger control and returned empty starting and qualification
roles. Model shopping is stopped. Provider-free v2.1 now clarifies endpoints,
coherent record identity, components, coverage, and speaker ownership while
leaving schemas and validators unchanged. It passes nine reviewed cases but has
no model-backed evidence.

These controls may use explicitly frozen provider-backed experiments. They do
not change the older Product Delta lane's read-only contract. The current stop
line is simple: extraction custody and the Case 01 smoke passed; Case 05
preserved a formal runner/sealer mismatch; the prospective shared-field repair
passed; and the next-ranked Case 10 passed full Stage A plus source-first
pressure review. Its complete paired contract was then frozen and executed
exactly once per arm. Mechanical custody passed, and the blind review found
accountable-consideration and correct-stand-down value but no unique answer
improvement. The pair is closed. Only a provider-free graph-attribution
preflight was authorized. That preflight is now complete: graph relationships
do reach Step 6 inside companion anchors, but no exact graph-derived item was
isolated in the frozen treatment and no graph chunk had individual disposition
custody. A paid Case 10 graph ablation is blocked. Only a provider-free search
for a different eligible case was authorized. That search is now complete:
six comparable July cases produced zero eligible graph-specific candidates.
Paid Gate 6 remains blocked pending a new holdout. A provider-free shadow
exporter now gives relationship chunks exact hashed identities without changing
runtime or claiming relevance. Gate 7 then built and froze a self-contained
Case 10 receipt and executed exactly one fresh-reader call with no retry and no
evaluator. The call passed its mechanical contract and reconstructed the main
reasoning history, but source-first review found source-sequence loss,
proof-of-work inflation, overly broad graph non-use language, and human-question
ambiguity. Gate 7's agent half is therefore a partial pass. Human feedback is
still pending. Its observed defects are now repaired prospectively in the
provider-free Reasoning Run Receipt v2 contract, including an explicit source-
end action/deadline, bounded custody language, authorization snapshot scope,
question-audience separation, graph claim levels, duplicate rejection, and a
valid empty-pressure outcome. The neutral inventory then found no safe untouched
core case: the only mechanically remaining case is the pre-excluded high-risk
whistleblower scenario. No new Stage A call is authorized.

Gate 7 instead applied v2 to the already-closed Case 06 accountability failure
without rerunning the pipeline. The first assembly attempt stopped when real
evidence exposed missing exact pair, pressure-identity, effect-consistency,
partial-token, and V60-origin fields; those were repaired before any receipt or
reader call. A self-contained receipt was then validated and given to one fresh
reader under a frozen no-retry, no-evaluator contract. The reader preserved the
central correct-standdown-plus-accountability-failure story, bounded custody,
graph non-claim, and as-of authorization. It still lost the explicit no-
deadline state, a material final user inference, exact lineage subtype, and
exact operating figures. The Case 06 result is a second and stronger partial
agent-transfer observation, not a full Gate 7 pass. Human usefulness is now the
next Gate 7 evidence need. A separate new safe fixed holdout is required before
causal or graph work. Gate 8, paid graph testing, and runtime integration remain
blocked.

The first neutral attempt to create that new source pool is also closed. Five
low-risk domains and a hash-derived ranking were frozen before generation. V1
failed on unsupported provider configuration; v2 generated five complete cases
but failed an over-strict message-ID scorer whose exact pattern was absent from
the prompt; v3 moved canonical IDs into deterministic code and then received a
preserved provider rate-limit error. No automatic retry or evaluator was used,
no case was selected, and the v2 text is not promoted post hoc. The next causal
prerequisite is founder-provided or otherwise genuinely new safe conversation
source material under a fresh intake contract—not another call against the
closed pool.

A separate founder-directed development corpus now provides five realistic,
ambiguous, seven-pair conversations. These are same-session synthetic fixtures,
not clean holdouts. Deterministic capture wrappers fixed an initial missing-
header defect, and the Stage A runner now freezes a compatible interpreter.
The third ranked case completed the full pipeline but formally failed an
understated core-call subbudget. Its source-first review found two plausible raw
pressure candidates alongside substantial repetition, forcing, unsupported
assumptions, malformed companion verification, and a V60-to-Step-6 transport
failure. The zero-call V60 transport repair is complete; downstream answer
testing remains blocked. Provider failure custody and the call-envelope repair
are now complete, and extraction quality has been measured across all five
designed cases. The extractor reliably understands the broad decision and
grounds passages, but it collapses joint proposal ownership, retains only
18/43 reviewed load-bearing constraints, and misclassifies all five extracted
dropped threads. The minimal conversation-state representation and provider-
free replay are now complete: five joint positions, five corrected thread
dispositions, 43 reviewed constraints, 88 exact source refs, and zero direct
graph seeds. This proves capacity, not automatic extraction. Provider-free
recovery work is now also complete: one typed source generates local and
OpenAI/Gemini projections; all 70 messages receive stable source custody; three
shallow microtask contracts feed a deterministic ledger and fail-closed
compiler; and five reviewed cases reassemble with late-turn trajectory intact.
Splitting two legacy `mixed` records produces 45 atomic constraints. Four
adversarial fixtures fail at the expected parser, custody, or absence boundary.
No provider, graph, or runtime call was made, so automatic extraction and
provider acceptance remained untested at that checkpoint. The subsequently
authorized Case 02 microtask probe is now closed informative failure. Its
positions call reached inference but stripped every `span-` prefix, causing all
three candidates to be quarantined, and again fragmented the reviewed joint
trajectory. Its thread call received HTTP 400 from Google AI Studio through
OpenRouter before inference; the frozen stop rule prevented the constraint
call. Two calls were attempted, no retry occurred, and no graph, pipeline,
evaluator, or runtime surface was touched. A future transfer repair requires a
new contract and authorization. That Case 05 transfer was subsequently
authorized and is now also closed. Replacing the nullable type array with
`anyOf` and adding a source-specific span-ID enum still produced HTTP 400 before
inference on the first thread call; the stop rule prevented constraints and
positions. This falsifies the nullable representation as a sufficient repair
without measuring semantic transfer. The next prospective experiment should
use JSON object mode with the exact schema in the prompt and retain all local
typed, source-custody, ledger, and quarantine gates. The delegated program then
completed that JSON-mode experiment and two prospectively frozen repaired
transfer cases. Transport and deterministic custody worked, but zero of three
cases passed every semantic family; strict constraint recall stayed at
0.20–0.22, source strength was inflated, thread trajectories remained
unreliable, and current positions were fragmented or polluted by adjacent
reported disagreements. The material-redesign stop fired after 9 calls and
$0.02172925. The current one-call-per-family design is closed and must not be
integrated or tuned further. The two-case
extraction-only probe was separately frozen with zero retries, a $0.02 ceiling,
truthful provider-failure custody, and six source-first axes. Its execution
lineage is now closed failed. Two deep provider-schema requests were rejected
before inference; JSON mode then exposed a missing formatting-schema defect and
finally the real Case 03 extraction failure. The packet failed joint ownership,
focal resolved-thread recall, atomic source strength, constraint coverage, exact
quote grounding, and assistant Turn 7 trajectory. Case 04 was not called. No
graph or full pipeline is authorized. See
`research/designed-ambiguous-pool-v1-2026-07-10/` and
`research/stage-a-amb1-case04-2026-07-10/`, plus
`research/designed-extraction-quality-v1-2026-07-10/` and
`research/conversation-state-handoff-v1-2026-07-10/`, and
`research/conversation-state-extraction-probe-v1-2026-07-11/` through
`research/conversation-state-extraction-probe-v4-2026-07-11/`, and
`research/conversation-state-recovery-v1-2026-07-11/`, plus
`research/conversation-state-microtask-probe-v1-2026-07-11/` and
`research/conversation-state-microtask-probe-v2-2026-07-11/`, plus the terminal
program decision at
`research/conversation-state-extraction-program-conclusion-2026-07-11/`.

## Big Picture

Lolla is trying to sit between fluent AI advice and real action.

The product question is not:

```text
Did the second answer sound better?
```

The product question is:

```text
Did structured audit pressure create a decision-useful delta that a reviewer
can inspect without pretending certainty?
```

That means the eval lane cares about concrete changes:

- action changed;
- threshold changed;
- sequence changed;
- evidence gate or stop rule appeared;
- scope narrowed;
- overclaim was retracted;
- a stakeholder, value, constraint, or unresolved question was preserved;
- uncertainty became visible in a way that matters.

It also cares about losses:

- useful original advice got weakened;
- ambition or momentum was buried under generic prudence;
- Lolla added process without leverage;
- the revised answer became longer but not more actionable;
- the system misunderstood the conversation;
- a clean artifact made weak evidence look stronger than it is.

## What To Look For

When reading Product Delta artifacts, look for:

- `vanilla_likely_next_action`: what the user seemed likely to do before Lolla;
- `lolla_likely_next_action`: what the revised answer seemed to make more likely;
- `material_difference`: whether the candidate delta changes a decision-relevant thing;
- `structural_delta`: action, threshold, sequence, gate, stop rule, scope, written term, or question changes;
- `useful_friction`: pressure that changes action or review burden in a useful way;
- `noisy_friction`: caution, delay, or structure that does not add decision leverage;
- `lost_value`: what the revised answer may have weakened or overwritten;
- `interpretation_adequacy`: whether Lolla and the reviewer understood the conversation well enough;
- source refs, field statuses, missingness, and uncertainty notes;
- human follow-up questions and falsification notes.

The healthiest current Product Delta signal is not a bigger win count. It is a
downgrade:

```text
accept-operations-role-startup
material_improvement_candidate -> partial_improvement_candidate
```

That downgrade matters because the specialist review preserved lost value,
value-overwrite risk, user-specific ambition, and written-gate proportionality
uncertainty instead of laundering a broad positive read into a smoother
conclusion.

## What Not To Infer

Product Delta artifacts do not prove:

- Lolla improves decisions;
- Codex-assisted reads are human labels;
- a judge is calibrated;
- clean artifacts imply good advice;
- a candidate label is ground truth;
- an agent may act on the revised answer;
- a lint-clean package is product proof.

Current Codex-assisted reads are provisional, internal, and lower-claim. Human
review later must validate, correct, or reject them.

## How We Evaluate

The current non-human phase uses four layers:

1. **Protocol and taxonomy.** Define what counts as a candidate product delta,
   useful friction, noisy friction, lost value, interpretation adequacy, and
   failure.
2. **Read-only deterministic tooling.** Build readiness reports, review shells,
   specialist packets, and boundary lint from existing safe artifacts.
3. **Context-engineered specialist reads.** Decompose broad judgment into
   narrow provisional reads, such as conversation interpretation, likely next
   actions, structural delta, friction/lost value, and overclaim risk.
4. **Conservative fan-in.** Preserve disagreement, downgrade pressure,
   missingness, and human follow-up questions without voting or scoring.

The point is not to create an LLM judge. The point is to make provisional
interpretation more inspectable.

## Safe Commands

Build a read-only Product Delta readiness report and PR72-shaped shells:

```bash
python3 scripts/evals/build_product_delta_provisional_review.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --out /tmp/product_delta_readiness.md \
  --json-out /tmp/product_delta_readiness.json
```

Build checked-in-safe specialist packets from existing eval artifacts:

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --limit 2 \
  --out /tmp/product_delta_specialist_packets.json
```

Run deterministic boundary lint over selected Product Delta artifacts:

```bash
python3 scripts/evals/lint_product_delta_evidence.py --paths \
  docs/evals/product-delta-provisional-report-v0.md \
  reviews/codex-assisted/product-delta-batch-v0/review.json \
  reviews/codex-assisted/specialist-review-batch-v0/review.json \
  reviews/codex-assisted/fan-in-disagreement-report-v0/report.json
```

Run the focused Product Delta tests:

```bash
python3 -m pytest -q \
  tests/test_product_delta_pr71_pr84_package_gate.py \
  tests/test_product_delta_fan_in_disagreement_report.py \
  tests/test_codex_assisted_specialist_review_batch.py \
  tests/test_provisional_reviewer_trap_set.py \
  tests/test_product_delta_specialist_packets.py \
  tests/test_product_delta_specialist_contracts.py \
  tests/test_product_delta_boundary_lint.py \
  tests/test_product_delta_batch_fixture.py \
  tests/test_product_delta_readiness.py
```

These commands are read-only against the Lolla runtime. They do not run the
skill, call providers, mutate archives, or create product proof.

## Current Phase Map

Start with these:

| File | Purpose |
|---|---|
| [Product Delta Evidence Thesis](product-delta-evidence-thesis-v0.md) | The PR71 claim, baseline, lower-claim doctrine, and Product Delta vocabulary. |
| [Product Delta Evidence And Interpretation Adequacy](product-delta-evidence-and-interpretation-adequacy-v0.md) | The bridge from audit machinery to product-delta evidence and why conversation interpretation is load-bearing. |
| [Vanilla-vs-Lolla Provisional Review Protocol](vanilla-vs-lolla-provisional-review-protocol-v0.md) | The PR72 review protocol and field shape. |
| [Product Delta Provisional Report](product-delta-provisional-report-v0.md) | PR77's report over readiness and broad Codex-assisted provisional reads. |
| [Product Delta Evidence Boundary Lint](product-delta-evidence-boundary-lint-v0.md) | PR78's deterministic non-claim and privacy-boundary lint. |
| [Context-Engineered Provisional Review Architecture](context-engineered-provisional-review-architecture-v0.md) | PR79's rejection of a broad judge in favor of bounded specialist reads. |
| [Product Delta Specialist Review Contracts](product-delta-specialist-review-contracts-v0.md) | PR80's typed contracts for specialist reads and fan-in. |
| [Product Delta Specialist Packet Builder](product-delta-specialist-packet-builder-v0.md) | PR81's read-only packetization stage. |
| [Provisional Reviewer Trap Set](provisional-reviewer-trap-set-v0.md) | PR82's checked-in-safe traps for thin context, length bias, lost value, and overclaim hardening. |
| [Codex-Assisted Specialist Review Batch](codex-assisted-specialist-review-batch-v0.md) | PR83's trap discipline and two-case specialist batch. |
| [Product Delta Fan-In / Disagreement Report](product-delta-fan-in-disagreement-report-v0.md) | PR84's static comparison of broad PR76 reads and specialist PR83 reads. |
| [Product Delta PR71-PR84 Packaging Gate](product-delta-pr71-pr84-packaging-gate-v0.md) | PR85's package manifest, validation boundary, useful signal, and unresolved risk. |
| [Product Delta Evaluation Readiness PRD](product-delta-evaluation-readiness-prd-v0.md) | PR235's eval-phase PRD: summarize existing Product Delta, Human Review, and Review Corpus lanes; preserve the downgrade signal; reject live judging as the immediate move; and choose a balanced offline Product Delta evidence batch next. |
| [Balanced Offline Product Delta Evidence Batch Plan](balanced-offline-product-delta-evidence-batch-plan-v0.md) | PR236's plan-only balanced-batch slice: define buckets, source rules, privacy/custody rules, check-in policy, anti-overclaim rules, and the candidate-selector plan gate without selecting cases or running a batch. |
| [Balanced Batch Candidate Selector / Readiness Builder Plan](balanced-batch-candidate-selector-readiness-builder-plan-v0.md) | PR237's plan-only selector/readiness-builder slice: define safe source signals, bucket hypotheses, readiness criteria, output shape, refusal/defer statuses, and anti-flattery rules before any selector implementation or Product Delta batch run. |

## Runtime And Skill Opportunities

From the skill perspective, the eval lane shows which runtime artifacts matter
most for future review:

- `agent_result.json` for compact run status, caller action, artifact refs, and
  product-level summary fields;
- `evaluation.json` for deterministic artifact/schema/custody/health checks;
- `reasoning_trace.json` for local custody, path/hash references, run health,
  usage, and model-call metadata without duplicating raw transcript text;
- review-corpus exports for case selection and human-review queues;
- audit decision records for safe accountability shells;
- Product Delta packets for narrower future interpretation reads.

The opportunity is to keep improving what the runtime preserves so later
reviewers can inspect decision deltas without raw/private leakage or fake
certainty. That does not require making Product Delta eval part of the live
skill. For now, the split is intentional.

## Current Stop Line

The PR71-PR85 non-human Product Delta phase is packaged. It is coherent enough
to inspect, lint, and use as internal scaffolding. It is not broad enough or
human-reviewed enough to claim product proof.

The new Product Delta Evaluation Readiness PRD keeps that boundary and selects
a balanced offline evidence batch before any live evaluator. The next PR should
plan that batch rather than build a live judge.

The Balanced Offline Product Delta Evidence Batch Plan now defines that batch
shape. The next PR should plan the candidate selector/readiness builder rather
than run Product Delta review.

The Balanced Batch Candidate Selector / Readiness Builder Plan now defines how
a future deterministic selector should choose candidate cases from explicit
safe source scopes, existing metadata, provisional labels, specialist fan-in,
human-review taxonomy hints, run-health/capture metadata, and review-corpus
readiness metadata. It stops before selector implementation, broad archive
scans, Product Delta review runs, model/provider calls, live judging, answer
scoring, or product-proof claims.

Good next moves later include:

- human-review intake over the current packets and reports;
- local-private packet mode for deeper interpretation adequacy review;
- a larger specialist batch that includes no-change, noise, worse, and
  inconclusive real cases;
- more trap fixtures if a specific failure mode repeats.

Do not expand this lane just to create more artifacts. New work should answer a
specific evidence question.

## Conversation-event A–E result — 2026-07-11

The small-window harvesting plus fresh-synthesis architecture is closed as
**material redesign required**. Provider-free custody passed, but three
overlapping harvest lenses created 88–95 events per fourteen-message case and
global synthesis failed after one generic repair. Current deterministic custody
compiles one of three cases and quarantines two; zero cases clear the semantic
end-to-end gate. Graph and runtime work were not run.

Use these as the continuation entrypoints:

- `research/conversation-event-a-e-conclusion-2026-07-11/result.md`;
- `research/conversation-event-a-e-conclusion-2026-07-11/decision.json`;
- `plans/conversation-event-architecture-a-e-2026-07-11.md`.

The next research target is bounded probabilistic consolidation at the local
window, with local source-strength classification and an explicit global fan-in
budget. It is not another prompt repair of the closed design.

## Turn-record redesign result — 2026-07-11

The bounded local-consolidation goal is also terminal. Both candidate
representations passed five-case provider-free replay but failed a one-case
model comparison and its single generic repair. The single reader met the repair
budgets only by losing reviewed signals; the three-lens consolidator retained
operational/custody failures and also lost thread and claim-strength targets.

No transfer or global synthesis was authorized. The next question is a product
boundary, recorded in
`research/conversation-turn-record-redesign-conclusion-2026-07-11/decision.json`:
whether broad accountability capture and compact reasoning input should become
two linked artifacts rather than one record serving both.

## Reasoning-process ledger and bounded views — Phase 2 result — 2026-07-11

The two-artifact direction has now passed its provider-free Phase 2 gate. Five
source-reviewed conversations have 25 bounded process-view fixtures with exact
lineage and complete dispositions. The coverage audit found 11/25 targets with
any Phase-1 span overlap but only 1/25 with a fully adequate inherited semantic
observation, so 24 missing targets were added prospectively through append-only,
non-independent source-review addenda. The Phase-1 ledgers were not modified.

Target-blind probe packets always retain the full conversation, never contain
the protected answers, and include the auxiliary ledger only as a complete
all-or-none budget unit. All development packets fit below 16,813 bytes. A real
24-message stress packet fits at 21,307 bytes by omitting its complete optional
32-observation ledger rather than selecting a semantic subset. No model,
embedding, graph, evaluator, pipeline, or runtime call was made.

Use these continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-bounded-views-v1.md`;
- `plans/reasoning-process-ledger-and-bounded-views-2026-07-11.md`;
- `research/reasoning-process-phase2-views-2026-07-11/report.json`.

The next step is a prospectively frozen one-case, five-job bounded development
probe. This result does not authorize graph or runtime integration and does not
measure final-answer quality, reasoning quality, effort, or trust.

## Reasoning-process bounded readers — Phase 3 result — 2026-07-11

The one-case Gemini/OpenRouter development probe is complete with **material
redesign required**. The baseline stopped after a third-call OpenRouter rate
limit; its two reviewable views showed one protected target and one earlier
alternative lost to salience. The single allowed generic repair then completed
all five calls and improved protected-target visibility to 4/5, but only 4/5
outputs were admitted. Exploration used a non-contiguous ellipsis quote and
still omitted the protected limiting condition. One admitted position item also
overstated its cited evidence.

The frozen gate therefore fails: 28/29 exact source references, one invalid
admitted item, one source-strength inflation, one context-invisible label, and
one critical dimension at zero. No second repair or Phase-4 transfer is
authorized. Total custody is eight provider requests and $0.018682 estimated,
with zero automatic retries, fallbacks, evaluator, embedding, graph, pipeline,
or runtime calls.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-phase3-development-result-v1.md`;
- `research/reasoning-process-phase3-development-2026-07-11/decision.json`;
- `research/reasoning-process-phase3-development-2026-07-11/result.md`.

The next work is provider-free design of five view-specific semantic contracts
and a lossless sentence-span evidence table. It is not another universal prompt
repair, global synthesis layer, graph experiment, or runtime integration.

## Reasoning-process view-specific redesign — 2026-07-11

The failure-derived redesign sequence is closed with a narrower decision.
Stable sentence aliases fixed the former quote-custody failure: the first
view-specific probe produced 61/61 valid citations, and a compiler-only replay
admitted all five unchanged payloads. Relationship-explicit v2 contracts then
passed 15/15 source-reviewed fixtures and append-only compilations across the
five development cases.

On Case 02, position, evidence discipline, unresolved state, and challenge
response now pass development source review. Exploration does not. A targeted
chronological call recovered the earlier named-role alternative but again lost
its attached “not all required ownership” qualification. A conversation-only
ablation recovered neither, so auxiliary-ledger anchoring is not supported as
the root cause. The ablation also showed that provider schemas must omit
auxiliary-ID fields when no auxiliary ledger is supplied.

All five v2 calls returned `false` for a schema field declared `const: true`.
The field represented whether omitted observations remain parked. That is now
classified correctly as deterministic custody policy, not a model-authored
semantic choice, and should disappear from future provider schemas.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-view-specific-development-result-v2.md`;
- `plans/reasoning-process-ledger-and-bounded-views-2026-07-11.md`;
- `research/reasoning-process-view-specific-v2-probe-2026-07-11/source-review.json`;
- `research/reasoning-process-exploration-v4-ablation-2026-07-11/source-review.json`.

Phase-4 transfer remains blocked. The next authorized work is provider-free
design of one exploration-only local chronological harvester that preserves
alternative-plus-attached-limit pairs without a new global semantic
synthesizer. No further model, graph, runtime, or final-output experiment is
authorized by this result.

## Exploration-local development result — 2026-07-11

The exploration-only local harvester now passes its development case. It
mechanically partitions a fourteen-message conversation into seven focal
user/assistant pairs, retains the preceding pair as role-limited context, and
returns at most two alternative-plus-attached-limit records per window. Prior
aliases may support only the alternative role; the attached limit must be
focal. No auxiliary ledger or global semantic synthesizer is used.

Provider-free evidence covers 35 development windows, five same-pair protected
fixtures, one cross-turn adversarial fixture, and a real 24-message stress case.
The target-blind Case-02 Turn-3 call recovered `e026` plus the previously lost
`e027` qualification. Across the complete case, record-level custody admitted
13 source-supported records and quarantined one exact prior-window duplicate.
All 32 admitted alias references are valid; no invalid record or source-
strength inflation was admitted.

The first six-window batch preserved one OpenRouter 429. After the official
rate-limit practice check and a separately frozen cool-off, one unchanged
operational completion succeeded. The terminal receipt therefore shows 6/7
first-attempt operational success, 7/7 eventual window completion, eight total
requests including the visible retry, and $0.00698625 estimated cost. There are
zero automatic retries, fallbacks, evaluator, embedding, graph, or runtime
calls.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-exploration-local-development-result-v1.md`;
- `docs/conversation-understanding/reasoning-process-exploration-local-current-practice-2026-07-11.md`;
- `research/reasoning-process-exploration-local-terminal-2026-07-11/terminal-result.json`;
- `research/reasoning-process-exploration-local-terminal-2026-07-11/source-review.json`.

All five semantic mechanisms now pass Case-02 development review. The next
authorized work is provider-free Phase-4 transfer design and case selection.
Transfer calls, graph, runtime, final-output evaluation, and scalar quality or
trust scores remain unauthorized.

## Reasoning-process Phase-4 transfer result — 2026-07-11

The prospectively frozen transfer ran on mechanically selected Case 05 and Case
01. It combined four whole-conversation readers with seven local exploration
windows per case. All 22 jobs eventually completed after one preserved
OpenRouter 429 and one separately frozen cooled operational completion. The run
produced 52 admitted source-linked records, zero quarantines, and non-empty
records for all five dimensions in both cases.

The protected minority-signal gate failed. Exact target visibility was 1/5 on
Case 05 and 4/5 on Case 01; source review classified the ten targets as six
supported, two partial, and two not observed. Both evidence readers omitted
part or all of their protected claim-boundary relationship. Stability repeats,
completed-case prompt tuning, graph, and runtime integration are therefore not
authorized.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-phase4-transfer-result-v1.md`;
- `research/reasoning-process-phase4-transfer-design-2026-07-11/contract.json`;
- `research/reasoning-process-phase4-transfer-review-2026-07-11/source-review.json`.
- `research/reasoning-process-phase4-transfer-review-2026-07-11/source-review-correction-v1.json`.

The next work is provider-free design of bounded chronological shards for the
four global readers. It must keep semantic interpretation probabilistic and
restrict deterministic machinery to chronology, source regions, evidence IDs,
budgets, and custody. It may not recreate a global synthesizer or an uncontrolled
event flood.

## Chronological shard provider-free design — 2026-07-11

The first redesign representation is built without model calls. It creates
three bounded shards for each of the four failed global-reader families while
keeping the existing seven local exploration windows. Across five reviewed
cases, all 20 protected full-reader targets are co-located in exactly one focal
shard, every source alias is focal exactly once per family, and the largest
packet is 6,013 bytes.

The prospective ceiling rises from 11 to 19 calls and from 30 to 38 maximum
records per fourteen-message case. This explicit cost is still below the former
88–95-event architecture, but representability is not model behavior. No probe
is authorized until family-specific prompts, schemas, role-limited context
rules, record-level custody, and a smallest-probe contract pass provider-free.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-chronological-shards-design-v1.md`;
- `docs/conversation-understanding/reasoning-process-chronological-shards-current-practice-2026-07-11.md`;
- `research/reasoning-process-chronological-shards-2026-07-11/report.json`;
- `research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json`.

The provider-free prompt/schema/custody interface then passed and the smallest
Case-05 evidence shard recovered its exact protected target. A frozen four-call
family batch recovered Case-01 evidence and the Case-05 direct correction, but
position and uncertainty remained partial. Position evidence roles were good
while its prose described only the starting state; uncertainty split one reopen
relationship across records; and another challenge record reversed semantic
roles. The full nineteen-call case is therefore blocked.

Next work is provider-free role-specific interpretation fields for position and
uncertainty and a challenge-role representation review. No new provider call,
graph, runtime, or completed-case prompt tuning is authorized.

## Role-explicit chronological shards v2 — 2026-07-12

The provider-free role redesign is complete. Position now separates starting,
current, qualification, and trajectory meaning. Uncertainty separates the
unresolved matter, preservation/reopen condition, and relationship. Challenge
separates prior frame, challenge, response, revision, and relationship.
Evidence schema and prompts remain unchanged.

All 60 prompts and 20 protected fixtures pass locally. Seven adversarial checks
show the intended boundary: missing role prose and text/evidence divergence are
rejected; challenge inversion and conceptual uncertainty splitting remain
inspectable semantic-review questions rather than brittle deterministic gates.

One frozen Case-05 position endpoint call fixed the original missing-current
prose failure. It produced all required role meanings and recovered the target
trajectory. Source review still failed the run because “I want the archive
organized first” became “insisted on the entire archive” and “total archival
completion.” This is one source-strength inflation.

No same-case repair or retry, uncertainty/challenge probe, full case, graph, or
runtime call is authorized. Next work is provider-free generic modal and
commitment-strength fidelity followed, if it passes, by a fresh prospective
case.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-role-explicit-v2-result-2026-07-12.md`;
- `research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12/report.json`;
- `research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12/adversarial-review.json`;
- `research/reasoning-process-role-explicit-v2-position-probe-2026-07-12/source-review.json`.

## Modal-strength chronological shards v3 — 2026-07-12

The generic modal-strength experiment is complete as a preserved negative
result. Position records now expose categorical starting/current force,
qualification modalities, and a strength-fidelity explanation. These are not
scores or an ordinal ladder. Code validates vocabulary, presence, exact source
custody, and terminal disposition but does not infer or compare semantic force.

All 60 prompts and 20 reviewed fixtures passed provider-free; non-position
interfaces stayed byte-identical to v2; adversarial tests preserved the
semantic boundary; and 167 reasoning-process tests passed before the call. A
source review also caught and corrected, only in the new v3 fixture, an inherited
Case-03 paraphrase that had changed “I think” into “demanding.” Frozen v2
artifacts were not modified.

The one frozen fresh Case-03 call was operationally successful and admitted two
records, but source review failed the semantic gate. Gemini labeled “I think the
final third needs a major re-edit” as `decision`, strengthened it to a “firm
belief” and “immediate, unilateral assessment,” and omitted the protected
revised-cut possibility/open-partnership relationship. This shows the fields
are useful for audit visibility but are not yet sufficient for semantic force
fidelity.

No repair, retry, additional provider call, graph, full-case, stability, or
runtime work is authorized. The next provider-free design question is the
stance object: separate belief from choice/action commitment, and separate a
decision to make a proposal from uncertainty about accepting its outcome.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-modal-strength-v3-result-2026-07-12.md`;
- `research/reasoning-process-modal-strength-v3-2026-07-12/report.json`;
- `research/reasoning-process-modal-strength-v3-2026-07-12/adversarial-review.json`;
- `research/reasoning-process-modal-strength-v3-probe-2026-07-12/source-review.json`.

## Stance-object chronological shards v4 — 2026-07-12

V4 replaces whole-role force labels with source-linked stance components for
belief/assessment, action/proposal, intended outcome/policy,
acceptance/willingness, and reported position landscapes. One explicit
temporal-role array keeps the schema smaller than the first three-array draft.
Code validates bounded shape and parent-role evidence custody but does not infer
semantic object/expression compatibility.

Provider-free gates passed: all 60 prompts built, all 20 reviewed fixtures
compiled, nine adversarial outcomes passed, non-position interfaces remained
byte-identical, and 184 reasoning-process tests passed before execution. The
suite also caught and reversed an attempted change to the runner frozen by v3,
preserving the historical contract's exact hash.

The one frozen Case-04 request failed operationally before inference. Google
returned HTTP 400 `INVALID_ARGUMENT`; there was no model candidate, compiled
record, usage, cost, or semantic result. Schema complexity is plausible but not
proven: v4 reaches depth 11 and adds a nested component evidence array, while
the previously served v3 schema was depth 9.

Case-04 is closed and no retry is authorized. Next work is provider-free v4.1:
one source alias per atomic component, no new nested evidence array, and no new
provider call until new ambiguous multi-turn cases exist and compatibility,
adversarial, and cold-reader gates pass.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-stance-object-v4-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v4-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v4-2026-07-12/adversarial-review.json`;
- `research/reasoning-process-stance-object-v4-probe-2026-07-12/operational-review.json`.

## Stance-object chronological shards v4.1 — 2026-07-12

V4.1 keeps stance objects but changes the provider wire to five index-aligned
string arrays. The compiler requires equal bounded lengths and one parent-role
alias per index, then reconstructs normal component objects. This reduces the
position schema to 3,654 bytes at depth 9. Semantic alignment across columns
remains a source-review question; an enum-valid permutation is deliberately
admitted structurally.

Three new seven-pair ambiguous conversations were frozen before model use.
Career transition was selected mechanically from career transition,
community-space commitment, and agency acquisition. All 20 legacy and three
fresh reviewed fixtures compiled, 12 adversarial outcomes passed, non-position
interfaces remained unchanged, and 200 reasoning-process tests passed before
execution.

The selected call still failed before inference with Google HTTP 400
`INVALID_ARGUMENT`. A current local `google-genai` 2.11.0 audit gives a probable
cause: native `Schema` rejects inherited `uniqueItems` on the three position
evidence arrays, and the full v4.1 schema validates after removing only those
keywords. The provider did not explicitly name the field, so the diagnosis is
high confidence but not provider-confirmed.

Career transition is closed and the other two cases cannot be called under the
v4.1 contract. Next work is v4.2: remove `uniqueItems` from the provider schema,
retain deterministic duplicate validation, freeze a current SDK preflight, and
use at most one reserved fresh case only after all gates pass.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-stance-object-v41-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v41-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v41-fresh-corpus-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v41-probe-2026-07-12/compatibility-diagnosis.json`.

## Stance-object chronological shards v4.2 — 2026-07-12

V4.2 changed only the provider wire: it removed the three inherited
`uniqueItems` keywords that current `google-genai` 2.11.0 rejects. Semantic
prompts, five-column stance reconstruction, exact source custody, validators,
and deterministic duplicate rejection remained unchanged. All 63 prompts and
23 reviewed fixtures passed, as did the adversarial, cold-reader, regression,
and current Google native-schema gates.

The one frozen community-space request still failed before inference with
Google HTTP 400 `INVALID_ARGUMENT`. No candidate, compiled record, usage, cost,
or semantic result exists. This proves that `uniqueItems` was not a sufficient
provider-side explanation. The exact remaining schema or translation
constraint is unknown; local SDK acceptance is not provider acceptance.

Community space is closed. Agency acquisition remains reserved and is not
authorized under v4.2. Next work must isolate provider schema compatibility
from semantic evaluation: build a provider-free one-dimension reduction matrix
first, and authorize only non-semantic compatibility probes before another
valuable multi-turn case. No retry, graph, runtime, stability, full-case, or
receipt work is authorized.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-stance-object-v42-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v42-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v42-2026-07-12/google-schema-preflight.json`;
- `research/reasoning-process-stance-object-v42-probe-2026-07-12/result.json`;
- `research/reasoning-process-stance-object-v42-probe-2026-07-12/compatibility-diagnosis.json`.

## July 2026 model/operator selection — 2026-07-12

The model/operator search is complete for the combined stance-object contract.
The unchanged v4.2 schema is accepted by GLM 5.2/DeepInfra, DeepSeek V4
Flash/Alibaba, DeepSeek V4 Pro/Alibaba, and MiniMax M3/Parasail. Google's
pre-inference rejection is therefore provider-path specific rather than a
universal schema limit.

No pair passes the full semantic gate. DeepSeek V4 Flash is closest and
cheapest, but even after the prompt-only v4.3 role-coverage correction it denies
the visible starting role while describing it in trajectory prose. GLM 5.2 and
MiniMax return empty; DeepSeek V4 Pro repeats the missing-component defect at
higher cost. The reserved agency case remains untouched.

Next work is provider-free decomposition into a role-trajectory LLM microtask
and separate per-role stance-object LLM microtasks, with deterministic joining
limited to exact role/evidence identifiers. No keyword gate, additional model
call, graph, runtime, or integration work is authorized.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-model-operator-current-practice-2026-07-12.md`;
- `docs/conversation-understanding/reasoning-process-model-operator-selection-result-2026-07-12.md`;
- `research/reasoning-process-model-operator-selection-2026-07-12/terminal-review.json`;
- `research/reasoning-process-model-operator-v43-development-2026-07-12/source-review.json`.

## Position role-first v2.1 and v2.2 — 2026-07-12

V2.1's new succession case recovered one coherent record for each role and
preserved protected e056 meaning, but qualification was quarantined because
the model returned unequal parallel component columns. V2.2 changed only that
wire: related component fields now live in one nested object. Ten reviewed
cases, 30 role records, 10 relationships, 10 joins, and 10 local/adversarial
tests passed provider-free.

The frozen fresh cooperative case then served all four DeepSeek V4
Flash/Alibaba calls for $0.000991064. All schemas, admissions, nested component
identities, and the exact-ID join passed; protected e056 irreversibility and
assistant ownership survived. Complete semantic review still failed: e052
leaked from qualification into current, starting expressions were flattened to
`reported_without_endorsement`, and the relation omitted some specific
option-changing pressure.

V2.2 is therefore the structural reference, not an integration candidate. No
retry, model control, graph, or runtime work is authorized. Next work is
provider-free role-boundary and expression-contract design, followed by a
genuinely new transfer case only after local gates pass.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-position-role-first-v22-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v22-2026-07-12/report.json`;
- `research/reasoning-process-position-role-first-v22-probe-2026-07-12/source-review.json`.

## Position role-first v2.3 — 2026-07-12

V2.3 tested a prompt/packet-only clarification of current versus qualification
and source-speaker-relative expression force. Eleven reviewed cases and the
local/adversarial gates passed provider-free. A new museum/AI-license case was
then frozen source-first and run once through the unchanged DeepSeek V4
Flash/Alibaba route.

All four calls, schemas, admissions, nested components, and the exact-ID join
passed for $0.001047746. Starting expression ownership improved: user desire,
counterpressure, and uncertainty were no longer flattened. The central defect
still repeated: unresolved e036 appeared in both current and qualification
despite an explicit instruction to exclude merely unresolved matters from
current. Protected e040 and assistant ownership survived.

Prompt-only role-boundary refinement is closed. No retry, model control, graph,
or runtime work is authorized. Next work must compare bounded provider-free
coordination designs; hard evidence-ID subtraction is not allowed because one
alias may legitimately contain both adopted and unresolved meanings.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-position-role-first-v23-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v23-probe-2026-07-12/source-review.json`.

## Paired role-first v2.4 and v2.4.1 — 2026-07-12

V2.4 pairs current and qualification in one semantic allocation call, keeps
starting independent, and uses one exact-ID relation call. It reduces the call
ceiling from four to three and allows one source alias in both roles only when
the model identifies distinct meanings. Code never subtracts aliases or judges
semantic role correctness.

Twelve reviewed cases and the adversarial gates passed provider-free. The
first registry probe allocated shared e036 correctly but contradicted its two
populated records with redundant `not_found` envelope statuses. Admission and
the relation call were correctly blocked. V2.4.1 removed only those redundant
status fields; replaying the exact preserved candidate then compiled without
changing its semantics.

On a new housing-retrofit case, all three v2.4.1 calls and the exact join passed
for $0.000959574. Shared e034 was correctly separated into an adopted current
condition and unresolved qualification. Protected irreversibility and speaker
ownership survived. Residual force, category, evidence-precision, allocation-
note, and prose-length defects block production or graph integration claims.

Next work is provider-free corpus-level paired-allocation evaluation with
separate, non-scalar judgments for allocation, protected meaning, ownership,
evidence precision, force, category precision, and relationship preservation.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-position-role-first-v24-v241-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v241-probe-2026-07-12/source-review.json`.

## Paired role corpus evaluation — 2026-07-12

Four prospectively reviewed provider cases were compared across seven separate
dimensions without a scalar score or automatic judge. Independent readers
failed central current/qualification allocation in both cases. Paired readers
passed it in both shared-meaning cases. Protected qualification and material
speaker ownership survived across all four, while evidence precision, modal
force, and object-category precision remained uneven across architectures.

The checked validator resolves every evidence path, rejects forbidden score
fields and unsafe authorization, and confirms zero provider, evaluator, graph,
or runtime calls. Another transfer call is not selected. The next experiment
is a provider-free read-only shadow comparing source-first and model-produced
graph inputs, followed only under a separate contract by selection-impact
comparison. Production and live routing remain unauthorized.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-paired-corpus-evaluation-result-2026-07-12.md`;
- `research/reasoning-process-paired-corpus-evaluation-2026-07-12/corpus-review.json`.

## Reasoning-process graph-impact shadow — 2026-07-12

The read-only shadow sealed Codex-assisted source/provider interpretations into
controlled fact-free reasoning-pattern packets. Source-first and provider
projections were identical for both paired cases, producing the same eight
seed models and identical one-hop neighborhoods. A missing-reversal ablation
removed `commitment-bias`, `premortem`, and `sunk-cost-fallacy` seeds, proving
sensitivity to the protected mechanism.

A shadow-only typed adapter then carried controlled mechanism text into the
activation matcher with empty evidence quotes. One frozen OpenAI batch request
embedded two unique projections with `text-embedding-3-large` at 3,072
dimensions. No tiebreaker fired; full selection remained deterministic. No
role prose or facts were embedded.

The result is conditional: extraction noise does not change graph pressure
after faithful abstraction on these cases. Automatic role-record-to-pattern
abstraction is not proven and is the next experiment. Production, runtime,
reconsideration, and receipt behavior remain unauthorized.

Continuation entrypoints:

- `docs/conversation-understanding/reasoning-process-graph-impact-shadow-result-2026-07-12.md`;
- `research/reasoning-process-graph-impact-shadow-2026-07-12/impact-review.json`.

## V1 closure and current constitutional handoff — 2026-07-13

The V1 simulated-reliability program is closed as an evidence program; product
reliability is not established. The final reassessment preserves seven
separate evaluation dimensions, closes premium testing, and requires a live
constitutional audit before integrating research corrections.

That audit is now complete. It found strong custody and failure honesty, but
also a direct Constitution-v5 violation in the live Model Companion path: a
probabilistic verifier removes most deterministic recalled candidates before
graph expansion and reconsideration. It also found silent manual
long-conversation pre-truncation risk, clean-run reliance inflation, and
missing hard cost/privacy controls. No provider calls were made.

Continuation entrypoints:

- `docs/evals/simulated-reliability-v1-final-constitutional-reassessment-2026-07-13.md`;
- `docs/evals/simulated-reliability-v1-final-completion-matrix-v1.json`;
- `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`;
- `docs/evals/lolla-current-state-constitutional-drift-register-v1.json`;
- `plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md`.
