# Reasoning-process stance-object v4 result

Status: provider-free design passes; frozen provider probe fails before inference  
Date: 2026-07-12

## Simple result

V4 solves the representation problem locally. Instead of applying one force
label to an entire position, it represents small source-linked components. Each
component says whether it concerns a belief, action or proposal, intended
outcome, willingness to accept, or a reported position landscape. This lets the
same sentence carry a plan to make a proposal and separate uncertainty about
accepting its outcome.

The provider-free result passed:

- all 60 prompts built;
- all 20 reviewed fixtures compiled with zero quarantine;
- the preserved Case-03 belief-versus-decision and proposal-versus-acceptance
  failures are representable;
- all non-position interfaces stayed byte-identical to v2;
- nine adversarial outcomes passed;
- 184 reasoning-process tests passed before execution;
- no deterministic keyword, semantic compatibility, scoring, hierarchy, graph,
  or runtime behavior was added.

The current-practice check also improved the first draft. Replacing three
repeated component arrays with one temporal-role array reduced the maximum
schema from 6,941 to 3,919 bytes.

## Provider result

The single frozen Case-04 request did not reach model inference. OpenRouter
routed it to Google, which returned HTTP 400 `INVALID_ARGUMENT`. There was no
candidate JSON, no compiled record, no token or cost observation, and nothing
to source-review semantically. The result file's prewritten
`pending_source_first_review` status is clarified append-only as
`not_applicable_no_model_output`; the frozen result was not changed.

The exact invalid argument is not exposed. Schema complexity is plausible:
v4 is depth 11 and adds a component object containing another evidence array,
whereas the previously served v3 schema was depth 9. Official Gemini guidance
warns that large or deeply nested schemas may be rejected. This is not a proven
root cause, so the failure must remain operational rather than semantic.

## What we learned

The stance-object idea remains promising, but provider-free conformance is not
provider compatibility. The next contract should make each component atomic
with one source alias. A multi-source landscape can become two components.
That removes the new nested evidence array, reduces depth, and fits the
microtask principle better while preserving exact source custody.

The regression suite also caught an attempted modification of the shared runner
frozen by v3. The shared file was restored to its exact recorded hash and v4
execution was isolated in a new runner. This is evidence that the custody rules
are working, not merely documented.

## Decision and next work

V4 is not ready for integration, graph, runtime, full-case, stability, or
receipt work. Case-04 is closed and may not be repaired or retried.

The next bounded goal should be provider-free v4.1 simplification plus fresh
case construction:

1. retain explicit stance objects and one component array;
2. use one source alias per atomic component;
3. avoid new schema keywords outside Gemini's documented subset when
   deterministic post-validation is sufficient;
4. replay the reviewed corpus and adversarial failures locally;
5. design new ambiguous multi-turn position cases because all five existing
   cases are closed;
6. authorize at most one newly selected case after compatibility and cold-reader
   gates pass.

Primary evidence:

- `research/reasoning-process-stance-object-v4-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v4-2026-07-12/adversarial-review.json`;
- `docs/evals/reasoning-process-stance-object-v4-cold-reader-review.json`;
- `research/reasoning-process-stance-object-v4-probe-2026-07-12/contract.json`;
- `research/reasoning-process-stance-object-v4-probe-2026-07-12/result.json`;
- `research/reasoning-process-stance-object-v4-probe-2026-07-12/operational-review.json`.
