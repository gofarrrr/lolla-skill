# Extraction Contract — PR Roadmap

**Authored:** 2026-04-22
**Last updated:** 2026-04-23 (post PR #1 learnings absorbed)
**Scope:** `lolla-skill` Step 2 (`scripts/run_extract.py`). NOT system_b.

## Why this document exists

The extraction contract work is a multi-PR effort. This roadmap exists so the sequence survives context loss. If a future session or new developer asks "what's next after PR #X?" the answer lives here, not in conversation memory.

Each PR is a ship-or-stop measurement event with its own acceptance gate. If a PR fails its gate, the plan pauses at that point — not every PR is predetermined to land.

This document is the **handover contract**. It must be sufficient for a cold-start session to understand: the system state, what we're trying to improve, what's done, what's next, what "good" looks like for each remaining PR, and the methodology discipline that keeps measurements honest.

## Supporting docs (READ FIRST for any cold start)

- `research/extraction-contract-observations-2026-04-22.md` — normative spec for each field (types, rules, rationale). Still the spec; what changed is how we measure it.
- `research/llm-decomposition-handover.md` — Cycle-1 context and why extraction-front was deferred there.
- `HOW_IT_WORKS.md` §Step 2 — current extraction behavior (now reflects PR #1's ≤120-char rule).
- `scripts/run_extract.py` — file every PR touches.
- `scripts/stability_check.py` — harness. After PR #1, includes canonical_key Jaccard with empty-exclusion, `invalid_key_rate`, and `--from-extractions` CLI mode.
- `tasks/tasks-extraction-contract-phase-1-live-constraints.md` — PR #1's task-file template. All subsequent PRs follow this pattern.
- `tasks/tasks-extraction-contract-phase-{1b,2,3,4a,4b,5}-*.md` — per-PR task files with TDD sub-tasks and acceptance gates.
- `research/stability-runs/contract-phase1-*/README.md` — pre-ship, C-full-post-ship, and diagnostic evidence from PR #1. Useful as baseline for all subsequent gates.
- Industry context (decision-informing but not ship-blocking): [Context Engineering 2.0 arxiv paper 2510.26493](https://arxiv.org/abs/2510.26493); [EDC framework paper](https://arxiv.org/html/2404.03868v1); [SemanticDeduplicator GitHub](https://github.com/gkamradt/SemanticDeduplicator).

## Current state (2026-04-23)

**Shipped in Cycle 1 + post-cycle work (commits `d157da2` through `b742564`):**

- D-skill anchor-naming (Step 6) — 100% anchor-naming rate across post-fix runs.
- Stability harness — Modes A/B/C live in `scripts/stability_check.py`.
- Pass 1 family clustering (Track B) — 6 clusters shipped. Jaccard 0.50 → 0.70.
- Silent-degradation items #1–3, #5 — all live.
- Per-run archival by fingerprint — `~/.local/share/lolla/runs/{case}/{run_id}/`.

**Shipped on feature branch (PR #13, IN REVIEW 2026-04-23):**

- **PR #1 — `live_constraints` terse canonical form.** Ships the ≤120-char terse-form rule on `constraint` text, `_validate_canonical_key` regex validator (pre-wired, inactive), `_apply_canonical_key_validation` post-extraction processor (pre-wired, inactive), harness `--from-extractions` CLI mode, canonical_key Jaccard (empty-excl) and `invalid_key_rate` metrics. Does NOT ship the `canonical_key` field itself.
- Cross-capture exact-text Jaccard on `live_constraints` moved **0.010 → 0.109 (10× win)**, with zero regressions on other fields.

**Not shipped (the rest of this roadmap):**

- `live_constraints.canonical_key` field with embedding-cosine metric — **PR #1b**
- `dropped_threads.canonical_key` + tie-break rule + ≤120-char rule on `thread` — **PR #2**
- `synthesized_position` as structured `Position` object — **PR #3**
- `decision_situation` terse canonical form — **PR #4a**
- `original_framing` first-turn anchor + terse form — **PR #4b**
- `reasoning_passages.move_type` enum + generalize hard-fail — **PR #5**

**Open Cycle-2 questions (conditional PRs #6–7, unchanged):**

- Negative-space field — PR #6 conditional
- Epistemic-posture field — PR #7 conditional

## Methodology upgrades (MANDATORY for all future PRs)

PR #1 produced four discipline changes. Every remaining PR adopts them:

### 1. Cross-capture is the acceptance signal; Mode C is a diagnostic

- Mode C N=5 has 10 pairs. Cross-capture 9-run has 36 pairs. The 3.6× sample-size gap matters.
- Mode C was contradicted by cross-capture on multiple fields during PR #1's diagnostic — **trust the larger sample for any gate call.**
- All acceptance gates below state cross-capture as the PRIMARY axis. Mode C is retained as a sanity check under conversation-held-constant conditions.

### 2. Exact-text Jaccard is the wrong metric for slug / enum / canonical fields

- Exact-text treats semantically-equivalent variants (`marcus-comp` vs `marcus-comp-below-market`) as disjoint.
- Industry pattern (EDC, Zep, Kamradt) uses embedding cosine or equivalent semantic metric.
- **Mandatory for PRs #1b, #2, and any enum field in PR #5.** Free-text similarity remains SequenceMatcher (suitable for character-level paraphrase drift).

### 3. Budget-balance every prompt addition

- PR #1 C-full caused fabricated-quote count 0→3 and `original_framing` similarity regression; stripping the prompt addition reversed both.
- Context pollution is observable in THIS pipeline, not just academic concept.
- **Every future PR must pre-measure ALL fields and post-measure ALL fields.** Gate includes "no regression on non-target fields beyond noise band" as an acceptance axis, not an afterthought.

### 4. Terse canonical-form rule is a compound pattern

- PR #1 proved: ≤120-char terse noun-phrase + state rule tightens free-text without semantic loss (0.010 → 0.109 cross-capture exact-text on `live_constraints`).
- Applicable wherever a free-text field has drifty phrasing: `thread` in dropped_threads (PR #2), `decision_situation` (PR #4a), `original_framing` (PR #4b), `latest_stance_text` in Position (PR #3).
- Apply the proven discipline; don't reinvent with per-field templates.

## Realistic-target calibration (from PR #1 baselines)

PR #1's cross-capture baselines on 9 Marcus captures should inform target-setting for every remaining PR. Aspirational targets in the original observations doc were overshoots; the table below reflects realistic ceilings given observed variance.

| Field | Pre-ship cross-capture | Observed ceiling on comparable rule (PR #1) | Realistic gate |
|---|---|---|---|
| `live_constraints.constraint` exact-text | 0.010 | 0.109 (10×) | — already achieved in PR #1 |
| `live_constraints.canonical_key` (embedding cosine) | undefined | TBD in PR #1b | ≥ 0.70 cross-capture |
| `dropped_threads.thread` exact-text | baseline to measure in PR #2 | expected ≥0.20 (thread is already more structured than constraint) | ≥0.20 cross-capture |
| `dropped_threads.canonical_key` (embedding) | undefined | TBD in PR #2 | ≥ 0.60 cross-capture (lower than #1b because dropped_threads is more of a judgment call) |
| `decision_situation` similarity | 0.367 | gain from terse-rule expected | ≥ 0.55 cross-capture |
| `original_framing` similarity | 0.209 | hard to move; baseline is already low | ≥ 0.35 cross-capture |
| `synthesized_position.latest_stance_text` similarity | 0.169 | structural change (Position object) | ≥ 0.35 cross-capture |
| `synthesized_position.stance` enum Jaccard | n/a | mechanical rule | ≥ 0.90 cross-capture (1.0 is a WARNING per harness doctrine) |
| `reasoning_passages` text Jaccard | 0.357 | no text-rule change in PR #5 | no regression (stay ≥ 0.30) |
| `reasoning_passages.move_type` agreement | undefined | depends on measurement design | distribution sanity (no single value > 60%) — see PR #5 |
| Fabricated count (any run) | 0 | 3 post-PR-1-C-full, 0 post-diagnostic | **always 0** |
| `invalid_key_rate` (on PRs introducing slug fields) | n/a | 0.0% in PR #1 diagnostic | ≤ 10% |

## Testing methodology (unchanged from original, refined with #1 learnings)

**Every PR's acceptance gate uses three axes, cross-capture primary:**

1. **Axis 1 — Cross-capture drift (PRIMARY, 9 Marcus captures × 1 run each, 36 pairs):**
   - Reproducible via `scripts/stability_check.py --from-extractions <post-ship JSON paths>`
   - Reports per-pair and aggregate metrics per field.

2. **Axis 2 — Mode C intrinsic drift (DIAGNOSTIC, N=5 on one capture):**
   - `scripts/stability_check.py --drift --conversation <newest> --n 5`
   - Sanity check under extraction-sampling-only variance. NOT a gate.

3. **Axis 3 — Qualitative read:**
   - Manual review of 3 extraction outputs per PR.
   - Does the target field read as intended (terse / stable / meaningful)?

**Regression check (mandatory on every PR):**
- No decrease outside noise band (~0.03) on any field the PR didn't target.
- `fabricated count` stays at 0.
- Cost per extraction call ≤ +10%.

## Validation set — Marcus-only, non-blocking external-case track

**What we have (unchanged 2026-04-22):** 9 Marcus `/tmp/lolla_*_conversation.txt` captures. No other cases ported from system_b (wrong shape).

**Honesty clause in every PR description:** results show the contract change works on Marcus. Generalization is verified only as non-Marcus cases accumulate in `~/.local/share/lolla/runs/`. No synthesis, no wrapped system_b cases, no dogfooding-to-accumulate.

**Parallel track:** whenever a non-Marcus `/lolla` run accumulates, add a line to `research/stability-runs/contract-phase{N}/cases.txt`. PR #N+1 re-runs all prior PRs' acceptance gates across new cases. The spec graduates from Marcus-only once the set reaches ≥ 5 distinct cases.

## PR sequence (revised 2026-04-23)

### PR #1 — `live_constraints` terse canonical form [IN REVIEW]

See PR #13 on GitHub. Shipped ≤120-char terse-form rule + infrastructure. Does NOT ship `canonical_key` field. See `tasks/tasks-extraction-contract-phase-1-live-constraints.md` and the `contract-phase1-*` evidence directories.

---

### PR #1b — `live_constraints.canonical_key` field + embedding-cosine metric [PAUSED 2026-04-23]

**What was tried:** two iterations of condensed canonical_key prompt text — inline in live_constraints block (attempt 1) and moved to SCHEMA NOTES footer (attempt 2). Evidence: `research/stability-runs/contract-phase1b-attempt-1-2026-04-23/README.md` + `contract-phase1b-attempt-2-2026-04-23/README.md`.

**What shipped from this work:** embedding-cosine metric infrastructure in `scripts/stability_check.py` (functions `_cosine_similarity`, `_best_match_mean_cosine`, `_get_embedding`, `compute_extraction_drift` extended with `live_constraints_canonical_key_embedding` metric). Fully tested (7 new unit tests). Available for any future canonical_key work.

**What did NOT ship:** the canonical_key prompt addition itself. Extractor still does not emit a `canonical_key` field.

**Why paused:** two iterations confirmed the canonical_key rule cannot be added to the monolithic extraction prompt without material trade-offs on other fields. Inline placement produces good slugs (embedding cosine 0.787 cross-capture — exceeds 0.70 target) but pollutes 4 adjacent fields (original_framing, decision_situation, live_constraints exact-text, dropped_threads each regressed beyond noise band). Footer placement reduces pollution on reasoning_passages but degrades slug quality (embedding cosine 0.664 — below target). Neither is a clean ship.

**What unblocks this PR:** Track A decomposition — separate LLM calls per field — structurally eliminates attention competition. Track A is deferred per the Cycle-1 handover. Until then, PR #1b stays paused.

**Doctrine insight captured:** even condensed prompt additions cause measurable context pollution in this pipeline. The "budget-balance" principle alone isn't enough — there's no fully-clean prompt addition possible at current model / prompt-shape. Future PRs add content at known cost; avoid unless the primary metric win clearly outweighs.

**Impact on roadmap:**
- PR #2 (dropped_threads canonical_key) was blocked on PR #1b. Re-scope PR #2 to ship ONLY the ≤120-char thread rule + tie-break detection, deferring canonical_key to the same Track A window as PR #1b.
- PRs #3, #4a, #4b, #5 proceed as planned; none depend on canonical_key.

**Why this PR exists:** the original PR #1 ambition (canonical_key as stable cross-run identity) failed because (a) the prompt text caused context pollution on other fields, and (b) exact-text Jaccard is the wrong metric for semantically-equivalent slugs. PR #1 shipped the proven side-effect win. PR #1b earns the canonical_key ambition with the right architecture: condensed prompt + semantic metric.

**Blocks:** PR #2 (needs canonical_key pattern proven before applying to dropped_threads).

**Task file:** `tasks/tasks-extraction-contract-phase-1b-canonical-key-embedding.md`.

**Scope:**

- Reintroduce `canonical_key` field in `EXTRACTION_SYSTEM_PROMPT` live_constraints block, **condensed** (~40% of the original block text) to budget-balance against other-field pollution.
- Add embedding-cosine helper to `scripts/stability_check.py`. Exact design (local sentence-transformer vs OpenAI embeddings API; pairwise vs clustered) is a task-start design decision — see task file §1.
- Extend `compute_extraction_drift()` with an embedding-cosine metric on `live_constraints.canonical_key`.
- Update acceptance-gate documentation to cite the embedding metric as the canonical_key primary axis.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| Cross-capture `canonical_key` embedding cosine mean | ≥ 0.70 |
| Cross-capture `canonical_key` embedding cosine min | ≥ 0.50 (no single pair catastrophically off) |
| `invalid_key_rate` overall | ≤ 10% |
| Regression on `original_framing` similarity | no decrease vs PR #1 baseline (cross-capture 0.218) — **sentinel field for pollution** |
| Regression on fabricated count | always 0 across 9 runs |
| Regression on other fields | no decrease > 0.03 vs PR #1 baseline |
| Cost per extraction call | ≤ +10% vs PR #1 shipped state (embedding calls add overhead) |
| Qualitative: canonical_keys read as stable identifiers | yes (3 spot-checks) |

**Risk / rollback:** prompt addition is the same class of change as PR #1 C-full. Mitigate via condensation + pre/post-measurement. If the embedding metric passes but pollution returns → roll back the prompt, keep the embedding infrastructure, retry with further condensation.

---

### PR #2 — `dropped_threads` tie-break rule + ≤120-char thread rule [RE-SCOPED 2026-04-23, NOT STARTED]

**Re-scope:** PR #1b paused → canonical_key portion of PR #2 deferred to Track A window. PR #2 now ships the two parts that don't depend on canonical_key: (1) ≤120-char terse-form rule on `thread` text (same mechanism as PR #1's win on `constraint`), and (2) tie-break rule as prose, measured via string-fallback until canonical_key ships.

**Blocked on:** nothing. Ready to execute independently.

**Task file:** `tasks/tasks-extraction-contract-phase-2-dropped-threads.md`.

**Scope:**

- Add `canonical_key` subfield to each `Thread` in `dropped_threads`, using the same pattern proved by PR #1b (condensed prompt + embedding metric).
- Add ≤120-char terse-form rule on `thread` text (mirror PR #1 win on `constraint`).
- Implement tie-break rule in the prompt: *a concern raised by a third party briefly addressed by the AI is a `Constraint` with `weight: situational`, NOT a `dropped_thread` — unless the user explicitly abandoned it later.* Mechanical rule: if user returned to it, it's live; if never revisited, it's dropped.
- Extend `_apply_canonical_key_validation` to walk dropped_threads as well as live_constraints.
- Extend `compute_extraction_drift` to compute canonical_key embedding metric on dropped_threads.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| Cross-capture `dropped_threads.canonical_key` embedding cosine mean | ≥ 0.60 |
| Cross-capture `dropped_threads.thread` exact-text Jaccard | ≥ 0.20 (vs pre-ship baseline 0.132) |
| Tie-break violations (items appearing in both `live_constraints` AND `dropped_threads` by canonical_key across any run) | 0 |
| `invalid_key_rate` overall (dropped_threads) | ≤ 10% |
| Regression on `live_constraints` metrics | no decrease vs PR #1b shipped state |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |

**Risk / rollback:** tie-break rule is the main new risk — it may cause the LLM to over-assign constraints as dropped_threads or vice versa. The "violations = 0" axis catches this. Rollback: revert the prompt + schema additions; infrastructure (validator extended to dropped_threads) stays inert.

---

### PR #3 — `synthesized_position` as structured `Position` object [NOT STARTED]

**Blocked on:** nothing (independent of canonical_key pattern). Can ship in parallel with PR #1b / #2 / #4a.

**Task file:** `tasks/tasks-extraction-contract-phase-3-synthesized-position.md`.

**Scope:** biggest structural change in the roadmap.

- Replace `synthesized_position: str` with object shape:
  ```json
  {
    "stance": "recommends_action" | "presents_tradeoffs" | "declines_to_recommend",
    "latest_stance_text": "...",
    "superseded_stances": [{"turn": N, "stance_text": "...", "superseded_reason": "..."}],
    "is_ambiguous": true | false
  }
  ```
- Mechanical temporal anchor: `latest_stance_text` = stance in FINAL assistant turn.
- Update `_map_to_critique_request` to read the object shape and build `vanilla_answer` equivalently to today (concat `latest_stance_text` + superseded summaries + full assistant text).
- Schema-version handling: either absorb the change inside `_map_to_critique_request` (cleanest) or version the extraction output. Design decision at task start.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| Cross-capture `stance` enum Jaccard (empty-excl) | ≥ 0.90 (1.0 is a warning per harness doctrine) |
| Cross-capture `latest_stance_text` similarity mean | ≥ 0.35 (vs pre-ship 0.169) |
| Qualitative: `is_ambiguous` correctly flags tradeoff presentations | yes (3 spot-checks) |
| Downstream `_map_to_critique_request` output functionally equivalent to today | yes (diff-test vs current state) |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |

**Risk / rollback:**
- `_map_to_critique_request` consumers may implicitly depend on string shape. Mitigation: grep all consumers before writing; absorb shape change inside mapping function.
- "Final assistant turn" brittle when final turn is a clarifying question. `is_ambiguous` should absorb; explicit fallback behavior documented in task file.
- Biggest pollution risk of the remaining PRs because the prompt addition is substantial. Condensed format required.

**Rollback:** the schema change is breaking. Revert the PR; old archived extraction JSONs still parse against the old shape.

---

### PR #4a — `decision_situation` terse canonical form [NOT STARTED]

**Blocked on:** nothing. Lowest-risk remaining PR; same mechanism as PR #1's proven win.

**Task file:** `tasks/tasks-extraction-contract-phase-4a-decision-situation.md`.

**Scope:** prompt-only change.

- Add ≤200-char rule to `decision_situation`: single sentence, neutral third-person, declarative.
- MUST NOT include: founder pronouns, emotive adjectives, speculative outcomes.
- Approach: apply PR #1's proven terse-rule discipline. Do NOT use the observation-doc's fill-in template ("[Whether|How|When] [action]...") — that's the inflexible path we've already rejected at the canonical_key level. Terse-rule alone is sufficient.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| Cross-capture `decision_situation` similarity mean | ≥ 0.55 (vs pre-ship baseline 0.367) |
| `decision_situation` length ≤ 200 chars | 9/9 runs |
| Qualitative: neutral third-person, single sentence | yes (3 spot-checks) |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |

**Risk / rollback:** template-over-constrain on edge-case conversations (compound decisions, multi-part framing). Mitigation: terse-rule instead of fill-in template; let the LLM preserve structure within the length budget. Rollback: revert prompt; no schema change.

---

### PR #4b — `original_framing` first-turn anchor + terse form [NOT STARTED]

**Blocked on:** PR #4a (same-file edit, second in a parallel track; also provides decision-making experience).

**Task file:** `tasks/tasks-extraction-contract-phase-4b-original-framing.md`.

**Scope:** prompt-only change.

- Anchor `original_framing` mechanically to FIRST user turn.
- MUST describe: what was assumed fixed, what alternatives were explicitly excluded, what lens the human brought.
- MUST NOT describe: framing shifts later in conversation (captured in `synthesized_position.superseded_stances` instead).
- ≤200-char terse-rule applied.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| Cross-capture `original_framing` similarity mean | ≥ 0.35 (vs pre-ship baseline 0.209 — baseline is genuinely low; stretch target is realistic) |
| `original_framing` length ≤ 200 chars | 9/9 runs |
| Qualitative: anchored to first user turn, no conversation-evolved framing | yes (3 spot-checks) |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |

**Risk / rollback:** original_framing has the lowest baseline of any field (0.209); it's genuinely hard to move. The 0.35 target is a stretch; acceptable outcome also includes "stayed at baseline but qualitative criteria met." If qualitative is strong but quantitative flat, ship — the anchor-to-first-turn rule produces structurally correct output even when character-level similarity is low.

---

### PR #5 — `reasoning_passages.move_type` enum + generalize hard-fail [NOT STARTED]

**Blocked on:** nothing (independent). Could ship anytime after PR #1.

**Task file:** `tasks/tasks-extraction-contract-phase-5-move-type.md`.

**Scope:**

- Add `move_type` enum to each `Passage`. **Reduced from 7 to 5 values** based on disambiguation-difficulty analysis in task file: `leap` / `dismissal` / `assertion_without_evidence` / `framing_shift` / `closure`. Drops `inversion` and `comparison` (those two were hard to disambiguate from `framing_shift` and `leap` respectively). Use `str` + validator, not strict enum, for future extensibility.
- Generalize existing retry-then-drop quote-validation into a reusable helper so future PRs referencing verbatim turn content don't re-implement it. **No behavior change** — just refactor.
- **Enum-stability measurement:** given passage text itself drifts (0.357-0.418 cross-capture), matching-passages-across-runs is itself unstable. Decision at task start: either (a) fuzzy-match passages first then measure enum agreement on matched set, or (b) distribution sanity only ("no single move_type > 60% of total passages") and accept that per-passage enum stability isn't cleanly measurable.

**Acceptance gate (cross-capture primary):**

| Axis | Target |
|---|---|
| `reasoning_passages.text` Jaccard (regression check on existing metric) | no decrease vs PR #1 baseline (stay ≥ 0.30) |
| `move_type` distribution sanity: no single value > 60% of passages across all 9 runs | pass |
| `move_type` enum-agreement method chosen at task start: (a) fuzzy-match + per-passage ≥ 0.60 OR (b) distribution-only | per chosen method |
| `_quote_validation.fabricated` count | 0 |
| Regression on other fields | no decrease > 0.03 |

**Risk / rollback:** enum may be too coarse or too fine — keep `str` + validator (not strict enum) so new values can be added in a follow-up without a breaking change. Generalized hard-fail helper is low-risk infrastructure.

---

## Dependency graph (revised 2026-04-23)

```
PR #1 (IN REVIEW)
    │
    ├──→ PR #1b (canonical_key + embedding metric)
    │         │
    │         └──→ PR #2 (dropped_threads.canonical_key + tie-break + thread ≤120-char)
    │
    ├──→ PR #4a (decision_situation terse form) ─── PR #4b (original_framing terse + anchor)
    │
    ├──→ PR #3 (synthesized_position Position object) — independent; substantial prep
    │
    └──→ PR #5 (reasoning_passages.move_type + hard-fail generalize) — independent
```

**Only hard dependency:** PR #1b → PR #2. Everything else can parallelize after PR #1 merges.

**Suggested execution order** (one PR shipped at a time, to keep context-pollution measurement clean):

1. PR #1 merge (IN REVIEW today)
2. PR #1b (smallest next — unblocks PR #2)
3. PR #4a (lowest-risk, same-mechanism as PR #1's win)
4. PR #4b (same mechanism as #4a; natural pair)
5. PR #2 (now unblocked; reuses PR #1b's pattern)
6. PR #3 (biggest structural change; benefits from the three previous PRs having shown how pollution-budgeting works)
7. PR #5 (can interleave anywhere after #1)

## Cycle 2 decision gate (after PR #5 lands)

Re-run Mode C + cross-capture full-suite on Marcus and assess:

1. **Lane 1 tendency-set stability across extraction-equivalent runs.** If Pass 1 tendencies Jaccard improved (because contract reduced input variance), the system achieves "repeatable structural read" on Marcus.
2. **Lane 2 anchor stability.** Same question for companion anchors.
3. **Qualitative: what subtle failures still slip through?** If answer is "nothing significant," Cycle 2 stops here.

If significant failures remain — especially Lane 1 still routing to different tendency families across runs despite tight extraction — Cycle 2 extends to the conditional PRs below.

## Conditional Cycle 2 PRs (unchanged structure)

### PR #6 (conditional) — Negative space field

Unchanged from 2026-04-22 plan. Unblock depends on Cycle 2 gate. See original section.

### PR #7 (conditional) — Epistemic posture field

Unchanged. Unblock depends on Cycle 2 gate AND PR #6 outcome.

## What this plan is NOT

- **Not Track A decomposition.** Splitting extraction into 5 specialists is still deferred. The contract must be proven first. Decomposition without a tight contract preserves ambiguity at a new layer.
- **Not a rewrite.** All schema changes are additive (canonical_key, move_type, Position object). `_map_to_critique_request` absorbs the shape change for Position so downstream lanes don't change.
- **Not cross-model.** Every PR uses current production model (`x-ai/grok-4.1-fast`). Model choice is orthogonal.
- **Not ensemble voting.** See `llm-decomposition-handover.md` §0e.

## Branching strategy

- One branch per PR. Names: `feat/extraction-contract-phase-{1b,2,3,4a,4b,5}-{slug}`.
- Rebase on `main` before opening each PR. Don't pile PRs on top of each other.
- Each PR independently revertible.
- Acceptance evidence → `research/stability-runs/contract-phase{N}-{date}/`, same subdirectory layout as PR #1 (`modec-n5/`, `cross-capture/`, `cross-capture-drift/`, `README.md`, optional `qualitative-spot-check.md`).
- PR description links to the evidence directory.

## What could change this plan

- **Non-Marcus cases accumulate.** Extend the test set; re-run all prior PRs' gates on any new case. If a non-Marcus case shows a failure mode Marcus didn't show, pause the sequence and extend the observations doc before continuing.
- **Cycle 2 gate shows Lane 1/2 still unstable despite tight extraction.** Contract isn't the bottleneck; something else is. Revisit `llm-decomposition-handover.md` §6 for held-track options.
- **Axis 1 (cross-capture) fails consistently across PRs.** Means capture drift (Step 1) is the dominant variance, not extraction (Step 2). The contract work caps out; next cycle addresses the capture layer (SKILL.md Step 1 rules, or upstream mechanical capture).
- **User scope change.** Park the remaining PRs with a status line noting where work stopped.

## Execution checklist for any future PR

Before starting:

- [ ] Re-read the corresponding field section in `research/extraction-contract-observations-2026-04-22.md`.
- [ ] Re-read this roadmap's §"Methodology upgrades" and §"Realistic-target calibration."
- [ ] Confirm prior PRs' cross-capture evidence still holds (no drift regression from production deploys).
- [ ] Check `~/.local/share/lolla/runs/` for non-Marcus cases. If any accumulated, ADD them to the test set and re-measure prior PRs' gates before starting this one.
- [ ] Open the PR's task file and execute sub-tasks in order.
- [ ] Branch off `main` fresh.

Ship criteria:

- [ ] All acceptance-gate axes meet targets.
- [ ] Cross-capture is the PRIMARY signal; don't ship on Mode C alone.
- [ ] Pre/post-measurement shows no regression on non-target fields outside noise band.
- [ ] Qualitative review passes on 3 spot-checks.
- [ ] Evidence directory populated + linked in PR description.
- [ ] Honesty clause in PR description (Marcus-only validation).

Roadmap status updates:

- Mark PR status in this file: `NOT STARTED` → `IN PROGRESS` (at branch creation) → `IN REVIEW` (at PR open) → `SHIPPED (commit: <merge-hash>)` (at merge) OR `PAUSED (reason: ...)` (at gate failure).

## References

- Observations doc (normative spec): `research/extraction-contract-observations-2026-04-22.md`
- Cycle 1 handover: `research/llm-decomposition-handover.md`
- Architecture: `HOW_IT_WORKS.md`
- Extraction code: `scripts/run_extract.py`
- Harness: `scripts/stability_check.py`
- Context Engineering 2.0 paper (GAIR-NLP, Oct 2025): arxiv 2510.26493 — entropy-reduction framing + 8-operation taxonomy + "context pollution" naming
- EDC framework (ACL 2024): arxiv 2404.03868 — three-phase Extract/Define/Canonicalize pattern
- Kamradt SemanticDeduplicator: github.com/gkamradt/SemanticDeduplicator — hybrid cosine + LLM verification reference implementation
