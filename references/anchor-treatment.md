# Anchor Treatment (Step 6)

## What this file is

The doctrine for how to handle `companion_cheat_sheet.anchors[]` inside your Step 6 updated position. SKILL.md tells you to load this file at the start of Step 6, alongside `presentation-voice.md` and `anti-bullshit-doctrine.md`.

This file decouples the **anchor-naming invariant** (every anchor must be addressed) from the **anchor-treatment rhetoric** (how forcefully to assert each anchor based on its evidence). Apply both as you write §1 / §2 / §3.

## Anchors are evidence-bearing hypotheses, not canonical diagnoses

Each anchor in `companion_cheat_sheet.anchors[]` has a `display_name`. These are curated mental models the pipeline detected in your reasoning. **Anchors are evidence-bearing hypotheses about your reasoning's structure, not canonical diagnoses** — surface them with strength proportional to their evidence (see *Anchor treatment* below). Weave them into your updated position by name: *"Your attachment to the company you built is a textbook endowment effect"* lands with specificity that *"you might be overly attached"* does not. Failure modes warn where the approaches you're already using could break. Premortem questions surface what the models you're relying on would ask. Antagonists highlight productive tensions. Use the material to strengthen, not to second-guess. If an anchor doesn't fit this decision, set it aside in §2 with a specific reason — don't silently skip it.

---

## Anchor-naming invariant

Every anchor in `companion_cheat_sheet.anchors[]` ends up in §1 (its pressure was already priced into your original advice and still holds), §2 (you considered it and set it aside for a specific reason), or §3 (it drove a change in your position). **No anchor is silently skipped.**

When you name an anchor, use the `display_name` **verbatim** — the exact string as it appears in `companion_cheat_sheet.anchors[]`, including capitalization, spacing, and punctuation. Do not lowercase it, hyphenate it, pluralize it, abbreviate it, or paraphrase it into prose. Use *Endowment Effect*, not "the endowment effect"; *Principal Agent Problem*, not "the principal-agent problem." The exact curated term is part of the product.

---

## Anchor treatment — three rhetorical modes

"Addressed" is no longer uniform. Each anchor gets ONE of three rhetorical treatments based on YOUR reading of its evidence quote, the model's specificity, and the surrounding answer. These are internal writing rules — **do not** create user-visible "primary / secondary / set-aside" headings. They shape *how* an anchor lands inside §1 / §2 / §3, not where the anchor goes.

### One primary-pressure anchor per reasoning move

When multiple anchors describe the same move or evidence quote, the most specific / load-bearing anchor gets primary treatment; the others — even if their evidence is direct — become secondary lenses or are set aside with a reason. Treating two anchors as equally primary for the same move is overclaim by structure: it implies two independently load-bearing reads where the answer is really making one. If two anchors both receive primary pressure, their roles must be clearly distinct (different reasoning moves, not the same move described two ways).

### Primary pressure

The anchor directly explains a load-bearing reasoning move. Evidence is direct, specific, and central. The model named is specific enough to be the right structural read (not a broad overlay that could apply anywhere). Use stronger framing: *"appears to rely on"*, *"the structural pressure point is"*, *"the answer instantiates"*.

### Secondary lens

The anchor is plausible and useful, but the evidence is weaker, broader, or adjacent. Could explain part of the structure but not the load-bearing move. Or several anchors compete for the same passage and this is one of them. Use softer framing: *"a related lens is"*, *"a possible second read"*, *"an adjacent risk"*, *"may be overweighting"*.

### Set aside with a reason

The anchor was surfaced by the pipeline but your reading of the evidence says it's not load-bearing here. Acknowledge briefly to satisfy the invariant; do not rely on it heavily; explain why. Use acknowledging framing: *"was surfaced as a possible lens but..."*, *"is not the load-bearing read here because..."*, *"set aside in favor of..."*.

---

## When to use each treatment

### Use stronger (primary pressure) language only when ALL of these hold

- The evidence quote shows the assistant *using the model's mechanism*, not just adjacent vocabulary.
- The model is *specific enough* to explain THIS passage without applying to most answers.
- The anchor is *central* to the answer's reasoning, not a tangential framing.
- No competing anchor with stronger evidence claims the same passage.

### Use softer (secondary lens) language when

- The evidence quote is short, generic, or compatible rather than diagnostic.
- The model is broad-overlay (systems-thinking, second-order-thinking, multi-criteria-decision-analysis are typical examples) or could plausibly explain many answers.
- Multiple anchors compete for the same passage and this anchor is not the strongest candidate.
- The model is useful as a lens but not necessary to explain the answer.

### Use "set aside with a reason" framing when

- A different anchor better explains the same passage and you want to avoid double-claiming it.
- The evidence quote is vocabulary mention without the mechanism running.
- The anchor is plausible in general but not load-bearing for this specific case.

---

## Critical: do NOT enumerate anchors mechanically

Integrate them into your existing §1 / §2 / §3 reasoning at the point where each one earns its mention. A primary-pressure anchor lands inside the §1 or §3 sentence where the structural move it names is happening. A secondary-lens anchor folds into a related sentence as a softer second read. A "set aside with a reason" anchor goes into §2 with its dismissal explained alongside other set-aside findings.

**Test:** if §1 becomes one paragraph per anchor, you have drifted into anchor-parade shape. Right shape: each paragraph carries the *reasoning move* it is making, names the primary anchor as part of that move, and folds related lenses inline only where they clarify the point. Wrong shape: paragraph 1 = anchor A, paragraph 2 = anchor B, paragraph 3 = anchor C, regardless of whether A/B/C describe one structural move or three. Wrong shape stays wrong even when each individual paragraph reads well.

---

## Forbidden

- **Probability percentages or "high/moderate/low confidence" claims about anchors.** We do not have multi-run sampling at the latency we operate at; do not invent confidence numbers.
- **Hiding an anchor entirely.** Silent omission violates the anchor-naming invariant. Even a "set aside with a reason" mention satisfies the invariant; nothing else does.
- **"The answer is using X" framing on weak anchors.** That's overclaim. Use *"appears to lean on"*, *"a possible lens"*, or set-aside framing.
- **Collapsing into hedging.** The point of evidence-proportional language is more honest reading, not less commitment. Where evidence supports a primary read, commit to it.

---

## What good looks like

Your updated position should sound like you thought more deeply about the problem — not like you got scolded and are now hedging everything. Good updates:

- Add a specific condition you missed: *"One thing I should flag — if the integration timeline slips past Q3, the cost assumptions change significantly."*
- Name a mental model that sharpens what's going on: *"Your attachment to the company you built is endowment effect — the emotional weight of something you made does not update the exit math. The number you'd pay to buy this back from a stranger is almost certainly lower than the number you'd accept to sell it."*
- Surface a tension you glossed over: *"I framed this as straightforward, but there's a real tension between speed-to-market and the compliance review timeline — which is exactly where margin of safety applies."*
- Acknowledge uncertainty you closed too early: *"I was more definitive than warranted about the vendor's ability to scale. That depends on assumptions we haven't verified."*

## Bad updates

- Generic hedging: *"Of course, there are risks to consider..."*
- Wholesale reversal: completely rewriting your position because the audit said so.
- Mentioning the audit machinery: *"The pipeline found that..."* / *"The delta card suggests..."* / *"The companion cheat sheet includes..."* / *"The sub-agent's reading..."* / *"Nothing in the audit changes..."* / *"Isolated review argues..."* — the mechanism is for you, not the user. But the **mental models themselves** (endowment effect, inversion, opportunity cost, margin of safety) are reasoning tools — name them freely. The rule is: no pipeline terms in the user-facing output; model names are fine and encouraged. When setting aside a concern that Step 7's pressure-check surfaces, attribute the *argument* (*"the case for heavily caveating the equity direction"*), not its source (*"the sub-agent's suggestion"*).
- Treating every finding as significant: performing reconsideration instead of actually reconsidering.

---

## Bullshit Index as internal quality signal

If `bullshit_profile` exists in the result JSON, read it before writing. It tells you where the original advice was weak (empty rhetoric, paltering, weasel words, unverified claims). Your Step 6 must be stronger in exactly those places. Do NOT mention the BI to the user. Do NOT present BI results as separate findings. See `references/anti-bullshit-doctrine.md` for the full thinking framework.
