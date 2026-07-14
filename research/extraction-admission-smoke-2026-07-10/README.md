# Extraction admission smoke — 2026-07-10

This is a deliberately narrow, one-attempt experiment. It exists because two
paired holdout attempts failed before graph value could be evaluated: one lost
the extraction artifact to an unprepared output path, and one retained invalid
quote delimiters after the allowed repair. Spending another holdout before
proving those boundaries would confound provider/runtime custody with the
reasoning experiment.

The smoke uses semantic-corpus Case 12 and permanently retires that fixture from
future downstream holdout claims. It runs extraction only. A pass means the
system can persist a complete, quote-valid extraction together with exact
OpenRouter call, model, token, and cost evidence under the frozen code and
prompt hashes. A pass authorizes consideration of the next paired holdout; it
does not count as reasoning-quality evidence.

The experiment has no retry. The extractor may make its one pre-existing,
prompt-locked quote-repair call because that behavior is part of the treatment.
Any failed admission gate is the final result for this frozen contract.

Artifacts:

- `contract.json`: frozen before the provider call;
- `run/lolla_admission_smoke_case12_20260710_a1_extraction.json`: provider-backed extraction, created only by the run;
- `/tmp/lolla_admission_smoke_case12_20260710_a1_extraction_calls.json`: local raw call sidecar;
- `result.json`: sanitized admission result and usage summary;
- `decision.json`: machine-readable stop/continuation decision;
- `review.md`: post-run interpretation and next-step decision.

The frozen attempt failed. See `review.md`; it is not authorized for rerun.
