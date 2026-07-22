# Mental Model Atlas first-viewport repair result — 2026-07-17

Status: implemented and verified locally, provider-free, pending founder
re-review.

Decision: `bounded_first_viewport_interaction_repair_implemented`

## Question and result

The bounded question was whether a first-time visitor could choose a named
canonical model, search, and see the selection reward without scrolling at a
common laptop or mobile viewport.

The repaired local candidate passes that structural browser gate:

- at `1280x720`, search, four named canonical model actions, and the graph are
  visible without scrolling;
- selecting Abstraction leaves scroll position at zero and shows its name,
  summary, and `Read complete model` action completely within the viewport;
- at `390x844`, four named model actions are visible without scrolling;
- the mobile selected state shows Abstraction, its summary, and the full-page
  action by pixel 842;
- searching for `abstraction` exposes a direct exact-match result, and Enter
  selects it as `?model=abstraction` rather than leaving the result below the
  fold;
- the Library replaces a non-actionable availability count with the explicit
  `Read Abstraction` action;
- all four Abstraction chapter actions are fully visible by pixel 653 at
  `1280x720`.

These are local browser geometry and interaction results, not real-user
usefulness evidence.

## Product changes

- The Atlas hero is shorter and task-led.
- Search results are derived directly from the verified loaded projection; no
  new state store, inference, fuzzy repair, or provider is involved.
- The first four records in the current deterministic projection become named
  start actions. Their order is projection order, not importance or ranking.
- Selecting a search result clears the query so a text filter cannot silently
  hide the selected model's neighborhood.
- The selected panel precedes the graph in document order while CSS preserves
  the desktop graph/panel layout.
- Relationship counts are buttons that apply exact type filters. The line and
  direction grammar is available through a compact disclosure after selection.
- Idle counts and filter-match metrics were removed from the primary path.
- Mobile hides the unavailable visual renderer and presentation switch, then
  reaches the named list directly after the compact action area.
- The Library entry is compact and points to the one complete reading page.
- The Abstraction hero is shorter while preserving all orientation cues and
  chapter actions.
- The shared shell uses the exact founder-supplied lowercase `lolla` wordmark;
  its original RGB bytes are preserved under `public/brand/`, while CSS owns
  only the clipped achromatic presentation. The redundant `Mental Model Atlas`
  descriptor beneath the wordmark is removed.

## Preserved boundaries

The repair does not change:

- the 222 canonical model identities or 1,358 checked-in relations;
- exact relation direction, kind, paging, or graph-survival behavior;
- the 16-model ordinary orientation source;
- complete-card versus summary-only availability;
- source hashes, source prose, operational curation, or missingness;
- provider, runtime, Observatory, Decision Work, or Teacher connections;
- deployment, Phase 2, publication rights, or product claims.

## Evidence classification

- React tests: local mechanical interaction evidence.
- TypeScript/build checks: local structural evidence.
- Browser screenshots and viewport coordinates: local visual-geometry evidence.
- Human value, comprehension, visual preference, native screen-reader behavior,
  rights, and usefulness: still open.

The browser captures live in `artifacts/atlas-human-review/`. The `after-*`
files are the repaired candidate; the earlier files preserve the pre-repair
comparison from the same session. `after-logo-*` captures verify the preserved
wordmark in the shared desktop and mobile shell.

## Local verification

The final checked-in-safe verification passed on 2026-07-17:

- all three Atlas projection validators reported `status: valid`, with 222
  canonical models, 1,358 exact relations, zero provider calls, and `$0.00`
  provider cost;
- the focused projection, card-first, and navigation suites passed 35 tests;
- the Atlas application passed 62 Vitest tests across 13 files;
- the TypeScript check and production Vite build passed, transforming 61
  modules;
- `npm audit --audit-level=moderate` reported zero vulnerabilities;
- the complete repository suite passed 5,016 tests and 93 subtests in 193.45
  seconds, with the one pre-existing `datetime.utcnow()` deprecation warning;
- `git diff --check` passed.

These checks verify deterministic integrity, interaction mechanics, build
health, and local geometry. They do not convert the open human evidence gates
into passes.

## Next decision

Re-review the repaired candidate as a human with mouse, keyboard, reduced
motion, and a native screen reader. A failure should authorize only a named
bounded repair. Passing this local gate must not imply deployment, Phase 2,
Teacher revival, rights clearance, or real-user usefulness.
