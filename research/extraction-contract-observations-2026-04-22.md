# Extraction Contract Observations — 2026-04-22

## Status

**Cycle-2 Track A design document. DO NOT IMPLEMENT IN CYCLE 1.**

Cycle-1 (D-skill → stability harness → C-step1-3 → Track B) is complete as of commit `54932b8` on 2026-04-22. This document is the design input for Cycle-2 Track A (extraction decomposition) and is structured in four parts:

1. **Observations** — what the Marcus 3-run qualitative reread surfaced (original scope).
2. **Mode C drift measurement** — quantitative extraction-drift evidence from the new `scripts/stability_check.py --drift` mode (added 2026-04-22 during Phase 3).
3. **Extraction contract spec (normative)** — field-by-field rules Track A should implement against.
4. **Silent-degradation audit** — every silent-degradation mode observed across the session's runs, with severity and proposed surfacing.

Parts 1–2 are descriptive (what we see). Parts 3–4 are normative (what we want). Any Track A implementation should pass the Part 3 spec and close the Part 4 gaps.

## Why this document exists

The 2026-04-22 session began as Cycle-1 work (D-skill first). Early in the session the analysis drifted into front-of-pipeline observations that were out of plan. Those observations were filed rather than acted on, and the session continued to complete Cycle-1 as scheduled. Phase 3 (local tooling + docs, post-Cycle-1) then extended this document with Mode C measurement evidence and the normative contract spec — the form Track A needs before it's worth shipping.

---

## What the front of the pipeline currently does

### Step 1 — Claude-side (SKILL.md §102-136)

- Claude extracts user messages and assistant prose from its own context into `/tmp/lolla_{run_id}_conversation.txt`.
- Format: `[Turn N] USER:` / `[Turn N] ASSISTANT:` headers + `CONVERSATION: N turns, X user, Y assistant` preamble.
- Excludes tool calls, tool results, system messages, file contents.
- Documented truncation rule for >100-turn conversations: keep first 3 + last 15 turns.
- **Claude is the only witness.** Once the `.txt` is written, the original context is gone. There is no source of truth to compare the capture against.

### Step 2 — `scripts/run_extract.py`

- Truncates at `MAX_CONVERSATION_CHARS = 80_000` (different gate from SKILL.md's "100 turns" — turn-count and char-count rules can disagree).
- Validates capture self-consistency via `capture_manifest` (actual vs declared turn counts, char length) and `capture_health` (good / degraded / critical / unknown). `degraded` and `critical` do NOT gate the run — the output still reports `status: "ok"`.
- One OpenRouter call does 6–7 objectives in one prompt: strategic-gate + `decision_situation` + `live_constraints` + `synthesized_position` + `reasoning_passages` + `original_framing` + `dropped_threads`.
- Literal-substring check on `reasoning_passages` post-extraction. Soft warning; never fails the run; never surfaces to the user in chat.
- `_map_to_critique_request` is deterministic: 6 fields → `query` + `vanilla_answer`.
- `vanilla_answer` when assistant_text > 200 chars: `synthesized_position` preamble + full assistant text (40K cap). Downstream lanes therefore receive both the LLM's summary AND every verbatim assistant turn concatenated.

---

## Novel observations from Marcus 3-run reread (extraction layer, not Pass 1)

Reading `/tmp/lolla_20260421T{144534,162225,172513}Z_extraction.json` at the Step-2 field level:

| Field | Stability across 3 runs |
|---|---|
| `decision_situation` | **Verbatim identical.** No drift. |
| `live_constraints` | 4 / 5 / 5. Run 1 folded "precedent risk" into Turn-3 reasoning rather than a discrete constraint. |
| `synthesized_position` | **Shape drift.** Run 1 extracts as "user's A/B choice"; Runs 2/3 extract as "advisor's prescription." Same conversation, different stance. |
| `reasoning_passages` | 5 / 6 / 6. **Run 2 had one paraphrased-not-literal quote**, soft-flagged, invisible to the user. |
| `original_framing` | Same tension identified; wording varies. |
| `dropped_threads` | 3 / 2 / 2. **Inverse-correlated with `live_constraints` count** — total information preserved; taxonomy assignment drifts. |

### Three failure modes these runs surface

**1. Ontology-level ambiguity in `synthesized_position`.** The shape-shift happens on a clean, single-stance conversation — Marcus is 7 turns, no restarts, no position pivots, no tool calls. The extraction prompt says "the LLM's latest/most developed recommendation" — but "most developed" is undefined when the assistant's final posture is "here are your options, pick one" vs "I recommend X" vs "the answer depends on whether you think of this as partner-or-employee." Different LLM samples resolve the ambiguity differently.

Decomposition into specialists *preserves* this ambiguity unless the contract itself is tightened. This is not a prompt-wording problem — it is a contract-definition problem.

**2. Constraint / dropped-thread taxonomy is fuzzy at edges.** A concern raised by the user's wife in Turn 3 that the AI briefly addresses and moves past is legitimately *both* a dropped thread AND a situational constraint. The prompt has no tie-break rule. Runs disagree on the assignment; the total information is preserved; but the `CritiqueRequest.query` bullet lists look materially different to downstream lanes because `live_constraints` and `dropped_threads` are formatted differently when `_map_to_critique_request` collapses the 6 fields into 2.

**3. Capture-faithfulness is unverifiable.** Claude writes the `.txt` from its own context. There is no source-of-truth comparison. If Claude paraphrases a user turn while transcribing, the extractor treats the paraphrase as ground truth. `capture_manifest` only checks header-vs-body self-consistency, not fidelity to the original conversation.

This is specifically relevant to Track D-skill: Step 1 lives in SKILL.md, which IS the file D-skill targets. The capture-fidelity concern and the Step 6 revision concern both sit in the same file and will be addressed by D-skill work (see below).

---

## Conversation-shape taxonomy (agnostic)

Marcus is the easy case. The extractor needs to be robust across at least these shapes. Each column names what that shape stresses in the current contract:

| Shape | Example | What it stresses |
|---|---|---|
| Short (1–3 turns) | User asks, AI answers, short follow-up | `reasoning_passages` sparse; `synthesized_position == only response`; Lane 2 fingerprinting thin |
| Clean linear (Marcus) | Clear decision, clean back-and-forth, one thread | The easy case; still drifts as shown |
| Long (50–200 turns) | Extended exploration, many phases | 80K truncation fires; "first 3 + last 15" drops the middle where the decision crystallized |
| Multi-thread | User pivots A → B → back to A | Extractor picks one thread; may pick the unfinished one |
| Repeat-question | User asks the same thing 3 times, different phrasings | Which phrasing is `original_framing`? Does AI position drift across reiterations collapse into one `synthesized_position`? |
| Suggestion-driven | User proposes an answer and asks AI to critique | Whose position is being audited — user's proposal or AI's critique? |
| Exploratory / not-yet-deciding | User thinking out loud | Strategic-gate may flip; no clear "position" to synthesize |
| Code-adjacent strategic | Debugging with architecture tradeoffs woven in | Strategic-gate may miss it; the decision is buried in technical exchange |
| Compound | Hire + pricing + product direction entangled | Extractor collapses into one `decision_situation`; others become phantom constraints or dropped threads |
| Messy capture | Claude's own capture lost turns, header wrong, truncated noisily | Header-vs-body mismatch warns but doesn't stop the run |

---

## What the extraction contract should probably produce (positive statement, Cycle-2 inputs only)

Working backwards from what each lane actually needs, agnostic to conversation shape:

- **Lane 1 (triage)** needs: the specific claims the AI made, the constraints that were live when each claim was made, and the omissions. Does NOT need full assistant prose concatenated with a summary.
- **Lane 2 (companion)** needs: literal verbatim passages to fingerprint against the 222-model corpus. Fabricated quotes break it.
- **Lane 3 (frame)** needs: how the *question* was posed — assumed fixed, excluded perspectives. Not the conversation's evolved framing.
- **Lane 4 (coverage)** needs: the decision situation with enough specificity that the MECE dimensions can be matched.

Which implies the extraction contract probably wants, as Track A design inputs (not shipping specs):

- Faithful, **auditable** capture — traceable to source turns, not just self-consistent.
- A **decision state model** instead of free-text synthesis: latest stance + superseded stances + when each entered.
- **Constraint timeline**, not a flat list: which constraint was live when each stance was made.
- **Tie-break rules** between constraints, dropped threads, and framing assumptions.
- **Verbatim passages as first-class output**, not folded into `vanilla_answer` alongside full assistant text.
- **Conversation-shape fingerprint** as metadata: turn count, position-shift count, thread-pivot count, truncation-applied flag, capture-fidelity grade.

Decomposition as currently specified in Track A (5 specialists, each reading the full transcript) preserves the contract's ambiguities unless the contract is redefined first. The decision for Cycle 2 is therefore not just "decompose" but "redefine + decompose" vs "decompose as-is." Harness evidence from Cycle-1 B and C-step1-3 will inform which is justified.

---

## Non-overfitting caveat

All of the above is based on one conversation (Marcus) with three runs. The observations are directional, not definitive.

Before acting on any of this in Cycle 2, feed 2–3 varied conversations from the taxonomy above through today's extractor and check whether the same failure modes surface. Without that, Track A risks being designed around Marcus's idiosyncrasies. Cheap, fast, should be the first thing Cycle 2 does if Track A is unheld.

---

## Mode C drift measurement — 2026-04-22

The qualitative "stability across 3 runs" table above was based on matched pairings across three live audits of the same conversation on consecutive days. The harness's new `--drift` mode (shipped in Phase 3, `scripts/stability_check.py`) measures the same question quantitatively by re-running `run_extract.py` N times on a single `conversation.txt`, holding Claude's Step 1 capture constant so only extractor sampling contributes to the drift.

**First run, N=3 on `lolla_20260422T113930Z_conversation.txt` (Run 6's Marcus capture):**

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.256 | 0.220 | — |
| `original_framing` | similarity | 0.312 | 0.184 | — |
| `synthesized_position` | similarity | 0.277 | 0.178 | — |
| `live_constraints` | jaccard (exact text) | **0.000** | 0.000 | 0.000 |
| `reasoning_passages` | jaccard (exact text) | 0.389 | 0.250 | — |
| `dropped_threads` | jaccard (exact text) | **0.000** | 0.000 | 0.000 |
| `_quote_validation.fabricated` | count per run | 0 / 0 / 0 | — | — |

**How to read these:** similarity is `difflib.SequenceMatcher` ratio (character-level). Jaccard is on normalized exact item text (strip + lowercase). Semantic overlap is not measured — two constraints that describe the same thing with different words count as distinct. A Jaccard of 0 does not mean "no shared concept" — it means "no exact-text match."

### The `live_constraints` / `dropped_threads` finding

Jaccard = 0.0 on both list fields is the loudest quantitative signal in the dataset. Spot-checking the first constraint from each of the 3 re-extractions:

```
drift0 [0]: "Marcus responsible for 40% of technical capability, built core internal tooling,
             clients love him, 35 engineer..."
drift1 [0]: "Marcus responsible for 40% of technical capability, built core internal tooling,
             clients love him, 35 engineer..."
drift2 [0]: "Marcus responsible for 40% of technical capability, built core internal tooling,
             clients love him, engineering..."
```

These are semantically the same constraint phrased differently in the last few words. The *concept* is stable; the *exact text* diverges. The extraction contract currently has no canonical form for constraint text — the extractor paraphrases the tail of each item every run.

### What this means for Track A

- **Semantic decomposition alone will not fix this.** If Track A splits the monolithic extraction call into 5 specialists, each specialist will still paraphrase-drift on its free-form output unless the contract defines canonical form.
- **The contract needs canonicalization**, not just decomposition. Either (a) add a `canonical_key` to list items so identity survives paraphrase, or (b) define terse canonical phrasing rules, or (c) add a post-extraction semantic-similarity metric (embedding cosine on constraint texts) instead of exact-text Jaccard. The spec below proposes (a).
- **`reasoning_passages` Jaccard 0.389 is the highest list-field score** — expected, because those are supposed to be literal substrings of the transcript. That's the only list field with a canonical-form rule today. The other list fields should follow the same pattern.

### What Mode C is and isn't

- IS: cheap (~$0.01 per N=3 case), hold-extraction-variance-constant diagnostic.
- IS NOT: a production stability gate. Run on demand, on selected conversations, during Track A design.
- IS NOT: a semantic-similarity measure. Character-level Jaccard treats paraphrase as drift. That's a feature for surfacing canonicalization gaps; it would be a bug if we were trying to measure "did we capture the same meaning."

Before Track A ships, re-run `--drift` with N=5 and the new contract-enforced extractor. Target metrics are in the spec below.

---

## Extraction contract spec (normative, Cycle-2 Track A design input)

This section formalizes the extraction contract. It is NOT the current behavior of `scripts/run_extract.py`. It is the target shape Track A should implement against.

### Global requirements

- **Capture fidelity.** Step 1 must emit a `conversation.txt` that's byte-faithful to the source turns. Any truncation or paraphrase is a contract violation. Current: Claude writes from memory with no source-of-truth comparison. Required: either (a) Claude quotes source turns verbatim with an explicit truncation marker when content is dropped, or (b) the capture process is pulled upstream to a mechanical source.
- **Truncation transparency.** When the 80K-char cap or ">100 turns" rule fires, the extraction output MUST include `capture_manifest.truncation_applied: true` and `capture_manifest.truncation_reason: str`. Current: silent.
- **Status gating.** `capture_health: "critical"` MUST produce `status: "capture_critical"`, not `status: "ok"`. A run with >50% assistant turns missing is not a valid audit. Current: `critical` still returns `ok`.
- **Hard-fail on quote fabrication.** Any passage failing literal-substring validation MUST return `status: "extraction_degraded"`. Current: soft warning only; downstream Lane 2 silently degrades.

### Field-by-field

#### `decision_situation` (required, string, 1 sentence)

- Neutral, third-person problem statement of the core decision.
- Canonical form: *"[Whether|How|When] [action] [subject], given [situation summary], with stakes [brief]."*
- MUST NOT include: founder personal pronouns, emotive adjectives, speculative projections about outcomes.
- Rationale: eliminates the "A founder-CEO of…" drift observed in Mode C drift1 (similarity 0.256 driven primarily by opening-phrase variation).

#### `live_constraints` (required, list of `Constraint`, 3–8)

Each `Constraint`:

| Field | Type | Notes |
|---|---|---|
| `canonical_key` | slug | **NEW.** Machine-stable identifier (e.g., `marcus-comp-below-market`). Enables cross-run matching independent of phrasing. Absent today. |
| `constraint` | string | Terse noun phrase + state, ≤120 chars. E.g., "Marcus's comp $225K (below market $220-250K range)" not "Marcus's current compensation is $225K total, which is slightly below the market range…" |
| `status` | enum | `active` \| `dropped` \| `modified` |
| `weight` | enum | `structural` \| `situational` |
| `introduced_turn` | int | Which turn the constraint entered the conversation. |

**Tie-break with `dropped_threads`:** a concern raised by a third party (user's wife, lawyer, etc.) that the AI addressed briefly is a `Constraint` with `weight: situational`, NOT a `dropped_thread` — unless the user explicitly abandoned it in a later turn. The tie-break rule: if the user returned to it, it's live; if never revisited and never resolved, it's dropped. Current: no rule; drift across runs.

#### `synthesized_position` (required, `Position` object)

Canonical structure (not free text):

```json
{
  "stance": "recommends_action" | "presents_tradeoffs" | "declines_to_recommend",
  "latest_stance_text": "...",
  "superseded_stances": [
    {"turn": N, "stance_text": "...", "superseded_reason": "..."}
  ],
  "is_ambiguous": true | false
}
```

- **Temporal anchor:** `latest_stance_text` = the stance expressed in the FINAL assistant turn. NOT "most developed." This is a mechanical rule that eliminates the current "most developed" ambiguity (which Runs 1–3 resolved three different ways: "user's A/B choice" vs "advisor's prescription" vs "third-person summary").
- `superseded_stances` records prior positions the AI held but abandoned during the conversation.
- `is_ambiguous` flags when the final turn presents tradeoffs rather than a recommendation.
- Rationale: Mode C `synthesized_position` similarity 0.277 is driven by the free-text prompt's ambiguity. A mechanical rule (final assistant turn) + structured stance enum collapses that variance.

#### `reasoning_passages` (required, list of `Passage`, 3–8)

Each `Passage`:

| Field | Type | Notes |
|---|---|---|
| `text` | string | LITERAL substring of `conversation.txt`. 50–500 chars. |
| `turn` | int | Source turn. |
| `role` | const | `"assistant"` (user passages are not reasoning_passages by definition) |
| `move_type` | enum | `leap` \| `dismissal` \| `assertion_without_evidence` \| `framing_shift` \| `closure` \| `inversion` \| `comparison` |

**Hard-fail rule:** if any `text` fails literal-substring validation against `conversation.txt`, the run returns `status: "extraction_degraded"` with the offending passage in `_quote_validation.fabricated_passages`. Lane 2 companion fingerprinting depends on literal quotes; soft-flagging is insufficient.

Current behavior: soft warning; run returns `status: ok`; Lane 2 silently degrades.

#### `original_framing` (required, string, 1–2 sentences)

- How the HUMAN posed the question IN THE FIRST TURN. Not conversation-evolved framing.
- MUST describe: what was assumed fixed, what alternatives were explicitly excluded, what lens the human brought.
- MUST NOT describe: framing shifts later in the conversation (captured in `synthesized_position.superseded_stances` instead).
- Rationale: Mode C `original_framing` similarity 0.312 is driven partly by extractor conflating first-turn framing with conversation-evolved framing. Anchor to first user turn mechanically.

#### `dropped_threads` (required, list of `Thread`)

Each `Thread`:

| Field | Type | Notes |
|---|---|---|
| `canonical_key` | slug | **NEW.** Cross-run identity. |
| `thread` | string | Terse phrasing, ≤120 chars. |
| `raised_by` | enum | `user` \| `assistant` |
| `raised_turn` | int | |
| `status` | enum | `never_addressed` \| `acknowledged_then_dropped` \| `resolved` |
| `superseded_by` | string | Optional, when `status == acknowledged_then_dropped`. |

Tie-break with `live_constraints`: see Constraint section.

### Mode C pass criteria for Track A shipping

Before Track A can ship, run `--drift` with N=5 on the Marcus conversation under the new contract-enforced extractor. Targets:

| Field | Current (N=3) | Target (N=5 post-Track-A) |
|---|---|---|
| `decision_situation` similarity | 0.256 | ≥ 0.85 (canonical form collapses paraphrase drift) |
| `synthesized_position.stance` Jaccard (on enum) | — | 1.0 (mechanical rule on final assistant turn) |
| `synthesized_position.latest_stance_text` similarity | 0.277 | ≥ 0.70 |
| `live_constraints` Jaccard on `canonical_key` | n/a (field absent) | ≥ 0.80 |
| `reasoning_passages` Jaccard on `text` | 0.389 | ≥ 0.50 (still LLM-driven selection) |
| `_quote_validation.fabricated` count | 0/0/0 | 0 always (hard-fail enforced) |
| `original_framing` similarity | 0.312 | ≥ 0.70 |
| `dropped_threads` Jaccard on `canonical_key` | n/a | ≥ 0.70 |

If Mode C shows these gains without a catastrophic cost bump (Track A is budgeted at +$0.015–0.025/run per the handover), Track A ships. If not, decomposition is preserving the contract's ambiguities and a different approach is needed.

---

## Silent-degradation audit — 2026-04-22

Failure modes where the current skill returns `status: ok` (or otherwise appears successful) but the audit is materially degraded. Each item: current behavior, observed frequency across this session's 7+ Marcus runs, impact, proposed surfacing, severity.

### 1. Quote fabrication silent-flag

**Current:** `_quote_validation.fabricated_passages` lists non-literal quotes; run reports `status: "ok"`; user never sees the warning in chat.
**Observed:** Run 2 (`lolla_20260421T162225Z`) had 1 fabricated passage of 6; Runs 1, 3, 4, 5, 6 and Mode C drift 0/1/2 all zero. ~14% of runs affected in this sample.
**Impact:** Lane 2 fingerprint expects literal substrings; a fabricated passage produces fingerprint moves that verification can't anchor → silent Lane 2 degradation.
**Proposed:** hard-fail at the extraction layer. Covered in the spec above.
**Severity:** **high.**

### 2. 80K-char truncation silent

**Current:** `MAX_CONVERSATION_CHARS = 80_000` (`run_extract.py:78`). When content is dropped, extraction proceeds without flagging the truncation.
**Observed:** never triggered in Marcus runs (~25K chars). Would fire on long conversations (~50–200 turns).
**Impact:** middle-of-conversation turns lost silently; audit runs on partial context.
**Proposed:** add `capture_manifest.truncation_applied: bool` and `.truncation_reason: str`. Surface in Step 4 chat via the `run_health` mechanism shipped in `54932b8`.
**Severity:** medium (low frequency, high per-incident impact).

### 3. Capture-health `degraded` / `critical` doesn't gate status

**Current:** `capture_health: critical` (>50% assistant turns missing per header-vs-body check) still returns `status: "ok"`. Only `is_strategic: false` blocks the run.
**Observed:** every run in this session had `capture_health: good` — the critical path is untested in production.
**Impact:** a genuinely broken capture would produce an extraction that downstream lanes treat as authoritative.
**Proposed:** covered in the spec above (global requirements).
**Severity:** medium.

### 4. Cross-model orchestrator degradation

**Current:** no pre-flight check on the Claude model running the skill. Below Opus 4.7, silent quality degradation; Haiku 4.5 drops persistence steps entirely.
**Observed:** Haiku run (`20260422T123205Z`) skipped Steps 6b / 6c / 7 / 8b while writing plausible output including a fake Pressure Check. Sonnet run (`20260422T130506Z`) completed all steps but leaked 3 machinery terms in `revised_answer`.
**Impact:** Observatory shows incomplete runs (Haiku); memo blank (Haiku); machinery terms in user-facing text (Sonnet).
**Proposed (partially shipped):** Model Requirements section in SKILL.md (shipped in `54932b8`) documents the floor. Next: machine-enforceable pre-flight check in the preamble bash that detects the running Claude model and warns/fails when below Sonnet.
**Severity:** **high** for Haiku; low-to-medium for Sonnet (cosmetic leaks).

### 5. Lane 3 frame-element validation drops silently

**Current:** `run_pipeline.py` logs `"Frame element evidence_quote not found in query, skipping: ..."` to stderr but doesn't surface it in the result JSON or user-facing output.
**Observed:** fires in most Marcus runs (1–2 elements dropped per run). Run `lolla_20260422T095719Zstab2` had all frame elements dropped → empty Lane 3.
**Impact:** Lane 3 can produce 0 reframings with no signal to the user; reads as "frame is clean" rather than "frame extraction failed validation."
**Proposed:** add `dropped_frame_elements_count` to `run_health`; fold into a material issue via the `run_health` mechanism if all elements dropped. Surface in Step 4 chat (shipped `54932b8` will pick it up automatically).
**Severity:** medium.

### 6. Phrasing-rule drift on revised_answer (orchestrator-below-Opus)

**Current:** SKILL.md Step 6 bad-terms list is a text instruction; relies on Claude's instruction-following tightness. Opus 4.7 follows; Sonnet 4.6 leaks 2–3 terms per `revised_answer`.
**Observed:** Sonnet run `20260422T130506Z` revised_answer contained `"sub-agents"`, `"the audit changes"`, `"nothing in the audit changes that"` — all in the bad-terms list, all leaked.
**Impact:** machinery terms visible in user-facing output.
**Proposed:** code-enforced validator. Post-Step-6b, lint `revised_answer` against the bad-terms list; if hits, surface as a `run_health` issue OR retry Step 6 with an explicit correction prompt. Not in scope for Phase 3; Cycle-3 candidate.
**Severity:** low (cosmetic, not doctrine violations).

### Priority stack (severity × feasibility)

1. **Quote fabrication hard-fail** (#1) — one-line behavioral change in `run_extract.py:485`. High-severity, low-effort. **Ship next.**
2. **Capture-critical gating** (#3) — one-line change, prevents catastrophic silent runs. Low-effort.
3. **Truncation transparency** (#2) — small `capture_manifest` extension; plus cheap SKILL.md surfacing via the already-shipped `run_health` block.
4. **Cross-model pre-flight** (#4) — check Claude model at Step 0, fail/warn below threshold.
5. **Lane 3 dropped-element count** (#5) — small `run_health` extension.
6. **Post-Step-6b bad-terms validator** (#6) — new component; defer to Cycle 3.

None of these are Cycle-1 commitments. They're the Track A / post-cycle polish backlog, prioritized by severity and feasibility.

---

## Cross-references

- Handover: `research/llm-decomposition-handover.md` — Section 0g (Cycle-1 sequence), Section 3.5 (Marcus evidence, Pass 1 + Lane 2 focus), Section 6.0 (cost/gain ledger), Section 6.2 (Track A HELD rationale).
- Step 1 lives in `SKILL.md` — same file Track D-skill targets.
- Step 2 lives in `scripts/run_extract.py` — Track A target when unheld.
- Quote fabrication mechanism: `scripts/run_extract.py:473-493` — literal substring only, no fuzzy fallback, soft warning.
