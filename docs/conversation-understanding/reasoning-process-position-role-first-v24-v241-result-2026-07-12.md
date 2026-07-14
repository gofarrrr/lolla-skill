# Paired role-first v2.4 and v2.4.1 result — 2026-07-12

## Decision

Retain paired current-plus-qualification allocation as the leading development architecture. Retain the v2.4.1 status-free wire. Close v2.4's redundant envelope-status wire. Do not integrate into graph or runtime yet: the central allocation problem improved, but complete expression, category, and evidence precision is not proven.

## Architecture

The system now uses at most three semantic calls:

1. independent starting-position interpretation;
2. paired current-plus-qualification allocation from the same source packet;
3. exact-ID relationship interpretation.

The paired call returns one role-labeled record list. Deterministic code splits the explicit labels, validates nested component structure and exact evidence custody, and joins exact IDs. It does not decide semantic correctness, subtract shared aliases, apply keyword or chronology gates, or compute quality scores.

## Provider-free result

V2.4 represented 12 reviewed cases, 36 role records, 12 relationships, and 12 complete joins with zero quarantine and no provider calls. The largest prompt was 7,378 bytes and the paired schema was 2,073 bytes at depth 11. Nine focused/adversarial tests passed, including legitimate shared-alias custody and deliberate admission of a semantically duplicated unresolved meaning for source review.

## V2.4 registry probe

The frozen rare-disease registry case used a shared e036 sentence containing both conditional approval and unresolved meaningful-withdrawal doubt. The paired model output allocated those meanings correctly and preserved protected path dependence. It failed structural admission only because it also set both redundant envelope statuses to `not_found` while returning populated supported records. The relation call was correctly blocked. Two calls cost $0.000736196.

The exact candidate is preserved. Removing its two status fields and replaying it through v2.4.1 admits the unchanged semantic records. This demonstrates structural simplification, not semantic repair.

## V2.4.1 change

V2.4.1 removes only `current_status` and `qualification_status` from the provider wire. Per-record semantic status remains model-authored. Code derives envelope bookkeeping mechanically: no role records means `not_found`; uniform record status passes through; mixed record statuses produce `mixed`. No prose or role meaning is repaired.

Provider-free v2.4.1 replay again passed 12 cases and all exact joins. The paired schema shrank to 1,855 bytes. Six focused tests passed before the new transfer case.

## V2.4.1 housing probe

The new housing-retrofit case contained shared e034: conditional approval of equipment ownership and exit, plus unresolved doubt about meaningful sensor opt-out under collective optimization.

All three calls passed for $0.000959574. The paired output correctly used e034 in both roles with distinct meanings. It retained the bounded pilot, contractual safeguards, thresholds, unresolved collective choice, and protected path dependence. The exact-ID relationship was source-faithful. This is the first fully operational development pass for the paired architecture.

Residual defects remain:

- e031 `leaning` was mislabeled as `conditional_willingness`;
- current evidence included two unnecessary assistant summary aliases;
- some object/expression categories were coarse;
- the allocation note falsely claimed e031 also contained unresolved opt-out meaning;
- current role prose reached its length bound and truncated, although components preserved the material meaning.

## Meaning for the roadmap

The important advance is not “better JSON.” Current and qualification were compared in one probabilistic task, a legitimately shared alias was separated by meaning without hard exclusivity, and the maximum call count fell from four to three.

This is enough to retain the architecture but not enough for graph integration. Next work is provider-free corpus-level evaluation that keeps separate judgments for:

- central role allocation;
- protected qualification survival;
- speaker ownership;
- evidence precision;
- expression force;
- object/category precision;
- relationship preservation.

Do not collapse these into one score. That evaluation should determine whether the residual defects matter to later mental-model selection and whether another transfer case or a read-only shadow integration is the next justified experiment.

## Evidence

- Provider-free v2.4.1: `research/reasoning-process-position-role-first-v241-2026-07-12/report.json`
- V2.4 preserved candidate: `research/reasoning-process-position-role-first-v24-probe-2026-07-12/call-02-result.json`
- V2.4.1 source review: `research/reasoning-process-position-role-first-v241-probe-2026-07-12/source-review.json`
