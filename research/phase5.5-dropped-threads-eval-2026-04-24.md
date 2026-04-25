# Phase 5.5 dropped_threads — evaluation vs Phase 5.5 gold

**Date:** 2026-04-24  **Cases:** 8 / 8  **Wall time:** 12.8s

## Aggregate

| Metric | Value |
|---|---|
| Gold items total | 9 |
| Gold recovered | 5 (56%) |
| Speaker agreement on matched | 5/5 (100%) |
| Kind agreement on matched | 2/5 (40%) |
| Validation pass rate | 12/12 (100%) |
| User-raised events | 12 |
| Assistant-raised events | 0 |
| Events beyond gold | 7 |
| Validation dropped | 0 |

## Gate thresholds

| Metric | Result | Threshold | Verdict |
|---|---:|---:|:---:|
| Recall | 56% | ≥55% | PASS |
| Validation pass rate | 100% | ≥90% | PASS |
| Speaker agreement | 100% | ≥90% | PASS |
| Kind agreement | 40% | ≥75% | FAIL |

## Per-case

### `user_has_plan`

- raw: 1, validated: 1 (user=1, assistant=0), dropped: 0
- gold recovered: 1/1 — found=['UHP-D1'], missed=[]
- speaker: 1/1, kind: 1/1
- extras: 0

<details><summary>all validated events</summary>

1. [turn 1 / user / open_loop] 'Can you help me think through the launch plan? I want to hit the ground running.' → superseded_by: 'discussion of delaying launch, pipeline risks, and three strategic options'

</details>

### `whistleblower`

- raw: 1, validated: 1 (user=1, assistant=0), dropped: 0
- gold recovered: 1/1 — found=['WB-D1'], missed=[]
- speaker: 1/1, kind: 0/1
  - kind mismatch `WB-D1`: gold=`open_loop` llm=`concern`
- extras: 0

<details><summary>all validated events</summary>

1. [turn 7 / user / concern] 'If I report now, it might implicate her for not reporting two years ago.' → superseded_by: 'timeline and next steps for reporting'

</details>

### `multi_offer`

- raw: 2, validated: 2 (user=2, assistant=0), dropped: 0
- gold recovered: 0/1 — found=[], missed=['MO-D1']
- speaker: 0/0, kind: 0/0
- extras: 2

<details><summary>all validated events</summary>

1. [turn 3 / user / open_loop] 'Maybe I want to build something that feels more mine.' → superseded_by: 'pivoting to financial math and EV calculation for option B'
2. [turn 4 / user / open_loop] "So on expected value it's a hard question." → superseded_by: 'reframing as career-shape discovery rather than financial EV decision'

</details>

### `oncologist`

- raw: 2, validated: 2 (user=2, assistant=0), dropped: 0
- gold recovered: 0/2 — found=[], missed=['ONC-D1', 'ONC-D2']
- speaker: 0/0, kind: 0/0
- extras: 2

<details><summary>all validated events</summary>

1. [turn 5 / user / open_loop] 'the other fellows will see it' → superseded_by: 'distinguishing status concern about how you leave from whether you leave'
2. [turn 7 / user / concern] "my mother's dementia moves faster than expected" → superseded_by: 'general family stress risks and 18-month check-in'

</details>

### `phd_research`

- raw: 1, validated: 1 (user=1, assistant=0), dropped: 0
- gold recovered: 0/1 — found=[], missed=['PHD-D1']
- speaker: 0/0, kind: 0/0
- extras: 1

<details><summary>all validated events</summary>

1. [turn 16 / user / concern] 'I\'m 29, this is my only shot at a PhD. I don\'t want to pick the "smart" option and then regret not doing the ambitious o' → superseded_by: 'reframing option 3 as both ambitious and smart, without directly weighing regret risk'

</details>

### `real_estate`

- raw: 2, validated: 2 (user=2, assistant=0), dropped: 0
- gold recovered: 1/1 — found=['RE-D1'], missed=[]
- speaker: 1/1, kind: 1/1
- extras: 1

<details><summary>all validated events</summary>

1. [turn 4 / user / open_loop] "My husband's argument is that we love the neighborhood, houses there don't come up often, we'll regret walking away over" → superseded_by: 'countered with financial regret and buffer risks instead of engaging scarcity logic'
2. [turn 4 / user / concern] "I find that emotionally compelling but I don't know if I'm being sensible or just scared." → superseded_by: 'pivot to test question on boiler failure scenario'

</details>

### `friendship_money`

- raw: 1, validated: 1 (user=1, assistant=0), dropped: 0
- gold recovered: 1/1 — found=['FRI-D1'], missed=[]
- speaker: 1/1, kind: 0/1
  - kind mismatch `FRI-D1`: gold=`open_loop` llm=`concern`
- extras: 0

<details><summary>all validated events</summary>

1. [turn 4 / user / concern] "I don't think you understand the stakes here. She's going to be homeless. With her kids. If I don't help her." → superseded_by: 'asking if user is the only possible helper and suggesting other resources'

</details>

### `messy_three_problems`

- raw: 2, validated: 2 (user=2, assistant=0), dropped: 0
- gold recovered: 1/1 — found=['MSY-D1'], missed=[]
- speaker: 1/1, kind: 0/1
  - kind mismatch `MSY-D1`: gold=`open_loop` llm=`concern`
- extras: 1

<details><summary>all validated events</summary>

1. [turn 2 / user / concern] 'I love DC and my whole life is here.' → superseded_by: "focusing on boyfriend commitment and mom's care as root blockers"
2. [turn 3 / user / concern] 'moving cities feels huge and I\'ve never done it before. I\'ve lived in DC for 11 years. The "my life is here" part is rea' → superseded_by: "pressure-testing boyfriend's commitment and dismissing as adjustment anxiety"

</details>
