# Extraction Contract — PR Roadmap

**Authored:** 2026-04-22
**Status:** Planning complete. PR #1 NOT STARTED.
**Scope:** `lolla-skill` Step 2 (`scripts/run_extract.py`). NOT system_b.

## Why this document exists

The extraction contract work is a multi-PR effort. This roadmap exists so the sequence survives context loss. If a future session asks "what's next after PR #2?" the answer is in this file, not in conversation memory.

Each PR is a ship-or-stop measurement event with its own acceptance gate. If a PR fails its gate, the plan pauses at that point — not every PR is predetermined to land.

## Supporting docs (READ FIRST)

- `research/extraction-contract-observations-2026-04-22.md` — the normative spec (fields, types, Mode C pass criteria). This roadmap implements that spec one field-group at a time.
- `research/llm-decomposition-handover.md` — Section 0 explains why extraction-front was deferred in Cycle 1; today's scope shift reverses that deferral per the user's 2026-04-22 call.
- `HOW_IT_WORKS.md` §Step 2 — current extraction behavior. This is what we're changing.
- `scripts/run_extract.py` — the file every PR in this roadmap touches.
- `scripts/stability_check.py` — Mode C drift harness. Used by every PR's acceptance gate.

## Current state (2026-04-22)

**Shipped in Cycle 1 + post-cycle work (commits `d157da2` through `b742564`):**

- D-skill anchor-naming (Step 6) — 100% anchor-naming rate across post-fix runs.
- Stability harness — Modes A/B/C live in `scripts/stability_check.py`.
- Pass 1 family clustering (Track B) — 6 clusters shipped. Jaccard 0.50 → 0.70.
- Silent-degradation items #1 (quote fabrication retry-then-drop), #2 (capture-critical gating), #3 (truncation transparency), #5 (Lane 3 dropped-element surfacing) — all live.
- Per-run archival by fingerprint — `~/.local/share/lolla/runs/{case}/{run_id}/`.

**NOT shipped (this roadmap's scope):**

- `live_constraints.canonical_key` — PR #1
- `dropped_threads.canonical_key` + tie-break rule with live_constraints — PR #2
- `synthesized_position` as structured `Position` object with stance enum + temporal anchor — PR #3
- `decision_situation` + `original_framing` canonical forms — PR #4
- `reasoning_passages.move_type` enum + generalize hard-fail — PR #5

**Open question, Cycle 2 only (PRs #6–7):**

- Negative-space field (alternatives never considered, what-ifs avoided, stakes never weighed) — PR #6 conditional
- Epistemic-posture field (confidence markers, hedging, authority claims, evidence gaps) — PR #7 conditional

## Validation set — n=1 constraint

**What we have:**

- **Archive** (`~/.local/share/lolla/runs/`): 4 runs total across 2 case fingerprints — `marcus-equity` (1 run) + `grant-equity-partnership-status` (3 runs). Almost certainly the same underlying Marcus conversation; capture drift produced different case fingerprints.
- **`/tmp/`**: 9 Marcus `conversation.txt` captures across different sessions + 11+ extraction JSONs including prior Mode C drift outputs.
- **No other cases.** System_b's (query, vanilla) pairs don't port — they're single-shot, so they don't exercise multi-turn contract parts (`superseded_stances`, `introduced_turn`, `status: active|dropped|modified`, turn anchors, dropped-vs-live tie-break).

**What this means for the plan:**

- Every PR's acceptance gate uses Marcus-only as the validation set.
- Each PR runs on three axes: (1) Mode C intrinsic drift N=5 on one capture, (2) cross-capture stability across the 9 Marcus captures, (3) qualitative read of output.
- **Honesty clause in PR descriptions:** results show the contract change works on Marcus. Generalization is verified only as non-Marcus cases accumulate in the archive. No synthesis, no wrapped system_b cases, no dogfooding-to-accumulate (that biases the set toward conversations chosen to test the contract).

**Non-blocking parallel track:** as real non-Marcus /lolla runs accumulate, add them to `research/stability-runs/contract-phaseN/cases.txt` indexes. PR #N+1 re-runs all prior PRs' gates on any cases added after #N. The spec only "graduates" from Marcus-only once the set reaches ~5 distinct cases.

## Testing methodology (applies to every PR)

Every PR uses the same three axes. Each PR's section states its field-specific targets; the method is identical.

**Axis 1 — Extractor intrinsic drift (Mode C, N=5 on one capture):**
- Run `scripts/stability_check.py --drift --conversation <newest-marcus-capture> --n 5`.
- Measures: Mode C reruns `run_extract.py` N times against the same `conversation.txt`. Isolates extractor sampling variance from capture variance.

**Axis 2 — Cross-capture robustness (9 Marcus captures, 1 run each):**
- Run the new extractor once against each of 9 archived Marcus `conversation.txt` files.
- Compute Jaccard on the PR's target fields across all 9 outputs.
- Tests whether the canonical form is robust to Step 1 (Claude-writes-from-memory) capture drift.

**Axis 3 — Qualitative read:**
- Human review of 3 outputs. Does the canonical form read as a stable identifier, or as a phrasing accident?
- For `canonical_key` fields: do two runs produce the same key for clearly the same concept?
- For stance/move_type enums: does the assigned enum value match how a reader would classify the passage?

**Regression check (every PR):**
- No decrease in similarity/Jaccard on fields the PR didn't change.
- No cost increase >10% per extraction call.
- `_quote_validation.fabricated` count stays at 0.

## PR sequence

### PR #1 — `live_constraints.canonical_key`

**Status:** IN PROGRESS (branch: `feat/extraction-contract-phase-1-live-constraints`).

**Scope (minimal):**
- Add `canonical_key` field to each `Constraint` in the extraction schema.
- Add canonical-form phrasing rule to the extraction prompt: constraint text ≤120 chars, terse noun-phrase-plus-state form.
- Add `canonical_key` rule to the prompt: 2–4 words, lowercase, hyphen-separated, noun-phrase identity (e.g. `marcus-technical-concentration`). LLM generates the key; Python validates the format.
- Update `capture_manifest` / result schema to include canonical_keys in serialized output.

**Files touched:**
- `scripts/run_extract.py` — prompt text, schema, post-extraction validation.
- `scripts/stability_check.py --drift` — extend the drift report to compute Jaccard on `canonical_key` in addition to exact text.
- `HOW_IT_WORKS.md` §Step 2 — update the field description for `live_constraints`.

**Acceptance gate (Marcus-only):**

| Axis | Target |
|---|---|
| Mode C N=5, `live_constraints.canonical_key` Jaccard | ≥ 0.80 |
| Cross-capture (9 captures), `live_constraints.canonical_key` Jaccard | ≥ 0.70 |
| Qualitative: canonical_keys read as stable identifiers | yes (3 spot-checks) |
| Regression: other fields' similarity/Jaccard | no decrease vs baseline |
| Cost delta per extraction call | ≤ +10% |

**Why this PR first:** Mode C baseline shows `live_constraints` Jaccard on exact text = 0.00. Biggest single signal in the dataset. If canonical_key mechanism works anywhere, this is where it shows up loudest.

**Risk / rollback:**
- If Axis 2 (cross-capture) fails but Axis 1 passes: the slug is LLM-variance-stable but not capture-variance-stable. Consider falling back to Python-side slugification from a canonicalized terse form (Option C in design notes).
- If both fail: the hypothesis that "canonical_key via LLM output" works is wrong. Pause roadmap; revisit the contract spec itself.
- Rollback: the schema change is additive. Revert the prompt + schema to pre-PR and old extractor runs still parse.

**Unblocks:** PR #2 (same mechanism, different field).

---

### PR #2 — `dropped_threads.canonical_key` + tie-break rule

**Status:** NOT STARTED. Blocked on PR #1.

**Scope:**
- Apply PR #1's canonical_key mechanism to `dropped_threads`.
- Implement the tie-break rule from the observations doc §live_constraints: a concern raised by a third party and briefly addressed by the AI is a `Constraint` with `weight: situational`, NOT a `dropped_thread` — unless the user explicitly abandoned it later. Rule: if the user returned to it, it's live; if never revisited, it's dropped.
- Add `raised_by` enum, `raised_turn`, `status` enum (`never_addressed` / `acknowledged_then_dropped` / `resolved`), `superseded_by` optional.

**Files touched:**
- `scripts/run_extract.py` — schema + prompt.
- `scripts/stability_check.py --drift` — add dropped_threads canonical_key Jaccard.
- `HOW_IT_WORKS.md` §Step 2 — update dropped_threads description.

**Acceptance gate (Marcus-only):**

| Axis | Target |
|---|---|
| Mode C N=5, `dropped_threads.canonical_key` Jaccard | ≥ 0.70 |
| Cross-capture, `dropped_threads.canonical_key` Jaccard | ≥ 0.60 |
| Tie-break consistency: no item appears in both `live_constraints` and `dropped_threads` across any run | 0 violations |
| Qualitative: tie-break rule assigns third-party concerns correctly | yes |
| Regression | no decrease on PR #1's gate |

**Why second:** same mechanism as PR #1, lower Mode C target (0.70 vs 0.80) because dropped_threads is more naturally a judgment call. Pairs naturally with PR #1 via the tie-break rule — attempting to ship the tie-break rule before both fields have canonical_keys produces incomplete semantics.

**Risk / rollback:** same as PR #1. Tie-break rule is the main new risk; monitor the "0 violations" metric.

**Unblocks:** PR #3 (independent mechanism; any order after #2 is fine).

---

### PR #3 — `synthesized_position` as structured `Position` object

**Status:** NOT STARTED. Blocked on PR #2.

**Scope:** biggest structural change in the roadmap.

- Replace `synthesized_position: str` with the `Position` object from the observations doc:
  ```json
  {
    "stance": "recommends_action" | "presents_tradeoffs" | "declines_to_recommend",
    "latest_stance_text": "...",
    "superseded_stances": [{"turn": N, "stance_text": "...", "superseded_reason": "..."}],
    "is_ambiguous": true | false
  }
  ```
- Mechanical temporal anchor: `latest_stance_text` = the stance expressed in the FINAL assistant turn. Not "most developed."
- Update `_map_to_critique_request` to build `vanilla_answer` from the new structure (concatenate `latest_stance_text` + superseded_stances summary + full assistant text as before).

**Files touched:**
- `scripts/run_extract.py` — schema, prompt, `_map_to_critique_request`.
- `engine/system_b/` — check whether any consumer of `synthesized_position` reads it as a string. Likely zero changes there because `_map_to_critique_request` absorbs the shape change. Verify via grep.
- `scripts/stability_check.py --drift` — stance Jaccard + latest_stance_text similarity.
- `HOW_IT_WORKS.md` §Step 2 — new field structure.

**Acceptance gate (Marcus-only):**

| Axis | Target |
|---|---|
| Mode C N=5, `stance` enum Jaccard | 1.0 (mechanical rule = identical enum) |
| Mode C N=5, `latest_stance_text` similarity | ≥ 0.70 |
| Cross-capture, `stance` Jaccard | ≥ 0.90 |
| Qualitative: `is_ambiguous` correctly flags tradeoff presentations | yes |
| Regression | no decrease on PR #1 + #2 |

**Why third:** biggest structural change, largest downstream-consumer risk. Ship after canonical_key pattern is proven so we're not juggling two experimental mechanisms at once.

**Risk / rollback:**
- `_map_to_critique_request` consumers may implicitly depend on the old string shape. Grep before writing.
- "Final assistant turn" is mechanically defined but brittle on conversations where the AI's final turn is a clarifying question rather than a position. `is_ambiguous` should absorb this.
- Rollback: schema change is breaking. Old extraction JSONs won't parse as new Position objects. Version the schema or add a migration helper — don't expect zero-downtime.

**Unblocks:** PR #4 (independent; any order fine).

---

### PR #4 — `decision_situation` + `original_framing` canonical forms

**Status:** NOT STARTED. Blocked on PR #3.

**Scope:** phrasing-rule PRs, lowest mechanism change of the roadmap.

- Add canonical-form template to `decision_situation`: *"[Whether|How|When] [action] [subject], given [situation summary], with stakes [brief]."* One sentence, neutral third-person. Forbid founder pronouns, emotive adjectives, speculative outcomes.
- Anchor `original_framing` mechanically to the FIRST user turn. MUST describe: what was assumed fixed, what alternatives were explicitly excluded, what lens the human brought. MUST NOT describe conversation-evolved framing (that's in `superseded_stances`).

**Files touched:**
- `scripts/run_extract.py` — prompt only. No schema changes.
- `scripts/stability_check.py --drift` — already measures similarity on these fields; no harness change.
- `HOW_IT_WORKS.md` §Step 2 — update field descriptions.

**Acceptance gate (Marcus-only):**

| Axis | Target |
|---|---|
| Mode C N=5, `decision_situation` similarity | ≥ 0.85 |
| Mode C N=5, `original_framing` similarity | ≥ 0.70 |
| Cross-capture, `decision_situation` similarity | ≥ 0.75 |
| Qualitative: canonical_form template followed | yes (3 spot-checks) |
| Regression | no decrease on PR #1–3 |

**Why fourth:** smallest mechanism change (prompt-only), so risk is low. Put it later so it's not a distraction while the bigger structural PRs are in flight.

**Risk / rollback:** the template may over-constrain on edge-case conversations (e.g., where the decision is compound or truly multi-part). If Axis 3 fails on that pattern, relax the template to a rule ("single-sentence, neutral third-person, opens with the decision verb") rather than a fill-in-the-blank form.

**Unblocks:** PR #5.

---

### PR #5 — `reasoning_passages.move_type` + generalize hard-fail

**Status:** NOT STARTED. Blocked on PR #4.

**Scope:**
- Add `move_type` enum to each `Passage`: `leap` / `dismissal` / `assertion_without_evidence` / `framing_shift` / `closure` / `inversion` / `comparison`.
- Generalize the existing retry-then-drop quote-validation to any future field that references verbatim turn content. Currently `reasoning_passages` is the only such field; this PR is the hook for future fields without changing live behavior.
- Per the observations doc: hard-fail was partially shipped as retry-then-drop (Option D). This PR keeps retry-then-drop as the behavior and refactors the validation layer so it's reusable. No behavior change there.

**Files touched:**
- `scripts/run_extract.py` — prompt + schema + validation refactor.
- `engine/system_b/companion_routing.py` — check whether Lane 2 fingerprint/verification could consume `move_type` as a filter (not required for this PR, just note in the PR description as a follow-up).
- `HOW_IT_WORKS.md` §Step 2.

**Acceptance gate (Marcus-only):**

| Axis | Target |
|---|---|
| Mode C N=5, `reasoning_passages` text Jaccard | ≥ 0.50 (same as current target) |
| Mode C N=5, `move_type` enum agreement rate | ≥ 0.60 (passage-level: when the same passage is extracted, what fraction of runs agree on move_type?) |
| Cross-capture, move_type distribution | no single move_type > 60% of all passages (sanity check that the enum isn't degenerate) |
| `_quote_validation.fabricated` count | 0 |
| Regression | no decrease on PR #1–4 |

**Why fifth:** additive enum, low-risk. Enables Lane 1 and Lane 2 to filter passages by reasoning-move type in future PRs (outside this roadmap). Reasoning_passages has the best current Jaccard (0.389); gains here are the smallest of the roadmap, which is why it's last.

**Risk / rollback:** the enum may need to grow as cases accumulate. Keep it open to extension in the schema (use `str` + validate-against-known-values rather than strict enum).

**Unblocks:** Cycle 2 evaluation — see below.

---

## Cycle 2 decision gate (after PR #5)

After PR #5 lands, re-run Mode C full-suite on the Marcus set and assess:

1. **Lane 1 stability across extraction-equivalent runs.** If Pass 1 tendencies Jaccard improved (because the contract reduced input variance), that's a major doctrinal win and the system achieves "repeatable structural read" on Marcus.
2. **Lane 2 anchor stability.** Same question for companion anchors.
3. **Qualitative: what subtle failures still slip through?** If answer is "nothing significant," Cycle 2 stops here.

If significant failures remain — specifically, if Lane 1 still routes to different tendency families across runs despite stable extraction — Cycle 2 extends to the conditional PRs below.

## Conditional Cycle 2 PRs

### PR #6 (conditional) — Negative space field

**Status:** CONDITIONAL. Depends on Cycle 2 gate.

**Scope (if unblocked):**
- Add `negative_space` field to extraction output. Subfields:
  - `user_asks_unaddressed` — user questions raised but not answered by the assistant. Must quote the user's turn verbatim.
  - `alternatives_never_considered` — decision paths the conversation never surfaced (e.g., if the decision is "buy vs build," was "partner-with" mentioned?).
  - `stakes_never_weighed` — stakes implicitly present in the scenario but never given weight in the assistant's analysis.
  - `what_ifs_avoided` — reversibility questions or what-if scenarios the assistant didn't raise.

**Why this is harder:** each of these requires the LLM to produce things that aren't in the transcript. That's a fundamentally different task from "summarize turn N." It might not be extractable in the same prompt even with a perfect contract — may need its own specialist call. Scope the PR to investigate both options (same call vs specialist call) before committing.

**Risk:** the LLM will fabricate negative-space items under pressure to produce output. Mode C will show whether the outputs are stable enough to be useful.

**Acceptance gate:** TBD when/if this PR is unblocked. Likely a qualitative gate ("does surfacing negative space change what Lane 1 catches?") more than a Mode C number, because negative space is fundamentally creative.

---

### PR #7 (conditional) — Epistemic posture field

**Status:** CONDITIONAL. Depends on Cycle 2 gate AND PR #6 outcome.

**Scope (if unblocked):**
- Add `epistemic_posture` field:
  - `confidence_markers` — verbatim phrases where the assistant expressed confidence (e.g., "clearly," "obviously," "without doubt").
  - `hedging_patterns` — verbatim phrases where the assistant hedged (e.g., "might," "could potentially," "it's worth considering").
  - `authority_claims` — passages where the assistant appealed to authority (e.g., "research shows," "experts agree").
  - `evidence_gaps` — claims made without supporting evidence in the conversation.

**Why maybe useful:** Lane 1 tendencies (overoptimism, authority-misinfluence) today re-derive these from vanilla_answer. Surfacing them in extraction gives Lane 1 structured signals instead of re-reading prose.

**Why maybe not:** may duplicate what `reasoning_passages.move_type` already captures. PR #6's outcome determines whether we need more negative-space-adjacent fields or whether move_type is sufficient.

**Acceptance gate:** TBD.

---

## What this plan is NOT

- **Not Track A decomposition.** Splitting extraction into 5 specialists is still deferred. The contract must be proven first (Cycle 2 gate above). Decomposition without a tight contract preserves ambiguity at a new layer, per the observations doc.
- **Not a rewrite.** The schema changes are additive (canonical_key, move_type, Position object). `_map_to_critique_request` absorbs the shape changes so downstream lanes don't change.
- **Not cross-model.** Every PR uses the current production model (`x-ai/grok-4.1-fast`). Model choice is orthogonal.
- **Not ensemble voting.** See `llm-decomposition-handover.md` §0e for the doctrinal reason.

## Branching strategy

- One branch per PR. `feat/extraction-contract-phase-1-live-constraints`, etc.
- Rebase on `main` before opening each PR. Don't pile PRs on top of each other.
- Each PR is independently revertible. If PR #3 regresses something, revert just #3 — #1 and #2 continue to hold.
- Acceptance evidence goes into `research/stability-runs/contract-phase{N}-{date}/` with the Mode C outputs + cross-capture diff + qualitative notes. PR description links to that directory.

## What could change this plan

- **Non-Marcus cases accumulate.** If new cases show Mode C failure modes that Marcus didn't show, the spec may need additions before the next PR ships. Revisit the observations doc first; extend if needed.
- **Cycle 2 gate shows Lane 1/2 still unstable despite tight extraction.** Means the contract isn't the bottleneck; something else is. Revisit `llm-decomposition-handover.md` Section 6 for the held-track options (C-extended, C-fingerprint).
- **Axis 2 (cross-capture) fails consistently across PRs.** Means capture drift (Step 1) is the dominant variance, not extraction (Step 2). The contract work caps out; next cycle has to address the capture layer (SKILL.md Step 1 rules, or upstream mechanical capture).
- **User scope change.** If the user decides extraction-front is no longer priority, park the remaining PRs here with a status line noting where work stopped.

## Execution checklist

Before starting any PR:

- [ ] Re-read the corresponding field section in `research/extraction-contract-observations-2026-04-22.md` — that's the normative spec; this roadmap is just the sequencing.
- [ ] Confirm prior PRs' Mode C evidence still holds (no regression from drift in the production environment).
- [ ] Check `~/.local/share/lolla/runs/` — if non-Marcus cases have accumulated, add them to the test set for this PR's acceptance gate.
- [ ] Branch off `main` fresh.
- [ ] Write the PR diff, run Mode C (N=5) on newest capture, run cross-capture across 9 captures, do qualitative review.
- [ ] If all three axes pass: open PR. If any fails: note the failure in this roadmap under the PR's section, diagnose before retrying.
- [ ] Mark PR status in this file: `NOT STARTED` → `IN PROGRESS` → `SHIPPED (commit: <hash>)` or `PAUSED (reason: ...)`.

## References

- Observations doc (normative spec): `research/extraction-contract-observations-2026-04-22.md`
- Cycle 1 handover (context): `research/llm-decomposition-handover.md`
- Architecture: `HOW_IT_WORKS.md`
- Extraction code: `scripts/run_extract.py`
- Mode C harness: `scripts/stability_check.py`
