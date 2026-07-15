# Mental Model Atlas Phase 1 Visual Truth Tracer Bullet Result

Status: local implementation complete; founder truth gate pending; unpublished

Date: 2026-07-15

Decision:

`phase1_local_visual_truth_tracer_bullet_complete_founder_gate_pending`

## Executive result

Lolla now has a source-controlled, provider-free local Atlas slice that shows
the intended product shape with real canonical data. A visitor can see a stable
16-model territory, select a model or exact directed relation, preview a second
model without losing the selection, search and filter the visual and semantic
views together, move through all six pages of a 233-record hub, read one
complete model page and one complete relation page, and continue through
keyboard/list/table routes when the visual renderer is unavailable.

The implementation is materially different from the parked v0 prototypes: the
projection is hash-bound to current source, the browser app is source-controlled
React/TypeScript rather than compiled Observatory output, and graph, page,
missingness, failure, accessibility, and performance evidence share one stable
contract.

This does not unpark Teacher yet. Founder visual acceptance, a native screen
reader pass, publication-rights review, and real-user usefulness evidence are
still missing. Phase 2, Teacher journeys, deployment, runtime integration, and
Observatory integration remain unauthorized.

Provider calls: 0.

Provider cost: $0.00.

## What was built

### Deterministic real-data projection

The builder at
[`build_mental_model_atlas_phase1_projection.py`](../../scripts/product/build_mental_model_atlas_phase1_projection.py)
verifies the frozen hashes of:

- `data/model_sources/manifest.json`;
- `data/knowledge_graph.json`;
- `data/relationship_graph.json`.

It then produces twelve local-review artifacts:

- one 16-model ordinary neighborhood;
- one parallel ally/tension fixture;
- one explicitly bidirectional fixture;
- six deterministic Confirmation Bias hub pages covering exactly 233 canonical
  incident records in source order;
- one exact medium-confidence source relation;
- one complete Abstraction page;
- one complete Abstraction → First Principles Thinking ally page.

The hub pages contain 40, 40, 40, 40, 40, and 33 records. Their union equals
the complete canonical incident sequence, source pointers preserve exact graph
indices, and every model shared by multiple pages keeps the same coordinate.
The fixture family is `confirmation_bias_hub`; page identity appears only in
the projection ID, filename, and page contract.

Projection-manifest SHA-256:

`203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52`

### Source-controlled application

The application lives at [`apps/mental-model-atlas`](../../apps/mental-model-atlas/README.md).
Its production dependencies are exact-pinned React 19.1.0 and React DOM 19.1.0.
TypeScript, Vite, Vitest, jsdom, and Testing Library are exact-pinned development
dependencies. `npm audit` reported zero vulnerabilities at implementation
closeout.

Routes:

- `/atlas`;
- `/models`;
- `/models/:slug`;
- `/relations/:relationId`;
- `/learn` and the reserved `/learn/:journeyId` boundary.

Durable graph state uses the History API and stable URL parameters. Model and
relation selection enter browser history; hover does not. Back/Forward restores
the exact durable object. Search with one match produces one graph node and one
semantic-list object without changing frozen coordinates. A valid no-match
search is `completed_zero`; an unknown ID is `missing`; a request or schema
failure is `failed`.

### Spatial and semantic interaction

The SVG renderer is the local default. Selection moves and scales a stable
camera group toward the chosen model or relation while source coordinates stay
unchanged. Unrelated context dims instead of disappearing. Hover can preview a
different model while the selected panel remains persistent.

Every exact focused relation remains a separate object. The app visibly and
semantically preserves:

- parallel Abstraction → First Principles Thinking ally and tension records;
- separately authored Active Listening ↔ Prisoners Dilemma directions;
- relation type through text plus solid, dashed, or dotted line treatment;
- source direction, explicit reciprocity, confidence, curation, and source
  status;
- a stronger non-certification caution for the exact medium-confidence
  Authenticity → Rationalization antagonist record.

### Non-canvas and failure equivalents

The semantic model list and exact directed relation table remain available
independently of SVG or Canvas. Model nodes, SVG relation objects, list records,
and relation-table controls are keyboard operable and expose selection state.
Clearing a selected panel returns focus to the originating model object.

The following remain distinct and were captured:

- valid completed zero;
- unknown stable ID;
- failed projection load;
- failed Canvas renderer with the semantic route preserved;
- incomplete page coverage;
- source-review and publication-rights status.

At 390 × 844, the dense graph is withheld and the app explicitly leads with
the source-backed list. There was no horizontal overflow. Under
`prefers-reduced-motion`, the app disables motion and keeps all semantic tasks
available.

## Independent review and repairs

An independent browser/architecture review initially blocked acceptance. Its
contradicting evidence identified seven real gaps:

1. selection did not move a camera;
2. search filtered the semantic list but not the graph;
3. the URL accepted `page=2` while serving page one;
4. clearing selection lost keyboard focus and relation selection was not
   announced;
5. Library copy blurred index completeness and full-page availability;
6. medium-confidence and failed-source scenarios were not recorded;
7. the checked-in visual, renderer, and performance receipt was incomplete.

The implementation now addresses each mechanical gap. A second architecture
review then found a subtler identity error: all hub pages inherited a “page 1”
fixture name and the frontend would admit any supported fixture in response to
another fixture request. The final contract uses a page-neutral hub family,
binds returned fixture and page to the request, reconciles every count and
ordered relation ID in both Python and TypeScript, and tests exact canonical
membership and source pointers.

The review did not decide the founder-owned aesthetic or product gates.

## Renderer result

The local decision is:

- SVG editorial: selected Phase 1 default;
- Canvas 2D: retained same-data comparison and failure control;
- Sigma.js/Cytoscape.js: deferred to the complete-corpus renderer recheck.

The bounded SVG gives each source object DOM identity, focus, selected state,
and exact relation semantics with a 1,579-byte gzip renderer chunk. Canvas
proved replaceability and same-coordinate rendering, but its accessibility and
hit testing require parallel handwritten logic. The complete rationale is in
the [renderer decision](lolla-mental-model-atlas-phase1-renderer-decision-2026-07-15.md).

This is a deliberate narrowing from the prospective plan, not a universal
rejection of Sigma or Cytoscape. A 222-model phase must re-run the renderer
decision instead of treating this bounded result as proof of scale.

## Performance result

Recorded profile: Headless Chrome 145.0.7632.6, 1920 × 1200, DPR 1, local
production Vite preview, unthrottled localhost.

- new-session first contentful paint: 424.0 ms;
- new-session Atlas useful mark: 586.8 ms;
- same-session reload Atlas useful mark: 369.8 ms;
- ten-sample selection two-frame p50/p95: 62.2 / 127.9 ms;
- ten-sample hover one-frame p50/p95: 16.9 / 18.3 ms;
- 300-frame p50/p95/worst: 16.7 / 18.3 / 20.6 ms;
- frames above 20 ms: 1; above 50 ms: 0;
- first-route resource transfer: 94,347 bytes;
- ordinary projection: 96,070 bytes raw / 12,340 bytes gzip;
- hub page one: 129,976 bytes raw / 17,770 bytes gzip.

This passes the Phase 1 local interaction bounds. It is not a public-network,
low-end-device, or complete-corpus benchmark.

## Evidence packet

The machine-readable evidence receipt is
[`lolla-mental-model-atlas-phase1-evidence-v1.json`](../evals/lolla-mental-model-atlas-phase1-evidence-v1.json).
It binds twenty final screenshots, browser/profile facts, performance samples,
projection custody, accessibility/failure observations, and the still-open
human gates.

The screenshot packet covers:

- idle truth;
- selected model;
- selection plus independent hover;
- selected exact relation;
- relation filtering;
- reduced motion;
- keyboard selection;
- parallel and bidirectional relations;
- hub page two;
- completed zero, missing ID, failed renderer, and failed projection;
- Canvas comparison;
- medium-confidence caution;
- complete model and relation pages;
- mobile list-first Atlas and model page.

## What remains intentionally absent

- complete 222-model projection;
- complete 1,358-relation public index;
- the other 221 complete model pages;
- the other relation pages;
- family filter semantics, because the current families overlap and are not a
  reviewed exhaustive partition;
- Teacher journeys or practice;
- publication or deployment;
- source-rights clearance;
- native VoiceOver/NVDA evidence;
- real-user learning or usefulness evidence;
- ordinary runtime, archive, R4, Decision Trail, Decision Work, or Observatory
  connections.

The local Library truthfully says that one of sixteen index records has a
complete Phase 1 page. It does not describe unavailable pages as complete.

## Lifecycle decision

The Stage 0 register now records the local tracer bullet while keeping Mental
Model Teacher at `park`. That is the correct state:

- the specific founder-selected user job now has an implementation;
- source, interaction, failure, and performance mechanics are inspectable;
- the human visual, accessibility, rights, and usefulness gates have not been
  satisfied.

No current Lolla live path changed. No product-usefulness claim is earned.

## Verification

Provider-free verification completed against the combined implementation and
documentation tree:

- deterministic projection, exact source-membership, pagination, evidence-hash,
  Stage 0 register, and PRD lifecycle tests: passed;
- Atlas TypeScript check: passed;
- Atlas Vitest suite: 13 passed;
- Atlas production build: passed;
- Atlas production dependency audit: zero known vulnerabilities;
- Stage 0 addendum register validation: valid, with 25 components, 24
  connections, 17 constitutional rules, 26 Decision Trail field groups, and
  638 accounted implementation files;
- complete repository suite: 4,990 passed and 93 subtests passed;
- complete-suite failures: zero;
- warning: one existing `datetime.utcnow()` deprecation warning in
  `scripts/stability_check.py`;
- changed JSON parsing: passed;
- changed Python compilation: passed;
- screenshot path and SHA-256 reproduction: passed;
- local-link, whitespace, added-material secret, and Git object-integrity
  checks: passed;
- provider calls and cost: 0 and `$0.00`.

The browser review exercised the local production build rather than a design
mock. It covered desktop, reduced-motion, keyboard, Canvas comparison and
failure, failed projection, medium-confidence, completed-zero, missing-ID,
hub-page, complete-page, and 390-pixel mobile scenarios. Automated and headless
browser evidence does not stand in for the still-pending founder visual or
native screen-reader gates.

## Git custody

The work was isolated on
`agent/mental-model-atlas-visual-truth-tracer-bullet` from the exact PRD
checkpoint `838546ec012610f3f900a163cabf169a9c191f03`. The provider-free
checkpoint sequence preserves the projection before the application and the
application before review-driven repair:

1. `e3bca896` — `feat: freeze Mental Model Atlas Phase 1 projection`;
2. `3537013a` — `feat: build Mental Model Atlas visual truth tracer bullet`;
3. `0efe8a99` — `fix: close Atlas Phase 1 truthfulness gaps`.

The final lifecycle/evidence closeout is additive to those checkpoints. No
branch was pushed, no pull request was opened, no merge or deployment was
performed, and the founder-owned shared worktree was not switched, staged,
stashed, reset, cleaned, or committed.

## Exact next founder decision

Review the checked-in visual packet and local app, then decide only whether the
Phase 1 composition, camera, relation readability, panel continuity, and
non-canvas equivalence meet the intended product bar.

If that visual decision passes, the remaining native screen-reader and source-
rights checks should be completed before any Phase 2 authorization. Publication
of this branch, Phase 2, Teacher journeys, public deployment, and a real-user
study are separate decisions.
