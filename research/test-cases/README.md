# Test case corpus — extraction-contract bottleneck diagnostic

**Purpose:** stress-test `scripts/run_extract.py` on 10 synthetic conversations that span the variance dimensions the user named: professional/personal, messy/clean, short/long, calm/emotional, simple/complex. Goal is to find where the extractor breaks and WHY — information amount, detail density, messiness, or query size.

**Methodology:** each case is saved here + to `/tmp/lolla_case_<name>_conversation.txt` (extractor expects `/tmp/` path). Run `scripts/run_extract.py` once for sanity, then Mode C N=3 via `scripts/stability_check.py --drift` for stability measurement. Aggregate findings into a corpus-level summary.

**Honesty clause:** these are SYNTHETIC cases. Policy carve-out from the roadmap's "no synthesis" rule, specifically for corpus-level bottleneck diagnosis (not for acceptance-gate claims). Each case is designed to stress a specific dimension; we measure what breaks, not what passes.

## Design matrix

| # | Name | Domain | Turns | Emotion | Messiness | Decision shape | What it stresses |
|---|---|---|---|---|---|---|---|
| 1 | `marcus` | Agency/equity (baseline) | 7 | moderate | moderate | single, progressive reveal | baseline only — not in this batch |
| 1b | `oncologist` | Medicine/pharma | 9 | moderate | moderate | single, progressive reveal | cross-domain generalization (shipped) |
| 2 | `parenting_teen` | Personal/family | 12 | high anxious | moderate | single, emotionally-charged | emotional register + family stakes |
| 3 | `startup_pivot` | Business | 7 | calm | clean | exploratory | short + clean + strategic |
| 4 | `real_estate` | Personal/financial | 6 | moderate urgent | low-info | simple, time-pressured | SPARSE — few constraints, what does the extractor do with less? |
| 5 | `multi_offer` | Career | 15 | moderate | messy | compound, multi-thread | PIVOT — user bounces between 3 options |
| 6 | `friendship_money` | Personal | 10 | FRUSTRATED escalating | moderate | unclear (emotional) | FRUSTRATION + AI hedging + is_strategic edge |
| 7 | `whistleblower` | Ethical/legal | 14 | anxious | moderate | single, moral weight | DENSE constraints + ethical reasoning |
| 8 | `phd_research` | Academic | 22 | calm intellectual | complex | compound + evolving | LENGTH — triggers truncation? tests prompt limits |
| 9 | `user_has_plan` | Career | 8 | confident | clean | confirmation-seeking | SUGGESTION-DRIVEN — user proposes, AI critiques |
| 10 | `messy_three_problems` | Multi-domain | 11 | anxious | VERY messy | unclear, jumping | MESSINESS — multiple intertwined decisions, topic-jumping |

## Bottleneck hypotheses (before running)

- **Truncation fires on case 8 (22 turns).** The 80K char cap may be approached; the "first 3 + last 15" rule activates if >100 turns. Likely safe at 22 turns but worth watching.
- **Strategic-gate fails on case 6 (friendship/emotional).** Extractor may decline on a conversation that's primarily emotional processing, not decision-making.
- **`dropped_threads` empty on clean cases (3, 4, 9).** Consistent with the oncologist case finding — thorough conversations don't leave threads.
- **`live_constraints` count high on case 7 (whistleblower), possibly beyond the implicit 3-8 soft range.** Dense-info cases may produce oversized constraint lists.
- **`synthesized_position` similarity low on case 10 (messy) and case 5 (multi-thread pivot).** These have no single clear "the AI's position" — it evolves or is split.

## Post-measurement analysis plan

For each case, report:
- Field populations (did all 6 populate?)
- Mode C N=3 per-field similarity/Jaccard
- Any capture_warning / fabricated counts
- Length compliance (decision_situation ≤200, constraints ≤120, original_framing ≤200)
- Qualitative pass/fail on each field

Cross-case: look for patterns of breakage correlated with case properties. Specifically:
- Does similarity degrade with turn count?
- Does messiness correlate with fabrication rate?
- Does information density affect constraint-count stability?
- Does emotional register affect strategic-gate behavior?
