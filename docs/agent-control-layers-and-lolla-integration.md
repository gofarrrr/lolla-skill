# Agent Control Layers And Lolla Integration

Status: Draft
Last updated: 2026-06-25

## Why This Exists

Lolla can run today as a skill. That is useful, but it is not the final shape.

If agents become ordinary production infrastructure, Lolla has to fit beside the other control layers companies already use: guardrails, permission systems, sandboxes, proxy gates, approval flows, identity scopes, trace stores, and eval suites.

The right question is not:

> Can Lolla replace those controls?

It cannot.

The right question is:

> Where does a reasoning audit belong in the control stack, and what contract lets other systems call it?

## Source Systems Reviewed

Representative primary-source systems:

- Brex CrabTrap: outbound HTTP/HTTPS proxy for AI agents, static rules plus LLM policy judge, PostgreSQL audit log, policy replay evals.
- OpenAI Agents SDK: input/output/tool guardrails and human-in-the-loop tool approvals.
- Claude Code: permissions, hooks, auto mode, and sandbox environments.
- LangGraph / LangChain: interrupts and human-in-the-loop approval patterns with persisted graph state.
- Invariant Guardrails: rule-based guardrailing layer between applications and MCP servers or LLM providers.
- LiteLLM Proxy: AI gateway guardrails for pre-call, post-call, tool permissions, PII/prompt-injection controls, and provider integrations.
- Guardrails AI and NVIDIA NeMo Guardrails: input/output/dialog/execution guardrails and structured validation.
- E2B, Modal, Daytona, and related sandbox providers: isolated execution environments for AI-generated code and agent actions.
- Langfuse and Braintrust: tracing, datasets, evaluations, and production/debug observability for agent workflows.
- Auth0 for AI agents and related identity systems: scoped user-delegated access to external APIs.

Primary links:

- [Brex CrabTrap](https://github.com/brexhq/CrabTrap)
- [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [OpenAI Agents SDK human-in-the-loop approvals](https://openai.github.io/openai-agents-js/guides/human-in-the-loop/)
- [Claude Code permissions](https://code.claude.com/docs/en/permissions)
- [Claude Code sandbox environments](https://code.claude.com/docs/en/sandbox-environments)
- [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangChain DeepAgents human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [Microsoft Agent Framework tool approval](https://learn.microsoft.com/en-us/agent-framework/agents/tools/tool-approval)
- [Invariant Guardrails](https://github.com/invariantlabs-ai/invariant)
- [LiteLLM Proxy guardrails](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)
- [LiteLLM tool permission guardrails](https://docs.litellm.ai/docs/guardrail_providers)
- [Guardrails AI](https://github.com/guardrails-ai/guardrails)
- [NVIDIA NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/home)
- [E2B sandboxes](https://e2b.dev/docs)
- [Modal sandboxes](https://modal.com/docs/guide/sandboxes)
- [Langfuse observability](https://langfuse.com/docs/observability/overview)
- [Braintrust agent evals](https://www.braintrust.dev/docs/best-practices/agents)
- [Auth0 tool calling and API authorization](https://auth0.com/blog/genai-tool-calling-intro/)

## Market Pattern

The market is not converging on one control.

It is converging on stacked controls at different points in the agent loop:

1. Before the model sees input.
2. While the model plans.
3. Before a tool call executes.
4. While a tool call executes.
5. Before outbound network/API traffic leaves the agent environment.
6. Before credentials or user-delegated tokens are used.
7. Before a high-impact action is finalized.
8. After the run, through trace review, replay, and evals.

Lolla belongs mainly at points 2, 7, and 8.

That is important. Lolla should not become a per-HTTP-request firewall. CrabTrap is better positioned for that. Lolla should not become an OS sandbox. E2B, Modal, Claude sandbox runtime, or a VM are better positioned for that. Lolla should not become an identity broker. Auth0-like systems are better positioned for that.

Lolla's native job is narrower:

> Before advice, plans, or agent actions become operational, test whether the reasoning frame is too smooth, too inherited, too unsupported, or missing the condition that should change action.

## The Control Stack

| Layer | Examples | What it controls | What it misses | Lolla relationship |
|---|---|---|---|---|
| Input guardrails | OpenAI input guardrails, LiteLLM pre-call guardrails, Guardrails AI, NeMo input rails | Malicious, irrelevant, unsafe, or policy-violating user input | A plausible but weak recommendation later in the conversation | Lolla can use their risk labels as trigger metadata. |
| Output guardrails | OpenAI output guardrails, Guardrails AI, NeMo output rails, LiteLLM post-call guardrails | Toxicity, format, PII, policy violations, structured output validity | Whether the answer accepted the wrong frame or omitted a stop rule | Lolla is a deeper reasoning-quality gate, not a replacement output filter. |
| Tool permission hooks | Claude Code permissions/hooks, OpenAI tool guardrails, LiteLLM tool permission guardrail | Which tools can be called and with what arguments | Whether the agent should be pursuing this plan at all | Lolla can run before high-impact tool approvals as a reasoning gate. |
| Human approval / interrupts | OpenAI HITL, Microsoft tool approvals, LangGraph interrupts, HumanLayer-style approvals | Pause, approve, reject, modify, resume | Human approval fatigue; reviewer may not know the reasoning risk | Lolla can generate approval context: "approve only after these questions/gates." |
| Outbound proxy | CrabTrap | HTTP/HTTPS egress, URL/method rules, LLM policy judge, audit log | Non-HTTP actions; response filtering; human approval; upstream reasoning | Lolla can consume proxy traces and attach reasoning-audit results to risky action chains. |
| MCP / tool middleware | Invariant Guardrails, MCP proxies, LiteLLM MCP/tool controls | Cross-tool flows, MCP calls, provider/tool policy | Broader strategic reasoning quality | Lolla can become a pre-action or post-run evaluator for multi-tool plans. |
| Runtime sandbox | Claude sandbox/runtime, E2B, Modal, Daytona, VMs/dev containers | Filesystem, process, network, resource isolation | Bad advice inside a safe box | Lolla complements isolation by auditing intent and decision quality. |
| Identity and secrets | Auth0 for AI agents, scoped OAuth, token brokers, secret injection systems | Who the agent acts as, token scopes, credential exposure | Whether the agent should use the permission it has | Lolla can require narrower scopes or user confirmation before sensitive delegated actions. |
| Observability and evals | Langfuse, Braintrust, OpenTelemetry GenAI, CrabTrap audit logs | Traces, spans, costs, outputs, replay, eval datasets | The domain-specific failure taxonomy unless humans build it | Lolla should export/import trace IDs and produce eval-ready artifacts. |

## Lessons From CrabTrap

CrabTrap's architecture is useful because it is specific.

It does not say "make the agent safer" in the abstract. It inserts a forward proxy between the agent and the internet:

1. Agent sends outbound HTTP/HTTPS through proxy.
2. Proxy terminates TLS.
3. Static URL/method rules run first.
4. If no static rule matches, an LLM judge evaluates the request against a natural-language policy.
5. Request is allowed or denied.
6. Decision and traffic metadata are logged.
7. Historical logs can be replayed against policies.

The good pattern for us:

- deterministic rules before LLM judgment,
- LLM only where policy language requires interpretation,
- every decision logged,
- replay/eval over historical decisions,
- admin UI for policy and audit review.

The boundary to respect:

- CrabTrap handles egress safety.
- Lolla handles reasoning quality.

For example, if an agent wants to send an email to a customer:

- CrabTrap can ask: "Is this outbound request allowed by policy?"
- OpenAI/LangGraph/HumanLayer-style approval can ask: "Should a human approve this send_email call?"
- Lolla can ask: "Is the reasoning behind sending this email sound, or did the agent accept a frame, skip a stakeholder, or fail to define a stop condition?"

Those are different questions.

## Lolla Integration Modes

### Mode 1: Pre-Final-Answer Gate

When:

- Agent is about to return serious advice, a plan, a recommendation, or a decision memo.

Input:

- conversation transcript,
- current answer,
- relevant trace IDs,
- risk metadata.

Output:

- revised answer,
- `caller_action`,
- do-not-act-before gates,
- human questions,
- artifact pointers.

This is the closest to today's `$lolla` skill flow.

### Mode 2: Pre-Action Reasoning Gate

When:

- Agent is about to execute a high-impact tool call or action.

Examples:

- send external email,
- change production setting,
- submit purchase/refund/payment,
- merge/deploy code,
- delete data,
- contact a third party,
- file or report something with legal/HR/compliance weight.

Input:

- proposed action,
- action arguments,
- chain of reasoning or recent trace summary,
- user objective,
- policy/approval context,
- tool risk class.

Output:

- proceed,
- ask user first,
- require human approval,
- rerun deeper,
- block because reasoning is incomplete or unsupported.

This is where Lolla could connect to OpenAI `needsApproval`, LangGraph interrupts, Microsoft approval-required tools, or HumanLayer-style approval channels.

### Mode 3: Post-Run Incident / Error Analysis

When:

- An agent run produced a bad outcome, denied request, human rejection, or degraded run.

Input:

- full trace,
- tool calls,
- denial/approval records,
- final output,
- user feedback.

Output:

- first upstream reasoning failure,
- failure taxonomy label,
- whether the control layer caught or missed it,
- eval fixture suggestion.

This connects Lolla to CrabTrap audit logs, Langfuse traces, Braintrust datasets, and local archived runs.

### Mode 4: Corpus / Regression Eval

When:

- We are testing a new Lolla prompt, skill step, model default, V60 selection behavior, or integration contract.

Input:

- archived trace corpus,
- expected failure labels,
- deterministic artifact checks,
- calibrated subjective judges.

Output:

- regressions,
- stability summary,
- smoothness-bias judge failures,
- before/after answer deltas.

This connects to the eval methodology.

## Implemented Interop Contract v0

Lolla can now preserve external control-plane metadata without depending on any
one vendor. This is a local archive contract, not a hosted API and not an
enforcement layer.

Input sidecar:

- Write `/tmp/lolla_<run_id>_control_input.json` before archive.
- The archive preserves it as `{case}/{run}/control_input.json`.
- Ordinary `$lolla` runs do not need this file.

Example `lolla_control_input.v1`:

```json
{
  "schema_version": "lolla_control_input.v1",
  "mode": "pre_action_reasoning_gate",
  "conversation": {
    "transcript_path": "/path/to/transcript.txt",
    "trace_id": "trace_123",
    "session_id": "session_456"
  },
  "agent": {
    "name": "support_agent",
    "version": "2026-06-24",
    "framework": "openai_agents_sdk"
  },
  "proposed_action": {
    "tool_name": "send_email",
    "arguments": {
      "to": "customer@example.com",
      "subject": "Account closure"
    },
    "risk_class": "external_side_effect"
  },
  "control_context": {
    "approval_id": "approval_789",
    "policy_engine": "crabtrap",
    "policy_decision": "needs_review",
    "sandbox_id": "sandbox_abc",
    "credential_scope": "gmail.send",
    "tool_call_ids": ["tool_call_1"]
  }
}
```

Generated output sidecar:

- When `control_input.json` is present, archive generation writes
  `{case}/{run}/control_result.json`.
- It also writes `/tmp/lolla_<run_id>_control_result.json` for caller
  convenience.
- `agent_result.json` receives a compact `control_context` summary.
- `reasoning_trace.json` indexes `control_input.json` and
  `control_result.json`.

Example `lolla_control_result.v1`:

```json
{
  "schema_version": "lolla_control_result.v1",
  "run_id": "20260624T000000Z_example",
  "control_mode": "pre_action_reasoning_gate",
  "caller_action": "ask_user_first",
  "approval_outcome": "require_human_approval",
  "reasoning_risk": "The action follows a plausible plan, but the agent has not tested the stakeholder cost or reversal condition.",
  "do_not_act_before": [
    "Confirm the user wants the email sent externally.",
    "Name what evidence would make this action inappropriate."
  ],
  "human_approval_context": {
    "summary": "Approve only if the user confirms external send and accepts the stated risk.",
    "suggested_rejection_message": "Do not send yet. Ask the user to confirm external recipient and consequence."
  },
  "artifact_paths": {
    "agent_result": "/tmp/lolla_agent_result.json",
    "memo": "/tmp/lolla_memo.md",
    "archive": "/Users/example/.local/share/lolla/runs/case/run"
  },
  "boundary": {
    "lolla_approves_actions": false,
    "lolla_replaces_policy_engine": false,
    "lolla_replaces_sandbox": false,
    "lolla_replaces_identity_scope": false
  }
}
```

This is additive to `lolla_agent_result.v1`, not a replacement for it. Proposed
action argument values are preserved in `control_input.json`; compact public
summaries expose argument keys only.

`caller_action` maps to control-plane outcome language as follows:

| `caller_action` | Control-plane outcome |
|---|---|
| `use_revised_answer` | `proceed_with_external_policy` |
| `ask_user_first` | `require_human_approval` |
| `rerun_deeper` | `rerun_deeper` |
| `do_not_use_run_degraded` | `block_reasoning_incomplete` |
| `unsupported_high_stakes_domain` | `block_unsupported_stakes` |

## Design Implications For Lolla

### 1. Keep The Skill, But Design The Contract

The skill is the human interface. The contract is the future system interface.

Near-term:

- `$lolla` remains the main user flow.
- `agent_result.json` is the first bridge: a compact archived
  `lolla_agent_result.v1` handoff with `caller_action`, run health, product
  summaries, and artifact pointers.
- `control_input.json` and `control_result.json` are optional sidecars for
  trace/action/approval metadata.

Longer-term:

- Lolla can be called by an agent framework, approval system, proxy, or trace pipeline.

### 2. Do Not Put Lolla Inline On Every Request

CrabTrap can judge every outbound HTTP request. Lolla should not.

Lolla is slower, deeper, and more expensive. It should be triggered at decision boundaries:

- final serious recommendation,
- high-impact action,
- human approval,
- policy denial,
- incident review,
- release/eval regression.

### 3. Keep Trace Reference Fields Compact

The v0 sidecar and summaries carry:

- `external_trace_id`,
- `external_span_ids`,
- `agent_run_id`,
- `tool_call_ids`,
- `approval_id`,
- `policy_engine`,
- `policy_decision`,
- `sandbox_id`,
- `credential_scope`.

These fields make later interop possible without copying raw tool arguments
into agent-facing summaries.

### 4. Make `caller_action` Useful For Control Systems

The current PRD's `caller_action` enum is the right bridge:

- `use_revised_answer`
- `ask_user_first`
- `rerun_deeper`
- `do_not_use_run_degraded`
- `unsupported_high_stakes_domain`

For pre-action use, `control_result.json` maps the enum to approval-system
language without adding a second source of truth.

### 5. Export To Eval And Observability Tools

Lolla should not force every team to use its Observatory only.

Future adapters should make it possible to:

- export Lolla runs as JSONL,
- attach Lolla results to Langfuse or Braintrust traces,
- use OpenTelemetry trace/span IDs where available,
- replay archived runs against changed Lolla versions,
- ingest CrabTrap audit entries as trace context.

## What This Means For The PRD

Add one roadmap item:

> Control-plane integration contract.

Current v0 acceptance:

- Lolla can receive optional external trace/control metadata.
- `agent_result.json` includes external trace references when supplied.
- A pre-action gate mode is represented in `control_input.json` /
  `control_result.json` without changing audit behavior.
- `caller_action` maps cleanly to approval systems.
- Lolla docs explain how it complements, not replaces, proxies, sandboxes, and guardrails.

## Strategic Positioning

The positioning should be:

> CrabTrap asks whether the outbound request is allowed.
> Sandboxes limit what damage execution can do.
> Approval systems pause high-impact tools.
> Observability tools record what happened.
> Lolla asks whether the reasoning that led to the answer or action deserves trust.

That is a real slot in the stack.

It is not a security layer by itself. It is a reasoning-quality layer that can feed security, approval, and evaluation systems.
