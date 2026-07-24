# Codex live-run transport boundary

Date: 2026-07-24

Status: current ordinary Codex transport contract

This document controls how the existing Lolla semantics are moved through a
Codex live run. It changes transport and custody, not the four pressure lanes,
the mental-model graph, graph selection/expansion, prompts, providers,
reconsideration doctrine, or apply/reject/park meaning.

## Why this exists

A real Codex run on 2026-07-24 completed the substantive audit but exposed the
source conversation and private runtime machinery in the visible terminal. The
helper itself knew how to disable terminal echo; the host sent source before
the readiness signal. Later, the host authored revised prose, three ledgers,
and memo fields through visible edit/heredoc operations, queried JSON ad hoc,
and repaired one invalid ledger in public. The curated narration artifact did
not capture those host operations, so it correctly remained `not_checked`.

The ordinary path now makes the safe operation the short path.

## Exact run handle

Setup prints:

```text
RUN_HANDLE: 20260724T182631Z_example
LOLLA_SETUP_STATUS: ready; ...
```

Keep the exact handle in the host's conversation state. Every later helper is
called with `--run-id RUN_HANDLE`. Helpers load the matching guarded state in
their own fresh shell. They do not follow `lolla_latest_env.sh`.

Do not copy or source an environment-state path. Missing, stale, or mismatched
state fails before private input is read.

## Private-input protocol

The following inputs are private runtime payloads:

- authoritative conversation source;
- product narration being appended to the curated live transcript;
- revised answer and Step 6 judgments;
- memo-note fields.

For each private-input helper:

1. start the process with only the helper, exact run handle, and operation kind
   in the command;
2. wait for the exact line `PRIVATE_INPUT_READY`;
3. send the payload through the host's process-input channel;
4. close standard input;
5. accept only the compact receipt.

Do not put a private payload in a command argument, shell heredoc, inline
Python, Apply Patch, or file-editor operation. If terminal echo cannot be
disabled, the helper fails without reading.

Source capture:

```bash
bash scripts/skill/capture_step.sh --run-id RUN_HANDLE
```

Narration persistence:

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind narration
```

Step 6 persistence:

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind step6
```

Memo-note persistence:

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind memo
```

Private receipt override (exceptional operator path):

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind receipt
```

## Schema-owned consumer packets

Do not inspect live extraction/result artifacts with improvised `sed`, `jq`,
inline Python, or broad file dumps. Ask deterministic code for the named
projection:

```bash
bash scripts/skill/prepare_consumer_step.sh \
  --run-id RUN_HANDLE \
  --stage readback

bash scripts/skill/prepare_consumer_step.sh \
  --run-id RUN_HANDLE \
  --stage reconsideration

bash scripts/skill/prepare_consumer_step.sh \
  --run-id RUN_HANDLE \
  --stage verification
```

Each command prints only `CONSUMER_PACKET_STATUS: <stage> ready` and writes one
owner-only, run-scoped packet. Use the host's ordinary bounded file-read
capability to read that packet. Do not print it through the shell. Codex may
still show a file-read tool card; repository code does not control or hide
host UI chrome.

The readback packet contains only the extraction fields required for the
source-grounded readback. The reconsideration packet contains the four pressure
products, exact active graph items and skeleton, private-table atoms/skeleton,
and selected V60 material/skeleton. The verification packet contains statuses,
counts, coverage, validation, graph policy, and cost state—not the private
reasoning prose.

## Step 6 packet

The private JSON object contains exactly:

```json
{
  "revised_answer": "the complete Updated position prose",
  "graph_decisions": {
    "exact pressure_id": {
      "disposition": "apply | reject | park",
      "strongest_plausible_application": "...",
      "attempted_application_condition": "...",
      "why": "...",
      "failed_condition": "...",
      "reopen_condition": "...",
      "visible_effect": "...",
      "private_guardrail": "...",
      "risk_if_forced": "...",
      "risk_if_ignored": "..."
    }
  },
  "private_table_decisions": {
    "exact source_id": {
      "disposition": "used | rejected | deferred | private_guardrail | confirming_support",
      "why": "...",
      "visible_effect": "...",
      "private_guardrail": "..."
    }
  },
  "v60_decisions": {
    "exact chunk_id": {
      "disposition": "used | rejected | deferred | not_considered",
      "route": "...",
      "strongest_plausible_application": "...",
      "why": "...",
      "visible_effect": "...",
      "private_guardrail": "...",
      "risk_if_forced": "...",
      "technical_blocker": "",
      "blocked_or_guarded_claim": "",
      "uncertainty_boundary": ""
    }
  }
}
```

Only fields present in the exact skeleton row are required/accepted for that
row. For example, the two absence-only V60 fields are not accepted for an
affordance row. The agent supplies judgments; deterministic code:

- requires exact identity coverage with no unknown IDs;
- copies immutable identity, provenance, and ordering from each skeleton;
- builds all three complete ledgers;
- validates the revised answer and all required ledgers in memory;
- replaces no artifact unless the whole packet is valid;
- writes result/revised/ledger artifacts owner-only;
- records safe success or failure custody.

An invalid packet prints one compact count and keeps full validation detail in
the owner-only operator log. It does not print the payload or validation
details. A corrected local packet may replace the invalid attempt; the failure
and replacement status remain in run events. This is deterministic local
repair, not a provider retry.

## Memo packet

The private JSON object contains exactly:

```json
{
  "memo_substantive_title": "...",
  "memo_orientation_note": "...",
  "memo_what_changed": "...",
  "memo_what_still_holds": "...",
  "memo_take_back_or_set_aside": "...",
  "memo_pressure_check": ""
}
```

After its compact success receipt, render with:

```bash
bash scripts/skill/render_memo_step.sh --run-id RUN_HANDLE
```

The normal success output is `MEMO_STATUS: ready`.

## Receipt override

The generated receipt is the ordinary path. If an operator must replace it,
submit the exact replacement text through `--kind receipt` after
`PRIVATE_INPUT_READY`. Then finalize with:

```bash
bash scripts/skill/finalize_and_archive.sh \
  --run-id RUN_HANDLE \
  --private-receipt-override
```

Do not put replacement text in a shell argument, heredoc, editor action, or
visible temporary-file write. The finalizer rejects simultaneous
`--receipt-file` and `--private-receipt-override`.

## Finalization

Prepare the verification packet instead of running ad hoc final queries. Then:

```bash
bash scripts/skill/finalize_and_archive.sh --run-id RUN_HANDLE
```

The generated receipt gives the same-context boundary, actual Observatory
status/URL, private-save confirmation, total known estimated cost, and a plain
health warning when needed. It does not expose temporary memo/log/archive
paths.

## Visible-surface truthfulness

The repository distinguishes:

- a curated narration artifact;
- a complete trusted host-visible transcript, when one is actually supplied;
- host tool cards/commands, which the repository may not observe;
- owner-only operator/run-event custody.

A clean curated narration is `not_checked`, with:

- `observed_scope: ["curated_live_transcript_artifact"]`;
- `complete_visible_surface_observed: false`;
- `complete_visible_surface_leak_count: null`.

The archive's `tool_calls: []` is paired with
`tool_call_coverage.status: not_observed`; it never means no host tools ran.
Surface-divergence comparison is explicitly limited to persisted revised prose
and the curated narration. `privacy.mode: local_only` is explicitly scoped to
archive storage and says nothing about provider egress or host UI visibility.

Only a complete trusted capture may claim the complete captured surface was
clean. Even then, the claim is about the supplied capture, not tool chrome the
host omitted.

## Provider and semantic nonchanges

This boundary adds no provider or embedding calls. It does not change:

- the six direct-active cap;
- outgoing one-hop ally/antagonist/tension graph expansion;
- graph active/reserve identity or order;
- four-lane prompts or outputs;
- model/provider routing or retry policy;
- V60 selection;
- same-context reconsideration;
- apply/reject/park or private disposition semantics.

The provider-free replay proves transport and structural custody only. It does
not prove better reasoning, graph relevance, user usefulness, semantic
understanding, or production readiness.
