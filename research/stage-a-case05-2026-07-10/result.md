# Case 05 full Stage A result

Date: 2026-07-10  
Status: formal Stage A failure; no rerun; Gate 4 blocked

## Simple result

The machinery ran, but the contract did not pass.

The conversation was captured completely, all six selected reasoning passages
were exact quotes, the extraction call receipt was preserved, the pipeline
finished, direct OpenAI embeddings were used, and all call and cost ceilings
were respected. The run used 24 OpenRouter calls and seven direct OpenAI calls,
cost an estimated `$0.036802`, and took about 33 seconds across extraction and
pipeline execution.

The formal failure came from our evaluator: the runner called a successful
extraction exit `extractor_exit_zero`; the sealer looked for
`extraction_exit_zero`. Because the frozen contract requires every gate to
pass, that mismatch is a real failed experiment even though the subprocess
exit code was zero. Changing the label after seeing the result would make the
evaluation less trustworthy.

## What this teaches us

The new transactional extraction custody worked on a much longer conversation:

- 24/24 messages preserved;
- six of six reasoning passages verified;
- one extraction call, no quote repair, no experiment retry;
- exact requested-model custody with an attributable served version;
- complete usage and cost evidence.

The existing pipeline also stayed inside its envelope:

- 11 core-pressure calls;
- 12 Bullshit Index calls with zero evaluation failures;
- seven direct OpenAI embedding/query-expansion calls;
- private table ready with 12 source items;
- eight V60 cards and 16 consideration transactions.

But the pipeline was only `partial`. Lane 3 generated one candidate and then
dropped it, and the main delta card produced no findings. Those facts matter,
but the stop rule prevents us from now reviewing the private table and declaring
novelty. We do not yet know whether this was a healthy stand-down, false
stand-down, or a weakness in pressure discovery.

## Decision

Gate 3 is not complete and Gate 4 is not authorized. Case 05 is burned and
will not be rerun or retroactively resealed.

The next work is small and deterministic: make runner and sealer consume one
shared execution-envelope field contract, and add an integration test using
the actual runner shape. After that provider-free repair, use the next case in
the already-declared digest order rather than choosing a case for convenience.
That next candidate is Case 10. It will need the same high-stakes research-only
boundary and a separately frozen Stage B safety/fidelity contract if Stage A
ever passes.

