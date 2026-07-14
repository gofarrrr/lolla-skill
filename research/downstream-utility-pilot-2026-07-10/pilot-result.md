# Downstream Utility Pilot Result

Date: 2026-07-10  
Status: two-call directional pilot complete; human review pending

## Result

The strong reconsideration control and the Lolla-pressure treatment produced
the same likely next action.

Both answers:

- withdrew the claim that prestige and friendly emails justified a public
  launch;
- required firmer participation or publicity commitment;
- checked engineering capacity before commitment;
- separated a private beta from public announcement;
- moved success or stop criteria before launch.

The control was slightly more explicit about permission to use the logo. The
treatment was slightly more explicit about separable commitments,
reversibility, and stop conditions. Those are differences in specificity, not
different user action. Treatment used 495 completion tokens versus 443 for the
control.

Blind review therefore found no material winner before the arm key was
revealed. After reveal, A was the strong control and B was the Lolla treatment.

## Decision

The positive-case success rule failed because treatment did not add a unique,
decision-relevant delta beyond control. Do not repeat this case, change the
prompt, or expand it to three samples per arm.

This is not evidence that Lolla is useless. The original advice in this case
was conspicuously weak: it called prestige market evidence, minimized capacity
risk, and deferred success criteria. A strong fresh model can see those errors
directly from the conversation. This case demonstrates that Lolla can produce a
good correction, but not that its machinery is necessary for the correction.

## What we learned

The correct product baseline is demanding. Lolla must beat more than the
original bad answer; it must beat a fresh strong reconsideration of that answer.

Future positive cases should test a non-obvious delta, such as preserving
ambition while changing authority, detecting an unresolved decision state, or
retracting an overconfident psychological interpretation. The next bounded
test should first be a quiet case where the existing answer already carries the
important pressure. In that case, success means standing down or staying
compact—not adding more analysis.

No runtime change or semantic-kernel integration is authorized.

