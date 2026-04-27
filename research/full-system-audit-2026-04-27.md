# `/lolla` full system audit — 2026-04-27

**Scope**: granular pass over `HOW_IT_WORKS.md` and `SKILL.md` against current `main`. Verifies specific claims by reading code, KG counts, and a recent product run. Surfaces drift, dead references, and gaps. Companion to `research/full-system-audit-2026-04-23.md` (4 days earlier; many of its open issues are now resolved).

**Honesty about depth**: I checked specific claims. I did NOT line-by-line audit every module. Verifications focused on: KG counts, file paths, script existence, schema fields in a real `result.json`, anchor-naming wiring, memo template structure, and recent additions from PRs #43–#60. I read the doc end-to-end but did not exhaust every claim — I prioritized the load-bearing ones and the recent additions.

**Today's main HEAD**: `3bfdd87` (PR #60, Lane 2 design-intent paragraph). Lane 2 closed.

**What this audit answers**:
- Is `HOW_IT_WORKS.md` accurate against current code?
- Where has the doc drifted from the system?
- What recent additions (PRs #43–#60) are not yet reflected?
- What dead references remain?

**What this audit does NOT answer**:
- Whether the doc's design philosophy is correct (the prior audit and HOW_IT_WORKS.md itself argue that case)
- Per-module line-by-line correctness
- Whether SKILL.md's prompts/wording is optimal

---

## 1. Verifications passed (the doc is accurate on these)

### 1.1 Knowledge graph counts

| Doc claim | Doc location | Verified | Source |
|---|---|---|---|
| 222 mental models | line 57 | ✅ 222 | `len(kg["models"])` |
| 25 cognitive tendencies | line 68 | ✅ 25 | `len(kg["tendencies"])` |
| 1,358 model-relationship edges | line 64 | ✅ 1,358 (ally 523 + structured_tension 491 + antagonist 344) | `kg["edges"]` filtered by relation type |
| 867 ally + antagonist edges | line 64 | ✅ 867 (523+344) | same |
| 241 antidote bindings | line 68 | ✅ 241 | `tendency_antidote` edge count |
| 15 reframing-routing frame patterns (Wave 5) | implied from §"Lane 3" | ✅ 15 frame patterns, 177 bindings, 50 unique models | `kg["reframing_routing"]` |
| Wave 5 — 50 models | line 65 | ✅ 50 unique models | same |
| 15-dimension MECE taxonomy (Lane 4) | line 594 | ✅ 15 | `kg["structural_coverage_routing"]["dimensions"]` |
| 82 model bridges across 74 unique models (Wave 6) | line 608 | ✅ 82/74 | per-dimension `models` arrays summed |

### 1.2 Pipeline runtime contract

| Doc claim | Verified |
|---|---|
| `SystemBPipeline.run()` accepts `ConversationContext` only, raises `TypeError` otherwise (line 151, 534) | ✅ Code path matches |
| IR built at entry via `construct_conversation_ir(...)` (line 159) | ✅ |
| Lane packets via `Lane4Packet` (line 161) | ✅ |
| `run_fingerprint_call_from_packet` and `run_verification_call_from_packet` (line 567) | ✅ Both functions exist in `companion_routing.py` |

### 1.3 Step 4 / Step 6 / Memo plumbing

| Doc claim | Verified |
|---|---|
| Memo has 8 sections in this order (lines 707–718): Heading, Key Findings, Mental Model Connections, Frame Alternatives, Structural Gaps, Delivery Check, Updated Position, Pressure Check | ✅ `scripts/render_memo.py:42-75` has the same 8 sections, same order |
| Anchor-naming invariant: every anchor goes to §1/§2/§3, never silently skipped (line 682) | ✅ Codified in `SKILL.md:350` |
| Three-treatment vocabulary: primary pressure / secondary lens / set aside with a reason (lines 684–688) | ✅ Codified in `SKILL.md:352-358` |
| Anchor `display_name` used **verbatim** (line 682) | ✅ `SKILL.md:350` requires verbatim string |
| `run_health` envelope, Pressure Check, gap_check persistence (lines 695–718) | ✅ Persisted in `result.json` (verified in production archive) |

### 1.4 Recent additions (PRs #43–#60) accurately reflected

| Addition | Doc location | Status |
|---|---|---|
| Lane 2 design-intent paragraph ("a lens, not a verdict") | lines 569–576 (PR #60) | ✅ Present, accurate, cites real artifacts |
| `BoundaryCallMetadata.model` and `finish_reason` capture (PR #58) | line 574 | ✅ Mentioned by name |
| `is_malformed_verifier_response` helper (PR #58) | line 574 | ✅ Mentioned by name |
| Track 2 KG bullet 4 tightening (Checklists `select_when[3]`) | line 576 (cited as `data/knowledge_graph.json:20486`) | ✅ Accurate citation; verified the file at that line is the new "recurring multi-step process" wording |
| Track 1 v1 catastrophic regression as anti-example | line 576 | ✅ References `e6-prompt-test-residual.md`; that file exists on main |

### 1.5 Lane 1 PR #37 expansion

The doc's PR #37 narrative (lines 542–555) — Pass 1/Pass 2 SOURCE broadened to both speakers, MISSED CHALLENGE added as fourth firing shape, validation against 10-case + Marcus corpus — is consistent with the prompts in `engine/system_b/prompts.py` and `engine/system_b/deep_checks.py`.

### 1.6 Architecture migration narrative

The §"Evolution: How It Used to Work, How It Works Now, and Why" (lines 168–238) is accurate against current code. Phase 6 deletions (`CritiqueRequest`, `--legacy-contract`, `_context_to_critique`) confirmed: those symbols don't exist on main.

---

## 2. Drift — claims that no longer match code

### 2.1 Lane 2 — "15-20 candidate mental models" vs actual default

**Doc** (line 561): *"Recall: Keyword overlap + optional embedding search identifies 15-20 candidate mental models from the 222-model substrate."*

**Code** (`companion_routing.py` recall_candidates and pipeline call site): max_candidates default is **60**, not 15-20. E2 / E6 baselines confirm the slate is 60 in production.

**Why this matters**: future contributors planning prompt or recall changes might assume the verifier sees ~20 candidates when it actually sees 60. Token-budget reasoning, slate-stability claims, and any "candidate cap tuning" discussion gets miscalibrated.

**Recommended fix**: change "15-20 candidate mental models" → "up to 60 candidate mental models (the candidate cap)" in line 561.

### 2.2 Lane 2 — "2-3 OpenRouter calls" header vs actual

**Doc** (line 557): *"**Lane 2 — Model Companion (2-3 OpenRouter calls):**"*

**Code**: Lane 2 is exactly 2 LLM calls (fingerprint + verification). Recall is deterministic. The "2-3" range was probably from a prior pipeline shape with embedding-LLM expansion.

**Recommended fix**: change to "(2 OpenRouter calls)" — fingerprint + verification.

### 2.3 §"Architecture / Current State (2026-04-25)" date stamp

**Doc** (line 149): *"### Current State (2026-04-25)"*

The state described (Phase 6 done, conversation-first runtime, IR + Lane4Packet) is still current. But the date stamp is stale — significant additions landed since (PR #43–#60). Either bump the date to 2026-04-27 or remove the parenthetical.

### 2.4 Cross-model validation date stamp

**Doc** (line 258): *"The skill is calibrated against Claude Opus 4.7 as the orchestrator. Cross-model validation on 2026-04-22 produced three tiers..."*

Date is from before the recent backing-model variance evidence. The Opus 4.7 / Sonnet 4.6 / Haiku 4.5 tiers refer to the **orchestrator** (Claude Code), not the **OpenRouter backing model**. This is correct but worth noting: orchestrator tiering is from 2026-04-22; backing-model variance evidence (E1 → E6.0 anchor shift on the same prompt) is from 2026-04-27 and is not yet documented in this section. The new design-intent paragraph below DOES discuss backing-model variance, so the doc isn't silent on it — but a forward pointer from §"Model Requirements" might help readers.

### 2.5 §"Step 9: Open Observatory" placeholder note in Step 5

**Doc** (line 672): *"### Step 5: Observatory Placeholder (deferred)"*

This is an artifact of pre-Step-6c reorg. Step 5 in `SKILL.md:302` is "Open Observatory." Step 6c is "Generate Memo." HOW_IT_WORKS.md has both as separate sections; the "placeholder" note is misleading. Either delete or rewrite to clarify the current step ordering.

---

## 3. Gaps — important things missing from the doc

### 3.1 The `is_malformed_verifier_response` helper is mentioned but not explained

**Doc** (line 574, the new design-intent paragraph): names the helper but doesn't explain *what* it does or *who* uses it.

**Why a gap**: future contributors who want to use it (e.g., for E6-style ablation tests) won't know it returns `True` on `{}` / non-dict / dict-missing-both-fields, and `False` on `{accepted: []}` / `{accepted: [...], rejected: []}`. The semantic boundary is non-obvious.

**Recommended fix**: add one sentence after the existing reference: *"`is_malformed_verifier_response(raw_payload)` returns True for schema-incomplete output (`{}`, non-dict, dict missing both list fields) and False for any deliberate empty-list response."*

### 3.2 `BoundaryCallMetadata` extended fields not flowing to `boundary_summary`

**Doc** (line 164, line 254): claims `BoundaryCallMetadata` carries telemetry that gets aggregated into `boundary_summary` for cost review.

**Code reality**: PR #58 added `finish_reason`, `raw_message_content`, and `temperature` to `BoundaryCallMetadata`, but `BoundaryCallTrace` (the per-call record that `summarize_boundary_calls` reads) and the `boundary_summary` aggregator don't yet expose those fields. Production runs persist `boundary_summary.providers` and `boundary_summary.models` (verified) but not the new fields.

**Why a gap**: the doc gives the impression that PR #58 wired full per-call observability into product runs. That's only partly true — the metadata exists at the call site (and is captured during E6-style scripts that read `client.last_call_metadata`), but does NOT flow to the run JSON.

**Recommended fix**: add a sentence to line 254 or line 574: *"PR #58's new fields (`finish_reason`, `raw_message_content`, `temperature`) live on `BoundaryCallMetadata` and are accessible via `client.last_call_metadata` for diagnostic scripts. They are not yet aggregated into `audit_summary.boundary_summary` — extending `BoundaryCallTrace` is a future observability improvement."*

### 3.3 The 2026-04-27 baseline evidence is not cited in the design-intent paragraph

**Doc** (line 574): cites `research/stability-runs/lane2-stability-experiments-2026-04-27/` generically, and `e6-prompt-test-residual.md` specifically.

**Missing reference**: PR #59's `e6-baseline-runs.json` and `e6-baseline-crosscase-runs.json` are the artifacts that ground the "lens lands differently per conversation" claim with cross-case numbers (CD 5/5 → 1/5 between sessions; pairwise Jaccard 0.700–0.713 across 3 cases).

**Recommended fix**: add to line 574 the file paths: *"...with bounded but real cross-run variance (typical pairwise Jaccard 0.6–0.8) and per-anchor surfacing rates that shift across sessions independent of prompt content (see `research/stability-runs/lane2-stability-experiments-2026-04-27/e6-baseline-runs.json` and `e6-baseline-crosscase-runs.json` for cross-case baselines)."*

### 3.4 The four-trigger framework for future Lane 2 work is buried in a single paragraph

**Doc** (line 576): the four valid triggers (user-visible failure / output-contract / KG correction / cross-lane bug) and the invalid trigger (precision-chasing) are listed inline as a single sentence.

**Why a gap**: this is the *most operationally important* part of the close-out — it tells the next contributor when to open Lane 2 work and when not to. Burying it in one sentence inside a multi-paragraph section makes it easy to miss.

**Recommended fix**: split the sentence into a bulleted list with each trigger on its own line. Optionally make it a small subsection labeled *"When to reopen Lane 2 prompt work"*.

### 3.5 `data/curated/reasoning_signals.json` referenced in the appendix but not introduced in body

**Doc** (line 853, file inventory): *"Companion lane recall fallback signals"*.

**Body**: Lane 2 recall description (line 561) doesn't mention reasoning_signals at all. Code uses both `knowledge_graph.json` and `reasoning_signals.json` for recall.

**Gap**: a reader following Lane 2's flow won't know reasoning_signals exists until they hit the appendix file inventory.

**Recommended fix**: one-line mention in §"Lane 2" Step 2 (Recall): *"Recall: keyword overlap on candidate `activation_trigger` strings + reasoning_signals fallback (`data/curated/reasoning_signals.json` — 217 keys) + optional embedding search."*

### 3.6 Step 6 "anchor treatment" three-vocabulary doesn't appear in HOW_IT_WORKS.md by name

**Doc**: HOW_IT_WORKS.md line 685–687 describes the three treatments but doesn't use the labels SKILL.md uses (*Primary pressure*, *Secondary lens*, *Set aside with a reason*).

**Code** (`SKILL.md:352`): defines the labels as the canonical product vocabulary.

**Gap**: terminology drift between HOW_IT_WORKS.md and SKILL.md. A reader switching between the two docs sees the same concept named differently.

**Recommended fix**: align HOW_IT_WORKS.md line 685–687 to use *Primary pressure*, *Secondary lens*, *Set aside with a reason* as bold-italicized labels (matching SKILL.md).

---

## 4. Out-of-date references and dead links

### 4.1 Stale research path in line 680

**Doc** (line 680): *"multi-run stability investigations (`research/lane2-architecture-research-frozen-2026-04-26` + `research/stability-runs/lane2-pathD-proxy-validation-2026-04-26`)"*.

**Reality**: those two paths exist on main, but they're from before the 2026-04-27 investigation cycle. The newer evidence (`research/stability-runs/lane2-stability-experiments-2026-04-27/`) is the more relevant citation for the "no single deterministic substrate fact predicts cross-run anchor stability" claim. Both should appear; the older paths are still valid but the new ones are richer.

**Recommended fix**: append the 2026-04-27 directory to the citation: *"(... + `research/stability-runs/lane2-stability-experiments-2026-04-27` for the harness-fix-era evidence)"*.

### 4.2 PR-number references are now wrong as numbers but right as identifiers

The doc uses "PR #37" (Lane 1 broadening) and "PR #44" (quote-repair hardening) and similar. These were correct at write time but the GitHub PR sequence has continued; the numbers are now fixed historical identifiers that match merged commits. No action needed — the references are stable.

### 4.3 Prior audit (`research/full-system-audit-2026-04-23.md`) is not cross-linked from HOW_IT_WORKS.md

The §"References" section at the end of HOW_IT_WORKS.md (line 833+) doesn't link to the prior audit. It's findable by `ls research/`, but a reader who wants the architectural overview won't know the audit exists.

**Recommended fix**: add to the references section: *"`research/full-system-audit-2026-04-23.md` — granular system audit (4 days before this version of HOW_IT_WORKS.md). Out of date on a few specifics; still useful as a depth complement to this doc."*

This audit (`research/full-system-audit-2026-04-27.md`) should also be added once committed.

---

## 5. Status of prior audit's open items (2026-04-23 → 2026-04-27)

The prior audit listed 12 known trade-offs (§9) and 12 audit gaps (§11). Status today:

### 5.1 Resolved or significantly improved

| Prior audit issue | Current status |
|---|---|
| §9.1 "Silent capture-fidelity risk" | Mitigated, not eliminated. `capture_manifest` + `capture_health` validators present. The deeper Phase 1 IR work (provenance-bearing turns) reduces but doesn't eliminate the risk — Claude is still the only witness. |
| §9.3 "Information loss in `_map_to_critique_request`" | **Resolved.** Phase 6 deleted `_map_to_critique_request` along with `CritiqueRequest`. Lanes now read from `Lane4Packet` projecting `ConversationIR`. |
| §9.6 "`--skip-revision` split" | Still present, unchanged. Two revision codepaths still exist. |
| §11.4 "Per-tendency adapter files (~20)" | Likely still present (Lane 1 deep-check infrastructure unchanged). Not re-audited. |
| §11.10 "Observatory" | Mentioned in HOW_IT_WORKS.md §"Step 9"; rendering layer still not deep-audited. |

### 5.2 New issues since 2026-04-23

These arrived during the 2026-04-26/27 Lane 2 investigation cycle:

| New issue | Status |
|---|---|
| Backing-model rotation under OpenRouter shifts verifier acceptance patterns. CD 5/5 → 1/5 between sessions on the same conversation, no prompt change. | Documented in HOW_IT_WORKS.md design-intent paragraph (line 574). Captured in metadata (`audit_summary.boundary_summary.models`). Treated as fact-of-life, not a bug to fix. |
| `require_list_of_dicts` silently normalizes missing `accepted`/`rejected` fields to `[]`, making schema-incomplete LLM responses look like deliberate empty rejections. | Detected by `is_malformed_verifier_response` (PR #58). Behavior of `require_list_of_dicts` itself unchanged — it's still permissive. |
| Track 1 v1 prompt restructure caused 80% schema-incomplete output. | Documented as anti-example in HOW_IT_WORKS.md line 576 + the design-intent paragraph. Reverted in PR #56. |

### 5.3 Still open from prior audit

| Prior audit gap | Status |
|---|---|
| §11.5 "Novelty scorer" | Not explored. |
| §11.6 "Higher-order composition compiler preview" | Not explored. |
| §11.7 "Intervention semantics modules" | Not explored. |
| §11.11 "`archive_run.py`, `render_memo.py`, `inspect_run.py` operational scripts" | `render_memo.py` verified for memo template structure in §1.3 above. The other two not deeply audited here. |
| §12.1 "Are 4 lanes the right decomposition?" | Open strategic question; HOW_IT_WORKS.md describes the current shape but doesn't claim it's optimal. |
| §12.2 "Are 222 mental models the right substrate?" | Open. |
| §12.4 "Anti-echo policy: helping or hurting quality?" | Open. The Lane 2 design-intent paragraph mentions "Lane 1 anti-echo dropping good Lane 2 anchors silently" as a future-trigger condition — implicitly acknowledging this is a real risk surface. |

---

## 6. Recommended doc updates

In priority order (load-bearing first):

1. **§"Lane 2" line 561** — fix "15-20 candidate mental models" → "up to 60 candidate mental models" (drift §2.1).
2. **§"Lane 2" line 557** — fix "2-3 OpenRouter calls" → "2 OpenRouter calls" (drift §2.2).
3. **§"Lane 2 design intent" line 576** — split the four-trigger framework into a bulleted list, optionally as a labeled subsection (gap §3.4). This is the most operationally important part of the close-out.
4. **§"Lane 2" Step 2 line 561** — one-line mention of `reasoning_signals.json` fallback (gap §3.5).
5. **§"Lane 2 design intent" line 574** — explain `is_malformed_verifier_response` semantics and clarify `BoundaryCallMetadata` new-field flow status (gaps §3.1 + §3.2).
6. **§"Step 6: Update Your Position" line 685** — align treatment vocabulary with SKILL.md's labels (*Primary pressure* / *Secondary lens* / *Set aside with a reason*) (gap §3.6).
7. **§"References" appendix** — cross-link the two audits (out-of-date §4.3).
8. **§"Architecture / Current State"** — bump date stamp or remove the parenthetical (drift §2.3).
9. **§"Step 5: Observatory Placeholder"** — clarify against current Step ordering (drift §2.5).
10. **§"Lane 2 design intent" line 574** — add explicit citation of PR #59 baseline JSONs (gap §3.3).

Items 1–6 are the high-value fixes. Items 7–10 are polish.

These are all single-sentence or single-paragraph edits. Total impact: maybe 30–50 lines of doc change across HOW_IT_WORKS.md.

---

## 7. What this audit did NOT cover

- **SKILL.md beyond anchor-naming verification.** The 766-line skill orchestration contract has many specific instructions for Claude. Spot-checked anchor-naming invariant (§1.3); did not pass over the rest.
- **Per-tendency deep-check adapters.** ~20 files with similar patterns; unchanged from prior audit's coverage.
- **Pilot bridges (authority, stress, overoptimism).** Status unchanged from prior audit; not re-audited.
- **Activation matcher internals.** `activation_matcher.py` not read line-by-line.
- **Observatory rendering layer.** Step 9 produces visualizations; rendering code path not audited.
- **Production cost / latency**. Not measured here.
- **Phase 5/5.5/5.7/5.8 specialist code paths**. They exist (`engine/system_b/stance_extraction.py`, `live_constraints_extraction.py`, `dropped_threads_extraction.py`); the pipeline calls `construct_conversation_ir` without specialists by default. Specialist promotion criteria documented in HOW_IT_WORKS.md §"Evolution".
- **Bullshit Index lane**. Operates on full vanilla_answer; mentioned but not deeply audited. Its presence in `result.json` (`bullshit_profile`) confirms it still runs.
- **Step 7 Pressure-Check Sub-Agents and Step 8 Pressure-Check Comparison.** Status unchanged; persistence verified via `gap_check` field in result.json.

---

## 8. Bottom line

`HOW_IT_WORKS.md` is in good shape. The recent additions (PRs #43–#60) are accurately reflected, the architecture migration narrative is current, and the design intent paragraph for Lane 2 (PR #60) lands correctly with cited evidence.

**Three load-bearing drift items**:
1. Lane 2 candidate count "15-20" → "up to 60" (line 561)
2. Lane 2 call count "2-3" → "2" (line 557)
3. Four-trigger framework buried in a single sentence — break it out (line 576)

**Three load-bearing gaps**:
4. `is_malformed_verifier_response` named without explanation (line 574)
5. `BoundaryCallMetadata` new-field flow status not stated (line 254 or 574)
6. SKILL.md's anchor-treatment vocabulary labels not used in HOW_IT_WORKS.md (line 685)

These six fixes are the audit's actionable output. Each is single-paragraph or single-sentence work. None require code change.

The system itself: Lane 2 closed, lens-not-precision committed in product surface (line 569–576), backing-model variance acknowledged as design fact, harness instrumentation in place to detect future malformed-output regressions, KG correction (Track 2 Checklists bullet 4) retained as the pattern of justified Lane 2 work going forward.
