# Invalid preflight preserved

These artifacts are not part of the repair evaluation result.

During the first paid Case 02 preflight, all provider calls reported transport
status `ok`, but two responses omitted their required top-level JSON arrays:

- one stance response produced no `stance_events` key;
- one decision-context response produced none of its three required keys.

The boundary parser returned an empty object, and the original evaluation
harness treated it as a semantically empty but structurally valid response.
That made one repeat contain zero stance events and another contain zero
decision-context events.

This exposed a deterministic contract defect, not evidence that the source
conversation lacked those events. The harness now requires every focused
reader's declared top-level keys, preserves missing-key responses as failed
attempts, and retries the missing shadow artifact. These files are retained for
auditability and excluded from aggregation.
