# Reasoning mechanism ontology v1

Status: research-only, runtime dormant  
Date: 2026-07-12

## Decision target

The interpreter answers one question: **which abstract reasoning weakness remains unresolved in the final joint reasoning trajectory?** It does not catalogue every mistake made by either actor at any earlier point.

Every controlled mechanism is reviewed exactly once as `unresolved`, `resolved_in_conversation`, `ambiguous`, or `not_observed`. Exhaustive review prevents omission; it does not imply that every mechanism is present. Only `unresolved` may enter the fact-free routing projection.

## Why v1 is necessary

The first role-record interpreter mixed an older local-pattern catalogue with the later joint-process routing target. It supplied suggestive mechanism names without operational definitions and routed all `present`, `missing_protection`, and `tension` states. Its six-arm probe consequently saturated the six-pattern cap, changed labels and actor scopes under harmless record variation, and failed protected-mechanism sensitivity.

V1 resolves that target conflict. The complete machine-readable definitions live in `engine/system_b/reasoning_mechanism_ontology.py`. Every card contains:

- an operational definition;
- evidence that is required;
- explicit exclusions;
- a distinction from its nearest confusing neighbor.

## Scope

`user` and `assistant` describe actor-local audit observations. They are not automatically reasoning weaknesses in the final trajectory. `joint_process` describes what remains after both contributions and any later repair are considered. This interpreter produces only joint-process routing nodes.

## Status and legacy state

- `unresolved`: remains operative; routes as `present` or `missing_protection`.
- `resolved_in_conversation`: appeared and was materially repaired; audit only.
- `ambiguous`: evidence supports competing interpretations; audit reserve only.
- `not_observed`: bounded records do not support it; audit only and not a claim about reality.

Legacy `tension` now corresponds to ambiguity, not weak confidence and not active routing. `missing_protection` requires bounded inspection of a safeguard; it cannot be inferred from ordinary uncertainty. This corrects the earlier shadow's use of `tension` as an active joint seed.

## Hybrid boundary

The model decides semantic status from the role records and ontology. Deterministic code only verifies complete mechanism coverage, enum compatibility, exact record IDs, hashes, fact leakage, and the rule that only model-declared `unresolved` rows route. It does not use keywords or facts to change a semantic decision.

No raw conversation, evidence quotation, case fact, graph model name, or expected answer enters the routing projection. No graph or runtime integration is authorized by this design.

