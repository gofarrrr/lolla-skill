# Pre-Step-6 Founder V60 Private Context Audit Readout

Date: 2026-05-22

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The model-family/V60 review showed that Founder becomes variable for both
model families only when V60-on private context is present:

```text
Kimi V60-on: 4/6 unlock, variable
Kimi V60-off: 6/6 unlock, stable positive
GPT V60-on: 2/3 unlock, variable
GPT V60-off: 0/3 unlock, stable stand-down
```

This audit asked a narrower question:

```text
What did the V60 private context add to the Founder case, and which
precommitted failure hypothesis does the saved evidence support?
```

This slice explicitly exits the pre-Step-6 portfolio perimeter. It audits V60
private-context behavior. It does not decide the correct Founder answer, does
not resolve Consultant, does not resolve PhD, and does not promote runtime or
`SKILL.md`.

## Artifacts

- `scripts/research/pre_step6_founder_v60_private_context_audit.py`
- `tests/test_pre_step6_founder_v60_private_context_audit.py`
- `research/pre-step6-founder-v60-private-context-audit/founder-v60-private-context-audit-contract.v1.json`
- `research/pre-step6-founder-v60-private-context-audit/founder-v60-private-context-audit-result.v1.json`

## Precommitted Outcomes

The contract preserved four interpretations before reading the audit result:

```text
genuine_edge_pressure_structurally_borderline
selection_noise
joint_overload
cross_chunk_consideration_gap
```

That matters because the deterministic artifact must not collapse the variance
into a convenient story after the fact.

## Result

The V60 context in saved Founder V60-on samples was:

```text
v60_chunk:overcommitment_without_evidence - Watch for informal promises becoming public commitments before written evidence and board process exist.
```

The mechanical relevance check found overlap with the case surface:

```text
overlap_terms = board, commitments, evidence
relevance_read = related_surface_terms_present
```

The aggregate audit read is:

```text
audit_read = v60_context_related_but_destabilizing
recommended_next_action = review_v60_selection_packet_before_architecture_choice
founder_answer_correctness = not_decided
consultant_followup_status = queued_not_addressed
phd_followup_status = queued_not_addressed
```

Outcome evidence:

| Outcome | Evidence state | Read |
| --- | --- | --- |
| `genuine_edge_pressure_structurally_borderline` | `plausible` | V60 is related, and V60-off does not settle answer correctness because Kimi and GPT stabilize in opposite directions. |
| `selection_noise` | `weak` | The chunk is not obviously unrelated noise; it shares concrete terms with the case. |
| `joint_overload` | `plausible` | Both model families become variable on V60-on and not on V60-off. The chunk may be individually defensible but destabilizing in the combined private packet. |
| `cross_chunk_consideration_gap` | `insufficient` | Saved Founder samples expose one synthetic V60 chunk, so cross-chunk behavior is not testable here. |

## Interpretation

This is not evidence that V60 is bad. It is evidence that this V60 private
context is related to the Founder reasoning shape and still destabilizes Step 6
on both tested model families.

The cleanest current hypothesis is packet interaction, not unrelated selection
noise. The V60 pressure may be individually defensible, but in this private
context it pushes Step 6 into inconsistent reads about whether the deck pressure
should become visible.

That does not authorize a new deterministic selector. The deterministic layer
learned an evidence shape; it did not decide wisdom.

## Limits

Founder remains unresolved at the answer level. Removing V60 stabilizes each
model family, but Kimi stabilizes positive while GPT stabilizes stand-down. So
this audit characterizes V60 contribution, not the correct Founder answer.

Consultant remains unresolved. GPT's stable consultant stand-down was not
cleanly reviewer-supported, and Kimi remained variable. That needs its own case
ambiguity design review.

PhD remains unresolved. GPT was stable and reviewer-supported on PhD, while Kimi
was variable. That is a Kimi/PhD variance finding, not permission to model-route
for stability.

Structural-delta validation remains small-N. The 3/3 GPT pure
`structural_delta_present` support is viable directional evidence, not global
robustness.

## Decision

```text
runtime_promotion_blocked
skill_update_blocked
global_shadow_implementation_blocked
no_new_deterministic_selector
founder_v60_private_context_characterized
consultant_case_ambiguity_design_review_v0_queued
kimi_phd_variance_diagnostic_v0_queued
```

Next safe research moves:

1. `consultant_case_ambiguity_design_review_v0`
2. `kimi_phd_variance_diagnostic_v0`

Do not let the V60 audit absorb those separate findings. The system is getting
smarter by preserving heterogeneity: V60 destabilization, Consultant ambiguity,
and PhD model-family sensitivity are different problems.
