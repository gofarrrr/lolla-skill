# Conversation-state extraction probe v1

Status: preflight passed; exact two extraction calls authorized once; calls not
yet executed.

This package freezes a two-case extraction-only probe. It asks whether one
probabilistic call can populate the minimal conversation-state handoff, not
whether Lolla improves an answer or whether the graph adds value.

The selected development cases exercise different thread outcomes. Case 03 is
the only reviewed resolved-thread case. Case 04 is the addressed-unresolved
case where a false `never_addressed` label previously propagated into false
downstream pressure and a possible grant benefit became a deadline.

The runner is structurally capable of two sequential OpenRouter calls, but the
CLI refuses execution without a separate one-time authorization artifact whose
contract hash matches exactly. Dry-run performs no provider I/O. Any first-call
failure stops the probe without retry; no pipeline, graph, evaluator, or
downstream answer call exists in this contract.

## What this will tell us

The probe tests one narrow question: can a probabilistic extractor populate the
minimal state packet more faithfully than the old monolithic extractor without
losing other useful information? Case 03 tests whether it can recognize a
resolved thread. Case 04 tests whether it can avoid both a false
never-addressed label and a material strengthening of source language.

It is not scored as “better writing.” Review is source-first and reports six
separate axes: position ownership, thread disposition, source strength,
constraint precision/recall, exact quote grounding, and late-turn trajectory.
There is no composite score. A pass still does not prove graph value, answer
improvement, or runtime readiness.

## Frozen execution boundary

- one structured extraction call per case;
- the same system prompt and typed response schema for both cases;
- zero automatic retries;
- stop after the first non-passing provider result;
- maximum estimated total cost of $0.02;
- raw provider content excluded from the custody artifact;
- provider `finish_reason=error` preserved as failure and never sealed;
- zero graph, pipeline, evaluator, or downstream-answer calls.

The dry run and 4,113-test non-network suite passed. The one-time authorization
is hash-bound to the exact contract in `call-authorization.json`. Any contract,
prompt, schema, or locked-code change invalidates that authorization.

## Commands

Provider-free preflight:

```bash
python3 scripts/evals/run_conversation_state_extraction_probe.py \
  --contract research/conversation-state-extraction-probe-v1-2026-07-11/contract.json \
  --dry-run
```

The authorized execution, when intentionally started, requires the repository
environment file and the separate authorization artifact:

```bash
python3 scripts/evals/run_conversation_state_extraction_probe.py \
  --contract research/conversation-state-extraction-probe-v1-2026-07-11/contract.json \
  --env-file .env \
  --authorization research/conversation-state-extraction-probe-v1-2026-07-11/call-authorization.json
```

After mechanical success, complete the generated source-review shell in the
declared source → reviewed packet → observed packet order. Sealing that review
does not authorize the graph or full pipeline:

```bash
python3 scripts/evals/run_conversation_state_extraction_probe.py \
  --contract research/conversation-state-extraction-probe-v1-2026-07-11/contract.json \
  --seal-review research/conversation-state-extraction-probe-v1-2026-07-11/run/conversation_state_probe_v1_20260711_a1/source-review-shell.json
```
