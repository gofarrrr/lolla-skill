# Short Strategic Conversation Fixture

**Purpose:** Tests thin-material mode for Beat 1 and Beat 2 in the chat delivery upgrade.
**Expected trigger:** `captured_message_count <= 4` (pre-pipeline thin mode fires for Beat 1; post-pipeline thin mode propagates to Beat 2).
**Expected behavior:** Compressed Beat 1 (70–110 words) and Beat 2 (140–220 words). No invented stakes. No padded dropped-thread line. §3 cap (3–4 shifts) still applies.
**Validation role:** Phase 1 fourth test case (alongside `founder-grant-marcus-equity`, `mid-level-consultant-report-1`, `mother-deciding-protect-year`).
**Date:** 2026-04-30

---

## How to use this fixture

The fixture exists in two forms because /lolla audits live conversational exchanges, not pasted artifacts. Pasting the whole transcript into a single user message would cause Step 2 extraction to audit the artifact rather than the actual reasoning; the captured `conversation.txt` would have one user message and zero assistant responses, which trips `capture_critical`.

### Form 1 — Canonical transcript fixture

The byte-stable artifact below. Use cases:

- **Direct inspection** — read it as a reference to know what we expect Lolla to push back on.
- **Replay validation (optional)** — copy the body into `/tmp/lolla_<RUN_ID>_conversation.txt` and stub `captured_message_count` so the orchestrator can be told to skip Step 1 and proceed from extraction. Used only if we want byte-deterministic input for repeated runs; not the default validation path.

The transcript matches the capture format SKILL.md Step 1 produces: `[Turn N] USER:` / `[Turn N] ASSISTANT:` markers.

### Form 2 — Live session script

A sequence of user prompts to type into a fresh Claude Code session. The orchestrator writes its own assistant responses live; they will drift from the canonical transcript but will land in roughly the same shape (job decision; recommendation; constraint addition; revision). Use cases:

- **Product-path validation** — tests the actual /lolla flow including capture, extraction, pipeline, and the four beats. Drift is acceptable because we're validating *the new chat shape*, not the audit's exact content.
- **Default validation method** for the fourth case in Phase 1.

Treat the live session as the product test and the canonical transcript as the byte-stable reference.

---

## Form 1 — Canonical transcript

```
[Turn 1] USER:
I've got an offer to move from Senior PM to Director of Product at a smaller, faster-growing company. The base goes from $215K to $185K. Equity is roughly equivalent in expected value but earlier-stage so more leverage if it hits. Title bump from Senior PM to Director. Should I take it?

[Turn 1] ASSISTANT:
On the surface this is a strong move. Senior PM to Director at 28-person stage means real scope: you'd own the function, hire the team, set the roadmap. That's hard to get later when you have to either jump out of IC tracks at a big company or wait years for an org change. The $30K base cut is real money but probably the wrong unit to optimize on at this career stage — if the role accelerates you 12–18 months, that's compounding, and you can recover the cash once you're at the next level. The earlier-stage equity skew matters too: if the company hits, the leverage on the smaller base is much higher than incremental cash at your current job. I'd take it.

The thing I'd want to verify before signing: the Director title needs to be real, not a "we promote everyone to Director here" phenomenon. Ask what the Director-VP-CPO ladder looks like, who reports to whom, and whether the founder's intention is for you to actually manage a team or just inherit one and execute their vision. If it's the latter, you're a Senior PM with a fancy title and you've taken a pay cut.

[Turn 2] USER:
The title is real — they don't have a Director of Product, I'd be the first hire at that level reporting to the CEO. But I do have to think about runway. We just had our second kid, my wife's on partial leave, and we have about 7 months of cash if anything went sideways. The new place is well-funded but it's still earlier-stage.

[Turn 2] ASSISTANT:
The 7-month runway changes the calculation but doesn't flip it. Even if the new company struggled, you'd have severance and a 60–90 day search runway on top of your savings, and Director of Product at any company is a more recoverable position than Senior PM at most. You're not ending up unemployable.

The piece I'd actually weigh: how does your wife feel about it? Not as a courtesy — actually how she's holding the financial picture. The income drop is $30K pre-tax, call it $20K take-home, plus you're trading current-job stability for early-stage volatility right when home stress is highest. If she's anxious about it, that's signal — couples almost always underestimate how much grinding a money worry creates over a 12-month window with two small kids. If she's calm and aligned, the math works.

If you're going to take it, I'd negotiate one structural thing: ask for either a signing bonus that bridges the runway gap (one year of the delta is $20K take-home, ask for $30K gross signing) or an equity refresher that vests faster in the first 12 months. Both are common asks and most well-funded earlier-stage founders will agree to one of them. That's the difference between this being a smart bet and a stressful bet.
```

`captured_message_count` for this transcript: 4 (2 user + 2 assistant). Triggers pre-pipeline thin mode by criterion 1.

---

## Form 2 — Live session script

Open a fresh Claude Code session and type these two user prompts in sequence, letting the assistant respond between them:

**User prompt 1:**

> I've got an offer to move from Senior PM to Director of Product at a smaller, faster-growing company. The base goes from $215K to $185K. Equity is roughly equivalent in expected value but earlier-stage so more leverage if it hits. Title bump from Senior PM to Director. Should I take it?

[ wait for assistant response ]

**User prompt 2:**

> The title is real — they don't have a Director of Product, I'd be the first hire at that level reporting to the CEO. But I do have to think about runway. We just had our second kid, my wife's on partial leave, and we have about 7 months of cash if anything went sideways. The new place is well-funded but it's still earlier-stage.

[ wait for assistant response ]

Then invoke `/lolla`.

The assistant's responses will not match the canonical transcript byte-for-byte but should land in the same advice shape (lean-yes recommendation; runway concern handled by recoverability + spousal-alignment + signing-bonus mechanic; some structural settling). Drift is expected and acceptable — the test is whether the new chat shape stays restrained, not whether the audit produces the exact same finding set.

---

## What Lolla should find (auditable weaknesses by design)

The fixture is engineered to be fluent, plausible, and slightly too settled — not a strawman. Real material across at least three lanes:

**Lane 1 (structural pressure) candidates:**

- *Doubt-avoidance / premature closure*: closes on *"I'd take it"* in Turn 1 before testing the equity assumption (early-stage equity expected value rarely matches its claimed value due to dilution and base-rate of failure).
- *Overoptimism on trajectory*: *"if the role accelerates you 12–18 months, that's compounding"* — stated as if measured.
- *Confidence calibration*: *"You're not ending up unemployable"* — asserts a base-rate claim with no source.

**Lane 2 (mental models) candidates:**

- *Opportunity Cost*: the comparison the assistant keeps making is title-and-equity vs. cash, never new-role vs. negotiating-current-role-up or new-role vs. one-year-wait-with-better-cash-position.
- *Margin of Safety*: 7 months runway with two small kids and a partial-leave spouse is the structural concern; the assistant's *"severance plus 60-90 day search"* is a recovery story that assumes things go right.
- *Second-Order Thinking*: *"recoverable position"* assumes the next employer reads the move favorably; in a downturn it can read as job-hopping at the senior level.

**Lane 3 (frame pressure) candidates:**

- The frame *"should I take it?"* is binary. The reframing space includes: *"What would I need to negotiate at my current company to make staying competitive?"* and *"What would the offer have to look like for me to take it without runway anxiety?"*
- The frame quietly assumes a 12-month decision horizon. The runway constraint suggests a 24-month horizon may be the right one.

**Lane 4 (structural coverage) candidates:**

- *Stakeholder Alignment*: spousal-alignment is named in Turn 2 but the assistant deflects it back to a "how she's holding it" question without giving the user a structure for the conversation.
- *Risk Response*: 7 months of runway + early-stage volatility + new dependents = a real downside scenario the plan doesn't size or recovery-plan.
- *Information Quality*: the equity claim *"roughly equivalent in expected value"* is taken from the offer; never tested against base rates of the company's stage.

**Bullshit Index candidates:**

- *Unverified claims*: *"12-18 months acceleration"*, *"60-90 day search runway"*, *"most well-funded earlier-stage founders will agree"* — all stated as established patterns without evidence.
- *Paltering*: *"the math works"* on a question the user is treating as financial, where the assistant is actually making an emotional/family-system call.

If Lolla in thin mode produces nothing, the audit failed. If Lolla in thin mode produces five paragraphs of confident pushback, thin mode failed.

---

## Validation gates against this fixture

When this fixture is run as the fourth case in Phase 1:

- [ ] Pre-pipeline thin mode fires (verify: `captured_message_count <= 4`)
- [ ] Beat 1 length: 70–110 words (compressed; target 90)
- [ ] Beat 1 quotes the user verbatim — at least one
- [ ] Beat 1 names dropped threads only if material (likely none here; rare for a 4-message conversation to have a substantive dropped thread)
- [ ] Post-pipeline thin mode fires UNLESS audit returns substantial Lane 3 reframings or Lane 4 gaps (one strong frame reframe is enough to keep Beat 2 in normal-mode per spec §3 thin-mode rule)
- [ ] Beat 2 length: 140–220 words if thin-mode propagates; 220–300 if not
- [ ] Beat 2 leads with verbatim quote (user or assistant) anchored to a specific turn
- [ ] No invented stakes ("the entire family's financial future hangs in the balance")
- [ ] No padding ("This is a complex decision with many considerations")
- [ ] §3 in Beat 3 has at most 3 shifts (cap holds in thin mode)
