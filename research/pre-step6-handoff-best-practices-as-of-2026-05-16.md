# Pre-Step-6 Handoff Best Practices As Of 2026-05-16

Date: 2026-05-16

Status: research note only. This does not change runtime behavior, `SKILL.md`,
`HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the canonical
knowledge base, or public output.

Related local receipts:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-comparison-subagent-readout-2026-05-16.md
research/pre-step6-comparison-aggregate-readout-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
```

## Verdict

Do not implement true agent handoff for the Pre-Step-6 path.

Use bounded worker calls as subordinate tools only when they beat a strong
Step-6 baseline. Step 6 must remain the manager and final reasoner.

The immediate best-practice interpretation for Lolla is:

```text
Step 6 owns final answer
  <- optional bounded workers as tools
  <- each worker receives a small validated workpack
  <- each worker returns a compact reasoning_artifact.v1
  <- deterministic code validates schema, caps, provenance, and source grounding
  <- reasoning_bundle.v1 is optional and must beat raw artifacts in evals
```

The same-day subagent comparison found that `reasoning_bundle.v1` was easier to
audit, but did not materially improve final answer quality over careful raw
`reasoning_artifact.v1` consumption. Under the standing tie rule, raw artifacts
win.

## Why This Note Exists

The first manual comparison made the indexed bundle look too good:

```text
manual pass: bundle wins 3/3
subagent pass: raw artifacts win 3/3 by tie/simpler-path rule
```

That is exactly the kind of uncomfortable evidence this research branch is for.
Before building machinery, we checked current handoff and context-engineering
practice as of 2026-05-16.

## Terms

Use these terms carefully:

- `true handoff`: one agent transfers user-facing control to another agent.
- `manager-worker`: a lead agent delegates bounded subtasks and synthesizes the
  result.
- `worker-as-tool`: a worker is invoked for a bounded artifact; it never owns
  the user conversation or the final answer.
- `artifact handoff`: an intermediate written object passed between reasoning
  stages.
- `context handoff`: the curated visible context given to a model at the next
  step.
- `state handoff`: machine-readable state stored outside the model-visible
  prompt.

For Lolla, Pre-Step-6 workers should be `worker-as-tool`, not true handoff.

## Source Scan

### OpenAI Agents SDK

OpenAI's handoff docs define handoffs as delegation of part of a conversation
to a specialist agent. The same page warns that if the specialist should stay
behind the original agent, use agents as tools instead. The docs also support
small structured handoff metadata, per-handoff input filters, and enabled/disabled
handoffs.

Lolla implication:

```text
Step 6 should not hand off conversation control.
Workers should stay behind Step 6 as bounded tool-like calls.
If a worker is invoked, pass a small structured payload and filtered context.
```

Sources:

- OpenAI Agents SDK handoffs: https://openai.github.io/openai-agents-js/guides/handoffs
- OpenAI Agents SDK orchestration: https://openai.github.io/openai-agents-js/guides/multi-agent/
- OpenAI Agents SDK context management: https://openai.github.io/openai-agents-js/guides/context/
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-js/guides/tracing/

### Anthropic Agent And Context Guidance

Anthropic's "Building effective agents" recommends the simplest solution that
works, adding workflow or agent complexity only when it demonstrably improves
outcomes. It also distinguishes workflows from agents and treats extra autonomy
as a cost, latency, and error-compounding tradeoff.

Anthropic's multi-agent research writeup describes subagents as useful because
they operate in separate context windows, explore independent directions, and
compress findings back to a lead research agent. The lead still synthesizes.

Anthropic's context-engineering note frames context engineering as the curation
of what enters the model's limited attention budget at each step. It explicitly
links multi-agent architectures to isolation of detailed search context in
subagents while a lead agent focuses on synthesis.

Lolla implication:

```text
Do not add workers because "more cognition" sounds good.
Use subagents only when parallel isolated attention is likely to pay.
Treat every worker result as compressed pressure, not transferred truth.
```

Sources:

- Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
- Multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Effective context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

### LangChain, Microsoft, Google ADK, And AutoGen

LangChain describes handoffs as useful when sequential constraints matter, when
the new agent needs to converse directly with the user, or when the system is a
multi-stage conversational flow.

Microsoft's Agent Framework handoff pattern puts topology and guardrails with
the developer while routing decisions stay with agents. That is a useful
separation: code owns graph shape and guardrails; models make bounded routing
or response decisions.

Google ADK emphasizes serializable session state, scoped temporary state, and
shared invocation context when subagents run inside an invocation. This supports
the distinction between machine state and LLM-visible context.

AutoGen's swarm/handoff docs show agents taking turns based on handoff messages
inside shared message context. They also warn that multiple parallel handoff
tool calls can produce unexpected behavior, which is a useful reminder that
handoff edges need deterministic control.

Lolla implication:

```text
Use true handoff only for direct conversational takeover or enforced stage flow.
Keep topology, caps, admission rules, and final ownership deterministic.
Store state explicitly; do not rely on transcript pileup as state.
```

Sources:

- LangChain handoffs: https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
- Microsoft Agent Framework handoff pattern: https://devblogs.microsoft.com/agent-framework/a-tour-of-handoff-orchestration-pattern/
- Google ADK multi-agent docs: https://github.com/google/adk-docs/blob/main/docs/agents/multi-agents.md
- Google ADK state docs: https://adk.dev/sessions/state/
- AutoGen swarm handoffs: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html
- AutoGen core handoffs: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/handoffs.html

### MCP And Progressive Context

MCP client best practices warn that injecting all available tool definitions can
consume the context window before the model sees the user request. They recommend
progressive discovery once tool definitions become a meaningful context burden.
They also list subagent-based selection as one strategy, with cost tradeoffs.

Lolla implication:

```text
Do not inject all lanes, V60 chunks, artifacts, and worker notes by default.
Prefer relevance selection, small source excerpts, and progressive disclosure.
```

Source:

- MCP client best practices: https://modelcontextprotocol.io/docs/develop/clients/client-best-practices

### Recent Research Caution

The MAST failure taxonomy identifies multi-agent failure modes across system
design, inter-agent misalignment, and task verification/termination.

A 2026 single-agent vs multi-agent paper argues that when reasoning-token budgets
are held constant, single-agent systems can match or outperform multi-agent
systems on multi-hop reasoning. The paper's broader lesson is methodological:
control for compute, context, and coordination overhead before claiming
multi-agent lift.

A 2026 strong single-agent baseline paper finds that homogeneous multi-agent
workflows can often be simulated by a single agent with efficiency advantages.
A separate 2026 skills paper argues that some multi-agent modularity can be
compiled into skill selection, but warns that selection degrades as similar
skills accumulate.

The May 2026 Agent Capsules paper reports that naively injecting more context
into merged calls can degrade quality, and that execution-mode switches should
be gated on rolling output quality.

Lolla implication:

```text
The correct control is not "bundle vs no bundle."
The correct control is "bundle vs strong Step 6 with disciplined raw artifacts
under comparable context and compute."
```

Sources:

- MAST failure taxonomy: https://arxiv.org/abs/2503.13657
- Single-agent vs multi-agent under equal reasoning-token budgets: https://arxiv.org/abs/2604.02460
- Strong single-agent baseline: https://arxiv.org/abs/2601.12307
- Single-agent with skills vs multi-agent: https://arxiv.org/abs/2601.04748
- Agent Capsules: https://arxiv.org/abs/2605.00410

### Telemetry And Governance

OpenAI exposes tracing for agent runs, including handoff and guardrail events.
Apple's 2026 governance-aware telemetry paper argues that multi-agent systems
need telemetry that can enforce policy in real time, not just observe failures
afterward.

Lolla implication:

```text
Every worker boundary needs traceable input, output, schema version, source IDs,
caps, failure reason, and final-use decision.
```

Sources:

- OpenAI tracing: https://openai.github.io/openai-agents-js/guides/tracing/
- Apple governance-aware telemetry: https://machinelearning.apple.com/research/governance-aware-agent-telemetry

## Best-Practice Synthesis

Use this checklist before adding any handoff-like boundary.

### 1. Name the final owner

Every run needs one final answer owner.

For Lolla:

```text
final owner: Step 6
workers: subordinate pressure producers
bundle: optional private map, not authority
```

### 2. Choose the simplest pattern that can win

Prefer this order:

```text
single Step 6 with better context discipline
raw reasoning_artifact.v1 inputs
bounded worker-as-tool calls
optional reasoning_bundle.v1 index
true handoff only for user-facing specialist takeover
```

True handoff is the wrong default for Pre-Step-6 because no worker should take
over the conversation.

### 3. Keep handoff payloads small and explicit

The workpack should include:

```text
owner
exact worker question
admission reason
decision situation
live constraints
included artifacts
excluded artifacts
source excerpts
forbidden moves
required output shape
discard condition
```

It should not include:

```text
full transcript
all lane outputs
all V60 chunks
all previous research docs
old dossier scaffolding
public machinery prose
```

### 4. Split state from visible context

Machine state should be explicit and serializable. LLM-visible context should be
curated for the current inference.

For Lolla:

```text
deterministic state: run IDs, artifact IDs, source IDs, caps, validation status
LLM-visible context: only the brief, selected artifacts, selected excerpts, task
```

### 5. Preserve provenance

Every worker output should make it cheap for Step 6 or an audit pass to answer:

```text
What source fact grounded this?
What artifact carried it?
What was excluded?
What would relax or discard it?
What risk appears if it is forced?
What risk appears if it is ignored?
```

### 6. Do not let indexes become truth selectors

An index can reduce attention burden. It cannot decide truth.

If a bundle exists, it should say:

```text
primary pressure
supporting pressure
duplicate/lower-priority pressure
conflicts
hard boundaries
relaxation conditions
discard candidates
rethinking questions
```

It should not say:

```text
therefore answer X
this artifact is true
ignore all non-primary material
```

### 7. Measure final-answer lift, not private neatness

The indexed bundle wins only if public answer quality improves. It does not win
because the operator can audit it faster.

Primary criteria:

```text
source-grounded force survives
unsupported precision decreases
hard boundaries survive
conflicts remain visible
duplicates are demoted
quiet artifacts do not bloat the answer
public prose does not leak machinery terms
answer is at least as clear as control
```

### 8. Give every handoff edge a kill switch

Before launch, define:

```text
worker unnecessary if
worker invalid if
bundle unnecessary if
Step 6 should discard if
research path stops if
```

For the current bundle path:

```text
If careful raw artifacts tie the indexed bundle, raw artifacts win.
```

### 9. Trace the boundary, not just the final answer

Each boundary should record:

```text
input artifact IDs
source excerpt IDs
schema version
token/cost if available
validator result
output artifact ID
Step 6 use/reject/defer decision
failure or discard reason
```

## Updated Lolla Position

The Pre-Step-6 plan should be revised this way:

```text
Keep:
  docs-only first
  no product promotion
  no product-doc change
  Step 6 final arbitration
  deterministic custody and validation
  compact reasoning_artifact.v1
  strict worker admission gate

Revise:
  "Reasoning Bundle handoff" becomes optional bundle index
  "subagents default producer" becomes bounded subagent workers only when admitted
  raw reasoning_artifact.v1 consumption becomes the baseline to beat
  true handoff is explicitly out of scope for Pre-Step-6

Do not build:
  live worker orchestration
  true agent handoffs
  product-runtime bundle integration
  broad OpenRouter synthesis
```

## Recommended Next Slice

Do not build `reasoning_bundle.v1` runtime machinery yet.

Run one of these research-only paths instead:

```text
Option A: raw-artifact discipline slice
  -> define the minimal Step-6 render contract for raw reasoning_artifact.v1
  -> compare against current control on the same three fixtures

Option B: worker-admission negative tests
  -> define cases where no worker should run
  -> test whether admission gate correctly declines extra cognition

Option C: bundle rescue test
  -> use only cases with real duplicate/conflict pressure
  -> require bundle to beat careful raw artifacts in final prose
```

Preference:

```text
Option A first
```

Reason: the subagent comparison suggests the raw artifact contract may contain
most of the value without the bundle index. We should harvest that before
building more machinery.

## Current Decision

```text
no_true_handoff
step6_as_manager
bounded_workers_only
raw_artifacts_first
bundle_optional_until_eval_win
no_product_promotion
```
