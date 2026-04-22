# Extraction Contract Observations — 2026-04-22

## Status

**Cycle-2 Track A input. DO NOT ACT IN CYCLE 1.**

The Cycle-1 priority order from `research/llm-decomposition-handover.md` Section 0g and 6.0 stands: D-skill → stability harness → C-step1-3 → B. Track A (extraction decomposition) is HELD pending post-B harness evidence.

These observations are filed so they feed the Cycle-2 decision about whether to unhold Track A and — if so — which shape it should take. They complement the Pass 1 analysis in the handover's Section 3.5; they do not duplicate it.

## Why this document exists

The 2026-04-22 session was kicked off to continue Cycle-1 work (D-skill first). The session drifted into front-of-pipeline analysis that is Track A preparatory work. That work was out of plan and is not being executed. The observations themselves, however, surface failure modes that were not captured in the handover and should not be lost.

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

## Cross-references

- Handover: `research/llm-decomposition-handover.md` — Section 0g (Cycle-1 sequence), Section 3.5 (Marcus evidence, Pass 1 + Lane 2 focus), Section 6.0 (cost/gain ledger), Section 6.2 (Track A HELD rationale).
- Step 1 lives in `SKILL.md` — same file Track D-skill targets.
- Step 2 lives in `scripts/run_extract.py` — Track A target when unheld.
- Quote fabrication mechanism: `scripts/run_extract.py:473-493` — literal substring only, no fuzzy fallback, soft warning.
