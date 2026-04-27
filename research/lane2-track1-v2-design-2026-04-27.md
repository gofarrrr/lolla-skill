# Lane 2 Track 1 v2 — design note

Date: 2026-04-27
Branch: `docs/lane2-track1-v2-design-2026-04-27`
Status: design note — scopes the next implementation slice; no code changes
Predecessor: `research/lane2-producer-implementation-2026-04-27.md` (PR #53, merged)
Triggering evidence: `research/stability-runs/lane2-stability-experiments-2026-04-27/e6-prompt-test-residual.md` (PR #55, merged)
Rollback: PR #56 (commit `a9c1044`) — reverted Track 1 prompt blocks A–E; kept Track 2 KG bullet 4 edit on main

## Opening — what this memo commits to (and does NOT)

The pre-registered §3 Track 3 catastrophic regression rule fired on E6. The pre-registered action was "roll Track 1 back; full reformulation; rerun E6." The rollback is done (PR #56). This memo scopes the **reformulation** before any new prompt code is written.

This memo commits to:

- A **harness output-contract change shipped before any v2 prompt work** so `{}` from the verifier is classified malformed instead of silently normalized into empty accept/reject lists
- An **ablation order** for v2 prompt blocks — one small change at a time, starting with the most general rule and only expanding if each step clears E6
- **E6 retest discipline** — every ablation step retests against the same two frozen slates (E6.a rerun4, E6.b E3 run 3) under the new harness contract, with pre-registered pass/fail rules
- **Capture of provider/model metadata + raw HTTP response shape** in every E6 retest, so future evidence is reproducible

This memo does NOT commit to:

- Specific v2 prompt content beyond an ablation start point. The four blocks (A: mechanism-not-topic, B: Tier 1 negatives, C: Tier 3 markers, D: danger_when respect) get tested individually before any are combined, and the order itself is hypothesis, not commitment beyond v2.1.
- A timeline. Each ablation step has its own decision point.
- Track 4 work. Path A gates remain blocked until a v2 prompt clears E6.
- Memo §3 Track 3's existing thresholds being correct as-is. The ablation reveal may change what "clean" means.

## §1 What exactly failed in E6 — separating two failure modes

E6 produced a 0-accept result on 8 of 10 verifier runs across two slates. Both pre-registered failure rules fired (catastrophic Jaccard mean 0.000, friction-yield collapse 4/5 runs at 0 accepts on each slate). But the *attribution* of those zeros is the load-bearing question.

### Two distinct failure modes are mixed in the runs JSON

1. **Verifier output-contract failure** (the one we observed): the LLM returned `{}` — a valid empty JSON object that satisfies JSON mode without committing to either an `accepted` or `rejected` field. The harness's `require_list_of_dicts` (`engine/system_b/boundary_validation.py:82`) silently normalized missing fields to `[]` with a warning, producing what looks like "0 accepts, 0 rejects" in the runs JSON.

2. **True reject-all** (would look identical in current logs): the LLM evaluates all 60 candidates and decides none of them apply, returning `{"accepted": [], "rejected": [<60 entries with reasons>]}`. The runs JSON would show 0 accepts but ~60 explicit rejects with reasons.

The current runs JSON cannot distinguish (1) from (2) without raw HTTP payload inspection. We confirmed (1) via a one-off diagnostic call that captured `client.run_json()` returning `{}`. We did NOT capture the full HTTP envelope, `finish_reason`, token counts, or message content string for the production E6 calls.

### Why this matters for v2 design

If the dominant failure mode is (1), the diagnosis is "the prompt induced schema-incomplete output." The fix space is prompt-side (smaller, less restrictive content) AND harness-side (don't normalize malformed output silently).

If the dominant failure mode is (2), the diagnosis is "the prompt taught the verifier to reject everything." The fix space is prompt-side only (less aggressive negatives).

The two diagnoses point to different v2 strategies. Without the distinction, any v2 prompt design is a guess.

### What we can already say from the 2 successful E6 runs

In the 2 of 10 runs that did produce structured JSON:
- **E6.a run 3**: accepted 5 anchors (commitment-bias, reasoning-mode-router, representativeness-heuristic, step-back, wysiati). RMR was accepted despite Block B's RMR negative.
- **E6.b run 5**: accepted 5 anchors (base-rates, optionality, representativeness-heuristic, step-back, wysiati).

Tier 3 anchors (Step Back, WYSIATI, Representativeness Heuristic) were accepted in both successful runs. **Block C did not categorically suppress them.** This rules out "Block C alone caused the catastrophic regression."

The successful runs also accepted 5 anchors each (matching E1's accept-count discipline). This rules out "the prompt teaches the verifier to reject everything." When the verifier produces structured output, the count behavior is preserved.

The remaining question — attributable to (1) or (2) — is whether the *cause* of the 8/10 `{}` runs is the prompt's combined restrictiveness or a deeper output-contract fragility under JSON mode. The harness fix in §4 is what makes that question answerable.

## §2 What v2 must protect

These are the success criteria v2 must clear, beyond the §3 Track 3 thresholds the implementation memo already pre-registered.

### 2.1 Accept-count stability

E1 baseline: every run produced exactly 5 accepts. The 5-per-run discipline is a real signal that the prompt is working as a discriminator. **A v2 ablation step is invalid if it produces 0 accepts on > 1 of N=5 runs**, regardless of which anchors were rejected. This must apply to a per-step E6 retest, not just the cumulative final E6.

### 2.2 Output-contract integrity

`{}` must not silently become `accepted=[], rejected=[]`. After §4's harness change, a malformed verifier output is recorded as `malformed_verifier_output`, not as a zero-anchor result. **A v2 ablation step is invalid if any of its N=5 runs produces malformed output** — that signals the prompt is destabilizing the output contract regardless of accept/reject content.

### 2.3 Friction-yield protection set must survive

WYSIATI and Time-Tested-Validation were E1 5/5 stable accepts on case 1. Optimism-Bias-and-Planning-Fallacy was E5's case-1 acceptable secondary and E4's clean positive control. **A v2 ablation step is invalid if WYSIATI, TTV, or OB+PF drops to < 3/5 acceptance** on either E6 slate. This is the friction-yield collapse rule from §3 Track 3, restated as a per-step gate.

### 2.4 Noise-reduction signal (the actual goal)

Cognitive Dissonance and Checklists were E1 5/5 stable accepts AND the load-bearing failure class. **A v2 ablation step is "encouraging" if CD or Checklists drop to ≤ 1/5 acceptance** on either E6 slate (the prompt is having the intended effect on the failure class without wholesale collapse). It is "neutral" if they remain at the E1 baseline (5/5) — that step is not yet doing useful work but is at least not breaking the system.

### 2.5 Reasoning-Mode-Router target (the live wound)

RMR was E1's stochastic edge (3/5 accepted) and the trust-breach anchor from PR #44. A v2 ablation step is "encouraging" if RMR drops to ≤ 1/5 acceptance. It is acceptable if RMR remains 3/5. It is **invalid** if RMR rises (e.g., to 4–5/5).

### 2.6 What is NOT a v2 success criterion

- Phase B numbers (cross-case noisy_adjacent ≤ 10%, etc.) are NOT yet in scope. Phase B applies only after a v2 ablation chain completes E6 cleanly. We do not chase Phase B numbers during v2 development.
- Single-run "this case looks good" is NOT sufficient evidence. Both E6.a AND E6.b must clear each gate per the §3 Track 3 two-slate rule.

## §3 Ablation order

The four prompt blocks from PR #54 are tested individually, smallest-and-most-general first. Block E (rejection_reason vocabulary extension) is a tiny JSON schema-example tweak with no behavioral content; it ships with whichever block introduces a new reason string.

| Step | Content tested | Rationale |
|---|---|---|
| **v2.1** | Block A only — MECHANISM-NOT-TOPIC RULE (general principle, ~1 line) | Smallest possible change. Tests whether the general "mechanism, not topic" framing alone stabilizes under E6 without any anchor-specific negatives. If v2.1 fails E6, the issue is general prompt sensitivity, not specific blocks. |
| **v2.2** | A + B (Tier 1 anchor negatives for RMR, CD, Checklists) — adds ~3 lines targeting the verified failure class | Tests whether the Tier 1 negatives, with no Tier 3 or danger_when, deliver noise reduction without collapse. Block E (`mechanism_topical_only`, `recurring_execution_required` reason strings) ships with this step since Block B uses them. |
| **v2.3** | A + B + D (DANGER_WHEN RESPECT) | Adds the danger_when rule (1 short paragraph). Smaller than Tier 3 markers; reuses existing `watches_for:` infrastructure (per the user-prompt formatter that already emits the clause when candidates have `danger_when`). |
| **v2.4** | A + B + D + C (Tier 3 anchor markers) | Adds the most expansive block — three anchors with explicit marker patterns. Tested last because it has the largest surface area for cumulative-burden problems. |

Each step retests against E6 (both slates, N=5 each, same harness with §4 fix in place) before moving to the next step.

If v2.1 fails E6 with §4's harness fix in place: the v1 catastrophic regression was NOT cumulative-burden alone. There is something fragile about ANY prompt addition in the current verifier setup. Stop the ablation chain and investigate at the harness/model layer (e.g., raw HTTP capture, finish_reason analysis, JSON-mode behavior with smaller prompts).

If a step succeeds: it becomes the new baseline; the next step adds on top.

If a step fails: the ablation chain stops at the previous successful step. That step's prompt becomes the v2 final, with the failed block deferred to a future re-attempt with different shape (e.g., shorter wording, fewer anchors per block).

This is hypothesis-driven: the implicit hypothesis is "smaller prompt changes are safer than larger ones." The chain tests that hypothesis incrementally. It does not assume which block specifically caused v1's failure.

## §4 Harness output-contract change (ships before v2.1)

Before any v2 prompt work, ship a harness change that classifies `{}` and other schema-incomplete verifier outputs explicitly.

### Change to `parse_verification_response` and/or `require_list_of_dicts`

Two options. The implementation PR for this section will pick one based on least-invasive scope:

**Option A — explicit malformed marker**: when the verifier returns a dict missing both `accepted` and `rejected` (or with non-list values), `parse_verification_response` records a `malformed_verifier_output` marker in the run metadata. Downstream consumers (audit logs, runs JSON) see this distinction explicitly. The runs JSON gains a `malformed_runs_count` field at the analysis level.

**Option B — retry-on-malformed**: when the verifier returns malformed output, the harness retries once with the same prompt. If the retry also returns malformed output, the call is recorded as `malformed_verifier_output_after_retry`. This biases the system toward producing useful evidence at the cost of one extra LLM call per malformed result.

Recommendation: **Option A first** (record the distinction without changing behavior), then evaluate whether retry adds value after one v2 ablation step has produced clean evidence.

### Run JSON metadata additions

E6 (and any future verifier-LLM experiment) must record per-run:
- `provider_name`
- `model` (specific model identifier, not just provider)
- `temperature`
- `finish_reason` (from the underlying HTTP response)
- `usage` (token counts, if returned)
- `raw_message_content` (the model's literal output before json.loads, if non-empty)
- `malformed` (boolean, set when the harness's malformed marker fires)

These satisfy the memo §7 cross-provider metadata commitment and resolve the §1 "raw payloads not preserved" limitation from the E6 evidence.

### What this change does NOT do

- Does NOT change `parse_verification_response`'s downstream contract for non-malformed runs. Existing tests pass unchanged.
- Does NOT add a Track 1 prompt change. Harness fix ships independently of any v2 prompt content.
- Does NOT decide whether malformed runs count toward decision rules — that's pre-registered as part of v2.1's E6 protocol (see §5 below).

## §5 Sequencing

The implementation order, with each step pre-registered for outcome dispatch:

1. **Harness PR (output-contract fix per §4)**. Single PR. Adds malformed marker, run-level metadata capture, and a small unit test asserting `{}` produces a malformed marker rather than silent empty lists. Ships before any v2 prompt work.
2. **v2.1 PR — Block A only**. Implementation PR with one prompt-content edit (insert MECHANISM-NOT-TOPIC RULE) plus the prompt-content presence test for that block.
3. **E6 retest after v2.1**. Two slates × N=5 each = 10 verifier calls. New harness records malformed counts and full metadata. Apply pre-registered v2.1 decision rule:
   - **Pass**: 0 malformed runs across both slates AND accept count = 5 in ≥4/5 runs each AND all of WYSIATI+TTV+OB+PF accepted in ≥3/5 runs on at least one slate AND CD/Checklists drop or hold steady → v2.1 becomes new baseline; proceed to v2.2.
   - **Fail (output-contract)**: ≥1 malformed run on either slate → v2.1 itself is too much for the output contract; STOP the ablation chain. Investigate at the harness/model layer, not the prompt.
   - **Fail (friction-yield)**: WYSIATI or TTV or OB+PF drops below 3/5 on either slate → roll v2.1 back; try a smaller Block A wording (one sentence instead of multi-clause).
   - **Fail (acceptable but no signal)**: CD and Checklists remain at 5/5 → v2.1 is safe but not useful; proceed to v2.2 since A alone was never expected to catch the failure class.
4. **v2.2 PR — A + B**. Same protocol as v2.1.
5. **E6 retest after v2.2**. Same pre-registered structure with the additional gate that CD or Checklists should drop to ≤ 1/5 on at least one slate (this is where Block B is supposed to do real work).
6. **v2.3 PR — A + B + D**. If v2.2 passes.
7. **E6 retest after v2.3**.
8. **v2.4 PR — A + B + C + D**. If v2.3 passes.
9. **E6 retest after v2.4**.
10. **Phase B testing** on the surviving v2 prompt across ≥3 cases. Per memo §4 acceptance criteria.

Each E6 retest produces its own short artifact (`e6-prompt-test-v2-N.md`) recording the per-run decision rule outcome. The chain is auditable.

## §6 What this memo does NOT do

- Does NOT pre-write the v2.1 prompt content. The MECHANISM-NOT-TOPIC sentence in v2.1 should be a SHORTER version of v1's Block A (probably ~1 sentence, not the full paragraph). The exact wording is part of the v2.1 implementation PR review, not this memo.
- Does NOT predict the ablation chain will reach v2.4. The chain stops at the first failure; that's the point of pre-registered ablation.
- Does NOT change Phase B acceptance criteria from the implementation memo §4. Phase B is unchanged for whichever v2 prompt clears E6.
- Does NOT commit to specific harness implementation (Option A vs B). The harness PR makes that call.
- Does NOT address embeddings-on (the memo §7 caveat still holds).
- Does NOT address Step 6 enrichment.

## §7 Status

- Memo: draft, awaiting review (this PR)
- Track 2 KG bullet 4 edit: on main, retained
- Track 1 v1 prompt: rolled back on main (PR #56)
- E6 v1 evidence: on main (PR #55)
- Track 4 (Path A gates): blocked until a v2 prompt clears E6
- Harness output-contract fix: not yet implemented
- v2 prompt: not yet implemented

The simple bottom line:

> The E6 v1 failure said "large prompt + permissive empty-output parsing is unsafe." It did NOT say which prompt block was bad. V2 design treats both halves as first-class: harness fix to make malformed output visible, ablation chain to attribute prompt-block contribution one step at a time. No more guessing.

> The system learned exactly the thing we needed before we spent Phase B money.
