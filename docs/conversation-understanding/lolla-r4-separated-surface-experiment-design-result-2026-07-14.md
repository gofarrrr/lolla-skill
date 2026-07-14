# R4 separated-surface experiment design result

Date: 2026-07-14

Status: complete provider-free design; no execution authorization

Scientific question: Does asking for the two existing residual surfaces in
separate provider calls reduce unsupported opposite-surface companion records
relative to asking for both surfaces together, while preserving genuine
findings?

Provider calls: 0

Provider cost: `$0.00`

## Custody sequence

The source/prior checkpoint is `f57829246fc4b2925ce56fd0fbb61bbde311234a`.
The declaration `human leakage review passes for R4 separated-surface source
freeze v1` is bound to the exact frozen bytes in checkpoint `69d3026`. The
protected source-first target and its review were then frozen in checkpoint
`740a525`, before any prompt, schema, or request preview existed. The reviewed
source and prior bytes did not change.

Protected evidence:

- `docs/evals/lolla-r4-separated-surface-experiment-v1-target.json` — SHA-256
  `d33b73a26d456b3c3322f191f51e7d1a820685b9b446f8f272654062bfd2117b`;
- `docs/evals/lolla-r4-separated-surface-experiment-v1-target-review.json` —
  SHA-256
  `13babc7a754ae8060859a3797dc800e9d5f2b817745ef20c4213f5db03383312`.

The target honestly confirms the intended portfolio: Case 01 and Case 02 are
quiet on both canonical surfaces; Case 03 has one supported
`unresolved_matter` and a quiet `reopen_condition`; Case 04 has a quiet
`unresolved_matter` and one supported `reopen_condition`. No intended role was
contradicted. These are protected human source-first judgments, not
provider-visible labels.

## Frozen matched intervention

The paired arm requests both residual surfaces in one call and returns two
reviews with a 1,600-token output cap. The separated arm requests one surface
per call, returns one review, and uses two 800-token caps. There are four paired
calls and eight separated calls in a counterbalanced twelve-call plan.

The only allowed provider-visible changes are the requested surface count,
returned review count, call count, necessary singular grammar, 1,600 versus
800+800 allocation, and schema name/container differences needed to represent
one review. Every exact JSON-path difference is inventoried; undeclared deltas
fail validation.

Complete source and prior bytes, aliases, source-to-prior-to-task order,
task-at-end placement, residual ontology and subtraction rules, evidence
authority, zero and ambiguity semantics, record fields and bounds, canonical
mapping, model, route, seed, reasoning, strict JSON, streaming, privacy, and
retry/fallback policy remain equal. The provider surfaces map without reading
prose:

- `residual_decision_gap` to `unresolved_matter`;
- `residual_reconsideration_dependency` to `reopen_condition`.

The execution-visible package and runner contain no protected-target path,
hash, classification, human-review conclusion, or discovery mechanism.

## Frozen request plan

| Ordinal | Case | Arm | Surface | Request-body SHA-256 |
| ---: | --- | --- | --- | --- |
| 1 | cave rescue | paired | both | `82ef9cbfc4352d87b6c4b4b7169a341d771c33060a1c4347a0df54b5a4d8419a` |
| 2 | cave rescue | separated | decision gap | `d6e09d7d6dcb67782571b31a828f4ada784b3befed86c660b8451e67905959ab` |
| 3 | cave rescue | separated | dependency | `e0eed2349ac5a22ce92c96642433b03a0e5ca722efe76d1ef32ab88b4c103bd7` |
| 4 | observatory | separated | decision gap | `4374fbe8f1fe8794404a3d6867dcf85d578f2126bee6e88d90efa2c2d56f3368` |
| 5 | observatory | separated | dependency | `0ec3b96becb2f4f800d67fb6fd344dc0d52d8170ea34235f5a6b05a15acbb860` |
| 6 | observatory | paired | both | `b6bd9ff0ae8d893e0995f517e02f8b0ed1b9376b0033b6d4980b7af6c3000bc8` |
| 7 | performance tour | separated | dependency | `c04af65cc3a9803d9595c8d39923eddfabc5174823c6963fec12263202c949f2` |
| 8 | performance tour | paired | both | `783e04d5ccd6e383733e0282b7de9f9444b6c2e6c8c4b50bfbe00e3376ee18d3` |
| 9 | performance tour | separated | decision gap | `8cf968e8ef07a9d677536dfb3df7957e04f32ccb5abe42a66ef815b3f9b90a11` |
| 10 | seed preservation | paired | both | `1c837d18fadc2868d3e6c1ae88c2c587e3ca901892610883b23f4d451aeddbc4` |
| 11 | seed preservation | separated | dependency | `a39feed4885b0a93377c4bcbb60f204b1ed2e73073aa337aef14202bf753152f` |
| 12 | seed preservation | separated | decision gap | `ac1d0cf85b75be2468c0a14da946bdc3c4def482a13e011b2c2cb9e8806148f3` |

## Evaluation and interpretation boundary

The frozen evaluation is categorical and non-scalar. Companion pressure is
supported only if paired calls create unsupported opposite-surface companions
on both positive cases, the corresponding separated calls remove them, and
the genuine Case 03 present finding and Case 04 future dependency remain
recoverable. Other outcomes separately identify persistent companions,
overcorrection, a non-discriminating paired arm, mixed evidence, or mechanical
non-evaluability.

Case 01 and Case 02 remain separate difficult-zero controls. Even a clean
companion result cannot establish reader safety: governed thresholds,
scheduled decisions, assistant-proposal authority, evidence adjudication,
transfer to real conversations, and real-user usefulness remain independent
blockers.

## Runner and cost custody

The future runner validates an exact separately supplied one-use authorization,
the frozen contract, all twelve request hashes, model/provider/generation
identity, usage, cost, reasoning exclusion, strict JSON, and local structural
admission. It preserves exact request and first terminal response bytes and
stops immediately on the first failure. Retries, fallbacks, healing,
substitutions, relationship/evaluator/embedding/graph/pipeline/runtime calls
are fixed at zero. Dry run constructs no transport.

Using exact request-size estimates, the maximum-output conservative estimate is
`$0.0485325`. This includes duplicated separated-arm input, an inherent cost of
the intervention. The proposed hard ceiling is `$0.075` per case and `$0.30`
total, solely as an anomaly, duplicate-call, and loop stop. It is not an
execution authorization.

## Decision

The complete provider-free design is ready for a separate founder publication
decision. Only after canonical publication could the founder separately choose
whether to issue one exact execution authorization. This result makes no model
semantic, production-readiness, integration, or product-usefulness claim.

## Verification

- frozen contract SHA-256:
  `2e3a731ba3880ed883044e5aa0ee039d4cf1f38925b785cf3325a0ffb4b18dde`;
- focused R4 slice: 123 passed;
- complete repository suite: 4,961 passed and 93 subtests passed, with the one
  existing `datetime.utcnow()` deprecation warning;
- historical replay: exactly 12 cases, 543 case/artifact links, and 400 unique
  frozen JSON artifacts;
- 54 changed JSON artifacts parsed;
- changed Python compiled;
- `git diff --check` passed;
- added-lines secret scan found zero secret-shaped values;
- Git object integrity passed;
- dry run: zero calls, `$0.00`, and no transport construction.
