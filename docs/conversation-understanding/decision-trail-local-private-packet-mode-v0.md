# Decision Trail Local-Private Packet Mode v0

Status: read-only local packet mode
Date: 2026-06-30
Slice: PR95 Decision Trail Local-Private Packet Mode v0

## Purpose

PR95 implements explicit `local_private_mode` for the Decision Trail specialist
packet builder.

PR91 proved that checked-in-safe packets can preserve custody, missingness, and
non-claims. PR93 and PR94 then showed the limit: checked-in-safe packets are too
thin for the messy interpretation fields users care about most.

PR95 does not fill those fields. It gives future offline specialist reads a
local-only packet surface that can inspect operator-selected completed run
artifacts while keeping deterministic custody around what was read, what was
not read, whether private text was copied into the local packet, and why the
output is unsafe to commit by default.

## Current Standing

PR95 is implemented and locally validated as a packet-preparation layer.

It means:

- checked-in-safe packet generation still works and remains the default;
- local-private packet generation can be run explicitly for an
  operator-selected completed run directory;
- metadata-only local-private packets can show what source material is
  available without copying private text;
- include-text local-private packets can copy capped private text into a local
  packet, but the output is unsafe for commit by default;
- the PR88 fixture-review input is retained as lineage only in local-private
  mode;
- packet content in local-private mode comes from the selected run artifacts
  and the PR90 specialist contract schema;
- raw transcript, revised-answer, and memo inclusion flags describe what was
  actually included, not merely which content mode was selected.

It does not mean:

- Lolla automatically runs Decision Trail specialists;
- likely actions, live options, stakeholders, values/priorities, assistant
  influence, useful/noisy friction, lost value, or fan-in are filled;
- local-private packet output is safe to share;
- human validation happened;
- Lolla improved a decision;
- an agent may act.

The next conservative step is a local-private packet smoke/review over one or
more operator-selected completed runs. That review should happen before any
contract-conforming specialist-output batch.

Completion note: PR96 has now performed that smoke/review:

- [Decision Trail Local-Private Packet Smoke Review v0](decision-trail-local-private-packet-smoke-review-v0.md)

PR96 found that metadata-only packets work over two real completed runs without
copying raw/private content, and that include-text packets work mechanically
with unsafe-for-commit marking. It still did not run specialists or prove
interpretation adequacy.

## Runtime Boundary

PR95 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- create specialist outputs;
- execute fan-in;
- score answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

The runtime remains the producer of completed run artifacts. The Decision Trail
packet lane remains an offline reader and packetizer.

## What Changed

The packet builder now supports two modes:

| mode | use |
|---|---|
| `checked_in_safe_mode` | Builds repo-safe packets from checked-in PR88 fixture-review context. This is still the default. |
| `local_private_mode` | Builds local-only packets from explicit operator-selected run directories. Output must go outside the repo and outside the run directory. |

Local-private mode adds:

- explicit `--mode local_private_mode`;
- required `--local-run-dir`;
- required `--out`;
- output-path rejection inside the selected run directory;
- output-path rejection inside the repository;
- repo-local fixture-review and contract-schema input refs;
- a local artifact read manifest;
- `metadata_only` and `include_text` content policies;
- truthful `raw_private_content_included` metadata;
- `commit_safety: unsafe_for_commit_by_default`;
- `requires_operator_review_before_share: true`;
- sanitized run refs that omit local absolute paths.

## Content Inclusion Modes

### `metadata_only`

This is the safer local-private default.

It records that artifacts exist, along with byte counts and statuses, but does
not read or copy private text into the output.

Use it to answer:

- which local artifacts are available;
- which local artifacts are missing;
- whether a future specialist pass would have enough source material available;
- what remains impossible to interpret without reading text.

### `include_text`

This mode copies local private artifact text into the packet output, capped by
`--max-text-chars` per artifact.

Use it only for local, operator-controlled review. The output is unsafe for
commit by default.

The packet records:

- `raw_private_content_included: true`;
- `raw_transcripts_included`, only when `conversation.txt` or
  `live_transcript.txt` text was actually included;
- `raw_revised_answers_included`, only when `revised.txt` text was actually
  included;
- `raw_memos_included`, only when `memo.md` text was actually included;
- `content_text`;
- `text_truncated`;
- `sha256` for included text;
- `commit_safety: unsafe_for_commit_by_default`.

This mode still does not interpret the conversation. It only makes source text
available to a future bounded specialist pass.

## How To Run

Metadata-only local-private packet:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --mode local_private_mode \
  --local-run-dir <archive-run-dir> \
  --content-inclusion metadata_only \
  --out /tmp/decision_trail_local_private_packets.json
```

Include private text in a local-only packet:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --mode local_private_mode \
  --local-run-dir <archive-run-dir> \
  --content-inclusion include_text \
  --max-text-chars 12000 \
  --out /tmp/decision_trail_local_private_packets_with_text.json
```

Do not write local-private outputs into the repo. The CLI rejects repo-local
output paths by default.

In local-private mode, the PR88 fixture review and PR90 contract schema inputs
must be repo-local. The PR88 fixture review is retained as a lineage/input
reference only; local-private packet content is built from the selected run
artifacts and the PR90 contract schema, not from PR88 review findings.

## What It Reads

Local-private mode inspects the same broad artifact family that the Decision
Trail report/exporter knows about:

- structured JSON artifacts such as `evaluation.json`, `agent_result.json`,
  `reasoning_trace.json`, `extraction_adequacy_report.json`, `extraction.json`,
  and `result.json`;
- private or raw local artifacts such as `conversation.txt`, `memo.md`,
  `revised.txt`, `live_transcript.txt`, `operator.log`, and private table or
  ledger artifacts.

In `metadata_only`, it records presence and byte counts.

In `include_text`, it reads text from available UTF-8 files and copies capped
text into the local packet output.

## What It Outputs

The output still uses:

```text
lolla.decision_trail_specialist_packets.v0
```

Every selected run gets all four PR90 packet roles:

- `conversation_shape_reader`
- `likely_action_reader`
- `friction_lost_value_reader`
- `conservative_fan_in_reader`

The packet output includes a local-private `available_context` with:

- `private_context_policy`;
- `local_private_artifacts_read`;
- `local_private_artifacts_not_read`;
- `redacted_or_private_refs`;
- `interpretation_needed_sections`;
- `overtrust_risk_sections`;
- `human_followup_questions`.

The packet builder does not fill specialist fields. It does not decide likely
actions, live options, assistant influence, useful friction, noisy friction, or
lost value.

The packet's raw-content family booleans describe what was actually included,
not merely which content mode was selected. For example, `include_text` with a
run that contains `conversation.txt` but no `memo.md` marks transcript content
included and memo content not included.

## Validation Meaning

Validation can show:

- local-private mode is explicit;
- output path guardrails work;
- the read manifest is deterministic;
- checked-in-safe fixtures remain private-content-free;
- include-text mode marks output unsafe and records private content inclusion;
- no runtime, provider, model, archive mutation, scoring, judging, or automatic
  labeling path was added.

Validation cannot show:

- the packet has enough context for a good specialist read;
- future specialists will interpret conversations correctly;
- a local-private packet is safe to share;
- Lolla improved any decision;
- human review happened;
- an agent may act.

## Relationship To PR94

PR94 selected local-private packet mode because the bottleneck was source
access, not contract shape.

PR95 implements that selected path narrowly. It does not create a broader
conversation-understanding IR, a specialist batch, a runtime integration, a
judge, or a product-proof report.

## Next Step

After PR96, the next conservative slice was a tiny local-private
specialist-output pilot over one or two operator-selected completed runs. PR97
has now completed the one-case version of that pilot:

- [Decision Trail Local-Private Specialist Output Pilot v0](decision-trail-local-private-specialist-output-pilot-v0.md)

PR97 asked:

- can the four PR90 specialist roles fill contract-shaped outputs from
  local-private packets without overclaiming;
- do likely-action, conversation-shape, friction/lost-value, and conservative
  fan-in reads preserve uncertainty and source refs;
- do local-private packets create too much private-content handling risk;
- do source refs remain readable after specialist outputs are added;
- should PR90 contracts or PR95 packet shape change before broader use?

The pilot found that the local-private packet path is usable for one bounded
specialist-output pass, but it also made the private-content/truncation and
one-case limitations impossible to ignore.

If local-private packets are too risky or too bulky, the lane should simplify
before adding more interpretation machinery.

The next conservative slice was PR98: review the PR97 specialist outputs and
decide whether contracts or packet shape should change before any broader
batch.

Completion note: PR98 has now performed that review:

- [Decision Trail Specialist Output Pilot Review v0](decision-trail-specialist-output-pilot-review-v0.md)

PR98 decided that packet shape should change before reuse. The next packet
patch should add role-readable source-scope metadata, truncation impact, and
local-private retention/deletion status before a second one-case pilot.
