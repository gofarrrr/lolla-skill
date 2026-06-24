# Observatory Archive Parity Audit

Status: investigation plus one small metadata-surfacing fix.

This note records what the current Observatory/local-history surface can inspect
after the Agent Result Contract and Risk Mode Metadata PRs. It does not propose
turning Lolla into a generic guardrail, sandbox, proxy, identity layer, or LLM
judge. The question here is narrower: after a manual `$lolla` run, can the
operator inspect the artifacts Lolla already gathered?

## Run Checked

Primary smoke archive:

`/Users/marcin/.local/share/lolla/runs/founder-months-runway-flat/20260624T192039Z_c6c235`

The archive contains the expected product and custody artifacts, including:

- `result.json`
- `agent_result.json`
- `reasoning_trace.json`
- `run_events.json`
- `memo.md`
- `graph_survival_report.json`
- `graph_survival_report.md`
- `operator.log`
- `live_transcript.txt`

The run health is `partial` because the provider returned reasoning details
despite reasoning being disabled. That is not a failure of the archive contract.
It is correctly surfaced as a conservative trust issue:
`vendor_boundary_reasoning_leak`.

## What Works Today

- The Observatory server can launch against the archived smoke `result.json`.
- `/api/cases` finds the local archive root and lists archived runs.
- `/api/case/<archive-case-id>` loads selected archived run data.
- `/api/case/<archive-case-id>/usage` loads selected archived usage telemetry.
- `/api/case/<archive-case-id>/graph` builds a selected archived reasoning graph.
- `/audit/reasoning-trace` can show active-run trace custody, including
  `agent_result.json`, `reasoning_trace.json`, `run_events.json`,
  `graph_survival_report.*`, and health-related trace adequacy.
- `/audit/events` can show active-run event history, including archive events.
- `/audit/memo` can render the active-run memo sidecar.
- `/audit/graph-survival` can render the active-run graph survival report.

## What Was Missing

`risk_mode` is part of the post-PR2 artifact chain. In the checked smoke archive,
the mode was available from `agent_result.json`; newer PR2-era runs should also
carry it directly in `result.json` and `reasoning_trace.json`. The Observatory
case API did not expose it, so the SPA could not show the current or archived
run's risk mode even when the artifact chain had the field.

This PR fixes that small gap:

- `/api/case/<id>` now includes top-level `risk_mode`.
- The server-rendered telemetry run header now includes `Risk mode: <mode>` when
  the active result has the field.

## Parity Gaps Still Open

The larger archive/local-history parity gap remains: selected archived cases and
server-rendered telemetry panels are not the same inspection surface.

The SPA case list can select archived runs through `/api/case/<id>`, but the
server-rendered telemetry pages such as `/audit`, `/audit/reasoning-trace`,
`/audit/events`, `/audit/memo`, `/audit/graph-survival`, and `/usage` are scoped
to the active result served at process start. They do not follow the case
selected in the SPA's local-history list.

That means:

- `agent_result.json` is archived and trace-indexed, but it is not a first-class
  selected-case panel.
- `reasoning_trace.json` is inspectable for the active served result, but not for
  an arbitrary selected archived case from the SPA.
- `run_events.json` is inspectable for the active served result, but not for an
  arbitrary selected archived case from the SPA.
- `memo.md` is inspectable for the active served result, but not for an
  arbitrary selected archived case from the SPA.
- `graph_survival_report.*` is inspectable for the active served result, but not
  for an arbitrary selected archived case from the SPA.
- The archive path is present in `/api/cases` as `result_path` and in
  `agent_result.json` artifact paths, but it is not presented as a clear
  selected-run custody panel.

During browser-driven inspection, the Cases list rendered and direct DOM
inspection found the archived runs. Selecting an archived case through browser
automation repeatedly left the page unreadable to the automation session, while
the corresponding backend endpoints continued to return quickly. That is not
enough to prove every human browser click fails, but it is enough to treat the
archive selection path as needing focused frontend reproduction before a UI
redesign.

## Likely Cause

This is not primarily an archive-root problem, static-path problem, or missing
API-endpoint problem for the main archived result, usage, and graph payloads.
Those endpoints work.

The current limitation is a split inspection model:

- The SPA has a selected-case state and can load archived result summaries.
- The deeper telemetry pages are server-rendered from one process-global
  `_RESULT` and sidecars next to `_RESULT_PATH`.

That design is adequate for inspecting the active/manual run, especially when
the server is launched directly against one archived `result.json`. It is not
yet archive-parity inspection for local history.

## Selected-Archive Custody Follow-Up

The follow-up keeps Observatory boring and read-only. It does not redesign the
UI; it makes the selected archived run's custody artifacts reachable through
fixed local endpoints and shows a compact selected-run custody panel in the SPA:

1. Selected-case sidecar API endpoints:
   - `/api/case/<id>/agent-result`
   - `/api/case/<id>/reasoning-trace`
   - `/api/case/<id>/events`
   - `/api/case/<id>/memo`
   - `/api/case/<id>/graph-survival`

   The first three return the raw JSON sidecar. `memo` returns a JSON wrapper
   with artifact metadata and the markdown string. `graph-survival` returns a
   JSON wrapper with the report JSON plus optional markdown artifact metadata and
   markdown string when `graph_survival_report.md` exists.

2. Resolve selected case IDs to archive run directories using the same archive
   lookup code already used by `/api/case/<id>`.

3. Keep these endpoints read-only and local-only. They should expose existing
   archived artifacts; they should not create new reasoning, run judges, replay
   traces, or change audit behavior.

4. Add deterministic tests proving selected archived cases can retrieve each
   sidecar independently of the active `_RESULT`.

5. The SPA selected-run custody panel shows availability and links for those
   artifacts. Missing sidecars render as unavailable rather than broken. The
   server-rendered `/audit/*` pages remain active-run scoped.

This keeps the next step aligned with the manual Lolla loop: run Lolla, open the
Observatory, inspect what happened, and trust the archive because the custody
trail is reachable.
