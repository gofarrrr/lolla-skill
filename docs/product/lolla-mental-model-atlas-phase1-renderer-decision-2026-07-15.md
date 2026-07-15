# Mental Model Atlas Phase 1 Renderer Decision

Status: local decision for founder review; no public deployment authorization

Date: 2026-07-15

## Decision

Use the source-controlled SVG editorial renderer as the Phase 1 default. Keep
the Canvas 2D implementation as a runnable same-projection comparison and
failure-control. Do not install Sigma.js or Cytoscape.js in this bounded slice;
reopen that comparison before the complete 222-model phase.

This is not a claim that SVG is the final full-corpus renderer. It is the
smallest renderer that met the actual Phase 1 job: 16 ordinary nodes, no idle
edges, a maximum of 40 focused exact relations, persistent selection,
independent hover, a stable selection camera, line semantics, keyboard focus,
and a complete DOM equivalent.

## Same-data candidates

### SVG editorial — selected default

Evidence:

- consumes the same validated `lolla.atlas_projection.v1` data and frozen
  coordinates as Canvas;
- keeps nodes and exact directed relations as inspectable DOM objects;
- supports visible keyboard focus and `aria-pressed` selected state;
- renders parallel ally/tension records and separately authored reverse edges;
- moves a stable camera group without changing source coordinates;
- preserves the synchronized semantic list and directed relation table;
- production renderer chunk: 3,731 bytes raw / 1,579 bytes gzip in the recorded
  pre-closeout build.

Limitation: SVG is proven only at the bounded Phase 1 density. It may not be the
right renderer for 222 simultaneous node positions or future interaction
volume.

### Canvas 2D — retained comparison, rejected as default

Evidence:

- consumes the same projection and coordinate hash;
- reproduces selection, hover, focused relations, and the selection camera;
- provides a useful control for a non-DOM visual renderer;
- production renderer chunk: 3,787 bytes raw / 1,841 bytes gzip;
- forced `getContext()` failure leaves the complete semantic list and relation
  table available.

Reason not selected: hit testing, focus semantics, and accessibility depend on
parallel handwritten logic. The visual renderer itself is not keyboard
content. That is acceptable as a comparison, but unnecessarily weak as the
default for the bounded slice.

### Sigma.js and Cytoscape.js — deferred, not rejected universally

The prospective plan recommended Sigma.js as a likely scalable baseline and
Cytoscape.js as a semantic-interaction control. Phase 1 did not install either:

- the bounded scene did not require a third-party graph engine;
- installing two engines before the projection and interaction truth gates
  passed would freeze extra dependencies prematurely;
- the SVG/Canvas boundary already proves that renderers can be replaced without
  changing public projection identity or route state.

This is a deliberate narrowing of the prospective renderer spike. Phase 2 may
not infer that SVG has already earned the complete-corpus job. A 222-model
comparison must recheck bundle size, focus semantics, keyboard/non-canvas
equivalence, dense labels, pan/zoom continuity, frame budget, and failure
behavior under the same source projection.

## Performance evidence

Recorded profile: Headless Chrome 145.0.7632.6, macOS-reported browser
platform, 1920 × 1200, DPR 1, local production Vite preview, unthrottled
localhost.

- new-session Atlas useful mark: 586.8 ms;
- same-session reload useful mark: 369.8 ms;
- selection two-frame p95 across ten samples: 127.9 ms;
- hover one-frame p95 across ten samples: 18.3 ms;
- 300-frame sample: p50 16.7 ms, p95 18.3 ms, worst 20.6 ms;
- frames above 20 ms: 1; above 50 ms: 0;
- recorded first-route transfer: 94,347 bytes.

These measurements pass the Phase 1 acknowledgement/settling bounds in the
recorded local profile. They are not a mobile-device benchmark, public-network
benchmark, or evidence for the complete corpus.

The machine-readable receipt and screenshot hashes are in
[`lolla-mental-model-atlas-phase1-evidence-v1.json`](../evals/lolla-mental-model-atlas-phase1-evidence-v1.json).

## Gate still open

The founder has not yet accepted the composition, camera, motion, or continuity
bar. A native VoiceOver/NVDA review is also pending. Publication rights remain
unknown. Therefore this renderer decision is local implementation evidence,
not product publication or Phase 2 authorization.
