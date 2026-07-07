# Observatory Data Exposure Audit v0

Status: product information-architecture audit.

Date: 2026-07-07

Decision gate: `proceed_to_graph_substrate_and_memory_export_design`

Machine-readable audit:
[Observatory data exposure audit JSON](observatory-data-exposure-audit-v0.json)

## Purpose

The current Observatory work has enough product surface to expose a deeper
problem: we are gathering far more information than the user should see at
once.

This audit decides how gathered data should be presented:

- what starts the experience;
- what is a primary product surface;
- what opens as detail;
- what stays technical;
- what belongs in an explicit agent memory export;
- what stays internal or private;
- what remains future graph/library work.

The correction from the previous slice is now part of the rule: internal review
mechanics are not product features.

## One Product Flow

The selected-run workspace should remain:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The user starts with general information and then chooses depth:

1. Outcome: what changed in this run?
2. Learn: what reasoning move can I practice?
3. Models: what do these mental models mean?
4. Relations: how do the models interact?
5. Map: where can I navigate next?
6. Receipts: what exists, what is missing, and what is not claimed?

Advanced Audit remains available, but it is not the learning path.

## Visibility Layers

| Layer | Meaning | Product examples |
| --- | --- | --- |
| `default_workspace_summary` | Visible immediately in the first read | selected run, outcome summary, availability statuses |
| `primary_product_surface` | Main product surface the user opens intentionally | Learn, Models, Relations, Map, Receipts |
| `expandable_product_detail` | Detail after a click, selection, or disclosure | canonical model sections, source refs, use/avoid, failure modes, local model neighborhood |
| `optional_technical_inspection` | Custody and telemetry for maintainers or careful users | extraction audit, usage, graph survival, process brief |
| `agent_memory_export` | Explicit compiled artifact for a future agent | conversation memory bundle |
| `future_or_suggestion_only` | Useful later, not current default product | full corpus graph, family filters, semantic neighbors, V60 affordances |
| `internal_only` | Implementation or eval material | raw rankings, embeddings, provider traces, Product Delta internals, code |
| `private_hidden` | Sensitive raw material | raw conversation, private ledgers, operator logs |

Current desired layer counts:

| Layer | Count |
| --- | ---: |
| `default_workspace_summary` | 3 |
| `primary_product_surface` | 5 |
| `expandable_product_detail` | 8 |
| `optional_technical_inspection` | 5 |
| `agent_memory_export` | 1 |
| `future_or_suggestion_only` | 6 |
| `internal_only` | 6 |
| `private_hidden` | 2 |

The important signal: 17 of the 36 audited data items are shown or partly
shown today, while 19 remain hidden, future, internal, private, or only
available as separate worktree capability. The visible product still underuses
the canonical library and relationship substrate.

## What We Show First

The first read should show:

- selected run context;
- outcome summary;
- whether Learn, Conversation Understanding, and Process Brief material exists.

This gives the user orientation without forcing them to decode telemetry.

## What We Show As Product Surfaces

The main product surfaces are:

- Teacher lesson in Learn;
- selected-run model pages;
- selected-run relation pages;
- selected-run graph neighborhood;
- Receipts.

These surfaces should be readable and navigable. They should not look like JSON,
system traces, review forms, or curation dumps.

## What We Show As Detail

The product still needs stronger detail pages.

Mental model pages should eventually expose product-safe translations of:

- canonical Markdown;
- use/avoid conditions from activation curation;
- failure modes, premortem questions, heuristics, and practice prompts from
  intervention semantics;
- source refs and hashes when opened as custody detail.

Relation pages should eventually expose product-safe translations of:

- relation semantics;
- source refs or quotes;
- misread risks;
- practice prompts;
- links to both model pages.

This is also where the user's graph concern lands: when a mental model is
opened, the page should not imply that the model only has one relation. It
should be able to show a local reviewed neighborhood from the richer graph
substrate.

## What Stays Technical

These can stay available, but not as default product copy:

- extraction audit;
- usage telemetry;
- graph survival and eval artifacts;
- process brief detail;
- advanced audit index.

Receipts can link to technical inspection. Outcome, Learn, Models, Relations,
and Map should not become telemetry dashboards.

## What Becomes Agent Memory

The separate Conversation Memory Bundle worktree is best understood as an
agent-readable export lane.

It is not a default user page.

It can become useful if merged as:

- offline only first;
- explicit generation only;
- no runtime default;
- no provider calls;
- no archive mutation;
- public-safe mode without raw conversation;
- private local mode only when raw conversation is explicitly requested.

The product value is different from Observatory:

- Observatory helps the user understand and navigate a run.
- Conversation Memory helps a future agent understand what happened in a run
  without reopening every artifact.

## What Stays Internal Or Private

Do not put these into the user product path:

- raw embeddings;
- raw routing rankings;
- provider raw text or reasoning traces;
- Product Delta and eval internals as proof;
- local absolute paths;
- raw conversation by default;
- private tables, ledgers, or operator logs.

These may support builders, tests, technical inspection, or explicit private
exports. They are not product copy.

## Graph Gap

The graph substrate is not small.

Current deterministic counts:

| Substrate | Count |
| --- | ---: |
| canonical model Markdown files | 222 |
| relationship graph edges | 1,358 |
| knowledge graph models | 222 |
| knowledge graph edges | 1,742 |
| relation semantics files | 225 |

The current visible Map is a selected-run learning neighborhood. It is not a claim that the selected mental model has only one relation.

Required graph modes:

| Mode | Purpose | Status |
| --- | --- | --- |
| selected-run learning neighborhood | Navigate the current lesson | present |
| model-detail local neighborhood | Show direct reviewed neighbors for one mental model | missing |
| filtered library graph | Browse canonical library by filter/search | future |
| full corpus graph | Explore the whole topology | future, not first surface |

The next graph product slice should add model-detail local neighborhoods before attempting a global full-corpus graph.

## Decisions

1. Keep the default user experience general first.
2. Keep Teacher inside Observatory, not as a second product.
3. Treat model pages and relation pages as the durable knowledge surfaces.
4. Treat the Map as navigation, not proof.
5. Treat the current selected-run graph as intentionally small, not as the full
   model graph.
6. Add local model neighborhoods before a global full-corpus graph.
7. Merge Conversation Memory, if at all, as explicit offline export before UI.
8. Keep raw conversation and private/operator artifacts hidden by default.

## Boundary

This audit:

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

## Next Gate

Recommended next gate:

`proceed_to_graph_substrate_and_memory_export_design`

Reason: the current product path is cleaner, but the next real decision is how
to expose model-detail graph neighborhoods and how to merge the offline
Conversation Memory Bundle without making it default product UI.
