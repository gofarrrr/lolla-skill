# Mental Model Atlas Design-System Consolidation Result

Status: local founder-validation candidate; provider-free; unpublished

Date: 2026-07-16

Parent checkpoint: `319d5c779e507a4cd28505616db1c89de23fa88e`

Decision: `atlas_design_system_consolidated_on_precise_editorial_cartography`

## Executive result

The Atlas now has one explicit visual contract and one active stylesheet
entrypoint. The previous implementation accumulated a 4,486-line monolithic
stylesheet and a 1,001-line override sheet whose competing rules produced the
inconsistent corners, borders, spacing, typography, relation-page contrast,
and route-specific exceptions observed during founder review. Both legacy
stylesheets have been removed from the active application.

The replacement is a token-driven, route-modular system called **precise
editorial cartography**. It is deliberately achromatic. Hierarchy comes from
typography, space, line weight, relationship pattern, direction, density, and
state—not from arbitrary color, rounded-card vocabulary, or accumulated
overrides.

This is a visual-system consolidation, not a new product claim. It changes no
source card, model identity, relationship identity, relationship direction,
curation record, graph meaning, missingness state, projection artifact, or
runtime connection.

## Binding rules

The complete contract is
[`apps/mental-model-atlas/DESIGN_SYSTEM.md`](../../apps/mental-model-atlas/DESIGN_SYSTEM.md).
Its enforced rules include:

- square structural surfaces;
- a two-pixel radius only for controls;
- circles only for graph nodes, step markers, loading geometry, and the brand;
- capsules only for compact status labels and the off-canvas skip link;
- one-pixel ordinary structure, two-pixel current/focus structure, and a
  three-pixel selected-record inset;
- Familjen Grotesk for identity, IBM Plex Sans for reading and interaction, and
  IBM Plex Mono for metadata;
- a four-pixel spacing scale;
- reading, standard, wide, and canvas shells with named width tokens;
- relationship kind encoded through solid, dashed, or double/dotted line form,
  independently from direction;
- motion limited to 120, 180, and 320 milliseconds and suppressed under
  reduced-motion preference;
- exactly three global viewport transitions: 700, 900, and 1,080 pixels;
- one visual language for loading, empty, completed-zero, unavailable, failed,
  selected, disabled, focus-visible, and custody states.

New visual exceptions must first be added to this contract. They may not be
introduced as a route-local override.

## Implementation shape

The application imports only `src/design-system/index.css`, which composes:

1. `tokens.css` — color, type, spacing, line, radius, motion, and shell tokens;
2. `base.css` — reset, document defaults, typography, controls, focus, and
   forced-color behavior;
3. `shell.css` — application frame, route navigation, common headers, and
   structural containers;
4. `atlas.css` — graph workspace, selection panels, tables, legends, and the
   accessible Atlas alternative;
5. `library.css` — Library search, counts, cards, and completed-zero state;
6. `model.css` — first viewport, guided source reader, practice, connection
   explorer, and technical-custody disclosure;
7. `relation.css` — relation identity, facts, source narrative, and boundary;
8. `states.css` — Learn, loading, missing, unavailable, failed, and custody;
9. `responsive.css` — the three shared viewport transitions.

The deleted `src/styles.css` and `src/restraint.css` are not compatibility
layers. No source import remains and contract tests reject their return.

## Route and state repair

The consolidation covers every public Phase 1 route:

- `/atlas` and its model, relation, fixture, and renderer states;
- `/models` including search and completed-zero results;
- `/models/abstraction` including guided/full source, practice, relationship
  tabs, selected records, boundaries, and collapsed technical custody;
- `/relations/abstraction__first-principles-thinking__ally`;
- `/learn`;
- route loading, data failure, unavailable-page, and missing-page states.

The relation page no longer carries a dark route-specific visual world. The
Library cards share one grid rhythm. The Atlas selection panel, accessible
table/list, graph controls, and mobile list-first alternative now use the same
components and line hierarchy. The model page preserves the prior guided-entry
repair while placing source, learning, relationship, and custody material in
the shared geometry.

## Browser review

The production build was reviewed at 1,440 by 1,000 pixels and at a 390 by 844
pixel mobile viewport. The review exercised Atlas model selection, Text Atlas,
Library search and completed-zero recovery, the complete Abstraction guided and
full-source paths, relationship-kind selection, the exact relation page, Learn,
keyboard focus, reduced motion, and mobile navigation.

Observed outcomes:

- no horizontal overflow on the reviewed routes;
- no browser console errors;
- visible three-pixel keyboard focus treatment;
- a light, readable relation page with visible title and square structure;
- equal-height Library cards;
- list-first Atlas behavior when the graph is suppressed on compact screens;
- complete source chapters remain reachable in explicit full-source mode;
- long source and record lists use `content-visibility` to avoid eagerly
  rendering off-screen detail;
- the application header remains opaque while content scrolls beneath it.

This was a browser and computed-style review, not a native screen-reader study,
publication-rights review, or real-user usefulness test.

## Verification

- Design-system contract tests: 8 passed.
- Complete Atlas application tests: 48 passed across 9 files.
- React/TypeScript check: passed.
- Production build: passed.
- Phase 1 and card-first projection validators: passed; 12 and 1 artifacts
  reproduced respectively with zero provider calls.
- Focused repository projection tests: 31 passed.
- Complete repository suite: 5,012 passed and all 93 subtests passed, with the
  one existing `datetime.utcnow()` deprecation warning.
- `git diff --check`: passed.
- Provider calls and provider cost: 0 and `$0.00`.
- Publication actions: none.

## Boundary and next decision

This result establishes a coherent implementation baseline that can be judged
without the old cascade obscuring it. It does not establish final visual
approval, select a future palette, complete the other 232 model pages, approve
source publication, prove native assistive-technology behavior, prove learning
value, connect Teacher to the live Lolla runtime, or authorize deployment or
Phase 2.

The next founder decision is visual and product validation of the consolidated
achromatic baseline. If accepted, later color work should begin from semantic
accent roles added to the token contract—not from page-specific fills or border
decoration.
