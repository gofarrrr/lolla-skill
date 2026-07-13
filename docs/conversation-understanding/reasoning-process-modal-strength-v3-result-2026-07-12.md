# Reasoning-process modal-strength v3 result

Status: provider-free structure passes; one fresh-case probe fails semantic force fidelity  
Date: 2026-07-12

## Simple result

We gave the position reader explicit categorical fields for the user's starting
stance, current stance, and remaining qualification. The categories are labels,
not scores or a commitment ladder. Deterministic code checks only shape,
allowed vocabulary, exact evidence custody, and terminal disposition; Gemini is
still responsible for interpreting meaning.

The local design passed. All 60 chronological-shard prompts built, all 20
reviewed fixtures compiled, and all non-position prompts and schemas remained
byte-identical to v2. Adversarial tests proved that malformed structure is
quarantined while an enum-valid semantic error remains admitted for source
review. The full reasoning-process suite passed 167 tests before the call.

The one prospectively frozen Case-03 call was operationally successful. Gemini
3.1 Flash Lite returned two schema-valid records through OpenRouter for an
estimated $0.00185025, with no retry, fallback, evaluator, embedding, graph, or
runtime call.

The semantic result failed. The source said, “I think the final third needs a
major re-edit.” The model labeled that as `decision`, strengthened it to a
“firm belief,” and described it as an “immediate, unilateral assessment.” A
belief or evaluative view is not a chosen course of action. The model also
omitted the protected qualification that the revised cut could resolve the edit
question while leaving the partnership question open.

## What we learned

The v3 representation is useful for diagnosis: the wrong `decision` label is
much easier to see and audit than force inflation hidden inside fluent prose.
But the representation is not yet sufficient to prevent the error.

The main design problem is now narrower. The model needs to classify the force
of a specific stance object, not the apparent confidence or intensity of the
sentence as a whole. In Case-03, it confused confidence in an assessment with a
decision. A second record exposed another ambiguity: “I will propose X, but I
am not sure I can accept X” contains a definite action and unresolved acceptance
in one sentence. One undifferentiated force label cannot cleanly describe both.

This confirms the product boundary rather than weakening it. We should not add
a deterministic keyword rule saying that “I think” means preference or that
“will” means decision. The next design must remain provider-free and clarify
the semantic contract: what proposition or action the force label applies to,
and how belief, proposal action, intended outcome, and willingness to accept
that outcome stay distinct.

## Decision and next work

Modal-strength v3 is not ready for graph, runtime, full-case, stability, or
receipt integration. Case-03 is closed: no prompt repair, retry, or same-case
tuning is authorized.

The next bounded goal is a provider-free stance-object redesign. It should:

1. define labels by the object they describe, especially separating epistemic
   belief from choice/action commitment;
2. represent mixed-force sentences without building deterministic semantic
   gates or a numeric ladder;
3. replay the reviewed corpus and adversarial failures locally;
4. preserve v3 evidence custody and the unchanged non-position interfaces;
5. authorize a different fresh case only after provider-free and cold-reader
   gates pass.

Primary evidence:

- `research/reasoning-process-modal-strength-v3-2026-07-12/report.json`;
- `research/reasoning-process-modal-strength-v3-2026-07-12/adversarial-review.json`;
- `docs/evals/reasoning-process-modal-strength-v3-cold-reader-review.json`;
- `research/reasoning-process-modal-strength-v3-probe-2026-07-12/contract.json`;
- `research/reasoning-process-modal-strength-v3-probe-2026-07-12/result.json`;
- `research/reasoning-process-modal-strength-v3-probe-2026-07-12/source-review.json`.
