# Lolla repository guidance

This file applies to the entire repository. It is the cold-start handoff for
agents and developers. Keep it current when a development goal changes the
project boundary or the next decision.

## Product in one paragraph

Lolla is an experimental reasoning-pressure and audit system. It preserves a
rich conversation, uses LLMs to interpret its messy meaning, uses deterministic
machinery and a curated mental-model graph to introduce provenance-bearing
external pressure, asks a reasoner to reconsider that pressure, and records the
process. Lolla is designed to make another angle inspectable—not to guarantee a
better answer, certify reasoning quality, or remove human decision authority.

## Read first

Read these in order before proposing architecture or the next experiment:

1. `docs/conversation-understanding/lolla-product-constitution-v5.md` — binding
   future-development rules. Earlier constitutions are immutable historical
   evidence, not the current contract.
2. `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`
   — ground-up product and architecture assessment, including the defects R1
   and R2 repaired.
3. `plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md` — current
   ordered development sequence and decision gates.
4. `docs/conversation-understanding/lolla-r4-semantic-distinction-preparation-result-2026-07-14.md`
   — latest completed work, exact evidence, costs, unknowns, and next decision.
5. `plans/lolla-r4-semantic-distinction-plan-2026-07-14.md` and
   `docs/conversation-understanding/lolla-r4-semantic-distinction-current-practice-2026-07-14.md`
   — the completed R4 causal plan and the official-practice check behind it.
6. `README.md`, `HOW_IT_WORKS.md`, `SKILL.md`, and `docs/skill/STEPS.md` when
   changing the live skill or explaining current user-facing behavior.

Older PRDs, research branches, and historical result files remain valuable,
but do not treat their proposals as current runtime behavior. Follow the newest
explicit status and preserve frozen historical evidence.

## Binding way to think about the system

Keep this boundary visible in every design:

```text
LLMs interpret messy conversational meaning.
Deterministic code owns identity, custody, exact evidence, bounds, replay,
budgets, graph traversal, and ledgers.
The graph introduces pressure; it does not certify relevance.
The reconsidering reasoner may apply, reject, or park pressure.
The receipt proves what process occurred, not that the result is wise.
The human owns the decision and its consequences.
```

Consequences:

- Do not build keyword, turn-count, chronology, or nested deterministic gates
  to decide semantic role, relevance, materiality, relationship meaning, or
  answer quality.
- Do not let a probabilistic applicability pass silently delete bounded graph
  candidates before the reconsidering reasoner can inspect them. That is the
  Constitution-v5 product evil: probabilistic re-domestication of independent
  pressure.
- Bounded context is necessary, but compactness must not erase custody. Keep
  the complete available conversation authoritative and declare every
  processing view and omission separately.
- Preserve `complete`, `completed_zero`, `partial`, `failed`, and `missing` as
  different states. Absence of a reader result is not semantic stand-down.
- Preserve overlap and disagreement. Do not merge, rank, or vote away distinct
  provider-authored interpretations merely to make the output cleaner.
- A strict schema proves shape, not semantic correctness. A clean receipt is
  not a quality badge. Never collapse the evaluation vector into one score.
- The desired pressure may be strange, weak, or rejected. Success is not
  forcing the LLM to use it; success is making it inspectable and preserving
  the disposition.

## Working method

- Start every goal from the constitution, the current roadmap stage, and one
  falsifiable question. Prefer one causal change over an architectural bundle.
- Take initiative on provider-free implementation, fixtures, validation,
  documentation, and gardening. Do not ask the founder to approve every small
  step. Stop when a product judgment, new provider spend, or material scope
  expansion genuinely requires the founder.
- Explain progress in plain language: what we changed, why, what it showed,
  what remains unknown, cost, and the next decision. Ask one founder question
  at a time.
- Label evidence honestly: development fixture, simulated conversation,
  provider output, human source-first target, local structural result, or real-
  user evidence. Polished simulations test reliability mechanics; they do not
  prove genuine user usefulness.
- Simulated conversations should resemble difficult, ambiguous, multi-turn
  human/LLM work to the greatest practical degree. Do not use tiny polished
  dialogues as a proxy for long-conversation performance unless the tested
  claim is explicitly narrow.
- When prompt, model, schema, provider, context-window, or reasoning-envelope
  work becomes nontrivial or produces dubious results, check current official
  primary guidance and relevant maintained implementations before changing the
  architecture. Record the date, sources, adopted practices, rejected changes,
  and why. Search for known versions of persistent failures rather than
  repeatedly improvising locally.
- Prefer small, clearly delimited probabilistic jobs with explicit authority,
  source order, zero/ambiguous behavior, and local admission. Do not make the
  task small by stripping the context needed to interpret its meaning.
- Update the plan, result note, README/index, and this file when the handoff
  changes. A new machine or agent should not need chat history to resume.

## Provider, key, cost, and privacy rules

- Provider calls are never implied by “continue,” “go,” a green local test, or
  the existence of a runner. Require an explicit founder authorization tied to
  an exact frozen contract, cases, call maximum, and USD ceiling.
- Before authorization, freeze source and role hashes, a hidden source-first
  target, prompts, schemas, request previews, model/provider routing, seeds,
  output caps, cost estimate, stop rules, and the exact authorization shape.
- After authorization, make no automatic retry, semantic retry, fallback,
  response healing, premium-model substitution, evaluator call, or scope
  expansion unless the same exact authorization permits it. Preserve the first
  terminal result honestly.
- LLM judgment calls use Gemini through OpenRouter for the current R4 contract.
  The pinned operator is `google/gemini-3.1-flash-lite` through
  `google-vertex`, with fallbacks off, required parameters, data collection
  denied, and ZDR requested. Do not use Gemini 3.5 Flash for routine testing.
- Embeddings use the direct OpenAI key (`OPENAI_API_KEY` or the explicitly
  supported Lolla alias), not the OpenRouter key. If the OpenAI key is absent,
  follow the documented provider-free/degraded path; do not silently redirect
  embeddings to another provider.
- Never print, commit, or copy `.env` values or secrets into artifacts. Store
  only declared routing policy, response/generation identity, usage custody,
  exact provider-reported cost when available, and safe hashes/redactions.
- Current prices, model behavior, schemas, and provider policies are unstable.
  Recheck official sources at the time of any future provider-facing change.

## Frozen evidence and repository discipline

- Do not rewrite historical experiment prompts, runners, source targets,
  authorizations, outputs, or closeouts. Add a prospective version and hash-lock
  the boundary instead.
- New downstream R4 artifacts that contain old case IDs must be explicitly
  excluded from the frozen corpus replay discovery, with a regression test, so
  later work cannot rewrite the historical 400-artifact inventory.
- Preserve user changes in dirty worktrees. Keep commits and stacked PRs
  narrow, explain their parent branch, and push restart-safe checkpoints.
- Use exact hashes, stable IDs, source aliases, speaker/turn provenance, and
  deterministic manifests for custody. Code may reject malformed custody; it
  may not repair meaning.
- Do not garden or archive historical files merely because they look old. First
  classify them as current entrypoint, immutable evidence, superseded proposal,
  generated artifact, or genuinely redundant material. Gardening is outside
  the current critical path unless confusion blocks development.

## Verification discipline

Run the smallest relevant checks while iterating, then the full suite before a
handoff or PR update. For the current R4 package:

```bash
PYTHONPATH=. python3 scripts/evals/build_r4_semantic_distinction_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_semantic_distinction_experiment.py --dry-run
PYTHONPATH=. pytest -q tests/test_r4_semantic_distinction.py tests/test_r4_semantic_distinction_contract.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
At the 2026-07-14 post-consolidation handoff, the full suite passes 4,869 tests
with all 93 subtests passing and one existing `datetime.utcnow()` deprecation
warning. A changed count is not automatically a regression; unexplained
failures or historical hash drift are.

## Current handoff — 2026-07-14

- R1 trust/capture/cost/privacy/custody hardening: complete provider-free.
- R2 constitutional graph survival: complete provider-free.
- R3 fresh-consumer work: honestly closed/deferred without meeting its semantic
  exit condition; do not reopen it casually.
- R4 inventory, fan-in, first complementary-reader attempt, token correction,
  corrected diagnostic, and provider-free semantic-distinction repair:
  complete and documented.
- Canonical branch: `main` at consolidation merge `8708319` (GitHub PR #360).
- PR #347 was recognized as merged through the consolidation. PRs #348-#359
  are closed as superseded after verifying every exact head commit is reachable
  from `main`; their historical branches and discussions remain intact.
- Provider calls currently authorized: zero.
- Runtime/graph integration, wider-corpus execution, model comparison,
  production-model selection, receipt claims, and scalar scoring: unauthorized.

The exact next decision is founder-owned: authorize or defer
`lolla-r4-semantic-distinction-holdout-a3`. The frozen package contains Case 01
as an unseen false-stand-down target and Case 04 as an unseen restraint control,
allows no more than four calls, has a conservative `$0.0280125` estimate, and a
hard `$0.03` ceiling. The package itself does not authorize transport, and the
live runner must never load the hidden source-first answer key.

If no explicit authorization is present, stop at the provider-free boundary.
R5 product usefulness and receipt reconstruction remain gated on evidence from
the R4 decision; they are not the automatic next implementation task.

## Resume on another machine

With GitHub CLI authentication available:

```bash
gh repo clone gofarrrr/lolla-skill
cd lolla-skill
git switch main
git pull --ff-only
git status -sb
```

If the repository already exists, fetch first, switch to `main`, and pull with
`--ff-only`. Read this file and the ordered entrypoints above before continuing.
Do not infer provider authorization from the runner, historical authorization
artifacts, merged preparation work, or any remote branch.
