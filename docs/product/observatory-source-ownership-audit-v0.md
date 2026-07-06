# Observatory Source Ownership Audit v0

Status: source ownership decision contract
Date: 2026-07-06
Decision gate: `proceed_to_observatory_portable_server_view_model_contracts`

## One Sentence

Observatory is one portable skill-presentation product shell: the Python server
in this repo owns the active product direction for now, while
`Lolla-system-b/observatory/svelte-app` is verified as the historical legacy
source for the old root SPA, not the future product source by default.

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

If we keep adding product UI through ad hoc serve-time injection, the UI will
stay fragmented. If we jump back into the legacy Svelte app, we revive the old
app-like direction instead of designing Observatory as the portable presentation
surface for the skill. The safe path is to make the Python/server-rendered
Observatory coherent first, using product-safe view models instead of raw
telemetry or scattered panels.

This audit verifies the current ownership shape and chooses the next safe
implementation sequence.

Related design trail:

- [Observatory Global Product Experience And Data Flow](observatory-global-product-experience-and-data-flow-v0.md)
- [Mental Model Teacher Observatory Ownership and Portability Boundary](mental-model-teacher-observatory-ownership-portability-boundary-v0.md)
- [Mental Model Teacher Observatory Integration Design](mental-model-teacher-observatory-integration-design-v0.md)
- [Observatory Conversation Understanding Boundary](observatory-conversation-understanding-boundary-v0.md)

## Short Verdict

The source owner is split by role, but the current product direction is not
split:

| Responsibility | Owner today | Decision |
| --- | --- | --- |
| Local serving, routing, archive/run loading, read-only APIs | `observatory/serve_result.py` in this repo | Keep here. This is the portable runtime boundary. |
| Server-rendered audit, usage, Learn, Receipts, and process-brief status | `observatory/serve_result.py` in this repo | Keep here as the active product surface direction. |
| Historical root SPA source for `/` | `Lolla-system-b/observatory/svelte-app` | Treat as legacy source evidence for the old app-era shell, not as the default future owner. |
| Checked-in runtime bundle | `observatory/build/*` in this repo | Treat as copied compiled output, not source. Do not hand-edit. |
| Product IA and contracts | `docs/product/*`, future view-model modules in this repo | Keep here because the portable runtime must own product-safe translation. |
| Future global selected-run shell | Portable Python/server-rendered Observatory first | Build here unless a later explicit frontend decision says otherwise. |

The next PR should not be another UI patch and should not be a Svelte revival.
It should define the product view model contracts that let the portable server
render Observatory as one coherent product surface.

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

That means this repo cannot be treated as a native Svelte source tree. That is
acceptable for the current direction: Observatory should remain portable and
server-rendered while the skill presentation surface is still being shaped.

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

This verifies that the historical root SPA source exists and is real. It also
verifies the user's concern: the Svelte source is app-era legacy for the current
product direction. It is not current with the latest product-surface additions
in this runtime repo and should not be treated as the default future UI owner.

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
byte-identical. Therefore, if we ever intentionally maintain or replace the
legacy root bundle, it needs a controlled sync path:

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

### Portable Runtime Repo Owns Product-Safe Translation And Rendering

This repo should own:

- selected-run archive loading;
- source custody and missingness;
- read-only sidecar discovery;
- product-safe model/relation/learning/receipt view models;
- API endpoints consumed by any UI;
- server-rendered fallback pages for audit, usage, Learn, and Receipts;
- the near-term global Observatory shell;
- runtime-safe non-claims.

Reason: this repo ships with the skill runtime. It must remain useful without a
frontend toolchain, and it is closest to the archive artifacts and product
boundaries.

### External Svelte Source Is Legacy Evidence, Not Current Direction

The external Svelte app proves where the old compiled root SPA came from. It
should not own the next Observatory product surface by default.

Reason: the current product goal is not to return to the old app project. The
goal is to make Observatory the portable presentation layer for the skill. The
old Svelte source can remain useful as visual/reference evidence, but a future
Svelte revival would require a separate explicit decision.

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
and injection layer. They are reviewable and useful, but the next product step
is not to port them to Svelte. The next product step is to replace scattered
injection with a coherent server-rendered workspace backed by stable view
models.

## What Not To Present Twice

This source audit does not change the global information architecture. It
reinforces it.

| Information | Source owner | Portable product home | Boundary |
| --- | --- | --- | --- |
| Revised answer and main run outcome | Runtime view model | Server-rendered Outcome | Do not copy into Learn as lesson body. |
| Teacher reasoning move | Runtime learning packet | Server-rendered Learn | Do not rename telemetry as teaching. |
| Mental model pages | Runtime product-safe model objects | Server-rendered Models | Do not expose raw Markdown as UI. |
| Relation pages | Runtime product-safe relation objects | Server-rendered Relations | Do not surface unsupported relation speculation. |
| Graph neighborhood | Runtime graph view model | Server-rendered Map | Graph edges are navigation, not proof. |
| Conversation Understanding status | Runtime receipt summary | Server-rendered Receipts | Do not put process brief inside Teacher lesson copy. |
| Raw audit telemetry | Runtime advanced routes | Advanced Audit links | Do not make telemetry the normal user landing page. |

## Portable Server Direction Requirements

Do not build more visible product panels until these exist:

1. product view model contracts for selected run summary, outcome summary,
   learning packet, model page, relation page, graph neighborhood, receipt
   summary, and advanced audit index;
2. one fixture or checked safe run payload for server-rendered shell
   development;
3. stable portable server adapters that produce those view models without
   provider calls or runtime mutation;
4. smoke tests against `observatory/serve_result.py`;
5. a fallback policy that says what works when the legacy `observatory/build/` is
   absent.

## Recommended Next Sequence

### PR-SO1 Source Ownership Audit

This document, review JSON, and tests.

Stop before code or UI changes.

### PR-SO2 Portable Product View Model Contracts

Define shared product-safe view models:

- `selected_run_summary`;
- `outcome_summary`;
- `learning_packet`;
- `model_page`;
- `relation_page`;
- `graph_neighborhood`;
- `receipt_summary`;
- `advanced_audit_index`.

Stop before additional UI rendering.

### PR-SO3 Portable View Model Adapters

Make the Python server expose the view models through stable APIs.

Stop before root workspace redesign.

### PR-SO4 Server-Rendered Global Workspace

Use the view models to render the selected-run workspace in the portable server:

```text
Outcome | Learn | Models | Relations | Map | Receipts
```

Stop before touching legacy bundle assets.

### PR-SO5 Legacy Root Bundle Bypass Or Retirement Plan

Decide whether `/` should route to the server-rendered workspace while the old
compiled SPA remains available as legacy/advanced navigation.

Stop before deleting or replacing the checked-in bundle.

### PR-SO6 Optional Legacy Bundle Sync Decision

Only if there is a strong reason to keep the old Svelte root shell, create a
separate decision and sync package for the legacy bundle.

Stop before Svelte source changes or bundle copies.

## Stop Conditions

Stop if implementation would require:

- running Lolla;
- invoking the Lolla skill;
- provider/model API calls;
- creating a new Lolla run;
- wiring or changing runtime behavior;
- mutating archives by default;
- hand-editing compiled JS/CSS;
- treating the external Svelte source as the future product owner without a new
  explicit decision;
- porting the global shell to the legacy app by default;
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
proceed_to_observatory_portable_server_view_model_contracts
```

The reason is simple: before we add more server-rendered UI, the portable
Observatory needs product-safe data objects. Otherwise we will keep stacking
panels instead of designing one coherent skill presentation surface.
