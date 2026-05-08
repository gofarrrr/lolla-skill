# PR84 Social/Incentive Enrichment v46 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr84-social-incentive-v46`

Artifact: `model_affordances_v46`

Status: dormant review substrate only. No runtime, prompt, lane, packet, adapter, renderer, or product pickup is introduced.

## Verdict

PASS as dormant source-custodied enrichment.

PR84 is intentionally narrow. The social/incentive ring looked tempting because it contains trust, persuasion, game theory, authority, reciprocity, and motivation material. That is exactly the kind of material that can become impressive but bloated if every rich paragraph becomes a card.

The strict operating question was:

> Would separating this material change the downstream receiver transaction?

Three candidates passed that test:

1. `signaling.create-actionable-coordination-signal`
2. `game-theory-payoffs.adverse-response-floor-test`
3. `nash-equilibrium.dominant-strategy-mechanism-design`

Most candidates did not pass. That is a good outcome. It means the corpus is not being expanded merely because more language exists in the source.

## Source Reading Scope

The audit focused on social, incentive, authority, trust, coordination, and strategic-interaction records. Full canonical Markdown sources under `MM_CANONICAL_216` were read for accepted changes, and read-only subagent audits covered adjacent candidates.

Accepted split sources:

- `Signaling_rag.md`
- `Game_Theory_Payoffs_rag.md`
- `Nash_Equilibrium_rag.md`

Adjacent audited records that remained compressed:

- `Incentives_rag.md`
- `Principal_Agent_Problem_rag.md`
- `Moral_Hazard_rag.md`
- `Adverse Selection_rag.md`
- `Information_Asymmetry_rag.md`
- `Prisoners_Dilemma_rag.md`
- `Batna_rag.md`
- `International_Negotiation_and_Diplomacy_Models_rag.md`
- `Social_Proof_rag.md`
- `Authority_Bias_rag.md`
- `Reciprocity_Principle_rag.md`
- `Liking_Principle_rag.md`
- `Psychological_Safety_rag.md`
- `Understanding_Motivations_rag.md`
- `Non_Violent_Communication_rag.md`

Subagents were used as independent read-only pressure checks. Their recommendations were accepted only after local source review and exact quote compilation.

## Why This Is Not Bloat

PR84 does not add absence records or broaden runtime authority. It adds only three positive affordances, each because the existing card shape was pooling two different future use/reject/defer decisions.

The rejected expansion pattern was:

> This source contains more nuance, therefore add more cards.

The accepted enrichment pattern was:

> This source contains a second operational move with different activation, evidence, treatment, and misuse guards.

That distinction matters for future packet compression. Richness is useful only when it gives the receiver a cleaner transaction, not when it makes a card sound wiser.

## Positive Splits Added

### `signaling.create-actionable-coordination-signal`

Why split:

The existing `signaling.costly-proof-of-intent-test` asks whether a signal proves hidden quality, intent, reliability, or commitment. The source also supports a distinct move: make an abstract or invisible strategy concrete enough for receivers to coordinate action.

Those are different transactions:

- proof card: “Is this signal costly enough to trust?”
- coordination card: “Does this signal tell the receiver what to do differently?”

Source custody anchors include:

- `communication is never just about transferring facts; it is about creating a shared, actionable reality`
- `resolve ambiguity and manage uncertainty`
- `Signaling is essential when communicating abstract or invisible ideas, such as company strategy, software architecture, or change management.`
- `An idea can be accurate but useless if it fails to help the recipient make decisions.`
- `telling a flight attendant to "maximize shareholder value" is accurate but offers no guidance on day-to-day choices`

Compression guard:

The new card does not promote persuasion polish, primal-brain tactics, or story craft as a standalone affordance. It requires a concrete receiver action, decision, or day-to-day choice. It also blocks using clearer signaling as proof of hidden capability when costly unstaged proof is needed.

### `game-theory-payoffs.adverse-response-floor-test`

Why split:

The existing `game-theory-payoffs.counterparty-response-payoff-map` maps players, moves, information, and decisive branches. PR77 added `credible-sequencing-commitment-device` for game-changing commitments, threats, promises, and forcing moves.

The source also supports a third transaction: compare strategies by survivable floor when the opponent's strongest plausible adverse response lands.

That changes receiver behavior:

- payoff-map card: “Which response changes the value of the move?”
- credibility card: “Is the game-changing move believable?”
- floor card: “Should we avoid, exit, continue, or redesign because the adverse response floor is unacceptable?”

Source custody anchors include:

- `Game theorists use constructs like minmax (choosing an outcome that maximizes your minimum gain) and maxmin (choosing an outcome that minimizes your maximum loss) to define robust strategies.`
- `Explicitly calculate strategies that minimize the maximum loss or maximize the minimum gain.`
- `use game theory to work through potential exit strategies and assess long-term outcomes.`
- `If the worst-case scenario occurs (the opponent chooses their best strategy against our best strategy), is the outcome bad enough to justify avoiding this game altogether?`
- `If the opponent's strongest adverse response lands, is the downside still survivable?`

Compression guard:

The card requires a plausible adversarial response. It is not a generic fear, tail-risk, risk-assessment, or expected-value card. It should not make every strategy packet worst-case dominated.

### `nash-equilibrium.dominant-strategy-mechanism-design`

Why split:

The existing `nash-equilibrium.stable-best-response-map` asks whether a stable response pattern is reachable and desirable. The source also supports a different mechanism-design move: change the rules so actors do not need strategic sophistication because the desired behavior becomes their best move regardless of what others do.

That changes receiver behavior:

- stable map card: “Can this stable pattern be found, sustained, and judged separately from goodness?”
- rule-design card: “Can we design the game so the desired behavior is individually rational?”

Source custody anchors include:

- `aiming to be so strategic when designing a game that the players **don’t have to be strategic** when they play it.`
- `creating a *dominant strategy*, which is a player's best move regardless of what others are thinking or doing.`
- `the dominant strategy is simply to bid what the item is worth to you`
- `where the **selfish motives of three parties** (advertiser, user, and Google) are harnessed by an algorithm`
- `resulting in the most productive interaction without a single controller.`
- `Works when incentives are visible but alignment is not guaranteed`

Compression guard:

The card does not promote formal mechanism-design math, all auction design, or clever rules as automatically good. It requires actors, desired behavior, payoff rule, per-player incentive compatibility, and side-effect constraints.

## Rejected Expansion Notes

The following records remained compressed after full or read-only source review:

| Model | Verdict |
| --- | --- |
| `incentives` | Already has payoff-field mapping and task-fit reward design. Social commitment material stays inside second-order reward design. |
| `principal-agent-problem` | Delegated alignment drift audit already covers role clarity, dashboards, hidden performance, blame vs design, and wicked-problem rejection. |
| `moral-hazard` | Social accountability and transparency are treatment context only when tied to transferred downside or hidden effort. |
| `adverse-selection` | Source is proxy-derived and should stay narrow: hidden type plus self-selection before commitment. |
| `information-asymmetry` | Already split where the social/authority/risk transaction matters. Exploitative persuasion remains deferred/absence-railed. |
| `prisoners-dilemma` | Defection, trust, enforcement, repeated interaction, framing, and cooperative repair are already one coherent transaction. |
| `batna` | Source explicitly lacks full BATNA doctrine; keep one medium-confidence walk-away test. |
| `international-negotiation-and-diplomacy-models` | Substance, signaling, stakeholders, relationship acceptance, and durable settlement are one compressed settlement transaction. |
| `social-proof` | Existing split between external proof-source validity and internal consensus contagion is correct. |
| `authority-bias` | Domain-bound deference audit already covers expertise, transfer boundary, reasoning chain, override evidence, and dissent checks. |
| `reciprocity-principle` | Value-first trust and obligation-pressure guard remain one transaction. |
| `liking-principle` | Warmth/receptivity with substance check remains one transaction. |
| `psychological-safety` | Withheld-signal surfacing and candor-to-correction are already the right two-way split. |
| `understanding-motivations` | Hidden-driver hypothesis plus implementation-path check remains one transaction. |
| `non-violent-communication` | Observation/need/request clarification remains one transaction. |

## Compiled v46 Signals

Compiled output:

- `data/compiled/model_affordances/affordances_v46.json`
- `data/compiled/model_affordances/quality_report_v46.md`

Metadata:

- Records: `222`
- Affordances: `287`
- Absence records: `555`
- New affordances vs v45: `3`
- New absences vs v45: `0`
- Schema validation failures: `0`
- Source quote rejections: `0`

The artifact remains `draft_review_only`.

## Runtime Boundary

No live runtime pickup is introduced.

Guard checked:

- no `affordances_v46` or `model_affordances_v46` references were added to live runtime paths;
- no `/lolla` behavior changes;
- no prompt, renderer, packet, lane adapter, or final-answer behavior changes.

This continues the PR55 posture: improve source-backed substrate quality first, then stress packet shape before any runtime use.

## Follow-Up Questions For Packet Stress

Before runtime pickup, packet review should test:

1. Can the receiver distinguish `signaling.costly-proof-of-intent-test` from `signaling.create-actionable-coordination-signal` under compact rendering?
2. Does `game-theory-payoffs.adverse-response-floor-test` improve adversarial decisions without making all strategy advice overly defensive?
3. Can `nash-equilibrium.dominant-strategy-mechanism-design` stay distinct from generic incentives and from stable equilibrium prediction?
4. Do broad social cards such as authority, social proof, reciprocity, and liking stay subordinate to evidence and transaction identity?
5. Does the future decoder ledger have enough affordance identity to record used, rejected, deferred, or merged decisions?

## Bottom Line

v46 adds three carefully bounded affordance identities:

- signal-as-proof vs signal-as-actionable-coordination;
- payoff-map vs adverse-response floor;
- stable equilibrium prediction vs dominant-strategy rule design.

This is the kind of enrichment the corpus needs at this stage: higher fidelity where the source supports a distinct downstream action, and disciplined compression everywhere else.
