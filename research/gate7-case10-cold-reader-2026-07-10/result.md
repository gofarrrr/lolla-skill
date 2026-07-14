# Gate 7 Case 10 cold-reader result

Status: **agent half complete; human feedback required**  
Date: 2026-07-10

## Simple result

We gave one fresh model a self-contained receipt and no prior session context.
It recovered most of the important story:

- the user chose 925000 dollars as a personal ceiling, not proven affordability;
- Stage A admitted three pressures and later used, used, and deferred them;
- Lolla and the strong control reached essentially the same immediate action;
- Lolla added inspectable pressure accountability but did not earn a better-answer claim;
- the first graph attribution missed indirect companion chunks, the v2 repair found
  them, and the completed case still could not identify graph contribution.

That is useful evidence that the receipt can transfer a complicated run to a
fresh agent without requiring repository archaeology.

## What did not transfer cleanly

The reader:

- missed the tomorrow-noon deadline and the exact raise-to-925000-then-walk
  sequence in its source-state summary;
- said execution completeness was “proven,” which overstates custody evidence;
- said graph chunks were not used, when the narrower supported claim is that no
  exact graph-lineage contribution was isolated;
- produced questions about the synthetic house decision rather than questions
  for human product review;
- repeated a pre-call authorization snapshot that became stale after the call.

Some of these failures were invited by the receipt itself. The frozen receipt
softened the source-end action, used broad proof language, lacked an explicit
as-of marker, and did not separate case unknowns from product-review questions.
Those errors are preserved rather than tuned away after seeing the output.

## Mechanical custody

- one reader call;
- zero retries;
- zero evaluator calls;
- 11,895 prompt tokens and 971 completion tokens;
- 12,866 tokens total;
- estimated cost `$0.02457875`;
- 10.899 seconds wall time;
- all frozen mechanical gates passed.

Verification added eight focused replay and custody tests. The non-network
repository suite passed `4011` tests with one skip. The current
`tests/test_stability_check.py` module was excluded because its unit path calls
live OpenAI embeddings; this Gate 7 goal did not authorize unbudgeted provider
calls. An earlier unrestricted attempt failed on missing local dependencies
before any such call and is not counted as a passing full suite.

## What this means

Gate 7's agent half is a **partial pass**. The receipt transfers the central
history and non-claims, but it is not yet self-evident enough to call complete.
Human readability and usefulness remain untested. Gate 8, paid graph testing,
graph promotion, and runtime integration remain blocked.

The next step is one compact human review. Any accepted changes apply
prospectively to a new receipt contract and a different case; the completed
Case 10 evidence stays frozen.
