# Lolla Mental Model Atlas — Phase 1 local tracer bullet

This is a private, source-controlled React/TypeScript review application for
the Mental Model Atlas Phase 1 visual truth gate. It is not deployed, connected
to the ordinary Lolla runtime, connected to Observatory, or cleared for public
publication.

## What is implemented

- `/atlas` — a source-hash-bound 16-model visual neighborhood, persistent model
  or exact-relation selection, independent hover, stable selection camera,
  relation-type filters, truthful deterministic search, and explicit data and
  renderer failure states;
- `/models` — the equivalent non-canvas Library for the frozen slice;
- `/models/abstraction` — one card-first guided page with the complete canonical
  Markdown source divided into five reviewed human chapters, persistent
  orientation, an optional full-source inspection mode, the complete Abstraction
  knowledge-graph record, all 12 exact incident relations grouped in a compact
  accessible master/detail explorer, redundant line-and-text relationship
  semantics, and an explicit partial-page coverage vector;
- `/relations/abstraction__first-principles-thinking__ally` — one complete
  exact directed relation page;
- `/learn` — an honest boundary page; no Teacher journey is requested in Phase
  1;
- six deterministic pages covering all 233 real Confirmation Bias incident
  records without merging direction or parallel relations;
- source-backed fixtures for parallel ally/tension records, explicit authored
  bidirectionality, and a medium-confidence caution;
- SVG editorial and Canvas 2D renderers consuming the same validated projection
  and frozen coordinates;
- keyboard/list/table equivalents, reduced motion, explicit motion pause, and a
  mobile list-first route.

Only Abstraction has a complete source-card projection and a reviewed human
reading projection. The broader Abstraction learning page remains partial
because reviewed runtime-affordance presentation, distinct practice prompts,
and Teacher journeys are not part of this repair.
Other Library records are valid index records with explicit unavailable page
status. Only the named ally relation has a complete relation-page artifact.
Missing pages are not generated or repaired.

## Run locally

From the repository root, reproduce the checked-in projection first:

```bash
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_phase1_projection.py --validate-only
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_phase1_projection.py
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_card_first_repair.py --validate-only
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_card_first_repair.py
```

Then run the app:

```bash
cd apps/mental-model-atlas
npm ci
npm run check
npm test
npm run dev
```

For the production build used by the recorded browser review:

```bash
npm run build
./node_modules/.bin/vite preview --host 127.0.0.1 --port 4173
```

## Useful review URLs

```text
/atlas
/atlas?model=abstraction
/atlas?relation=abstraction__first-principles-thinking__ally
/atlas?fixture=mixed-parallel-relations&model=abstraction
/atlas?fixture=explicit-bidirectionality&model=active-listening
/atlas?fixture=confirmation-bias-hub&model=confirmation-bias&page=2
/atlas?fixture=medium-confidence-relation&relation=authenticity__rationalization__antagonist
/atlas?model=abstraction&renderer=canvas
/models
/models/abstraction
/relations/abstraction__first-principles-thinking__ally
/learn
```

## Source and projection boundary

The deterministic builder reads the checked-in model manifest, knowledge graph,
relationship graph, model Markdown, and curation files only after verifying the
frozen primary source hashes. It copies or presentation-normalizes source text;
it does not call a provider, infer relation meaning, assign importance, or fill
missing sections.

The public review projection declares:

- stable model and exact relation IDs;
- source and curation references;
- page counts and deterministic order;
- stable precomputed coordinates and hashes;
- review, rights, publication, and missingness state;
- explicit nonclaims.

Graph position, visual emphasis, relation confidence, and connection count are
navigation metadata. They are not truth, relevance, usefulness, importance, or
mastery certification.

## Current lifecycle

The card-first guided-reader repair is ready for founder visual and product
review. Its light editorial and segmented-color visual language is currently a
route-scoped Abstraction tracer, not a completed redesign of the global SVG or
Canvas graph. The Mental Model Teacher component remains `park` because four gates
are still open: founder learning-journey acceptance, native screen-reader review,
source-rights/publication review, and a separately authorized real-user
usefulness study. Phase 2, Teacher journeys, deployment, live-runtime links,
and Observatory links are not authorized.

See:

- [Phase 1 result](../../docs/product/lolla-mental-model-atlas-phase1-visual-truth-tracer-bullet-result-2026-07-15.md)
- [Card-first truthfulness repair](../../docs/product/lolla-mental-model-atlas-card-first-truthfulness-repair-result-2026-07-16.md)
- [Card-first evidence](../../docs/evals/lolla-mental-model-atlas-card-first-repair-evidence-v1.json)
- [Renderer decision](../../docs/product/lolla-mental-model-atlas-phase1-renderer-decision-2026-07-15.md)
- [Evidence receipt](../../docs/evals/lolla-mental-model-atlas-phase1-evidence-v1.json)
- [Product PRD](../../docs/product/lolla-mental-model-atlas-and-teacher-prd-v1.md)
