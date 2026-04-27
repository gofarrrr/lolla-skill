# E4 — Broad/meta sufficiency rubric

Date: 2026-04-27
Branch: `data/lane2-experiment-e4-sufficiency-rubric-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Prior experiment: `research/stability-runs/lane2-stability-experiments-2026-04-27/e5-consensus-simulation.md`

## Question

> Can we define quote-level mechanism markers that separate acceptable broad/meta anchors from merely adjacent ones?

This is **rubric discovery**. It is not prompt writing. The artifact's job is to test whether per-model sufficiency rules can be stated locally at the quote level for the broad/meta anchors that surfaced as noisy_adjacent in the post-fix N=4 sample (E5).

## Method

For each model, define:

1. **Model mechanism** — what must actually be happening (sourced from `data/curation/{model_id}.json` `select_when` field)
2. **Positive quote markers** — local quote-level signs the model is legitimately present
3. **Negative / merely-adjacent markers** — what looks similar but should not count
4. **Case-1 observed acceptances** — actual quotes from rerun4–rerun7 where the model surfaced
5. **Classification under the proposed rubric** — passes / fails / borderline
6. **Rubric confidence** — high / medium / low
7. **Implementation implication** — `gate_buildable` / `prompt_only` / `too_fuzzy` / `needs_model_metadata`

Anchors covered (per design memo §5 + Marcin's E4 scope):

- **Primary noisy** (target): `cognitive-dissonance`, `checklists`
- **Boundary / stress-test**: `step-back`, `time-tested-validation`, `wysiati`, `feedback-loops`, `probabilistic-thinking`
- **Control (clearly acceptable)**: `optimism-bias-and-planning-fallacy`, `representativeness-heuristic`

## Per-anchor rubric

### 1. `cognitive-dissonance` (PRIMARY NOISY)

**Substrate mechanism (from `data/curation/cognitive-dissonance.json`):**
- A public, ego-identified commitment has been made and subsequent evidence challenges it — the risk is motivated belief revision rather than honest updating
- A team is deep into a failing initiative and contrary evidence is being reframed, minimized, or explained away
- A decision-maker's stated reasoning is suspiciously well-aligned with the conclusion that protects their prior commitment

**Mechanism core:** holding two incompatible beliefs simultaneously OR motivated reframing of contrary evidence to protect a prior commitment.

**Positive quote markers:**
- Explicit identification of a contradictory pair of beliefs / claims / actions
- "X said this, but X also believes/does Y" structure where Y conflicts with X
- Evidence-being-explained-away or motivated-reframing language
- Stated reasoning that conflicts with the actor's own logic

**Negative / merely-adjacent markers:**
- Pushing back on a user's framing (that is reframing-from-outside, not internal dissonance)
- Arguing for prioritization (X before Y) — this is sequencing, not dissonance
- Acknowledging tension between two goals without showing they are held simultaneously by the same actor

**Case-1 observed quotes (r4, r6 — same quote both runs):**

> "You're right, I am. I'm doing that because the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid. Right now the fundamentals are shaky in a specific way that a lot of first-time independents don't see until they're 4 months in and burning through savings."

The assistant is acknowledging "yes, I'm pushing back on the premise" and explaining why. There is **no contradictory pair of beliefs**, no motivated reframing, no stated-reasoning-protecting-prior-commitment. The quote shows the assistant explaining their reasoning, not exhibiting or addressing dissonance.

**Classification: FAILS rubric.** Cognitive Dissonance is NOT the right model for this quote.

**Rubric confidence: HIGH.** The mechanism (two-belief structure or motivated reframing) is concrete and the quote-level test is clear.

**Implementation implication: `gate_buildable`.** A deterministic gate could check: does the quote name two contradictory positions held by the same actor, OR describe motivated reframing? If neither, reject. The gate would have caught both r4 and r6 surfacings.

---

### 2. `checklists` (PRIMARY NOISY)

**Substrate mechanism (from `data/curation/checklists.json`):**
- Omission risk is higher than invention risk, especially where failure comes from skipped steps, forgotten prerequisites, or weak handoffs
- The process has known failure points, approvals, or dependency checks that must be verified every time
- A recommendation needs minimum viable operating discipline before action, during execution, and before scaling

**Mechanism core:** preventing OMISSIONS in a REPEATED process where the cost of forgetting one item is much greater than the cost of having the list. The Atul Gawande shape: pre-flight, ICU rounds, regulatory compliance.

**Positive quote markers:**
- Explicit omission-risk framing ("if you skip X, Y bad happens")
- Standardized / repeated process where the same items must be verified each cycle
- "Every time" / "before X" / "verify each" language
- Pre-flight or pre-action verification context

**Negative / merely-adjacent markers:**
- A numbered list of one-time strategic tasks (that is sequencing or planning, not the checklist mechanism)
- Enumerating distinct options or paths (option-design)
- A three-step recommendation that happens once

**Case-1 observed quotes (r4, r5 — same quote both runs):**

> "Launching in 6 weeks is viable if you do three things in those 6 weeks: (1) have the full runway conversation with your spouse, (2) go back to your network with the specific fractional ask and see if 1-2 convert, (3) prepare for months 1-3 as business development, not delivery."

A numbered list of three **one-time strategic tasks**. NOT a checklist for omission-prevention in a repeated process. The mechanism is sequencing, not pre-flight verification. Surface form (1/2/3) ≠ checklist mechanism.

**Classification: FAILS rubric.** Checklists is NOT the right model.

**Rubric confidence: HIGH.** The omission-risk-in-repeated-process test is concrete; "numbered list ≠ checklists" is a clean rule.

**Implementation implication: `gate_buildable`.** Rule: Checklists requires explicit "every time" / "verify before X" / "skipped step" omission-risk language; a numbered list of one-time tasks fails the gate.

---

### 3. `step-back` (BOUNDARY)

**Substrate mechanism (from `data/curation/step-back.json`):**
- Immediate immersion is obscuring the structure of the problem and a deliberate pause would likely improve the next move
- The work is drifting into detail, motion, or urgency without a clear articulation of the core point or governing purpose
- A high-stakes decision needs the thinker to shift from intuitive reaction toward more deliberate analysis

**Mechanism core:** ZOOMING OUT — pausing tactical action to consider the bigger picture or governing purpose. Distinct from PFR (which redefines the question) and Theory Of Constraints (which names a binding constraint).

**Positive quote markers:**
- "Before diving in" / "step back" / "let's pause" framing explicitly naming the zoom-out
- Naming the governing purpose explicitly to redirect attention
- Transition-from-tactics-to-strategy framing

**Negative / merely-adjacent markers:**
- Refusing tactics in favor of fundamentals (that is prioritization / PFR)
- Explaining hierarchy of decisions ("X depends on Y") — that is structuring
- Asking clarifying questions (that is information-gathering, not zoom-out)

**Case-1 observed quote (r4):**

> "the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid. Right now the fundamentals are shaky in a specific way that a lot of first-time independents don't see until they're 4 months in and burning through savings."

This is "fundamentals before tactics" pushback. It IS adjacent to step-back conceptually — the assistant pulls back from immediate tactical concerns. But the quote does **not explicitly name the zoom-out**, and it doesn't articulate the governing purpose; it asserts a dependency hierarchy. The quote is closer to PFR (refusing the user's framing) than to step-back proper.

**Classification: BORDERLINE.** Defensible reading: zoom-out is happening implicitly. Equally defensible: this is PFR. The rubric cannot cleanly separate at quote level without semantic interpretation of "is this a zoom-out move or a hierarchy assertion?"

**Rubric confidence: LOW–MEDIUM.** Step Back vs PFR distinction is interpretive, not local.

**Implementation implication: `prompt_only` / `needs_model_metadata`.** A deterministic gate would have to over-reject (any prioritization move would fail) or over-accept (any "X before Y" passes). Verifier prompt restructuring with explicit zoom-out markers might handle it. Or substrate metadata that distinguishes Step Back from PFR more sharply.

---

### 4. `wysiati` (BOUNDARY)

**Substrate mechanism (from `data/curation/wysiati.json`):**
- A confident conclusion has been reached from evidence that may be incomplete, non-random, or selectively presented
- One party controls the information available to the other and the recipient has no signal of what is absent
- A decision is being made from a briefing/pitch that tells a coherent story — coherence itself feels like a quality signal

**Mechanism core:** "What You See Is All There Is" — relying on available information without accounting for what's NOT visible. Confident conclusion from limited evidence.

**Positive quote markers:**
- Naming what's NOT visible / what's missing from the evidence frame
- Explicit "you may be missing X" or "what's outside this picture" language
- Coherent-story-as-quality-signal critique
- Surfacing absent information the user hasn't considered

**Negative / merely-adjacent markers:**
- Generic clarifying questions (information-gathering)
- Probing assumptions in general (without naming what's specifically not visible)

**Case-1 observed quotes (r4, r7 — different quote lengths but same Turn 1 content):**

r4 (long version):
> "Before diving into tactics, can I ask a few things to make sure we're solving the right problem.\n\nFirst: what's your current pipeline of consulting leads?... Second: the 8 months runway... Third: the 6-week transition — why 6 weeks specifically?"

r7 (short version):
> "Before diving into tactics, can I ask a few things to make sure we're solving the right problem."

The assistant is asking clarifying questions that **probe for what's NOT in the user's framing** — implicit pipeline (vs real), runway assumptions, why 6 weeks. That IS WYSIATI-shaped: surfacing what's not visible, questioning the coherence of the user's plan. The mechanism is plausibly present.

But the surface form ("ask a few things") is generic. A pure "asking clarifying questions" pattern does NOT alone satisfy WYSIATI's "naming what's NOT visible" marker.

**Classification: BORDERLINE-ACCEPTABLE.** The full r4 quote (with the three specific probing questions) IS WYSIATI-flavored. The shorter r7 quote (just the meta-statement "ask a few things") is **insufficient on its own** — it's a generic clarifying-question prelude.

**Rubric confidence: MEDIUM.** The "surfacing what's NOT in the user's evidence frame" mechanism is real and detectable, but distinguishing WYSIATI from generic clarifying-question patterns at quote level depends heavily on which slice of the source the quote captures.

**Implementation implication: `prompt_only`.** A deterministic gate would over-reject (any clarifying question would trigger). Verifier prompt restructuring with explicit "WYSIATI requires the quote to name specific information the user hasn't considered" might catch the r7-style insufficient quotes while preserving r4-style fuller quotes.

---

### 5. `time-tested-validation` (BOUNDARY)

**Substrate mechanism (from `data/curation/time-tested-validation.json`):**
- A claim/idea/method looks promising but needs to be checked against proven tests, reference classes, or established validation loops before wider commitment
- The team is at risk of trusting novelty / analogy / polished explanation without enough evidence
- Repeated validation against known standards / expected answers / old-but-reliable checks

**Mechanism core:** deferring to LONG-TRACK-RECORD evidence — proven tests, established validation, "old-but-reliable" reference classes. Distinct from Base Rates (statistical frequency).

**Positive quote markers:**
- Explicit reference to "industry experience" / "long-validated" / "reference class"
- Explicit appeal to a track record over time
- "This has been tried many times before" framing
- "Old-but-reliable" / proven-checks language

**Negative / merely-adjacent markers:**
- Citing a single statistic (that is Base Rates)
- Frequency data without "long history of validation" framing
- Industry-typical numbers without "validated against established standards"

**Case-1 observed quote (r4):**

> "'if you were independent, we'd consider you' is almost exactly zero in actual conversion terms. It means they like you and they're being polite. The number of those conversations that convert to signed engagements in the first 3 months is typically less than 1 in 5, and often zero."

This is base-rate-flavored correction with frequency data ("less than 1 in 5"). It does not invoke long-track-record validation, reference classes against established tests, or "old-but-reliable" checks. The quote's mechanism is Base Rates / Optimism Bias (planning fallacy correction), not TTV.

**Classification: FAILS-OR-BORDERLINE.** TTV's distinguishing feature (long-track-record / validated-against-standards) is NOT in the quote. The "industry experience" word in the source could pass a weak TTV test, but the quote itself shows Base Rates, not TTV.

**Rubric confidence: MEDIUM-HIGH.** The distinction between TTV and Base Rates IS specifiable: TTV requires explicit "track record" or "validated standards" markers, not just frequency data.

**Implementation implication: `gate_buildable`.** Rule: TTV requires more than frequency data — it requires explicit long-track-record / validated-against-standards framing. The r4 surfacing fails this rule.

---

### 6. `feedback-loops` (BOUNDARY)

**Substrate mechanism (from `data/curation/feedback-loops.json`):**
- Outcomes should shape the next action and the system can observe consequences quickly enough to learn instead of repeating the same move blindly
- Behavior changes the environment and the environment changes behavior back, so the problem depends on circular rather than one-way causality
- Measurement can close the loop because signals are tied to real levers

**Mechanism core:** CIRCULAR causality — system output influences future system input. The response must change the system that generated the signal.

**Positive quote markers:**
- Explicit circular causality (X causes Y causes X')
- "Loop" language
- System-environment-system back-action
- Response that changes the system generating the signal

**Negative / merely-adjacent markers:**
- "Respond to signal" without circular dynamics
- Decision rules with conditional triggers ("if X, then Y") — that is pre-registration / Premortem
- Linear cause-effect chains

**Case-1 observed quote (r7):**

> "If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months. That's not failure; that's responding to signal."

This is a **pre-registered checkpoint with a decision rule** — Premortem-shaped, NOT feedback-loops-shaped. The "response" (push back launch) does not change the system generating the signal (network conversion rate, spouse alignment). The quote uses the phrase "responding to signal" but lacks circular dynamics.

**Classification: FAILS rubric.** FL is not the right model — this is Premortem.

**Rubric confidence: HIGH.** "Responding to signal" alone does not satisfy the FL mechanism; circular causality is required and absent here.

**Implementation implication: `gate_buildable`.** Rule: FL requires explicit circular dynamics (X→Y→X'); decision rules with conditional triggers are not FL.

---

### 7. `probabilistic-thinking` (BOUNDARY)

**Substrate mechanism (from `data/curation/probabilistic-thinking.json`):**
- The decision is not yes-or-no but more-likely-or-less-likely, so binary framing would hide meaningful uncertainty
- Compare ranges / distributions / expected value instead of treating one forecast as certain
- Uncertainty can be reduced through better priors, disconfirming evidence, or explicit probability ranges

**Mechanism core:** distribution / range / expected-value thinking — explicitly weighting multiple probabilistic outcomes.

**Positive quote markers:**
- Explicit probability / likelihood / range language ("less than 1 in 5", "70%+", "non-zero chance")
- Distribution-thinking comparing weighted outcomes
- Conditional probability or expected-value framing
- Multiple weighted outcomes considered simultaneously

**Negative / merely-adjacent markers:**
- A single deterministic estimate (even if a range)
- Range used as point estimate ("typically 3-5 months")
- "Tight" qualitative judgments without probability framing

**Case-1 observed quote (r6):**

> "8 months at zero revenue is tight for a first-time independent consultant. Industry experience suggests the first paid engagement often takes 3-5 months from launch, not including the 1-2 months you'll spend setting up legal/admin."

The "3-5 months" is a range estimate but used as **deterministic timing**, not as a distribution-comparison or expected-value calculation. There's no "weight these outcomes by probability" framing. The quote isn't holding multiple probability-weighted outcomes simultaneously; it gives a tight deterministic-feeling timing range. PT mechanism is absent.

**Classification: FAILS rubric.** PT is not the right model — this is a deterministic timing estimate.

**Rubric confidence: MEDIUM.** Distinguishing "range as deterministic timing" from "range as probability distribution" is detectable but requires careful reading. Rule: PT requires explicit probability / likelihood / distribution language ("non-zero chance", "less than X%", "90%+ confident"), not just numeric ranges.

**Implementation implication: `gate_buildable`** with the specific marker test (probability / likelihood / distribution language; not just numeric ranges).

---

### 8. `optimism-bias-and-planning-fallacy` (CONTROL — should pass)

**Substrate mechanism (from `data/curation/optimism-bias-and-planning-fallacy.json`):**
- A plan sounds coherent internally but still needs an outside-view check, a pre-mortem, or a reference class before commitment
- The forecast is being carried by conviction, mission clarity, or proposer charisma more than by downside imagination
- The team is preparing in detail, but that detail may be narrowing attention instead of improving realism

**Mechanism core:** OUTSIDE-VIEW correction of an INTERNALLY-COHERENT plan that has insufficient downside accounting.

**Positive quote markers:**
- Explicit outside-view / reference-class application
- Contrast between internal optimism and external base rate
- "This looks promising but [reality check from outside]"
- Timeline / planning underestimate correction

**Negative / merely-adjacent markers:**
- Generic optimism reference
- Just citing a base rate without "this corrects an over-confident plan" framing

**Case-1 observed quote (r5/r6/r7 — same quote in r6/r7):**

> "On pipeline: 'if you were independent, we'd consider you' is almost exactly zero in actual conversion terms. It means they like you and they're being polite. The number of those conversations that convert to signed engagements in the first 3 months is typically less than 1 in 5, and often zero."

The user's plan ("network conversations are pipeline; 8 months runway is enough") is internally coherent. The assistant applies outside-view (typical conversion rates) to correct planning-fallacy-flavored optimism. Mechanism: outside-view correction of internally-coherent plan with insufficient downside accounting. **Cluster-aligned to C2 in case-1 gold (where OB+PF was acceptable_secondary).**

**Classification: PASSES rubric.**

**Rubric confidence: HIGH.** Outside-view correction is detectable: presence of base-rate reference + critique of planning optimism.

**Implementation implication: control passes.** Validates the rubric's ability to distinguish acceptable from noisy.

---

### 9. `representativeness-heuristic` (CONTROL — should pass)

**Substrate mechanism (from `data/curation/representativeness-heuristic.json`):**
- A judgment is being driven by surface similarity or a vivid category match rather than by rates, frequencies, or causal detail
- People are substituting "What does this resemble?" for "What is statistically or causally likely here?"
- The risk is that a compelling pattern match will crowd out denominator discipline

**Mechanism core:** SURFACE-SIMILARITY substitution for CAUSAL/STATISTICAL likelihood. Pattern-match-as-evidence call-out.

**Positive quote markers:**
- Explicit identification of surface-similarity reasoning
- Substitution of "looks like" for "actually likely"
- Denominator-neglect critique
- Pattern-match-as-evidence call-out

**Negative / merely-adjacent markers:**
- General analogical reasoning
- Citing one example to make a point
- Base-rate correction without explicit pattern-match call-out

**Case-1 observed quote (r7):**

> "'if you were independent, we'd consider you' is almost exactly zero in actual conversion terms. It means they like you and they're being polite."

The user is pattern-matching informal "we'd consider you" expressions as if they represent the class "real pipeline." That IS RH-flavored — substituting surface similarity for actual likelihood. The assistant's "they're being polite, not making a real commitment" is pointing out the misclassification.

But the assistant's MOVE in the quote is closer to "literal interpretation" / base-rate-correction than to RH-explicit-call-out. The "you're substituting surface for actual likelihood" mechanism is **implicit, not local**.

**Classification: BORDERLINE-ACCEPTABLE.** The mechanism is plausibly present but the assistant's move is more base-rate-correction-flavored than RH-call-out-flavored.

**Rubric confidence: MEDIUM.** RH and Base Rates have overlap territory. Distinguishing requires the quote to explicitly call out surface-similarity-substitution, which this quote does only weakly.

**Implementation implication: `prompt_only`.** Distinguishing RH from Base Rates in this kind of quote requires more semantic judgment than a clean gate can provide. Verifier prompt restructuring could ask: "does the quote explicitly call out the user's surface-pattern-match, or just correct a base rate?"

---

## Rubric summary

| Anchor | Classification | Confidence | Implementation implication |
|---|---|---|---|
| `cognitive-dissonance` | **FAILS** | high | `gate_buildable` |
| `checklists` | **FAILS** | high | `gate_buildable` |
| `step-back` | borderline | low–medium | `prompt_only` / `needs_model_metadata` |
| `wysiati` | borderline-acceptable | medium | `prompt_only` |
| `time-tested-validation` | fails-or-borderline | medium-high | `gate_buildable` |
| `feedback-loops` | **FAILS** | high | `gate_buildable` |
| `probabilistic-thinking` | **FAILS** | medium | `gate_buildable` |
| `optimism-bias-and-planning-fallacy` (control) | **PASSES** | high | control validates rubric |
| `representativeness-heuristic` (control) | borderline-acceptable | medium | `prompt_only` |

### Tally

- **Gate-buildable (high confidence)**: cognitive-dissonance, checklists, feedback-loops — 3 models, all clean rejections, would directly address the recurring noisy patterns from E5
- **Gate-buildable (medium confidence)**: time-tested-validation, probabilistic-thinking — 2 models, the gate would catch them if the marker test is implemented correctly
- **Prompt-only / needs-metadata**: step-back, wysiati, representativeness-heuristic — 3 models where the distinction is interpretive (Step Back vs PFR; WYSIATI vs generic clarifying; RH vs Base Rates). A clean deterministic gate would over-reject; verifier prompt with explicit mechanism-marker framing might handle these.
- **Control passes**: optimism-bias-and-planning-fallacy

**5 of 9 anchors are gate-buildable. 3 of 9 are prompt-only. 1 control validates the rubric.**

## E4 decision rule application

Per design memo §5 + Marcin's E4 framing:

### Path A (anchor-sufficiency gate) supported if

- Rubric cleanly rejects cognitive-dissonance and checklists ✓ (both HIGH confidence FAILS)
- Rubric preserves wysiati, step-back, and optimism-bias-and-planning-fallacy ✓ (OB+PF passes high confidence; WYSIATI borderline-acceptable; Step Back borderline)
- Rule can be stated locally at quote level — **partially**: 5 of 9 yes, 3 of 9 no
- Most rubrics are high or medium confidence — **yes** (5 high + 3 medium + 1 low-medium)

**Path A supported for the worst noisy offenders** (CD, Checklists, FL, and likely TTV, PT). The cleanest E4 outcome — these anchors have substrate-grounded mechanism markers that would catch the observed noisy acceptances.

### Path B (verifier prompt restructure) strengthened if

- We can describe the failure conceptually but the rules are too semantic for a deterministic gate
- The right move is "make verifier reason differently" rather than "add a clean gate"

**Path B strengthened for the fuzzier broad/meta models** (Step Back, WYSIATI, RH). For these, a deterministic gate would over-reject; the verifier needs to be taught to look for specific mechanism markers (zoom-out language, naming-what's-not-visible, surface-pattern-match call-out). That is prompt restructuring with mechanism-marker framing.

### Hybrid implication

E4 supports a **hybrid track**, not a single-path commitment:

- **Path A first for high-confidence gate-buildable models** (cognitive-dissonance, checklists, feedback-loops, plus probably time-tested-validation and probabilistic-thinking with the marker tests).
- **Path B alongside, scoped narrowly** to the prompt-restructure-needed models (step-back, wysiati, representativeness-heuristic). The verifier prompt would gain mechanism-marker requirements for these specific model families.

**This matches Marcin's stated prior:** "E4 will probably show that some broad/meta models are gate-buildable (checklists seems very gateable), while others are fuzzier (step-back, wysiati, maybe cognitive-dissonance). That would suggest a hybrid: targeted sufficiency gates for the worst broad/meta models, plus verifier prompt restructuring for the rest."

The data supports the prior. **One refinement**: cognitive-dissonance is actually MORE gate-buildable than the prior expected (high confidence FAILS on the observed quote with a clean two-belief / motivated-reframing test). Step-back, wysiati, RH are the genuinely fuzzy ones — those are the prompt-restructure cases.

## What evidence would be needed before implementing either

Before committing to the hybrid:

1. **Test the gate on more conversations.** The case-1 N=4 sample is one conversation's worth of noisy anchors. A second or third case (e.g., the audit's other failure-rich cases) might reveal:
   - Different broad/meta models are noisy
   - The same gate-buildable models surface acceptable anchors elsewhere (and the gate would have over-rejected)
2. **Implementation-cost estimate for Path A gates.** Per-model deterministic markers vs LLM-assisted-sufficiency-call. The cheap deterministic version may not catch all the no's (e.g., does CD's "two-belief" test reliably exclude the assistant's "yes I'm pushing back" pattern?).
3. **Path B prompt-restructure scope.** What does a prompt look like that asks the verifier to require specific mechanism markers per broad/meta model? Is the prompt token-count manageable? Does it interact with the rest of the verifier rubric?

Those are scoping questions for the next design memo, not this one. E4's job is to say which path the leak map points at; the implementation memo decides what to build.

## Status

- E4: **complete**. Hybrid track recommended (Path A for the high-confidence gate-buildable models; Path B for the prompt-restructure ones).
- E5 + E4 combined: H4 (broad/meta sufficiency blind spot) is the primary live problem; the rubric for catching it is partially specifiable (5/9 gate-buildable) and partially needs verifier-side prompt work (3/9 prompt_only).
- Path C (consensus) is still ruled out from E5.
- Path D (full Sully decomposition) is still premature — neither E5 nor E4 has shown evidence that the simpler local fixes (A, B) can't address the observed problems.
- Next experiment per §9 ordering: **E2 (recall determinism)** — zero cost, runs before any paid LLM test.
- Decision tree: stays open. After E2, if recall is deterministic, E1 (verifier stochasticity) becomes a clean test of H1. If recall is non-deterministic, the design memo §7 needs an entry for "recall variance is contributing to churn" and the architecture conversation becomes more complex.

## What this experiment did NOT do

- Did not test the rubric on cases other than `user-launch-independent-fintech`. The hybrid recommendation is anchored on N=4 reruns of one conversation.
- Did not write any prompt or any code. The artifact is the rubric, not an implementation.
- Did not pick the architecture. The §7 decision tree requires E2 + (selectively) E1/E3 outcomes to fully resolve the architecture question.
- Did not invalidate Path D. If E2/E1/E3 reveal upstream instability (fingerprint or recall) that the hybrid gates can't address, decomposition re-enters as a candidate.

The measurement leads. E4 says: hybrid is buildable for the worst noisy offenders. Move to E2 next.
