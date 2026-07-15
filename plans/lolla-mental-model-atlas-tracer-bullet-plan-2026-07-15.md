# Plan: Lolla Mental Model Atlas and Teacher

> Source PRD: [Lolla Mental Model Atlas and Teacher PRD v1](../docs/product/lolla-mental-model-atlas-and-teacher-prd-v1.md)

Status: prospective plan; no implementation phase is authorized

Date: 2026-07-15

Canonical planning base: `2f05fd1ca7081f602317d670faad8d1293d5b0ff`

## Planning Decision

Build through narrow, complete tracer bullets. Each phase must connect real
canonical source, deterministic product projection, user-visible behavior,
accessibility, tests, and a human gate. A phase that only adds schemas, only
generates data, or only paints an attractive graph does not qualify as
complete.

No phase automatically authorizes the next. The Mental Model Teacher remains
parked until a separate founder authorization starts Phase 1 and that phase
passes its gate.

## Architectural Decisions

- **Product shape:** Atlas is self-directed exploration; full pages carry
  durable knowledge; Teacher is a curated journey and practice layer.
- **Routes:** `/atlas`, `/models`, `/models/:slug`,
  `/relations/:relationId`, `/learn`, and `/learn/:journeyId`.
- **Public schema:** a versioned `lolla.atlas_projection.v1` projection owns
  public model, exact directed relation, layout, page, and journey identity.
- **Compatibility:** existing Teacher v0 artifacts remain valid historical and
  small-lesson inputs; Observatory keeps its bounded workspace contract. Any
  reuse goes through explicit adapters.
- **Application boundary:** a new source-controlled static TypeScript app, not
  a mutation of compiled Observatory assets.
- **Source boundary:** canonical model IDs begin with the 222-entry source
  manifest. Directory filenames do not define the corpus.
- **Relation boundary:** the default Atlas layer contains exact curated ally,
  antagonist, and tension records. Direction and parallel records survive.
- **Overview boundary:** all 222 models may be positioned, but the idle view
  draws zero relations. Focused relation pages draw no more than 40 exact
  records and disclose shown, available, and omitted counts.
- **Overlay boundary:** tendencies, prerequisites, reframing, and structural
  dimensions are separate named overlays. They do not silently enter the
  relation map.
- **Family boundary:** current family semantics overlap and cover only part of
  the corpus. They are optional filters, not an exhaustive partition or layout
  authority.
- **Layout:** precomputed, versioned, hash-bound coordinates. Browser visits do
  not re-run a semantic layout.
- **Renderer:** selected by the Phase 1 same-data visual spike. Sigma.js stable
  is the recommended baseline; Cytoscape.js is the semantic-interaction
  control; custom WebGL is considered only if necessary.
- **Deployment:** local only until source rights, attribution, privacy, and
  public projection review pass.
- **Runtime:** no ordinary live-pipeline, R4, Decision Trail, Decision Work,
  embedding, retrieval, or relationship-curation changes.
- **Providers:** zero provider calls and `$0.00` until a different exact goal is
  separately authorized.
- **Truth:** graph position and salience are navigation, not proof of relevance,
  correctness, usefulness, importance, or mastery.

---

## Phase 1: Visual Truth Tracer Bullet

**User stories:** `US-02`, `US-03`, `US-04`, `US-05`, `US-08`, `US-09`

### What to build

Create one local, source-backed vertical slice from real canonical models and
relations to a polished Atlas interaction. Use a frozen 12-to-20-model ordinary
neighborhood plus the real mixed-relation, bidirectional, and hub-pagination
fixtures. Produce a deterministic projection and stable layout, render the
same projection through bounded renderer candidates, support durable selection
and independent hover, open one complete model page and one complete relation
page, and provide the synchronized keyboard/list alternative.

The slice is a visual and semantic truth test. It is not an SVG-only data demo,
a full-corpus build, or an invitation to tune generated copy.

### Acceptance criteria

- [ ] Every displayed node and relation resolves to canonical IDs, source
  hashes, and product-safe source references.
- [ ] `abstraction -> first-principles-thinking` preserves separate ally and
  tension records.
- [ ] `active-listening` and `prisoners-dilemma` preserve explicit records in
  both directions.
- [ ] The `confirmation-bias` fixture reports 233 incident records, uses a
  maximum 40-record canvas page, and discloses omitted counts without calling
  them irrelevant.
- [ ] Selected state persists while hover previews another model.
- [ ] Selection dims unrelated context rather than rebuilding or erasing the
  map.
- [ ] Browser Back/Forward restores durable selection; hover never enters
  history.
- [ ] One model page and one relation page are understandable without the
  graph and expose source, review, missingness, and non-claims.
- [ ] A synchronized semantic list and directed relation table provide the same
  durable information without canvas interaction.
- [ ] Keyboard navigation, visible focus, reduced motion, and WebGL/canvas
  failure fallback pass manual review.
- [ ] The recorded 1920 x 1200 scenarios meet the founder's composition,
  motion, panel, and continuity bar.
- [ ] Input acknowledgement and hover begin within 100 ms; selection settles
  within 450 ms; the recorded performance profile meets the PRD frame budget.
- [ ] The renderer decision records evidence for the selected and rejected
  candidates.
- [ ] No provider, runtime, Observatory, R4, archive, private conversation, or
  public deployment path is constructed.

### Stop gate

Stop and revise or re-park if the graph is primarily spectacle, if exact
direction/multi-edge semantics become unreadable, if non-canvas access is
materially inferior, or if no candidate can meet the visual bar within the
bounded slice.

---

## Phase 2: Complete Atlas Projection And Stable Global Layout

**User stories:** `US-01`, `US-02`, `US-03`, `US-04`, `US-06`, `US-08`, `US-09`

### What to build

Extend the proven vertical slice to the complete 222-model identity set and the
1,358-record default relation index. Deliver the lean idle overview, stable
precomputed layout, model search, exact focused relation paging, filters,
URL-addressable state, complete non-canvas relation access, and data/layout
manifests. Preserve the successful Phase 1 visual system without turning the
screen into an all-edge hairball.

### Acceptance criteria

- [ ] The Atlas projection contains exactly 222 canonical model IDs and every
  model-source hash matches the canonical manifest.
- [ ] The default relation index contains exactly 523 ally, 344 antagonist,
  and 491 tension records.
- [ ] Idle state renders all model positions and zero relation edges with a
  truthful scope label.
- [ ] Focused pages preserve direction, parallel records, deterministic order,
  total counts, pagination, and omission counts.
- [ ] Search and filters return distinct `completed_zero`, `partial`, `failed`,
  and `missing` states.
- [ ] Global layout coordinates and their hash reproduce across identical
  builds; filters do not move the user's map.
- [ ] Family filters are overlapping and optional; 147 currently uncovered
  models remain explicit rather than being force-assigned.
- [ ] The initial compressed graph payload and first-useful-paint targets pass
  under the recorded reference profile.
- [ ] All Phase 1 accessibility, visual-state, semantic-fixture, and performance
  tests pass against the complete projection.
- [ ] No full article bodies or V60 affordance package are loaded by the
  initial graph route.

### Stop gate

Stop before page/content expansion if the complete index breaks the Phase 1
interaction, accessibility, or truthfulness bar. A larger corpus is not a
reason to weaken exact record custody.

---

## Phase 3: Complete Library And Durable Model/Relation Pages

**User stories:** `US-04`, `US-05`, `US-06`, `US-08`

### What to build

Turn the Atlas into a durable reference work. Add the complete searchable
Library and deterministic page coverage for all canonical models and relation
records, while making section-level source, curation, human review,
missingness, and publication rights visible. Translate reviewed source fields
into readable pages; do not fill gaps with plausible prose.

### Acceptance criteria

- [ ] Every canonical model has a stable page state: available, partial,
  blocked by review/rights, or unavailable.
- [ ] Every default relation record has a stable relation route or an explicit
  disclosed unavailable state.
- [ ] Relation pages preserve source direction and reciprocity rather than
  rendering an unordered pair.
- [ ] Library and page navigation provide complete non-canvas access to the
  corpus.
- [ ] The public projection contains no local paths, runtime rankings,
  embedding scores, private artifacts, raw provider material, or unreviewed
  invented text.
- [ ] Per-section provenance and missingness are visible without turning the
  page into a developer receipt.
- [ ] Authorship, redistribution rights, attribution, and publication status
  are accounted for before any public deployment.
- [ ] Cold reviewers can explain a model and relation and identify what remains
  provisional.

### Stop gate

If rights or source quality do not support a full public corpus, ship nothing
public automatically. Return with a clearly bounded source-cleared subset or
re-park the public surface.

---

## Phase 4: First Curated Teacher Journey

**User stories:** `US-07`, `US-05`, `US-04`, `US-08`

### What to build

Create one source-cleared, human-reviewed journey through three to seven models
and two to six exact relation lessons. Connect its question, ordered model
sequence, relation explanations, worked contrast, practice reps, and
do-not-overlearn boundaries to the same Atlas pages and graph identities.

### Acceptance criteria

- [ ] The learning objective and intended audience are explicit.
- [ ] Every step has an editorial sequencing reason; graph centrality does not
  select the order.
- [ ] Each relation lesson resolves to the same public relation object used by
  the Atlas.
- [ ] Practice asks the user to apply or distinguish a reasoning move without
  claiming advice correctness or mastery.
- [ ] The focused journey graph and complete Atlas remain mutually navigable.
- [ ] Human review covers educational clarity, relation understanding,
  practice value, overlearning risk, source status, and non-claims.
- [ ] A cold reviewer can complete the journey without implementation context.

### Stop gate

Stop if the journey reads like a glossary slideshow, decision advice,
telemetry, or a private-run interpretation. Do not create more journeys until
the first one earns learner evidence.

---

## Phase 5: Optional Read-Only Lolla And Observatory Bridge

**User stories:** `US-10`, `US-05`, `US-04`

### What to build

Only after the independent public product works, add a read-only bridge from a
source-custodied Lolla run or Observatory model reference to the same Atlas
model and relation routes. Pass stable public IDs and explicit run-provenance
labels; keep private prose and interpretation in their original archive.

### Acceptance criteria

- [ ] The bridge is optional, read-only, fail-closed, and does not block archive
  or Observatory behavior.
- [ ] Only stable model/relation IDs and safe locators cross the boundary.
- [ ] The Atlas does not infer that a linked model was relevant, applied,
  helpful, or decisive.
- [ ] Private conversation, memo, pressure text, dispositions, and Decision
  Work state do not enter the public payload.
- [ ] Missing or unknown IDs remain missing/quarantined rather than repaired.
- [ ] The ordinary four-lane pressure pipeline is unchanged.

### Stop gate

Stop if the bridge requires a new semantic reader, private-data replication,
runtime coupling, or an authority claim. The Atlas remains independently
useful without this phase.

---

## Phase 6: Real-User Evidence And Architecture Decision

**User stories:** all, evaluated as product behavior rather than implementation

### What to build

Run separately authorized cold-truthfulness and consent-bound learner studies.
Compare the Atlas/journey with a model list or static article, preserve the
full evidence vector and reviewer disagreement, then make one product
investment decision.

### Acceptance criteria

- [ ] Reviewers can find, explain, and distinguish model/relation semantics
  without treating graph salience as authority.
- [ ] The study records navigation, understanding, correction burden,
  distraction, practice transfer, trust, privacy reaction, and qualitative
  usefulness separately.
- [ ] The graph demonstrates incremental orientation or learning value over the
  comparison surface.
- [ ] No scalar score erases mixed evidence.
- [ ] The founder selects exactly one outcome: expand Atlas and Teacher, keep
  Library/pages only, revise the product shape, or re-park Teacher.

### Stop gate

If the product is beautiful but does not improve understanding or creates
recurring semantic overclaim, narrow or re-park it. Do not justify expansion by
the amount of code, content, or graph work already completed.

## Exact Next Decision

This plan remains prospective until the PRD is reviewed and published. The
first eligible authorization is only:

```text
authorize_mental_model_atlas_visual_truth_tracer_bullet
```

It carries zero provider calls, `$0.00`, no public deployment, and no authority
for Phases 2 through 6.
