# Contributing to Lolla

Lolla is in an evidence-gated experimental stage. Contributions are welcome,
but a pull request does not authorize a provider call, a private-archive scan,
runtime integration, or revival of a retired architecture.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md),
[the Product Constitution](docs/conversation-understanding/lolla-product-constitution-v5.md),
and [AGENTS.md](AGENTS.md) before changing architecture or claims.

## Fresh-clone setup

The supported development baseline is Python 3.13 or newer on a POSIX shell
(macOS, Linux, or WSL). From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
PYTHONPATH=. python3 scripts/evals/validate_stage0_public_handoff.py
```

The public-handoff workflow in `.github/workflows/public-handoff.yml` repeats
the provider-free cold-start checks on GitHub. It is deliberately narrower than
the full local suite. Installing dependencies or running validators does not
make provider calls.

## Source and edit ownership

| Surface | Current owner | Change rule |
|---|---|---|
| Product/lifecycle truth | `PROJECT_STATUS.md`, Constitution v5, `docs/README.md` | Update current entrypoints; do not modernize frozen evidence. |
| Live skill behavior | `SKILL.md`, `docs/skill/STEPS.md`, `scripts/skill/`, `scripts/run_*.py`, `engine/system_b/` | Keep narration, provider, artifact, and host-reasoner contracts aligned. |
| Mental-model source | `data/mental-models/*.md` plus reviewed curation/manifests | Markdown owns available prose; reviewed curation owns authored relation meaning. |
| Published graph read | `data/knowledge_graph.json`, `data/relationship_graph.json`, `engine/system_b/published_knowledge_substrate.py` | Validate candidate equivalence; never compile or repair meaning at runtime. |
| Pressure policy | `data/curation/constitutional_pressure_policy_v1.json`, current planner wrapper, frozen compatibility serializer | Change prospectively and replay all frozen windows; do not rewrite historical policy evidence. |
| Atlas | `apps/mental-model-atlas/` plus current V2 custody result/evidence | Keep V2 custody separate from frozen V1 and from Teacher claims. |
| Completed-artifact surfaces | Decision Trail/Product Delta, Decision Work, Observatory modules and indexes | Preserve their bounded, offline, operator-directed, or read-only authority. |
| Research history | dated results, `research/`, frozen contracts and artifacts | Add a prospective version; do not rewrite a historical checkpoint. |

Use [the documentation map](docs/README.md) to load the controlling evidence for
the surface being changed. No supported source, build, test, or setup path may
depend on another checkout or a private founder archive.

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

Preserve unrelated work in dirty worktrees. Work on a narrow branch, stage
explicit paths, and avoid destructive Git commands. Another worktree is never a
source dependency; if one is used as a Git convenience, a fresh clone must
still contain every source and instruction needed to reproduce the result.

## Provider and secret boundary

Provider calls require explicit authorization tied to a frozen contract, call
maximum, and USD ceiling. “Continue,” a green test, or an existing runner is
not authorization.

Never print or commit `.env` values. Use the documented external credential
locations. Store only safe route policy, response identity, usage, cost,
hashes, and redactions.

The live skill sends captured user/assistant prose to the configured
OpenRouter route and may send derived retrieval queries to OpenAI when the
optional embedding layer is enabled. Local archives may contain sensitive
conversation prose. Provider operation and local archive custody are separate
from provider-free repository development.

## Verification

Run the smallest relevant checks while iterating, then the public-handoff and
full repository gates before a merge-ready handoff:

```bash
PYTHONPATH=. python3 scripts/evals/validate_constitution_stage0_addendum_register.py \
  --register docs/evals/lolla-constitution-stage0-addendum-register-v1.json
PYTHONPATH=. python3 scripts/evals/validate_stage0_public_handoff.py
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
PYTHONPATH=. pytest -q tests/test_constitution_stage0_addendum_register.py \
  tests/test_stage0_public_handoff.py \
  tests/test_self_contained_skill_readiness.py \
  tests/test_skill_contract.py \
  tests/test_final_receipt.py \
  tests/test_model_cost_hardening.py \
  tests/test_published_substrate_consumer_register.py
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
