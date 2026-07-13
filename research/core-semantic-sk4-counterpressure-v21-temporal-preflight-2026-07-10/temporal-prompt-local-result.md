# Counter-Pressure v2.1 Temporal Prompt — Local Result

Date: 2026-07-10  
Status: locally implemented and verified; no paid v2.1 call executed  
Decision: retain as the next bounded preflight candidate

## Change

The failed v2 prompt remains unchanged and reproducible. V2.1 is a separate
prompt contract built from the frozen v2 prompt plus one temporal addendum.

The addendum asks the LLM to:

- review counter-pressure chronologically as semantic threads;
- preserve the earliest user span where each material thread enters the
  reasoning;
- preserve a later span separately only when it materially strengthens the
  evidence, makes an ambiguity explicit, or changes the implication;
- never replace the first introduction with a later, cleaner statement;
- prioritize first introductions across distinct threads before later
  strengthenings when the cap binds.

Thread identity and strengthening remain LLM judgments. The prompt adds no
thread ID, relation field, keyword rule, or deterministic semantic inference.

## Non-changes

- one reader call;
- one `user_pressure_events` array;
- labels: `premise_correction`, `material_qualification`, and
  `reasoning_objection`;
- exact source quotes and user turns;
- eight-item cap;
- candidate ledger and duplicate custody;
- no option/evidence, question, stance, constraint, or dropped-thread rerun;
- no graph, lane, Step 6, receipt, archive, or live behavior.

The artifact schema version is distinct only to prevent accidental reuse of a
v2 artifact as a v2.1 result. The semantic event shape is unchanged.

## Local Case 08 fixture

A deterministic fixture using the real Case 08 source returned both:

- the turn-2 first introduction of the missing husband-alignment issue;
- the turn-4 later strengthening that distinguishes passive permission from
  genuine household agreement.

The local path made exactly one reader call. Both events passed the unchanged
label and exact-source validator and were preserved in source order. No
relationship or thread field was added.

This proves prompt routing, schema compatibility, and deterministic custody
only. It does not show that Gemini will follow the temporal instruction.

Verification passed 31 focused counter-pressure, temporal-scoring, runner, and
contract tests. The complete non-network repository suite passed 3,872 tests
with one existing skip and 93 subtests under Python 3.12.

## Frozen next gate

The next paid test, if separately approved, remains Case 08 with three repeats
and one successful call per repeat. It reports three measures separately:

- concept coverage for the reasoning substrate;
- first-introduction coverage for the audit trail;
- later-strengthening coverage for the audit trail.

All three must be stable across the three repeats, and all candidates must be
exact-source valid. A pass authorizes discussion of a three-case temporal
pressure-only ablation, not SK4 promotion or integration.

The machine-readable contract is `preflight-contract.json`. No paid call has
been made under its prompt hash.
