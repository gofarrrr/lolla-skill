# Mental Model Atlas Graph Legibility Repair Result

Status: local founder-validation candidate; provider-free; unpublished

Date: 2026-07-17

Parent checkpoint: `d42785198345c0742660e4728580f465e76225f7`

Implementation checkpoint: `bba6f3f168870cacd71127da81c5f048d553fe97`

Decision: `atlas_graph_full_field_directional_grammar_repaired`

## Executive result

Founder review found that the consolidated Atlas shell was coherent while the
interactive graph itself was materially broken. Model nodes rendered as large
opaque disks over their labels, selected-model camera movement pushed other
models outside the viewport, relation types looked alike, arrowheads were
hidden beneath target nodes, the graph offered no visible source-to-target
movement, and two legends described the line system differently.

The primary cause was a renderer/design-system contract mismatch. The SVG
emitted `node-aura`, `node-core`, `node-label`, and `marker-*`, while the active
design system styled `graph-node-aura`, `graph-node-core`,
`graph-node-label`, and `graph-marker`. It also expected a `data-relation`
attribute the renderer never emitted. Browser defaults therefore painted the
large aura circles black and relation-specific selectors never matched.

The contract is repaired rather than cosmetically patched. The graph now keeps
the complete loaded field visible, separates small nodes from collision-aware
labels, uses one canonical relation key, distinguishes all three line types,
shows arrowheads outside target nodes, and animates a marker along the authored
source-to-target path. The global motion control and reduced-motion preference
pause that movement.

## Graph grammar

The visible relationship language is now:

- ally: one solid line;
- antagonist: a dashed line with a midpoint cross;
- tension: a double line;
- direction: an arrowhead plus a traveling marker moving from source to target.

Relation type and direction remain separate. Neither line weight, node size,
movement, nor position is presented as importance, truth, relevance, quality,
or mastery.

The relationship controls above the map are the only visible legend. The idle
selection panel no longer repeats a second key. The controls, SVG edges, Canvas
comparison, model-page relation language, and exact relation page now share the
same ally/antagonist/tension distinction.

## Model and viewport repair

All loaded models remain in the original full-field coordinate system after a
model or relation is selected. Selection changes emphasis but no longer pans or
zooms unrelated models beyond the graph boundary.

Each model now uses:

- a 10-unit outlined aura rather than a 19-unit opaque disk;
- a 3.25-unit identity core;
- a modest selected-state enlargement;
- a separately bounded label connected by a subtle leader;
- deterministic collision-aware label placement constrained to the graph;
- 50% rather than near-invisible opacity for unrelated models.

The ordinary 16-model projection deterministically produces 16 in-bounds,
non-overlapping labels. A regression test rejects label collision or escape
from the 1,000 by 700 graph field.

The Atlas introduction was also compressed so the useful controls and graph
begin earlier. This does not change Atlas copy, source projection, graph
coordinates, model identity, relation identity, or relationship meaning.

## Renderer parity

The default SVG renderer and hidden review-only Canvas comparison now share:

- achromatic nodes and label boxes;
- full-field identity camera;
- collision-aware label placement;
- solid ally, dashed antagonist, and double tension lines;
- arrow direction;
- antagonist cross;
- moving directional marker;
- selected, hovered, related, and dimmed treatment;
- pause and reduced-motion behavior.

Canvas remains a comparison renderer, not an ordinary visitor control. The
text Atlas remains the keyboard and non-canvas equivalent.

## Browser evidence

At a 1,440 by 1,000 viewport:

- default Atlas rendered 16 models and 16 labels;
- selected Critical Thinking rendered all 16 models without camera clipping;
- all 8 focused relationships carried `ally`, `antagonist`, or `tension` data;
- all 8 focused relationships rendered a directional flow marker;
- flow-marker coordinates changed after 800 milliseconds while motion ran;
- the same coordinates remained stable across 800 milliseconds after Pause;
- the relationship controls showed solid, dashed, and double line forms;
- no horizontal overflow or browser error was present.

At an iPhone 14 viewport, the visual graph remained intentionally suppressed,
the touch-friendly list-first entry remained visible, and horizontal overflow
remained absent.

## Verification

- New graph-geometry and SVG-grammar tests: 2 passed.
- Focused design-system and Atlas interaction slice: 15 passed.
- Complete Atlas application suite: 50 passed across 11 files.
- React/TypeScript check: passed.
- Production build: passed.
- Complete repository suite: 5,012 passed, 93 subtests passed, with the one
  existing `datetime.utcnow()` deprecation warning.
- `git diff --check`: passed.
- Provider calls and provider cost: 0 and `$0.00`.
- Publication actions: none.

## Boundary and next decision

This repairs the reported interaction and legibility defects. It does not
validate the frozen coordinate layout as the best information architecture,
complete the full model corpus, approve a color system, clear publication
rights, establish native screen-reader acceptance, prove learning usefulness,
connect the Atlas to the live Lolla runtime, authorize deployment, or authorize
Phase 2.

The next action is founder review of the repaired interactive Atlas. Further
layout or aesthetic work should begin only from specific use friction observed
in this coherent graph, not from the superseded broken rendering.
