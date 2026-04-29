# TODOS

Design and product debt tracked here. Each entry: what, why, pros, cons, depends on.

---

## Observatory DESIGN.md

**What:** Formalize the Observatory's implicit design system into a `DESIGN.md` at the repo root.

**Why:** Today the system lives in code (`_SHARED_PANEL_CSS`, `_render_scaffold`, the `/usage` voice, the post-2026-04-29 telemetry framing) and in convention. The next contributor adding a panel re-derives all of it from source. A short `DESIGN.md` codifies it once.

**Pros:** Reduces drift on future panels; codifies the "telemetry-as-mirror, not as debug log" framing; junior-readable handover.

**Cons:** ~30 min of doc writing; risks staling if not maintained alongside CSS edits.

**Context:** Captured during the 2026-04-29 plan-design-review on the audit-panels gardening pass. The implicit system covers: scaffold structure, run-header anatomy, headline-summary voice (system-as-agent, numbers-up-front), empty-state warmth rules, FAB pattern, the `/audit/*` vs `/usage` vs `/` cleavage, AI-slop guardrails (no card grids, no centered hero, no emoji, no purple gradients, no carousels).

**Depends on:** Gardening pass shipping first so DESIGN.md describes settled state.
