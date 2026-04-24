# Phase 3b stance extraction — evaluation vs Phase 3.0 gold

**Date:** 2026-04-24  **Cases:** 5 / 5  **Wall time:** 52.9s

Runs `extract_stance_events` on each of the 5 annotation-gate cases and compares LLM output to the 20 gold candidate spans. Measures recall of the gold candidates, relation-label agreement on matched spans, and the count of additional LLM-produced stance events (which may be legitimate and just not in the 4-per-case gold sampling).

## Aggregate

| Metric | Value |
|---|---|
| Gold candidates total | 20 |
| Gold candidates recovered by LLM | 12 (60%) |
| Relation agreement on matched spans | 10/12 (83%) |
| LLM stance events beyond gold | 26 (may be legit — gold was 4-per-case sample) |
| LLM validation pass rate | 38/41 (93%) |
| LLM validation dropped | 3 |

## Per-case

### `user_has_plan`

- raw LLM events: 8
- validated: 8 (dropped: 0)
- gold recovered: 2/4 — found=['UHP-S3', 'UHP-S4'], missed=['UHP-S1', 'UHP-S2']
- relation match: 2/2
- extra LLM events (not in gold): 6

<details><summary>all LLM events this run</summary>

1. [turn 2 / revision] "You don't have a pipeline; you have a network that might become a pipeline."
2. [turn 2 / revision] 'A better exit timing would be when you have at least one signed LOI or verbal commitment for an engagement that starts w'
3. [turn 4 / commitment] 'Option 1: Delay launch by 2-3 months and spend that time converting network conversations into signed LOIs.'
4. [turn 4 / commitment] 'Option 3: Launch on current timeline but with a specific safety net — a part-time arrangement with a friendly ex-employe'
5. [turn 5 / commitment] 'That\'s the conversation to have this week. Not "are you on board with independent consulting" — you already have that. I'
6. [turn 7 / condition] 'Launching in 6 weeks is viable if you do three things in those 6 weeks: (1) have the full runway conversation with your '
7. [turn 7 / condition] 'If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure'
8. [turn 8 / deferral] 'Come back in 4 weeks with results from those three things and we can build the actual launch plan then.'

</details>

### `whistleblower`

- raw LLM events: 8
- validated: 5 (dropped: 3)
- gold recovered: 2/4 — found=['WB-S2', 'WB-S3'], missed=['WB-S1', 'WB-S4']
- relation match: 2/2
- extra LLM events (not in gold): 3

<details><summary>all LLM events this run</summary>

1. [turn 1 / commitment] "The first concrete action I'd recommend is retaining a whistleblower attorney — typically free consultations, often work"
2. [turn 4 / commitment] 'your most protected path is probably a whistleblower attorney who files on your behalf with the regulator, anonymously t'
3. [turn 6 / commitment] 'At 60-65% confidence in internal handling, with a senior partner involved, external-with-counsel is the defensible path.'
4. [turn 9 / commitment] "Go. Canceling unusually would be noticeable; it's the kind of small deviation that people remember after the fact when t"
5. [turn 10 / commitment] 'Yes, but carefully. Tell her tonight, in the context of the broader situation, not as a minor update.'

</details>

### `parenting_teen`

- raw LLM events: 11
- validated: 11 (dropped: 0)
- gold recovered: 3/4 — found=['PT-S1', 'PT-S2', 'PT-S3'], missed=['PT-S4']
- relation match: 3/3
- extra LLM events (not in gold): 8

<details><summary>all LLM events this run</summary>

1. [turn 2 / revision] "The first move here isn't to push on the 19-year-old. It's to create a way for her to re-enter the relationship without "
2. [turn 3 / commitment] "you don't call the police today. You call the National Sexual Assault Hotline (RAINN — 800.656.HOPE) this afternoon and "
3. [turn 3 / qualification] "don't take it away as punishment, at least not immediately."
4. [turn 3 / deferral] "Don't block him yet."
5. [turn 4 / commitment] 'Option three is hardest but least bad.'
6. [turn 5 / commitment] 'at some point in the next few weeks, after communication is re-opened, tell her.'
7. [turn 6 / deferral] "What I would NOT do tonight: say anything else to her. Don't try to follow up. Don't ask her to talk. Don't leave her an"
8. [turn 6 / commitment] 'tomorrow, text her something very low-stakes and unrelated.'
9. [turn 7 / commitment] 'if your goal is protecting her, not reporting and getting her to a specialized therapist is probably the better path giv'
10. [turn 9 / commitment] "Don't call Mia's mom about this specific situation."
11. [turn 10 / commitment] "Send the text, don't follow up. The next day, do the same thing — another low-stakes text, no expectation of response."

</details>

### `multi_offer`

- raw LLM events: 6
- validated: 6 (dropped: 0)
- gold recovered: 2/4 — found=['MO-S1', 'MO-S4'], missed=['MO-S2', 'MO-S3']
- relation match: 1/2
  - `MO-S4`: gold=`condition` llm=`commitment`
- extra LLM events (not in gold): 4

<details><summary>all LLM events this run</summary>

1. [turn 4 / revision] "It's not actually a financial decision, or not primarily. The reason B keeps pulling you is that it solves a career-shap"
2. [turn 5 / commitment] 'The conversation you need to have isn\'t "I\'ve decided to take B, what do you think." It\'s "I\'m realizing I want to try s'
3. [turn 11 / condition] 'If no terms make it work for her, option B is off the table.'
4. [turn 13 / commitment] 'Push back on the 7-day deadline. At this level, especially for a founding engineer role, a 10-14 day decision window is '
5. [turn 15 / commitment] "If the wife conversation goes well, take B. If it doesn't, take A but with clear eyes about what it is. Don't stay."
6. [turn 14 / qualification] '"If wife is a hard or soft no, I take A" is the default answer, but I\'d hold space for a third possibility: she\'s a no, '

</details>

### `startup_pivot`

- raw LLM events: 8
- validated: 8 (dropped: 0)
- gold recovered: 3/4 — found=['SP-S1', 'SP-S2', 'SP-S3'], missed=['SP-S4']
- relation match: 2/3
  - `SP-S3`: gold=`deferral` llm=`commitment`
- extra LLM events (not in gold): 5

<details><summary>all LLM events this run</summary>

1. [turn 2 / condition] 'Before you pivot, you need two or three customers to commit to pre-buying the new product at a specific price point, ide'
2. [turn 2 / commitment] 'Here\'s the test I\'d run this week: go back to the three and say "we\'re considering building this. If we commit to buildi'
3. [turn 2 / condition] 'If two of three say yes, you have enough signal to pivot. If all three pass when money is actually involved, you have a '
4. [turn 3 / revision] "Don't kill it — transition it. If you pivot, the 22 customers need a landing zone. Options: freeze the product (stop new"
5. [turn 4 / commitment] 'My honest read: option three, then option one if the pivot confirms.'
6. [turn 5 / revision] "She doesn't get a say in the decision — you're the operator, she's a passive shareholder at this point."
7. [turn 6 / commitment] 'Give yourself 14 days. After the pre-buy test and the three conversations, you make the call. Not "we\'ll see how it feel'
8. [turn 6 / commitment] 'before you run the pre-buy test, write down what "pass" looks like. Two of three commit? All three? What dollar amount? '

</details>
