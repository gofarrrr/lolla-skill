# Pre-Step-6 PhD Producer/Compressor Test Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-compact-json-replay-readout-2026-05-16.md
research/pre-step6-strict-json-subagent-replay-readout-2026-05-16.md
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Can a separate native compressor take a useful rich PhD worker artifact and
produce a Step-6 card that:

```text
preserves fallback executability
preserves Silva/data access
preserves relaxation and discard conditions
validates as reasoning_artifact.v1
stays under the 1,500-character cap
```

## Setup

Input was the compact PhD worker artifact from the previous replay. It already
preserved both gates but failed the cap:

```text
compact worker artifact: 1,769 validator chars
```

The compressor saw only that artifact and was told:

```text
compress into one JSON reasoning_artifact.v1 object
preserve fallback and Silva/data gates
do not introduce new facts
do not write final-answer prose
target <= 1,200-1,500 chars
```

The compressor was then retried with progressively stricter size instructions
because each output remained close but over cap.

## Results

| Attempt | Validator Size | Valid JSON | Gates Preserved | Cap |
| --- | ---: | --- | --- | --- |
| Direct compact worker output | 1,769 | Yes | Yes | Fail |
| Compressor pass 1 | 1,677 | Yes | Yes | Fail |
| Compressor pass 2 | 1,617 | Yes | Yes | Fail |
| Compressor pass 3 | 1,569 | Yes | Yes | Fail |
| Compressor pass 4 | 1,540 | Yes | Yes | Fail |

All attempts preserved:

```text
fallback executability
Silva/data access
relaxation condition
discard condition
risk if ignored
```

No attempt passed the 1,500-character validator cap.

## Interpretation

This is a useful negative result.

The compressor did not destroy reasoning. It consistently preserved the two
controlling gates. The problem is not that the model cannot identify what
matters.

The problem is that native LLM self-compression is not reliable enough at this
threshold:

```text
it keeps landing just above the cap
it needs validation feedback
it may require multiple retries
even multiple retries did not pass in this one-case test
```

So the bottleneck is now narrower:

```text
not cognition
not admission
not JSON syntax
not gate preservation
but cap-obedient compression
```

## Decision

```text
producer_compressor_preserves_meaning
producer_compressor_does_not_reliably_hit_1500_cap
do_not_add_compressor_stage_yet
do_not_relax_cap_yet
do_not_build_runtime_worker_ingestion
do_not_build_reasoning_bundle
```

## What This Means

The worker path is still promising for producing better reasoning pressure, but
it has not earned automation. The current safe position is:

```text
raw reasoning_artifact.v1 remains the baseline
admission-first native workers remain research-only
strict JSON is viable
compression under 1,500 chars remains unsolved
```

If this path continues, the next experiment should not be another unconstrained
native compressor. It should test one of two tighter choices:

```text
deterministic field-budget trimming
or a smaller Step-6 card schema with fewer fields
```

## Next Options

Option A: deterministic field-budget trimming.

```text
Keep the full worker artifact for audit.
Use deterministic truncation/summarization rules per field.
Validate that fallback and Silva/data keywords survive.
Risk: crude truncation can preserve keywords while damaging reasoning.
```

Option B: smaller Step-6 card schema.

```text
Instead of full reasoning_artifact.v1, render a smaller card:
pressure
boundary
relax_if
discard_if
risk_if_ignored
This may be the better actual Step-6 handoff surface.
```

Option C: raise the cap.

```text
Set cap around 1,800-2,200 chars.
This would pass the PhD compact output and likely many worker artifacts.
But it risks making Step 6 consume too much private worker text.
```

Recommendation:

```text
test smaller Step-6 card schema before relaxing the cap
```

Reason:

```text
Step 6 probably does not need every reasoning_artifact.v1 field from workers.
It needs the pressure, boundary, relaxation, discard, and risk. The full
artifact shape may be right for audit but too bulky for consumption.
```
