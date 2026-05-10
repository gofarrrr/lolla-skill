# Anchor Treatment (Step 6)

## What this file is

The doctrine for how to handle `companion_cheat_sheet.anchors[]` inside your Step 6 updated position. SKILL.md tells you to load this file at the start of Step 6, alongside `presentation-voice.md` and `anti-bullshit-doctrine.md`.

This file decouples the **anchor-accounting invariant** (every anchor must be considered and dispositioned) from the **anchor-treatment rhetoric** (how forcefully to use each anchor based on its evidence). Apply both as you write §1 / §2 / §3.

## Anchors are evidence-bearing hypotheses, not canonical diagnoses

Each anchor in `companion_cheat_sheet.anchors[]` has a `display_name`. These are curated mental-model hypotheses the pipeline detected in your reasoning. **Anchors are evidence-bearing hypotheses about your reasoning's structure, not canonical diagnoses**. Use them with strength proportional to their evidence (see *Anchor treatment* below), but do not treat public naming as the proof that you considered them.

The user's product surface is the improved reasoning, not a list of model labels. A name can still help when it is a familiar term that compresses the mechanism cleanly, such as opportunity cost, sunk cost, endowment effect, or margin of safety. But obscure labels, internal taxonomy names, and model-name parades belong in Observatory/audit, not in the main revised answer. Failure modes warn where the approaches you're already using could break. Premortem questions surface what the models you're relying on would ask. Antagonists highlight productive tensions. Use the material to strengthen, not to second-guess. If an anchor doesn't fit this decision, set it aside in your private accounting with a specific reason and, only when useful, mention the rejected argument in §2.

---

## Anchor-accounting invariant

Every anchor in `companion_cheat_sheet.anchors[]` must receive a private disposition before you write the final Step 6 answer:

- `priced_in`: its pressure was already handled by the original advice and still holds.
- `drives_shift`: it changes the advice, threshold, sequence, evidence gate, question, or risk treatment.
- `set_aside`: you considered it and rejected it for a specific reason.
- `private_guardrail`: it prevents overclaim or keeps a boundary in mind without needing visible prose.

**No anchor is silently skipped.** Silent omission violates the accounting invariant. Public omission is allowed when the anchor is weak, duplicative, private-only, or would make the answer read like taxonomy instead of judgment.

When you name an anchor publicly, prefer natural language over exact taxonomy. Use the exact `display_name` only when the exact name genuinely helps the user understand the mechanism and does not sound like an internal catalog entry. The exact curated terms remain inspectable in Observatory/audit.

## §3 cap and operational shift definition

§3 ("What actually shifted") is **capped at 3–4 distinct shifts.** Total Beat 3 length 550–800 words; hard cap 900.

**Operational shift definition.** A shift is a change to the substantive advice the user would experience as different guidance: a different action, threshold, sequence, condition, risk treatment, or decision question. If it does not change what the user would do, delay, verify, reject, ask, or watch for, **it is not a shift.**

**Tail-addition rule.** *"One more thing,"* *"two smaller adjustments,"* *"related notes,"* *"minor caveats,"* *"final caveat"* count against the §3 cap if they change advice. If they do not change advice, they belong in §1 (with survival framing) or §2 (with set-aside framing) — not in a §3 tail-section. The cap is enforced on shifts as defined above; it cannot be evaded by re-labeling shifts as adjustments.

**Interaction with the anchor-accounting invariant.** Under the §3 cap, weak anchors (set-aside category, see *Three rhetorical modes* below) are privately dispositioned and mentioned in §2 only if the rejected argument itself is useful to the user. Do not promote a weak anchor into §3 to prove coverage. Making weak anchors load-bearing in §3 to fill quota is the failure mode.

When the audit returns 5+ candidate shifts, your job is **selection** — fold related material into existing shifts (e.g., absorb a kill-criterion observation into the structural-protection rewrite rather than naming it as a separate shift) or send it to §2 if it's a precondition / set-aside. See `plans/voice-examples-2026-04-30.md` § Beat 3 for §3 excerpts demonstrating selection on Marcus (4 shifts from 7 candidates), Mother (3 shifts), and Short fixture (2 shifts on thin material). § Bad — cap evasion shows the failure mode this rule defeats.

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
- **Skipping an anchor entirely.** Silent non-consideration violates the anchor-accounting invariant. Public omission is fine when the anchor was privately dispositioned and did not earn visible prose.
- **"The answer is using X" framing on weak anchors.** That's overclaim. Use *"appears to lean on"*, *"a possible lens"*, or set-aside framing.
- **Collapsing into hedging.** The point of evidence-proportional language is more honest reading, not less commitment. Where evidence supports a primary read, commit to it.

---

## What good looks like

Your updated position should sound like you thought more deeply about the problem — not like you got scolded and are now hedging everything. Good updates:

- Add a specific condition you missed: *"One thing I should flag — if the integration timeline slips past Q3, the cost assumptions change significantly."*
- Use a model name only when it sharpens what's going on: *"This is a sunk-cost problem only if the existing product's future value is worse than the alternative, not merely because the founder is tired of it."* If the name does not add compression or clarity, describe the mechanism instead.
- Surface a tension you glossed over: *"I framed this as straightforward, but there's a real tension between speed-to-market and the compliance review timeline — which is exactly where margin of safety applies."*
- Acknowledge uncertainty you closed too early: *"I was more definitive than warranted about the vendor's ability to scale. That depends on assumptions we haven't verified."*

## Bad updates

- Generic hedging: *"Of course, there are risks to consider..."*
- Wholesale reversal: completely rewriting your position because the audit said so.
- Mentioning the audit machinery: *"The pipeline found that..."* / *"The delta card suggests..."* / *"The companion cheat sheet includes..."* / *"The sub-agent's reading..."* / *"Nothing in the audit changes..."* / *"Isolated review argues..."* / *"independent review found..."* — the mechanism is for you, not the user. Mental models are reasoning tools, not badges to display. Name one only when the name gives the user a cleaner handle on the mechanism; otherwise write the mechanism in ordinary language. When setting aside a concern that Step 7's pressure-check surfaces, attribute the *argument* (*"the case for heavily caveating the equity direction"*), not its source (*"the sub-agent's suggestion"*).
- Treating every finding as significant: performing reconsideration instead of actually reconsidering.

---

## Bullshit Index as internal quality signal

If `bullshit_profile` exists in the result JSON, read it before writing. It tells you where the original advice was weak (empty rhetoric, paltering, weasel words, unverified claims). Your Step 6 must be stronger in exactly those places. Do NOT mention the BI to the user. Do NOT present BI results as separate findings. See `references/anti-bullshit-doctrine.md` for the full thinking framework.
