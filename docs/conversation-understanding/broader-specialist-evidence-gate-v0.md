# Broader Specialist Evidence Gate v0

This note records a local broader specialist probe after PR29B and the
specialist runtime design gate.

The purpose was to test whether the PR29B result generalized beyond four
modern baseline archives, without changing normal `$lolla` behavior.

This was an offline evidence run. It did not change runtime behavior, prompts,
archives, `SKILL.md`, provider-boundary policy, semantic coverage archive
integration, or `conversation_understanding_ir.v0`.

## Sample Selection

The intended gate was 15-20 modern archives if available. The local archive
root had only four full-modern archives with the preferred artifact chain:

- `conversation.txt`
- `extraction.json`
- `result.json`
- `extraction_adequacy_report.json`
- `evaluation.json`
- `agent_result.json`
- `reasoning_trace.json`

To avoid pretending legacy archives were fully modern, this probe used a
broader 19-run reasoning-trace sample and labels it as mixed-custody evidence:

- 4 full-modern baseline archives;
- 15 legacy-limited modern-custody archives with `reasoning_trace.json` but
  without the complete modern adequacy/evaluation chain.

This sample is useful evidence for specialist behavior. It is not enough to
unlock runtime integration.

Artifact availability across the 19 sampled runs:

| artifact | count |
|---|---:|
| `conversation.txt` | 19 |
| `extraction.json` | 19 |
| `result.json` | 19 |
| `extraction_adequacy_report.json` | 4 |
| `evaluation.json` | 5 |
| `agent_result.json` | 7 |
| `reasoning_trace.json` | 19 |
| `revised.txt` | 19 |
| `memo.md` | 19 |

## Sampled Runs

| case | run_id | sample tier |
|---|---|---|
| `accept-founding-engineer-role` | `20260623T095719Z` | reasoning-trace custody |
| `accept-founding-engineer-role` | `20260624T094511Z_605567` | reasoning-trace custody |
| `accept-founding-engineer-role` | `20260624T125142Z_2aa96f` | reasoning-trace custody |
| `accept-founding-engineer-role` | `20260625T081013Z_9580b5` | reasoning-trace plus agent result |
| `consultant-report-senior-partner` | `20260623T112550Z` | reasoning-trace custody |
| `consultant-report-senior-partner` | `20260623T130424Z_127d92` | reasoning-trace custody |
| `consultant-report-senior-partner` | `20260624T123714Z_bb0359` | reasoning-trace custody |
| `five-person-saas-team` | `20260626T133147Z_99712f` | full modern |
| `founder-months-runway-flat` | `20260624T192039Z_c6c235` | reasoning-trace plus agent result |
| `implement-price-increase-three` | `20260626T132915Z_49172d` | full modern |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` | full modern |
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` | full modern |
| `mid-level-consultant-report-2` | `20260624T133814Z_b4a2dd` | reasoning-trace custody |
| `pivot-b2b-saas-product` | `20260623T113203Z_c4df83` | reasoning-trace custody |
| `pivot-b2b-saas-product-1` | `20260623T121306Z_fcaceb` | reasoning-trace custody |
| `prioritize-control-plane-contract` | `20260625T125625Z_aae54e` | reasoning-trace plus evaluation/agent result |
| `senior-software-engineer-accept` | `20260622T203350Z` | reasoning-trace custody |
| `senior-software-engineer-accept` | `20260623T085537Z` | reasoning-trace custody |
| `senior-software-engineer-accept-1` | `20260623T105031Z` | reasoning-trace custody |

## Aggregate Result

| metric | value |
|---|---:|
| records inspected | 19 |
| model calls | 57 |
| boundary status | `ok:57` |
| estimated cost USD | 0.076218 |
| cost estimate state | complete |
| per-run cost range USD | 0.001416-0.005452 |
| provider-boundary warnings | 57 |
| improved target elements | 56/57 |

Provider/model telemetry:

| field | value |
|---|---|
| provider | `openrouter` |
| requested model | `google/gemini-3.1-flash-lite` |
| served model | `google/gemini-3.1-flash-lite-20260507` |
| prompt tokens | 223145 |
| completion tokens | 13621 |
| total tokens | 236766 |

## Per-Specialist Validation

| specialist | attempted | raw candidates | validated | improved runs | grounding | validation failures |
|---|---:|---:|---:|---:|---|---|
| `live_constraints` | 19 | 84 | 84 | 19 | `span:78`, `derivation:6` | none |
| `stance` | 19 | 105 | 93 | 18 | `span:93` | `dropped_not_substring:10`, `dropped_invalid_turn:2` |
| `dropped_threads` | 19 | 19 | 19 | 19 | `span:19` | none |

The main validation weakness was the stance specialist. One full-modern run,
`initiate-pre-sale-coffee/20260626T131939Z_368960`, did not improve stance
coverage after validation dropped five stance candidates.

## Semantic Coverage Deltas

| semantic element | baseline | enhanced | count |
|---|---|---|---:|
| `live_constraints` | `partial / turn_ref` | `present / span` | 19 |
| `assistant_stance_or_recommendation_lineage` | `partial / artifact_present_only` | `present / span` | 18 |
| `assistant_stance_or_recommendation_lineage` | `partial / artifact_present_only` | `partial / artifact_present_only` | 1 |
| `dropped_or_under_carried_threads` | `partial / turn_ref` | `present / span` | 5 |
| `dropped_or_under_carried_threads` | `not_measured / artifact_present_only` | `present / span` | 12 |
| `dropped_or_under_carried_threads` | `partial / none` | `present / span` | 2 |

The specialists still moved the target semantic coverage surface substantially:

- live constraints became span-grounded in all 19 sampled runs;
- dropped/under-carried threads became span-grounded in all 19 sampled runs;
- stance lineage became span-grounded in 18 of 19 sampled runs.

The result is weaker than PR29B because:

- the sample is mixed-custody, not 19 full-modern archives;
- the live-constraints specialist produced six derivation-grounded events;
- the stance specialist had 12 validation drops and one non-improving run;
- every model call repeated the provider-boundary reasoning-detail warning.

## Provider Boundary

All 57 boundary calls returned provider reasoning metadata despite reasoning
being disabled.

This matches the PR29B pattern and remains separate from extractor validation
quality. It also means specialist success should not make a degraded or partial
run clean. Provider-boundary policy remains unchanged.

## Privacy And Mutation Checks

Generated outputs were written outside archive folders:

- `/tmp/lolla_broader_specialist_probe_v0.json`
- `/tmp/lolla_broader_specialist_probe_v0.md`
- `/tmp/lolla_broader_specialist_probe_v0_runs/`

The privacy scan over aggregate Markdown, aggregate JSON, and all per-run JSON
had no hits for the configured local-path, secret-marker, raw-content,
provider-reasoning, or credential patterns.

Before/after archive tree fingerprints matched for all 19 sampled archive
folders. Archive mutation count: 0.

## Decision

Decision: **B + D, with an E caution.**

**B. Existing specialists help, but should stay offline/research for now.**

Reason: the specialists improved 56 of 57 target semantic elements across the
19-run mixed-custody sample, but the improvement was not universal and the
sample was not fully modern.

**D. `user_values_or_priorities_signal` remains separate and unsolved.**

Reason: the current three specialists do not extract user values or priorities.
Do not add user-values extraction to the specialist path under another name.

**E caution. Provider-boundary and sample-custody issues still block runtime
integration.**

Reason: all 57 calls produced provider-boundary warnings, and only four sampled
runs had the full modern adequacy/evaluation artifact chain.

## Recommendation

Runtime integration remains blocked.

The next acceptable use of specialists is still offline or explicit
operator-approved deeper review. A future integration PR would need a cleaner
full-modern sample, not just this mixed-custody evidence.

This probe strengthens the case that the existing specialists are useful. It
does not approve normal `$lolla` specialist calls, archive integration,
semantic coverage archive artifacts, `evaluation.json` semantic correctness
judgment, or `agent_result.json` action approval.

## Non-Goals Held

- no `$lolla` run;
- no `SKILL.md` change;
- no runtime behavior change;
- no prompt change;
- no `archive_run.py` integration;
- no semantic coverage archive integration;
- no specialist artifacts added to archives;
- no `conversation_understanding_ir.v0`;
- no user-values extractor;
- no graph DB;
- no embeddings;
- no chunking;
- no memory layer;
- no LLM judge;
- no answer-quality scoring;
- no provider-boundary policy change;
- no automatic human-review labels.
