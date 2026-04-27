# E6 — Verifier prompt-test (post Track 1+2)

Date: 2026-04-27
Branch: `data/lane2-experiment-e6-prompt-test-2026-04-27`
Implementation memo: `research/lane2-producer-implementation-2026-04-27.md` (PR #53, merged commit `9b1da1a`)
Tracks under test: Track 1 (Path B verifier prompt restructure) + Track 2 (Checklists KG bullet 4) — merged as PR #54 commit `d339efc`
Runs JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e6-prompt-test-runs.json`

## Verdict

**E6 failed catastrophically on both slates.** Two pre-registered failure rules fire simultaneously:

| Rule (memo §3 Track 3) | Threshold | E6.a | E6.b | Fires? |
|---|---|---|---|---|
| Catastrophic prompt regression | mean Jaccard < 0.60 | **0.000** | **0.000** | ✅ |
| Friction-yield collapse | accept count ≤ 2 in ≥ 2/5 runs | 4/5 runs at 0 | 4/5 runs at 0 | ✅ |

Per the pre-registered rule: **Roll Track 1 back; full reformulation; rerun E6 before any Track 4 deployment.**

**Track 4 (Path A gates) is blocked.** No further E6 reruns until Track 1 rolls back and a v2 prompt reformulation is drafted.

## Execution

- **E6.a — primary slate**: rerun4 fingerprint → 60-candidate slate (matches E2 byte-for-byte). N=5 verifier reruns with new prompt.
- **E6.b — target-present sensitivity slate**: E3 run 3 fingerprint → 60-candidate slate. All 7 target anchors present (CD pos 18, Checklists pos 56, TTV pos 43, wysiati pos 12, RMR pos 31, Optionality pos 8, OB+PF pos 51). N=5 verifier reruns with new prompt.

Total cost: 10 verifier calls.

## Per-run results

### E6.a (rerun4 slate)

| Run | Accept count | Accepted ids |
|---:|---:|---|
| 1 | 0 | — (empty/malformed verifier output) |
| 2 | 0 | — (empty/malformed) |
| 3 | 5 | commitment-bias, reasoning-mode-router, representativeness-heuristic, step-back, wysiati |
| 4 | 0 | — (empty/malformed) |
| 5 | 0 | — (empty/malformed) |

### E6.b (E3 run 3 slate)

| Run | Accept count | Accepted ids |
|---:|---:|---|
| 1 | 0 | — (empty/malformed) |
| 2 | 0 | — (empty/malformed) |
| 3 | 0 | — (empty/malformed) |
| 4 | 0 | — (empty/malformed) |
| 5 | 5 | base-rates, optionality, representativeness-heuristic, step-back, wysiati |

## Important attribution: empty/malformed verifier output, not deliberate rejection

The 8/10 "0 accept" runs are **not** clean evidence that the verifier considered all 60 candidates and rejected them. They are evidence of **verifier output-contract failure** that the harness silently normalized.

### What we observed

A diagnostic call captured the raw response from `client.run_json()` for one E6.a invocation:

```
raw response type: dict
raw response keys: []
raw response content: {}
```

The verifier returned `{}` — a valid empty JSON object that satisfies JSON mode's structural requirement but contains neither `accepted` nor `rejected` keys.

### How the harness normalized it

`engine/system_b/boundary_validation.py:82` (`require_list_of_dicts`) treats a missing field as an empty list plus a warning:

```
[companion_verification] field 'accepted': expected list[dict], got <missing> — returning []
[companion_verification] field 'rejected': expected list[dict], got <missing> — returning []
```

So `{}` → `accepted=[], rejected=[]` in the parsed result, which then renders as "0 accept, 0 reject" in the runs JSON. This is a downstream artifact of permissive parsing, not the verifier's actual judgment about the slate.

### What this means

- **Cannot claim**: "the new prompt successfully rejected CD/Checklists across runs." The 8/10 empty runs do not produce verifiable rejection rows for any anchor; the parser invented `rejected=[]` from `{}`.
- **Can claim**: "the new prompt induced the verifier to produce schema-incomplete output on 80% of calls."
- **Open question**: do `{}` responses come from (a) the model producing literal `{}` text under JSON mode, (b) the model producing some other content that gets normalized, or (c) something else? `client.run_json()` returns the parsed message content; we did not capture `finish_reason`, token counts, or the full OpenAI HTTP response in this E6 run.

### Limitation

Raw HTTP payloads are NOT preserved in `e6-prompt-test-runs.json`. The diagnostic re-run captured one `{}` response after the parsed-content step. To distinguish the three causes above, a future re-run would need to capture the full HTTP response (`finish_reason`, `usage`, the literal message content string before json.loads). This is a known limitation of the current E6 evidence.

## Cumulative prompt burden — leading hypothesis, not proven diagnosis

The new prompt added 5 blocks (A: mechanism-not-topic, B: 3 anchor negatives, C: 3 Tier 3 markers, D: danger_when respect, E: vocabulary extension) to an already-large prompt with multiple existing rule classes. The total was 8197 chars system + 34104 chars user = 42301 chars (~10.6K tokens) for a single verification call.

**Leading hypothesis**: cumulative prompt burden plus weak output-shape enforcement caused the verifier to default to schema-incomplete output as the safest action under JSON mode.

**Not proven**: the evidence does NOT isolate which block(s) caused the regression. In the 2 non-empty runs, Tier 3 anchors (Step Back, WYSIATI, RH) were accepted — so Block C did not categorically suppress them. The failure shape is "8/10 schema-incomplete," not "selective over-rejection of Tier 3."

A v2 reformulation should treat the cumulative-burden hypothesis as something to TEST via ablation, not a proven diagnosis to act on.

## Provider / model metadata

| Field | Value |
|---|---|
| Boundary client | OpenAICompatibleBoundaryClient |
| Provider | openrouter (via `load_boundary_client_from_env`) |
| Specific model | not captured in runs JSON (limitation) |
| JSON mode | enabled (`response_format: json_object`) |
| Temperature | client default |

A future v2 E6 should capture provider+model+temperature in the run JSON metadata so this evidence is reproducible across backing-model rotation. This was a memo §7 commitment that the current E6 run did not satisfy.

## What this experiment does NOT prove

- Does NOT prove the verifier "carefully rejected all 60 candidates." Empty-schema output is not the same as deliberate rejection.
- Does NOT prove "Tier 3 markers were the cause." The two non-empty runs accepted Tier 3 anchors.
- Does NOT prove the new prompt would still fail with output-contract enforcement (e.g., a stricter JSON schema, structured outputs API, or a retry-on-empty harness layer).
- Does NOT prove Track 2 (Checklists KG bullet 4) is implicated. Track 2 is a corpus edit; it affects what the verifier sees in candidate descriptions, not the prompt rules. No evidence pin Track 2 to the failure.

## Next deliverable per pre-registered rule

1. **Partial rollback PR**: revert Track 1 prompt blocks A–E from `engine/system_b/companion_routing.py`. Keep Track 2 (Checklists KG bullet 4) — it is independent and not implicated. Remove or move tests that depend on the reverted prompt blocks.
2. **No Track 4 work** until Track 1 v2 ships and a clean E6 dispatches per pre-registered decision rules.
3. **V2 reformulation**: treat output-contract handling as first-class. Options to test as ablations: smaller prompt (A + shortened B + E only); explicit "if uncertain, return `{\"accepted\": [], \"rejected\": [{\"model_id\": \"...\", \"rejection_reason\": \"uncertain\"}]}`" instruction; harness-side retry-on-empty-schema. Do not pick a fix from the §3 table without evidence.

## Status

- E6: **complete**. Both pre-registered failure rules fire.
- Track 4: **blocked**.
- Track 1: **must roll back** (partial — prompt only).
- Track 2 (Checklists KG bullet 4): **keep** — not implicated.
- Architecture: implementation memo's pre-registered failure path is now the active path. No new architectural decisions until v2 lands.

The discipline worked: the pre-registered stop sign fired and we stop. The failure is information.
