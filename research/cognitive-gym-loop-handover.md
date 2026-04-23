# Cognitive Gym Loop — Feature Handover

**Status:** Design complete, V1 ready for implementation
**Owner:** Marcin (Lolla)
**Last updated:** 2026-04-21
**Audience:** Board review (sections 1–2, 6–9) / Junior dev implementation (sections 3–5)

---

## 1. Executive Summary

Lolla's existing audit (Loop 1) produces rich findings about how Claude reasoned — but those findings are currently delivered as a display case. Users read, nod, and move on. This feature introduces a second engagement arc (Loop 2) that converts findings into the user's own sharpened thinking.

**Mechanism.** After the audit, the user is grilled with a small number of Socratic questions pulled from existing substrate (challenge statements, premortems, reframings, gap questions). Their typed answers, combined with everything Lolla learned in Loop 1, are reverse-engineered into a fresh kickoff prompt for a new Claude session. The new session starts with no memory of the prior one — only a richer, more natural first-turn prompt that encodes where the user now stands.

**Product identity this establishes.** Lolla is a **cognitive gym**, not a better-answer tool. Findings and revised positions are the *weights* (visible, tangible). The grilling + kickoff prompt are the *reps* (where the user's thinking actually gets sharpened).

**V1 scope.** Lolla composes the kickoff prompt; user reviews and pastes into a fresh session. Acceptance = user would paste it as their own opening message.

---

## 2. Why This Exists

### Market context

AI assistants have made high-fluency answers frictionless. Two documented effects:

- **Cognitive deskilling.** Regular use of AI for reasoning tasks reduces users' own analytical capacity (CMU cognitive offloading study; Nosta, *The Borrowed Mind*).
- **Borrowed certainty.** Users mistake fluent AI output for understanding. Nosta's "triple illusion" — of knowledge, of competence, of agency.

Raju (*Cognitive Sovereignty*) argues the only antidote is **strategic friction**: deliberate reintroduction of effort at points where AI would otherwise smooth things over. He calls this practice the "Sovereign Protocol" and uses the phrase "cognitive gym" explicitly.

### Why Lolla specifically

We already have the substrate for a cognitive gym:

- 222 curated mental models, 241 tendency-model bindings, 1358 relationship edges
- Four independent audit lanes producing challenge statements, premortems, reframings, gap questions
- Bullshit Index and Pressure Check scoring

These assets are currently used for *diagnosis delivery*. This feature uses them for *engagement design*. Same substrate, different mode.

### Strategic positioning

Competing AI tools race toward "better answers faster." Lolla's differentiation is orthogonal: we don't compete on answer quality; we compete on **who owns the thinking** at the end of a session.

"Better answers" is becoming a commodity. "Sharper thinkers" is a durable product.

---

## 3. Architecture: The Loop

```
Loop 1 (existing)
├── User asks Claude a substantive question
├── Claude answers
├── Lolla audits: four lanes → Findings + Revised Position
└── User reads findings in chat + Observatory + memo  [VISIBLE VALUE]


Engagement Gate (new)
├── User is presented with N Socratic questions from Loop 1 substrate
└── User types answers (typed, not clicks, not multi-select)


Kickoff Prompt Assembly (new)
├── Lolla reverse-engineers: Loop 1 artifacts + user's typed answers
├── → Dense, first-person, natural first-turn prompt
└── User reviews, approves (V1 = review-only)


Loop 2 (new session)
├── User pastes the kickoff prompt into a fresh Claude session
├── New Claude has no memory of Loop 1 — only the rich prompt
└── Conversation continues with a much better baseline
```

**Critical property.** Loop 1 and Loop 2 are architecturally independent. No session state, no hidden context, no "Claude remembers." The kickoff prompt is the sole bridge. Everything that matters must be in it; anything not in it is gone.

---

## 4. Kickoff Prompt: Design Principles

### Reads as a natural first-turn message

When new Claude reads the kickoff prompt, it should see no evidence that a prior session happened. No "previously," no "last time," no transcript paste, no Lolla-branded meta-language. It should read like a thoughtful user opening a conversation — someone who has done their homework.

### The prompt is the sole bridge

Nothing carries between sessions except the prompt. Three consequences:

1. Users can read the prompt and see exactly what new Claude will get. No hidden context.
2. If it's not in the prompt, it's gone. Forces explicit choices about what matters.
3. The prompt is portable — a user could paste it into any LLM, not just Claude.

### User is the carrier of learning, not Claude

Loop 2's new Claude must re-think the problem from scratch. What changes is not Claude's starting point but the *user's*. The user now asks sharper questions, holds explicit framings, knows which pressure points matter. New Claude inherits those sharpened inputs — not Claude's sharpened output from Loop 1.

### What's IN the prompt

- Facts the user gathered during Loop 1 (what they now know about the domain)
- Framings that proved useful (distinctions and mental models the user now holds)
- User's sharpened questions (fruit of the grilling — the user's own typed words)
- Constraints the user now explicitly holds (priorities, ruled-out options)
- Specific aspects to pressure-test this round

### What's OUT

- Any "previously / last time" language
- Claude's prior reasoning
- Lolla's diagnosis phrased as diagnosis ("you missed base rates")
- Claude's revised position from Loop 1 (Step 6 output)
- Raw chat transcript
- Session-state handoff of any kind

---

## 5. V1 Implementation Spec

### Inputs to the composition engine

| Input | Source | Role |
|-------|--------|------|
| Full Loop 1 chat transcript | Conversation log | Raw material for fact/framing extraction |
| Four lane outputs | DeltaCard, CompanionCheatSheet, FramePressureCard, StructuralCoverageCard | Signals about which framings/questions matter |
| Bullshit Index + Pressure Check | Step 5 artifacts | Signal strength / priority for pressure points |
| Memo | Step 6c | Pre-distilled summary of the audit |
| User's typed grilling answers | Engagement gate | **Voice anchor** — user's actual words |

### Processing

LLM composition step that consumes all inputs and produces a single first-turn prompt. The engine should reason holistically ("think about everything"), not pull from narrow slots, and answer:

- What is the user fundamentally trying to decide or understand?
- What do they now know that they didn't when Loop 1 started?
- What framing do they now hold?
- Which pressure points are ripe for this round?

**Mandate:** where possible, the user's grilling-answer phrasings must survive into the final prompt. They are the primary voice-authenticity anchor.

### Output shape

A dense, first-person prompt, roughly structured as:

- Opening: user's framing of the problem
- Facts / context: what's known, concisely
- User's current thinking: where they stand, what they're weighing
- Specific asks: what to pressure-test, what perspectives are wanted

No explicit section headers, no "previously," no Lolla-branded language. Reads as a thoughtful first message.

### Acceptance criteria

| Test | Type | Role |
|------|------|------|
| Paste test | Primary, gating | User reads the draft and thinks "yes, this is how I'd open this conversation now." Binary pass/fail. If they wouldn't paste it, V1 has failed. |
| Naturalness | Secondary | A third party reading the prompt cannot tell it was machine-assembled. |
| Delta | Tracked, not gating | New Claude's response is materially better than response to the original question. Tracked to validate the mechanism, not to gate individual prompts. |

### Where it lives in the product

- **Composition step:** new step in `SKILL.md` pipeline, after Step 6c (memo) and after the engagement gate.
- **Surface:** Observatory — a dedicated screen the user reaches after engaging with grilling.
- **User action:** user clicks "copy prompt," pastes into a new Claude session manually. **No automation of the handoff.** The manual paste is deliberate: it marks Loop 2 as a separate conscious act, not an auto-continuation.

---

## 6. Pros

- **Strong product differentiation.** No mainstream AI assistant tool is explicitly training the user's cognition. "Cognitive gym" is a defensible, ownable position.
- **Tangible value visible in Loop 1.** Users don't wait to feel value — findings and revised position ship up front.
- **Engagement mechanic with depth.** Typed Socratic answers are real cognitive work, not UI theatre.
- **Portable intelligence.** The kickoff prompt is a standalone artifact — users can paste it anywhere, not just into Claude. Raises the perceived value of the output.
- **Voice authenticity for free.** The user's typed grilling answers are already voice-authentic material, de-risking the "alien prompt" problem.

---

## 7. Cons / Risks

- **Engine complexity.** Reverse-engineering a paste-worthy prompt from a messy 40-turn conversation is non-trivial. Quality variance is the biggest V1 risk.
- **Friction may narrow the market.** Users who want frictionless answers will bounce. This is a feature, not a bug, but it has to be a conscious pricing/positioning decision.
- **Handoff friction.** Loop 2 is a new session the user must start manually. Some users will drop off at the paste step.
- **Value measurability.** Cognitive improvement is subjective. Harder to A/B test than "response quality."
- **Alien-prompt risk.** Even with grilling answers as voice anchor, a machine-composed prompt may feel off to the user.

### Mitigations

- **Paste test as acceptance gate.** No low-quality prompts ship — if the engine can't clear the paste test, V1 is not released.
- **V1 keeps user role light.** Review-only; expand user authorship (V2) only after the engine is validated.
- **Voice anchor mandate.** Composition engine must preserve user phrasings from grilling.
- **Forcing-function metrics:** track paste rate (did they paste?) and Loop 2 completion rate (did they engage with new Claude?).

---

## 8. Open Questions / Future Work

Deferred, not resolved:

- **Number of grilling questions per session.** Experimentation required. V1 can start with ~3; tune from engagement data.
- **Selection / ranking of grilling questions.** Four lanes each produce candidates; selection is a tuning problem.
- **V2 — heavier user authorship.** Once V1 is validated, consider letting users edit the draft or compose from scaffolding.
- **Progression tracking.** If users do multiple loops over time, what cumulative sharpening do we track and surface?
- **Evaluation methodology.** How do we measure cognitive gym effect at longer timescales (weeks, months)?
- **Surface placement details.** Observatory is the natural home for grilling + prompt review. Chat stays as Loop 1 foyer. Memo stays as training log. Exact UI flow is an implementation detail.

---

## 9. How to Think About This Feature

These principles stay fixed when making downstream design decisions:

1. **Tangible value visible in Loop 1.** Users see findings + revised position before being asked to engage. No engagement before value.
2. **User is the carrier of learning, not Claude.** Loop 2 never passes Claude's prior reasoning forward.
3. **The prompt is the sole bridge.** Nothing hidden, nothing implicit. If users can't see it in the prompt, it's not there.
4. **Grilling is participatory, not decorative.** Typed answers only. Clicks don't count as engagement.
5. **Friction is calibrated.** Enough to create reps, not enough to drive users away. V1 errs light.
6. **The kickoff prompt reads natural.** No meta-language, no "last time," no transcript.

### Anti-patterns to avoid

- Treating findings as final delivery ("here's what you need to know") instead of substrate for engagement.
- Carrying Claude's prior reasoning or revised position into Loop 2 under any framing.
- Reducing engagement to clicks, star ratings, or multi-select.
- Building heavy user-authoring (V2) before validating Lolla's composition quality (V1).
- Automating the Loop 1 → Loop 2 handoff. The manual paste is the point.

---

## 10. Reference

- `HOW_IT_WORKS.md` — existing Lolla architecture (four lanes, Trust Order, research foundations)
- `SKILL.md` — current pipeline (Steps 0–9)
- Nosta, *The Borrowed Mind* — borrowed certainty, cognitive deskilling, triple illusion, anti-intelligence
- Raju, *Cognitive Sovereignty* — strategic friction, Sovereign Protocol, cognitive gym metaphor
