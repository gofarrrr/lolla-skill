# Cross-lane design intent — 2026-04-27

**Status**: investigation memo, no code change. Successor to `HOW_IT_WORKS.md` §"Lane 2 — design intent" (PR #60). Walks Lanes 1 / 3 / 4 through the same lens-or-verdict question that Lane 2 just resolved, names the unifying principle, and proposes concrete actions per lane.

**Why now**: PR #60 codified that Lane 2 is "lens, not verdict" — bounded probabilistic enrichment, graded by Step 6, neighborhood-absorbing. That reframe has implications for the other three lanes that haven't been carried through. Doing the cross-lane walk while the framing is fresh costs a memo; doing it later costs re-derivation.

**What this memo commits to**: an updated framing for each lane (where current framing matches actual reliability) and named gaps (where it doesn't). It does NOT commit to code changes; it scopes them.

---

## §1 The big picture — four lanes, one detector chassis

Lolla audits a strategic conversation through four independent detection paths. Each lane reads the same conversation and asks a different question. None of the four is "the" audit; the union is.

| Lane | Question | Output card | What the user does with it |
|---|---|---|---|
| **Lane 1 — Tendency / Bullshit** | *Does the assistant's reasoning exhibit a known cognitive failure pattern?* | `delta_card.findings[]` (top + secondary), compound groups | Reads it as "here's where my reasoning bent" — most authoritative |
| **Lane 2 — Companion** | *Which curated mental models structurally describe what this reasoning is doing?* | `companion_cheat_sheet.anchors[]` with quotes + curated chunks | Reads it as "useful lens through curated knowledge" — graded |
| **Lane 3 — Frame Pressure** | *What did the question itself bake in as assumed?* | `frame_pressure_card.frame_elements[]` + `reframings[]` | Reads it as "different question to consider" — challenges framing |
| **Lane 4 — Structural Coverage** | *What dimensions of the problem did the answer never enter?* | `structural_coverage_card.gap_questions[]` per uncovered dimension | Reads it as "discovery questions" — surfaces gaps |

### The shared chassis

All four lanes use the same architectural pattern (HOW_IT_WORKS.md §"Probabilistic Edges, Deterministic Middle"):

1. **Probabilistic detection** at the LLM edge — the LLM reads conversation text and produces a structured judgment.
2. **Deterministic routing / chunk gathering** in the curated middle — KG traversal, anti-echo filtering, budget-constrained selection.
3. **Substring / schema validation** at every quote and identifier — paraphrased evidence is dropped, malformed JSON is detectable.

The probabilistic edge is where each lane's noise lives. The deterministic middle absorbs that noise into curated chunks the LLM doesn't have natively. **Lane 2's reframe (PR #60) named one specific instance of this absorption mechanism — "the graph absorbs anchor imprecision." The unifying claim for the system is the same: each lane is a noisy detector wired into a clean curated routing layer.**

### Where Step 6 fits

Step 6 (Claude reconsiders, SKILL.md §"Step 6") is the integration layer. It reads all four cards and produces a revised position. Two integration mechanisms:

- **Anchor-naming invariant** (SKILL.md:350): every Lane 2 anchor goes to §1 / §2 / §3 (priced in / set aside / drove a change). No silent skipping.
- **Three-treatment vocabulary** (SKILL.md:352-358): each Lane 2 anchor gets *Primary pressure* / *Secondary lens* / *Set aside with a reason* based on the strength of its evidence.

**Critical observation**: the three-treatment vocabulary is **Lane-2-specific**. Lane 1 findings, Lane 3 reframings, and Lane 4 gap questions don't have an equivalent graded vocabulary. They're presented in Step 6 at the strength their lane's design implies.

That's a deliberate asymmetry IF each lane's framing is calibrated to its actual reliability. It's a calibration mismatch IF some lane is more probabilistic than its framing implies but lacks the vocabulary to hedge.

This memo's central question: **for each of Lanes 1 / 3 / 4, is the lane's framing calibrated to its actual reliability?**

---

## §2 Lane 1 — Tendency / DeltaCard

### What it produces

Lane 1 is two-stage:

- **Pass 1 (family-clustered triage)**: 6 parallel LLM calls, each scoring 3-5 tendencies in its cluster (authority / closure / incentive / availability / self-regard / residual). Score ≥4 → tendency enters the "triggered" set. Cluster-specific confusion guardrails reduce per-call obligation. (PR #37, refactor from monolithic 25-tendency triage; Jaccard improved 0.50 → 0.70.)
- **Pass 2 (deep checks)**: 1 LLM call PER triggered tendency, parallel up to 8 concurrent. Each call sees ONE tendency's definition + sub-pattern menu + the conversation source. Returns: detected/not-detected, confidence, sub-pattern, specific passage, severity. **Per-tendency context isolation is the key reliability mechanism.**

The DeltaCard is then assembled deterministically: top findings get full treatment (challenge statement, reversal trigger, corrective model, supporting models, tensions); secondary findings get one-line summaries; compound patterns flag lollapalooza.

### Current framing (claimed reliability)

`HOW_IT_WORKS.md` line 47: *"Lolla reads the thinking, not the topic. It detects reasoning patterns... 'This reasoning closes uncertainty without a stop-rule, so Doubt Avoidance is in play' is correct behavior."*

`HOW_IT_WORKS.md` §"Step 4 chat" implicitly treats DeltaCard findings as the most authoritative output. SKILL.md doesn't give Lane 1 findings an explicit graded vocabulary like Lane 2's three treatments. The implication: Lane 1 findings are presented at default authority — "the answer exhibits this tendency, here's the corrective model."

### Reliability profile (what's actually happening)

Lane 1's noise is **structurally different from Lane 2's**:

- **Pass 1 stochasticity is at the WHICH-tendencies-to-look-at layer.** Family-clustering reduced this to ~0.70 Jaccard. That's roughly Lane 2's verifier baseline.
- **Pass 2 stochasticity is at the IS-IT-PRESENT-GIVEN-WE'RE-LOOKING layer.** Per-tendency isolation means Pass 2 is checking ONE thing in isolation — much less obligation than Lane 2's verifier (which reads up to 60 candidates in one call).
- **Pass 2's per-call accuracy is plausibly substantially higher than Lane 2's verifier**, because the load is dramatically lower. Pass 2 is the "already-good model" callout in `research/llm-decomposition-handover.md` §0c — it's the template Lane 2 was supposed to emulate but couldn't because of the candidate-cap shape.

So Lane 1's noise lives at the triage layer (which tendencies even get inspected) more than at the deep-check layer (whether a triggered tendency is genuinely present). The DeltaCard's "top findings vs secondary findings" assembly is a natural gradation that **implicitly hedges the triage-layer noise** — top findings are the high-confidence tendencies that deep-check confirmed; secondary findings are the lower-confidence ones.

### Empirical evidence for current framing

- PR #37 corpus validation (10 cases + Marcus): whistleblower 0→2, real_estate 0→1, Marcus 3→4, others stable. One prior detection corrected (parenting_teen authority-misinfluence on RAINN references — over-fire on legitimate evidence-application).
- Family-clustering refactor: Pass 1 Jaccard 0.50 → 0.70.
- No recent E1-style multi-run analysis of Pass 2 on a fixed conversation under controlled conditions.

### Gap analysis

**Lane 1's framing roughly matches its actual reliability**, with one potential gap:

- **Top vs secondary findings is the gradation, but it's not labeled as such for Step 6.** Lane 2 has three explicit treatments (primary pressure / secondary lens / set aside). Lane 1 has top/secondary findings emitted from the pipeline — but Step 6 doesn't have an explicit vocabulary that maps these to rhetorical strength in the revised answer. A "top finding" lands in §1 / §3 the same way a "secondary finding" does. **The reader can't tell whether Step 6 considered the secondary findings carefully or skimmed past them.**
- **No multi-run reliability measurement on Pass 2 specifically.** The 0.70 Jaccard claim is from Pass 1 (family-clustering refactor era). Pass 2's stability under fixed Pass 1 input has never been measured the way Lane 2's E1 measured the verifier.

### Recommended action for Lane 1

| Priority | Action | Cost |
|---|---|---|
| Medium | Add a Step 6 graded vocabulary for top vs secondary findings, mirroring Lane 2's three-treatment shape. Top findings = full §1/§3 treatment; secondary findings = "noted as lower-confidence pressure" framing. | Doc edit only (SKILL.md + HOW_IT_WORKS.md) |
| Low | Run an E1-style measurement of Pass 2 reliability on fixed Pass 1 input across one or two corpus cases. Confirm or falsify the "Pass 2 is high-accuracy in isolation" claim. | ~$5-10 in LLM calls |

**Default position**: Lane 1's framing is acceptably calibrated. The verdict shape matches the per-tendency isolation of Pass 2. Top/secondary differentiation is the natural hedge. Action items are polish, not blockers.

---

## §3 Lane 3 — Frame Pressure

### What it produces

Lane 3 is two LLM calls:

- **Frame extraction** (1 call): reads the user's source turns. Returns 0-5 `frame_elements` typed as `assumption | mutable_constraint | suppressed_counterfactual`, each with `evidence_quote` (literal user-turn substring), `frame_pattern` (from curated Wave 5 taxonomy), `fragility_signal`, `inquiry_stage`, `likely_default`. Validation drops elements with empty fields.
- **Reframing generation** (1 call): generates up to 2 alternative questions, each with `reframed_question`, `what_opens` (reasoning path), `reframe_move_type`, `grounding_model` (which model drove it).

Anti-echo: Lane 3 excludes models already used in Lane 1.

### Current framing (claimed reliability)

`HOW_IT_WORKS.md` line 587: *"Lane 3 is most powerful on short conversations where the question itself constrains the answer space."*

The doc explicitly acknowledges a known weakness (§"Lane 3 — Frame Pressure" in `full-system-audit-2026-04-23.md`): *"when `original_framing` is unstable (first user turn is a context-dump rather than a clean question), Lane 3's extraction is noisy."*

Step 6 absorbs Lane 3 reframings into the revised answer as "what if" challenges. No graded vocabulary; reframings present at default strength.

### Reliability profile (what's actually happening)

Lane 3's reliability has two components:

- **Frame extraction**: reads only the user's turns (not the assistant's), so the surface area is smaller than Lane 1 / Lane 2. Smaller surface usually means tighter calibration. The audit noted instability when the first user turn is a context-dump, but Phase 2a (PR #15) showed verbatim-grounded frame extraction is qualitatively cleaner than paraphrase-grounded.
- **Reframing generation**: produces creative alternative questions. This is inherently more stochastic than detection — the LLM is GENERATING content, not classifying it. Two reruns may produce two different but equally-defensible reframings.

**The reframings themselves are structurally lens-shaped, not verdict-shaped.** A reframing isn't a claim ("the user is wrong about X"); it's an offer ("what if X weren't fixed?"). The user reads the offer and either engages or doesn't.

### Empirical evidence for current framing

- Phase 2a corpus validation (10 cases): +22% elements after Lane 3 migrated to verbatim grounding, drop rate 0.069 → 0.000, zero regressions.
- Production bug fix on `real_estate` (old path produced empty Lane 3 cards 2/3 runs).
- **No recent multi-run reliability measurement.** The 2026-04-27 stability investigation cycle was Lane-2-only.

### Gap analysis

Lane 3 has the most underdetermined framing of the three lanes:

- **Reframing-generation reliability is unmeasured.** If two reruns of Lane 3 produce two completely different reframings ("what if you weren't constrained by money?" vs "what if you didn't need to decide this at all?"), and both are valid, that's H5-shaped honest hypothesis diversity (similar to Lane 2's RMR ↔ Optionality stochastic-edge substitution). The user gets value from the diversity, but the system never names that diversity.
- **No graded vocabulary.** Step 6 absorbs reframings at default strength. There's no explicit way to say "this reframing is sharp evidence, this one is a softer alternative."
- **Lane 3 anti-echo with Lane 1** is doctrine but not measured. If Lane 3's grounding_model frequently overlaps with Lane 1's selected_model_ids, Lane 3 silently produces fewer reframings — not necessarily worse, but the reduction is invisible.

### Recommended action for Lane 3

| Priority | Action | Cost |
|---|---|---|
| Medium | Run an E1-style measurement of Lane 3 reliability on a fixed corpus case. Specifically: N=5 reruns, measure (a) frame_element extraction Jaccard on user-turn substrings, (b) reframing semantic overlap (manual, since reframings are free-text). | ~$5-10 |
| Medium | Add a design-intent paragraph to HOW_IT_WORKS.md §"Lane 3" capturing: reframings are GENERATIVE (more stochastic than detection); the user gets value from diversity, not consistency; Step 6 absorbs reframings as offers, not claims. | Doc edit only |
| Low | Measure anti-echo dropout rate: how many Lane 3 reframings does the anti-echo policy silently exclude? If high (>20% on average), the policy may be costing user value. | Adjustment to existing eval scripts |

**Default position**: Lane 3 is currently under-framed but its actual behavior is structurally lens-shaped. A design-intent paragraph should make this explicit.

---

## §4 Lane 4 — Structural Coverage

### What it produces

Lane 4 is three LLM calls (one optional):

- **Question classification** (LLM call 1): classifies into causal-diagnosis / decision-evaluation / action-planning / prediction.
- **Dimension detection + coverage check** (LLM call 2): checks the question + answer against 15 structural dimensions. A dimension is "covered" only if the answer explicitly identifies the tension, reasons through both sides, and reaches a position. Hard cap of 5 gaps.
- **Gap question generation** (LLM call 3, only when gaps exist): generates discovery questions per uncovered dimension.

Routing: deterministic (Wave 6 KG lookup, 82 model bridges across 74 unique models). Anti-echo against Lanes 1, 2, 3.

### Current framing (claimed reliability)

`HOW_IT_WORKS.md` line 587 (canonical): *"Lane 4 is **informative only**. It doesn't influence Lanes 1-3, doesn't change the delta card, doesn't alter companion routing. It sits at the end and surfaces structural angles the decision-maker might not have considered. Even imperfect gap detection is valuable because the gap questions — not the coverage labels — are the product."*

This is **the most explicit lens-shaped framing in the system.** It's already what PR #60 just codified for Lane 2 — *the questions are the product, the labels are the routing.*

### Reliability profile (what's actually happening)

Lane 4's reliability:

- **Question classification** is the lowest-load call (4 categories, narrow input). Likely high accuracy.
- **Dimension detection** has medium load (15 dimensions × covered/uncovered judgment). Phase 2b corpus validation showed "+15% gap_qs" and "0-gap-qs anomaly eliminated" after explicit enum-checklist reminder for abstract dimensions.
- **Gap question generation** is creative (similar to Lane 3 reframings). More stochastic than detection.

The hard cap of 5 gaps is a structural hedge against over-flagging.

### Empirical evidence for current framing

- Phase 2b corpus validation (10 cases): +15% gap_qs with stricter coverage bar after migration; 0-gap-qs anomaly eliminated.
- Marcus A/B: same 4 dim_ids + same 12 gap_qs count between paths.
- Lane 4 calibration memory entry exists (`project_lane4_calibration.md`): documents FP/FN patterns with grok-4.1-fast and the informative-lane philosophy.
- No recent multi-run stability measurement.

### Gap analysis

Lane 4's framing is **the canonical example of correct calibration**. The doc already says "gap questions are the product, labels are routing." That IS lens-shaped framing.

The only gap is empirical confirmation:
- We have no recent E1-style stability measurement on Lane 4. Whether N=5 reruns produce overlapping gap question sets, or different-but-defensible alternatives, isn't measured.

### Recommended action for Lane 4

| Priority | Action | Cost |
|---|---|---|
| Low | Run a small N=3 multi-run measurement to confirm gap-question diversity is bounded (i.e., reruns produce overlapping discovery-question sets, not chaotic alternatives). If reruns are wildly different, the "informative-only" framing still holds but might warrant explicit note. | ~$3-5 |

**Default position**: Lane 4 framing is correctly calibrated. No code change needed. The "informative only" doctrine is the explicit canonical statement of what PR #60 just landed for Lane 2. **Lane 4 was the model; Lane 2 caught up.**

---

## §5 The unifying principle

After walking the four lanes, the unifying claim is sharper than I had it before reading them in order:

> **Each lane is an independent probabilistic detector wired into a deterministic curated routing layer. Step 6 integrates the four detectors. The system's design intent is that each detector's framing reflects its own reliability profile — verdict shape where reliability is high, lens shape where reliability is bounded.**

The four lanes ALREADY have differentiated framings:

| Lane | Framing shape | Why |
|---|---|---|
| Lane 1 | Verdict-on-the-tendency, hedged-on-which-tendency-to-look-at | Pass 2 isolation gives high per-call accuracy; Pass 1 noise hedged by top/secondary differentiation |
| Lane 2 | Lens (PR #60) | Verifier reads up to 60 candidates per call → high load → bounded variance; graph absorbs anchor imprecision |
| Lane 3 | Generative offers, currently under-framed | Reframings are CREATIVE, not classified — diversity is a feature; doc currently doesn't say so |
| Lane 4 | Informative-only, lens by design | Gap questions are the product; coverage labels are routing keys |

**Lane 4 is the model for what good looks like**: explicit doctrine that names what's the product (questions) vs what's routing (labels). PR #60 brought Lane 2 to the same place. Lanes 1 and 3 are not yet there, but for different reasons — Lane 1 is mostly fine and just needs a Step 6 vocabulary to make its top/secondary differentiation visible, Lane 3 is genuinely under-framed.

### Where Lane 2's reframe propagates

| Lane | Should Lane 2's "lens, not verdict" reframe propagate? |
|---|---|
| Lane 1 | **Partially** — adopt Step 6's graded vocabulary (top finding ≈ primary pressure; secondary finding ≈ secondary lens). Don't adopt the "graph absorbs imprecision" claim — Lane 1's reliability story is different (per-tendency isolation, not graph absorption). |
| Lane 3 | **Yes**, with adjustment. Lane 3 is also "lens, not verdict" — reframings are offers, not claims. A design-intent paragraph similar to PR #60 would land. |
| Lane 4 | **Already there.** Lane 4's "informative only" doctrine is the explicit canonical of what PR #60 codified for Lane 2. No propagation needed. |

### Where Lane 2's reframe does NOT generalize

PR #60 said *"the graph absorbs anchor imprecision"* — Lane 2's neighborhood-of-curated-knowledge mechanism. This is a **Lane 2-specific** absorption mechanism. Lane 1 doesn't have a "graph neighborhood" in the same way (it has tendency → corrective-model routing, but the user sees a single corrective model per finding, not a neighborhood). Lane 3 doesn't have one. Lane 4 doesn't have one.

Each lane has its OWN absorption mechanism:
- Lane 1: per-tendency isolation in Pass 2 + top/secondary differentiation in DeltaCard
- Lane 2: 222-model graph traversal pulls the neighborhood
- Lane 3: anti-echo + grounding_model citation
- Lane 4: hard cap of 5 gaps + "questions are the product, labels are routing" doctrine

The unifying principle isn't "the graph absorbs noise" — it's "each lane has a structural mechanism that absorbs its own type of noise, and the framing should match the actual reliability after that mechanism applies."

---

## §6 Cross-lane interaction risks

Three known interactions worth naming:

### 6.1 Anti-echo policy

Lane 2 anti-echoes against Lane 1 (`selected_model_ids`). Lane 3 anti-echoes against Lane 1. Lane 4 anti-echoes against Lanes 1, 2, 3 (broadest scope).

The risk: a model that's *correctly* surfaced in Lane 1 (as a tendency's corrective model) but *also legitimately fits* Lane 2's anchor-detection or Lane 3's reframing — the anti-echo silently drops it from the later lane. The user gets one mention instead of two, and the reduction is invisible.

This is named in PR #60's design-intent paragraph as a future-trigger condition for Lane 2 work ("Lane 1 anti-echo dropping good Lane 2 anchors silently"). Same risk applies to Lane 3 and Lane 4.

**No measurement exists for anti-echo dropout rate.** The prior audit's open question (§12.4: "Is the anti-echo policy helping or hurting quality?") is still open.

### 6.2 Step 6's grading asymmetry

Lane 2 has the three-treatment vocabulary. Lane 1 has top/secondary findings (which Step 6 handles implicitly). Lane 3 has no graded vocabulary. Lane 4 has the question-vs-label distinction.

If Step 6 inherits the three-treatment vocabulary's discipline only for Lane 2, the other lanes' evidence may land at miscalibrated strength. The most likely failure: Lane 1 secondary findings get §1/§3 treatment as if they were primary, OR Lane 3 reframings get presented as more authoritative than they are.

### 6.3 Compound detection (lollapalooza)

Lane 1 has compound detection — multiple tendencies on overlapping evidence get grouped as compound_groups. There's no equivalent for cross-lane compounding. If Lane 1 detects a tendency AND Lane 2 detects a related anchor AND Lane 3 reframes around the same axis — the user sees three separate signals, even though they're describing the same structural issue from different angles.

This is by design (multiple overlapping signals, swiss-cheese pattern). But it can read as redundancy in Step 6's revised answer if Step 6 doesn't unify them.

---

## §7 What Step 6 needs to do well (and currently does asymmetrically)

Reading SKILL.md §"Step 6" (lines 320-403) carefully:

**Lane 1 handling in Step 6**: SKILL.md says "Use the delta card findings as evidence for §1/§2/§3 reasoning. Top findings get foregrounded; secondary findings can be acknowledged or left implicit if not load-bearing." — the implicit gradation is there in prose, not in a labeled vocabulary.

**Lane 2 handling**: explicit three-treatment vocabulary with worked examples.

**Lane 3 handling**: SKILL.md says "Reframings can become §1 challenges to your original framing or §3 questions you should re-engage." — the absorption mechanism is named (§1 vs §3) but the gradation isn't.

**Lane 4 handling**: SKILL.md says "Surface gap questions as discovery questions, not as findings. They go in §3 if relevant; otherwise they can be left for the memo / Observatory." — clear separation between findings and discovery questions.

**The Step 6 vocabulary asymmetry**:

| Lane | Has explicit graded vocabulary in SKILL.md? |
|---|---|
| Lane 1 | Implicit (top vs secondary in prose) |
| Lane 2 | **Explicit** (Primary pressure / Secondary lens / Set aside with a reason) |
| Lane 3 | Implicit (§1 challenge vs §3 reengagement) |
| Lane 4 | Explicit separation (findings vs discovery questions) |

Lane 2 is the most heavily verbalized; Lane 4 is the cleanest by structural separation; Lanes 1 and 3 are implicitly graded. **None of these are wrong; they reflect the differentiated reliability of the lanes.** But making the implicit explicit might tighten Step 6's discipline.

---

## §8 Recommended actions, prioritized

### High-priority (likely to improve product)

1. **Lane 3 design-intent paragraph in `HOW_IT_WORKS.md`** — single paragraph similar in shape to PR #60's Lane 2 paragraph. Names: reframings are GENERATIVE (more stochastic than classification); the user gets value from diversity, not consistency; Step 6 absorbs reframings as offers, not claims. Cost: doc edit only.

2. **Lane 1 top/secondary vocabulary in SKILL.md** — make the implicit Step 6 gradation explicit. Top findings = primary §1/§3 treatment; secondary findings = "noted as lower-confidence pressure" framing. This mirrors Lane 2's three-treatment vocabulary at the lane appropriate for Lane 1's reliability profile. Cost: doc edit only.

### Medium-priority (closes empirical gaps)

3. **Lane 1 Pass 2 reliability measurement** — N=5 multi-run on a fixed corpus case to confirm Pass 2's per-tendency isolation produces high per-call accuracy. Cost: ~$5-10. Result confirms or falsifies the framing in §2 above.

4. **Lane 3 multi-run measurement** — N=5 reruns on a fixed corpus case. Measure frame_element extraction Jaccard + reframing semantic overlap. Cost: ~$5-10.

5. **Anti-echo dropout measurement** — across all three anti-echo edges (Lane 1 → Lane 2, Lane 1 → Lane 3, Lanes 1+2+3 → Lane 4), measure how often anti-echo silently drops a model the lane would have surfaced. If high, the policy is paying a hidden cost. Cost: instrumentation + corpus rerun.

### Low-priority (polish)

6. **Lane 4 N=3 stability measurement** — confirm gap-question diversity is bounded. Cost: ~$3-5.

7. **Cross-lane compounding investigation** — open the question of whether Step 6 should explicitly unify cross-lane signals about the same structural issue, or whether the swiss-cheese-redundancy framing is correct as-is. Memo, not code.

### Explicitly NOT recommended

- **Don't propagate Lane 2's "graph absorbs imprecision" claim to other lanes.** Each lane has its own absorption mechanism. The unifying principle is "match framing to actual reliability," not "all lanes use the graph the same way."
- **Don't add new lanes.** The 4-lane decomposition is in current shipped state; adding a fifth without evidence of unmet need would be premature.
- **Don't refactor anti-echo without measurement.** Anti-echo is doctrine; the dropout rate is unmeasured. Fix the measurement gap first.
- **Don't re-open Lane 2 prompt work** unless one of PR #60's four triggers fires.

---

## §9 What this memo does NOT do

- Does NOT propose code changes. All recommendations are doc-edit (high-priority) or measurement (medium-priority) work.
- Does NOT measure any lane's actual reliability. The §3, §4 reliability profiles are inferences from existing PR validation evidence + structural reasoning.
- Does NOT commit to a sequencing order beyond priority tiers above.
- Does NOT change SKILL.md's anchor-naming invariant or three-treatment vocabulary for Lane 2 — those are correct as-is.
- Does NOT touch the swiss-cheese redundancy doctrine. Multiple overlapping signals across lanes is the design intent; this memo confirms it.
- Does NOT address Step 6 quality independently of the four lanes' inputs. Step 6 quality investigation is a separate concern (memo would mention orchestration tier — Opus / Sonnet / Haiku — and the current self-identification floor; out of scope here).

---

## §10 The unifying status update

After this walk:

- **Lane 4** is the canonical example of correctly-calibrated lens framing. No work needed. Optional N=3 confirmation.
- **Lane 2** caught up in PR #60. Lens framing codified. Empirical foundation in PR #59 baselines.
- **Lane 1** is roughly correctly framed but the Step 6 vocabulary asymmetry leaves implicit work for the orchestrator. Two doc edits (Step 6 vocabulary + optional Pass 2 measurement) close the gap.
- **Lane 3** is the most under-framed of the four — generative reframings deserve their own design-intent paragraph similar to PR #60. Doc edit + optional measurement closes the gap.

The system's design intent — *"LLMs at the probabilistic edges, curated knowledge in the deterministic middle, Step 6 grades"* — survives the walk intact. What needs work is making the implicit per-lane gradation explicit where the orchestrator (Claude in Step 6) has to do that grading from prose rather than from a labeled vocabulary.

This is small work with high leverage. The total cost of the high-priority + medium-priority items is roughly two focused sessions and ~$30 in LLM calls. The output is a system whose four lanes' framings are each calibrated to their actual reliability profile, and whose Step 6 vocabulary makes the gradation explicit per lane.

---

## §11 Status

- This memo: investigation, no code changes
- Next deliverable (if approved): the Lane 3 design-intent paragraph in HOW_IT_WORKS.md (high-priority item 1) + Lane 1 top/secondary vocabulary in SKILL.md (high-priority item 2). Two doc-only PRs.
- Measurement work (medium-priority items) deferred until you decide whether the framing changes are sufficient or whether empirical confirmation matters.
- The remaining open questions (anti-echo dropout, cross-lane compounding) are real but smaller leverage; pick up later or never depending on user-visible signal.

The simple bottom line:

> Lane 2's lens-not-precision reframe was a specific instance of a broader principle: each lane has its own reliability profile and its own absorption mechanism, and the framing should match. Lane 4 has had this from day one. Lane 2 just got there. Lane 1 is mostly there but Step 6 vocabulary is implicit. Lane 3 is the gap. Two doc paragraphs close most of it.
