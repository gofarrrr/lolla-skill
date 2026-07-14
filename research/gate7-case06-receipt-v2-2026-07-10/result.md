# Gate 7 Case 06 receipt v2 result

Status: **agent reconstruction partial pass; human usefulness pending**  
Date: 2026-07-10

## Simple result

We applied the repaired receipt contract to an already-closed Case 06 run. No
pipeline stage was rerun. The receipt was assembled from frozen evidence and
then given to one fresh model with no prior session context.

The reader recovered the product's central distinction: the public answer can
stand down correctly while exact pressure identity and effect accounting still
fail. It also kept custody separate from quality, did not claim answer
improvement, and did not infer graph value.

This is a stronger transfer than Case 10, especially around exact pressure
identity, private-versus-visible effects, as-of authorization, and the split
between case unknowns and human product questions.

## Remaining transfer failures

The reader:

- recovered the stated plan but omitted that no deadline was stated;
- did not surface the user's final conditional judgment about what rejection
  would mean about the friend;
- said no exact lineage was preserved, instead of distinguishing preserved V60
  lineage from absent exact relationship-graph lineage;
- preserved partial-token and cost scope but omitted the exact operating
  numbers;
- described the missing pre-key seal as a route to “full certainty,” when such
  a seal would improve order custody only.

These failures are preserved. The completed receipt, prompt, and response were
not tuned after the call.

## Mechanical custody

- one reader call;
- zero retries;
- zero evaluator calls;
- 9,534 prompt tokens and 694 completion tokens;
- 10,228 tokens total;
- estimated cost `$0.0188575`;
- 8.416 seconds wall time;
- all frozen mechanical gates passed.

Provider-free verification passed 36 focused Gate 7 tests. The broader
non-network repository suite passed 4,039 tests with one skip and 93 subtests
under the workspace Python 3.12 runtime. `tests/test_stability_check.py` was
excluded because its current test path invokes live OpenAI embeddings; no
additional provider calls were authorized.

## What this means

The Case 06 agent transfer is a **partial pass, stronger than Case 10**. Receipt
v2 fixed several concrete defects, but typed output and mechanical validity do
not guarantee complete reconstruction. The next receipt version should consider
a bounded place for material user beliefs or conditional inferences and should
make graph-lineage subtypes explicit. Those are prospective changes, not
permission to retune this case.

Human readability and usefulness remain untested. The pipeline rerun, graph
ablation, graph promotion, and runtime integration remain blocked.
