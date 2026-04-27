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
| Verifier | Stochastic with structure: stable core (mean Jaccard 0.800, accept count exactly 5), stochastic edge (RMR ↔ Optionality substitution) | E1 (PR #51) |
| Fingerprint | Semantic-stable (same 7 reasoning moves recur), text-unstable (5 distinct phrasings/quote-selections per slot), downstream slate Jaccard 0.615 | E3 (PR #52) |
| Sufficiency rubric | 5/9 anchors gate-buildable (rubric specifiable), 3/9 prompt-only, 1 control | E4 (PR #48) |
| Consensus | k=2 makes trust worse (50% noisy vs 31% at k=1); k=3 collapses friction. **Path C ruled out as first lever.** | E5 (PR #47) |

The smoke variance (14 unique anchors / 4 reruns) decomposes as compound effect of fingerprint stage (Jaccard 0.615) and verifier stage (Jaccard 0.800), with deterministic recall between them.

The most load-bearing finding: **`cognitive-dissonance` and `checklists` are accepted in 5/5 verifier runs on identical input AND appear in 4/5 fresh-fingerprint slates.** The verifier-stable failure class survives both variance sources. This is the failure class Path A+B targets.

## §2 KG vs verifier attribution (per anchor)

A verified split, from independent reading of `data/knowledge_graph.json`:

- **`cognitive-dissonance`** (`data/knowledge_graph.json:3225-3234`): all 5 `select_when` bullets are mechanism-bearing (public/ego commitment + contrary evidence, motivated reframing, post-hoc rationalization, evidence avoidance, suspiciously aligned reasoning). The KG is tight. The case-1 quote ("less than 1 in 5 conversion") is assistant pushback against optimistic assumption — not motivated reframing of a held belief by the user. **Pure verifier-side overmatch.** Path A+B is the right layer.
- **`checklists`** (`data/knowledge_graph.json:20479-20566`): bullets 1 and 2 are tight (omission risk, "every time"); `input_type` is "repeatable execution with omission risk." But **bullet 4 — "Working memory limits are turning a complex multi-step task into cognitive clutter or inconsistent execution"** — drops the recurrence requirement and reads as "any multi-step task." This invites "list of three options ⇒ Checklists." **Verifier-side error AND a small KG breadth issue.** Path A+B targets the verifier-side error; a one-line curation tightening (Track 2 below) closes bullet 4.

## §3 Architecture commitment

### Track 1 — Path B (verifier prompt restructure)

Rewrite the verifier prompt to:

1. **Mechanism, not topic.** "A literal quote must instantiate the model's local mechanism markers, not just be topically adjacent. A quote that is *about* the same domain as the model is not evidence the model is *in play*."
2. **Explicit anchor negatives** (prevents the known noisy-recurrence patterns):
   - **Reasoning Mode Router**: clarifying questions before tactics is NOT mode/path selection. RMR's mechanism (per `data/knowledge_graph.json:15010-15014`) is choosing among reasoning modes (diagnosis vs execution vs exploration); "asking before answering" does not satisfy this.
   - **Cognitive Dissonance**: the assistant pushing back on the user's optimistic assumption is NOT cognitive dissonance. CD requires a *holder* of a commitment whose reasoning is bent to protect it. Pushback on someone else's claim does not satisfy.
   - **Checklists**: a numbered list of options or one-time recommendations is NOT a checklist. Checklists require *recurring execution with omission risk*.
3. **Respect `danger_when`.** Where a model's `danger_when` markers are present in the source, that is evidence *against* selection, not for.
4. **Reject reason taxonomy.** Add `mechanism_topical_only` and `recurring_execution_required` as new rejection reasons distinct from existing ones.

This is a single-file change (`engine/system_b/companion_routing.py` — verifier prompt builder + reject-reason enum) plus prompt regression tests.

### Track 2 — Curation tightening on Checklists bullet 4 (parallel to Track 1)

Edit `data/knowledge_graph.json:20486` (Checklists `select_when` bullet 4) to require recurrence. Two acceptable forms:

- **Form A** (preferred): merge bullet 4 with bullet 2 ("must be verified every time") into a single bullet that requires repeated execution.
- **Form B**: tighten bullet 4 in place to "Working memory limits in a *recurring* multi-step process are turning execution into cognitive clutter or inconsistent execution across instances."

Form A is the preferred minimal edit. This is a single-line corpus change, scoped narrowly. Not a broader curation project.

### Track 3 — E6 prompt-test (gates Track 4 deployment)

After Track 1 and Track 2 ship, run **E6 — verifier prompt-test on frozen slate** before committing Path A's tier deployment.

**Method**: identical harness to E1. Frozen 60-candidate slate from E2 (`research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism-runs.json`). Frozen rerun4 fingerprint payload. Run the new verifier prompt N=5 times. Cost: ~5 verifier calls.

**Pre-registered decision rules**:

| E6 result | Implication for Track 4 |
|---|---|
| CD: 0/5 noisy_adjacent AND Checklists: 0/5 noisy_adjacent AND mean Jaccard ≥ 0.85 | Track 4 Tier 1 deployment is **deferred** (prompt + curation alone sufficient on the verifier-stable failure class). Tier 2 still considered if H4 partial-supported anchors persist. |
| CD: 0/5 AND Checklists: 0/5 AND mean Jaccard < 0.85 | Track 4 Tier 1 **not needed for CD/Checklists**; Tier 2 narrow LLM gates apply only to whichever anchors still cause Jaccard drop. |
| CD: > 0/5 OR Checklists: > 0/5 (post-fix) | Track 4 Tier 1 deterministic gates apply to the residual. Pre-deploy Tier 1 only for anchors that fail in E6. |
| Mean Jaccard < 0.70 (catastrophic prompt regression) | Roll Track 1 back; reformulate prompt; rerun E6. |

E6 is zero new infrastructure (reuses E1's harness in `/tmp/run_e1.py`). The pre-registration prevents the "rationalize after results" failure mode the design memo warned against.

### Track 4 — Path A (anchor sufficiency, tiered) — conditional on E6

Tier scheme committed; deployment breadth is conditional on E6's residual.

| Tier | Models | Implementation form |
|---|---|---|
| **Tier 1** | `cognitive-dissonance`, `checklists` | Deterministic sufficiency check on the literal evidence quote. Per E4: CD requires two-belief / motivated-reframing markers; Checklists requires omission-in-repeated-execution markers (e.g., "every time," "always," "each X," recurrence words). Zero new LLM calls. Implemented as a post-acceptance filter in the verification pipeline. |
| **Tier 2** | `time-tested-validation`, `probabilistic-thinking`, `feedback-loops` | Deterministic rule first, narrow binary LLM gate as fallback if rule fires "unknown" on >X% of accepts in audit reruns (X to be set during Track 3 development based on actual unknown rate). The narrow gate is its own LLM call: temperature 0, rubric-in-prompt, output `pass`/`fail` only, no free-form reasoning. |
| **Tier 3** | `step-back`, `wysiati`, `representativeness-heuristic` | Path B only (no gate). Per E4, these are gate-resistant — gate would over-reject. |

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
| Reasoning Mode Router | RMR ≤ 1/5 reruns may surface; if it does, the evidence quote must literally contain reasoning-mode/path-selection language. 0/5 on case 1 is aspirational since E3 showed RMR drops out of fresh-fingerprint slates |

Phase B is the merge gate for the implementation PR. Phase A is the dev-iteration metric.

### Two-layer reporting (per methodology amendment)

All Phase B testing must report both:
- **Repair-local**: pass/fail of the specific pre-registered metrics above
- **Whole-run**: full audit-corpus rerun trust (false positives, friction yield, surfaced anchor classification per §7.2 schema)

Single-layer "this case looks good" is not sufficient evidence. Both layers must clear.

## §5 Path D-fingerprint contingent trigger

Path D-fingerprint is triggered when, after Track 1 + Track 4 ship and Phase B testing completes:

> **Whole-run noisy_adjacent rate stays > 10% AND attribution analysis shows the residual noise traces to anchors that the gate would catch when present in the slate but where the gate doesn't always see them because fingerprint-induced slate rotation dropped them out of the top-60.**

### Attribution rule (operational, per sparring-partner refinement)

For each noisy_adjacent row in Phase B's whole-run reporting, classify it as:

- **Gate failure** (the bad anchor was in the slate but the gate accepted it anyway) — this is a Path A+B residual, not a Path D-fingerprint signal.
- **Slate-rotation miss** (the bad anchor was NOT in the top-60 on the run that surfaced it; it surfaced via a sibling anchor or via Step 6) — this is the Path D-fingerprint signal.
- **Step 6 enrichment** (the bad anchor came from Step 6's independent enrichment, not from Lane 2's verifier output) — this is a Step 6 issue, out of scope for Path D-fingerprint.

Concretely: per noisy row, was that `model_id` in the top-60 candidate slate on **≥4 of 5 fresh fingerprints** for that case? If yes → gate-failure or Step-6-enrichment classification. If no → slate-rotation classification, and Path D-fingerprint trigger fires once the rate of slate-rotation-classified noise crosses a threshold (proposed: ≥ 30% of total noisy_adjacent rows).

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
- **Cross-provider verifier-prompt validation.** Track 1 ships against the production verifier provider; cross-provider tests are a separate scope.
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

- Memo: draft, awaiting review (this PR)
- Predecessor design memo: PR #46, merged
- Investigation experiments: E1 (PR #51), E2 (PR #49), E3 (PR #52), E4 (PR #48), E5 (PR #47) all complete; PRs #51 and #52 awaiting merge
- Implementation tracks: not yet started
- Code changes: none

The next deliverables this memo expects:
1. Implementation PR for Track 1 (Path B prompt) + Track 2 (Checklists KG bullet 4)
2. E6 results memo (`research/stability-runs/lane2-stability-experiments-2026-04-27/e6-prompt-test-residual.md`) after Track 1+2 ship
3. Implementation PR for Track 4 (whichever Path A tiers E6 indicates)
4. Phase B cross-case testing report
5. Merge of the consolidated implementation PR
6. (Contingent) Path D-fingerprint design memo, triggered only if §5's attribution rule fires

The simple bottom line:

We located the variance. It lives in two places: the verifier overmatching on broad/meta anchors with topical-only quotes (Jaccard 0.800 stable + edgy), and the fingerprint LLM rephrasing the same semantic moves enough that downstream slates rotate (Jaccard 0.615). Recall is innocent. The highest-ROI fix is tightening "mechanism, not topic" enforcement on the verifier — Path B prompt restructure, with a deterministic Tier 1 gate behind it for the failure class that survives both variance sources, and a small KG curation edit on Checklists bullet 4 in parallel. We test Path B alone (E6) before deploying gates to know what they actually need to catch. We measure across ≥3 cases including Marcus before merging. If residual noise traces to fingerprint-induced slate rotation, Path D-fingerprint kicks in as a second track.

> The measurement led. The architecture commitment follows the evidence.
