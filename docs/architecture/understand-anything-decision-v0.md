# Understand-Anything vs Local Audit: Decision (2026-07-09)

## Purpose

This decision records the tool choice for the question:

> Should we use Understand-Anything as our main way of understanding code dependencies and architecture, or keep the existing local audit approach as the source of truth?

## What I actually ran

- Checked local installation availability:
  - `understand-anything` CLI: **not found**.
  - `understand_anything` CLI: **not found**.
- Attempted repository install path (`git clone https://github.com/Egonex-AI/Understand-Anything.git`).
  - In this environment the clone failed with DNS/host resolution error (`Could not resolve host: github.com`), so local execution of the tool was not possible.
- Ran a local deterministic scan in the current repo as a replacement signal (AST + symbol/path scan):
  - Python files scanned: **806**
  - Top-level Python density:
    - `engine`: 178
    - `scripts`: 158
    - `tests`: 466
    - `observatory`: 3
    - `research`: 1
  - Reverse importers:
    - `engine.system_b.pipeline`: 17 modules
    - `observatory.serve_result`: 39 modules
    - `scripts.archive_run`: 0 modules
    - `scripts.run_pipeline`: 2 modules
  - High-coupling symbol counts:
    - `run_health`: 87 hits
    - `SystemBPipeline`: 7 hits
    - `ConversationContext`: 40 hits
    - `build_conversation_memory_bundle`: 4 hits
    - `download_md`: 0 direct symbol hits
  - Runtime artifact pattern hits:
    - `_result.json`: 80
    - `_extraction.json`: 22
    - `_extraction_calls.json`: 3
    - `/tmp/lolla_`: 20

## Verdict

**Primary source of truth should stay with local audits/graphs in-repo** for now.

Why:

1. We need a canonical, deterministic baseline for:
   - active runtime surface definitions
   - archive mutation boundaries
   - provider boundaries
   - presentation/review layer separation
2. The environment limitations here currently prevent actually running Understand-Anything end-to-end.
3. The project already has a working “connectedness map” + architecture audit package that can be updated deterministically and diff-reviewed.

## Recommended operating model

### Primary (decisions + correctness checks)
- Use `docs/audits/lolla-system-architecture-audit-2026-07-06.md` and `docs/architecture/connectedness-map.md` as authoritative status.
- Update these files when architecture changes.
- Run local scans/tests to validate coupling and boundary changes.

### Secondary (visual onboarding)
- Once the environment allows tool execution and interneted clone, install Understand-Anything and use it as:
  - onboarding visualization
  - long-distance dependency discovery
  - “how does this fit together?” exploration

This is a **supplement**, not the canonical behavior proof.

## Practical next step

If you want this activated in a networked environment:

1. Install in a networked shell:
   - `bash -c "curl -fsSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s codex"`
2. Run scoped analysis in this repo (within your assistant/CLI after plugin install):
   - Set context/project to `/Users/marcin/Desktop/Apps/lolla-skill-public-runtime`
   - Run `/understand . --full --no-auto-update`
3. Export graph and compare with `connectedness-map` assertions by checking:
   - nodes/edges touching `engine/system_b/`, `observatory/`, `scripts/run_pipeline.py`, `scripts/archive_run.py`, and related tests.

## Bottom line

For your current goals (“where we stand / how it works / what to prioritize”), we should not wait on Understand-Anything output.
Use it later for navigation speed, not as the correctness authority.
