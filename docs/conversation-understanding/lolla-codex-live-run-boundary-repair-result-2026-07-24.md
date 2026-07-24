# Lolla Codex live-run boundary repair result

Date: 2026-07-24

Status: provider-free implementation candidate; full-repository verification
and canonical publication are pending

Source incident: user-operated run `20260724T182631Z_b8cec8`

Provider calls used by this repair: **0**

Provider cost used by this repair: **USD 0.00**

## Result in one paragraph

The source run completed a substantive Lolla audit, but Codex exposed much of
the machinery used to produce it: the complete conversation, temporary paths,
revised prose, graph decisions, private-table decisions, V60 decisions, memo
fields, an invalid ledger, its repair, and ad hoc JSON queries. This repair
does not change the audit's reasoning or graph. It changes how an ordinary
Codex run transports and records private material. A run now has one exact
handle; private payload helpers wait until terminal echo is disabled; revised
prose and decisions enter through validated private standard input; bounded
consumer packets replace improvised artifact dumps; final receipts omit local
paths; and machine claims state exactly which visible surface, host tools,
provider boundary, and cost scope they did or did not observe.

## Falsifiable question

Can the existing Lolla audit pass a 14-message Codex-style provider-free replay
through source capture, extraction custody, graph custody, reconsideration
persistence, disposition validation, memo rendering, final receipt, archive,
and reasoning trace without placing private payloads or raw machinery in the
normal visible stream?

The replay is a mechanical development fixture. It tests transport and custody.
It does not test whether the revised advice is good, whether the graph supplied
the best lenses, or whether a real user finds Lolla useful.

## What the incident showed

The archived run and its visible Codex trace established different facts.

The archive established that:

- all 14 available user/assistant messages were preserved;
- the ordinary graph path ran with six direct items and three outgoing
  one-hop items;
- the reasoner received graph pressure and later recorded dispositions;
- revised prose, memo, archive, cost, and inspection artifacts existed;
- one of twelve optional passage checks returned no usable judgment, so the
  run was truthfully `partial`.

The visible trace established that:

- the first fresh shell did not retain the manually assigned environment-state
  path;
- the host sent source before the capture process had proved no-echo readiness,
  so the complete conversation was repeated;
- later private payloads were authored with visible heredocs and edit cards;
- broad `sed` and `jq` operations exposed internal structures;
- one invalid graph ledger was repaired in public;
- a final ad hoc query requested fields that did not exist and printed
  misleading nulls;
- the curated narration, operator log, run events, and reasoning trace did not
  observe those host-side operations.

The old archive's `live_output_health: not_checked` was therefore the correct
state. Its zero recorded leaks could not prove that the complete Codex-visible
surface was clean.

## Repairs

### One exact run handle

Setup prints one non-secret `RUN_HANDLE`. Every later ordinary helper accepts
that handle and loads only its matching guarded state, including from a fresh
shell. It does not follow the compatibility `lolla_latest_env.sh` pointer.
Missing, stale, incomplete, or mismatched state fails before private input is
read.

This removes the repeated manual pattern:

```text
copy an environment-file path
  -> start another shell
  -> forget to restore it
  -> improvise recovery
```

### One private-input protocol

Conversation source, product narration, the revised answer, three disposition
families, memo fields, and an exceptional receipt override now use the same
protocol:

```text
start helper with run handle and operation name
  -> helper disables terminal echo
  -> helper prints PRIVATE_INPUT_READY
  -> host sends private payload over process input
  -> helper validates and persists it
  -> helper prints one compact status
```

If no-echo setup fails, the helper stops before reading. The payload is not put
in a shell argument, heredoc, inline program, patch, or editor card. Files are
written owner-only.

### Deterministic ownership of ledger shape

The reasoner supplies only the fields it is authorized to judge. Deterministic
code owns exact IDs, order, immutable provenance, required field sets, and
identity coverage for:

- constitutional graph-survival decisions;
- private-table decisions;
- V60 affordance and absence decisions.

All candidate ledgers and the revised result are built and validated in memory
before any of them is replaced. An invalid packet emits one small failure
status, keeps the previous artifacts, and records safe failure custody without
copying the private payload into the event. Individual replacements are
atomic. The implementation does not claim a cross-file crash transaction
across every resulting artifact.

### Bounded consumer packets

The ordinary instructions no longer tell the host to inspect live artifacts
with arbitrary `sed`, `jq`, inline Python, or broad dumps. Deterministic code
prepares three named, owner-only views:

- `readback` for the source-grounded orientation;
- `reconsideration` for the exact pressure and disposition skeletons;
- `verification` for statuses, counts, source coverage, graph policy,
  validation state, and cost state.

The helper prints only a compact ready/unavailable status. The host may still
display its own file-read card when the reasoner consumes a packet. Repository
code cannot control that user-interface chrome.

### Runtime-root consistency

Current live helpers now resolve their run-scoped working files from the same
runtime root, with `/tmp` retained as the default. Tests can use an isolated
root without borrowing or overwriting unrelated machine runs. Archive
finalization, ledgers, memo, pressure-check state, usage sidecars, and run
events follow the exact run root.

### Truthful interface, privacy, trace, and cost claims

The machine artifacts now distinguish:

- curated narration from a complete trusted host-visible capture;
- observed leak count from complete-surface leak count;
- `tool_calls: []` from proof that no host tools ran;
- comparison of persisted prose from observation of the complete interface;
- owner-only local archive storage from provider egress or host UI privacy;
- the OpenRouter hard-budget scope from later observed or estimated whole-run
  vendor cost.

When only curated narration was supplied, complete-visible-surface coverage is
false and its complete leak count is null. A clean count is never promoted into
proof about unobserved Codex tool cards.

### Path-free ordinary completion

Ordinary success statuses and the final receipt no longer print temporary
environment, log, memo, or archive paths. The final receipt states health,
same-context reconsideration, Observatory availability, private-save
completion, and estimated cost. Detailed paths remain in owner-only operator
custody.

## Provider-free evidence

The focused boundary group passed **59 tests** before the final public-handoff
update. It includes:

- a fresh-shell test that deliberately points `lolla_latest_env.sh` at another
  run and proves the exact requested state still wins;
- true-PTY tests proving `PRIVATE_INPUT_READY` occurs before the source or
  narration is sent and that unique private markers do not appear in visible
  output;
- exact Step 6 skeleton reconstruction and owner-only mode checks;
- invalid-packet tests proving prior artifacts survive and safe failure custody
  contains no secret marker;
- consumer-packet tests proving only compact receipts reach the shell;
- output-health and reasoning-trace tests preventing full-surface or no-tool
  claims when the host surface was not observed;
- a provider-free 14-message Marcus replay through capture, synthetic
  extraction/result custody, graph-disposition persistence, memo, pressure
  state, finalization, archive, and reasoning trace.

The full replay removes provider and embedding keys and uses no provider
runner. Its visible stream is checked for source markers, revised prose, memo
prose, raw JSON, temporary paths, `Added`/`Edited` payload previews, and private
decision content.

The first full-repository pass produced 5,212 passes and 24 failures. Twenty
were expected git-state gates that require the intentionally changed live-skill
files to be committed. The remaining four exposed one repository-authority
count drift and three positional-helper compatibility cases; those four were
repaired and their focused tests pass. The suite will be repeated from the
narrow committed checkpoint before publication.

## What a user should expect

An ordinary future `$lolla` run may still show:

- Lolla's short progress narration;
- compact tool-operation cards owned by Codex;
- `PRIVATE_INPUT_READY` and short status receipts;
- the source-grounded readback, counterargument, updated position, and final
  receipt.

It should not normally show:

- the complete source conversation repeated by capture;
- revised prose or memo prose inside a command or patch;
- graph/private/V60 JSON bodies and repair ledgers;
- environment-state, temporary memo, operator-log, or archive paths;
- improvised schema queries and their raw diagnostics;
- private payloads in shell heredocs or file-edit previews.

## Unchanged graph and reasoning

This repair changes no canonical Markdown, relation, compiler, graph snapshot,
or selection policy. The live graph remains:

- at most six direct-active candidates;
- outgoing authored relations only;
- one expansion hop;
- bounded ally, antagonist, and tension slots;
- explicit active and reserve custody;
- apply, reject, or park disposition by the reconsidering reasoner.

It also changes no pressure prompt, model route, provider, retry rule, V60
selection, same-context reconsideration, or semantic admission rule.

## Limits and nonclaims

This result does not establish:

- that Codex can hide its own tool chrome;
- that a host-supplied surface capture includes UI material the host omitted;
- that provider-bound material remains local;
- that every multi-file update is one crash-atomic transaction;
- that a provider-backed live run will complete;
- that the source was interpreted correctly;
- that graph pressure uniquely caused an answer change;
- that more graph hops or graph-wide search would help;
- that the revised answer is better;
- that Lolla is useful to real users or production-ready.

The exact ordinary Codex transport contract is
[`docs/skill/CODEX_LIVE_RUN_BOUNDARY.md`](../skill/CODEX_LIVE_RUN_BOUNDARY.md).
The implementation register is
[`plans/lolla-codex-live-run-boundary-repair-2026-07-24.md`](../../plans/lolla-codex-live-run-boundary-repair-2026-07-24.md).
