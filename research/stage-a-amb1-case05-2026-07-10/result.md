# Ambiguous development Case 05 — Stage A result

Date: 2026-07-10  
Status: stopped at pipeline import; no rerun

## Simple result

The capture-envelope repair worked. The system verified all 14 messages, the
extraction succeeded, six reasoning passages were exact, and no quote repair was
needed. The pipeline then failed before making any of its model or embedding
calls because the orchestrator had been launched with macOS Python 3.9. The
current pipeline code requires Python 3.10 or newer.

This attempt used one extraction call, 3,182 tokens, and an estimated
$0.00143925. The pipeline ran for only 0.077 seconds, made zero OpenRouter calls,
made zero OpenAI calls, and produced no pressure artifact. There was no retry.

## What this taught us

The earlier evaluation contract froze code, prompts, data, call ceilings, and
timeouts but did not freeze the interpreter that executes them. That is part of
reproducibility. Stage A now requires a minimum and exact Python version, the
resolved executable path, and its hash. The next dry run will refuse to start
under the wrong runtime before paying for extraction.

The admitted extraction again found the broad decision and exact supporting
passages but showed the same provisional nuance problems as Case 02. It inferred
the mother's health, strengthened competing care and labor claims into contested
ownership, blurred who proposed the exact first-ten-years theme, compressed
important constraints, and overstated the status of the Mara-letter thread.
Across two designed conversations, this makes joint-process provenance and
source-strength calibration a high-priority hypothesis—not yet a frequency
claim or a reason to tune on these cases.

## Next decision

Case 05 is consumed and will not be rerun. The next bounded observation uses the
capture-ready version of `amb1-case04-research-tool-release`, the next case in
the frozen rank, and launches the orchestrator with the bundled Python 3.12
runtime. Downstream answer generation, graph ablation, and semantic tuning remain
unauthorized.
