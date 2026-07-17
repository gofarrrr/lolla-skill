# Mental Model Atlas Monochrome Structure Study Plan

Status: implementation complete; local founder validation pending; provider-free; unpublished

Date: 2026-07-16

Parent checkpoint: `82313ff2c571503a13ab6a719e8f29450bec654f`

## Why this study exists

The first restraint pass reduced large flat color fields but replaced them with
colored edge rules. That still made color carry an arbitrary visual burden and
left the system looking transitional. The founder rejected that direction.

This study therefore removes chromatic color from the complete visitor-facing
Atlas layer. It asks a more basic question before any palette is reconsidered:

> Can hierarchy, relationship meaning, navigation, state, and movement feel
> coherent when the interface is allowed to use only typography, spacing,
> achromatic fill, rule weight, line form, and direction?

## Falsifier

The study fails if any of the following remain:

- a chromatic literal or visible inherited chromatic state;
- a line whose only purpose is to add an accent;
- relationship meaning that depends on hue;
- selected, disabled, hover, focus, loading, or failure states that escape the
  monochrome system;
- a first viewport dominated by a title before useful orientation appears;
- repository or evaluation vocabulary in the primary visitor journey;
- loss, merging, reranking, or reinterpretation of source or relationship
  records.

## Structural grammar

- hairlines separate related information;
- dark rules mark major boundaries;
- solid, dotted, and dashed-with-cross lines distinguish ally, tension, and
  antagonist relationships;
- arrows preserve authored direction;
- selected state uses weight, fill, or an inset rule;
- hover and focus reveal an existing boundary rather than adding decoration;
- motion is limited to navigation underlines, graph camera/state transitions,
  and other structural feedback;
- reduced-motion preference disables nonessential movement cleanly.

## Scope

Allowed:

- the shared Atlas, Library, and model-page visual layer;
- visitor-facing copy needed to make the monochrome contract truthful;
- the previously implemented visitor-first information hierarchy;
- browser evidence and provider-free regression tests;
- local cold-start documentation.

Forbidden:

- choosing or proposing the future brand palette;
- changing source Markdown or generated source bytes;
- changing model or relationship identity, type, direction, or multiplicity;
- provider calls, deployment, publication, rights clearance, or usefulness
  claims;
- Teacher journey generation, runtime, Observatory, Decision Work,
  conversation understanding, R4, or R5.

## Verification

- every literal in the new visual layer is achromatic;
- browser computed styles expose no visible chromatic state on Atlas, Library,
  or the Abstraction model page;
- desktop review at 1,440 by 900;
- mobile review at 390 by 844 and narrow-width target checks;
- graph selection, exact line grammar, model-page relationship tabs, anchor
  navigation, full-article disclosure, and reduced-motion behavior;
- complete Atlas tests and production build;
- complete repository suite before local handoff;
- no provider transport and no publication action.

## Decision boundary

Founder acceptance would approve the monochrome structural grammar as a base
for a separate color study. It would not approve a final visual brand, public
release, Phase 2, Teacher journeys, full-corpus content, source rights,
screen-reader certification, or real-user usefulness.
