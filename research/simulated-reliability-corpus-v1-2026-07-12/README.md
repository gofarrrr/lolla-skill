# Lolla simulated reliability corpus V1

Status: **naturalized source corpus frozen; no Lolla pipeline calls run**  
Date: 2026-07-12

V1 is the first balanced corpus for evaluating Lolla's complete
reasoning-pressure loop across consequential, ambiguous simulations. It is not
real-user evidence.

Read in this order:

1. `../../plans/lolla-simulated-reliability-corpus-v1-2026-07-12.md` — goal,
   evidence boundary, scorecard, experiment ladder, and stop rules;
2. `manifest.json` — frozen source identities, hashes, and custody boundary;
3. `authoring-contract.json` — source-shape and anti-leakage requirements;
4. `inventory.json` — why existing cases are calibration-only;
5. `source-review.json` — hidden source-level behavior strata and review notes;
6. `pre-call-draft-record.json` — custody record for the rejected short draft;
7. `transfer-sources/` — immutable semantic skeletons used during source work;
8. `naturalization-run/` — preserved rejected Gemini source-editor attempt;
9. `naturalized-source-review.json` — admission review for the final sources;
10. `naturalized-transfer-sources/` — twelve final frozen 24-message conversations;
11. `provider-free-three-arm-preflight/` — local pressure and quiet packaging
    proofs with zero provider calls.

## Shape

- eight known calibration conversations;
- twelve new prospective simulated transfer conversations;
- twelve user/assistant pairs per transfer case;
- 288 transfer messages and 21,938 transfer words;
- six pressure-expected, four stand-down-expected, and two park-expected cases.

Each final transfer conversation continues beyond a first reasonable recommendation.
Later evidence or resistance reopens the reasoning, an earlier thread returns,
and the final position shows what changed and what remained unresolved.

## Claims boundary

V1 can test custody, semantic and temporal interpretation, abstraction,
deterministic replay, candidate disposition, paired-control contribution,
false pressure, unsupported precision, and cold-reader transfer under simulated
conditions.

V1 cannot establish real-user usefulness, population representativeness, human
decision improvement, production reliability, or unique value from graph
expansion.

## Provider-free validation

Run:

```bash
/tmp/lolla-phase0-py312/bin/python scripts/evals/validate_simulated_reliability_corpus_v1.py
/tmp/lolla-phase0-py312/bin/python -m pytest -q \
  tests/test_simulated_reliability_corpus_v1.py \
  tests/test_capture_ready_development_corpus.py \
  tests/test_skill_capture_validator.py
```

The earlier seven-test result applied to the structurally expanded checkpoint.
The naturalized manifest and validator supersede it. The rejected source-editor
calls do not authorize Lolla execution. Provider-free three-arm packaging now
passes on pressure and quiet sentinels; the runtime and evaluation contract
must still be frozen before any calibration call.
