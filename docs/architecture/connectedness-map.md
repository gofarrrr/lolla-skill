# Lolla Connectedness Map

Last seeded from: `docs/audits/lolla-system-architecture-audit-2026-07-06.md` with a 2026-07-09 scope refresh.
Purpose: help maintainers and reviewers quickly tell what is active runtime behavior, what is offline tooling, what is a review/product surface, what is historical, and what still needs verification.

This is a living project map, not a proof that every file listed here is complete or final. When code and docs disagree, verify against code before making architecture claims.

## How To Use This Map

For any future PR, ask:

1. Which status label does this change touch?
2. Can this change call a provider or spend money?
3. Can this change mutate the run archive?
4. Does this change affect the normal `lolla` skill path?
5. Does this change update docs/plans only, or does it change observed behavior?

If a PR touches `active runtime`, `provider boundary`, or `archive-mutating` components, it deserves more careful review than a docs-only or offline-tool change.

## 2026-07-09 Product Truth Refresh

- `Observatory` and the `Observatory Library Graph Scope Decision v0` were updated and are now the current source for map/product-surface accounting:
  - `docs/product/observatory-library-graph-scope-decision-v0.md`
  - `docs/product/observatory-library-graph-scope-decision-v0.json`
  - `reviews/codex-assisted/observatory-library-graph-scope-decision-v0/review.json`
- The current branch includes the graph-scope decision PR; the active graph scope is now explicit:
  - Selected-run learning map: present.
  - Model-detail reviewed-neighborhood cards: present.
  - Model-detail visual neighborhood: recommended next UI slice.
  - Filtered library/full-corpus graph: future.
- `Download MD` remains the private agent-memory export path; raw transcript remains out of the default read surface.
- No runtime/provider/archive behavior changed by this decision update.

## 2026-07-08 Product Truth Refresh

The following is the project-wide contract currently used for coding and maintainer handoff:

- `observatory/serve_result.py` is the default portable product surface after a run.
- Primary UI progression is `Outcome -> Learn -> Models -> Relations -> Map -> Receipts`.
- The first-class learning surfaces are in `Outcome`, `Learn`, `Models`, `Relations`, and `Map` tabs/cards.
- `Receipts` is the trust/accountability + missingness layer and the entry to optional inspection routes.
- `Download MD` is the explicit private export/action for full conversation-memory style material. It is not meant as the primary, default reading layer.
- Advanced routes (`/audit`, `/audit/extraction`, `/usage`) and deeper inspection endpoints remain review surfaces and should not lead the default user narrative.

## 2026-07-09 Tooling Status Note

- We evaluated the Understand-Anything tool path for this repo.
- In this environment the tool could not be installed or run:
  - CLI binary not found (`understand-anything` / `understand_anything`).
  - Network clone attempt to GitHub failed (DNS/host resolution).
- Practical choice: keep local, deterministic scan + architecture audit as the decision baseline for now; treat Understand-Anything as a future visualization layer when environment permits installation.
- Local replacement output for this date is captured in:
  - [docs/architecture/understand-anything-decision-v0.md](/Users/marcin/Desktop/Apps/lolla-skill-public-runtime/docs/architecture/understand-anything-decision-v0.md:1)
  - [docs/architecture/understand-anything-readiness-review-v0.json](/Users/marcin/Desktop/Apps/lolla-skill-public-runtime/docs/architecture/understand-anything-readiness-review-v0.json:1)
- This keeps the “truth” boundary stable while still enabling a visual onboarding tool later.

## Status Labels

| Label | Meaning | Review posture |
|---|---|---|
| `active runtime` | Used in a normal Lolla skill run. | Treat as behavior-changing unless proven otherwise. |
| `provider boundary` | Can call an external provider or spend API money. | Require explicit provider/cost awareness. |
| `archive-mutating` | Can write or modify local run archive artifacts. | Require artifact/custody review. |
| `review surface` | Used to inspect, browse, or review run outputs. | Check user-visible behavior and artifact compatibility. |
| `offline tool` | Manual/local tool outside the normal skill path. | Check whether it is safe, dry-run, or fixture-only. |
| `docs-only` | Documentation, plans, product notes, or explanations. | Check for drift against code if it claims behavior. |
| `historical artifact` | Old or generated artifact kept for lineage/history. | Do not delete casually; do not assume active use. |
| `dormant/default-off` | Code exists but is not used in the default runtime path. | Verify before activating; document the activation path. |
| `unknown` | Not yet verified enough to classify. | Investigate references/imports/callers before acting. |

## Normal Active Runtime Path

This is the currently understood default skill flow:

```text
User invokes lolla skill
  -> SKILL.md
  -> docs/skill/STEPS.md
  -> scripts/skill/setup.sh
  -> /tmp/lolla_${RUN_ID}_conversation.txt
  -> scripts/skill/run_extract_step.sh
  -> scripts/run_extract.py
  -> OpenRouter extraction call
  -> /tmp/lolla_${RUN_ID}_extraction.json
  -> scripts/skill/run_pipeline_step.sh
  -> scripts/run_pipeline.py
  -> engine/system_b/pipeline.py
  -> OpenRouter runtime lane calls
  -> optional OpenAI embeddings if configured
  -> Bullshit Index provider calls
  -> V60 enrichment and private sidecars
  -> /tmp/lolla_${RUN_ID}_result.json
  -> skill answer revision and memo/pressure state
  -> scripts/archive_run.py
  -> scripts/skill/launch_observatory.py
  -> observatory/serve_result.py
```

Provider boundaries and archive mutation happen inside this flow. Treat direct execution of these scripts as potentially live unless using known test fixtures/fake providers.

## Component Map

| Component / cluster | Status | Normal caller | Calls into | Provider/API risk | Archive mutation risk | Notes |
|---|---|---|---|---|---|---|
| `SKILL.md` | `active runtime` | User/agent skill invocation | `docs/skill/STEPS.md`, setup helpers | No direct calls | No direct mutation | User-facing skill contract and orchestration instructions. |
| `docs/skill/STEPS.md` | `active runtime` | `SKILL.md` | Skill shell helpers and manual orchestration steps | Documents provider paths | Documents archive path | More authoritative than broad narrative docs for current step order. |
| `scripts/skill/setup.sh` | `active runtime` | Skill preamble | `engine.system_b.run_state`, env files | Checks provider keys | Writes run env/log state, not archive | Creates run ID and `/tmp/lolla_*` env/log artifacts. |
| `scripts/skill/run_extract_step.sh` | `active runtime` | Skill Step 2 | `scripts/run_extract.py` | Indirect OpenRouter call | No archive mutation | Guards run ID and expected paths. |
| `scripts/run_extract.py` | `active runtime`, `provider boundary` | Extract wrapper or direct CLI | OpenRouter-compatible extraction | Yes, OpenRouter | No archive mutation | Rejects critical capture before provider call. |
| `scripts/skill/run_pipeline_step.sh` | `active runtime` | Skill Step 3 | `scripts/run_pipeline.py` | Indirect provider calls | No archive mutation | Uses `--skip-revision` and private Step 6 portfolio mode. |
| `scripts/run_pipeline.py` | `active runtime`, `provider boundary` | Pipeline wrapper or direct CLI | `SystemBPipeline`, BI, V60, private sidecars, usage/run health | Yes, OpenRouter; optional OpenAI embeddings | No direct archive mutation | Main runtime CLI and current bottleneck file. |
| `engine/system_b/pipeline.py` | `active runtime` | `scripts/run_pipeline.py` | pass runners, routing, companion, frame, structural coverage | Uses boundary client | No direct archive mutation | Core orchestrator and compatibility hub. |
| `engine/system_b/pass1_runner.py` | `active runtime`, `provider boundary` | `pipeline.py` | boundary client | Yes, via boundary client | No | Extracted pass 1 helper. |
| `engine/system_b/pass2_runner.py` | `active runtime`, `provider boundary` | `pipeline.py` | boundary client | Yes, via boundary client | No | Extracted pass 2 helper. |
| `engine/system_b/conversation_context.py` | `active runtime` | loader/pipeline/tests | Dataclass/runtime contract | No | No | Canonical conversation object. Preserve as a core boundary. |
| `engine/system_b/conversation_loader.py` | `active runtime` | `scripts/run_pipeline.py` | `ConversationContext` | No | No | Loads extraction and transcript into runtime context. |
| `engine/system_b/ir_constructor.py`, `engine/system_b/ir.py` | `active runtime` | `pipeline.py` | IR/provenance structures | No by default | No | Specialist extractors appear injectable/dormant unless wired by caller. |
| `engine/system_b/boundary_provider.py` | `provider boundary`, `active runtime` | extraction/pipeline/BI paths | OpenRouter/OpenAI-compatible APIs, optional Gemini CLI | Yes | No | Main external-call boundary. |
| `engine/system_b/usage_summary.py`, `engine/system_b/pricing.py`, `engine/system_b/provider_boundary_health.py` | `active runtime` | `scripts/run_pipeline.py`, archive/result builders | Usage/cost/health helpers | No direct calls | No | Important for provider accounting and receipts. |
| `engine/system_b/v60_enrichment.py` | `active runtime`, `review surface` | `scripts/run_pipeline.py`, archive finalizers | V60 affordance data | No | No direct archive mutation | Enriches runtime/product transport; not a final-answer selector. |
| `engine/system_b/pre_step6_private_table.py` | `active runtime` | `scripts/run_pipeline.py` | Local support assembly | No | No | Writes private support sidecars through caller. |
| `scripts/archive_run.py` | `active runtime`, `archive-mutating` | Skill archive/finalize step or direct CLI | artifact builders, optional Decision Work hook | No direct provider calls expected | Yes | Copies run files and writes generated archive artifacts. |
| `engine/system_b/agent_result.py` | `active runtime`, `archive-mutating` through caller | `scripts/archive_run.py` | Local artifact builder | No | Writes through archive caller | Conservative machine-readable run result. |
| `engine/system_b/evaluation.py` | `active runtime`, `archive-mutating` through caller | `scripts/archive_run.py` | Local artifact builder | No | Writes through archive caller | Run-readiness artifact, not an advice-quality judge. |
| `engine/system_b/reasoning_trace.py` | `active runtime`, `archive-mutating` through caller | `scripts/archive_run.py` | Local artifact builder | No | Writes through archive caller | Artifact custody and reasoning-support trace. |
| `scripts/skill/launch_observatory.py` | `active runtime`, `review surface` | Skill Observatory step | `observatory/serve_result.py` | No provider calls | No archive mutation | Launches local server and waits for readiness. |
| `observatory/serve_result.py` | `review surface`, partly `active runtime` | Launch helper or direct CLI | archive readers, sidecar readers, local API routes | No provider calls expected | No normal archive mutation | Largest active file; local UI/API over results and archive, plus the main product-facing workspace flow. |
| `observatory/build/` | `review surface`, `historical artifact` unless build regenerated | `observatory/serve_result.py` | Browser assets | No | No | Compiled SPA assets. Source build process appears external to this repo. |
| `engine/system_b/mental_model_teacher_observatory_packet_adapter.py` | `review surface` | Observatory routes | Local Teacher package summary | No | No | Read-only adapter with explicit non-claims. Teacher content is intentionally embedded in the Observatory flow, not a separate primary product surface. |
| `scripts/lolla_doctor.py`, `engine/system_b/lolla_doctor.py` | `offline tool` | Manual CLI | Local diagnostics | No | No by design | Good candidate for preflight before live runs. |
| `scripts/evals/*` | `offline tool`, sometimes `review surface` | Manual eval/product commands, tests | Fixtures, eval/product modules | Varies by script; verify before running | Varies by explicit mode | Not part of default skill runtime. |
| `docs/evals/*` | `docs-only` | Humans | None | No | No | Evaluation methodology and planning docs. |
| `docs/product/*` | `docs-only`, sometimes `review surface` context | Humans/product work | None | No | No | Product plans/prototypes. Verify before treating as runtime truth. |
| `docs/conversation-understanding/*` | `docs-only` | Humans | None | No | No | Design/research material, not runtime proof. |
| `plans/*` | `docs-only` | Humans | None | No | No | Implementation and PR planning notes. |
| `reviews/*` | `review surface`, `historical artifact` | Humans/review tooling | None unless consumed by scripts | No | No | Review outputs and generated review records. |
| `research/*` | `historical artifact`, `offline tool` context | Humans/research scripts | None directly | No unless a script is run | No unless a script is run | Large generated/source research area. |
| `scripts/research/*` | `offline tool` | Manual research workflows | Research providers/files depending on script | Unknown per script; verify before running | Unknown per script | Do not assume safe/static without inspection. |
| `data/knowledge_graph.json`, `data/relationship_graph.json`, `data/curated/*`, `data/embeddings.db` | `active runtime`, `historical artifact` for generated data lineage | Pipeline data loaders | Local graph/retrieval code | No direct provider calls | No | Active substrate; large files are expected. |
| `data/compiled/model_affordances/affordances_v60.json` | `active runtime`, `review surface` support | V60 enrichment | Local enrichment | No | No | Current active V60 artifact. |
| `data/compiled/model_affordances/affordances_v1.json` through `affordances_v59.json` | `historical artifact` | Humans/offline lineage | None in normal V60 path | No | No | Keep as lineage unless maintainers decide otherwise. |
| Promoted authority/stress/overoptimism pilot bridges | `dormant/default-off` | `PipelineConfig` flags if enabled | Pilot bridge/workspace modules | Likely provider/local side effects depending on activation | Possible local `.tmp` writes | Not enabled in normal `scripts/run_pipeline.py` path observed in audit. |
| Step 7 pressure-check agents | `dormant/default-off`, `provider boundary` if enabled | Skill operator when explicitly requested | Subagent/model review paths | Yes if enabled | Writes pressure-check state | Default-off per skill docs. |
| Gemini CLI provider path | `dormant/default-off`, `provider boundary` | Boundary provider loader if selected | `gemini` subprocess | Yes if selected | No | Normal live path uses OpenRouter. |
| Decision Work Brief archive attachment hook | `dormant/default-off`, `archive-mutating` through caller | `scripts/archive_run.py` hook | Decision Work brief builder | No expected provider calls | Optional archive attachment | Failed-closed hook; verify current default before enabling. |
| Specialist IR extractors | `dormant/default-off` | Injectable `ir_constructor.py` callers | Constraint/thread/stance extraction helpers | Unknown if activated | No direct archive mutation | Not observed in normal runtime path. |

## Provider / API Boundaries

These areas can call external model/provider services or otherwise spend money when used live:

| Boundary | Status | Notes |
|---|---|---|
| `scripts/run_extract.py` | Active OpenRouter boundary | Calls provider after local capture validation. |
| `engine/system_b/boundary_provider.py` | Active provider boundary | Central OpenRouter/OpenAI-compatible boundary client and optional Gemini CLI client. |
| `scripts/run_pipeline.py` main lanes | Active OpenRouter boundary | Loads `SystemBPipeline` with `provider_name="openrouter"` in the normal live path. |
| Bullshit Index path inside `scripts/run_pipeline.py` | Active provider boundary | Runs even when skill pipeline passes `--skip-revision`; treat as separate from answer revision. |
| Optional OpenAI embeddings | Active only if configured | Enabled when `OPENAI_API_KEY` is present in the environment. |
| Step 7 pressure-check agents | Default-off provider boundary | Only run when explicitly requested by operator/user. |
| Gemini CLI boundary | Dormant/default-off provider boundary | Present as an alternative provider path, not normal default runtime. |
| Research/eval scripts | Unknown per script | Inspect before running; some may be static, some may call providers. |

Rule: do not run provider-boundary scripts during documentation or static review unless the command is known to be fixture-only/fake-provider/no-call.

## Archive-Mutating Paths

These paths can write or modify local run archive artifacts:

| Component | Status | Notes |
|---|---|---|
| `scripts/archive_run.py` | Active archive mutation | Main archive writer and generated artifact creator. |
| Archive generated artifact builders | Archive mutation through caller | `agent_result`, `evaluation`, `reasoning_trace`, graph survival, and related artifacts. |
| Decision Work Brief archive hook | Default-off or conditional archive mutation | Called from archive script as a failed-closed optional attachment path. |
| Explicit eval/product sidecar writers | Offline/conditional archive mutation | Some offline tools may write fixtures or archive sidecars when explicitly requested. Verify script docs/options before running. |

Rule: when changing archive-mutating code, review backward compatibility with existing archive cases and distinguish dry-run/fixture writes from real archive writes.

## Review Surfaces

Review surfaces inspect or present run outputs. They are user/product-facing locally but should not be assumed to be part of core reasoning.

| Surface | Reads | Writes | Notes |
|---|---|---|---|
| `observatory/serve_result.py` | Live result, archive result, sidecars, compiled SPA | HTTP responses; no expected provider calls | Local review UI/API and current largest bottleneck file. |
| `observatory/build/` | Browser loads compiled assets | Browser cache only | Compiled SPA build checked into repo. Source build process appears external. |
| Teacher Observatory adapter | Teacher package data | API response only | Explicitly read-only and non-provider. |
| Review artifacts under `reviews/` | Existing review JSON/Markdown | Humans or tools may add new review artifacts | Treat as product/review history, not runtime proof. |

## Offline Tools And Docs-Only Areas

| Area | Status | Notes |
|---|---|---|
| `scripts/evals/*` | Offline tool | Use for evaluation/product/review workflows. Inspect provider/archive side effects before running. |
| `scripts/lolla_doctor.py` | Offline tool | Read-only preflight; useful before live runs. |
| `scripts/research/*` | Offline tool | Verify each script before running; not part of normal skill path. |
| `docs/evals/*` | Docs-only | Methodology and eval plans. |
| `docs/product/*` | Docs-only/product context | Product plans/prototypes unless a script or Observatory route wires them. |
| `docs/conversation-understanding/*` | Docs-only | Design/research docs. |
| `plans/*` | Docs-only | PR plans and implementation notes. |
| `tasks/*` | Docs-only or review support | Verify if a task artifact is consumed by a script. |

Rule: docs-only claims are intent, not proof. Verify against code before saying a behavior exists.

## Dormant / Default-Off Paths

These components are not confirmed dead. They are simply not part of the normal default runtime path observed in the audit.

| Component | Why dormant/default-off | What to verify before activation |
|---|---|---|
| Step 7 pressure-check agents | Skill docs describe them as default-off. | Provider cost, output files, archive/state effects. |
| Promoted authority/stress/overoptimism pilot bridges | `PipelineConfig` flags default false; normal CLI does not enable them. | Required data, provider calls, `.tmp` writes, result schema effects. |
| Gemini CLI provider | Normal live CLI uses OpenRouter. | CLI availability, cost/auth behavior, response metadata compatibility. |
| Specialist IR extractors | Normal pipeline path does not inject specialist extractors. | Caller path, provider/local side effects, IR schema implications. |
| Decision Work Brief runtime attachment | Archive hook exists but is conditional/default-off in practice. | Activation flag, archive mutation behavior, failure policy. |

Rule: do not delete dormant paths merely because they are not default-active. First decide whether they are roadmap, research, compatibility, or truly obsolete.

## Historical Artifacts

Historical artifacts can be valuable even if they are not active runtime inputs.

| Artifact area | Status | Notes |
|---|---|---|
| `data/compiled/model_affordances/affordances_v1.json` through `v59.json` | Historical artifact | Earlier affordance generations; V60 is active. |
| Older review artifacts under `reviews/` | Historical/review artifact | Useful for product and decision history. |
| Older plans under `plans/` | Historical/docs-only | Useful for intent/history; may not reflect current code. |
| Generated research under `research/` | Historical/research artifact | Large and not normal runtime. |

Rule: historical artifacts should be archived, labeled, or moved intentionally, not deleted opportunistically during feature work.

## Unknown / Needs Verification

Use this section for things maintainers encounter that are not yet classified.

Current known unknowns:

| Area | Question |
|---|---|
| Individual `scripts/research/*` commands | Which are static/local and which call providers? |
| Some product/review scripts under `scripts/evals/*` | Which can mutate real archives versus fixtures? |
| External Observatory SPA source/build process | Is this intentionally external long-term, or should build provenance live in this repo? |
| Full test-suite categories | Which tests are safe, slow, provider-backed, archive-mutating, or research-only? |

When an unknown is resolved, move it into the appropriate section above.

## Change Review Checklist

For future PRs, reviewers can use this quick checklist:

- Does this PR touch `active runtime`?
- Does this PR touch a `provider boundary`?
- Does this PR touch `archive-mutating` behavior?
- Does this PR change `/tmp/lolla_${RUN_ID}_*` artifact naming or sidecar conventions?
- Does this PR change result, archive, evaluation, agent result, reasoning trace, or Observatory response schemas?
- Does this PR turn a `dormant/default-off` path into default behavior?
- Does this PR add a new major script, product surface, data artifact, or archive artifact?
- If yes, was this connectedness map updated?

## Update Rules

When adding or materially changing a major component, update this map with:

1. Component or cluster name.
2. Status label.
3. Normal caller.
4. Main things it calls into.
5. Whether it can call providers.
6. Whether it can mutate archives.
7. Any important notes about runtime, offline, historical, or default-off behavior.

Prefer cluster-level entries over listing every file. The goal is to make navigation and review easier, not to create a second file tree.

## Source Snapshot

This map was seeded from the architecture audit:

- `docs/audits/lolla-system-architecture-audit-2026-07-06.md`

If this map and the audit disagree in the future, treat this map as the intended living document, but verify against code before making behavior claims.
