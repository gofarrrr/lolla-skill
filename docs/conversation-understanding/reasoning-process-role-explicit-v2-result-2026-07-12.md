# Role-explicit chronological shard result v2

Status: provider-free design passes; one-call position probe fixes relationship shape but fails source-strength gate  
Date: 2026-07-12

## Simple explanation

The previous shard design often found the right sentences but could still write
one vague interpretation that described only one side of a relationship. V2
requires the model to explain each semantic role separately:

- position: starting position, current position, qualification, and trajectory;
- uncertainty: unresolved matter, preservation/reopen condition, and their
  relationship;
- challenge: prior frame, challenge, response, revision, and their relationship;
- evidence: unchanged from the passing claim-plus-boundary reference.

Code checks only that required meanings and source roles are present together,
that aliases come from allowed regions, and that every record has terminal
custody. It does not decide whether the model assigned the semantic roles
correctly.

## Provider-free result

- 60 prompts across five reviewed conversations;
- 20/20 reviewed protected fixtures compile;
- evidence schema and prompts remain exactly unchanged;
- maximum schema size 2,145 bytes at depth 8;
- maximum user prompt 6,537 bytes;
- seven adversarial outcomes behave as designed;
- 150 reasoning-process tests passed before the probe;
- no temporal semantic gate, semantic merge, global synthesis, evaluator,
  embedding, graph, or runtime behavior was added.

Challenge inversions and conceptual uncertainty splits remain semantic review
questions. This is deliberate. A deterministic rule such as “the prior frame
must occur earlier in textual order” would reject valid reported or
retrospective challenges and drift back toward brittle conversation gating.

## One-call position probe

The frozen Case-05 endpoint probe succeeded operationally and structurally. It
produced one admitted record with separate, useful statements for all four
position roles. This fixes the original failure where current evidence was
cited but the prose described only the starting state.

Source review found one remaining error. The conversation says the user *wants*
the archive organized first. The model paraphrased this as *insisted on the
entire archive* and *total archival completion*. The trajectory, current
position, unresolved decision rule, and deadline concern are otherwise
supported.

Because source-strength inflation is a frozen failure condition, the probe does
not pass overall.

## Decision

- Role-explicit relationship representation: pass.
- Position probe semantic-strength gate: fail.
- Same-case prompt repair or retry: not authorized.
- Uncertainty, challenge, full-case, graph, and runtime calls: not authorized.

The next work should be provider-free and generic: preserve modal and commitment
strength explicitly so `want`, `consider`, `lean`, `provisionally decide`, and
`commit` cannot be casually promoted in model prose. Any later call must be
prospective on a fresh case, not a repair of this completed Case-05 output.

## Evidence

- provider-free interface:
  `research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12/`;
- cold-reader decision:
  `docs/evals/reasoning-process-chronological-shard-role-explicit-v2-cold-reader-review.json`;
- frozen probe, call, and source review:
  `research/reasoning-process-role-explicit-v2-position-probe-2026-07-12/`.
