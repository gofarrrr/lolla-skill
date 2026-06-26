# Lolla: A Reasoning Audit Layer for AI Agents

Last updated: 2026-06-26

## The Short Version

Lolla is a reasoning audit layer for AI agents and serious AI conversations.

It takes a multi-turn advisory exchange, tests the answer against structured mental-model pressure and traceable evidence, then returns a revised position, a clean memo, a machine-readable run result, and an inspectable local audit trail.

Why does that matter?

Because the dangerous AI answer is often not obviously wrong. It is fluent, useful, and slightly too settled. Lolla is built for that moment.

The point is not to make the answer longer. The point is to make the answer harder to trust blindly, and easier to inspect when the stakes justify inspection.

## The Moment Lolla Is Built For

Imagine a founder asks an AI whether to fire an executive.

Or a manager asks whether to report a serious internal problem.

Or a product team asks whether to ship a risky feature.

The model gives a thoughtful answer. It names tradeoffs. It sounds humane. It seems to understand the stakes. Maybe it even gives a numbered plan.

That is exactly when the problem starts.

Not because the answer is necessarily bad. Many AI answers are useful. The problem is that fluency creates borrowed certainty. A model can sound balanced while carrying forward a hidden frame from the user, skipping a reversal condition, treating one scenario as decisive, or smoothing over the exact risk that should have slowed the decision down.

Humans do this too. We fall in love with the first clean story. We prefer the answer that makes the mess feel manageable. The difference is that modern AI can produce clean stories at industrial speed, in perfect tone, across every domain.

Lolla asks: before this answer becomes advice, what should push back on it?

## What Lolla Does

Lolla runs after an AI conversation has already produced advice, a strategy, a recommendation, or a plan.

It captures the conversation, extracts the decision structure, runs a four-lane reasoning audit, forces the agent to reconsider the original answer, then saves the result as a memo and local audit record.

The output is not a second generic opinion. It is a structured reconsideration:

- What still holds.
- What should be taken back or set aside.
- What actually changed in the advice.
- What questions still require human judgment.
- What artifacts prove the run was complete, partial, degraded, or incomplete.

The core product is the improved reasoning. The machinery exists so that improvement is not just vibes.

The current product loop is deliberately concrete:

1. Call Lolla on a serious conversation.
2. Read the revised answer and memo.
3. Open the local Observatory.
4. Inspect whether the run was healthy, partial, degraded, or incomplete.
5. Check the custody artifacts before deciding how much to trust the result.

That may sound prosaic. It is also the difference between "the model sounded better on the second try" and "we can see what happened."

## How It Works, In Plain English

Lolla has a simple operating idea:

Use LLMs where language judgment is needed. Use deterministic structure where consistency, custody, and traceability matter.

In the current skill, a run works like this.

### 1. It Captures The Conversation

Lolla starts from the actual exchange: the user's words, the assistant's answer, the constraints, the changes in position, and the unresolved concerns.

This matters because advice does not live in the final answer alone. It lives in the conversation. The user may have mentioned a constraint in turn 2 that the answer forgot by turn 8. The assistant may have accepted the user's frame without noticing. A dropped thread can be more important than a polished paragraph.

The raw conversation remains the canonical source. Extracted summaries are treated as derived views, not as truth.

### 2. It Extracts The Decision Structure

The system identifies:

- the decision situation,
- the live constraints,
- the current recommendation,
- the user's original framing,
- reasoning passages from the assistant,
- and threads that were raised but not resolved.

Quote handling is intentionally strict. If a reasoning passage is supposed to be a quote, it has to appear in the transcript. Paraphrase cannot quietly masquerade as evidence.

This is one of the quiet but important design choices. A reasoning audit that cannot trace its evidence is just another fluent answer.

### 3. It Runs Four Independent Audit Lanes

Lolla does not ask one model to "be critical."

It splits the audit into four different checks:

1. Structural pressure: what cognitive tendency or reasoning failure pattern may be distorting the answer?
2. Model companion: what mental models are already being used, violated, or underused?
3. Frame pressure: what did the question assume before the answer began?
4. Structural coverage: what decision territory was never entered at all?

Each lane has a different job. One challenges weak reasoning. One enriches reasoning with relevant models. One tests the frame. One asks what the answer did not cover.

That separation matters. A single critic prompt tends to collapse into commentary. Lolla tries to keep different kinds of pressure from contaminating each other.

### 4. It Routes Through A Curated Knowledge Substrate

The current system routes through:

- 222 curated mental models,
- 25 Munger-style cognitive tendencies,
- curated tendency-to-model bindings,
- relationship edges between models,
- optional embedding recall,
- and source-backed V60 affordance and absence records.

That is a mouthful, so here is the simpler version:

Lolla has a library of reasoning patterns and failure modes. When it sees a structural weakness, it does not merely say "consider the risks." It tries to route that weakness to the specific counter-pressure that should challenge it.

If the answer closed on a recommendation without naming what evidence would reverse it, the useful pressure is not more prose. It is a reversal condition. If the user framed the situation as "A or B" but the real issue is "what experiment would reduce irreversibility?", the useful pressure is not a better answer to A vs. B. It is a different question.

This is the part that makes Lolla different from ordinary prompting. The LLM reads the messy language. The deterministic system preserves the routes, candidates, provenance, and custody.

### 5. It Forces A Real Reconsideration

After the audit, the agent has to revise its own answer.

Not "here are the audit findings." Not "there are pros and cons." The agent must say:

- what survived,
- what it would take back or set aside,
- and what actually shifted.

This structure is small, but it is doing real work. It prevents the agent from pretending the original answer was all wrong. It also prevents the opposite failure, where the audit is acknowledged politely and nothing changes.

The best Lolla output feels like a good second read from someone who is willing to say: "The core advice still holds, but I overclaimed here, missed this gate, and the sequence should change."

### 6. It Leaves An Inspectable Trail

A completed run produces:

- the revised answer,
- a portable memo,
- `agent_result.json`, a compact machine-readable result for callers,
- `reasoning_trace.json`, a local custody manifest with artifact hashes and trace metadata,
- `evaluation.json`, a deterministic run-readiness receipt,
- `capture_adequacy` metadata, a compact summary of what conversation shape was captured or omitted,
- local Observatory views,
- run health,
- metadata-only risk mode,
- optional control-plane sidecars when supplied,
- usage and cost telemetry,
- run-event history,
- model-call traces,
- private consideration ledgers,
- graph-survival reports,
- and a local archive under `~/.local/share/lolla/runs/`.

This is not cosmetic. If an audit system cannot tell you what it saw, what it used, what failed, and what was only partial, it can create the same false confidence it was supposed to fight.

Lolla tries to make the process part of the product.

The current custody loop makes that inspection more explicit. Current and archived runs are not only files on disk; the Observatory can expose run-custody sidecars for the active `lolla-audit` run and for selected local-history runs. Immediately after a run, the user can inspect active-run artifacts. If the user selects an older run from local history, the interface shows whether core artifacts for that selected run exist:

- `agent_result.json`,
- `reasoning_trace.json`,
- `run_events.json`,
- `memo.md`,
- `graph_survival_report.*`,
- `evaluation.json`.

That matters because "local history exists" is not enough, and "the active run just finished" is not enough either. The user needs to know whether the run they are looking at is actually inspectable, and whether the displayed artifacts belong to that run rather than a stale active or archived neighbor.

## Why This Becomes More Necessary As AI Gets Better

The case for Lolla is not "current models are dumb."

The case is almost the opposite.

Models are becoming more capable, more agentic, and more persuasive. They are moving from answering questions to taking actions. OpenAI's Responses API and Agents SDK are built around models using tools, tracing, and evaluations. ChatGPT agent can reason and act through a computer-like environment. Anthropic's agent guidance draws the same broad distinction: some systems follow predefined workflows, while more agentic systems dynamically direct their own tool use.

That direction is powerful. It also changes the risk.

When a chatbot gives a weak answer, the damage is often bounded by the user's next decision. When an agent gives a weak answer and can call tools, write files, contact people, buy things, update systems, or steer a workflow, reasoning quality becomes operational quality.

The next problem is not just "did the model hallucinate a fact?"

It is:

- Did the model accept the user's frame too easily?
- Did it overfit to the most vivid constraint?
- Did it recommend action without a stop rule?
- Did it miss the stakeholder who pays the cost?
- Did it create a plan whose failure conditions are invisible until too late?
- Did it sound careful while avoiding the hard part?

The 2026 Stanford AI Index describes the broader pattern well: capability is accelerating, adoption is spreading, and the ability to measure and govern AI is not keeping pace. The same report points to the jagged frontier: models can be extraordinary on some hard benchmarks while still failing in ordinary-looking places.

This is why "the next model will fix it" is not a sufficient strategy.

Better models reduce some errors. They also make the remaining errors harder to see. A weak answer with bad prose invites skepticism. A weak answer with excellent prose can become a decision.

There is an even larger version of the same problem. In "Virtual Agent Economies," Tomašev et al. argue that autonomous agents may create a new economic layer where agents coordinate and transact faster than direct human oversight can follow. Their answer is not "add a human reviewer to every action." That cannot scale. They argue for intentional design: sandbox boundaries, machine-speed oversight, containment, legal accountability, and standardized audit trails. Lolla is much narrower, but it fits that direction. It is a reasoning audit component for the moment before advice, plans, or agent actions become operational.

## The Research Signal Behind The Need

There are several outside signals that point toward the same category of need.

First, sycophancy is not a personality quirk. Anthropic's research on sycophancy found that RLHF-trained assistants can favor responses matching user beliefs over more truthful responses. Stanford's 2026 work on interpersonal advice found that major AI models affirmed users more often than humans did, including in harmful or illegal scenarios, and users often preferred the agreeable responses.

That matters for Lolla because serious decisions often arrive with emotional gravity. The user is not always asking for truth. Sometimes they are asking for permission. A good reasoning audit has to catch the places where the assistant inherited that desire.

Second, explanations are not the same as faithful reasoning. Research on chain-of-thought faithfulness has shown that models can produce plausible explanations that do not reflect the true reason for the answer. So we should be cautious about treating a well-explained AI answer as automatically well-reasoned.

Third, agent systems need observability. OpenAI's agent tooling emphasizes tracing and evaluations. NIST's AI Risk Management Framework is organized around managing trustworthy AI through design, development, use, and evaluation. OWASP's 2025 GenAI Top 10 includes risks like prompt injection, excessive agency, vector and embedding weaknesses, and misinformation. Those are not the same problem Lolla solves, but they point in the same direction: as systems become agentic, "just trust the model" is not an architecture.

Lolla sits in a narrower slot:

It is not a full safety system. It is not a cybersecurity control. It is not a legal, medical, or financial expert.

It is a reasoning-quality gate.

More precisely, Lolla is a reasoning-audit harness:

- LLMs do semantic judgment where language judgment is needed.
- Deterministic code handles routing, validation, artifact custody, health, telemetry, archive, and replay.
- The Observatory exposes the instrument panel.
- `agent_result.json` gives callers a compact handoff without forcing them to parse the memo.

That boundary is important. Lolla should be able to connect to guardrails, approval systems, sandboxes, proxies, trace stores, and eval suites. It should not pretend to replace them.

## Who Lolla Is For

Lolla is most useful where the answer is consequential enough that a second pass is worth the cost.

It is useful for AI power users who already use models for strategy, career decisions, product decisions, negotiation, writing important memos, or thinking through ambiguous tradeoffs.

It is useful for founders and operators who use AI as a thinking partner, especially when the model's answer could influence hiring, firing, fundraising, product direction, vendor selection, litigation posture, or organizational design.

It is useful for teams building agents. An agent that can plan, call tools, and act on behalf of a user needs a way to pause before finalizing serious recommendations. Lolla can become that pause.

It is useful for advisors, coaches, consultants, lawyers, analysts, and domain experts who want a second reader on the reasoning shape, not a replacement for their expertise.

It is useful for AI evaluation and governance teams that want artifacts: traces, memos, run health, archive records, cost, and repeated-run comparison.

It is probably not useful for simple factual Q&A, ordinary coding fixes, casual brainstorming, or tasks where deterministic tests already answer the question better than a reasoning audit.

## How Agents Should Use It

The simplest agent-facing rule is:

Call Lolla when you think you are done.

More precisely, an agent should call Lolla when all of these are true:

- The conversation produced advice, a strategy, a plan, or a recommendation.
- The advice could materially affect a person, organization, budget, relationship, legal posture, or operational workflow.
- The answer sounds settled enough that the user may act on it.
- The agent has not yet run an independent reasoning-quality check.

For agent or workflow callers, the local contract is now intentionally compact:

Input:

- conversation transcript,
- final answer or current recommendation,
- optional domain/stakes metadata,
- optional user constraints,
- optional control-plane metadata such as trace, approval, policy, sandbox, or credential references.

Output:

- `agent_result.json`,
- optional `control_result.json`,
- audit status and run health,
- strongest counter-pressure,
- revised position,
- take-backs,
- new gates or stop rules,
- unanswered user questions,
- memo,
- local trace and artifact pointers.

The agent does not have to expose all machinery to the user. The user should see the improved advice. The developer or operator should be able to inspect the machinery when something feels off.

That split is important.

Humans need a clear answer. Builders need traces. Lolla tries to serve both without dumping the instrument panel into the chat.

That contract now exists as an archive artifact. A completed modern run has a compact `lolla_agent_result.v1` result with fields like:

- run status,
- run-health summary,
- product-output health,
- live-output health,
- `caller_action`,
- main counter-pressure,
- whether the advice changed,
- take-backs,
- human questions,
- do-not-act-before items,
- artifact paths,
- cost and usage summary.

The current `caller_action` is intentionally conservative. If a run is partial, degraded, incomplete, capture-critical, or product-output unsafe, the machine-readable result should not invite an agent to use it automatically.

For external systems, Lolla can now preserve optional control-plane context through local sidecars. A caller may provide `control_input.json` with trace, action, approval, policy, sandbox, or credential references. Lolla then archives that input, adds compact references to the agent result and reasoning trace, and can generate `control_result.json` as a wrapper around `caller_action`. This is not an approval decision. It is a reasoning-audit handoff that another policy, approval, sandbox, identity, or trace system can consume.

The same principle applies to provider-boundary warnings. If a model provider returns reasoning details even though reasoning was disabled, Lolla should not shrug and call the run healthy. The current policy classifies the warning: was it only a provider-boundary violation, did it contaminate product output, did it contaminate live output, or is persistence still unknown? It stays conservative even for contained provider-boundary warnings; classification improves explanation first, not automatic approval.

The same caution applies to evaluation. The current `evaluation.json` is not a judge of whether the answer is wise. It is a deterministic receipt for the run envelope: did the expected artifacts exist, did schemas match, did the trace index the right files, did hygiene checks pass or warn, and did caller policy stay conservative where it should?

Capture adequacy follows the same philosophy. Lolla does not pretend to reconstruct omitted turns from a long conversation. Instead, it records the capture shape: whether capture was full, warning-level, or critical; how many turns were declared, captured, and omitted; which windows were kept; which windows were dropped; and whether the omission should affect trust. That matters because a perfect audit over an incomplete conversation can still be misleading. The first job is to make the missing context visible.

Risk modes are also recorded as metadata. A run can record intent such as `quick`, `standard`, `deep`, `high_stakes`, or `stability`. For now, this is not a promise that the audit behaved differently. It is a way to preserve operator or caller intent before controlled behavior changes are added later.

Across runs, Lolla can export a local review corpus. That corpus summarizes run envelopes, health, capture adequacy, evaluation status, usage/model metadata, artifact availability, and optional control-plane references. It includes blank human-review fields and review-readiness tiers, but it does not copy raw transcript or memo text, does not score advice quality, and does not use an LLM judge. Synthetic reviewers can help rehearse labels, but their outputs stay synthetic and cannot become human review without ratification.

This is the rhythm we want: first make the run legible, then make it inspectable, then make it evaluable, then make it callable by other systems.

## What Lolla Is Not

Lolla is not a truth oracle.

It does not guarantee the final answer is correct.

It is not a fact-checking engine. It audits reasoning structure. If a domain fact is wrong, Lolla may catch the reasoning consequence, but factual verification still needs separate tooling.

It is not a substitute for professional judgment. A legal, medical, financial, or safety-critical decision still belongs with qualified humans and domain-specific controls.

It is not a generic "devil's advocate" prompt. The point is not to disagree for flavor. The point is to apply structured pressure where the reasoning is fragile.

It is not trying to make AI less useful. It is trying to make useful AI less dangerously smooth.

## Why The Local Audit Trail Matters

Many AI products produce only the final answer.

That is not enough for serious use.

If an agent gives advice that later proves flawed, people will ask:

- What conversation did it audit?
- Was the conversation fully captured, or were important middle turns omitted?
- Which constraints did it capture?
- Which reasoning passages were tested?
- Which model calls ran?
- Which findings were produced?
- Which private chunks were considered, rejected, or used?
- Was the run healthy, partial, degraded, or incomplete?
- What did the final memo say?
- Can we compare this run to earlier runs?

Lolla's archive and Observatory exist for those questions.

They are not there because dashboards are fun. They are there because reasoning systems need custody. Without custody, every postmortem becomes guesswork.

## The Current Strategy: Custody First, Agents Next

This is also why the current work has prioritized the manual inspection loop before grander agent-control diagrams. It is tempting to jump straight to schemas, gates, and integrations. But if the human cannot open a local run and see what exists, what failed, and what belongs to the selected run, the agent-facing story is premature.

The near-term target is therefore:

```text
run Lolla manually
-> get a revised answer and memo
-> archive the run
-> open Observatory
-> select any archived run
-> inspect custody, health, trace, memo, and cost
-> decide what to trust
```

Because that loop is now materially in place, the same artifacts can support agent use:

```text
agent or workflow calls Lolla
-> Lolla returns agent_result.json
-> caller reads caller_action and artifact pointers
-> human or control system inspects the archive when needed
-> deterministic evaluation checks the run envelope
```

## The Current State

Today, Lolla works as a Claude Code and Codex skill.

In Claude Code, it is invoked with `/lolla`. In Codex, it can be invoked with `$lolla` or by asking to use the Lolla skill.

The current live flow:

1. Captures the conversation.
2. Records capture adequacy metadata.
3. Extracts the decision structure.
4. Runs the four audit lanes.
5. Adds private source-backed enrichment.
6. Produces a strongest-counterargument beat.
7. Forces an updated position.
8. Persists private consideration ledgers.
9. Records pressure-check state.
10. Renders a memo.
11. Opens the local Observatory.
12. Archives the run.
13. Generates `agent_result.json`.
14. Optionally generates `control_result.json` when external control input was supplied.
15. Generates `reasoning_trace.json`.
16. Generates `evaluation.json`.
17. Lets the Observatory expose selected-run custody artifacts from local history.

It is already usable. It is also still early.

The major recent shift is that Lolla is no longer only a manual skill that produces a memo. It is a local reasoning-audit harness: a run produces product output, custody artifacts, deterministic readiness checks, machine-readable handoffs, optional control-plane context, and a local review-corpus path.

What is now in place:

1. Modern archived runs are machine-readable through `agent_result.json`.
2. Risk-mode intent is recorded without pretending behavior has changed.
3. Active and archived Observatory custody artifacts are reachable.
4. `evaluation.json` checks the deterministic run envelope before any broad judge exists.
5. Capture adequacy is visible before long-conversation strategy changes.
6. Optional `control_input.json` and `control_result.json` preserve external trace/action/approval context without making Lolla the control plane.
7. Archived run envelopes can be exported into a local review corpus with human-owned labels and synthetic-review rehearsal kept separate.

This order matters. If we build agent-control language before the run is inspectable, we get architecture theater. If we make the local audit trail real first, the agent contract has something solid to point at.

What is still not claimed:

- risk modes do not yet change cost, prompts, capture strictness, Step 7 behavior, replay, or high-stakes policy,
- `evaluation.json` does not judge answer wisdom,
- the review corpus does not create gold labels by itself,
- synthetic review is rehearsal, not human review,
- Lolla does not approve actions, sandbox tools, enforce policy, or replace domain expertise,
- capture adequacy makes omissions visible, but does not yet solve decision-aware long-conversation capture.

The next natural step is not more eval-methodology polishing for its own sake. It is either to use the current review workflow on real records, or to keep improving the product/runtime loop where real users still feel friction.

## What We Want To Learn Next

The public project is an invitation.

We want people to run Lolla on real conversations and tell us where it helped, where it overreached, where it missed the obvious thing, and where the output was technically complete but not humanly useful.

We especially want feedback on:

- which decisions deserve this kind of audit,
- which outputs are most useful to humans,
- which traces are most useful to builders,
- whether the local Observatory makes a run genuinely inspectable,
- whether capture adequacy makes omitted context visible enough to trust or rerun,
- whether `agent_result.json` contains the right compact handoff for callers,
- whether `caller_action` is conservative in the right places,
- how provider-boundary warnings should affect run health,
- when the audit changes the answer in a valuable way,
- when the audit adds friction without improving judgment,
- which deterministic evaluation checks should block trust in a run,
- whether the review corpus and human-review workflow help people find real failure patterns,
- what domain-specific model packs would matter,
- and how agents should decide when to call Lolla automatically.

The long-term direction is not one monolithic product shape.

There may be:

- a shareable skill,
- an agent tool,
- a local Observatory,
- an API-level reasoning gate,
- a decision-journal layer,
- an eval corpus generator,
- and domain packs for legal, medical, engineering, investing, product, or organizational reasoning.

But the center should stay stable:

Lolla helps agents become accountable for advice after they have already sounded convincing.

## A Plain Invitation

If you build agents, run Lolla where your agent sounds most confident.

If you advise people, run it on the advice you liked too quickly.

If you work on AI governance, look less at the final memo and more at the trace: what was captured, what failed, what was considered, what was partial.

If you are skeptical, good. This project needs skeptical readers. The claim is not that Lolla solves AI reasoning. The claim is smaller and more testable:

Serious AI advice should have a second-pass reasoning audit before it becomes action.

Lolla is one working attempt at that layer.

## Sources And Further Reading

Internal project docs:

- [README](../README.md)
- [How It Works](../HOW_IT_WORKS.md)
- [Problem and Thesis](how-it-works/problem-and-thesis.md)
- [Architecture and Evolution](how-it-works/architecture-and-evolution.md)
- [Live Flow](how-it-works/live-flow.md)
- [Operations and Limits](how-it-works/operations-and-limits.md)
- [Cost and Telemetry](cost-and-telemetry.md)
- [Agent Result Contract](lolla-agent-result-contract.md)
- [Reasoning-Audit Harness PRD](lolla-reasoning-audit-harness-prd.md)
- [Agent Control Layers And Lolla Integration](agent-control-layers-and-lolla-integration.md)
- [Evaluation Methodology](lolla-evaluation-methodology.md)
- [Human Review Workflow](evals/human-review-workflow.md)
- [Observatory Archive Parity Audit](observatory-archive-parity-audit.md)

External references:

- OpenAI, [New tools for building agents](https://openai.com/index/new-tools-for-building-agents/)
- OpenAI, [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/)
- OpenAI, [ChatGPT agent System Card](https://openai.com/index/chatgpt-agent-system-card/)
- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic, [Towards Understanding Sycophancy in Language Models](https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models)
- Stanford HAI, [The 2026 AI Index Report](https://hai.stanford.edu/ai-index/2026-ai-index-report)
- Stanford Report, [AI overly affirms users asking for personal advice](https://news.stanford.edu/stories/2026/03/ai-advice-sycophantic-models-research)
- Tomašev et al., [Virtual Agent Economies](https://arxiv.org/abs/2509.10147v1)
- Turpin et al., [Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388)
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- OWASP GenAI Security Project, [2025 Top 10 Risk and Mitigations for LLMs and GenAI Apps](https://genai.owasp.org/llm-top-10/)
