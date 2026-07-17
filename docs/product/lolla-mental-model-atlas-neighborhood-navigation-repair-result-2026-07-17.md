# Mental Model Atlas Neighborhood Navigation Repair Result

Status: local founder-validation candidate; provider-free; unpublished

Date: 2026-07-17

Parent checkpoint: `02479cfe5eea1402e5e134bbd1c064a9d56e0bc1`

Implementation checkpoint: `7090c743b10ee657ff454e134be4c200192a2a4e`

Decision: `atlas_selection_rebuilds_exact_canonical_neighborhood`

## Executive result

Founder review correctly identified that the repaired graph still selected
connections only from the already-loaded 40-record Phase 1 fixture page. A
model such as Root Cause Analysis could therefore appear to have no useful
connections even though the canonical relationship graph contains fourteen.
The graph was visually coherent but exploration was not yet truthful.

Ordinary selection now uses a new sanitized navigation index containing all
222 canonical model identities and all 1,358 exact checked-in relationship
records. Selecting a model deterministically filters exact incoming and
outgoing records, constructs the current neighborhood page, and makes every
revealed neighbor selectable as the next center. No provider, ranking,
relationship inference, semantic repair, or score participates.

## What the interaction now means

- The unselected Atlas remains a 16-model orientation slice.
- Selecting a model replaces that slice with its exact incident neighborhood.
- Selecting a revealed neighbor rebuilds the map around that neighbor.
- A maximum of 40 exact relation records appears on one graph page.
- Larger neighborhoods expose Previous and Next controls and exact before,
  shown, after, eligible, and omitted counts.
- Relation-type filters operate on the current exact page; they do not change
  the underlying page custody.
- The URL preserves selected model and page so the state is reloadable.

The browser performs deterministic incident-edge filtering only. It does not
decide which connections are important or relevant and does not create a
relationship absent from `data/relationship_graph.json`.

## Source and package boundary

The additive `navigation-v1` package is separate from the frozen Phase 1
fixtures and manifest. Its deterministic builder verifies the same canonical
source hashes, strips source-only affinity and score fields, preserves every
relation's source JSON pointer, and emits:

- `neighborhood-index.json`: 222 models, 1,358 relations, 2,181,357 bytes,
  SHA-256 `565ccef599ecc018f3501c36febadb9468ecaaaab310598d0c6e467ffd33417f`;
- `manifest.json`: package custody and nonclaims, SHA-256
  `fcd2f994ea03221ceea31601c1e991e46750512154222bb5da536f866a24de62`.

The original Phase 1 projections, hub pages, model page, relation page,
manifest, screenshots, and historical evidence remain byte-unchanged.

## Layout and legibility

Neighborhood coordinates are generated deterministically from exact model
identity. The selected model is the hub and neighbors use a stable concentric
order. Up to twenty models retain nearby labels; denser pages reserve ordered
left and right label lanes and a central graph field. This prevents dense hubs
from reintroducing the label occlusion repaired in the preceding checkpoint.

Relationship kind and direction retain the existing grammar: solid ally,
dashed antagonist with a cross, double tension, target arrowhead, and pausable
source-to-target marker.

## Browser evidence

- Root Cause Analysis expanded to 14 exact connections and 13 visible models.
- Five Whys Method appeared even though it was outside the original 16-model
  orientation slice.
- Selecting Five Whys Method rebuilt the graph around seven exact connections
  and six visible models.
- Confirmation Bias exposed 233 exact connections through six pages.
- Confirmation Bias page 2 showed records 41–80, 40 edges, and 30 models.
- All 30 dense-page labels were in bounds with zero pairwise overlaps.
- Desktop and iPhone 14 checks had no horizontal overflow.
- Mobile retained the intentional list-first view with all 13 Root Cause
  Analysis neighborhood models and 14 relation rows.
- The Strict Mode double-effect path no longer aborts the shared index load.

## Verification

- Deterministic navigation builder tests: 3 passed.
- Focused navigation, projection, geometry, and Atlas tests: 19 passed.
- Atlas type check: passed.
- Complete Atlas suite: 55 passed across 12 files.
- Production build: passed; dependency audit: zero vulnerabilities.
- Complete repository suite: 5,015 passed, 93 subtests passed, with the one
  existing `datetime.utcnow()` deprecation warning.
- `git diff --check`: passed.
- Provider calls and provider cost: 0 and `$0.00`.
- Publication actions: none.

## Boundary and next decision

This repairs exploration of the checked-in canonical relationship graph. It
does not certify any relationship as true, important, relevant, useful, or
complete; approve publication rights; complete every model's long-form page;
prove learning value; connect Atlas to the live Lolla runtime; select a final
palette; authorize deployment; or authorize Teacher/Phase 2 work.

The next action remains founder use of the local candidate. The relevant test
is now whether traversing exact neighborhoods helps a person form a coherent
picture—not whether the graph merely contains more lines.
