# Mental Model Atlas design system

Status: binding implementation contract for the local Atlas candidate.

The only active stylesheet entrypoint is `src/design-system/index.css`. It
imports the route modules in a fixed order; the superseded monolithic and
restraint override stylesheets have been removed. New visual work belongs in
the appropriate module and must extend this contract before introducing a new
exception.

## Direction

The Atlas uses **precise editorial cartography**: a human-readable field guide
whose hierarchy comes from type, space, rules, direction, and controlled
density. It is not a rounded SaaS dashboard, a neo-brutalist poster, a
glassmorphic surface, or a gamified learning product.

The current candidate is deliberately achromatic. Color may return only after
the structural contract is stable and reviewed.

## Geometry

- Structural panels, cards, tables, disclosures, and navigation groups are
  square (`--radius-structure`).
- Buttons and form controls use the two-pixel control radius
  (`--radius-control`).
- Circles are reserved for graph nodes, numbered learning steps, loading-node
  geometry, and the brand mark.
- A full capsule radius is reserved for compact status labels and the
  off-canvas skip link.
- No other corner radius is part of the system.

## Lines

- One pixel separates or contains ordinary structure.
- Two pixels identify a current route/section or keyboard focus.
- A three-pixel inset identifies a selected record.
- Relationship kind is expressed by line form, not by color or importance
  weight: solid for ally, dashed for antagonist, double/dotted for tension.
- Direction remains separate from relationship kind.

## Atlas graph grammar

- The unselected map is the bounded 16-model orientation slice. Selecting a
  model replaces that slice with the current exact incident-neighborhood page;
  selecting any revealed neighbor rebuilds around that model.
- Every model and edge on the current page remains in view. High-fan-in
  neighborhoods use exact 40-record pages and disclose all omitted records.
- Model identity uses a small outlined node and a separately bounded label.
  Labels must remain inside the graph and must not collide with one another.
  Dense pages reserve two ordered label lanes rather than allowing overlap.
- The relationship controls are the single visible legend. Do not repeat a
  second key in the selection panel.
- Every visible edge carries its exact relation type, a source-to-target
  arrowhead, and a traveling directional marker. Motion pauses through the
  global control and under reduced-motion preference.
- SVG and Canvas comparison renderers use the same achromatic node, label,
  relation-type, direction, selection, and motion grammar.

## Typography

- Familjen Grotesk: page and section identity.
- IBM Plex Sans: body, explanation, and interaction.
- IBM Plex Mono: labels, stable IDs, source metadata, indexes, and counts.
- Serif and system-default display voices are not part of the active product.

## Space and shells

Spacing follows a four-pixel scale. Component internals use fixed tokens;
responsive `clamp()` values are limited to page, hero, and major-section
boundaries.

- Reading shell: source and long-form explanation.
- Standard shell: Library, Learn, relation facts, failure, and boundaries.
- Wide shell: model and relationship workspaces.
- Canvas shell: the Atlas graph.

## Material and motion

Document-flow surfaces are flat. Shadows are permitted only for a genuinely
floating overlay and must use the single overlay token. Motion communicates
selection, state, or graph movement; it does not run perpetually for decoration.
The system uses 120, 180, and 320 millisecond durations and preserves reduced
motion.

## State contract

Every visitor-facing path must present loading, empty, missing, unavailable,
failed, selected, focus-visible, disabled, and reduced-motion states in this
same language. Missing, failed, and completed-zero remain semantically
different even when their geometry is shared.

## Responsive contract

Only three viewport breakpoints are active:

- compact: 700px and below;
- medium: 900px and below;
- wide transition: 1080px and below.

Component-specific layout changes should prefer container-aware layout before
adding another global breakpoint.

## Allowed exceptions

Graph nodes, step markers, and the brand mark may be circular. Relationship
lines may vary by pattern. Reading, standard, wide, and canvas shells may use
different widths. Monospaced metadata may be denser than teaching prose.
Every other exception requires an explicit addition to this contract.
