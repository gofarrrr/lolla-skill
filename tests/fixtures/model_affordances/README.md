# Model Affordance Fixtures

These files are validation fixtures for the dormant model-affordance contract.
They are not reviewed corpus extraction and must not be compiled into runtime
artifacts.

- `theory_of_constraints_valid.json` is a strong source-backed fixture shaped
  from a small number of exact source quotes.
- `source_too_thin_valid.json` and `not_supported_by_source_valid.json` are
  synthetic absence fixtures. They prove the schema does not require every
  model to have affordances.
- `*_invalid.json` files intentionally fail validation and exist only to keep
  future bulk generation honest.

Future pilot extraction PRs should add reviewed model records outside this
fixtures directory. Reviewed records must not share a directory with
intentionally-invalid JSON.
