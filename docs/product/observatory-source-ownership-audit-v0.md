# Observatory Source Ownership Audit v0

Status: source ownership decision contract
Date: 2026-07-06
Decision gate: `proceed_to_observatory_product_view_model_contracts`

## One Sentence

Observatory is one product shell with hybrid source ownership: the portable
runtime server in this repo owns local serving, read-only APIs, audit panels,
and current Learn/Receipts additions, while the historical root SPA source lives
in the separate `Lolla-system-b/observatory/svelte-app` Svelte repo and should
only receive the global shell after product-safe view models and a controlled
source-port package exist.

## Why This Exists

The global Observatory design says the product should become one selected-run
workspace:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Before building that globally, we had to answer a source question:

```text
Where does the Observatory UI actually belong?
```

If we keep adding product UI only through the portable server and serve-time
injection, the UI will stay fragmented. If we jump directly into the compiled
bundle, we risk editing the wrong artifact. If we port Teacher/Receipts into the
external Svelte app before view models are stable, we duplicate product logic
and recreate the same information-flow confusion in a different stack.

This audit verifies the current ownership shape and chooses the next safe
implementation sequence.

Related design trail:

- [Observatory Global Product Experience And Data Flow](observatory-global-product-experience-and-data-flow-v0.md)
- [Mental Model Teacher Observatory Ownership and Portability Boundary](mental-model-teacher-observatory-ownership-portability-boundary-v0.md)
- [Mental Model Teacher Observatory Integration Design](mental-model-teacher-observatory-integration-design-v0.md)
- [Observatory Conversation Understanding Boundary](observatory-conversation-understanding-boundary-v0.md)

## Short Verdict

The source owner is split by responsibility:

| Responsibility | Owner today | Decision |
| --- | --- | --- |
| Local serving, routing, archive/run loading, read-only APIs | `observatory/serve_result.py` in this repo | Keep here. This is the portable runtime boundary. |
| Server-rendered audit, usage, Learn, Receipts, and process-brief status | `observatory/serve_result.py` in this repo | Keep here until product-safe view models exist. |
| Historical root SPA source for `/` | `Lolla-system-b/observatory/svelte-app` | Treat as the native SPA source owner, but do not port yet. |
| Checked-in runtime bundle | `observatory/build/*` in this repo | Treat as copied compiled output, not source. Do not hand-edit. |
| Product IA and contracts | `docs/product/*`, future view-model modules in this repo | Keep here because the portable runtime must own product-safe translation. |
| Future global selected-run shell | External Svelte source consuming product-safe APIs | Port after contracts and sync path are explicit. |

The next PR should not be another UI patch. It should define the product view
model contracts that both the portable server and future Svelte shell can share.

## Evidence From This Repo

### Runtime Server

The local runtime repo contains:

- `observatory/serve_result.py`;
- `observatory/render_schema.json`;
- `observatory/build/index.html`;
- `observatory/build/assets/*.js`;
- `observatory/build/assets/*.css`.

`observatory/serve_result.py` is the active local server. It owns:

- `/api/cases`;
- `/api/case/<id>`;
- `/api/case/<id>/graph`;
- `/api/case/<id>/usage`;
- `/api/case/<id>/teacher-learning`;
- `/api/case/<id>/decision-work`;
- `/api/case/<id>/decision-work/prepare`;
- `/api/model/<model_id>`;
- `/api/families`;
- `/teacher-learning`;
- `/audit/*`;
- `/usage`;
- the current serve-time Learn/Receipts/status injection into `/`.

This confirms the portable server is not a thin static-file server anymore. It
is the local product adapter and custody surface.

### No Local SPA Source

This repo still does not contain a local frontend source app:

- no root `package.json`;
- no `observatory/package.json`;
- no `observatory/svelte-app/`;
- no local `vite.config.*`;
- no local `svelte.config.*`;
- no local `tsconfig.json` for an Observatory app.

That means this repo cannot be treated as the native Svelte source tree.

### Source Note In Server

`observatory/serve_result.py` states that the bundle in `observatory/build/`
is compiled output from:

```text
Lolla-system-b/observatory/svelte-app
```

The same header says `/audit/*` and `/usage` are rendered from the Python file
and stay portable when `observatory/build/` is empty.

### Portability Doctrine

`docs/how-it-works/live-flow.md` says the launch path is:

```text
finalize_and_archive.sh -> scripts/skill/launch_observatory.py -> observatory/serve_result.py
```

It also states that every audit panel is server-rendered HTML and works whether
or not the Svelte SPA bundle exists. That is the portability boundary: the skill
runtime must keep a useful local Observatory without a Node toolchain.

## Evidence From The External Svelte Source

A local sibling checkout was inspected read-only:

```text
Lolla-system-b/observatory/svelte-app
```

Observed facts:

- Git remote: `gofarrrr/lolla-system-b`;
- branch inspected: `feat/skill-backport-quality-improvements`;
- head inspected: `85dc10b`;
- app package name: `observatory`;
- stack: Svelte 5, Vite 6, TypeScript, Vitest;
- source files include `src/App.svelte`, `ReasoningGraph.svelte`,
  `ModelDetailPanel.svelte`, `FamiliesView.svelte`, `KpiHeader.svelte`,
  `RunHealthView.svelte`, and related component tests;
- the Svelte app fetches `/api/cases`, `/api/case/<id>`,
  `/api/case/<id>/graph`, `/api/model/<model_id>`, and `/api/families`;
- the root app still presents a case/family picker and selected-case
  dashboard, not the new global product tabs;
- the source does not contain the newer Teacher Learn, Decision Work,
  Conversation Understanding, process brief, Models/Relations/Map/Receipts
  product shell work.

This verifies that the historical root SPA source exists and is real, but it is
not current with the latest product-surface additions in this runtime repo.

## Bundle Provenance Finding

The runtime bundle and the external app build have matching `index.html` content
and matching asset filenames:

```text
index-DDa-RNf7.js
index-DHa6Vrq4.css
index-H3UEopEj.js
```

Two checked asset hashes matched during inspection; one main JS asset with the
same filename differed between the runtime repo and the external local build.

This does not prove manual editing. It does prove that the current local
external build snapshot and the checked-in runtime bundle are not fully
byte-identical. Therefore, a future source port needs a controlled sync path:

```text
external Svelte source
  -> clean build
  -> recorded artifact manifest / hashes
  -> copied observatory/build/*
  -> runtime smoke tests
```

Do not treat `observatory/build/*` as editable source. Do not assume the local
external checkout is already a clean rebuild of the runtime bundle.

## Product Ownership Decision

### Portable Runtime Repo Owns Product-Safe Translation

This repo should own:

- selected-run archive loading;
- source custody and missingness;
- read-only sidecar discovery;
- product-safe model/relation/learning/receipt view models;
- API endpoints consumed by any UI;
- server-rendered fallback pages for audit, usage, Learn, and Receipts;
- runtime-safe non-claims.

Reason: this repo ships with the skill runtime. It must remain useful without a
frontend toolchain, and it is closest to the archive artifacts and product
boundaries.

### External Svelte Source Owns The Native Root Shell

The external Svelte app should own the eventual native selected-run workspace:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Reason: the current `/` shell, case picker, model drawer, family browser, and
reasoning graph are already Svelte concepts. A polished root UX should be built
in source, not by continuing to inject more controls into compiled HTML.

### The Compiled Bundle Is A Distribution Artifact

`observatory/build/*` should be treated as a copied distribution artifact.

Allowed:

- copy a clean external build into this repo as a deliberate PR;
- record source commit and build hashes;
- smoke test the copied bundle through `observatory/serve_result.py`.

Not allowed:

- hand-edit compiled JS/CSS;
- treat compiled assets as the product source of truth;
- merge product UI logic only into the copied bundle.

## Current Product Gap

The existing root SPA still asks the user to start from:

```text
Cases | Families
```

After a case is selected, it presents useful Observatory panels, but it does not
natively express the global product workspace:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

The newer Learn/Receipts/Decision Work additions exist in the portable server
and injection layer. They are reviewable and useful, but they are not the final
native root UX.

## What Not To Present Twice

This source audit does not change the global information architecture. It
reinforces it.

| Information | Source owner | Native shell owner after port | Boundary |
| --- | --- | --- | --- |
| Revised answer and main run outcome | Runtime view model | Svelte Outcome tab | Do not copy into Learn as lesson body. |
| Teacher reasoning move | Runtime learning packet | Svelte Learn tab | Do not rename telemetry as teaching. |
| Mental model pages | Runtime product-safe model objects | Svelte Models surface | Do not expose raw Markdown as UI. |
| Relation pages | Runtime product-safe relation objects | Svelte Relations surface | Do not surface unsupported relation speculation. |
| Graph neighborhood | Runtime graph view model | Svelte Map surface | Graph edges are navigation, not proof. |
| Conversation Understanding status | Runtime receipt summary | Svelte Receipts surface | Do not put process brief inside Teacher lesson copy. |
| Raw audit telemetry | Runtime advanced routes | Advanced Audit links | Do not make telemetry the normal user landing page. |

## Source-Port Readiness Requirements

Do not port the global shell until these exist:

1. product view model contracts for selected run summary, outcome summary,
   learning packet, model page, relation page, graph neighborhood, receipt
   summary, and advanced audit index;
2. one fixture or checked safe run payload for native shell development;
3. a source-port package that records the external source repo, branch, commit,
   build command, expected output files, and copied asset hashes;
4. smoke tests against `observatory/serve_result.py` after copied build assets
   land;
5. a fallback policy that says what still works when `observatory/build/` is
   absent.

## Recommended Next Sequence

### PR-SO1 Source Ownership Audit

This document, review JSON, and tests.

Stop before code or UI changes.

### PR-SO2 Product View Model Contracts

Define shared product-safe view models:

- `selected_run_summary`;
- `outcome_summary`;
- `learning_packet`;
- `model_page`;
- `relation_page`;
- `graph_neighborhood`;
- `receipt_summary`;
- `advanced_audit_index`.

Stop before Svelte source work.

### PR-SO3 Portable View Model Adapters

Make the Python server expose the view models through stable APIs.

Stop before root SPA redesign.

### PR-SO4 Source-Port Package

Create a source-port packet for `Lolla-system-b/observatory/svelte-app`:

- source repo and commit;
- branch;
- local build command;
- build artifact manifest;
- runtime-copy checklist;
- smoke-test list.

Stop before copying a new bundle.

### PR-SO5 Native Global Shell In External Svelte Source

Build the selected-run workspace in Svelte source:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Stop before copying built assets into the runtime repo.

### PR-SO6 Runtime Bundle Sync

Copy a clean Svelte build into this repo with recorded hashes and smoke tests.

Stop before changing runtime launch behavior.

## Stop Conditions

Stop if implementation would require:

- running Lolla;
- invoking the Lolla skill;
- provider/model API calls;
- creating a new Lolla run;
- wiring or changing runtime behavior;
- mutating archives by default;
- hand-editing compiled JS/CSS;
- treating the external source as clean without a source-port manifest;
- claiming product proof;
- claiming human validation;
- claiming answer or advice correctness;
- adding answer-quality scoring;
- adding approval or certification labels;
- authorizing agent or automatic action;
- treating graph edges as proof;
- treating embedding similarity as validated relation semantics.

## Decision Gate

Recommended next gate:

```text
proceed_to_observatory_product_view_model_contracts
```

The reason is simple: before we move UI into the external Svelte source, both
the portable server and the future native shell need the same product-safe data
objects. Otherwise we will merely move the current fragmentation into a nicer
frontend.
