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
4. `docs/conversation-understanding/lolla-r4-matched-holdout-v2-leakage-correction-result-2026-07-14.md`
   and `plans/lolla-r4-matched-holdout-v2-leakage-correction-plan-2026-07-14.md`
   — latest completed work, the rejected v1 evidence, leakage-corrected v2
   sources and priors, hash-bound human review, protected target, matched
   requests, non-authorizing contract, and next founder decision.
5. `docs/conversation-understanding/lolla-r4-residual-task-identity-repair-result-2026-07-14.md`
   and `plans/lolla-r4-residual-task-identity-repair-plan-2026-07-14.md` — the
   published additive residual-discovery contract and frozen boundaries.
6. `docs/conversation-understanding/lolla-r4-semantic-distinction-causal-diagnosis-2026-07-14.md`
   — the record-level Case 01/04 map, competing causal explanations,
   falsifiers, and the single repair class that earned the latest work.
7. `docs/conversation-understanding/lolla-r4-semantic-distinction-execution-result-2026-07-14.md`
   — consumed holdout evidence, exact provider cost, and the semantic failure
   that the causal diagnosis explains.
8. `docs/conversation-understanding/lolla-r4-semantic-distinction-preparation-result-2026-07-14.md`,
   `plans/lolla-r4-semantic-distinction-plan-2026-07-14.md`, and
   `docs/conversation-understanding/lolla-r4-semantic-distinction-current-practice-2026-07-14.md`
   — the consumed frozen contract, completed R4 causal plan, and official-
   practice check behind it.
9. `README.md`, `HOW_IT_WORKS.md`, `SKILL.md`, and `docs/skill/STEPS.md` when
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
PYTHONPATH=. python3 scripts/evals/build_r4_residual_task_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/build_r4_matched_holdout_v2_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_matched_holdout_v2_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/build_r4_matched_residual_holdout_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_matched_residual_holdout_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/build_r4_semantic_distinction_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_semantic_distinction_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/finalize_r4_semantic_distinction_execution.py --validate-only
PYTHONPATH=. pytest -q tests/test_r4_matched_residual_holdout_v2.py tests/test_r4_residual_task.py tests/test_r4_residual_task_contract.py tests/test_r4_semantic_distinction.py tests/test_r4_semantic_distinction_contract.py tests/test_r4_semantic_distinction_execution.py tests/test_r4_provider_free_corpus_replay.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
At the 2026-07-14 leakage-correction closeout, the full suite passes 4,928
tests with all 93 subtests passing and one existing `datetime.utcnow()`
deprecation warning. The focused R4 slice passes 100 tests. A changed count is
not automatically a regression; unexplained failures or historical hash drift
are.

## Current handoff — 2026-07-14

- R1 trust/capture/cost/privacy/custody hardening: complete provider-free.
- R2 constitutional graph survival: complete provider-free.
- R3 fresh-consumer work: honestly closed/deferred without meeting its semantic
  exit condition; do not reopen it casually.
- R4 inventory, fan-in, first complementary-reader attempt, token correction,
  corrected diagnostic, provider-free semantic-distinction repair, exact
  holdout execution, provider-free causal diagnosis, and provider-free
  residual-task identity repair, rejected v1 matched holdout, and provider-free
  leakage-corrected v2 matched holdout: complete and documented. The residual
  contract makes residual discovery the complete provider-visible job,
  deterministically maps its two enum values to the existing canonical roles,
  and preserves source/prior order, paired shape, relationship behavior,
  model, provider route, runtime, and graph. Case 04 locally expects two quiet
  surfaces; Case 01 preserves only the recurring operating-capability
  funding/ownership residual. The v1 matched design at `b464642` is permanently
  rejected because its evidence leaked classifications. The additive v2
  package freezes four new 28-message sources and priors, a human leakage pass
  bound to exact hashes, a protected source-first target, and eight exact
  v2/residual requests; it has not been executed.
- Canonical integration target: `main`. The founder-authorized residual commit
  `b513686d` was published through GitHub PR #364 and is contained by canonical
  merge `06422338`. The matched holdout goal began from that clean canonical
  state. GitHub PR #362 remains the consumed R4 execution handoff and PR #363
  the completed causal-diagnosis publication.
- PR #347 was recognized as merged through the consolidation. PRs #348-#359
  are closed as superseded after verifying every exact head commit is reachable
  from `main`; their historical branches and discussions remain intact.
- Provider calls currently authorized: zero. The one-use A3 authorization was
  consumed by exactly four calls at an exact provider-reported `$0.01107025`.
- The residual-task goal made zero provider calls at `$0.00`, prepared no new
  holdout, and did not request authorization. Its exact decision is
  `residual_contract_ready_for_new_holdout_design`.
- The matched holdout v2 leakage-correction goal made zero provider calls at
  `$0.00`. Its four simulated source/prior pairs, exact human review, protected
  source-first target, eight request previews, context/delta manifests,
  counterbalanced call plan, exact-authorization shape, non-scalar evaluation
  vector, and stop-on-first-failure runner are frozen. The conservative future
  estimate is `$0.040521`, with proposed anti-runaway ceilings of `$0.03` per
  matched case and `$0.12` total. Those values do not authorize or request
  execution. Its exact decision is
  `matched_residual_holdout_v2_ready_for_founder_authorization`.
- Runtime/graph integration, wider-corpus execution, model comparison,
  production-model selection, receipt claims, and scalar scoring: unauthorized.

The leakage-corrected matched residual holdout v2 is complete, but no execution
is authorized. A future founder decision may authorize only the exact frozen
eight-call plan and `$0.12` ceiling, or decline it. Do not create an
authorization artifact, make a provider call, reveal protected targets to the
runner, or modify the frozen sources, priors, arms, operator, order, seeds,
reasoning, or output allocation without a new goal. Do not combine any future
validation with a context-authority change, task split, relationship-reader
change, governed-pending output surface, or model/context change.

Do not retry A3, execute rejected v1, or make an unapproved provider call. The
leakage-corrected v2 holdout and frozen contract now exist, but execution still
requires separate exact founder authorization. R5 product usefulness and
receipt reconstruction, runtime/graph integration, wider-corpus execution,
model comparison, and production-model selection remain gated and
unauthorized.

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
