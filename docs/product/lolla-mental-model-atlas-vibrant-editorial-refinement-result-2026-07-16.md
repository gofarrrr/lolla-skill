# Mental Model Atlas Vibrant Editorial Refinement Result

Status: local founder validation ready; unpublished

Date: 2026-07-16

Decision:

`vibrant_editorial_abstraction_tracer_ready_for_founder_validation`

## Executive result

The Abstraction tracer now has a disciplined, distinctive visual system rather
than the previous mixture of warm brown, orange, teal, violet, and generic
card styling. A cool-gray instrument-paper field keeps the page quiet. Dark
vibrant blue supplies structure and typographic authority. Teal, lime, and
purple appear as strong functional signals with fixed jobs.

The signature element is a four-stop page signal path:

1. **Learn the source** — lime;
2. **Put it to work** — teal;
3. **Read the relations** — purple;
4. **Keep judging** — dark blue.

These are real anchors, not decoration. Each lands below the sticky site
header on desktop and mobile. The existing five-step source reader remains
collapsed to one chapter at a time, keeps the current step visible, and retains
its full-source inspection mode.

Provider calls: 0.

Provider cost: `$0.00`.

## Art direction and token roles

The implemented direction is **vibrant editorial field guide**. The primary
tokens are:

| Role | Token | Use |
| --- | --- | --- |
| Structural ink | `#060761` | headings, borders, graph direction, focus, header |
| Primary action | `#41FFA7` | actions and practical-use signal |
| Primary background signal | `#C4FF4D` | source entry, current step, current record |
| Secondary layer signal | `#BA8CFF` | derived/relationship transition |
| Quiet field | `#E7E8E4` | instrument-paper page background |
| Surface | `#F7F7F2` | reading and inspection surfaces |
| Error | `#A5163A` | failure only; never a relationship category |

The active route layer contains none of the superseded brown `#A4471E`, muted
teal `#1D6F67`, violet `#6E56CF`, or orange `#C65A1E`. The palette is not a set
of interchangeable decoration colors. Each accent has a primary product role;
ordinary interaction feedback may borrow lime for current state and teal for a
user action, but relationship categories never acquire separate hues.

Familjen Grotesk carries model identity and large section titles. IBM Plex Sans
carries human reading. IBM Plex Mono carries evidence, direction, counts, and
small structural labels. The fonts are packaged locally; the route does not
depend on Inter, Roboto, Arial, or a network font service.

## Relationship meaning remains truthful

All 12 exact Abstraction-incident relationship records remain in the interface:
five authored outward and seven authored inward. Parallel records remain
separate. The UI still exposes seven allies, four tensions, and one antagonist.

The refinement deliberately does **not** assign the founder palette to
relationship categories. Bright colors are page-layer and current-selection
signals. Relationship meaning is repeated through words and dark-blue line
form:

- ally: written label plus a solid line;
- tension: written label plus a dotted line;
- antagonist: written label plus a dashed line and cross.

Source/target labels and arrows preserve authored direction. A grayscale
browser capture confirms that the three types remain distinguishable without
color. The interface continues to state that these records are not scores,
recommendations, confidence, relevance, or proof that a model applies.

## Navigation and responsive behavior

The major signal-path anchors now use explicit scroll margins. At 1440 pixels,
the relationship section settles 112 pixels below the 80-pixel sticky header.
At 390 pixels it settles 160 pixels below the 137-pixel mobile header. The
section title and orientation copy remain visible after the jump.

The guided reader continues to show one chapter at a time. On the 390-pixel
Step 3 state, the site header occupies 0–137 pixels, the sticky chapter rail
occupies approximately 144–294 pixels, and the active Step 3 control occupies
193–241 pixels. The active chapter begins below that rail. The active step is
automatically brought into the horizontally bounded chapter rail.
Previous/next and direct-step controls remain keyboard operable.

Browser checks found:

- no document-level horizontal overflow at 1,440, 390, or 320 pixels;
- the `Abstraction` H1 remains intact at 320 pixels;
- every visible button, link, tab, and disclosure target at 320 pixels is at
  least 44 by 44 pixels;
- the mobile motion control keeps a visible Pause/Resume label and changes both
  its icon and accessible name with state;
- the deep exact-relationship link and skip link are each 44 pixels high;
- the four signal-path actions stack to full width at 320 pixels;
- relation tabs retain roving arrow-key focus and correct `aria-selected` state;
- all 12 relationship controls remain in the DOM while only the chosen group
  is displayed.

## Interaction and failure states

The route includes deliberate default, hover, pressed, focus-visible, disabled,
and selected states. Reduced-motion preference sets the route to paused motion,
disables the motion control, removes smooth scrolling, and reduces transition
durations to the clean fallback.

The source-artifact failure state is branded but unambiguous. It says that the
artifact could not be verified, does not convert failure into a valid zero, and
offers **Reload the source page** and **Browse the model library**. A real
browser check aborted the source artifact, observed the failure state, restored
the route, used Reload, and recovered the canonical Abstraction page with all
12 relation records.

Unavailable model pages, projection loading, graph-renderer failure, empty
searches, and disabled controls remain separate states. No silent failure or
default browser error page was introduced.

## Accessibility and contrast

The principal contrast pairs reproduce as:

- dark blue on gray: `14.09:1`;
- dark blue on teal: `13.29:1`;
- dark blue on lime: `14.67:1`;
- dark blue on purple: `6.84:1`;
- white on dark blue: `17.34:1`;
- muted body text on gray: `7.14:1`;
- quiet text on gray: `4.76:1`;
- error text on the error surface: `6.61:1`.

The route keeps semantic HTML, visible focus, keyboard relation tabs, explicit
pause/reduced-motion behavior, non-color relationship grammar, forced-colors
line fallbacks, and print expansion of the source. Inactive header controls now
receive a white focus outline plus a lime inner keyline against dark blue. The
solid, dotted, dashed, and cross markers were inspected as rendered pseudo-
elements as well as in grayscale. Native VoiceOver, NVDA, and JAWS testing
remains open; the browser and structural checks are not a claim of native
screen-reader certification.

## Verification and independent acceptance

Three independent, read-only re-audits now accept the final state with no
actionable blockers:

- the frontend/code audit verified focus visibility, 44-pixel targets,
  Pause/Resume semantics, reduced-motion behavior, disabled controls, and exact
  mobile anchor/reader geometry;
- the graph audit verified all 12 exact records, authored direction, parallel
  records, normal and forced-color line grammar, the antagonist cross, and the
  settled evidence hashes;
- the visual/reference audit verified palette discipline, responsive
  containment, the mobile control language, and the final screenshots.

Mechanical verification is also green:

- frontend tests: 36 passed;
- production TypeScript/Vite build: passed; the `ModelPage` chunk is 38.58 kB
  raw and 11.35 kB gzip;
- focused PRD/evidence tests: 5 passed;
- complete repository suite: 5,010 passed and all 93 subtests passed;
- known warning: one existing `datetime.utcnow()` deprecation warning;
- package audit: zero vulnerabilities;
- Stage 0 public-handoff validator: valid, including 84 local links;
- JSON parsing, `git diff --check`, and Git object-integrity checks: passed.

The Git integrity check reported six harmless dangling blobs from local edit
cycles. They are not referenced by the index, reviewed commits, or branch
history and do not indicate corruption.

## Evidence

The new visual packet is
[`lolla-mental-model-atlas-vibrant-editorial-refinement-2026-07-16`](evidence/lolla-mental-model-atlas-vibrant-editorial-refinement-2026-07-16/README.md).
It contains desktop hero, guided-source, practice, ally, tension, antagonist,
grayscale, mobile, 320-pixel, and failure-state captures. The machine-readable
receipt is
[`lolla-mental-model-atlas-vibrant-editorial-refinement-evidence-v1.json`](../evals/lolla-mental-model-atlas-vibrant-editorial-refinement-evidence-v1.json).

The former card-first, guided-reader, and relational-aesthetic packets remain
additive historical checkpoints. They are not relabeled as current screenshots.

## Product boundary

This is still one local Abstraction tracer. It does not redesign the global
`/atlas` SVG/Canvas renderer, create the other 221 full model pages, create
Teacher journeys, connect the Atlas to the Lolla runtime or Observatory, clear
source rights, prove comprehension, or prove real-user usefulness.

The global graph still uses the earlier Phase 1 language. Following **Explore
the full graph** therefore crosses from the refined model-page tracer into an
older visual system. That renderer-unification question remains a separate
founder decision after this route is accepted; it is not hidden inside this
refinement.

## Exact founder decision

Run the local Atlas app and review `/models/abstraction`, then decide whether
this palette discipline, typography, navigation, and relation grammar feel
like the Lolla direction. Acceptance validates this one visual tracer. It does
not authorize publication or the next product phase.
