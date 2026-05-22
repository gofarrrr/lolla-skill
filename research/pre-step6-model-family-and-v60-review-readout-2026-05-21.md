# Pre-Step-6 Model-Family And V60 Review Readout

Date: 2026-05-21

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The repaired Kimi calibration left four variable cases. A GPT probe then made
three of those cases visibility-stable, but stability is not correctness. This
review asked three narrower questions:

```text
1. Is founder variance tied to V60-on context, or is the base founder case
   itself unstable?
2. Are GPT-stable PhD visible outputs actually reviewer-supported?
3. Is GPT's stable consultant stand-down correct, or confident wrongness?
```

The deterministic scripts only build contracts, compare saved sample shapes,
and aggregate reviewer labels. They do not decide which answer is wiser.

## Founder V60 Symmetry

Artifacts:

- `research/pre-step6-founder-v60-symmetry-check/founder-v60-symmetry-contract.v1.json`
- `research/pre-step6-founder-v60-symmetry-check/founder-v60-symmetry-result.v1.json`
- `research/pre-step6-founder-v60-symmetry-kimi/step6-samples/*.json`
- `research/pre-step6-founder-v60-symmetry-gpt51/step6-samples/*.json`

Result:

| Model family | V60 mode | Samples | Unlocks | Read |
| --- | --- | ---: | ---: | --- |
| `moonshotai/kimi-k2.6` | on | 6 | 4 | variable |
| `moonshotai/kimi-k2.6` | off | 6 | 6 | stable positive |
| `openai/gpt-5.1-chat` | on | 3 | 2 | variable |
| `openai/gpt-5.1-chat` | off | 3 | 0 | stable stand-down |

Aggregate:

```text
symmetry_read = v60_on_specific_destabilization_plausible
recommended_next_action = audit_v60_private_context_before_architecture_choice
```

Interpretation:

Both model families are variable on founder V60-on. Neither model family is
variable on founder V60-off. They disagree on the V60-off direction
(Kimi visible, GPT anchor), so this does not prove which output is correct.
It does support a narrower claim: founder's residual instability is plausibly
triggered by the V60-on private context, not by the base founder case alone.

This is an existing-system/V60 audit finding, not a reason to add a portfolio
visibility gate.

## GPT Stability Correctness Review

Artifacts:

- `research/pre-step6-gpt-stability-correctness-review/gpt-stability-correctness-contract.v1.json`
- `research/pre-step6-gpt-stability-correctness-review/judgments/*.json`
- `research/pre-step6-gpt-stability-correctness-review/gpt-stability-correctness-result.v1.json`

Reviewer families:

```text
openai/gpt-5.1-chat
google/gemini-3.1-flash-lite
```

The contract separated answer quality from visibility-decision correctness:

```text
output_label: better | non_inferior | worse_but_visible | worse_unwise | tie | ambiguous
visibility_judgment: correct_visible | correct_anchor | wrong_visible | wrong_anchor | ambiguous
```

Aggregate:

```text
case_count = 9
gpt_visible_case_count = 6
gpt_anchor_case_count = 3
gpt_visible_supported_count = 6
gpt_visible_rejected_count = 0
gpt_anchor_supported_count = 0
gpt_anchor_rejected_count = 1
ambiguous_count = 2
tension_count = 1
structural_delta_only_reviewed_count = 3
structural_delta_only_supported_count = 3
structural_delta_only_rejected_count = 0
reviewer_read = gpt_stability_design_review_required
```

Case read:

| Case group | Result |
| --- | --- |
| PhD V60-off, GPT visible | 3/3 supported |
| PhD V60-on, GPT visible | 3/3 supported |
| Pure `structural_delta_present` GPT visible samples | 3/3 supported |
| Consultant, GPT anchor stand-down | 1 rejected, 2 ambiguous, 1 tense record |

Interpretation:

GPT's stability is useful evidence on the PhD cases: both reviewer families
supported all six GPT-visible PhD outputs, including all three pure
`structural_delta_present` samples. This means the structural-delta path is not
just syntactically valid; in these samples, reviewers found the structural
changes useful enough to show.

GPT's stability is not uniformly trustworthy. On consultant, GPT stabilized at
anchor-visible, but reviewers did not cleanly support that stand-down. One
sample was confirmed `gpt_anchor_rejected`: both reviewer families preferred or
accepted the GPT Step 6 answer as visible. Two consultant samples remained
ambiguous, and one reviewer record had label/winner-arm tension.

So the result is not "ship GPT because it is stable." The result is:

```text
GPT stability can align with correctness on some case shapes.
GPT stability can also suppress useful visible answers on other case shapes.
Model-family stability is evidence, not authority.
```

## Model Commitment Contract

The Step 6 model class is now part of the calibrated contract.

Consequences:

- Calibration claims are model-scoped. The Kimi calibration result describes
  `moonshotai/kimi-k2.6` under the repaired prompt, not arbitrary Step 6 models.
- GPT evidence describes `openai/gpt-5.1-chat` on the reviewed variable cases,
  not a global provider swap.
- A future model upgrade, provider swap, or OpenRouter backend change is a
  recalibration event.
- Model-family stability cannot become a hidden cognitive shortcut. Reviewer
  evidence is required before stability can be treated as useful.
- Mixed model-family samples must not be blended into one calibration read
  unless the read explicitly says it is cross-model diagnostic evidence.

## Decision

```text
runtime_promotion_blocked
skill_update_blocked
global_shadow_implementation_blocked
do_not_model_route_for_stability_alone
audit_founder_v60_private_context_before_architecture_choice
preserve_structural_delta_vocabulary
```

The next design conversation should focus on two findings:

1. Founder V60-on looks like a V60 destabilization/audit problem.
2. GPT improves the PhD variable cases but fails to cleanly support consultant
   anchor stand-down.

No deterministic selector should be added to hide this variance. The system is
getting smarter by preserving where cognition is unstable, not by pretending the
unstable cases are solved.
