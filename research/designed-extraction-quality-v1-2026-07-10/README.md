# Designed extraction quality measurement v1

This package asks a narrower question than the full Lolla evaluation: does the
probabilistic extraction preserve the decision process well enough that later
deterministic pressure is acting on the real conversation rather than on an
invented simplification?

The five conversations are development fixtures authored in the same project
session. Three existing extraction artifacts are reused. Only Cases 01 and 03
require new extraction-only calls. No pipeline, graph, revision, answer
comparison, or integration call is authorized here.

The review deliberately does not compute one quality score. Exact quotes can be
perfect while a false `never_addressed` label creates a false downstream blind
spot. Proposal provenance, source-strength calibration, constraint coverage,
thread status, topic fidelity, and quote fidelity therefore remain separate.

The pre-registered outcome is diagnostic: identify which errors are model
variance, which are prompt-contract problems, and which cannot be represented
by the current schema. It is not permission to add more prompt rules. Any repair
must first show that it reduces downstream-corrupting errors without making the
messy conversation parser brittle.
