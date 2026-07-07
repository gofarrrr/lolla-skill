# Observatory Run Data Visibility Matrix v0

Status: reviewable product information matrix.

Date: 2026-07-07

Decision gate: `await_user_review_of_run_data_visibility_matrix`

Related source audit:
[Observatory Data Exposure Audit](observatory-data-exposure-audit-v0.md)

## Purpose

This is the table to review before changing more Observatory UI.

The earlier data exposure audit named what we gather and assigned visibility
layers. This matrix adds the missing product thinking:

- how the data comes into the system;
- what it helps us understand;
- why a user might care;
- where the user discovers that this data exists;
- how it should go out to the user;
- what the user can do with it;
- what needs a summary, expansion, technical route, explicit export, or
  redacted receipt.

The product problem is not that we lack data. The product problem is that raw
run artifacts, teaching content, model-library content, graph data, receipts,
agent memory, and technical telemetry can all look equally important if we show
them at the same time.

The goal is:

```text
selected run
  -> what changed
  -> what reasoning move can I learn
  -> what models and relations explain it
  -> where can I navigate
  -> what exists, what is missing, and what is not claimed
  -> optional technical inspection or agent export
```

## Show Everything, But In Layers

The working principle is:

```text
If we gather it, the user should be able to account for it.
```

That does not mean every artifact becomes first-read product copy. It means
every gathered artifact needs one of these forms:

- visible summary;
- expandable detail;
- technical inspection route;
- explicit file export;
- receipt that says the artifact exists but its body is private, unsafe, or
  misleading to render raw.

So the question is not:

```text
Should we show this or hide it?
```

The question is:

```text
At what depth, in what form, with what warning, and for what user action?
```

The only hard exception is sensitive material that should be redacted rather
than displayed raw, such as local absolute paths, credentials, private operator
logs, or provider/private bodies. Even then, Observatory should usually show a
receipt that the thing exists and explain where it can or cannot be inspected.

## Review Vocabulary

| Layer | Meaning | First product rule |
| --- | --- | --- |
| `show_by_default` | General first-read information | Keep it short, readable, and useful without technical knowledge. |
| `primary_surface` | Main surfaces in Observatory | Outcome, Learn, Models, Relations, Map, Receipts. |
| `expandable_detail` | Useful detail after a click or disclosure | Model details, relation details, source/custody detail, local neighborhoods. |
| `technical_inspection` | Evidence, telemetry, and debug material | Reachable from Receipts or Advanced Audit, not first-read product copy. |
| `agent_export` | Markdown/file output for a future agent | Explicit user action, private by default, never automatic. |
| `future_design` | Useful but not ready as current UI | Needs a later design or data gate. |
| `operator_inspection` | Machinery, ranking, vectors, eval internals, code | Show through technical/operator inspection or receipts, not as product copy. |
| `explicit_private_export` | Sensitive raw/private material | Show only by explicit private export or receipt; redact unsafe bodies by default. |

## Red-Team Decisions

This matrix incorporates an external red-team review, but it does not accept
every recommendation mechanically.

Accepted revisions:

1. Every gathered artifact family needs a discoverable place, even when the
   body stays out of first-read UI.
2. The next UI slice should be a run inventory receipt, not a bigger graph.
3. Conversation extraction should not be buried only in technical audit; a
   short interpretation status belongs near Outcome/Receipts.
4. Model pages should lead with readable meaning and expandable sections, not a
   raw canonical Markdown dump.
5. Local model neighborhoods should come before a full corpus graph.
6. Treatment audits, Gate 4 probes, schemas, non-V60 affordance files,
   agent-result style outputs, memo artifacts, run events, and graph survival
   artifacts must be accounted for.

Rejected or deferred revisions:

1. Do not collapse `show_by_default` into `primary_surface` yet. First-glance
   copy and main-tab copy are different product jobs.
2. Do not collapse `operator_inspection` into `technical_inspection` yet.
   User-reachable audit details and maintainer-only raw machinery need
   different gates.
3. Do not rename `Download MD` in this slice. The label is intentionally short;
   its hover/help text should explain that it means a private run memory file
   for another agent.
4. Do not make raw embeddings, private ledgers, or provider-private bodies
   directly visible just because they exist. The product obligation is to show
   a receipt/status/count and a safe route, not to dump unsafe bodies.

## What The User Should Understand First

| Moment | User question | Data used | What we should show | What the user can do |
| --- | --- | --- | --- | --- |
| Run selection | Which run am I looking at? | case id, run id, run health, archive/current state | Compact selected-run header | Switch run or continue. |
| Outcome | What changed after Lolla looked at this? | revised answer, change memo, top pressure | Human-readable outcome summary | Decide whether to read, practice, or inspect. |
| Learn | What reasoning move can I learn? | Teacher learning packet | Case anchor, thinking move, relation story, practice rep | Practice the move. |
| Models | What do these models mean? | selected-run model objects and canonical source translation | Model cards and model detail pages | Open a model and learn when to use it. |
| Relations | Why do these models belong together? | relation semantics and selected relation pages | Plain-language relation story first | Open both models or practice the relation. |
| Map | Where can I navigate next? | selected-run graph neighborhood | Small clickable graph | Search, filter, select a node/edge, open detail. |
| Receipts | What exists and what is not claimed? | source refs, missingness, sidecar status, non-claims | Trust summary, status chips, optional inspection | Check custody or limits. |
| Agent export | How can a future agent understand this run? | conversation memory bundle | `Download MD` explicit action | Download the run memory file. |
| Advanced Audit | What exactly happened under the hood? | extraction, usage, trace/eval artifacts | Optional technical audit routes | Inspect only when needed. |

## Discovery Map

This is the product answer to "we gather it, so where does the user find it?"

| Discovery place | What appears there first | What can expand from there |
| --- | --- | --- |
| Run header / picker | Selected run, case id, availability, current/archive status | Run switcher and missing-artifact status. |
| Outcome | What changed, strongest pressure, decision situation summary | Interpretation status, extraction detail link, memo/result detail when present. |
| Learn | Case anchor, thinking move, model stack, relation story, practice rep | Worked example, do-not-overlearn boundary, model/relation links. |
| Models | Selected-run model cards and model detail pages | Canonical meaning, use/avoid guidance, failure modes, premortem prompts, source custody, local model neighborhood. |
| Relations | Selected-run relation cards and relation detail pages | Plain-language edge story, misread risk, practice prompt, source/ref detail. |
| Map | Small selected-run graph neighborhood | Node/edge panel, filters, model/relation links. |
| Receipts | What exists, what is missing, what is private, what is not claimed | Run inventory receipt, source custody, sidecar status, raw-transcript/export status, advanced inspection links. |
| Download MD | Explicit private run memory export | Agent-readable Markdown, raw transcript only when explicitly included. |
| Advanced Audit | Technical evidence and operational details | Extraction body, reasoning trace, usage, run events, eval sidecars, treatment audits, graph survival artifacts. |
| Operator inspection | Maintainer-only or unsafe raw machinery | Private/operator bodies, embeddings/vectors, provider-private bodies, raw affordance batches. |

## Run Data Visibility Matrix

| Data we gather | How it comes in | What it helps us see | User value | How it should go out | What the user can do | Disclosure guardrail |
| --- | --- | --- | --- | --- | --- | --- |
| Selected run context | `result.json`, current run state, archive picker | Which case/run the page is about | Know where they are before reading detail | `show_by_default` in the header and run picker | Switch run or keep reading | Raw local paths and raw JSON. |
| Run health and availability | `result.json`, adapter status, sidecar presence | Whether the workspace is complete, partial, blocked, or missing | Avoid clicking into absent detail | `show_by_default` as plain status chips | Know whether detail exists before clicking | Schema names as first-read copy. |
| Outcome summary | `result.json` revised answer and memo fields | What changed in the answer or advice | See the main change quickly | `primary_surface` in Outcome | Read the main change before learning or auditing | A wall of audit text. |
| Agent result object | `agent_result.json`, `result.json`, final result payloads | What the run actually returned | Compare the visible outcome to the stored result | `expandable_detail` from Outcome and Receipts | Open result detail when the summary feels incomplete | Raw object dumps as product copy. |
| Memo artifact | `memo.md`, `user_receipt.md`, generated run memo when present | The portable human note for the run | Read a clean memo without opening technical artifacts | `expandable_detail` from Outcome/Receipts | Open the memo or receipt when available | Duplicating the whole UI in memo form. |
| Strongest pressure or top finding | `result.json`, delta/top finding fields | What challenged the original framing | Understand why a lesson is relevant | `primary_surface` Outcome support line | Decide whether to continue to Learn | Treat as proof of correctness. |
| Conversation extraction status | `extraction.json` | What the system thought the conversation was about | Check whether the run was interpreted in the right direction | `expandable_detail` from Outcome/Receipts | Inspect if the outcome feels misframed | Raw extraction schema in Learn. |
| Decision situation summary | `extraction.json`, `result.json` | The central question or situation | Confirm "this is the case" | `show_by_default` summary in Outcome/Learn | Accept the frame or inspect interpretation | Multiple conflicting phrasings without hierarchy. |
| Raw extraction detail | `extraction.json` | Full extracted structure and labels | Audit interpretation when something looks wrong | `technical_inspection` from Advanced Audit | Inspect extraction body and labels | Treat extraction labels as user-facing truth. |
| Reasoning trace | `reasoning_trace.json` | Which lenses/models were considered, selected, or suppressed | Understand why something appeared | `technical_inspection`; selected pieces may feed Model/Receipts copy | Inspect the selection path when needed | Raw routing/ranking as product explanation. |
| Selected lenses | reasoning trace, model selection outputs | Which mental models or lenses were used | Jump from run to model study | `primary_surface` summary chips and model links | Open model pages | Present selection as certification. |
| Suppressed or unadjudicated signals | reasoning trace, conversation memory packet | What the system noticed but did not resolve | Notice uncertainty before over-trusting the output | `expandable_detail` in Receipts, with full context in agent export | Revisit unresolved questions | Make suppressed internals a default lesson. |
| Evaluation artifact | `evaluation.json`, eval sidecars | Whether internal checks ran and what they reported | See whether internal discipline exists | `technical_inspection` and Receipts status | Inspect quality-discipline artifacts | Product proof or human validation language. |
| Run events | `run_events.json`, event sidecars, archive event records | What happened when the run executed | Reconstruct sequence and timing when debugging | `technical_inspection` in Advanced Audit | Check lifecycle and event order | Turn event logs into first-read product copy. |
| Usage telemetry | usage summary, run events, provider call records | Cost, calls, and operational facts | Understand operational cost and calls | `technical_inspection` in Usage page / Advanced Audit | Check cost and call breakdown | Use telemetry as quality signal. |
| Teacher learning packet | Teacher adapter/learning packet | The teachable reasoning move from the run | Learn one reasoning move from the case | `primary_surface` in Learn | Practice a reasoning rep | Duplicate all raw Outcome/Receipts content. |
| Case anchor | Teacher learning packet | The concrete situation that makes the lesson understandable | Keep the lesson tied to the run | `primary_surface` Learn first-read | Understand what case this teaches from | Make it generic and detached from the run. |
| Thinking move | Teacher learning packet | The reasoning action the user can practice | Try a reusable move on the user's own thinking | `primary_surface` Learn first-read | Practice the move on another case | Do not bury it under model taxonomy. |
| Worked example | Teacher learning packet | How the move works in this run | See the move in action before practicing | `primary_surface` Learn detail or first-read when present | Compare example to their own thinking | Show "not supplied" as prominent narrative. |
| Practice rep | Teacher learning packet | What the user can actually do next | Leave with a concrete exercise | `primary_surface` Learn first-read | Perform the practice prompt | Treat practice as advice correctness. |
| Do-not-overlearn boundary | Teacher learning packet | What not to generalize from the lesson | Avoid misusing the lesson | `primary_surface` Learn and Receipts | Avoid overapplying the move | Bury the boundary in technical notes. |
| Selected-run model pages | Teacher packet model objects | Which mental models explain this run | Open the models behind the lesson | `primary_surface` Models and model detail routes | Open, read, practice | Imply this subset is the full canonical library. |
| Canonical model Markdown | `data/model_sources/*.md` | Durable source meaning of a model | Learn the model beyond this run | `expandable_detail`, translated into clean sections | Read model meaning, examples, and limits | Raw Markdown dumps or private file paths. |
| Model source manifest and hashes | `data/model_sources/manifest.json` | Source custody and source stability | Verify source custody when needed | `expandable_detail` source/custody detail | Check where model content came from | Hashes as quality proof. |
| Activation curation | `data/curation/*.json` | When/why a model is useful or risky | Decide when the model applies | `expandable_detail` on model pages | Read use/avoid guidance | Routing internals as model definition. |
| Intervention semantics | `data/curation/intervention_semantics/*.json` | Failure modes, premortems, heuristics, practice prompts | Practice the model and avoid common misuse | `expandable_detail` in Model detail and Learn practice support | Practice or avoid common misuse | Extraction metadata dominating the page. |
| Relation semantics | `data/curation/relation_semantics/*.json` | Why two models interact and how to read the edge | Understand the relation before seeing taxonomy | `primary_surface` Relations plus expandable detail | Read relation story and open both models | Unsupported relation speculation. |
| Selected-run relation pages | Teacher packet relation objects | The model-pair lesson for this run | Practice the relation, not just the individual models | `primary_surface` Relations | Practice the relation, open both models | Confidence as certification. |
| Selected-run graph neighborhood | Teacher packet graph | The small map around the lesson | Navigate the lesson's models and relations | `primary_surface` Map | Search, filter, click node/edge | Treat map edge as proof. |
| Relationship graph substrate | `data/relationship_graph.json` | Reviewed relation substrate beyond one run | Know richer model links exist | `expandable_detail` through model local neighborhoods | Browse direct reviewed neighbors of one model | Raw affinity, rank, or truth claims. |
| Model-detail local neighborhood | relationship graph plus relation semantics | The direct reviewed neighbors of one mental model | Fix the "only one connection" problem | `expandable_detail` on model pages | Jump from one model to related models/relations | Full corpus graph as first surface. |
| Knowledge graph | `data/knowledge_graph.json` | Broader model/relation topology | Prepare for future library browsing | `future_design` filtered library graph | Search and browse when designed | Dump the full topology by default. |
| Curated chunks | `data/curated/*.json` | Extra structured/source-backed material | Enrich pages with reviewed examples/details | `expandable_detail` after review | Read clearer examples/details | Chunk ids as product UI. |
| Family semantics | `data/family_semantics/*.json` | Model families and browsing categories | Browse models by useful clusters later | `future_design` library filters | Browse by family when designed | Family as quality/certification label. |
| V60 affordances | `data/compiled/model_affordances/affordances_v60.json` | Advanced model teaching affordances | Support deeper teaching pages later | `future_design` after translation gate | Learn deeper affordances later | Raw transaction JSON. |
| Non-V60 model affordance files | `data/model_affordances/**/*.json` | Source batch affordance material before compilation | Account for raw affordance substrate | `operator_inspection` receipt/status only | Inspect existence and compilation lineage | Raw batch JSON as product UI. |
| Semantic neighbors | `data/embeddings.db` | Similarity-based candidates | Suggest possible discovery after review | `future_design` suggestion queue | Maybe find related models after review | Treat similarity as validated relation semantics. |
| Data schemas | `data/schemas/*.json`, schema fixtures | Artifact contracts and validation shape | Understand what artifacts are supposed to contain | `operator_inspection` contract reference | Debug or validate artifact shape | Schema fields as user-facing product language. |
| Treatment audits | `data/treatment_audits/*.json`, calibration reports | Model/treatment discipline and calibration history | Check internal calibration when auditing | `technical_inspection` in Advanced Audit | Inspect calibration and audit evidence | Treat audits as product proof. |
| Gate 4 edge probes | `data/evaluations/gate4_edge_probes/*.json` | Edge-case evaluation discipline | Understand graph/eval risk when maintaining | `technical_inspection` in Advanced Audit | Inspect probe summaries | Treat probes as human validation. |
| Graph survival artifacts | graph survival reports and generated survival summaries | Which graph relations survived checks | Maintain graph evidence discipline | `technical_inspection` in Advanced Audit | Inspect survival summaries | Market graph survival as proof that edges are true. |
| Process brief / Decision Work sidecars | Decision Work sidecars, if present | A separate process/accountability read | Understand process only when requested | `technical_inspection` with Receipts status | Open only if requested/available | Merge it into Teacher lesson copy. |
| Conversation memory Markdown | Conversation memory packet/export | A self-contained agent-readable run memory | Let another agent understand the run later | `agent_export` via `Download MD` | Download and give to another agent | Default-on generation or public-safe raw transcript. |
| Raw 1:1 conversation transcript | `conversation.txt` or captured transcript | Original source conversation | Preserve full context for future sessions | `explicit_private_export`; receipt/status in Observatory | Include in private MD export or inspect only after explicit user action | Keep out of first-read UI; expose through receipt/export/explicit inspection. |
| Private/operator artifacts | private ledgers, operator logs, private tables | Debug/custody material | Know private material exists without exposing it | `explicit_private_export` receipt-only inventory | Debug locally if authorized | Do not render private bodies in normal Observatory. |
| Provider raw text/reasoning traces | retained provider artifacts, if any | Debugging provider behavior | Diagnose provider boundary issues | `operator_inspection` custody if retained | Inspect only in operator context | Do not turn provider raw text into user-facing product copy. |
| Raw embeddings/vectors | `data/embeddings.db` | Retrieval machinery | Account for retrieval substrate without showing vectors | `operator_inspection` receipt or diagnostics | Power suggestions internally; inspect existence and counts | Present existence/counts, not distance scores as relation meaning. |
| Product Delta/eval internals | eval and Product Delta artifacts | Builder diagnostics | Maintain evidence discipline without confusing users | `operator_inspection` in Advanced Audit | Maintain the system and inspect discipline | Do not turn internals into marketing, proof, or approval labels. |

## What This Means For Observatory

The first screen should not try to be the archive, the teacher, the model
library, the graph, the receipt, and the audit dashboard at the same time.

The first screen should say:

1. This is the selected run.
2. This is what changed.
3. This is the lesson you can practice.
4. These are the models and relation behind it.
5. This is the map for navigation.
6. These are the receipts and limits.
7. Download MD if you want a future agent to understand the full run.

Everything else needs a deliberate place:

| If the user wants... | Send them to... | Reason |
| --- | --- | --- |
| A quick understanding of the run | Outcome | Start general. |
| A reasoning practice rep | Learn | Teacher owns learning. |
| A durable mental model explanation | Models | Model pages own model study. |
| A model-pair explanation | Relations | Relation pages own edge meaning. |
| Navigation between models and relations | Map | Graph is a map, not proof. |
| Custody, missingness, non-claims | Receipts | Trust info belongs together. |
| Full artifact-level inspection | Advanced Audit | Technical detail stays optional. |
| A portable file for another agent | Download MD | Agent memory is an explicit export. |

## Open Review Questions

These are the questions to double-check before the next UI slice:

1. Should Outcome remain the default first tab, or should the first screen be a
   combined "Run summary plus next action" card?
2. Which five or six fields are allowed in the first read before we require a
   click or disclosure?
3. Should model pages lead with selected-run context or durable canonical model meaning?
4. How much canonical Markdown should be translated into the model page before
   the page feels too dense?
5. Should the next graph slice be a model-detail local neighborhood instead of
   a global graph? The current recommendation is yes.
6. Should raw transcript remain only in `Download MD`, with no Observatory page for it by default? The current recommendation is yes.
7. What data should be marked "agent-useful but human-overwhelming" and kept
   out of the visible UI?

## Boundary

This matrix:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate or attach sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.

## Recommended Next Gate

`await_user_review_of_run_data_visibility_matrix`

Reason: the next UI slice should not begin until the table is reviewed. Once
the visibility matrix is accepted, the next implementation should revise the
Observatory first-read and detail boundaries against this matrix.
