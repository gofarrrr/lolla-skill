# Extraction call custody repair — 2026-07-10

This no-provider cycle repairs the F11 failure exposed by the frozen Case 12
smoke. It changes only deterministic custody and evaluation operability.

Implemented:

- atomic extraction call-sidecar persistence immediately after every initial
  or quote-repair provider boundary;
- unexpected boundary-exception recording before re-raise;
- explicit attempt / record / admission custody in extraction artifacts;
- unknown rather than numeric-zero usage when call evidence is absent;
- frozen provider and outer wall-clock timeouts in smoke contract v1;
- provider-free terminal-path regression coverage.

Not changed:

- extraction prompts or semantic required fields;
- exact-quote rules;
- mental-model graph, routing, selection, or Step 6;
- paired downstream experiment design;
- live runtime integration status.

No API call is authorized or made in this cycle. The failed Case 12 smoke
remains immutable. The next separate goal may freeze a new smoke on a different
non-holdout only after this cycle's full verification is complete.

Verification requires Python 3.10 or newer because the repository uses PEP 604
union syntax at runtime. On this machine the verified runtime is Python 3.12;
do not use Apple system Python 3.9 for the full suite.

Final verification:

- 96 focused custody, pipeline-compatibility, doctrine, and measurement tests
  passed;
- 3,979 non-network repository tests passed with one expected skip;
- the legacy stability-check module remained excluded because it makes
  unmocked OpenAI embedding calls;
- provider calls made by this cycle: zero.

Cycle decision: the repair goal is complete. A separate next goal may freeze a
new non-holdout smoke under contract v1. This is permission to test admission,
not permission to select or run a paired holdout.
