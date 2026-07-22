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

The shared shell uses the founder-supplied lowercase `lolla` raster wordmark
from `public/brand/lolla-wordmark-original.png`. The repository copy preserves
the supplied source bytes. CSS owns only its clipped presentation and contrast
against the achromatic raised surface; it must not redraw, infer, or silently
replace the letterforms. The enclosing home link supplies the accessible name,
so the raster is decorative to assistive technology. The wordmark stands alone
in the header; do not place a `Mental Model Atlas` descriptor beneath it.

## Geometry

- Structural panels, cards, tables, disclosures, and navigation groups are
  square (`--radius-structure`).
- Buttons and form controls use the two-pixel control radius
  (`--radius-control`).
- Circles are reserved for graph nodes, numbered learning steps, and
  loading-node geometry.
- A full capsule radius is reserved for compact status labels and the
  off-canvas skip link.
- No other corner radius is part of the system.

## Lines

- One pixel separates or contains ordinary structure.
- Two pixels identify a current route/section or keyboard focus.
- A three-pixel inset identifies a selected record.
- Relationship kind is expressed by line form, not by color or importance
  weight: solid for ally, dashed for antagonist, double for tension. Public
  labels are owned by `src/relationPresentation.ts`.
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
- Before selection, the first viewport prioritizes search and named canonical
  model actions over relationship configuration or counts.
- After selection, connection counts are filter controls in the selection
  panel. The same panel owns one progressively disclosed line-and-direction
  grammar; do not repeat a second visible legend elsewhere.
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

At representative `1280x720` and `390x844` viewports, the first screen must
contain a named canonical model action. A search exact match must be directly
selectable, and selection must reveal the model name, summary, and available
full-page action without requiring scroll. The compact route is list-first;
the hidden visual renderer must not leave a dead presentation control.

## Allowed exceptions

Graph nodes, step markers, and the brand mark may be circular. Relationship
lines may vary by pattern. Reading, standard, wide, and canvas shells may use
different widths. Monospaced metadata may be denser than teaching prose.
Every other exception requires an explicit addition to this contract.
