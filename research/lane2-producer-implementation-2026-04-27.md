# Lane 2 producer-implementation memo

Date: 2026-04-27
Branch: `docs/lane2-implementation-memo-2026-04-27`
Status: implementation memo — binds the next coding PR(s) on Lane 2 producer changes
Predecessor memo: `research/lane2-producer-stability-design-2026-04-27.md` (the design memo that scoped the investigation)

Inputs (closed investigation phase):
- `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md` (incl. §8 post-script)
- `research/stability-runs/lane2-quote-repair-smoke-2026-04-27/characterization.md`
- `research/lane2-quote-repair-validation-amendment-2026-04-27.md`
- `research/stability-runs/lane2-stability-experiments-2026-04-27/e5-consensus-simulation.md` (PR #47)
- `research/stability-runs/lane2-stability-experiments-2026-04-27/e4-broad-meta-sufficiency-rubric.md` (PR #48)
- `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism.md` (PR #49)
- `research/stability-runs/lane2-stability-experiments-2026-04-27/e1-verifier-stochasticity.md` (PR #51)
- `research/stability-runs/lane2-stability-experiments-2026-04-27/e3-fingerprint-variance.md` (PR #52)

## Revision note (2026-04-27, pre-merge)

This memo was substantively revised before merge to address ten holes identified in pre-merge review. Summary of changes:

1. **Track 1 form specification** (§3): added explicit prompt form — incremental edit, single-pass, rule-based, no few-shot, output schema unchanged.
2. **Track 1 Tier 3 protection** (§3 #3 + §3 Track 4 cross-reference): added explicit prompt-level markers for Step Back / WYSIATI / RH so Tier 3 has real protection (was previously gate-resistant with no prompt coverage).
3. **Reject-reason taxonomy compatibility** (§3 Track 1): added consumer list, compatibility tests, migration-note requirement.
4. **Track 2 form commitment** (§3 Track 2): committed to Form B (in-place tightening). Form A rejected to preserve the bullet 4 vs bullet 2 curation distinction.
5. **E6 sensitivity scope** (§3 Track 3): expanded from one frozen slate (rerun4) to two (rerun4 + rerun5) to guard against rerun4-specific friendliness/hostility to the new prompt.
6. **E6 thresholds** (§3 Track 3): mean Jaccard threshold downgraded from 0.85 (unjustified, above E1 baseline) to 0.75 (below baseline, appropriate for tighter prompt). Catastrophic threshold set at 0.60. Friction-yield collapse rule added to fire at Phase A, not Phase B.
7. **Friction-yield recovery rule** (§3 Track 3): explicit Phase-A rollback trigger if accept count or stable-core acceptance collapses — was previously detectable only at Phase B.
8. **Phase B reporting tables** (§4): four required tables operationalized — repair-local trust, whole-run trust, strict-yield regression guard, Path D attribution.
9. **Path D-fingerprint trigger threshold** (§5): committed at ≥ 25% slate-rotation-classified noise, calibrated against E3's empirical 20% per-anchor miss rate.
10. **Cross-provider metadata** (§7): added concrete requirements (provider+model recorded in run JSON, re-run procedure, audit-diff flag for backing-model mismatch).

In addition: §1 Evidence summary corrected to reflect E3's pre-merge correction commit `08aaf41` (RMR/Optionality are 5/5 in fresh-fingerprint slates, not 0/5; their churn is verifier-side only). §1 also adds the empirical ~20% per-anchor slate-rotation miss rate as the Path A reach ceiling.

PR sequencing note: this memo's branch was rebased onto post-merge main after PR #51 (E1) and PR #52 (E3) merged, so cited paths resolve correctly.

## Opening — what this memo commits to

The five pre-registered experiments closed. The §7 decision tree fires two rows. This memo binds the next implementation work on Lane 2 producer changes by:

- committing to **Path B (verifier prompt restructure)** as the first track shipped
- pre-registering **E6 (verifier prompt-test on frozen slate)** as the gating experiment for Path A's deployment breadth
- committing to a **tiered Path A (anchor sufficiency)** design whose Tier 1 deployment is conditional on E6's residual measurement
- committing to a **scoped KG curation tightening** on Checklists `select_when` bullet 4, in parallel with Path B
- defining **Phase A (development checkpoint) and Phase B (merge ship gate)** acceptance criteria with numeric pass/fail
- defining **Path D-fingerprint** as a contingent second track with a non-trivial attribution-based trigger, not an absolute-Jaccard threshold

The investigation phase was about discriminating between candidate fixes. This memo's job is to commit the implementation track, with pre-registered metrics so the work isn't relitigated post-hoc.

## §1 Evidence summary — what the experiments proved

| Stage | Verdict | Source |
|---|---|---|
| Recall | Deterministic given fixed fingerprint, source, KG, embeddings off | E2 (PR #49) |
| Verifier | Stochastic with structure: stable core (mean Jaccard 0.800, accept count exactly 5), stochastic edge (RMR ↔ Optionality substitution; both 5/5 in slate, churn is verifier-side) | E1 (PR #51) |
| Fingerprint | Trajectory-stable (same 6-step reasoning trajectory across all 5 runs), granularity-moderately-unstable (8-vs-7 split, "signal vs noise" theme in 3/5 runs only), text-unstable (5 distinct phrasings/quote-selections per slot), downstream slate Jaccard 0.615 | E3 (PR #52) |
| Sufficiency rubric | 5/9 anchors gate-buildable (rubric specifiable), 3/9 prompt-only, 1 control | E4 (PR #48) |
| Consensus | k=2 makes trust worse (50% noisy vs 31% at k=1); k=3 collapses friction. **Path C ruled out as first lever.** | E5 (PR #47) |

The smoke variance (14 unique anchors / 4 reruns) decomposes as compound effect of fingerprint stage (Jaccard 0.615) and verifier stage (Jaccard 0.800), with deterministic recall between them.

The most load-bearing finding: **`cognitive-dissonance` and `checklists` are accepted in 5/5 verifier runs on identical input AND appear in 4/5 fresh-fingerprint slates** (each missing from exactly one run; CD missing run 5; Checklists missing run 1; TTV missing run 2). The verifier-stable failure class survives both variance sources. This is the failure class Path A+B targets.

**~20% per-anchor slate-rotation miss rate** is the empirical ceiling on Path A's reach: for the 80% of fresh runs where the gate sees the bad anchor, it can act; for the 20% where slate rotation hides it, the gate doesn't get to act. This is the empirical surface area for Path D-fingerprint's contingent trigger (§5).

**Correction note**: an earlier draft of this memo stated RMR and Optionality "drop out of fresh-fingerprint slates." That was based on a false claim in PR #52's initial draft (corrected commit `08aaf41`). RMR and Optionality are in **5/5** fresh-fingerprint slates. Their E1 substitution is purely verifier-side judgment variance, not fingerprint-input variance.

## §2 KG vs verifier attribution (per anchor)

A verified split, from independent reading of `data/knowledge_graph.json`:

- **`cognitive-dissonance`** (`data/knowledge_graph.json:3225-3234`): all 5 `select_when` bullets are mechanism-bearing (public/ego commitment + contrary evidence, motivated reframing, post-hoc rationalization, evidence avoidance, suspiciously aligned reasoning). The KG is tight. The case-1 quote ("less than 1 in 5 conversion") is assistant pushback against optimistic assumption — not motivated reframing of a held belief by the user. **Pure verifier-side overmatch.** Path A+B is the right layer.
- **`checklists`** (`data/knowledge_graph.json:20479-20566`): bullets 1 and 2 are tight (omission risk, "every time"); `input_type` is "repeatable execution with omission risk." But **bullet 4 — "Working memory limits are turning a complex multi-step task into cognitive clutter or inconsistent execution"** — drops the recurrence requirement and reads as "any multi-step task." This invites "list of three options ⇒ Checklists." **Verifier-side error AND a small KG breadth issue.** Path A+B targets the verifier-side error; a one-line curation tightening (Track 2 below) closes bullet 4.

## §3 Architecture commitment

### Track 1 — Path B (verifier prompt restructure)

#### Form (committed)

- **Edit shape**: incremental edit to the existing verifier prompt builder (`_build_verification_user_prompt_from_packet` in `engine/system_b/companion_routing.py`), not a wholesale replacement. The existing CONTEXT/SOURCE/fingerprint/candidates structure is preserved; the changes are additive instructions and explicit negatives.
- **Output schema**: unchanged (existing accept/reject schema with reason field). Reject reasons are extended (see #4 below).
- **Decision style**: single-pass judgment per candidate, not an explicit "explain reasoning before deciding" two-step. Two-step would add latency and a second LLM call per candidate; existing single-pass is preserved.
- **Few-shot vs rule-based**: rule-based instructions only (no in-prompt examples). Examples have a known stochastic-amplification cost (the LLM may anchor on the example wording) that the team has hit before. Rules + explicit negatives have produced cleaner regression behavior in prior verifier-prompt iterations.

#### Content (committed)

The rewritten prompt body adds, in this order:

1. **Mechanism, not topic.** "A literal quote must instantiate the model's local mechanism markers, not just be topically adjacent. A quote that is *about* the same domain as the model is not evidence the model is *in play*."
2. **Explicit anchor negatives** for the verifier-stable failure class plus the stochastic-edge anchor that's a live wound:
   - **Reasoning Mode Router**: clarifying questions before tactics is NOT mode/path selection. RMR's mechanism (per `data/knowledge_graph.json:15010-15014`) is choosing among reasoning modes (diagnosis vs execution vs exploration); "asking before answering" does not satisfy this.
   - **Cognitive Dissonance**: the assistant pushing back on the user's optimistic assumption is NOT cognitive dissonance. CD requires a *holder* of a commitment whose reasoning is bent to protect it. Pushback on someone else's claim does not satisfy.
   - **Checklists**: a numbered list of options or one-time recommendations is NOT a checklist. Checklists require *recurring execution with omission risk*.
3. **Tier 3 anchor markers** (per Hole 5 below — Tier 3 needs prompt-level protection since no gate covers it):
   - **Step Back**: requires explicit reframing/distance from the immediate problem ("zoom out," "first principles," "before getting tactical"). General advisory language is not Step Back.
   - **WYSIATI**: requires the source surfacing what is NOT visible/known/measured ("we don't see," "what's missing"). General incomplete-information language is not WYSIATI.
   - **Representativeness Heuristic**: requires the source naming a base-rate / category-membership confusion. Generic similarity language is not RH.
4. **Respect `danger_when`.** Where a model's `danger_when` markers are present in the source, that is evidence *against* selection, not for.
5. **Reject reason taxonomy.** Add `mechanism_topical_only` and `recurring_execution_required` as new rejection reasons distinct from existing ones (see compatibility note below).

#### Reject-reason taxonomy compatibility

The reject-reason field is consumed by:
- **Audit corpus comparison** (`research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md` §7.2 schema and downstream characterization scripts) — adding new enum values does not break existing rows; old runs continue to use old reasons.
- **Step 6** (skill-side) — does not branch on specific reject-reason values; treats the field as opaque metadata.
- **Run archives** under `~/.local/share/lolla/runs/` — schema is forward-compatible; consumers iterate values rather than enumerate.

**Compatibility tests required in the implementation PR**:
- Existing audit-corpus diff scripts run cleanly against a sample post-Track-1 run (no parser errors on new reject reasons).
- A snapshot test in `tests/test_lane2_contextual.py` capturing the new reason strings (so future renames are detected).
- A migration note in the implementation PR description if any consumer in this list turns out to enumerate reject reasons (verify by grep for the existing enum values across the repo before merge).

This is a single-file change in `engine/system_b/companion_routing.py` (verifier prompt builder + reject-reason enum extension) plus the regression tests above.

### Track 2 — Curation tightening on Checklists bullet 4 (parallel to Track 1)

**Committed form (Form B in the original split)**: tighten bullet 4 in place at `data/knowledge_graph.json:20486` to:

> "Working memory limits in a *recurring* multi-step process are turning execution into cognitive clutter or inconsistent execution across instances."

Form B is committed (not Form A) because preserving bullet 4 as a distinct bullet from bullet 2 retains a separable curation concern (working-memory-limit pressure vs. dependency-check-required pressure) that may matter for future audit attribution. Form A's merge would lose that distinction.

This is a single-line corpus change, scoped narrowly. Not a broader curation project.

**KG structural validation tests** must pass post-edit (existing schema validators in the build pipeline).

### Track 3 — E6 prompt-test (gates Track 4 deployment)

After Track 1 and Track 2 ship, run **E6 — verifier prompt-test on frozen slates** before committing Path A's tier deployment.

#### Scope (committed — addresses one-fingerprint risk)

E6 runs against **two frozen slates**, not one:

- **E6.a — primary slate**: rerun4 fingerprint → 60-candidate slate from E2 (the same setup as E1). N=5 verifier reruns. This is the direct E1-comparable measurement.
- **E6.b — sensitivity slate**: rerun5 fingerprint → fresh 60-candidate slate from `recall_candidates`. N=5 verifier reruns. This guards against the failure mode "rerun4's fingerprint is uniquely friendly/hostile to the new prompt."

Total E6 cost: ~10 verifier calls. The two-slate scope is the minimum sensitivity check; if E6.a and E6.b disagree on the decision-rule outcomes below, E6 is treated as ambiguous and the prompt is iterated before Track 4 deployment.

If team capacity allows, E6.c–E6.e (rerun6–7 fingerprints + a fresh 5th rerun fingerprint per E5's k=5 protocol) are encouraged but not required for Track 4 deployment dispatch.

#### Pre-registered decision rules (per slate; both must agree)

| E6 result on a given slate | Implication for Track 4 |
|---|---|
| CD: 0/5 noisy_adjacent AND Checklists: 0/5 noisy_adjacent AND mean Jaccard ≥ 0.75 AND accept count ≥ 4 in ≥ 4/5 runs | Track 4 Tier 1 deployment is **deferred** for that anchor class (prompt + curation alone sufficient). Tier 2 considered only if other H4 partial-supported anchors are still surfacing. |
| CD: 0/5 AND Checklists: 0/5 AND mean Jaccard < 0.75 (variance not improved) | Track 4 Tier 1 **not needed for CD/Checklists**; Tier 2 narrow LLM gates apply only to anchors causing the residual Jaccard drop. |
| CD: > 0/5 OR Checklists: > 0/5 (post-fix) | Track 4 Tier 1 deterministic gates apply to whichever of {CD, Checklists} fail. Tier 1 deploys per-anchor based on E6 evidence. |
| **Friction-yield collapse** (accept count drops to ≤ 2 in any 2/5 runs OR ≥ 2 of {wysiati, time-tested-validation, optimism-bias-and-planning-fallacy} accepted in ≤ 1/5 runs) | **Track 1 prompt is over-tightened.** Roll back; reformulate to reduce negatives' aggressiveness; rerun E6 before any Track 4 deployment. **This rule fires at Phase A, not Phase B.** |
| Mean Jaccard < 0.60 (catastrophic prompt regression — worse than E1 baseline 0.800) | Roll Track 1 back; full reformulation; rerun E6. |

#### Threshold rationale

- **Mean Jaccard ≥ 0.75 (down from earlier draft 0.85)**: E1 baseline is 0.800. A tighter prompt that rejects more anchors mechanically introduces more variance possibilities at the boundary. Setting the bar above the E1 baseline (0.85) was unjustified — it implicitly assumed prompt tightening would also stabilize, but tightening typically does the opposite. 0.75 is "close to E1 baseline, not catastrophically worse" — appropriate for a tighter prompt.
- **Mean Jaccard < 0.60 catastrophic**: 25 percentage points below E1 baseline. If we drop that far, the prompt is producing different acceptance sets every run; no reasonable claim about effect can be made. Roll back.
- **Accept count ≥ 4 in ≥ 4/5 runs**: protects against the prompt over-tightening into "rejects everything." E1 baseline was exactly 5 every run; allowing 4 absorbs single-anchor rejection variance without permitting collapse.
- **Friction-yield collapse rule (new)**: the {wysiati, TTV, OB+PF} set is the verifier-stable acceptable core that the audit gold reads as legitimate friction. If those drop out, the prompt is rejecting good anchors, not just bad ones. This catches over-tightening at Phase A rather than letting it ride into Phase B.

E6 reuses E1's harness (the script in `/tmp/run_e1.py` should be promoted to `scripts/run_e6.py` or similar with a CLI flag for slate selection — this is part of the E6 implementation PR). The pre-registration prevents the "rationalize after results" failure mode the design memo warned against.

### Track 4 — Path A (anchor sufficiency, tiered) — conditional on E6

Tier scheme committed; deployment breadth is conditional on E6's residual.

| Tier | Models | Implementation form |
|---|---|---|
| **Tier 1** | `cognitive-dissonance`, `checklists` | Deterministic sufficiency check on the literal evidence quote. Per E4: CD requires two-belief / motivated-reframing markers; Checklists requires omission-in-repeated-execution markers (e.g., "every time," "always," "each X," recurrence words). Zero new LLM calls. Implemented as a post-acceptance filter in the verification pipeline. |
| **Tier 2** | `time-tested-validation`, `probabilistic-thinking`, `feedback-loops` | Deterministic rule first, narrow binary LLM gate as fallback if rule fires "unknown" on >X% of accepts in audit reruns (X to be set during Track 3 development based on actual unknown rate). The narrow gate is its own LLM call: temperature 0, rubric-in-prompt, output `pass`/`fail` only, no free-form reasoning. |
| **Tier 3** | `step-back`, `wysiati`, `representativeness-heuristic` | **Prompt-level protection only** (no gate). Per E4, these are gate-resistant — a deterministic gate would over-reject. Tier 3 protection is delivered by Track 1's prompt content #3 (Tier 3 anchor markers): Step Back requires explicit reframing language; WYSIATI requires the source surfacing what is not visible/known/measured; RH requires base-rate / category-membership confusion language. **Without Track 1 #3, Tier 3 has no protection.** This is the load-bearing cross-reference between Track 1 and Track 4. |

Tier 1 deploys **only for anchors that E6 shows still fail post-Track 1**. If E6 catches CD and Checklists via prompt alone, Tier 1 is deferred until evidence on a future case shows the gate is needed.

### Track 5 — Path D-fingerprint (contingent second track)

Path D-fingerprint is **not committed by this memo**. It is contingent on the trigger defined in §5.

If triggered, Path D-fingerprint scopes to:
- constrain `reasoning_move` output format (shorter, structured)
- canonicalize evidence-quote selection (deterministic post-processing: shortest substring that supports the move)
- move splitting/joining policy (minimum granularity rule)

These are options, not commitments. The Path D-fingerprint design memo would be a separate deliverable triggered by §5's measurement.

## §4 Phase A and Phase B acceptance criteria

### Phase A — development checkpoint (case 1 only)

**Phase A is NOT a ship gate.** It is the iteration metric used during Track 1 + Track 2 + Track 3 development. The audit's repeated lesson (synthesis §8): single-case verdicts over-read.

Phase A passes when:

- Track 1 prompt change compiles, prompt regression tests pass (existing `tests/test_lane2_contextual.py` + new tests for explicit anchor negatives)
- Track 2 KG edit applied, structural validation tests pass
- E6 (Track 3) executes per protocol; results dispatched per pre-registered decision rules in §3 Track 3 table
- On case 1 N=5 fresh reruns post-fix: CD and Checklists noisy_adjacent rate is 0/5

### Phase B — merge ship gate (corpus generalization)

Phase B passes when, on **≥3 cases** including Marcus and at least one consultant case beyond case 1:

| Metric | Target |
|---|---|
| Median whole-run noisy_adjacent rate | ≤ 10% |
| Single-case noisy_adjacent rate cap | ≤ 20% (any single case > 20% requires explicit written exception in PR description, e.g. Marcus thin-slate persistence) |
| `cognitive-dissonance` and `checklists` noisy rows | 0 across all reruns (hard bar) |
| Strict-yield regression guard | No case sees a strict-yield drop > 15 percentage points vs pre-change baseline on the same case |
| Reasoning Mode Router | RMR ≤ 1/5 reruns may surface; if it does, the evidence quote must literally contain reasoning-mode/path-selection language. RMR is 5/5 in fresh-fingerprint slates (per E3 corrected), so the verifier always has the option to accept it — the prompt restructure (Track 1 #2) is what must keep it out of the accept set |

Phase B is the merge gate for the implementation PR. Phase A is the dev-iteration metric.

### Two-layer reporting (per methodology amendment) — required tables

All Phase B testing must report both layers, with the following **specific tables attached to the implementation PR description** (not just maintained internally):

#### Required Table 1 — Repair-local trust (per case)

| Case | N reruns | CD noisy_adjacent rows | Checklists noisy_adjacent rows | RMR accepted | accept count distribution | mean Jaccard |
|---|---|---|---|---|---|---|
| user-launch-independent-fintech | 5 | x/5 | x/5 | x/5 | [c1,c2,c3,c4,c5] | x.xx |
| marcus | 5 | x/5 | x/5 | x/5 | ... | x.xx |
| consultant-case-2 | 5 | x/5 | x/5 | x/5 | ... | x.xx |

#### Required Table 2 — Whole-run trust (per rerun, all cases)

| Case | rerun | total surfaced anchors | acceptable strict | acceptable with drift | borderline | noisy_adjacent | strict yield (cluster level) |
|---|---|---|---|---|---|---|---|
| ... | r1 | x | x | x | x | x | x/N |

Per §7.2 of `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`. Classifications use the same gold-label protocol used by the audit; the gold labels for each case must be cited explicitly (linked to the case-specific gold table in the audit corpus).

#### Required Table 3 — Strict-yield regression guard

| Case | strict yield BEFORE Track 1+4 | strict yield AFTER Track 1+4 | delta (pp) | passes ≤15pp guard? |
|---|---|---|---|---|
| ... | x% | x% | ±x | yes/no |

Baselines come from PR #43 audit synthesis, with re-measurement against the same gold tables.

#### Required Table 4 — Path D-fingerprint attribution (per noisy_adjacent row)

If any noisy_adjacent rows remain after Phase B, Table 4 classifies each per §5:

| Case | rerun | model_id | classification | (if slate-rotation) was model_id in top-60 on ≥4/5 fresh fingerprints? |
|---|---|---|---|---|

This table is what feeds the Path D-fingerprint contingent trigger.

**Single-layer "this case looks good" is not sufficient evidence. All four tables must be present in the implementation PR description.** If a table cannot be filled (e.g., baseline not available for a case), explicit text in the PR description must state which table is partial and why.

## §5 Path D-fingerprint contingent trigger

Path D-fingerprint is triggered when, after Track 1 + Track 4 ship and Phase B testing completes:

> **Whole-run noisy_adjacent rate stays > 10% AND attribution analysis shows the residual noise traces to anchors that the gate would catch when present in the slate but where the gate doesn't always see them because fingerprint-induced slate rotation dropped them out of the top-60.**

### Attribution rule (operational, per sparring-partner refinement)

For each noisy_adjacent row in Phase B's whole-run reporting, classify it as:

- **Gate failure** (the bad anchor was in the slate but the gate accepted it anyway) — this is a Path A+B residual, not a Path D-fingerprint signal.
- **Slate-rotation miss** (the bad anchor was NOT in the top-60 on the run that surfaced it; it surfaced via a sibling anchor or via Step 6) — this is the Path D-fingerprint signal.
- **Step 6 enrichment** (the bad anchor came from Step 6's independent enrichment, not from Lane 2's verifier output) — this is a Step 6 issue, out of scope for Path D-fingerprint.

Concretely: per noisy row, was that `model_id` in the top-60 candidate slate on **≥4 of 5 fresh fingerprints** for that case? If yes → gate-failure or Step-6-enrichment classification. If no → slate-rotation classification, and Path D-fingerprint trigger fires once the rate of slate-rotation-classified noise crosses a threshold.

#### Threshold rationale (committed at ≥ 25%)

E3 measured per-anchor slate-rotation miss rate on case 1 at ~20% (CD missing 1/5 slates, Checklists missing 1/5, TTV missing 1/5 — different slates each time). At Phase B's median noisy_adjacent target of ≤ 10%, slate-rotation-classified rows above 25% of that residual would mean fingerprint-input variance is the dominant remaining cause of trust failure (the 80%/20% gate-reach ratio breaks down at higher rates).

- **≥ 25% of total noisy_adjacent rows are slate-rotation-classified across the Phase B cases**: Path D-fingerprint trigger fires.
- **15%–25% slate-rotation classification**: ambiguous; widen N reruns to 10 per case before deciding (per design memo §7 mixed-evidence row).
- **< 15% slate-rotation classification**: Path D-fingerprint deferred — residual noise is gate-failure or Step-6-enrichment, addressed by iterating Track 1 or by separate Step 6 work.

The 25% threshold is calibrated against E3's empirical 20% per-anchor miss rate, not picked from thin air. It is roughly "modestly above the empirical base rate" — guarding against over-firing on noise that's expected.

This trigger does **not** auto-fire on E3's pre-existing 0.615 Jaccard. It only fires when attribution shows Path A+B's gates and prompts are working but slate rotation is hiding the bad anchors from them.

## §6 Sequencing

The implementation order:

1. **Track 1 (Path B prompt) and Track 2 (KG bullet 4) drafted in parallel** on a single feature branch. Both ship together as preparation for E6.
2. **Track 3 (E6) executed** on the post-Track-1+2 system. E6 is a measurement experiment; its results dispatch Track 4 deployment per the pre-registered rules in §3.
3. **Track 4 (Path A tiers) deployed conditionally** based on E6 residual. Only the tiers/anchors E6 indicates are needed.
4. **Phase B testing** on the post-Track-1+2+4 system across ≥3 cases.
5. **Merge** if Phase B clears.
6. **Path D-fingerprint** triggered only if Phase B's residual analysis fires §5's attribution rule.

This sequencing makes each track's contribution measurable. Each step has its own pre-registered decision rule.

## §7 What this memo does NOT commit to

- **Specific implementation form for Tier 2's narrow LLM gate fallback threshold (X%).** Set during Track 3 development based on observed unknown rate.
- **Tier 3 prompt text.** Implementation detail of Track 1.
- **Cross-provider verifier-prompt validation.** Track 1 ships against the production verifier provider (OpenRouter routing). Cross-provider validation is a separate scope, but the implementation PR must record:
  - The provider name + model identifier used during E6 and Phase B (in the run JSON metadata) — so future drift can be detected by re-running the same eval against a new provider/model and comparing
  - A documented procedure for re-running E6 and Phase B if production routing changes the backing model
  - A flag in the audit-corpus diff scripts that surfaces "this run used a different backing model than the baseline" rather than silently mixing them
  This is a metadata-and-procedure commitment, not a cross-provider validation commitment. The latter remains out of scope.
- **Embeddings-on validation.** Per E2 and E3 caveats, all metrics are embeddings-off. If embeddings-on becomes production-default, rerun E2-equivalent + E3-equivalent before claiming the same stability budget. This memo's commitments scope to embeddings-off.
- **Step 6 changes.** The audit found Step 6 sometimes drops verifier-accepted anchors (e.g., Probabilistic Thinking Step-6-hidden). That is a separate concern.
- **Path D-full (Sully decomposition).** Premature. Not committed by this memo.
- **DSPy / prompt optimization.** Not committed by this memo. Could become useful once Path A+B's measurement loop is in place; not a v1 commitment.

## §8 Alternative interpretations considered

For audit completeness, alternatives that were considered and explicitly rejected:

1. **"It's a KG breadth problem, not a producer problem."** Rejected for CD (KG verified tight). Partially accepted for Checklists bullet 4 (Track 2 addresses the small breadth issue). The dominant failure class is producer-side.
2. **"Path C consensus would fix this."** Rejected by E5: k=2 worsens trust because the bad anchors are stable, not random.
3. **"Path D-full Sully decomposition is the right answer."** Rejected as premature: E1 + E3 show the variance is localizable to verifier overmatch + fingerprint text-instability, not a fundamental architecture failure. Path D-fingerprint is the targeted version, contingent.
4. **"Single-case Phase A is sufficient as a ship gate."** Rejected. Audit's repeated lesson (synthesis §8): case 1 trust does not generalize. Phase B's ≥3-case requirement is mandatory.
5. **"Ship Path B without E6."** Rejected. Without E6, Track 4's deployment breadth is undisciplined (deploy "just in case" or skip "just in case"). E6's pre-registered decision rule replaces speculation with measurement.

## §9 Status

- Memo: revised, awaiting review (this PR)
- Predecessor design memo: PR #46, merged
- Investigation experiments: E1 (PR #51, merged commit `0183659`), E2 (PR #49, merged), E3 (PR #52, merged commit `3ee4930`), E4 (PR #48, merged), E5 (PR #47, merged) — all closed and on main
- Implementation tracks: not yet started
- Code changes: none

**Pre-merge dependency note**: this memo was originally drafted before PRs #51 and #52 were merged. The branch has been rebased onto post-merge main; cited E1/E3 paths now resolve correctly. PR #52 received a pre-merge correction commit (`08aaf41`) fixing false 0/5 RMR/Optionality slate-presence claims; this memo's framing has been updated accordingly.

The next deliverables this memo expects:
1. Implementation PR for Track 1 (Path B prompt) + Track 2 (Checklists KG bullet 4 Form B)
2. E6 results memo (`research/stability-runs/lane2-stability-experiments-2026-04-27/e6-prompt-test-residual.md`) after Track 1+2 ship — must include both E6.a (rerun4 slate) and E6.b (rerun5 slate) results
3. Implementation PR for Track 4 (whichever Path A tiers E6 indicates per §3 Track 3 decision rules)
4. Phase B cross-case testing report (≥3 cases including Marcus) with all four required tables (§4)
5. Merge of the consolidated implementation PR
6. (Contingent) Path D-fingerprint design memo, triggered only if §5's attribution rule fires (≥ 25% slate-rotation-classified)

The simple bottom line:

We located the variance. It lives in two places: the verifier overmatching on broad/meta anchors with topical-only quotes (Jaccard 0.800 stable + edgy), and the fingerprint LLM rephrasing the same semantic moves enough that downstream slates rotate (Jaccard 0.615). Recall is innocent. The highest-ROI fix is tightening "mechanism, not topic" enforcement on the verifier — Path B prompt restructure, with a deterministic Tier 1 gate behind it for the failure class that survives both variance sources, and a small KG curation edit on Checklists bullet 4 in parallel. We test Path B alone (E6) before deploying gates to know what they actually need to catch. We measure across ≥3 cases including Marcus before merging. If residual noise traces to fingerprint-induced slate rotation, Path D-fingerprint kicks in as a second track.

> The measurement led. The architecture commitment follows the evidence.
