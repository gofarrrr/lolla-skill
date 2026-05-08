# Reasoning Substrate Packet Comparison

Compare handoff usefulness only.

- Do not answer the user case.
- Do not choose user-visible output.
- Do not rank final wisdom.
- Review whether the later packet improves activation, evidence, dismissal, misuse, treatment, absence, and burden.

## Compared Packets

- Before: `pr27-mixed-packet-review`
- After: `pr29-v5-mixed-packet-depth-review`

## Count Delta

| Measure | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 7 | 7 | 0 |
| Reviewed cards | 3 | 7 | +4 |
| Graph-only cards | 4 | 0 | -4 |
| Missing reviewed records | 4 | 0 | -4 |
| Absence-only cards | 0 | 0 | 0 |
| Source-too-thin cards | 0 | 0 | 0 |
| Weak/conflicting cards | 0 | 0 | 0 |

## Coverage Changes

- `chain-of-verification`: `graph_only_runtime_card` -> `reviewed_affordance_available`
- `confirmation-bias`: `graph_only_runtime_card` -> `reviewed_affordance_available`
- `constraints`: `graph_only_runtime_card` -> `reviewed_affordance_available`
- `step-back`: `graph_only_runtime_card` -> `reviewed_affordance_available`

## Reviewer Rubric

- Activation clarity: worse / same / better
- Evidence-needed clarity: worse / same / better
- Do-not-use clarity: worse / same / better
- Misuse-guard usefulness: worse / same / better
- Treatment usefulness: worse / same / better
- Absence/overclaim protection: worse / same / better
- Packet burden: lighter / acceptable / too heavy
- Net handoff judgment: no added depth / useful depth / useful depth but too bulky
