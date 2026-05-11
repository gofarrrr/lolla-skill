# Seeking Wisdom Step 2 Actionable Handover

Date: 2026-05-11

Status: planning artifact only. This is not a code/runtime change.

## Purpose

Step 1 reframed `Seeking Wisdom` correctly: Bevelin is not a fifth lane, not a
lexical audit layer, and not a product taxonomy. It is possible source material
for improving the existing Lolla substrate.

Step 2 turns that into a handover that someone can execute without confusing
the story of the system. The job is to decide:

1. what knowledge we would inject;
2. why that knowledge should help;
3. where it belongs in the existing system;
4. what evidence would count as a win;
5. what it costs to test;
6. when we stop because the signal is redundant, noisy, or too broad.

The central principle remains:

> Bevelin should enrich the existing LLM/embedding/deterministic interaction. It
> should not create a parallel reasoning architecture.

## System Fit

The live system already has the right places for this knowledge.

| Layer | Current owner | What Bevelin may change | What it must not change |
| --- | --- | --- | --- |
| Lane 1 LLM triage/deep checks | Pass 1 and Pass 2 prompts plus `data/curated/subpattern_catalog.json` | Sharper activation contexts and subpattern materiality tests | No lexical Bevelin detector, no checklist score |
| Embedding recall | Existing `text-embedding-3-large` chunks, tendency guidance, activation conditions, V60 recall | Candidate recall after source-backed chunks enter compiled artifacts | No embedding-only conclusion; embeddings stay additive |
| Deterministic middle | Explicit artifact lookup, graph traversal, caps, packet custody, ledger validation | More source-backed records for the existing deterministic selector to preserve | No deterministic semantic judgment about usefulness |
| V60 private enrichment | `data/compiled/model_affordances/affordances_v60.json` | New or sharpened affordance/absence records selected into the existing private packet | No fifth lane, no public Bevelin card |
| Step 6 LLM consideration | Claude/Codex reads lane cards and V60 chunks, then writes the update and ledger | Better private pressure: evidence gates, thresholds, guardrails, role-reversal checks, learning traces | No public machinery/source leakage |
| Product output | Chat, memo, Observatory split | Better decision pressure in natural language | No `Bevelin says`, no V60/affordance/chunk labels in chat/memo |

This means the safest first implementation path is source packet -> V60
candidate artifact -> replay -> only then subpattern or prompt changes.

## Quality-First Call Discipline

The goal is not to minimize call count at the expense of judgment quality. The
goal is to keep each cognitive task small enough that we can see what happened.

Do not improve Bevelin uptake by stuffing more obligations into an already
heavy call. A prompt that asks one model to detect a tendency, select source
material, judge usefulness, rewrite the answer, hide private machinery, and
produce a valid ledger is too loaded. Past V60 replay already showed this
failure shape: useful private reasoning can coexist with invalid ledgers,
leaky public fields, or generic composition when one call carries too many
jobs.

Use this rule:

> If the new work is cognitively meaningful, isolate it into the smallest
> possible call or replay surface that can answer that one question well.

Good uses of additional calls:

- a narrow private-trace call that only judges whether selected Bevelin/V60
  chunks are useful, rejected, deferred, or private guardrails;
- a small system-bound composer call that only asks whether a private trace can
  become a clean product delta;
- an isolated Lane 1 probe that only asks whether one subpattern route is
  materially present in a tiny case;
- parallel pressure checks when each call receives one bounded artifact and can
  disagree without sharing context.

Bad uses of additional complexity:

- bulk-inserting Bevelin checklist language into every Step 6 update;
- adding a new layer that must always run even when the substrate has not
  selected relevant material;
- asking one model to both reason with private source material and perfectly
  sanitize all public output;
- testing usefulness through broad cases where we cannot tell which candidate
  unit caused the change.

The deterministic middle should still own merging, custody, caps, and
validation. The LLM call should own one high-quality judgment at a time.

## Small-Case Discipline

The first useful tests should be small, almost surgical. We are not trying to
prove that Bevelin is broadly good. We are trying to answer one local question
at a time:

- Does the candidate unit enter the packet?
- Does the model understand the strongest plausible application?
- Does it reject the chunk for a real reason?
- Does it create one concrete product operator?
- Does that operator improve the answer without leaking machinery?

Prefer tiny ASCII/plain-text cases and narrow archived cases before full
end-to-end runs. A case should be small enough that a reviewer can point to the
exact reasoning pressure under test. For example:

- **absolute yardstick**: one short decision where the answer accepts a worse
  term because it is "better than the scary alternative";
- **role reversal**: one short fairness/conflict case where the answer appeals
  to what the other side should do instead of designing an enforceable rule;
- **postmortem trace**: one recurring-decision case where the answer recommends
  action but does not preserve what will be learned later;
- **disconfirmation control**: one commitment case where the answer needs a
  named observation that would reverse the recommendation.

Only after these tiny probes behave well should the 8-case replay manifest or
live repeated skill runs decide promotion. This keeps the story inspectable:
first prove the unit can do one thing well, then test whether it survives the
larger system.

## What To Inject

The Bevelin material that looks most useful is not "more biases." Lolla already
has Munger's tendency ontology. The useful Bevelin units are operational tests
that make a detected tendency sharper.

The table below is the candidate knowledge packet for review. Each row is an
injection hypothesis, not an approved record.

| ID | Knowledge unit | Bevelin source anchors | Existing owner | Candidate injection | Why inject | Expected runtime effect | Win signal | Stop condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BVL-01 | Disconfirmation / prosecutor test | `Seeking Wisdom.md:5372-5398`, `Seeking Wisdom.md:4369-4377`; System B Munger source `The_Psychology_of_Human_Misjudgment.md:227` | V60: `falsifiability`, `scientific-method-evidence-testing`, `premortem`; Lane 1: `inconsistency-avoidance-tendency/missing-reversal-condition`, `reason-respecting-tendency/*`, `overoptimism-tendency/missing-reversal-condition` | Mostly sharpen existing records. Possible absence blocker: "generic skepticism without a named falsifier or consequence." | The current system already has falsifiability, but Bevelin gives a concrete operator: think like a prosecutor and name what would prove the conclusion wrong. | Pass 2 and Step 6 turn "be skeptical" into a reversal condition, evidence gate, or kill criterion. | Selected chunk becomes `used` or private guardrail and final answer names a concrete falsifying observation or threshold. | If outputs merely add generic "look for contrary evidence" language, reject as duplicate/checklist theater. |
| BVL-02 | Representative evidence and track record | `Seeking Wisdom.md:5380-5388`, `Seeking Wisdom.md:4337-4343`, `Seeking Wisdom.md:2876` | V60: `base-rates`, `statistical-discipline`, `scientific-method-evidence-testing`, `confidence-calibration`; Lane 1: `overoptimism-tendency/missing-denominator`, `availability-misweighing-tendency/vivid-proof-substitution` | Lower-priority enrichment. Add only if source review finds a sharper evidence-quality blocker than current records. | Lolla often needs to distinguish anecdote from reference-class evidence. Bevelin's value is the track-record/representativeness question, not just base-rate naming. | Embedding/V60 recall surfaces representative-evidence requirements when an answer leans on vivid examples, current trend, or one success story. | Final answer asks for or uses the correct reference class, denominator, or historical range before recommending commitment size. | If current `base-rates.outside-view-reference-class-anchor` already produces the same pressure, do not duplicate. |
| BVL-03 | Consequences if wrong / reversibility / opportunity cost | `Seeking Wisdom.md:5401-5424` | V60: `margin-of-safety`, `risk-assessment`, `opportunity-cost`, `decision-trees`, `calculated-risk-taking`; Lane 1: `overoptimism-tendency`, `simple-pain-avoiding-psychological-denial-tendency` | Likely absence blocker or treatment requirement: downside must be tied to reversibility, opportunity cost, or handleability. | Many answers mention downside but fail to say whether the user can survive or reverse being wrong. | Step 6 converts "risk exists" into a concrete decision boundary: what is at stake, what is reversible, what alternative is displaced. | Product delta changes commitment sizing, sequencing, or "try first" recommendation. | If it only lengthens risk sections without changing action, reject. |
| BVL-04 | Absolute yardstick after removing the contrast frame | `Seeking Wisdom.md:5427-5431`, `Seeking Wisdom.md:4135`, `Seeking Wisdom.md:4182`; System B mapping `munger_structural_mapping.md:103` | V60: `baseline-establishment`, `goal-setting`, `statistical-discipline`, `constraints`, `false-precision-avoidance`, `multi-criteria-decision-analysis`; Lane 1: `contrast-misreaction-tendency/*` | High-priority candidate. Add source-backed treatment requirement or subpattern sharpening for "comparison removed, what standard still governs?" | Contrast misreaction is often not a missing comparison, but missing an independent standard. Bevelin's yardstick language fits that gap. | Lane 1/Step 6 asks what threshold, absolute cost, or baseline governs after the adjacent deal/status/current option is removed. | Real-estate, offer, and pricing cases get a clearer absolute go/no-go line. | If candidate mostly restates "compare options," reject as already covered by MCDA/trade-offs. |
| BVL-05 | Incentive/accountability map | `Seeking Wisdom.md:785`, `Seeking Wisdom.md:793`, `Seeking Wisdom.md:817-821`, `Seeking Wisdom.md:895`; System B Munger source `The_Psychology_of_Human_Misjudgment.md:103-119` | V60: `incentives`, `principal-agent-problem`, `obligations-controls-mapping`, `power-dynamics`, `systems-thinking`; Lane 1: `reward-and-punishment-superresponse-tendency/*`, `kantian-fairness-tendency/*` | Mostly sharpen existing V60 records. Possible missing-evidence gate: "who benefits, who pays, who is accountable?" | Lolla already has incentives, but Bevelin adds operational accountability and upside/downside sharing. | Step 6 stops treating stated intent as enough and maps actor payoffs, measurement, and consequence-bearing. | Whistleblower, consultant, friendship-money, and org-design cases surface an actor/accountability map. | If it becomes suspicious mind-reading or bad-faith defaulting, reject or make it an absence blocker. |
| BVL-06 | Role-reversal system fairness | `Seeking Wisdom.md:5464-5490` | V60: `power-dynamics`, `principal-agent-problem`, `obligations-controls-mapping`, `boundaries`, `systems-thinking`; Lane 1: `kantian-fairness-tendency/*`, `reciprocation-tendency/*` | High-priority candidate. Likely new treatment requirement, maybe subpattern enrichment: "would this rule/system still be acceptable if roles were reversed?" | Current Kantian fairness routes catch unenforced fairness expectations. Bevelin may improve the antidote: test the system, not just the moral feeling. | Step 6 reframes fairness from "they should act fairly" to "what enforceable rule would be fair from both positions?" | Product answer adds an enforceable term, boundary, governance rule, or negotiation test rather than moral appeal. | If it moralizes or turns every conflict into symmetry theater, reject. |
| BVL-07 | Active decision and update condition | `Seeking Wisdom.md:5440-5443`, `Seeking Wisdom.md:5372-5378` | V60: `decision-trees`, `falsifiability`, `feedback-loops`, `iteration`, `adaptation`, `auditability-traceability`; Lane 1: `inconsistency-avoidance-tendency/*`, `doubt-avoidance-tendency/*` | Candidate treatment requirement: before commitment, record the event or evidence that would change the decision. | This is a bridge between decision pressure and learning. It makes the system ask whether the user is choosing actively or drifting with the default. | Step 6 adds a live update trigger, not just a recommendation. | Final answer includes a date/event/evidence threshold for revisiting the choice. | If it adds process overhead to trivial decisions, keep it only for high-stakes/reversible-boundary cases. |
| BVL-08 | Postmortem / learning trace | `Seeking Wisdom.md:5445-5451` | V60: `feedback-loops`, `auditability-traceability`, `iteration`, `hindsight-bias`, `lean-startup-methodology`, `adaptation`; Lane 1: `use-it-or-lose-it-tendency/*`, `inconsistency-avoidance-tendency/*` | High-priority candidate. Add treatment requirement: record original reasons, expected signal, and later reality before memory rewrites the lesson. | Lane 1 can catch stale methods and lapsed process, but Bevelin adds a pre/post trace that lets future runs learn honestly. | Step 6 turns decisions into testable records when learning value is high. | Product answer tells user what to record now and what later outcome will teach them. | If it creates diary-like bloat for one-off choices, narrow activation to recurring, expensive, or identity-loaded decisions. |
| BVL-09 | State-of-mind / self-interest audit | `Seeking Wisdom.md:5366-5370`, `Seeking Wisdom.md:5460-5464`, `Seeking Wisdom.md:631-662` | V60: `self-control`, `emotional-intelligence`, `incentives`, `simple-pain-avoiding-psychological-denial-tendency` related routes | Do not promote early. Keep as source packet only unless a concrete owner emerges. | It is real, but it is easy to overreach into psychologizing the user. | At most, private Step 6 guardrail notices urgency, pain avoidance, or ego threat before giving advice. | Useful only if it improves caution without public diagnosis. | If it sounds like mind-reading, reject. |

## First Recommended Injection Set

Do not start with everything. The first real candidate should use four units:

1. **BVL-04 Absolute yardstick**
2. **BVL-06 Role-reversal system fairness**
3. **BVL-08 Postmortem / learning trace**
4. **BVL-01 Disconfirmation / prosecutor test as a control target**

Reasoning:

- `BVL-04`, `BVL-06`, and `BVL-08` look like the clearest additions to current
  behavior. They are not obviously redundant with the strongest existing V60
  records.
- `BVL-01` is central but already represented. Including it as a control tells
  us whether Bevelin improves quality or merely restates current falsifiability
  substrate.
- `BVL-02`, `BVL-03`, and `BVL-05` are important but already heavily represented
  by current V60 records. They should be used for gap-filling only.
- `BVL-09` is too easy to misuse and should stay dormant until a case proves
  the need.

## Expected Results

The desired change is not "more findings." The desired change is better
decision pressure when the existing system has already found or retrieved a
relevant reasoning pattern.

Expected improvements:

- Lane 1 should pick more precise subpatterns only when the conversation
  contains that reasoning shape.
- V60 should select source-backed chunks that create a concrete private
  consideration opportunity.
- Step 6 should translate useful chunks into one of five product effects:
  evidence gate, reversal threshold, absolute yardstick, role-reversal system
  check, or learning trace.
- The final answer should become more actionable, not longer by default.
- Observatory should show the exact selected/rejected/deferred path.

Non-goals:

- No extra public taxonomy.
- No Bevelin label in chat/memo.
- No generic checklist paragraph.
- No increase in tendency detections unless precision is maintained.
- No lexical matching as evidence of usefulness.

## Handover Plan

### Step 0: Freeze The Baseline Story

Action:

- Record the current baseline artifact paths:
  - `data/curated/subpattern_catalog.json`
  - `data/compiled/model_affordances/affordances_v60.json`
  - `data/embeddings.db`
  - `HOW_IT_WORKS.md`
- Use `origin/main` or an explicitly named branch as the baseline.
- Do not modify default runtime artifacts during the exploratory phase.

Evidence produced:

- A short baseline note with commit SHA and artifact hashes.

Gate:

- If the candidate cannot be run by explicit path, stop. It is too easy to
  confuse baseline and candidate runs.

### Step 1: Build The Source Packet

Action:

- Create a review-only source packet from Bevelin, not runtime code.
- For each candidate unit, capture:
  - source file and line range;
  - short paraphrase;
  - at most a tiny source quote where needed;
  - proposed owner model/tendency/subpattern;
  - expected runtime effect;
  - misuse guard;
  - duplicate check against current V60.

Suggested output:

- `research/seeking-wisdom-source-packet-2026-05-11.md`

Gate:

- Every candidate must have a current owner or an explicit "no clean owner"
  reason.
- Anything that reads like general advice without a concrete runtime effect is
  rejected before implementation.

### Step 2: Gap Audit Against Current Substrate

Action:

- For each selected unit, inspect current V60 records and subpatterns.
- Classify the unit as one of:
  - **duplicate**: current substrate already expresses it cleanly;
  - **sharpen existing**: same owner, better activation/treatment wording;
  - **new affordance/absence candidate**: owner exists but record is missing;
  - **subpattern candidate**: Lane 1 needs a more precise route;
  - **reject/defer**: useful idea, no safe owner yet.

Known current substrate facts:

- V60 has 222 model records, 306 affordances, and 697 absence records.
- `falsifiability`, `scientific-method-evidence-testing`, `premortem`,
  `base-rates`, `incentives`, `principal-agent-problem`, `opportunity-cost`,
  `decision-trees`, `margin-of-safety`, `feedback-loops`,
  `auditability-traceability`, `baseline-establishment`, `goal-setting`,
  `statistical-discipline`, `constraints`, `power-dynamics`,
  `obligations-controls-mapping`, `boundaries`, `systems-thinking`,
  `iteration`, `lean-startup-methodology`, and `adaptation` already have V60
  records.
- `metrics` was mentioned as a possible conceptual owner in Step 1, but it is
  not a V60 model record in the current artifact. Use actual current owners
  instead: `baseline-establishment`, `goal-setting`, `statistical-discipline`,
  `constraints`, or `multi-criteria-decision-analysis`.

Gate:

- At least one of the first candidate units should be "sharpen existing" rather
  than "new." If everything requires new ontology, we are multiplying
  architecture.

### Step 3: Create Candidate Records Outside Default Runtime

Action:

- Create candidate V60 records or record edits in an explicit experiment path.
- Do not overwrite `affordances_v60.json`.
- Do not set the candidate as the default skill artifact.
- Keep records source-backed and schema-valid.

Suggested implementation shape for the next PR, not this planning PR:

- `data/model_affordances/bevelin_candidate/*.json`
- `data/compiled/model_affordances/affordances_v60_bevelin_candidate.json`
- `data/compiled/model_affordances/quality_report_v60_bevelin_candidate.md`

Gate:

- Candidate artifact must be runnable only with an explicit path such as
  `--affordances-path data/compiled/model_affordances/affordances_v60_bevelin_candidate.json`.
- If candidate records require broad prompt instructions to make sense, the
  substrate is too weak.

### Step 4: Dry Packet Replay

Action:

- Use the existing offline preflight harness before any paid calls.
- Run the 8-case balanced manifest because it already covers negotiation,
  legal/ethical risk, pivot uncertainty, real estate, messy multi-problem
  advice, PhD research, user-plan commitment, and friendship/money fairness.

Dry-run command shape:

```bash
python3 scripts/run_v60_transaction_replay_lab.py \
  --case-manifest research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json \
  --affordances-path data/compiled/model_affordances/affordances_v60_bevelin_candidate.json \
  --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-XX-bevelin-candidate-dry-run \
  --card-cap 8 \
  --max-nominations 18 \
  --dry-run
```

Evidence produced:

- Candidate pool diff.
- Selected cards/chunks.
- Suppressed/not-presented candidates.
- Whether Bevelin chunks enter the packet at all.
- Which baseline chunks were displaced.

Gate:

- If candidate chunks never enter selected packets across the 8 cases, either
  the injection is irrelevant to the manifest or retrieval/ownership is wrong.
- If Bevelin chunks enter by displacing stronger baseline chunks without a
  clear reason, stop and revise the records.

### Step 5: Cheap Private-Trace Test

Action:

- Before full judged A/B, isolate the private reasoning question.
- Use exact-chunk private replay or equivalent to ask: if Step 6 sees these
  chunks, does it find them useful, reject them with a grounded reason, or defer
  them for missing evidence?

Relevant harness:

```bash
python3 scripts/run_v60_chunk_exact_private_replay.py --help
```

Real local price from prior paid run:

- `2026-05-10-c44c-exact-chunk-private-replay-hardened-paid`
- 8 cases, 8 calls
- 118,153 input tokens, 18,683 output tokens
- total cost `$0.032632`
- cost per case `$0.004079`

Gate:

- Continue only if at least 3 of 8 cases show concrete usefulness or a valuable
  private guardrail, and low/irrelevant rejections are explainable.
- A grounded rejection can be a success. A vague "not useful" is not.

### Step 6: System-Bound Composer Test

Action:

- If private trace is promising, test whether the useful private pressure can
  be admitted into product prose without leaking substrate.

Relevant harness:

```bash
python3 scripts/run_v60_system_bound_enrichment_replay.py --help
```

Real local price from prior paid run:

- `2026-05-10-c45-system-bound-enrichment-paid`
- 8 cases, 8 calls
- 45,419 input tokens, 2,016 output tokens
- total cost `$0.009722`
- cost per case `$0.001215`

Gate:

- Continue only if product deltas are small, concrete, and source-safe.
- Stop if the composer leaks V60/source/chunk language or produces generic
  checklist prose.

### Step 7: Full A/B Replay

Action:

- Run baseline vs candidate through the existing V60 transaction paid replay.
- Use `consideration_router` first because it matches the current philosophy:
  private consideration, not public model theater.

Command shape:

```bash
python3 scripts/run_v60_transaction_paid_replay.py \
  --case-manifest research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json \
  --affordances-path data/compiled/model_affordances/affordances_v60_bevelin_candidate.json \
  --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-XX-bevelin-candidate-paid \
  --c-variant consideration_router \
  --max-items 8 \
  --seed 4211
```

Real local price from comparable prior runs:

- `2026-05-10-c43-consideration-router-paid-edge-all`
  - 8 cases, 24 calls
  - 178,947 input tokens, 74,358 output tokens
  - total cost `$0.275665`
  - cost per case `$0.034458`
- `2026-05-10-c43-embedding-balanced-4211-paid-edge-all`
  - 8 cases, 23 calls
  - 175,195 input tokens, 78,697 output tokens
  - total cost `$0.273664`
  - cost per case `$0.034208`

Gate:

- Continue only if the candidate wins on product usefulness or private
  reasoning usefulness without worse validation/product hygiene.
- Do not promote based on one case. Treat a single case as a diagnostic, not a
  conclusion.

### Step 8: Live Skill Repeats

Action:

- Only after lab signal, run the actual skill on a small focused set.
- Use repeated runs for borderline cases, because LLM stages are probabilistic.

Suggested live set:

- `friendship_money`: role-reversal/system fairness.
- `real_estate` or `multi_offer`: absolute yardstick under contrast pressure.
- `phd_research` or `messy_three_problems`: postmortem/learning trace.
- `whistleblower`: incentives/accountability as a stress case, if included.

Minimum repeat plan:

- 3 cases x 2 runs each if budget is tight.
- 4 cases x 3 runs each if deciding promotion.

Observed live archive cost:

- 13 archived runs with `usage_summary.estimated_total_cost_usd`.
- Minimum `$0.173422`, median `$0.944086`, mean `$0.825057`, maximum `$1.279149`.
- This is higher than the OpenRouter-only lane estimate because live skill runs
  can include Claude Step 6/Step 7 pressure-check usage.

Gate:

- Use `scripts/compare_archived_runs.py` to compare candidate vs baseline:

```bash
python3 scripts/compare_archived_runs.py LEFT_RUN_DIR RIGHT_RUN_DIR \
  --format markdown \
  --output research/bevelin-candidate-run-comparison-2026-05-XX.md
```

- Promote only if the story is consistent across cases:
  - better evidence gate, threshold, system check, or learning trace;
  - no run-health degradation;
  - no product-output leakage;
  - no broad overfire in Lane 1;
  - no memo bloat.

## Real Price Envelope

These prices should be rechecked before paid promotion work. Pricing is unstable
and one current model has a near-term availability warning.

Current published API prices checked on 2026-05-11:

- OpenAI `text-embedding-3-large`: `$0.13` per 1M tokens, batch `$0.065` per 1M tokens.
- OpenAI `gpt-4o-mini`: `$0.15` per 1M input tokens, `$0.075` cached input, `$0.60` output.
- OpenRouter `x-ai/grok-4.1-fast`: `$0.20` per 1M input tokens, `$0.50` output. OpenRouter also marks it as "Going away May 15, 2026", so do not assume it remains available after that date.
- OpenRouter `moonshotai/kimi-k2.6`: `$0.74` per 1M input tokens, `$3.49` output.

Pricing references:

- OpenAI model docs: `https://platform.openai.com/docs/models/text-embedding-3-large`
- OpenAI model docs: `https://platform.openai.com/docs/models/gpt-4o-mini`
- OpenRouter model page: `https://openrouter.ai/x-ai/grok-4.1-fast/pricing`
- OpenRouter model page: `https://openrouter.ai/moonshotai/kimi-k2.6/pricing`

Local repo estimates and measurements:

| Test layer | Extra runtime calls? | Observed / expected cost | What it buys |
| --- | --- | --- | --- |
| Source packet only | No | `$0` API cost | Human-reviewable knowledge inventory |
| V60 candidate artifact lookup | No extra OpenRouter call in live skill | `$0` API cost, except possible existing embedding retrieval reuse | Tests deterministic custody and packet selection |
| Embedding query expansion in normal run | Existing optional OpenAI calls | `HOW_IT_WORKS.md` estimates about `$0.001` for gpt-4o-mini expansion and `$0.0002` for query embeddings | Candidate recall through existing embedding layer |
| Re-embedding candidate source chunks | OpenAI embeddings | At `$0.13/M`, even 10,000 new tokens is `$0.0013`; full current rebuild cost depends on actual token volume. `HOW_IT_WORKS.md` currently says 867 edge activation vectors are about `$2` per rebuild. | Makes new source chunks retrievable |
| Cheap private exact-chunk replay | Yes | Prior 8-case run `$0.032632`, `$0.004079/case` | Isolates whether chunks are useful before public writing |
| System-bound composer replay | Yes | Prior 8-case run `$0.009722`, `$0.001215/case` | Tests whether useful private pressure can become clean product prose |
| Full judged V60 replay | Yes | Prior 8-case runs about `$0.274-$0.276`, `$0.034/case` | Controlled product comparison |
| Live skill repeat | Yes, full orchestration | Archived observed range `$0.173-$1.279/run`, median `$0.944` | Actual end-to-end behavior |

The cheapest honest sequence is therefore:

1. source packet and gap audit: no API cost;
2. dry packet replay: no API cost;
3. exact private trace on 8 cases: about `$0.03`;
4. system-bound composer on 8 cases: about `$0.01`;
5. full judged replay on 8 cases: about `$0.27`;
6. live repeated runs only after signal: budget about `$1/run` unless the current stack changes.

## Prompt Upgrade Candidates

Prompt changes should come after substrate evidence. If we change prompts first,
we will not know whether Bevelin helped or whether we merely told the model to
ask more checklist questions.

### Candidate Step 6 Micro-Upgrade

Use only if V60 chunks are selected and the ledger shows they are useful, but
Step 6 fails to translate them into product pressure.

Candidate wording:

```text
When private source-backed material is useful, translate it into one concrete
decision operator: an evidence gate, reversal threshold, absolute yardstick,
actor incentive/accountability map, role-reversal system test, or learning
trace. If none fits the case, reject or defer it with a reason. Keep source and
substrate labels private.
```

Why:

- It does not add Bevelin knowledge directly.
- It teaches Step 6 how to cash out selected private chunks.
- It preserves the ledger discipline: use, reject, defer, or private guardrail.

Risk:

- It could turn into formulaic output if added globally.

Gate:

- Add only after candidate chunks show private usefulness but product deltas are
  weak or leaky.

### Candidate Lane 1 Subpattern Prompt Micro-Upgrade

Use only if candidate subpattern edits are present and Pass 2 keeps selecting
the broad/general route when evidence supports a sharper route.

Candidate wording:

```text
When choosing a subpattern, prefer the route that names the missing decision
test: missing falsifier, missing yardstick, missing accountability, missing
role-reversal/system test, or missing update trace. Do not select a sharper
route unless the conversation evidence supports that exact omission.
```

Why:

- It directs the LLM toward material omissions rather than familiar labels.

Risk:

- It may over-select the new routes unless calibration examples are added.

Gate:

- Add only after replay shows real subpattern ambiguity.

## Evaluation Rubric

Score each candidate unit per case.

| Dimension | Good | Bad |
| --- | --- | --- |
| Selection | Candidate chunk selected for a case where the reasoning shape is present | Candidate selected because wording is broad or fashionable |
| Ledger | `used`, `deferred`, or `rejected` with strongest plausible application and clear reason | Generic rejection, missing ledger, invalid ledger, or forced use |
| Product delta | Adds a concrete evidence gate, threshold, role-reversal test, accountability map, or learning trace | Adds generic advice or longer prose without action change |
| Precision | Improves the exact tendency/subpattern route | Broad overfire across unrelated cases |
| Safety | Keeps source/private machinery out of chat and memo | Leaks V60, affordance, chunk, Bevelin, lane, or internal IDs |
| Cost | Fits cheap lab-first sequence | Requires expensive live repeats before signal exists |

Promotion threshold:

- Lab: at least 3 of 8 cases show concrete useful private pressure, with no
  systematic validation/product leakage.
- Live: repeated runs show the same kind of improvement in at least 2 targeted
  case families.
- Product: final answers are shorter or equal length unless added length creates
  a decision-relevant operator.

Rejection threshold:

- More detections but lower precision.
- Selected chunks mostly rejected as irrelevant.
- Product outputs become checklist-like.
- Candidate records duplicate current V60.
- Improvement appears only in one case and fails on adjacent cases.

## Case Matrix

Use the existing balanced manifest first:

- `multi_offer`: negotiation, opportunity cost, power, absolute yardstick.
- `whistleblower`: incentives, accountability, evidence threshold, high-stakes
  caution.
- `startup_pivot`: overoptimism, evidence quality, active update condition.
- `user_has_plan`: commitment, falsifier, reversal condition.
- `real_estate`: contrast frame, absolute downside, yardstick.
- `messy_three_problems`: process/learning trace and scope discipline.
- `phd_research`: postmortem, learning loop, skill decay/stale method.
- `friendship_money`: fairness, reciprocity, role reversal, enforceable terms.

Do not infer usefulness from one case. A single case can identify a failure mode
or promising pattern, but promotion needs adjacent-case confirmation.

## Concrete Next PR Shape

The next PR should be small and reversible:

1. Add a source packet doc.
2. Add candidate V60 records for only the first selected units.
3. Compile a candidate artifact with a non-default filename.
4. Add no new lane, no new CLI surface except explicit artifact-path usage if
   needed.
5. Run schema/compiler tests.
6. Run dry replay against the 8-case manifest.
7. If dry replay is healthy, run cheap private trace before any full judged A/B.

Suggested tests after records exist:

```bash
python3 -m pytest \
  tests/test_model_affordance_schema.py \
  tests/test_model_affordance_compiler.py \
  tests/test_v60_transaction_replay_lab.py \
  tests/test_v60_transaction_paid_replay.py
```

Suggested report artifact:

- `research/seeking-wisdom-candidate-v60-readout-2026-05-XX.md`

That readout should answer:

- Which Bevelin units were injected?
- Which current records did they sharpen?
- Which cases selected them?
- Which chunks were used, rejected, deferred, or private guardrails?
- What product deltas appeared?
- What did it cost?
- Did any outputs leak internal machinery?
- Should the unit be promoted, revised, or rejected?

## Decision Standard

The promotion question is not:

> Did we add Bevelin?

It is:

> Did Bevelin source material make the existing Lolla system produce better
> evidence gates, thresholds, system checks, and learning traces through the
> existing LLM, embedding, deterministic custody, and Step 6 consideration path?

If yes, promote the narrow records that proved it.

If no, keep the source packet as research and do not burden the runtime.
