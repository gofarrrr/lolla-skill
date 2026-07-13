# Structured-output semantic overload: problem-class research

Status: current-practice research complete; supports provider-free decomposition experiment  
Date: 2026-07-12

## Exact local signature researched

The search was not “how to make JSON work.” It targeted this observed pattern:

1. a valid structured-output schema is rejected by one provider but accepted
   by others;
2. accepted responses are syntactically valid yet semantically empty,
   internally inconsistent, or wrong;
3. stronger and more expensive models do not reliably repair the defect;
4. the call asks one model to identify temporal roles, preserve exact evidence,
   interpret trajectory, decompose stance objects, align five output columns,
   classify expressions, and explain fidelity at once;
5. deterministic validation catches some contradictions but cannot decide
   messy semantic correctness without violating Lolla's boundary.

Search questions included:

- Do structured-output constraints reduce semantic or reasoning quality even
  when JSON validity is perfect?
- Does schema breadth or complexity reduce extraction reliability?
- Are schema support and semantic correctness separate provider/model gates?
- Is “reason first, format later” or task/schema decomposition an established
  mitigation?
- What must still be evaluated locally before adopting those patterns?

## What current evidence says

### 1. Provider-valid JSON Schema is not portable JSON Schema

Google documents only a subset of JSON Schema, tells applications to validate
values despite syntactically correct JSON, explicitly warns about
schema-compliant but semantically incorrect outputs, and says very large or
deep schemas may be rejected. The documentation does not publish the exact
complexity boundary. This matches our opaque Google rejection and the success
of the same schema through other operators, without proving the exact rejected
feature. See [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output).

JSONSchemaBench evaluates 10,000 real-world schemas across several constrained
decoders, including Gemini and OpenAI, because syntax coverage, efficiency, and
generated quality are different dimensions. Its maintained reference
implementation and the `llguidance` project both describe support as a large
subset of JSON Schema rather than universal portability. See
[JSONSchemaBench](https://arxiv.org/abs/2501.10868),
[benchmark repository](https://github.com/guidance-ai/jsonschemabench), and
[`llguidance`](https://github.com/guidance-ai/llguidance).

### 2. Valid structure can hide worse semantics

The 2026 Constraint Tax study separates schema validity, answer accuracy,
executable accuracy, and wrong-valid-schema rate. In its small-model setting,
hard constraints raised validity to 100% while increasing wrong-but-valid
outputs. Its scale is not directly comparable to our large hosted models, but
the metric separation maps exactly to Lolla's wire/admission/source-review
gates. See [The Constraint Tax](https://arxiv.org/abs/2605.26128).

This validates our refusal to treat HTTP success, JSON validity, or
deterministic admission as semantic quality.

### 3. Structure competes with reasoning when the task is near model capacity

The April 2026 Format Tax study finds that format instructions can reduce
reasoning and writing quality, with much of the cost entering through the
prompt rather than decoder token masking. Free-form reasoning followed by a
separate formatting pass recovers much of the loss in the studied settings.
See [The Format Tax](https://arxiv.org/abs/2604.03616).

The June 2026 Capacity, Not Format study refines this: structured output is not
uniformly harmful, but the penalty grows with schema complexity when a task is
near a model's capacity. Delayed structure recovers much of the observed loss.
See [Capacity, Not Format](https://arxiv.org/abs/2606.09410).

This is consistent with our result that stronger models and stricter validity
did not reliably preserve the source roles. It does not prove that format tax
is the only cause; ontology ambiguity and source salience remain plausible.

### 4. Extraction reliability falls with schema breadth

ExtractBench evaluates 12,867 human-annotated fields across schemas ranging
from tens to hundreds of fields. It reports sharp degradation as schema breadth
increases and 0% valid output on its 369-field financial schema across all
tested frontier models. Its maintained repository scores individual fields,
arrays, missing values, and spurious values separately. See
[ExtractBench](https://arxiv.org/abs/2602.12247) and its
[reference repository](https://github.com/ContextualAI/extract-bench).

Lolla's nineteen-property record is far smaller than a 369-field filing, so we
must not transfer the magnitude of that result. The analogous lesson is that
one-call extraction breadth is an empirical variable and missingness must not
be hidden by aggregate validity.

## Practices adopted

- Keep wire compatibility, deterministic admission, and source fidelity as
  separate gates.
- Stop searching for a “smarter model” on the unchanged combined contract.
- Decompose the semantic work provider-free before another call.
- Make each LLM job answer one visible semantic question with the smallest
  useful schema.
- Preserve ordinary JSON validation and exact evidence custody after every
  microtask.
- Measure maximum calls, candidate counts, token/schema size, and fan-in before
  claiming decomposition is simpler.
- Preserve valid empty, disagreement, and partial-role outcomes rather than
  forcing completion.
- Keep a future delayed-format/free-form-first ablation as an explicit option,
  not a default architectural layer.

## Practices rejected for now

- No deterministic keyword or state-machine repair of missing semantic roles.
- No response-healing loop or semantic retry policy.
- No assumption that DeepSeek V4 Flash is a winner because it came closest.
- No immediate free-form reasoning plus second formatter call; it doubles
  calls and creates a new transfer boundary before smaller schemas are tested.
- No schema-splitting victory claim without measuring fan-in.
- No self-hosted constrained-decoding framework; our current failure is
  semantic as well as provider-specific, and self-hosting would expand the
  architecture without evidence of product value.

## Remaining unknowns

1. Is the main local defect simultaneous task load, ambiguous ontology, source
   salience, or an interaction among them?
2. Will a small role-trajectory reader preserve an undecided preference as a
   genuine starting position?
3. Will per-role stance readers preserve belief/action/outcome/acceptance
   distinctions without seeing the entire combined schema?
4. Can exact deterministic joins preserve disagreement without manufacturing a
   coherent story the models did not produce?
5. Does the maximum fan-out and fan-in remain worth the expected semantic gain?
6. Would delayed free-form interpretation followed by structured packaging
   outperform small direct schemas if decomposition still fails?

These unknowns do not block provider-free design. They define its gates. They
do block further paid model comparisons and the reserved agency case.
