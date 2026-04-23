# LLM Decomposition — Session Handover

Research date: 2026-04-17
Last updated: 2026-04-21 (revised after Marcus 3-run stability evidence + cost/gain rationalization)
Scope: **`lolla-skill` (LIVE — priority).** `Lolla-system-b` has a different, non-live extraction path and is out of scope here.
Status: **Audit COMPLETE. Evidence base UPGRADED (three runs of the Marcus case, 2026-04-21). Priority order REVISED on cost/gain grounds. Stability harness NOT YET BUILT. Zero code changes yet. Next: ship a short first cycle (D-skill → harness → C-step1-3 → B), measure, then decide whether A / C-extended / fingerprint-decomposition are worth their cost.**

---

## 0. CURRENT STATE — READ THIS FIRST

**We audited every LLM call in the Lolla pipeline under the Sully "context engineering vs iteration" lens. Two calls are already well-shaped. Six are overloaded. The work is to decompose the overloaded ones — not to rebuild the architecture.**

**Then on 2026-04-21 we pulled three runs of the same live conversation (the "Marcus partnership" case) out of `/tmp` and compared them. They disagreed with each other in exactly the places theory predicted — different tendencies, different anchor models, different synthesized positions, all with `run_health: healthy`. That evidence, plus a hard cost/gain pass, re-ordered the work.**

This section is the authoritative summary. Sections 1-13 contain the full plan, evidence, and junior-developer instructions. **If you only read one section, read 0. If you read two, also read Section 3.5 (Marcus evidence) and Section 3.6 (the doctrine behind this plan).**

### 0.0 — TWO SYSTEMS, ONE IN SCOPE

Lolla has two repos that sometimes share code but differ at the runtime boundary:

- **`lolla-skill`** — the LIVE skill. Uses OpenRouter for every LLM call. User-facing flow is `conversation → run_extract.py → (query, vanilla_answer) → 4-lane pipeline → 4 cards → Claude synthesizes the revision itself`. **This is the priority.**
- **`Lolla-system-b`** — authoring + curation + compilation infrastructure. Has a separate, richer conversation-extraction path used for evaluation and curation. NOT user-facing. NOT in scope for this plan.

**Key consequence for this plan:** the skill's `run_pipeline.py` is invoked with `--skip-revision`, which means `testing_harness.py build_revision_prompt` is **not called in the live skill**. Claude (the skill host) produces the revised position itself in Step 6 using the 4 cards as input. So the "revision" LLM call (#12 in Section 4) is **not a live skill concern**. It remains in the inventory for completeness and as a system_b improvement candidate.

Every track below is scoped to the **live skill path**. System_b has parallel opportunities that are explicitly deferred.

### 0a. Why this plan exists

Sully.ai published a piece arguing that context engineering and iteration are **substitutes, not complements**: monolithic agents juggling 6-8 concurrent cognitive tasks degrade per-task accuracy, and the fix is to narrow each call's objective and input, not to iterate on prompt wording at the same complexity. The user asked: does this apply to Lolla? Audit says yes, in concentrated places.

Lolla's core doctrine is already "LLMs at the probabilistic edges, curated knowledge in the deterministic middle." This plan extends that doctrine **inside the LLM boundary itself**: each LLM call should have one semantic objective, narrow input, and composable output — the same shape Pass 2 and companion fingerprint already have.

**But we are not trying to make Lolla deterministic.** Messy conversations will always produce some variance; that's accepted, not a bug. What we *are* trying to do is cut each LLM call's load — both *input* (how much it reads) and *obligations* (how many jobs it does) — until the call can arrive at the same *structural read* of the same input most of the time. That's the doctrine section 3.6 expands on. The handover reader should internalize it before picking a track: **load is the lever; variance is a cost we accept, not a principle we embrace.**

### 0b. What we audited

Every LLM boundary in the pipeline, 12 calls total. Source files read:

- `scripts/run_extract.py` — upstream extraction
- `engine/system_b/prompts.py` — Pass 1 triage (Lane 1)
- `engine/system_b/deep_checks.py` — Pass 2 deep check (Lane 1)
- `engine/system_b/companion_routing.py` — Lane 2 fingerprint + verification
- `engine/system_b/frame_pressure.py` — Lane 3
- `engine/system_b/structural_coverage.py` — Lane 4 (question classification, dimension detection, gap question generation)
- `engine/system_b/bullshit_index.py` — auditor
- `engine/system_b/testing_harness.py` — revision
- `engine/system_b/prompt_versioning.py` — the 5 officially-versioned prompts
- `engine/system_b/pipeline.py` — orchestration (Pass 2 parallel fan-out)

### 0c. The full LLM call inventory (12 calls)

| # | Stage | Call | Objectives | Input shape | Overload |
|---|---|---|---|---|---|
| 1 | Upstream | `run_extract.py:111` extraction | 6–7 (classify + decision + constraints + passages + framing + threads + drops) | full transcript | **HIGH** |
| 2 | Lane 1 Pass 1 | `prompts.py` pass1_triage | 25 tendencies + ~12 critical rules + ~11 confusion guardrails | extracted text | **HIGH** |
| 3 | Lane 1 Pass 2 | `deep_checks.py:230` pass2_deep_check | **1 tendency**, runs in parallel | narrow slice | **MODEL** (already good) |
| 4 | Lane 2 | `companion_routing.py` fingerprint | 1 (abstract reasoning moves, no model names) | revised answer | **MODEL** (already good) |
| 5 | Lane 2 | `companion_routing.py` recall_candidates | *deterministic* (not LLM) | fingerprint → token overlap | — |
| 6 | Lane 2 | `companion_routing.py` verification | 1 + ~40-line guardrail stack, ≤60 candidates | anchored bundle | **HIGH** |
| 7 | Lane 3 | `frame_pressure.py` frame_extraction | extract + classify, ~10 calibration rules + 9 negatives | raw text | MEDIUM |
| 8 | Lane 4 | `structural_coverage.py` question_classification | 1 (light) | question only | LOW |
| 9 | Lane 4 | `structural_coverage.py` dimension_detection | 4 (dims + coverage + materiality + cap) | answer + question | MEDIUM |
| 10 | Lane 4 | `structural_coverage.py` gap_question_generation | 1 + 6 design rules | covered/missing dims | LOW |
| 11 | Auditor | `bullshit_index.py` per-passage | 4 subtypes (empty / paltering / weasel / unverified) | 1 passage | MEDIUM |
| 12 | Sink | `testing_harness.py:68` revision | monolithic: full delta_card + cheat_sheet + vanilla answer + query | everything | *NOT LIVE IN SKILL* — only called when `--skip-revision` is off; user-facing revision is Claude in Step 6 |

**Already-good models (#3 and #4).** Both follow Sully's prescription: narrow objective, narrow context, composable with deterministic glue. These are the templates for everything else.

**The live-skill overloads (#1, #2, #6; #7, #9, #11 as follow-ups).** Each gets its own track in Section 6 with specific file paths, line numbers, and decomposition shape. #12 (revision) is retained in the inventory but **deferred** — it is not part of the live skill path.

### 0d. Why we are not rebuilding anything

For the same reason the graph enrichment was an upgrade, not a rebuild:

1. **The prompt-versioning infrastructure already exists.** `prompt_versioning.py` tracks the 5 boundary prompts. Splitting a prompt into N specialists means registering N prompts in the versioning layer — no new mechanism needed.
2. **The parallel fan-out pattern already exists.** `pipeline.py:499` runs one Pass 2 call per triggered tendency in parallel. Every track in this plan uses the same pattern.
3. **Deterministic glue already exists.** Lane 2's recall_candidates is purely deterministic. We extend the same idiom (specialist → deterministic glue → specialist).
4. **The runtime interfaces don't change.** Each lane returns its existing dataclass (DeltaCard, CompanionCheatSheet, FramePressureCard, StructuralCoverageCard). Decomposition lives inside the lane.

### 0e. What's NOT in scope (explicit non-goals)

- No new lanes.
- No new model vendors or routing layers (grok-4.1-fast stays the production model; opus stays the heavy-lift alternative).
- No retrieval-augmented generation beyond what's already there.
- No fine-tuning.
- No architecture changes to the 4-lane shape.
- No changes to the closed vocabulary of 222 models.
- **No multi-run reconciliation / SALI-style ensembles.** Running each call N times and reconciling is a valid direction but it is 3–5× the cost of every production run, and it fights the doctrine that the LLM boundaries should be narrow *specialists*, not probabilistic voters. Explicitly ruled out for this plan. Revisit only if the cost/gain picture changes dramatically.
- **No touching `testing_harness.py build_revision_prompt`.** It is dead code in the skill path (`run_pipeline.py` is invoked with `--skip-revision`). Any time spent tuning it returns zero live-user improvement.
- **No Track E (Lane 4 dimension-detection split) or Track F (bullshit subtype split) in this cycle.** Cost/gain ledger (Section 6) marks both as decorative for live skill users; Lane 4 is designed to be informative-only so variance there is tolerated by the product's own doctrine, and bullshit is already decomposed at the passage level.

This is strictly: **narrow the prompts, cut per-call input where cheap, preserve the interfaces, measure before expanding.**

### 0f. Reading order for new sessions

1. This section (0a-0g) — what's done, what's next, what we're deliberately not doing.
2. **Section 3.5** — the Marcus 3-run evidence. This is the concrete case that reset the plan. Do not skip.
3. **Section 3.6** — the doctrine (load is the lever; variance is a cost, not a principle). Do not skip.
4. Section 1-4 — understand the system and the overloads in detail.
5. Section 5 — the methodology (stability harness as diagnostic, two-axis chunking).
6. The "already-good model" files: `deep_checks.py:230` and `companion_routing.py` fingerprint. See how a narrow prompt looks in this codebase.
7. Section 6 — pick a track from the **revised priority order** and follow the detailed instructions. Do **not** start with Track A despite its upstream position; the evidence says it is the worst cost/gain ratio of the useful tracks.

### 0g. What to do next — the first-cycle sequence (ordered, skill-only, ship-or-stop)

This is one ship sequence, in this order. Do not fan out into parallel tracks. Each step is small, measurable, and informs the next.

1. **Ship Track D-skill (SKILL.md Step 6 + anchor check).** Zero API cost. Directly addresses the one documented revision failure (anchor dropout). Text edits to SKILL.md + card rendering; no pipeline changes. Measure anchor-mention count in revised_answer before and after on the Marcus case + 2–3 more as they accumulate.
2. **Build the stability harness (`scripts/stability_check.py`).** Establish a baseline on the Marcus case: Pass 1 tendency Jaccard (across N=3 runs), Lane 2 anchor Jaccard, extraction passage/constraint Jaccard, Step 6 anchor-mention count. Cost ~$0.50 per case baseline. Commit the baseline report to `research/stability-runs/marcus-baseline-2026-04-21/`. Not a gate — a compass. See Section 5c.
3. **Ship Track C-step1-3 (verification prompt tightening + candidate cap 60→30).** Negative production cost (savings from smaller prompt). Measure Lane 2 anchor Jaccard against baseline. If Jaccard moves meaningfully upward and cost goes down, keep and move on. If Jaccard is flat, note it — we'll learn from the gap.
4. **Ship Track B (Pass 1 family clustering + compound pass).** Small cost bump (~+$0.005/run). Uses existing parallel fan-out machinery. Measure Pass 1 tendency Jaccard against baseline. The Marcus evidence predicts this is the biggest single stability win in the plan.
5. **Stop. Read the numbers.** Compare post-B Marcus stability scores + anchor-mention counts to baseline. Three outcomes:
   - If stability moved up and anchor mentions hold → the first cycle is done. Publish results, close this handover version, open v3 to plan Cycle 2.
   - If Pass 1 stability improved but Lane 2 anchor Jaccard is still low → Track C-extended (family-partitioned verification) and/or Track C-fingerprint (fingerprint decomposition) are now evidence-justified. Pick one based on which half of Lane 2 the harness blames.
   - If stability barely moved on any stage → something's wrong with the methodology, not the tracks. Do not do Track A on hope. Diagnose before spending.
6. **Track A (extraction decomposition) is deferred until Cycle 2.** Cost/gain ledger says it is the worst ratio of the useful tracks (5× input tokens; variance observed on Marcus is smaller than Pass 1/Lane 2 variance). Revisit only after B and C-step1-3 numbers are in.
7. **Track D (system_b revision)** stays **deferred**. Not a live skill lever.
8. **Tracks E and F** stay **unselected**. Cost/gain ledger marks them decorative. Revisit only if Cycle 2 closes and there is demonstrated appetite.

**Hard rule for this cycle: one track at a time, each ship is its own measurement event, no parallel fan-out of work streams.** The graph enrichment handover proved this cadence works; the decomposition plan needs the same discipline.

---

## 1. What This Project Is (Read First)

Lolla is a reasoning-about-reasoning engine with 4 lanes, 222 curated mental models, and a doctrine of **"LLMs at the probabilistic edges, curated knowledge in the deterministic middle."**

This plan is about the first half of that doctrine. Today, several of the LLM "edges" are not edges — they are stuffed corridors doing many jobs at once. Sully's framing (context engineering ≫ iteration) names the failure mode: when you put 6 objectives in one prompt, no amount of prompt iteration will get you the accuracy of 6 specialists with one objective each.

**This work does not change what the system does. It changes how each LLM call is shaped so the system does what it already claims to do, reliably.**

Prerequisite reading before starting any track:

- `/Users/marcin/Desktop/Apps/lolla-skill/HOW_IT_WORKS.md` — skill-level system doc
- `/Users/marcin/Desktop/Apps/Lolla-system-b/PRODUCT_VISION.md` — product doctrine
- `/Users/marcin/Desktop/Apps/Lolla-system-b/SYSTEM_UNDERSTANDING.md` — architecture
- This handover (Section 0 is authoritative)
- `research/deep-graph-enrichment-handover.md` — parallel handover for the graph side (same shape, same principles)

---

## 2. Where the LLM Calls Live (Live Skill Path)

All paths below are inside `lolla-skill`. The live skill pipeline is:

```
Step 2  run_extract.py     OpenRouter → (query, vanilla_answer) extraction  ← Track A
Step 3  run_pipeline.py    OpenRouter → 4 lanes, --skip-revision:
          Lane 1: prompts.py pass1_triage            ← Track B
                  deep_checks.py pass2_deep_check    (template)
          Lane 2: companion_routing.py fingerprint   (template)
                  recall_candidates (deterministic)
                  verification                       ← Track C
          Lane 3: frame_pressure.py frame_extraction ← follow-up
          Lane 4: structural_coverage.py             ← Track E
          Auditor: bullshit_index.py                 ← Track F
Step 6  Claude (skill host) synthesizes revised position from 4 cards ← Track D-skill
```

`testing_harness.py build_revision_prompt` is **not invoked** in this live flow.

### Runtime files

| File | Calls | Notes |
|------|-------|-------|
| `scripts/run_extract.py` | #1 extraction | Upstream; monolithic; 6–7 objectives |
| `engine/system_b/prompts.py` | #2 pass1_triage | 25 tendencies in one prompt |
| `engine/system_b/deep_checks.py` | #3 pass2_deep_check | **Good model** — one tendency, specialist |
| `engine/system_b/companion_routing.py` | #4 fingerprint, #5 recall (deterministic), #6 verification | Fingerprint good; verification overloaded |
| `engine/system_b/frame_pressure.py` | #7 frame_extraction | Extract-and-classify; medium overload |
| `engine/system_b/structural_coverage.py` | #8 question_classification, #9 dimension_detection, #10 gap_question_generation | #9 is 4-in-1 |
| `engine/system_b/bullshit_index.py` | #11 per-passage | 4 subtypes in one call; already decomposed at the passage level |
| `engine/system_b/testing_harness.py` | #12 revision | Monolithic — **NOT LIVE IN SKILL**. Skill runs with `--skip-revision`; Claude synthesizes revision from cards. Listed for system_b/evaluation context only. |
| `engine/system_b/prompt_versioning.py` | — | Tracks the 5 officially-versioned prompts |
| `engine/system_b/pipeline.py` | — | Orchestration; fan-out parallelism is here |

### Evidence trails

- **Apr 16 run** (`/tmp/lolla_20260416T202819Z_result.json`): revised_answer 5,374 chars, zero mentions of endowment / inversion / opportunity-cost / sunk-cost / power-dynamics / game-theory. This is the revision-sink degrading richness.
- **Pass 2 spec** (`deep_checks.py:230`): system prompt literally starts "CRITICAL: You are checking for ONE tendency ONLY." The same sentence should be the opening line of every decomposed prompt in this plan.
- **Companion verification prompt** (`companion_routing.py`): ~40 lines of guardrails for passage exclusivity, tie-breakers between authority-bias and tier-2-high-value, broad-overlay exclusions — against up to 60 candidates.
- **Extraction prompt** (`run_extract.py:111`): six or seven fields extracted in one response — classic Sully overload.

---

## 3. The Architectural Decision: Decompose Prompts, Don't Rebuild Lanes

**We are narrowing existing LLM calls into specialists, not building new lanes or vendors.**

Why:

1. **Two calls already work this way.** Pass 2 and fingerprint are in-tree proof the pattern succeeds in this codebase.
2. **Fan-out parallelism is already implemented.** `pipeline.py:499` runs multiple Pass 2 calls concurrently. Every decomposition in this plan reuses that exact machinery.
3. **Prompt versioning is already implemented.** `prompt_versioning.py` tracks prompt hashes per call. New specialists register as new prompt IDs. Rollback is a config flip.
4. **Interfaces don't change.** Each lane still returns its existing card. Decomposition lives inside the lane.

What we are doing:

- **Narrowing prompts** — one objective per call.
- **Adding deterministic glue** — Python assembles specialist outputs into the lane's existing card.
- **Registering new prompt versions** — so rollback is trivial and cost/parity are measurable.
- **Running parallel fan-out** — where independent specialists can run concurrently.

What we are NOT doing:

- No new lanes.
- No new retrieval infrastructure.
- No new embeddings, no reranker models, no GNNs.
- No "single mega-prompt with better wording" — Sully's whole point is that iteration ≠ context engineering.
- No fine-tuning.
- No cross-call chain-of-thought memory (each specialist is stateless).

---

## 3.5 What We Observed — The Marcus 3-Run Evidence (2026-04-21)

**Why this section exists:** Sections 1–3 argued the overloads in theory (objective count, guardrail length, input size). Theory is not proof. On 2026-04-21 we pulled three live runs of the **same 7-turn conversation** (the "Marcus partnership" case) out of `/tmp` and compared their outputs stage-by-stage. The conversation is a realistic strategic case — a $14M agency founder deciding whether to grant 15% equity + CTO title + board seat to his head of engineering. No inputs changed between runs. No code changed. The three runs produced materially different pipeline outputs, all reporting `run_health: healthy`.

### The three runs

| Run ID | Triggered tendencies (Pass 1) | Companion anchors (Lane 2) | Extraction (constraints / passages / dropped) |
|--------|-------------------------------|----------------------------|------------------------------------------------|
| `lolla_20260421T144534Z` | liking-loving, contrast-misreaction | opportunity-cost | 4 / 5 / 3 |
| `lolla_20260421T162225Z` | deprival-superreaction, inconsistency-avoidance | endowment-effect, opportunity-cost, problem-framing-and-reframing | 5 / 6 / 2 |
| `lolla_20260421T172513Z` | inconsistency-avoidance, deprival-superreaction | premortem, inversion | 5 / 6 / 2 |

### What this shows, stage by stage

- **Pass 1 (tendency triage) — Jaccard 0.0 between run 1 and runs 2/3.** Run 1 detected two tendencies that share zero overlap with runs 2/3. These are not "close neighbors" — they are different tendency families. Runs 2 and 3 agree with each other, which suggests the correct read may live in the `inconsistency + deprival` region, but the system has no way to know that. This is the single loudest variance in the pipeline.
- **Lane 2 (companion anchors) — three disjoint sets.** Run 1 surfaces one anchor. Run 2 surfaces three, including `endowment-effect` (which is highly plausible for the founder's "company I built" emotional attachment). Run 3 surfaces `premortem` and `inversion` — neither of which appeared in the other two runs. The only overlap anywhere is `opportunity-cost` between runs 1 and 2. The "present mental models" in the same vanilla answer are being detected as three different worlds.
- **Extraction — structural drift but not catastrophic.** Constraint counts shift (4/5/5), passage counts shift (5/6/6), dropped-thread counts shift (3/2/2). `synthesized_position` was rewritten three different ways — as an A/B option framing, as a partner-vs-employee framing, and as a third-person summary of recommendations. Input to downstream lanes therefore also varied, but less than Pass 1 or Lane 2 output.
- **`run_health: healthy` on all three.** The system has no internal measurement of repeat-run consistency. It cannot see its own disagreement.

### What this does NOT show

- It does not show which answer is "right." Variance is not the same as error — any one of these could be the most useful audit for that conversation.
- It does not show that decomposition will eliminate variance. It shows that the current monolithic prompts *produce cross-family variance on cross-family-relevant stages* (Pass 1), which is the strongest possible signal that those calls are overloaded beyond the point where they can commit.

### Why this is the evidence base, not a synthetic golden set

We cannot build a 10–20 case golden set before any work starts. We do not have that archive, and waiting to build one delays everything. **The Marcus case is n=1 with three repeats, which is enough to orient the first cycle.** Additional cases accumulate as real runs happen; the stability harness in Section 5c is designed to absorb them case-by-case.

### What this changed about the plan

1. **Revised priority order.** Original plan put Track A (extraction decomposition) and Track B (Pass 1 clustering) as co-equal starting points. Marcus evidence + the cost/gain ledger (Section 6.0) reorder the cycle as: **D-skill → harness → C-step1-3 → B**, with A, C-extended, and fingerprint-decomposition held until Cycle 2 and conditional on measured remaining variance.
2. **Sharpened Track B compound-detection.** Previously a stated concern ("does family clustering break lollapalooza detection?"). Marcus data resolves it: Pass 1 is *already* missing compound signals via cross-family variance — clustering plus a lightweight compound-check pass will plausibly improve compound detection, not break it. See Section 6.
3. **Expanded Track C.** Previously "tighten verification prompt + cap candidates." The Lane 2 variance on Marcus is large enough that fingerprint stability likely matters too; added explicit fingerprint-decomposition subtrack, but held as conditional pending harness diagnosis.
4. **Elevated Track D-skill.** The only track with a *specific documented failure* (Apr 16 anchor dropout). Zero API cost. Highest per-dollar leverage in the plan.

**Evidence artifacts** (do not delete — part of the audit trail):
- `/tmp/lolla_20260421T144534Z_result.json`, `_extraction.json`
- `/tmp/lolla_20260421T162225Z_result.json`, `_extraction.json`
- `/tmp/lolla_20260421T172513Z_result.json`, `_extraction.json`

When the stability harness is built, its first job is to snapshot these into `research/stability-runs/marcus-baseline-2026-04-21/` and re-compute the Jaccard scores from them so the numbers are reproducible.

---

## 3.6 The Doctrine Behind This Plan — Load Is the Lever; Variance Is a Cost

**This section exists because the Marcus evidence is easy to misread.** The natural reaction to "three runs, three different answers" is "we need determinism." That is the wrong conclusion for this system. Lolla is built on three doctrinal commitments that make strict determinism *incompatible* with the product:

1. **LLMs at the probabilistic edges, curated knowledge in the deterministic middle.** The curated substrate (222 models, 1,358 edges, 241 bindings) is deterministic. The LLM boundaries are probabilistic by architectural intent — they do semantic judgment that no deterministic system can do reliably. A world where every LLM call returns the exact same structured output for the same input is a world where the LLMs have stopped doing semantic judgment.
2. **Swiss cheese redundancy.** Each layer has holes. Embeddings catch what the LLM misses; the LLM catches what embeddings miss. This design explicitly *assumes* non-zero variance at each layer and uses parallel independent detection to compensate.
3. **Evals measure the process, not declare truth.** The system cannot know whether its challenge was "right" — that depends on a future that hasn't happened. It can only know whether the challenge was specific, traceable, novel, and structurally grounded.

### What we accept

We accept that some variance is unavoidable. Real conversations are messy. The system will encounter queries and inputs we cannot predict. When the input is ambiguous, the structural read *can* legitimately land in more than one place, and that's fine as long as every landing is a real structural finding rather than noise. The product promise is "less wrong," not "deterministic answers."

### What we reject

We reject the idea that variance is a feature. It is a cost. Every run that produces a disjoint tendency set from a prior run of the same input *erodes the user's trust* in the audit, even if each individual finding is defensible. The user's objection is exactly right: "the system we are providing is not reassuring because we are not confident that it will work the same way every time." Trust does not require determinism — it requires that when variance happens, the *structural read* of the conversation is consistent enough that a reader can't tell which run they are looking at on the basis of tendency family alone.

### What we are optimizing for

**Load per LLM call is the lever.** The Marcus Pass 1 failure is not a prompt-wording problem. It is an attention problem: 25 concurrent hypotheses + 11 confusion guardrails + a vanilla answer, all in one call. Under that load the model's attention lands in different places on different runs. Narrow the call — fewer hypotheses, smaller guardrail stack, same input or less — and the call can commit to a structural read on repeat inputs. The call is still probabilistic. Its variance is now inside a single tendency family rather than across families.

**The product target is "repeatable structural understanding," not "identical output."** Operationally:

- Same structural read of the same passage (same reasoning pattern family detected, even if the specific tendency ID shifts between close neighbors).
- Same *commitments* captured from the user's conversation — if a user's constraint is "equity feels like giving away something I earned," every extraction should capture that, even if `decision_situation` is phrased differently.
- Same *omissions detected* — dropped threads, missing reversal conditions.
- The same anchor model **families** identified in Lane 2 — Run 2's `endowment-effect` and Run 3's `inversion` are both defensible reads of the founder's "I built this" framing, but a user comparing the two runs experiences whiplash. The goal is that both runs would at least name the "emotional ownership / attachment" family even if they differ on which specific model best challenges it.

### The two axes of chunking

The plan applies chunking on two axes, and both matter:

1. **Obligation chunking** (fewer jobs per call) — the Sully-style decomposition. Example: Pass 1 currently scores 25 tendencies; family clusters each score 4–5.
2. **Input chunking** (less data per call) — audit what each call *currently sees* versus what it *needs to see*. Example: Lane 2 verification currently looks at up to 60 candidates; family-partitioned verification looks at ~12. Example of where input chunking is limited: every extraction specialist needs the full transcript, so Track A gets obligation chunking but not much input chunking — that unevenness is why A is not at the front of the cycle.

### What we are not doing (doctrine-level)

- **Not building multi-run reconciliation / ensembles.** Running each call N times and voting is a coherent alternative approach to variance. It is ruled out for this plan on cost (3–5× per run) and on doctrine grounds: we want narrow specialists, not probabilistic voters. If the Cycle 1 numbers show decomposition is insufficient and costs are already low, ensembles become a legitimate Cycle 2+ conversation. Not now.
- **Not targeting 1.0 stability.** If any stage's stability hits 1.0 after decomposition, that is a *warning* — the specialist has probably stopped doing semantic judgment and is rule-matching instead. The target is "meaningfully upward from current" with a floor that preserves the call's ability to read ambiguous reasoning shape.
- **Not treating the stability harness as a gate.** It is a diagnostic. Low stability tells us *where* to chunk next; rising stability tells us a treatment worked. It does not replace qualitative review.

### In one sentence

**Accept probabilism where the conversation is genuinely ambiguous; cut load until the calls that should be stable become stable; measure, don't hope.**

---

## 4. The Overloads We Are Solving

### 4a. Extraction (#1) — upstream monolith

`run_extract.py:111` runs one prompt that produces all of:
- `is_strategic` (binary classifier)
- `decision_situation` (free text)
- `live_constraints` (list with status + weight per item)
- `synthesized_position` (free text)
- `reasoning_passages` (3–8 literal substrings, verified by substring match)
- `original_framing` (free text)
- `dropped_threads` (list with raised_by / status / superseded_by)

**Why it's the biggest target:** extraction sits upstream of every lane. Every downstream failure has extraction as its root cause candidate. A single extraction failure cascades through Pass 1, Lane 2, Lane 3, Lane 4, and revision. And retry cost is the whole pipeline.

### 4b. Pass 1 Triage (#2) — 25 tendencies in one call

`prompts.py` PASS_1_TRIAGE_SYSTEM scores all 25 Munger tendencies simultaneously. The prompt contains:
- The list of 25 tendencies with brief descriptions.
- ~12 "CRITICAL RULES" for avoiding false positives.
- ~11 "COMMON CONFUSION GUARDRAILS" between look-alike tendencies (e.g., authority-misinfluence vs social-proof).

Pass 2 (#3) is already perfectly shaped (one tendency, parallel). Pass 1 is the mirror image — one call doing 25 jobs.

### 4c. Companion Verification (#6) — 60 candidates under heavy guardrails

Lane 2's shape is already Sully-correct:
1. fingerprint (LLM, 1 objective: abstract moves) → `_build_fingerprint_system_prompt` says "Do not name mental models. Describe abstract reasoning moves only."
2. recall_candidates (deterministic token overlap — up to 60 candidates) → zero LLM.
3. verification (LLM, 1 objective: which of these candidates are actually present).

The architecture is fine. **The verification prompt is the overload.** ~40 lines of guardrails, up to 60 candidates, passage-exclusivity rules, tie-breakers between specific candidate pairs, broad-overlay exclusions.

### 4d. Revision (#12) — NOT LIVE IN SKILL

`testing_harness.py:68` `build_revision_prompt` exists and is a monolith, but the skill's `run_pipeline.py` is invoked with `--skip-revision` (see `SKILL.md:155`). In the live skill, the revised answer is produced by Claude (the skill host) in Step 6 using the 4 cards directly — **no OpenRouter revision call happens.**

This means:
- The revision-monolith overload does NOT affect live skill users.
- It still matters for `Lolla-system-b` (evaluation harness, telemetry, testing) where revision is called.
- Track D below is therefore deferred in the skill-first work stream and belongs to a separate system_b pass.

**The user-facing revision problem in the skill is different:** Claude is the "LLM" doing the revision, and its context is the 4 cards. If anchor models drop out of the revised answer (Apr 16 run: zero mentions of half the curated models), the cause is not an OpenRouter call — it's either (a) card content missing the anchors, (b) Claude's synthesis step giving cards too little weight, or (c) SKILL.md instructions not emphasizing anchor preservation strongly enough. **Any skill-side revision improvement lives in SKILL.md Step 6 and the card rendering logic, NOT in `testing_harness.py`.**

### 4e. Secondary overloads (lower priority)

- **Frame extraction (#7)** — extract-and-classify with 10 calibration rules + 9 negative examples. Tight as-is, but splittable.
- **Dimension detection (#9)** — 4 jobs simultaneously (dims + coverage + materiality + cap). `structural_coverage.py:251-268`.
- **Bullshit (#11)** — 4 subtypes per passage; already decomposed at the passage level, so less urgent.

### 4f. What we are NOT claiming is broken

- **Pass 2 deep check (#3)** — gold standard. Copy this pattern.
- **Companion fingerprint (#4)** — gold standard. Copy this pattern.
- **Question classification (#8)** — already narrow.
- **Gap question generation (#10)** — 6 design rules, narrow objective. Fine.

---

## 5. The Methodology (READ BEFORE TOUCHING ANY PROMPT)

This is the equivalent of the graph work's "read the canonical article fully" rule. Skip it and the decomposition will regress silently.

### 5a. The Decomposition Principle

Each LLM call must have **one semantic objective**, **bounded input**, and **a narrow guardrail stack** (the guardrails for its single objective, not for 25 others). If a prompt has multiple objectives, it splits. If input scales beyond a family boundary, it splits. If the guardrail stack rivals the instruction in length, it splits.

Corollary: when splitting, **Python assembles**. The LLM never sees the other specialists' outputs during its own turn.

### 5b. The Fidelity Principle (Sully)

Context engineering and iteration are **substitutes**. When a call is under-performing, the first move is to narrow its context — fewer objectives, smaller input, tighter prompt — not to iterate on wording at the same complexity. Iteration is what you do **after** the call is correctly shaped, to polish.

If you catch yourself re-wording a 40-line guardrail stack, stop. You are iterating where you should be decomposing.

### 5c. Stability harness — diagnostic, not gate

**This section replaces the earlier "golden replay" framing.** We cannot build a 10–20 case golden set before any work starts — that archive does not exist and waiting to build it delays the whole plan. Instead, each real run that flows through the skill becomes a potential stability case, starting with the Marcus 3-run baseline from 2026-04-21 (Section 3.5).

**The harness is a measurement tool, not a pass/fail gate.** Low stability on a stage tells us that stage is load-overloaded; rising stability after a track ships tells us the treatment worked. It does not tell us whether an answer was "correct" — that is not a thing the system can know (Section 3.6). It does not replace qualitative review of the cards.

**What the harness does:**

1. Take an existing extraction JSON (captured in `/tmp/lolla_{run_id}_extraction.json`). Do not re-extract — we hold the extraction constant so we isolate pipeline variance from extraction variance.
2. Run `run_pipeline.py --skip-revision` N=3 times against that extraction, with N configurable up to 5.
3. For each stage, compute a stability score:
   - **Pass 1 tendency triggering** — Jaccard over `detected_tendencies` across the N runs.
   - **Lane 2 companion anchors** — Jaccard over `companion_cheat_sheet.anchors[].model_id`.
   - **Lane 3 reframings** — Jaccard over `frame_pressure_card.reframings[].model_id`.
   - **Lane 4 gap dimensions** — Jaccard over `structural_coverage_card.gap_routes[].dimension_id`.
   - **Extraction drift** — separate harness mode that *does* re-extract N times, computing Jaccard on constraint text, passage text, and cosine on `synthesized_position`.
   - **Step 6 anchor mention count** — regex match of anchor `model_id` tokens in the revised_answer (requires SKILL.md integration so Claude's revision is captured back to file; see Track D-skill).
4. Write a per-case stability report to `research/stability-runs/{case-id}-{date}/`:
   - Pipeline config hash (prompt versions in effect)
   - Per-stage Jaccard scores with the N raw run IDs
   - Per-stage variance diff (which items differed across runs)
   - Total token cost and wall-clock for the N runs

**What the harness does NOT do:**

- It does not compare "new pipeline vs old pipeline." It compares "pipeline against itself" across N repeat runs. That is sufficient for the first cycle.
- It does not declare a track succeeded. The reviewer does, by looking at the stability delta AND the qualitative card content.
- It does not run on every production user audit. It runs on demand, on selected cases, typically as part of a shipping decision.

**Cost.** One harness invocation at N=3 costs ~3× a normal run (~$0.09–$0.18). One baseline + one post-track re-measurement per case ≈ $0.30. Measurement spend is one-time per track, not per production run.

**Acceptance criterion for any track in this plan:**

1. Stability on the *targeted* stage moves meaningfully upward from baseline (at minimum +0.2 Jaccard, or a clear movement in the right direction on cosine measures).
2. No neighboring stage regresses below its baseline by more than 0.1.
3. Production per-run cost stays within the cost ceiling declared in Section 6 for that track.
4. At least one qualitative review pass by a human reader on 2–3 post-track cases confirms the cards are structurally real (not rule-matched, not hollowed out).

If (1) holds but (4) shows the cards have lost semantic richness, the track regressed on doctrine grounds even if the numbers moved. 1.0 stability is not the goal (Section 3.6).

### 5d. Version every prompt

Every specialist registers in `prompt_versioning.py` with a unique ID and a stable hash. The pipeline reads the prompt ID from config. Rollback is a config flip. No git revert required, no cache invalidation scares.

The 5 official boundaries today are:
- `pass1_triage`
- `pass2_deep_check`
- `companion_fingerprint`
- `companion_verification`
- `frame_extraction`

This plan adds ~15 new prompt IDs. Naming convention: `{lane}_{objective}_{version}` (e.g., `extraction_strategic_classifier_v1`, `pass1_authority_cluster_v1`).

### 5e. Stateless specialists

Every specialist is independently retriable. No conversation memory between calls. Python glue holds all cross-specialist state.

Consequence: if a specialist returns malformed JSON, only that specialist retries — not the whole pipeline. This is the deterministic-engine upside the user asked for ("lets analyze system inside out to improve our extraction to deterministic engine").

### 5f. Post-LLM verification where it's cheap

Wherever a specialist's output shape allows deterministic verification, run it in Python after the call and fail/retry on verification failure. Example: `reasoning_passage_extractor` returns literal substrings from the transcript. Python verifies each substring exists in the source and drops non-literal outputs. No second LLM call needed.

---

## 6. The Work Plan — Cost/Gain Ledger and First-Cycle Sequence

**This section was reordered on 2026-04-21 based on the Marcus 3-run evidence (Section 3.5) and an explicit cost/gain pass. Read 6.0 before reading any individual track description. The track descriptions that follow are not a menu — they are a ranked sequence, and two of them (E, F) are explicitly not being done.**

### 6.0. The cost/gain ledger

Baseline per run (from `HOW_IT_WORKS.md`): **10–13 OpenRouter calls, 30–40K tokens, ~$0.03–0.06 per audit, roughly `grok-4.1-fast` prices.** All estimates below are deltas against that baseline.

| Track | Cost delta/run | Friction | Evidence of gain | Tier |
|-------|----------------|----------|------------------|------|
| **D-skill** — SKILL.md Step 6 rewrite + anchor-mention check | **$0** (Claude is already doing this; text edits only) | None in production; adds a small verification step inside Claude's existing synthesis pass | Apr 16 run: 50% of anchor models dropped from revised_answer. Direct, observed failure. | **DO FIRST** |
| **Stability harness** — `scripts/stability_check.py` + `research/stability-runs/` baseline | $0 in production; ~$0.30 per case measured | None in production; manual tool | Unblocks every other measurement in the plan; Marcus baseline is its first case | **DO SECOND** |
| **C-step1-3** — verification prompt cleanup (dead-guardrail deletion) + candidate cap 60→30 | **−$0.002 to −$0.005/run** (savings from smaller prompt + fewer candidates) | Minimal — one prompt version + one config value | Observed: 40-line guardrail stack is bloated; 60-candidate cap inherited from earlier calibration | **DO THIRD** — free win |
| **B** — Pass 1 family clustering (5 clusters) + lightweight compound-check pass | **+$0.004 to +$0.007/run** (5 small parallel calls; vanilla answer duplicated across calls) | Parallel fan-out already in-tree (`pipeline.py:499`); wall-clock unchanged | Marcus: Pass 1 Jaccard 0.0 between run 1 and runs 2/3 — the biggest observed variance source in the pipeline | **DO FOURTH** |
| **C-extended** — family-partitioned verification (5 parallel family calls, ~12 candidates each) | +$0.008 to +$0.012/run | Moderate — more prompts, more glue | Plausibly closes remaining Lane 2 variance, **only if** C-step1-3 doesn't | **HOLD** — only if harness still shows Lane 2 variance after C-step1-3 |
| **C-fingerprint** — decompose `companion_fingerprint` into 3 specialists (structural / closure / attribution moves) | +$0.005 to +$0.008/run | Moderate | **Uncertain.** The Lane 2 variance on Marcus could be fingerprint-rooted or verification-rooted. Harness will tell us. | **HOLD** — diagnose with harness first |
| **A** — Extraction decomposition (5 specialists, each reads full transcript) | **+$0.015 to +$0.025/run** (biggest hit: 5× input tokens because every specialist needs the full transcript) | Parallel fan-out, but input duplication is unavoidable | Marcus: extraction variance exists but is **smaller** than Pass 1/Lane 2 variance. Track's cost/gain ratio is the worst of the useful tracks. | **HOLD** — Cycle 2 candidate; do not start in Cycle 1 |
| **E** — Lane 4 dimension-detection split | +$0.003 to +$0.006/run | Moderate | Lane 4 is **informative-only by design** (Section 231 of HOW_IT_WORKS.md); variance here does not affect Lanes 1–3 output | **DO NOT DO** — decorative for live skill |
| **F** — Bullshit subtype split (4 subtypes × N passages) | Roughly +4× Lane F spend | High — multiplies per-passage calls | Bullshit is already decomposed at the passage level; subtype-level split multiplies cost for marginal gain | **DO NOT DO** — decorative |
| `testing_harness.py` revision split | N/A | N/A | Dead code in skill path (`--skip-revision`) | **DO NOT TOUCH** |
| Multi-run reconciliation / SALI ensembles | 3–5× every production run | Massive — rewrites orchestration layer | Explicitly ruled out (Section 0e, 3.6) | **DO NOT BUILD** |
| Fine-tuning / new vendors | High one-time + ongoing ops | High | Premature given we haven't exhausted chunking | **OUT OF SCOPE** |

**Aggregate math for Cycle 1 (D-skill + harness + C-step1-3 + B):**

- Production per-run cost: **flat to slightly cheaper** (Track B adds ~$0.005, C-step1-3 saves ~$0.003).
- Wall-clock per run: **unchanged** (all new work is parallel-capable).
- One-time diagnostic spend: ~$0.50–1.50 (Marcus baseline + post-track re-measurements).
- Expected observable wins: anchor dropout closed in Step 6; Pass 1 stops jumping families; Lane 2 verification prompt shrinks and produces more stable anchor sets.

**The Cycle 1 rule:** ship in sequence, not in parallel. Read the numbers after each track. If a track misses its acceptance criterion (Section 5c), diagnose before shipping the next one.

### 6.1. Where the big gains are, ranked

1. **D-skill** — the only track with a *specific documented failure*. Zero API cost. Highest per-dollar leverage in the plan.
2. **B (Pass 1 family clustering)** — Marcus shows this is the noisiest stage. Clustering is cheap and reuses existing parallel fan-out.
3. **C-step1-3** — literally negative production cost. Ship the cleaner verification prompt and the tighter candidate cap; measure; stop if Lane 2 variance closes.
4. **Stability harness** — without it, every other track ships blind. Not a track in itself, but the *enabling infrastructure* for everything else.

### 6.2. Where the decorative work lives (will NOT be shipped in this cycle)

- **Track E** — Lane 4 is designed to be informative, not load-bearing. Variance here is tolerated by the product's own doctrine.
- **Track F** — per-passage bullshit is already decomposed at the passage level; splitting subtypes multiplies spend for marginal gain.
- **Track C-extended** and **C-fingerprint** — may be needed; do not commit until the harness says so after Track B.
- **Track A** — 5× input duplication for a stage the Marcus evidence says is not the biggest variance source. Good later, bad first.

### Track A — Extraction Decomposition (HELD; Cycle 2 candidate)

**Status: HELD until Cycle 2.** The Marcus 3-run evidence (Section 3.5) shows extraction variance exists but is *smaller* than Pass 1/Lane 2 variance, and the cost delta is the worst of the useful tracks (+$0.015–0.025/run, driven by 5× input-token duplication because every specialist needs the full transcript). Starting with A would spend the most budget on the least-evidenced stage. Revisit only after Track B numbers are in and remaining variance justifies the spend.

**Goal:** Replace the one 6–7-objective extraction call (`run_extract.py:111`) with 5 specialists composed by Python.

**Why upstream still matters (just not first):** Every downstream lane inherits extraction quality, so this remains on the roadmap. The evidence-based reordering does not say extraction is fine; it says Pass 1 and Lane 2 variance will dominate *our user-visible stability numbers* until they are addressed first.

**Specialists:**

1. **`extraction_strategic_classifier_v1`** — input: transcript → output: `{is_strategic: bool, confidence: float, reason: str}`. One objective. Pure classification.
2. **`extraction_situation_v1`** — input: transcript → output: `{decision_situation: str, original_framing: str}`. Free text, but narrow.
3. **`extraction_constraints_v1`** — input: transcript → output: `[{text, status, weight}]`. Structured list only.
4. **`extraction_passages_v1`** — input: transcript → output: `[str]` (3–8 literal substrings). Most deterministic of all: Python verifies each substring exists in the transcript and drops non-literal hallucinations.
5. **`extraction_threads_v1`** — input: transcript → output: `[{thread, raised_by, status, superseded_by}]`. Dropped threads with supersession chains.

Python glue assembles an `ExtractionResult`. Each specialist caches and retries independently. Run #1, #2, #3, #4 in parallel; #5 can also run in parallel (independent of the others' outputs).

**Cost estimate:** ~5× the calls, but each is small, so ~1.5–2× total tokens. Latency comparable (parallel fan-out).

### Track B — Pass 1 Family Clustering + Compound-Check Pass (Cycle 1, step 4)

**Status: DO FOURTH in the first cycle (after D-skill, harness, C-step1-3).** Marcus 3-run evidence (Section 3.5) identifies Pass 1 as the single noisiest stage in the pipeline — run 1 shares zero triggered tendencies with runs 2/3. That is the loudest signal in the evidence base that a call is load-overloaded. The fix is cheap (~+$0.005/run) and uses machinery already in-tree.

**Goal:** Replace the one 25-tendency pass1_triage call with 5 family-cluster triage calls + 1 lightweight compound-check pass.

**Why this track is evidence-justified:** Pass 2 is already the right shape. Pass 1 is the mirror-image mistake — 25 concurrent hypotheses + 11 confusion guardrails in one prompt. The Marcus data shows the model's attention lands in different tendency families on different runs under that load. Clustering forces each cluster to commit to its 4–5 tendencies with isolated guardrails.

**Proposed clusters (draft — validate before implementing):**

- **`pass1_authority_cluster_v1`** — authority-misinfluence, doubt-avoidance, reciprocation, liking-loving, social-proof.
- **`pass1_incentive_cluster_v1`** — incentive-caused-bias, reward-and-punishment, envy-jealousy, self-serving.
- **`pass1_stress_commitment_cluster_v1`** — stress-influence, inconsistency-avoidance, commitment-and-consistency, deprival-superreaction.
- **`pass1_availability_cluster_v1`** — availability-misweighing, contrast-misreaction, over-optimism, excessive-self-regard.
- **`pass1_residual_cluster_v1`** — curiosity, kantian-fairness, simple-psychological-denial, use-it-or-lose-it, drug-misinfluence, senescence, false-consensus, lollapalooza, twaddle.

Each cluster scores only its 4–5 tendencies, with only the confusion guardrails for that cluster (not all 11). 5 parallel calls. Triggered tendencies fan into Pass 2 as today — **no change to Pass 2.**

**Compound-check pass (required addition, in response to Marcus evidence).** Previously this handover worried that family clustering might hurt lollapalooza detection. The Marcus data *resolves* that concern in the opposite direction: Pass 1 is already losing compound signals to cross-family variance — run 1 caught `liking + contrast`, runs 2/3 caught `inconsistency + deprival`, and no single run saw all four. A family-clustered Pass 1 plus one lightweight compound-check pass will plausibly produce better compound detection than today's 25-in-one prompt.

The compound-check pass:
- Runs after the 5 family clusters return.
- Input: the vanilla answer + the combined triggered-tendency list (IDs only) from the 5 clusters.
- One objective: "Among these triggered tendencies, are 3 or more converging on the same passage or reasoning move? If yes, flag as compound and name the converging passage."
- Output: a compound record (optional — zero compounds is a valid result) consumed by DeltaCard assembly.
- Cost: one small call (~$0.002/run).

This brings the total Pass 1 cost to: 5 family-cluster calls + 1 compound-check call ≈ +$0.004–0.007 over the current single-call Pass 1. Latency unchanged (parallel fan-out on the 5 clusters, the compound check runs after them but is a small call).

**Cost estimate:** ~5–6 parallel calls + 1 compound check, small prompts each, so ~+$0.005/run. Latency unchanged.

**Validation step specific to Track B:** Before implementing, re-read each of the 25 Munger tendencies in `prompts.py` and confirm the clustering is semantically clean. Some tendencies (notably `lollapalooza` and `twaddle`) may not belong with peers; keep them in `residual` rather than forcing a bad cluster. The compound-check pass specifically replaces the previous hope that `lollapalooza` would get detected as a tendency in its own right — under the new shape, lollapalooza *is* the output of the compound-check pass, not an item in a cluster's menu.

**Acceptance criterion** (per Section 5c): Pass 1 tendency Jaccard on the Marcus 3-run baseline moves from 0.0 → at minimum 0.4, with qualitative review confirming the clusters are still doing semantic judgment (not rule-matching).

### Track C — Lane 2 Stability (three sub-tracks, only step 1-3 in Cycle 1)

**Status: C-step1-3 is DO THIRD in Cycle 1 (after D-skill and harness; before B). C-extended and C-fingerprint are HELD — conditional on post-B harness numbers.** Marcus evidence shows Lane 2 anchor Jaccard is near-zero across three runs — three disjoint anchor sets. But we do not yet know whether that variance is upstream in `companion_fingerprint` or downstream in `companion_verification`, or both. The harness built in step 2 of the cycle is explicitly designed to attribute Lane 2 variance; only then do we decide which of C-extended / C-fingerprint (if any) is worth the cost.

**Goal (step 1-3):** Make the ~40-line guardrail stack in `companion_verification` leaner, and tighten the candidate pool before feeding it to the verifier. This is the cheapest part of the whole Cycle 1 — it saves money and plausibly improves stability.

**Steps (in order):**

1. **Read the current verification prompt** and classify each guardrail as:
   - **Always-on** (applies to every candidate regardless of family)
   - **Triggered** (applies only when specific candidate pairs are present)
   - **Dead** (no longer needed; relic of earlier calibration)
2. **Delete the dead guardrails.** Ship the tightened prompt as `companion_verification_v2`.
3. **Cap recall candidates lower** — today up to 60. Evaluate whether top-30 by affinity produces equivalent verification outcomes against the Marcus baseline run JSONs. If yes, cap at 30.

**Cost estimate for step 1-3:** **negative** (savings from smaller prompt + fewer candidates). Latency unchanged or slightly faster.

**Acceptance criterion** (per Section 5c): Lane 2 anchor Jaccard on the Marcus baseline moves meaningfully upward AND per-run cost decreases. If stability moves but cost stays flat, acceptable. If stability flat, proceed to measurement step — see below.

---

**Track C-extended — Family-partitioned verification (HELD; only if post-B harness still shows Lane 2 variance attributable to verification):**

Pre-bucket recall candidates by family (authority, incentive, framing, coverage, decision-quality, residual). Run one verification specialist per family in parallel, each with only that family's triggered guardrails. ~5 small calls instead of 1 big one.

This does NOT expand the 222-model vocabulary — it partitions the existing 222 for routing only. Fits the closed vocabulary principle.

**Cost estimate:** +$0.008–0.012/run. Do not commit without harness evidence.

---

**Track C-fingerprint — Fingerprint decomposition (HELD; only if post-B harness attributes Lane 2 variance to fingerprint, not verification):**

Decompose `companion_fingerprint` into 3 specialists:

1. **`fingerprint_structural_moves_v1`** — abstract moves that shape the argument's structure (e.g., "weighing tradeoffs," "collapsing a multi-option decision into A/B").
2. **`fingerprint_closure_moves_v1`** — moves that close uncertainty (e.g., "committing to a path without naming a reversal condition").
3. **`fingerprint_attribution_moves_v1`** — moves that assign agency, causation, or credit (e.g., "attributing behavior to incentive vs. character").

Python glue combines the three specialists' outputs before feeding to `recall_candidates`.

**Cost estimate:** +$0.005–0.008/run. Do not commit without harness evidence showing fingerprint — not verification — is the variance source.

**Do C-step1-3 first. Do not jump to C-extended or C-fingerprint without measurement.**

### Track D — Revision Stage Split (DEFERRED for skill; system_b only)

**Status: NOT a live skill concern.** `run_pipeline.py` runs with `--skip-revision`. The skill's revision is produced by Claude in Step 6 using the 4 cards.

Retained here for system_b and evaluation-harness work. If/when system_b revision is revisited, the shape would be a 3-stage sequential split:

1. `revision_incorporate_pressures_v1` — query + vanilla answer + delta_card → draft absorbing Lane 1 pressures.
2. `revision_weave_anchors_v1` — draft + companion_cheat_sheet → draft with anchor models named.
3. `revision_tighten_v1` — draft + frame + coverage cards → final revised answer.

**Do NOT work on this for the skill.** The skill-side analogue lives in Track D-skill below.

### Track D-skill — Claude Revision Context (Cycle 1, step 1 — DO FIRST)

**Status: DO FIRST.** Zero API cost. Addresses the only *specifically documented* failure in the plan (Apr 16 anchor dropout: revised_answer was 5,374 chars with zero mentions of half the cheat sheet's anchor models). Highest per-dollar leverage in the whole plan — every other track spends at least $0.005/run; this one spends nothing and directly improves what the user sees.

**Goal:** Make Claude (Step 6, the actual live "reviser" in the skill) keep more of the curated enrichment in the revised position.

**Why this matters (skill-specific):** The failing "LLM" in the skill's revision flow is Claude following SKILL.md Step 6, not an OpenRouter call. The fix lives in:
- `SKILL.md` Step 6 — the instructions Claude follows for synthesis.
- `references/output-field-guide.md` — how cards are interpreted.
- Card rendering — are anchor models surfaced clearly enough for a synthesizer to weave them?

**Proposed moves (in priority order):**

1. **Audit SKILL.md Step 6 language.** Does it instruct Claude to explicitly name anchor models from the companion cheat sheet in the revised position? If not, add that instruction with concrete examples.
2. **Audit the companion_cheat_sheet output format.** Are the anchor models surfaced at the top of the card, or buried? Make the anchor list impossible to miss.
3. **Add a post-synthesis check in SKILL.md.** Before presenting the revised position, Claude counts how many anchor models from the cheat sheet appear by name. If fewer than 50% appear, revise to include them or explain the drop.
4. **Optional — split Step 6 into two passes in SKILL.md.** Pass 1: "incorporate Lane 1 pressures + name anchors." Pass 2: "address frame/coverage gaps + tighten." Same Sully idiom as Track D, applied at the skill instruction layer.

**What NOT to do:** Do not touch `testing_harness.py build_revision_prompt` — it's dead code in the skill path. Changing it will have no effect on live skill users.

**Validation:** Stability harness at the chat-output level — same Marcus extraction, compare anchor-model mention count in the revised_answer before vs after. The harness's `step6_anchor_mention_count` metric (Section 5c) is designed for this track specifically. Target: recover at least 80% of cheat-sheet anchors by name in the revised answer.

### Track E — Dimension Detection Split (DO NOT DO — decorative)

**Status: NOT shipping in Cycle 1 or Cycle 2. Marked decorative by the cost/gain ledger (6.0).**

Rationale: Lane 4 is **informative-only by design** — its outputs (gap dimensions, discovery questions) do not feed back into Lanes 1-3 and do not change the DeltaCard or CompanionCheatSheet. Variance in Lane 4 is tolerated by the product's own doctrine. Spending $0.003–0.006/run to stabilize a lane that is supposed to surface "structural angles the decision-maker might not have considered" would be optimizing the wrong loss function.

If retained for future reference, the shape would be:

1. **`coverage_dimension_match_v1`** — which of 15 dims are covered by the answer?
2. **`coverage_score_v1`** — per-covered-dim coverage quality score.
3. **`coverage_materiality_v1`** — per-uncovered-dim materiality assessment.

Gap-question generation (#10) stays as-is; it is already narrow.

**Do not ship without explicit reversal of the cost/gain ledger decision.**

### Track F — Bullshit Subtype Split (DO NOT DO — decorative)

**Status: NOT shipping. Marked decorative by the cost/gain ledger (6.0).**

Rationale: The bullshit auditor is **already decomposed at the passage level** — it runs per-passage, and each passage's four subtypes (empty rhetoric / paltering / weasel / unverified) are adjudicated together. Splitting those four subtypes into parallel sub-detectors multiplies per-passage spend by ~4× for marginal gain. The per-call overload is minor compared to Pass 1 or Lane 2.

**Do not ship without explicit reversal of the cost/gain ledger decision.**

---

## 7. Detailed Instructions (For the Junior Developer)

### Before you start

1. Read `/Users/marcin/Desktop/Apps/lolla-skill/HOW_IT_WORKS.md` fully.
2. Read `PRODUCT_VISION.md` fully.
3. Read Section 0 of this handover.
4. Read `engine/system_b/deep_checks.py:230` — the Pass 2 system prompt. This is what a narrow prompt looks like in this codebase. You will copy its shape.
5. Read `engine/system_b/companion_routing.py` — the full Lane 2 flow. Note how fingerprint → deterministic retrieval → verification is already decomposed. The `recall_candidates` function is the model for "Python glue" in all decompositions.
6. Read `engine/system_b/prompt_versioning.py` — how prompts are registered, hashed, and version-pinned.
7. Read `engine/system_b/pipeline.py:499` `_run_pass2_parallel` — how parallel fan-out works in the codebase. You will copy this pattern.

### The workflow for every track

Regardless of which track you pick, follow this exact flow:

1. **Ensure the stability harness exists (Section 5c).** If not, build it first — it's the foundation for every measurement in this plan. For Track D-skill specifically, the harness's `step6_anchor_mention_count` metric is the acceptance bar.
2. **Snapshot the baseline for this track's metric.** At minimum the Marcus 3-run baseline. Commit to `research/stability-runs/{case-id}-baseline-{date}/`. As real conversation runs accumulate, add more cases.
3. **Write the specialist prompts.** For each specialist:
   - One objective, stated in the first sentence ("You are a [objective]. Return strict JSON with the following fields...").
   - Input described explicitly.
   - Output schema described explicitly with types.
   - Only guardrails relevant to this one objective.
   - No mention of other specialists. No mention of downstream consumers. No mention of the 4-lane architecture.
4. **Register each prompt in `prompt_versioning.py`** with a unique ID.
5. **Build the Python glue function.** It takes the lane's existing input, calls the specialists (parallel where independent, sequential where dependent), assembles the lane's existing output dataclass.
6. **Run the stability harness against the new pipeline.** Compare per-stage Jaccard / cosine scores against baseline. Acceptance: Section 5c criteria.
7. **Measure cost.** Tokens and latency, per specialist and in aggregate. Compare to the per-track cost ceiling declared in Section 6.0.
8. **Qualitative review pass.** Read 2–3 post-track cards by hand. Confirm the cards are still doing structural work (not rule-matched, not hollowed out). If stability moved up but cards look thin, that's a doctrinal regression (Section 3.6) — do not ship.
9. **Ship behind a config flag.** Old pipeline stays active until the flag is flipped.
10. **Flip the flag after one week of shadow-mode runs** — new pipeline running alongside old, outputs compared via stability harness. No regressions → promote. Remove the old prompt version.

### What to NOT do (every track)

- Do not rewrite prompts in a "rich" LLM-native style. The specialists should be almost boring. Boring is correct.
- Do not cross-import specialists. Each specialist is a pure function from input to output. No specialist calls another specialist; only Python glue composes them.
- Do not skip the stability harness. The whole plan is worthless if stability isn't measured.
- Do not chase 1.0 stability. If any stage's Jaccard hits 1.0 after decomposition, that's a warning — the specialist has stopped doing semantic judgment. See Section 3.6.
- Do not add retries inside the LLM call. Retries live in the Python wrapper around the call — that's what makes each specialist independently retriable.
- Do not let a specialist see another specialist's output in its prompt. That reintroduces the overload you just split apart. The one exception is Track D (system_b), where revision stages are *explicitly* sequential; each stage's output is the next stage's input, by design.
- Do not run tracks in parallel. Each Cycle 1 track is its own measurement event; parallel work streams overwhelm the harness and conflate signals.

### Model choice per track

- **Production model today:** `grok-4.1-fast` for most calls, `grok-4.1` for heavier ones. Check `prompt_versioning.py` for per-call specifics.
- **Recommendation for this work:** keep the same model per call family. The goal of decomposition is to let the *existing* model succeed by giving it a narrower job. Swapping models at the same time as decomposing confounds the measurement.
- **Later:** once decomposition ships, consider downgrading some specialists to `grok-4.1-fast` if their narrower scope allows it. Measure first.

---

## 8. Runtime / Infra Changes

### 8a. `prompt_versioning.py` extension

Today tracks 5 prompt boundaries. After this plan, it tracks ~20. No mechanism change — just new IDs.

### 8b. Pipeline config flags

Each Cycle-1 track introduces a config flag. Active flags (in priority order): `skill_revision_v2` (D-skill; lives in SKILL.md, not pipeline config, but tracked here for completeness), `tighten_companion_verification` (C-step1-3), `family_triage_with_compound_check` (B). Default `False` at ship time; flip to `True` after the stability harness confirms no regression on the Marcus baseline plus any new cases added to `research/stability-runs/`.

Held tracks (`extraction_decomposition` for A, `extend_companion_verification` for C-extended, `decompose_companion_fingerprint` for C-fingerprint) get no flag until explicitly unheld — Section 6.0 ledger gates them.

### 8c. Parallel fan-out helpers

`pipeline.py:499` `_run_pass2_parallel` is the template. For Track B's compound-check pass, either reuse this helper directly (compound check is a single extra call after family clusters return) or keep inline — no abstraction needed yet. Re-evaluate if Cycle 2 unlocks Track A or C-extended.

### 8d. Stability harness

New file: `scripts/stability_check.py`. Inputs: a case conversation file + pipeline config + run count (default 3). Outputs: per-stage Jaccard / cosine-pair scores written to `research/stability-runs/{case-id}-{date}/`. This is the single most important new infrastructure piece — every Cycle-1 track gates on it.

Design contract (per Section 5c):
- Run the pipeline N times against the same input. Capture extraction, Pass 1, anchors, Pass 2, revised answer per run.
- Per stage, compute pairwise Jaccard (set-valued outputs) or mean cosine (embedding-valued outputs) across the N runs.
- Acceptance is a **threshold band**, not a target. Pass 1 Jaccard near 1.0 signals a specialist that stopped doing semantic judgment — treat as a warning, not a win.
- Harness cost budget: ~$0.30 per 3-run case at production model pricing. Production impact: $0 (diagnostic only, not on the hot path).

### 8e. No new data artifacts

Decomposition does not require new artifacts in `data/`. The lane outputs (DeltaCard, CompanionCheatSheet, FramePressureCard, StructuralCoverageCard) stay unchanged.

---

## 9. Validation Steps

### After each track is prototyped

- [ ] Stability harness: per-stage Jaccard / cosine scores **improved vs. baseline** on the Marcus case and any new cases in `research/stability-runs/`. Improvement is relative to the pre-track baseline, not to 1.0.
- [ ] No stage's Jaccard pins to 1.0 (would signal lost semantic judgment — see Section 3.6).
- [ ] Cost: tokens per pipeline run (per specialist + aggregate) within the Section 6.0 ledger for this track.
- [ ] Latency: p50 and p95 per specialist + end-to-end — parallel fan-out should keep end-to-end flat or lower.
- [ ] Failure modes: when a specialist fails, does retry + isolation work as designed?
- [ ] Qualitative spot-check: 2–3 post-track cards read by hand, still doing structural work (not rule-matched, not hollowed out).
- [ ] Stability report committed to `research/stability-runs/{track}-{date}/`.

### After each track ships

- [ ] One week of shadow-mode running; nightly stability harness on the baseline case plus accumulated cases.
- [ ] Manual spot-check: 3 runs per week, human reads old vs new output.
- [ ] No regression in user-facing artifacts (revised_answer richness, anchor count, tendency detection rate).
- [ ] Old prompt version removed; `prompt_versioning.py` cleaned.

### After all Cycle-1 tracks ship (D-skill → harness → C-step1-3 → B)

- [ ] Re-audit LLM calls: is any remaining call still overloaded under the Section 5a criterion? Decide whether to unhold Track A or C-extended based on evidence.
- [ ] Cost baseline vs before: expected net delta within the ledger (6.0) — D-skill free, C-step1-3 cost-negative, B +$0.004–0.007/run.
- [ ] Revised_answer richness: count model-name mentions per run (D-skill's primary metric); should rise meaningfully against the Apr 16 anchor-dropout regression.
- [ ] Close this handover with a "done" status banner and link to the stability-run evidence.

---

## 10. Quality Gates — What NOT to Do, What TO Do

### DO NOT

- **Do not skip the stability harness.** Same rule as the graph enrichment pilot. Mediocre decomposition is worse than the current monoliths because it creates false confidence.
- **Do not batch Cycle-1 tracks in parallel.** Ship one, measure, absorb lessons, ship the next. Parallel tracks conflate stability signals.
- **Do not use decomposition as an excuse to change semantics.** If extraction currently returns 3–8 reasoning passages, the decomposed version returns 3–8 reasoning passages. If pass1_triage currently scores 25 tendencies, the clustered version scores 25 tendencies. Scope creep during decomposition is a bug.
- **Do not rewrite the "already-good" prompts** (#3 pass2_deep_check, #4 companion_fingerprint). They are the templates. Leave them alone.
- **Do not let a specialist see the 4-lane architecture in its prompt.** The specialist knows its one objective. It does not know about lanes, cards, or downstream consumers.
- **Do not couple tracks.** A failed Track B must not block Track D-skill. They're independent on purpose.
- **Do not add new vendors or models as part of this work.** Same model per call family. Measure decomposition effect in isolation.
- **Do not chase 1.0 stability.** Section 3.6 — if a stage's Jaccard goes to 1.0 after decomposition, the specialist has stopped doing semantic judgment. That's a regression, not a win.
- **Do not run Tracks E or F.** Section 6.0 ledger marks them decorative. Do not ship without explicit reversal.
- **Do not build a SALI-style multi-run ensemble.** Section 0e — too costly, wrong lever.

### DO

- **Read the "already-good" prompts first.** `deep_checks.py:230` and `companion_routing.py` fingerprint. Internalize the tone and structure. Your specialists should feel like siblings.
- **Write the Python glue before the specialists.** Define the assembly function and its input/output types first. Specialists slot in.
- **Measure stability AND cost.** Both are required. Better stability at higher cost is acceptable within the Section 6.0 ledger. Lower stability is a regression regardless of cost.
- **Version every prompt.** Even the specialists inside a track. Rollback must be a config flip.
- **Commit stability-run evidence.** Snapshots + reports go in `research/stability-runs/`. This is the audit trail.
- **Document surprises.** If a specialist consistently outperforms expectations on a dimension, or if a guardrail turns out to be load-bearing when you thought it was dead — write it down. Future decompositions benefit.

---

## 11. What Comes After (Future Sessions)

**Cycle 2 (after D-skill → harness → C-step1-3 → B have shipped and stability data accumulates):**

1. **Re-audit.** Repeat Section 4 against the post-Cycle-1 pipeline. Flag any remaining overload points using fresh stability data.
2. **Decide on held tracks.** Track A (extraction decomposition), C-extended (constraint lock + alignment), and C-fingerprint (hot-seat split) are held by the Section 6.0 ledger. Unhold only if evidence shows the specific monolith is the current bottleneck.
3. **Downgrade specialists where possible.** Narrow specialists may run on cheaper models. Measure per-specialist before committing.
4. **Cross-lane stability metrics.** Once decomposition is stable, compute per-lane "context quality" metrics: input size per call, guardrail count per prompt, objective count per prompt. Surface regressions automatically via the harness.

**Explicitly DO NOT revisit (Section 6.0 ledger):**

- Tracks E (dimension detection split) and F (bullshit subtype split). Decorative.
- SALI-style multi-run ensembles. Wrong lever.

**Out of scope but worth remembering:**

- Fine-tuning a specialist on Lolla-specific judgments (only consider once decomposition is stable, stability-run corpus is large, and a specific specialist proves hard to prompt-engineer to parity).
- Retrieval augmentation for companion verification (delay until Track C-step1-3 ships and proves insufficient).
- Cross-conversation memory (explicitly out of scope — orthogonal to this plan).

---

## 12. Summary of Key Files

| File | Role |
|------|------|
| **This handover** | Section 0 is authoritative | `lolla-skill/research/llm-decomposition-handover.md` |
| `deep-graph-enrichment-handover.md` | Parallel handover for graph side; same principles | `lolla-skill/research/` |
| `run_extract.py:111` | Track A target — extraction monolith | `lolla-skill/scripts/` |
| `prompts.py` | Track B target — Pass 1 triage monolith | `lolla-skill/engine/system_b/` |
| `deep_checks.py:230` | **Template — Pass 2 specialist prompt.** Copy the shape. | `lolla-skill/engine/system_b/` |
| `companion_routing.py` | **Template — Lane 2 fingerprint + recall + verification.** Fingerprint is the prompt template; the overall shape is the decomposition template. | `lolla-skill/engine/system_b/` |
| `testing_harness.py:68` | **NOT LIVE IN SKILL** — deferred to system_b; see Track D | `lolla-skill/engine/system_b/` |
| `SKILL.md` | **Track D-skill target** — Claude's Step 6 revision instructions | `lolla-skill/` |
| `references/output-field-guide.md` | Track D-skill reference — how cards are interpreted for synthesis | `lolla-skill/references/` |
| `structural_coverage.py:251-268` | Track E target — dimension detection | `lolla-skill/engine/system_b/` |
| `bullshit_index.py` | Track F target — per-passage subtype | `lolla-skill/engine/system_b/` |
| `prompt_versioning.py` | **Registration and hashing for every new specialist prompt.** Extend here. | `lolla-skill/engine/system_b/` |
| `pipeline.py:499` | **Template — parallel fan-out helper.** Copy the pattern. | `lolla-skill/engine/system_b/` |
| `scripts/stability_check.py` | **NEW — the stability harness (Section 5c, 8d).** Must exist before any Cycle-1 track ships. Writes to `research/stability-runs/`. | `lolla-skill/scripts/` |
| `research/stability-runs/` | **NEW — per-case, per-track stability evidence directory.** Audit trail for every decomposition decision. | `lolla-skill/research/` |
| HOW_IT_WORKS.md | Full system documentation | `lolla-skill/` |
| PRODUCT_VISION.md | Product doctrine | `Lolla-system-b/` |

---

## 13. Guiding Principles

### Load Is the Lever

The observed failure mode across the Marcus 3-run evidence (Section 3.5) is not prompt wording or model choice — it is too much knowledge flowing through too few LM rounds. Every Cycle-1 decision gates on whether it reduces per-call load (chunking inputs, chunking obligations, narrowing specialists). Variance is a cost we accept, not a property we celebrate; we reduce load to reduce variance, not by ensembling it away. SALI-style multi-run reconciliation is the wrong lever and is explicitly out of scope (Section 0e).

### Decomposition Principle

Each LLM call must have one semantic objective, bounded input, and a narrow guardrail stack. Multi-objective prompts split. Oversized inputs split. Guardrail stacks that rival the instruction in length split.

When splitting, Python assembles. The LLM never sees other specialists' outputs during its own turn (with the single exception of Track D's explicit sequential staging).

### Fidelity Principle (Sully)

Context engineering and iteration are substitutes, not complements. When a call is under-performing, the first move is to narrow its context — fewer objectives, smaller input, tighter prompt — not to iterate on wording at the same complexity. Iterate only after the call is correctly shaped.

### Doctrine Continuity

Lolla's existing doctrine — "LLMs at the probabilistic edges, curated knowledge in the deterministic middle" — is extended here, not replaced. The probabilistic edges must themselves be narrow and composable. The 222 canonical articles and the enriched graph are the deterministic middle; this plan does not touch them. It tightens the probabilistic edges so the deterministic middle actually reaches the user. The closed-vocabulary principle holds: enrichment refines the concept space, never expands it, and the corpus remains the authority — rubrics evaluate, never override.

### Quality Standard

If decomposition succeeds, the observable win is a user-visible revised answer that names more of the curated models (D-skill's primary metric), incorporates more of the curated pressures, and shows measurably tighter per-stage stability across repeat runs on the same input. The graph doesn't need to be smarter. The LLM calls around it need to stop hiding it under monolithic prompts.
