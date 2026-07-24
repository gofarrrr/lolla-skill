# Lolla Codex live-run boundary repair

Date: 2026-07-24

Status: complete — provider-free implementation and verification published
through [PR #404](https://github.com/gofarrrr/lolla-skill/pull/404) at merge
`f799152671730d631488841a039b1358182a16db`

Source incident: user-operated run `20260724T182631Z_b8cec8`

Provider calls authorized for this goal: **0**

Provider cost authorized for this goal: **USD 0.00**

## Falsifiable goal

Can an ordinary Codex `$lolla` run preserve the current conversation,
pressure, graph, reconsideration, disposition, memo, and archive semantics
without placing source text, agent-authored private payloads, raw JSON,
temporary-file contents, validation repair, or ad hoc diagnostics in the
normal visible execution stream?

The goal passes only when a provider-free Codex-style replay proves the
complete mechanical boundary. A green helper unit test, a clean manually
curated narration, owner-only filesystem modes, or a plausible final answer
does not pass the goal by itself.

Codex may continue to display compact tool chrome because the repository skill
does not own the Codex interface. The repair must keep private or verbose
content out of that chrome; it does not claim that tool cards can disappear.

## Controlling boundaries

This goal must not change:

- canonical Markdown, curation, the 222-model manifest, or the 1,358 authored
  relations;
- direct selection, the six-item direct cap, outgoing one-hop
  ally/antagonist/tension expansion, reserve custody, graph prompts, or
  apply/reject/park semantics;
- provider models, routes, request parameters, credentials, retry policy,
  privacy policy, or cost policy;
- four-lane pressure semantics, V60 candidate selection, same-context
  reconsideration, Observatory meaning, or archive case identity;
- frozen experiment inputs, outputs, authorizations, or closeouts.

No live run, provider call, embedding call, graph experiment, model
comparison, usefulness claim, R4/R5 restart, Atlas expansion, or global/multi-
hop traversal is authorized.

## Evidence from the source incident

The completed archive proves:

- 14 source messages were preserved with zero omissions;
- the graph was active with six direct and three one-hop pressure items;
- the revised answer, memo, ledgers, Observatory, archive, cost, and machine
  handoff were produced;
- one of twelve optional passage judgments was missing and the run was
  truthfully `partial`;
- archive files were owner-only.

The user-visible Codex trace separately proves:

- the first fresh shell failed because `LOLLA_ENV_STATE` was not pinned;
- the host sent the conversation before the capture readiness protocol
  protected the live surface, and the full source was echoed;
- revised prose, graph decisions, private-table decisions, V60 decisions, and
  memo fields were exposed through file-authoring tool cards;
- an improvised `jq` query failed;
- an initially invalid graph ledger was repaired visibly;
- a final improvised evaluation query requested nonexistent fields and printed
  misleading nulls;
- those host-side operations were absent from `live_transcript.txt`,
  `operator.log`, `run_events.json`, and `reasoning_trace.tool_calls`.

The archive's `live_output_health: not_checked` statement was honest. Its zero
leak count was not evidence that the complete visible surface was clean.

## Repair register

Status values are `pending`, `in_progress`, `complete`, or `blocked`.

| ID | Priority | Status | Repair | Falsifiable acceptance criterion |
|---|---:|---|---|---|
| UX-01 | P0 | complete | Define the normal visible-surface allowlist and forbidden-content classes. | The checked-in contract distinguishes product prose, compact tool receipts, private payloads, and host-owned chrome without promising invisible tools. |
| STATE-01 | P1 | complete | Remove the need to manually copy/source a run-state path in every fresh shell. | Every helper in a fresh-shell replay resolves one pinned run; missing, stale, or ambiguous state fails before reading private input. |
| INPUT-01 | P1 | complete | Enforce `PRIVATE_INPUT_READY` in the end-to-end host interaction, not only inside the Python helper. | A true PTY orchestration test with a unique marker proves the marker reaches the owner-only artifact and never reaches visible output; early-send and echo-disable failures fail closed. |
| PERSIST-01 | P1 | complete | Add private-input deterministic persistence for live narration and the revised answer. | No revised/narration content appears in command arguments, shell heredocs, stdout, stderr, or edit cards in the replay; the exact content is persisted owner-only. |
| PERSIST-02 | P1 | complete | Add private-input deterministic persistence for graph, private-table, and V60 decisions. | The agent submits only mutable judgment fields; deterministic code copies exact skeleton identity/order, validates before replacement, and emits only a compact receipt. |
| PERSIST-03 | P1 | complete | Add private-input deterministic persistence for memo-note fields and optional receipt overrides. | Memo/receipt payloads do not appear in visible transport; existing render/finalize semantics and owner-only modes remain intact. |
| CONSUME-01 | P1 | complete | Replace normal-run ad hoc `sed`/`jq` inspection with schema-owned bounded consumer packets. | The replay completes Steps 2.5, 4, 6, 8c, and final verification without an improvised JSON query or full artifact dump. |
| SURFACE-01 | P1 | complete | Capture the complete replay-visible stream or classify it truthfully when complete capture is absent. | A forbidden marker makes live output `unsafe`; incomplete/manual capture remains `not_checked`; zero leak counts are never presented as full-surface proof. |
| CUSTODY-01 | P2 | complete | Record safe host-operation failure and repair custody. | A failed local validation attempt records stage, safe error class, visibility, and replacement status without raw private payloads; later archive inspection can see it. |
| HEALTH-01 | P2 | complete | Clarify local storage, provider egress, interface privacy, trace coverage, tool-call coverage, and surface-divergence fields. | A cold reader cannot interpret `local_only`, `tool_calls: []`, `matched`, or zero leaks as evidence about a surface those fields did not observe. |
| COST-01 | P2 | complete | Clarify enforced provider budget versus later whole-run estimated cost. | Detailed custody identifies which calls/costs the hard ceiling enforces and separately reports total known/estimated vendor use without changing routing or pricing. |
| REPLAY-01 | P1 | complete | Add one provider-free Codex-style full-run mechanical replay gate. | The full 14-message Marcus fixture completes private capture/persistence/finalization with no network transport and no forbidden visible marker. |
| DOCS-01 | P3 | complete | Update current entrypoints, skill instructions, and cold-start handoff; preserve historical evidence. | Fresh-clone docs describe the implemented boundary, known Codex-chrome limit, exact nonclaims, and next decision without relying on chat history. |
| VERIFY-01 | P3 | complete | Run focused, handoff, frozen-boundary, and full verification. | All named focused tests, current Stage 0 validators, full suite, JSON/Python/Bash/whitespace/secret checks, and graph/frozen hash checks pass with explained counts. |
| PUBLISH-01 | P3 | complete | Publish through a narrow GitHub PR and merge only when ready. | The exact reviewed commit is pushed, PR checks and actionable review are resolved, the PR is merged normally, and local `main` matches canonical GitHub. |

## Normal visible-surface contract

Normal product prose may contain only:

1. the short invocation acknowledgement;
2. the source-grounded readback and audit promise;
3. the counterargument lead and an honest partial warning when necessary;
4. the updated position;
5. an optional material pressure-check divergence when explicitly enabled on a
   supported host;
6. the final functional receipt.

Compact tool receipts may disclose only non-sensitive state needed to continue,
for example:

```text
PRIVATE_INPUT_READY
CAPTURE_STATUS: ready; message_blocks=14; bytes=26304
EXTRACTION_STATUS: ok
PIPELINE_STATUS: ok
PRIVATE_PERSIST_STATUS: revised_answer ready
PRIVATE_PERSIST_STATUS: step6_decisions valid
MEMO_STATUS: ready
FINALIZE_STATUS: complete
```

Normal visible output must not contain:

- source conversation prose or a distinctive source marker;
- agent-authored revised text, private rationales, memo fields, or receipt
  bodies inside a tool command/result;
- JSON bodies, copied skeleton fields, internal IDs, private cards/chunks,
  graph pressure details, or provider prompts;
- environment-file preambles, temporary paths, raw archive diagnostics, or
  raw schema validation output;
- `Added`/`Edited` payload previews for private runtime artifacts;
- ad hoc `sed`, `jq`, Python, or shell snippets used to interpret live result
  schemas;
- repair-loop content, stack traces, provider secrets, or raw provider errors.

Failures may appear as one compact, source-free status. Full safe diagnostics
belong in owner-only operator custody.

## Implementation order

1. Freeze this register and write red replay tests for the actual failures.
2. Introduce one pinned state resolver and private-input transport shared by
   capture and later persistence helpers.
3. Move mutable Step 6 decisions into a compact private packet; make
   deterministic code own skeleton copying and atomic validation.
4. Add bounded consumer/final-verification packets and remove normal-run ad hoc
   inspection instructions.
5. Add safe host-operation custody and full-surface replay classification.
6. Update current docs and handoff.
7. Run the complete completion audit, publish, and merge only if every register
   item has authoritative evidence.

## Completion nonclaims

Passing this repair will not prove:

- that Lolla improves decisions or is useful to real users;
- that graph pressure uniquely caused an answer change;
- that the one-hop graph should expand;
- that the source was semantically understood;
- that provider privacy equals local-only processing;
- that Codex tool cards are invisible;
- that Lolla is production-ready.
