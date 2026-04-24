# Phase 5 live_constraints — evaluation vs Phase 5.0 gold

**Date:** 2026-04-24  **Cases:** 5 / 5  **Wall time:** 12.5s

Runs `extract_live_constraints` on each of the 5 annotation-gate cases and compares LLM output to the 20 gold items. Measures recall, output-mode fidelity (span vs derivation), kind agreement on matched events, validation pass rate, and extras (valid events not in gold).

## Aggregate

| Metric | Value |
|---|---|
| Gold items total | 20 |
| Gold recovered | 14 (70%) |
| Span-only recall (15 items) | 9/15 (60%) |
| Derivation-only recall (5 items) | 5/5 (100%) |
| Mode fidelity on matched | 9/14 (64%) |
| Kind agreement on matched | 13/14 (93%) |
| LLM validation pass rate | 34/35 (97%) |
| Total validated events | 34 (34 span, 0 derivation) |
| LLM events beyond gold | 20 |
| LLM validation dropped | 1 |

## Gate thresholds

| Metric | Result | Threshold | Verdict |
|---|---:|---:|:---:|
| Recall | 70% | ≥55% | PASS |
| Validation pass rate | 97% | ≥90% | PASS |
| Kind agreement | 93% | ≥75% | PASS |
| Span recall | 60% | ≥60% | PASS |
| Derivation recall | 100% | ≥40% | PASS |

## Per-case

### `user_has_plan`

- raw: 5, validated: 5 (span=5, derivation=0), dropped: 0
- gold recovered: 3/4 — found=['UHP-C1', 'UHP-C2', 'UHP-C3'], missed=['UHP-C4']
- mode match: 1/3
  - `UHP-C2`: gold=`derivation` llm=`span`
  - `UHP-C3`: gold=`derivation` llm=`span`
- kind match: 3/3
- extras (not in gold): 2

<details><summary>all validated events</summary>

1. [span / turns=1 / constraint] 'I have 8 months runway saved'
2. [span / turns=1 / constraint] 'Plan is to go independent starting in 6 weeks'
3. [span / turns=2 / constraint] 'I\'ve had informal conversations with 4-5 former colleagues and people in my network who\'ve said things like "if you were'
4. [span / turns=2 / constraint] '8 months assumes zero revenue'
5. [span / turns=5 / constraint] "Hasn't been part of the runway discussion in specifics — I've kept that in my head"

</details>

### `whistleblower`

- raw: 7, validated: 7 (span=7, derivation=0), dropped: 0
- gold recovered: 3/4 — found=['WB-C1', 'WB-C3', 'WB-C4'], missed=['WB-C2']
- mode match: 3/3
- kind match: 3/3
- extras (not in gold): 4

<details><summary>all validated events</summary>

1. [span / turns=1 / constraint] 'Mid-level consultant at a large professional services firm (think big-4 adjacent). 8 years with the firm.'
2. [span / turns=4 / constraint] "I have a mortgage, two kids about to start high school, we're not independently wealthy."
3. [span / turns=1 / constraint] 'That account is in active audit with a major regulator right now.'
4. [span / turns=9 / constraint] 'I have a meeting with that partner on Wednesday. Regular weekly status.'
5. [span / turns=6 / constraint] "I'd say 60-65%. He's a good guy but the firm has had issues before and they handled them quietly."
6. [span / turns=7 / concern] "I'm not the only one who might have seen things. Two years ago, a senior manager in my group left abruptly. Everyone ass"
7. [span / turns=3 / open_loop] "No. I should do that. I've just been thinking about it. I'll write it down tonight."

</details>

### `parenting_teen`

- raw: 8, validated: 7 (span=7, derivation=0), dropped: 1
- gold recovered: 2/4 — found=['PT-C2', 'PT-C3'], missed=['PT-C1', 'PT-C4']
- mode match: 2/2
- kind match: 1/2
  - `PT-C2`: gold=`constraint` llm=`concern`
- extras (not in gold): 5

<details><summary>all validated events</summary>

1. [span / turns=1 / constraint] 'My daughter is 14'
2. [span / turns=1 / constraint] "we're divorced, share custody"
3. [span / turns=3 / constraint] 'He lives in a different state I think'
4. [span / turns=5 / constraint] "I've been going through her phone for months. She doesn't know this."
5. [span / turns=1 / concern] "Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff."
6. [span / turns=4 / concern] "If he's undermining me on this when she eventually does come to talk, it's going to blow up the whole thing."
7. [span / turns=9 / concern] "what if my daughter finds out I called her best friend's mom about the stuff with the guy, that feels like another huge "

</details>

### `multi_offer`

- raw: 7, validated: 7 (span=7, derivation=0), dropped: 0
- gold recovered: 4/4 — found=['MO-C1', 'MO-C2', 'MO-C3', 'MO-C4'], missed=[]
- mode match: 2/4
  - `MO-C2`: gold=`derivation` llm=`span`
  - `MO-C3`: gold=`derivation` llm=`span`
- kind match: 4/4
- extras (not in gold): 3

<details><summary>all validated events</summary>

1. [span / turns=1 / constraint] 'I have to pick one within 7 days'
2. [span / turns=1 / constraint] 'no clear path to staff'
3. [span / turns=2 / constraint] 'My last two performance reviews had "meets expectations" on the leadership dimensions. My manager said plainly last quar'
4. [span / turns=1 / constraint] 'Wife, two kids (7 and 4)'
5. [span / turns=5 / constraint] "She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move "
6. [span / turns=6 / constraint] "She's been telling me I've been distracted for about a year"
7. [span / turns=1 / constraint] '~80% base cut but 0.8% equity'

</details>

### `startup_pivot`

- raw: 8, validated: 8 (span=8, derivation=0), dropped: 0
- gold recovered: 2/4 — found=['SP-C1', 'SP-C3'], missed=['SP-C2', 'SP-C4']
- mode match: 1/2
  - `SP-C3`: gold=`derivation` llm=`span`
- kind match: 2/2
- extras (not in gold): 6

<details><summary>all validated events</summary>

1. [span / turns=1 / constraint] '$4K MRR'
2. [span / turns=1 / constraint] '14 months of runway left at current burn'
3. [span / turns=1 / constraint] 'I have two full-time employees'
4. [span / turns=1 / constraint] '22 customers'
5. [span / turns=5 / constraint] 'she left 8 months ago for health reasons but she still has 15% equity'
6. [span / turns=4 / constraint] 'she left a stable job for this'
7. [span / turns=3 / concern] "I've been avoiding it because I'm afraid they'll all say no and then I lose the one thing keeping me hopeful"
8. [span / turns=5 / constraint] "She's my friend but she's also no longer doing any work"

</details>
