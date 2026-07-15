# Contributing to Lolla

Lolla is in an evidence-gated experimental stage. Contributions are welcome,
but a pull request does not authorize a provider call, a private-archive scan,
runtime integration, or revival of a retired architecture.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md),
[the Product Constitution](docs/conversation-understanding/lolla-product-constitution-v5.md),
and [AGENTS.md](AGENTS.md) before changing architecture or claims.

## Useful contributions now

- correct a mismatch between reachable code, documentation, and lifecycle
  status;
- improve deterministic custody, privacy, missingness, replay, or validation;
- make a completed artifact easier to inspect without overstating meaning;
- report a reproducible live-skill failure with exact environment and artifact
  status;
- propose a human evidence gate with one falsifiable product question;
- identify a real user job that can be tested with explicit consent and narrow
  scope.

## Work that needs a separate founder decision

- any paid or provider-facing experiment;
- private archive access or real-conversation review;
- new semantic readers or automatic Decision Work supply;
- R4/R5 continuation, prompt repair, task splitting, or model comparison;
- Teacher or Observatory expansion;
- runtime, graph, or sidecar integration;
- historical branch deletion, PR closure, or large-artifact migration;
- claims of product usefulness, production readiness, or better decisions.

## Evidence language

Label evidence as one of:

- development fixture;
- simulated conversation;
- provider output;
- human source-first semantic judgment;
- local structural/mechanical result;
- consented real-user evidence;
- market evidence.

Do not use test count, strict JSON, clean receipts, or provider completion as a
quality score. Preserve disagreement and non-scalar findings.

## Pull request shape

Keep changes narrow and state:

1. the falsifiable question or maintenance defect;
2. the lifecycle scope touched;
3. what changed and what did not;
4. provider calls and exact cost, including zero;
5. tests and validators run;
6. privacy and secret handling;
7. what remains unknown;
8. the next decision, if any.

Preserve unrelated work in dirty worktrees. Use isolated worktrees for
publication or broad gardening. Stage explicit paths and avoid destructive Git
commands.

## Provider and secret boundary

Provider calls require explicit authorization tied to a frozen contract, call
maximum, and USD ceiling. “Continue,” a green test, or an existing runner is
not authorization.

Never print or commit `.env` values. Use the documented external credential
locations. Store only safe route policy, response identity, usage, cost,
hashes, and redactions.

## Verification

Run the smallest relevant checks while iterating, then the public-handoff and
full repository gates before a merge-ready handoff:

```bash
PYTHONPATH=. python3 scripts/evals/validate_constitution_stage0_addendum_register.py \
  --register docs/evals/lolla-constitution-stage0-addendum-register-v1.json
PYTHONPATH=. python3 scripts/evals/validate_stage0_public_handoff.py
PYTHONPATH=. pytest -q tests/test_constitution_stage0_addendum_register.py \
  tests/test_stage0_public_handoff.py
PYTHONPATH=. pytest -q
git diff --check
```

Also parse changed JSON, compile changed Python, resolve changed local Markdown
links, scan added material for secret-shaped values, and preserve frozen
evidence hashes.

## Human authority

Lolla introduces and records pressure. It does not own the decision. Do not
turn a graph candidate, model output, receipt, sidecar, or interface into action
authority.
