# Decision Work Receipt Debug Summary

This is an internal diagnostic packet generated from Lolla custody artifacts. It is not the customer-facing decision story and not a judgment that the final answer was correct or useful.

## Case

- Case: `launch-public-enterprise-beta`
- Run: `20260627T104146Z_7bfe79`
- Receipt readiness: `decision_trail_review_ready`
- Receipt mode: `checked_in_safe_mode`

## What Happened

- Process shape: `multi_turn_evidence`
- Captured turn metadata: reported total `12`, `12` user, `12` assistant (role counts sum to `24`; treat this as a metadata inconsistency, not a semantic finding).
- Maintainer meaning: this was not just a one-prompt answer; Lolla sees evidence of a back-and-forth conversation.
- Boundary: turn count is process evidence, not proof of good thinking.

## What Lolla Challenged

- Visible challenge surfaces:
  - structural pressure
  - model companion
  - frame pressure
  - structural coverage
  - delivery bullshit-index check
  - audit summary trace
  - private enrichment
  - optional pressure-check state
  - pre-Step-6 private table
  - graph survival report
- Run-health caveats: none recorded in the receipt.
- Boundary: visible challenge surfaces are not proof that the challenge was sufficient.

## What The Receipt Links

- Decision Trail report: `available_from_structured_artifact`
- Product Delta report: `not_supplied`
- Maintainer meaning: linked reports make the process easier to inspect, but do not turn the receipt into proof.

## What The Decision Trail Can Read

- Available from structured artifacts:
  - conversation understanding summary
  - decision question
  - constraints
  - audit pressure summary
  - structural delta
- Still requiring LLM or human interpretation:
  - vanilla likely next action
  - revised likely next action
  - option map
  - stakeholders
  - values/priorities
  - assistant influence
  - useful/noisy friction
  - lost value
- Missing, unclear, or not supplied:
  - unresolved questions: `not_supplied`
- Boundary: this is field status, not answer-quality scoring.

## What Is Still Missing Or Private

- Safe structured sources read: `11`
- Raw/redacted/private sources not exported: `10`
- Missing sources: `1`
- Fields still needing interpretation:
  - `conversation_process_map.semantic_process_fields`
  - `challenge_coverage.challenge_quality`
  - `decision_trail_summary.semantic_interpretation`
  - `product_delta_summary.product_value`
  - `process_evidence_readiness.semantic_meaning`
- Boundary: private availability is different from missing; the receipt records that distinction without exposing private content.

## What This Must Not Be Used For

- clean artifacts do not imply good advice
- not agent action authorization
- not answer-quality scoring
- not correctness proof
- not an LLM judge
- not product proof
- not runtime integration

## Internal Diagnostic Read

- This case is ready for a reviewer to inspect the work trail, because the receipt has process evidence and a linked Decision Trail reference.
- What this helps maintainers inspect: whether a visible process existed, which artifacts support that process, what was private or missing, and which interpretation fields remain unresolved.
- What this does not give users: the actual decision consequence, what action changed, which trade-off mattered, whether Lolla improved the decision, or whether an agent should act.
- Current product gap: the user-facing brief still needs bounded LLM or human interpretation for options, likely actions, stakeholders, useful/noisy friction, lost value, and action consequence.
