# Case 05 strict-schema transfer probe v2

Status: **closed operational interoperability failure**

The provider-specific repair did not reach semantic inference. Google again
returned HTTP 400 `INVALID_ARGUMENT` for the thread schema through OpenRouter.
The change from nullable type array to `anyOf` was therefore not sufficient.
The frozen stop rule prevented the constraints and positions calls.

One local wrapper mismatch was encountered and repaired before any provider
call; it is preserved in `pre-provider-runner-failure.json`. The repair changed
only the internal label bridge and did not change prompts, schemas, selection,
or budget.

This run does not tell us whether thread, constraint, or position extraction
improved. It tells us that strict provider-side schema enforcement is currently
an unreliable experimental boundary for this OpenRouter-to-Google path.

The recommended next wire mode is `json_object` with the exact typed schema in
the prompt and the existing local typed, source-custody, ledger, and quarantine
checks. That is not a relaxation of semantic admission: malformed or
unsupported candidates still fail closed. It moves syntax enforcement away
from the provider adapter that is preventing inference.

A new call requires a new prospective contract and authorization.

