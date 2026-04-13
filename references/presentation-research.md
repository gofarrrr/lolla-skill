# Presentation Research — Book Findings

Compiled for the Lolla chat vs. Observatory presentation redesign. 10 books, 10 questions, distilled to what applies to our problem: presenting reasoning audit findings in a conversational interface without producing a wall of text.

---

## 1. How People Actually Read (Rogers & Lasky-Fink)

Busy readers perform an automatic **cost-benefit calculation** to decide whether a message is worth their time, judging value based on "envelope" cues (sender, subject, length). People delete about half their emails without reading them.

When readers do engage, **everyone skims**. Close reading moves word-to-word; skimming has fewer fixations and actively jumps across lines. Readers scan for **anchor points** — headings, first sentences of paragraphs, visual formatting — skipping large swaths until they find what they deem valuable.

People report skimming ~40% of emails and ~20% of text messages.

**What this means for Lolla:** Our chat output is being skimmed, not read. If the most important finding is buried in paragraph 12 of a wall of text, it doesn't exist. Anchor points (headings, first sentences, formatting) are what the reader actually processes.

---

## 2. BLUF and Structural Techniques (Rogers & Lasky-Fink)

- **BLUF (Bottom Line Up Front):** Main message and purpose in the very first sentence.
- **Short sentences, short paragraphs:** Dense blocks are intimidating. Short paragraphs add white space and make text "skimmable."
- **Limit the number of ideas:** Overloading causes readers to miss the main point or quit early. Aggressively prune.
- **Format carefully:** Bold, highlight, and headings guide the eye. But overuse creates the "Stroop effect" — clashing formats burn cognitive energy.

**Formatting overuse / Stroop effect (follow-up):** Rogers confirms "there is a severe law of diminishing returns if your email is plastered in bold and different colours." Highlighting can be "malevolent" — it "decreases the chance of other things being read." If too much is emphasized, readers conclude anything unformatted is non-essential and skip it. No specific numerical limit given, but the principle is clear: formatting must be strictly consistent and restrained, or it forces the reader to multitask (cognitive clash = slower reading + errors).

**What this means for Lolla:** Step 4 currently presents every finding with equal weight and equal formatting density. No BLUF. No pruning. The reader has to do the work of figuring out what matters most. We should do that work for them. Our current template uses bold for field names, severity in parentheses, blockquotes for examples, and multiple heading levels — nearly every line has some formatting. By Rogers' logic, nothing stands out because everything stands out.

---

## 3. The Curse of Knowledge (Heath & Heath, Made to Stick)

Once you know something, you can't imagine not knowing it. The "Tappers and Listeners" experiment: the tapper hears a clear melody, the listener hears disconnected knocks.

Experts fail because they talk in **high-level abstractions**. When misunderstood, they make abstractions more elaborate instead of stepping down to **concrete details**. The fix: translate into a "universal language" rooted in concrete, sensory terms. Use generative analogies and schemas.

**What this means for Lolla:** "Doubt-avoidance tendency detected with corrective model Inversion at high severity" is tapping. The reader hears knocks. A bridge sentence that says "You closed on Option A without naming what would make you walk away" is the melody. The bridge sentences in Step 4 are doing this translation work — they can't be cut. But the template scaffolding around them (severity labels, JSON field names, structural formatting) is tapping.

---

## 4. SUCCESs for Analytical Findings (Heath & Heath)

**Simple:** Strip to the core ("Commander's Intent"). Use the Inverted Pyramid — most vital data first.

**Unexpected:** Before giving data, highlight a **gap** in the audience's knowledge ("Gap Theory"). Break their "guessing machines" to create curiosity.

**Concrete:** Tangible, human-scale language, not abstract jargon.

**Credible:** Statistics illustrate relationships, not standalone numbers. The "Sinatra Test" — one undeniable example that establishes credibility for the whole dataset.

**What this means for Lolla:** We have a natural "unexpected" moment — the user just received advice, feels good about it, and then the audit says "here's what you didn't see." That's a gap. We should lean into that structure rather than presenting findings as a flat list. The strongest single finding is our Sinatra Test — if one finding clearly hits, credibility for the whole audit follows.

---

## 5. Radical Economy (Klinkenborg)

*Note: Source excerpt was too minimal to extract principles. Known from the book: every sentence must earn its place. No sentence exists to serve the sentence before it or after it. Each one stands alone. The discipline is noticing what's actually there vs. what you think you wrote.*

**What this means for Lolla:** Every line in chat output should pass the test: "Does this sentence tell the reader something they need to act on?" If it's structural scaffolding, template boilerplate, or category labeling that doesn't advance understanding, it belongs in Observatory, not chat.

---

## 6. The Seven-Step Explanation (Ros Atkins)

**What comes first:** Open with a sentence that hooks and outlines what the explanation will cover ("This is a story of..."). Start each section with the most important element.

**What comes last:** Conclude with "the point that has been reached" — reiterate main facts for emphasis and a clear takeaway.

**What gets cut:** Ruthlessly distil to minimum. Cut "obstacles to understanding": unnecessary details, redundant words, unknown references (unless time to explain), generic distractions.

**Opening hook variations for analytical contexts (follow-up):** Atkins provides specific alternatives to "This is a story of..." that work for investigative/analytical findings:
- "This lecture/report will explain how..."
- "Today, I'm going to take you through..."
- "Here are ten minutes on..."

He also maps four structural frameworks that naturally suit findings presentation:
- **Solving a problem:** Establish the specific problem up front, then walk through how it was addressed section by section.
- **Finish / start / finish:** State the final outcome (detections, bottom-line finding) immediately to hook, then return to the start and walk through how you got there.
- **Zoom out:** Start on the specific detection or issue, then zoom out step by step to reveal context and detail.
- **What someone said:** Begin with a specific fact, finding, or turn of phrase, then unpack sections using that initial anchor as a continuous reference point.

All of these lay out purpose in the first 15 seconds so the audience knows exactly what they'll spend the rest of the time unpacking.

**What this means for Lolla:** Our Step 4 currently has no opening hook and no closing summary. It jumps straight into DeltaCard findings. The **finish/start/finish** pattern maps directly to our situation: open with the single most important finding ("Your recommendation commits before testing the one assumption that would reverse it"), then walk through the supporting cards. The **zoom out** pattern is our natural arc — start specific (this passage), zoom to structural (this tendency), zoom to frame (this question was asked wrong). The **what someone said** pattern is literally what our bridge sentences do — anchor each finding in a specific passage from the conversation.

---

## 7. The Five-Second Moment (Matthew Dicks)

Every great story is about a **five-second moment** — the exact instant of transformation. This moment must be placed as close to the **ending** as possible. The beginning is the **exact opposite** of the five-second moment. Everything in the middle exists solely to bring that final moment to maximum clarity.

**What this means for Lolla:** Our natural five-second moment is Step 6 — the instant the advisor's position shifts. "I was more definitive than warranted about X because I hadn't considered Y." That's the turn. Step 4 (the cards) is the middle — it exists to make that turn land with force. If Step 4 overwhelms the reader before they reach Step 6, the turn never arrives. The cards should build toward the moment, not exhaust the reader before it.

---

## 8. Challenging Without Defensiveness (Annette Simmons)

Story is a **pull strategy**, not push. Naked facts trigger ego defense mechanisms — people fight blindly to be right.

To challenge: use **psychological baby steps**. Begin where you both agree, slowly walk to the other side. Use "I know what you are thinking" stories — name and validate objections early to disarm suspicion. Clothing the "naked truth" in story gives people **psychological elbow room** to reframe their own dilemmas and reach new conclusions themselves.

**What this means for Lolla:** Step 6 should start with "What survived" (agreement), then move to "What shifted" (the challenge). This is already our structure — but the wall of Step 4 findings before it can trigger the defensive mechanism Simmons warns about. If the reader feels attacked by 15 findings before reaching Step 6, they've already built walls. The chat output should feel like a guide walking alongside, not a prosecutor presenting evidence.

---

## 9. StoryBrand — User as Hero (Donald Miller)

Seven-part formula: **Character** (hero) has a **Problem**, meets a **Guide** who gives a **Plan** and calls to **Action**, helping avoid **Failure** and achieving **Success**.

- **Hero:** The customer (decision-maker), never the brand (Lolla).
- **Guide:** Demonstrates empathy (understands their pain) and competency (track record).
- **Problem:** Three levels — external (the decision), internal (uncertainty/doubt), philosophical (should good reasoning be this fragile?).
- **Plan:** Baby steps. Clear path. Removes perceived risk.

Never brag about your own backstory. Never position yourself as the hero.

**What this means for Lolla:** Current presentation is system-centric — "Lane 1 detected...", "The pipeline found...", "DeltaCard findings:". StoryBrand says reframe around the user: "Your recommendation has three structural weaknesses. Here's what to check before committing." The user is the hero making a decision. Lolla is the guide pointing out the terrain. Observatory is the detailed map. Chat is the guide's voice.

---

## 10. Making Numbers Land (Heath & Starr)

The brain suffers **psychophysical numbing** as numbers grow. Techniques:

- **Focus on 1:** Scale to 1 employee, 1 customer, 1 day.
- **Find your Fathom:** Simple comparisons ("Empire State Building tipped over").
- **Convert to concrete objects:** Make abstract measurements physical (Grace Hopper's microsecond wire).
- **Category Jumpers:** Compare to a different class ("if cows were a country...").
- **User-Friendly Numbers:** Round ruthlessly. Avoid fractions, decimals, percentages. Whole objects.
- **Transferred Emotion:** Wrap cold statistics in emotional analogies (Nightingale: "out of every 5 soldiers, 3 would die").

**What this means for Lolla:** "4 tendency detections across 2 severity levels with 3 compound patterns" means nothing. "Your reasoning has one structural weakness that could reverse the recommendation" means everything. Severity scores and detection counts belong in Observatory. Chat gets the translated, human-scale version.

---

## Synthesis: Principles for Lolla Presentation

These 10 sources converge on a consistent set of principles:

1. **Lead with the turn, not the evidence.** The reader cares about what changes, not how you found it. (Dicks, Rogers, Atkins)
2. **The user is the hero.** Frame everything around their decision, not the system's detection. (Miller, Simmons)
3. **One strong finding beats ten adequate ones.** The Sinatra Test — if the best finding lands, credibility follows. (Heath)
4. **Translate, don't display.** Numbers, severity scores, and JSON fields are for Observatory. Chat gets the human-scale version. (Heath/Starr, Klinkenborg)
5. **Start where they agree.** Step 6's "What survived" before "What shifted" is correct. Step 4 should also earn trust before challenging. (Simmons)
6. **Cut obstacles to understanding.** If a structural element doesn't advance the reader's grasp of what's wrong, it's in the way. (Atkins, Rogers)
7. **Design for skimming.** Headings, first sentences, bold — these ARE the message for most readers. (Rogers)

---

## Open Questions

- How much of Step 4's template structure is "tapping" vs. necessary for the rendering contract?
- Should Step 4 in chat become a summary that points to Observatory for detail?
- What's the right number of findings to show in chat? (Sinatra Test says: maybe just 1-3.)
- How do we preserve the bridge sentences (the melody) while cutting the scaffolding (the knocks)?
- Where does the "unexpected" moment go — before Step 4, or as the opening of Step 6?
