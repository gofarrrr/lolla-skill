# Lolla Mental Model Atlas — canonical Phase 1 experimental baseline

This is a local, source-controlled React/TypeScript review application for
the Mental Model Atlas Phase 1 visual truth gate. It is not deployed, connected
to the ordinary Lolla runtime, connected to Observatory, or cleared for public
content distribution.

Requires Node.js `>=20.19.0`. The controlling data status is the
[Atlas custody V2 result](../../docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md).
The [Atlas baseline publication result](../../docs/product/lolla-mental-model-atlas-baseline-publication-result-2026-07-17.md)
and its V1 packages remain immutable reviewed checkpoints.

## What is implemented

- `/atlas` — a source-hash-bound 16-model visual neighborhood, persistent model
  or exact-relation selection, independent hover, a full-field selection view,
  collision-aware labels, one relation key, pausable source-to-target motion,
  truthful deterministic search, and explicit data and renderer failure states;
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

From the repository root, validate the checked-in V2 projection and its frozen
V1 boundary first:

```bash
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_custody_v2.py --validate-only
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_custody_v2.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_phase1_projection.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_card_first_repair.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_navigation_index.py
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
/atlas?model=root-cause-analysis
/atlas?model=five-whys-method
/atlas?model=confirmation-bias&page=2
/atlas?relation=abstraction__first-principles-thinking__ally
/atlas?review=1&fixture=mixed-parallel-relations&model=abstraction
/atlas?review=1&fixture=explicit-bidirectionality&model=active-listening
/atlas?review=1&fixture=confirmation-bias-hub&model=confirmation-bias&page=2
/atlas?review=1&fixture=medium-confidence-relation&relation=authenticity__rationalization__antagonist
/atlas?review=1&model=abstraction&renderer=canvas
/models
/models/abstraction
/relations/abstraction__first-principles-thinking__ally
/learn
```

## Source and projection boundary

The deterministic V2 builder reads the checked-in model manifest, knowledge
graph, relationship graph, model Markdown, and curation files only after
verifying their current repository-local hashes. It hash-locks every V1 package,
then proves that V2 differs only in declared custody fields. It copies or
presentation-normalizes source text; it does not call a provider, infer relation
meaning, assign importance, or fill missing sections.

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

The card-first guided-reader repair and the cross-route design-system
consolidation are ready for founder visual and product review. The current
candidate is an intentionally achromatic **precise editorial cartography**
system shared by Atlas, Library, Abstraction, the exact relation page, Learn,
and application states. It uses typography, spacing, hairlines, strong rules,
line form, direction, and structural motion so those fundamentals can be
judged before color returns.

[`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) is the binding visual contract. The
application imports only `src/design-system/index.css`; its ordered route
modules replace the removed monolithic and restraint override stylesheets.
New exceptions must be added to the contract rather than hidden in route-local
overrides.

The latest graph-legibility repair fixes a renderer/CSS naming mismatch that
had produced opaque label-covering nodes and visually identical edges. All
loaded models now remain visible after selection. Ally, antagonist, and tension
use solid, dashed-with-cross, and double lines respectively; arrows and moving
markers show authored direction; and the global motion control pauses them.

The subsequent neighborhood-navigation repair removes the old fixture-page
ceiling from ordinary clicks. A sanitized, deterministic local index contains
all 222 canonical model identities and all 1,358 checked-in relationship
records. Selecting a model derives its exact incoming and outgoing
neighborhood, paginates above 40 records, and lets any newly revealed neighbor
become the next center. This is graph traversal, not relationship inference.

The latest founder-feedback repair keeps `Model Library / Abstraction` on one
aligned line and removes the repeated source-title introduction: `Understand`
now enters the chapter reader directly, while the exact title returns in the
explicit full-source mode.
The current local first-viewport repair shortens the Atlas, Library, and model
openings; exposes deterministic named model actions; makes exact search results
selectable by click or Enter; keeps selected meaning and the available full-page
action in the first representative laptop/mobile viewport; turns connection
counts into filters; and progressively discloses relationship grammar. It adds
no model, relation, teaching content, inference, provider, or product claim.
The shared application shell now uses the founder-supplied lowercase `lolla`
wordmark. Its exact original bytes and provenance note live under
`public/brand/`; the checkerboard is part of the RGB source, so CSS clips and
contrasts the original at display time without rewriting the asset. The header
uses the wordmark alone without a descriptive subtitle beneath it.
The previous vibrant-editorial pass is superseded historical evidence; no
future palette has been selected. The Mental Model Teacher component remains `park` because four gates
are still open: founder learning-journey acceptance, native screen-reader review,
source-rights/publication review, and a separately authorized real-user
usefulness study. Phase 2, Teacher journeys, deployment, live-runtime links,
and Observatory links are not authorized.

See:

- [Current Atlas custody V2 result](../../docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md)
- [Current Atlas custody V2 evidence](../../docs/evals/lolla-mental-model-atlas-custody-v2-evidence.json)
- [Canonical Atlas baseline publication](../../docs/product/lolla-mental-model-atlas-baseline-publication-result-2026-07-17.md)
- [Current first-viewport interaction repair](../../docs/product/lolla-mental-model-atlas-first-viewport-repair-result-2026-07-17.md)
- [Controlling Atlas baseline consolidation](../../docs/product/lolla-mental-model-atlas-baseline-consolidation-result-2026-07-17.md)
- [Current Atlas baseline evidence](../../docs/evals/lolla-mental-model-atlas-baseline-consolidation-evidence-v1.json)
- [Current graph-legibility repair](../../docs/product/lolla-mental-model-atlas-graph-legibility-repair-result-2026-07-17.md)
- [Current graph-legibility evidence](../../docs/evals/lolla-mental-model-atlas-graph-legibility-repair-evidence-v1.json)
- [Current neighborhood-navigation repair](../../docs/product/lolla-mental-model-atlas-neighborhood-navigation-repair-result-2026-07-17.md)
- [Current neighborhood-navigation evidence](../../docs/evals/lolla-mental-model-atlas-neighborhood-navigation-repair-evidence-v1.json)
- [Current design-system consolidation](../../docs/product/lolla-mental-model-atlas-design-system-consolidation-result-2026-07-16.md)
- [Current design-system evidence](../../docs/evals/lolla-mental-model-atlas-design-system-consolidation-evidence-v1.json)
- [Phase 1 result](../../docs/product/lolla-mental-model-atlas-phase1-visual-truth-tracer-bullet-result-2026-07-15.md)
- [Card-first truthfulness repair](../../docs/product/lolla-mental-model-atlas-card-first-truthfulness-repair-result-2026-07-16.md)
- [Current monochrome structure study](../../docs/product/lolla-mental-model-atlas-monochrome-structure-study-result-2026-07-16.md)
- [Current guided-entry founder-feedback repair](../../docs/product/lolla-mental-model-atlas-guided-entry-repair-result-2026-07-16.md)
- [Vibrant-editorial refinement](../../docs/product/lolla-mental-model-atlas-vibrant-editorial-refinement-result-2026-07-16.md)
- [Card-first evidence](../../docs/evals/lolla-mental-model-atlas-card-first-repair-evidence-v1.json)
- [Current monochrome structure evidence](../../docs/evals/lolla-mental-model-atlas-monochrome-structure-study-evidence-v1.json)
- [Current guided-entry evidence](../../docs/evals/lolla-mental-model-atlas-guided-entry-repair-evidence-v1.json)
- [Vibrant-editorial evidence](../../docs/evals/lolla-mental-model-atlas-vibrant-editorial-refinement-evidence-v1.json)
- [Renderer decision](../../docs/product/lolla-mental-model-atlas-phase1-renderer-decision-2026-07-15.md)
- [Evidence receipt](../../docs/evals/lolla-mental-model-atlas-phase1-evidence-v1.json)
- [Product PRD](../../docs/product/lolla-mental-model-atlas-and-teacher-prd-v1.md)
