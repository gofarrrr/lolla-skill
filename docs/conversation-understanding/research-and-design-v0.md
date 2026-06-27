# Conversation Understanding Research And Design v0

Status: design proposal
Last updated: 2026-06-27

This note is a research/design slice. It does not propose a runtime rewrite, a
new memory product, a graph database, an LLM judge, or a change to `SKILL.md`.

The goal is narrower:

Build a source-grounded conversation-understanding layer that helps Lolla
preserve the reasoning material inside messy conversations: constraints,
commitments, options, reversals, dropped threads, gates, claims, and audit
hinges.

Lolla should not become generic personal memory. It should remain a local
reasoning-audit harness. The raw transcript stays the source of truth; extracted
structure is a reviewable, fallible, cost-accounted artifact.

## Current Lolla Baseline

The current system already has a strong harness foundation:

- `conversation.txt` is captured as the raw source conversation.
- `scripts/run_extract.py` performs one semantic extraction pass and writes
  `extraction.json`.
- `engine/system_b/conversation_context.py` defines the runtime
  `ConversationContext` shape: turns, live constraints, synthesized position,
  reasoning passages, dropped threads, capture metadata, and capture adequacy.
- `engine/system_b/capture_adequacy.py` deterministically records capture shape:
  declared/captured/omitted turns, captured windows, omitted windows, risk
  flags, and status.
- `agent_result.json` gives callers a conservative machine-readable result.
- `reasoning_trace.json` indexes artifacts, hashes, run health, capture
  adequacy, control-plane summaries, and custody metadata without duplicating
  raw transcript text.
- `evaluation.json` checks the run envelope and policy consistency, not answer
  quality.
- The review corpus exports compact run metadata and blank human-review fields
  without copying transcript, memo, revised answer, raw model messages, or
  control-action argument values.

That is good scaffolding. The remaining gap is not "more artifacts." The gap is
that Lolla still lacks a durable, source-grounded record of what the conversation
established before the audit began.

### Existing Local Prior Art To Reuse

This design should not be read as "start a new IR from scratch." Lolla already
has local IR and specialist-extractor work that any next implementation must
measure and reuse before introducing another ontology:

- `engine/system_b/ir.py` defines the provenance-bearing runtime
  `ConversationIR` plus `Turn`, `TurnRef`, `SpanRef`, `SpanProvenance`,
  `TurnRefProvenance`, `DerivationProvenance`, `FrameAnchor`,
  `UserIssueEvent`, `StanceEvent`, and `drill_back(...)`.
- `engine/system_b/ir_constructor.py` builds `ConversationIR` from
  `ConversationContext`. In default production wiring this construction is
  deterministic and conservative: paraphrased extraction fields become
  turn-reference or derivation-provenance objects rather than invented exact
  spans.
- `engine/system_b/live_constraints_extraction.py` is an LLM-backed specialist
  extractor for user-side live constraints. It emits verbatim-grounded
  `UserIssueEvent` objects with `SpanProvenance` or validated multi-turn
  `DerivationProvenance`.
- `engine/system_b/dropped_threads_extraction.py` is an LLM-backed specialist
  extractor for dropped threads raised by either user or assistant. It rejects
  paraphrase and keeps single-turn substring grounding.
- `engine/system_b/stance_extraction.py` is an LLM-backed specialist extractor
  for assistant stance events: commitments, revisions, qualifications,
  conditions, deferrals, and initial stances, each anchored to a verbatim
  assistant span.
- `docs/how-it-works/live-flow.md` documents the current boundary: production
  constructs `ConversationIR` without specialist extractors by default, while
  tests, eval harnesses, and ad-hoc callers can inject `stance_extractor`,
  `live_constraints_extractor`, and `dropped_threads_extractor`.

The naming boundary is:

- `ConversationIR` is the current runtime lane-input representation.
- `conversation_understanding_ir.v0`, if pursued, is an offline/archive
  reasoning-custody artifact or projection. It is not a runtime replacement in
  v0.

The first implementation should therefore measure the existing chain before it
names or persists anything new:

```text
conversation.txt -> extraction.json -> ConversationContext -> ConversationIR
```

Only if that measurement shows gaps the existing `ConversationIR` and
specialist extractors cannot carry should Lolla introduce a broader durable
conversation-understanding artifact.

Today, extraction has useful but blunt fields:

- `decision_situation`
- `live_constraints`
- `synthesized_position`
- `reasoning_passages`
- `original_framing`
- `dropped_threads`

For a short conversation this is often enough. For long or messy conversations,
the current shape is too compressed to answer questions like:

- Which assistant recommendation did the audit actually pressure?
- Which user constraints were current, superseded, contradicted, or unresolved?
- Which options appeared and disappeared?
- Which assistant commitments or domain claims later became load-bearing?
- Which middle-turn hinge was omitted by capture?
- Which revised-answer claims trace back to transcript evidence?

The next layer should answer those questions without pretending to prove
semantic correctness.

## Research Survey

The systems below are useful references, but none should be copied wholesale.
Most are generic memory/context engines. Lolla needs a reasoning-specific
conversation record.

| System | Representation | Provenance | Temporal handling | Extraction method | Update strategy | Cost strategy | Brittleness risk | Relevance to Lolla |
|---|---|---|---|---|---|---|---|---|
| [Graphiti / Zep](https://github.com/getzep/graphiti), [Zep docs](https://help.getzep.com/graphiti/getting-started/overview), [Zep paper](https://arxiv.org/html/2501.13956v1) | Temporal context graph with episodes, entities, relationship/fact edges, and optional custom entity/edge types. | Strong: episodes are raw ingested data and derived entities/facts trace back to episodes. | Strong: facts have validity windows and invalidation rather than deletion. | LLM-based entity/fact extraction, entity resolution, temporal extraction, graph insertion. | Incremental graph construction; new facts can invalidate older facts. | Hybrid semantic, keyword, and graph retrieval; graph DB/runtime infrastructure. | Overkill for Lolla v0; graph schemas, DB ops, entity resolution, and fact invalidation can become the product instead of the audit. | Copy the episode/provenance/temporal invalidation ideas. Do not adopt graph DB integration yet. |
| [Mem0](https://github.com/mem0ai/mem0), [migration docs](https://docs.mem0.ai/migration/oss-v2-to-v3), [graph memory docs](https://docs.mem0.ai/platform/features/graph-memory) | Memories as records, entity-linked graph memory, user/session/agent scopes. | Moderate: memories originate from added content, but the product is optimized for recall rather than custody. | Newer algorithm emphasizes temporal recall and ADD-only extraction in OSS migration docs. | LLM extracts memories; entities are extracted and linked; retrieval fuses vector, BM25, and entity signals. | ADD-only in current OSS migration path; graph memory links facts by entities/co-occurrence. | Hybrid signals and graceful degradation when optional dependencies are missing. | User-personalization bias; memory may store what is useful to recall rather than what is needed to audit a reasoning path. | Copy multi-signal retrieval and graceful degradation. Avoid user-only memory bias and unlabeled assistant-commitment loss. |
| [Supermemory](https://github.com/supermemoryai/supermemory) | Memory/context engine with facts, profiles, RAG, connectors, and a single memory structure/ontology. | Product docs emphasize extraction from conversations and connectors more than per-claim custody. | Handles temporal changes, contradictions, and automatic forgetting. | Automatic extraction, profiles, hybrid search, connectors, multimodal ingestion. | Background learning across conversations and sources. | API/local modes; abstracts vector/chunking details away from developers. | Too generic for Lolla; "remember the user" is not the same as "audit this answer's reasoning basis." | Copy the idea that memory should be easy to consume and local-capable. Avoid becoming a broad personal brain. |
| [LangMem](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) / LangGraph memory concepts | Semantic, episodic, and procedural memory; profiles or collections; optional schema-specific memory managers. | Depends on developer schema and store; can preserve episodes as structured memories. | Explicitly distinguishes when memories are formed: hot path versus background. | LLM determines how to expand or consolidate memory state. | Application-specific insert/consolidate/update flows. | Background formation avoids latency; hot-path formation is immediate but costly. | Memory consolidation can silently encode product taste if not source-grounded. | Copy the semantic/episodic/procedural distinction and hot-path/background cost split. |
| [LlamaIndex memory](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/) | Short-term chat history plus long-term memory blocks: static, fact extraction, vector. | Vector blocks can store message batches; fact blocks summarize/extract. | Older messages can flush into long-term blocks after token thresholds. | LLM fact extraction block; vector memory block for retrieved chat batches. | Memory blocks are prioritized and truncated when over budget. | Token limits, flush sizes, priority-based truncation. | Fact extraction blocks can become lossy summaries; vector retrieval does not know what is load-bearing. | Copy block separation and priority budgeting. Avoid retrieval-only truth. |
| [Letta / MemGPT memory](https://www.letta.com/blog/agent-memory/) | Message buffer, core memory blocks, recall memory, archival memory. | Recall stores conversation history; archival stores processed/indexed knowledge. | Memory is framed as context engineering: which tokens enter the window. | Agent-managed memory tools and possible sleep-time memory agents. | Memory can be edited by agents or specialized background agents. | Hierarchy keeps immediate context small and pushes heavier maintenance out of the live path. | Autonomous self-editing memory can create false authority unless edits are auditable. | Copy memory tiers: raw transcript, compact IR, optional retrieval surface. Avoid agent self-editing Lolla's audit record. |
| [Cognee](https://github.com/topoteretes/cognee) | Persistent memory platform combining knowledge graph, vector search, ontology generation, and data pipelines. | Emphasizes traceability and audit traits in a broader memory platform. | Knowledge evolves as data is ingested and connected. | Ingest/cognify/load style pipeline over documents and memories. | Continuous graph building and recall. | Infrastructure-heavy but self-hosted/local-capable. | Graph-first systems can force premature ontology design. | Copy the pipeline separation and audit posture. Avoid graph-first implementation in v0. |
| [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | Raw sources plus LLM-maintained wiki plus a schema/instruction file. | Strong if raw sources are immutable and the wiki cites them. | The wiki is maintained over time; contradictions and stale claims can be noted. | LLM compiles sources into interlinked Markdown pages. | Incremental ingest, query, lint, and log operations. | Moderate scale can work with an index/log before heavier search. | LLM-maintained synthesis can drift if source citations and lint are weak. | Copy "compiled artifact over raw RAG" and append-only log. For Lolla, the compiled artifact should be JSON custody plus optional Markdown views, not a freeform wiki. |
| [GBrain](https://github.com/garrytan/gbrain) | Local/hosted brain with schema packs, capture/import, hybrid search, synthesis with citations and gap analysis. | Emphasizes source pages, citations, local capture, and schema-pack boundaries. | Trajectory/gap analysis distinguishes stale, uncited, contradictory, or missing knowledge. | Hybrid retrieval plus synthesis; schema packs determine how pages are interpreted. | Capture/import workflows and schema-pack evolution. | Raw search is cheaper; synthesized `think` path costs more. | Broad brain systems optimize for reusable knowledge, not necessarily audit-lineage. | Copy the separation between raw retrieval and synthesized answers with gap analysis. Avoid turning Lolla into a general "brain." |
| Dialogue-history graph research, e.g. [IWSDS 2025 paper](https://aclanthology.org/2025.iwsds-1.31.pdf) and [GraphWOZ](https://arxiv.org/abs/2211.12852) | Dialogue, turns, semantic units, conversational entities, and graph dialogue state. | Turn-level structure makes references and updates auditable. | Dialogue states update incrementally as turns/actions occur. | Manual or model-assisted annotations/extractions. | New turns update the graph/dialogue state. | Research setups can require detailed annotation or domain constraints. | Domain-specific graphs can be brittle in open-ended strategic conversations. | Copy the layers: turns -> semantic units -> entities/relations. Keep Lolla's ontology small and escape-hatch friendly. |
| Current Lolla extraction | `ConversationContext` with turns, live constraints, dropped threads, synthesized position, reasoning passages, capture metadata. | Partial: raw transcript persists; reasoning passages are quote-validated; constraints/threads have turn references but not quote spans. | Partial: constraints have active/dropped/modified; dropped threads have unresolved statuses; capture adequacy records omitted windows. | Single LLM extraction over full or truncated transcript, plus deterministic quote validation for reasoning passages. | Per-run artifact; no cross-run or incremental semantic memory yet. | One extraction call; long conversations use first-3/last-15 truncation after char cap. | Can miss middle-turn hinges, assistant commitments, changed options, and non-quoted constraints. | Use as substrate. Add a source-grounded IR beside it rather than replacing it first. |

## Design Position

Lolla should build a reasoning-specific conversation record, not a generic memory
store.

Generic memory asks:

> What should an agent remember for future personalization or retrieval?

Lolla asks:

> What did this conversation establish that the audit must preserve, pressure,
> contradict, or qualify?

That means Lolla's conversation-understanding layer should prioritize:

- decision options,
- constraints and stakeholder boundaries,
- assistant recommendations and commitments,
- factual/domain claims,
- gates and stop conditions,
- reversals and changed stances,
- dropped threads and open loops,
- unresolved uncertainty,
- final-position lineage,
- source evidence and missing evidence.

It should not prioritize:

- all user preferences,
- generic entity recall,
- a permanent personal graph,
- reusable profile memory,
- raw document RAG,
- automatic action approval,
- answer-quality scoring.

## Proposed Artifact: `conversation_understanding_ir.v0`

This name is provisional. It should not create a second source of truth beside
the existing runtime `ConversationIR`.

The safe interpretation is:

> `conversation_understanding_ir.v0` is an offline/archive reasoning-custody
> projection that can reuse `ConversationIR` primitives and specialist
> extractor outputs. It is not a runtime replacement in v0.

PR20 should test whether the existing `ConversationIR` plus provenance reports
are already enough for the first durable artifact. If they are, the eventual
artifact may be a persisted/exported `ConversationIR` view plus adequacy
metadata rather than a wholly new shape.

The proposed artifact is an archive-time/offline JSON artifact:

```text
conversation.txt
extraction.json
conversation_understanding_ir.json
result.json
agent_result.json
reasoning_trace.json
evaluation.json
```

The artifact should be generated after the existing transcript and extraction
exist. In v0 it should not block the live `/lolla` path.

### Top-Level Shape

```json
{
  "schema_version": "lolla.conversation_understanding_ir.v0",
  "created_at": "2026-06-26T00:00:00Z",
  "run_id": "20260626T000000Z_example",
  "case_id": "example-case",
  "source": {
    "conversation_path": "conversation.txt",
    "conversation_sha256": "sha256:...",
    "extraction_path": "extraction.json",
    "extraction_sha256": "sha256:...",
    "raw_transcript_is_source_of_truth": true
  },
  "scope": {
    "artifact": "conversation_understanding",
    "runtime_blocking": false,
    "model_calls": 0,
    "llm_judge_used": false,
    "advice_quality_scored": false
  },
  "turns": [],
  "items": [],
  "relations": [],
  "coverage": {},
  "validation": {},
  "cost": {}
}
```

### Turn Records

Turn records are deterministic and should come from the same parser used by
`load_conversation_context()`.

```json
{
  "turn_id": "turn_015",
  "turn_index": 15,
  "role": "user",
  "char_start": 12421,
  "char_end": 12888,
  "sha256": "sha256:...",
  "captured": true,
  "window": "recent"
}
```

The deterministic turn layer is important because every semantic item should
point back to a source turn.

### Semantic Items

Each extracted object should have a stable id, type, source, evidence, state,
confidence, visibility, and review flags.

```json
{
  "id": "constraint_001",
  "type": "constraint",
  "facet": "constraint",
  "text": "Spouse consent is a hard gate before accepting the startup role.",
  "source_role": "user",
  "source_turn_ids": ["turn_015"],
  "evidence": [
    {
      "turn_id": "turn_015",
      "quote": "my wife has to be really on board",
      "span": {
        "char_start": 12603,
        "char_end": 12637
      },
      "match_status": "verified"
    }
  ],
  "state": "current",
  "confidence": "high",
  "extraction_status": "extracted",
  "visibility": "public",
  "ambiguity_notes": [],
  "needs_review": false
}
```

Recommended v0 `type` values:

- `decision`
- `option`
- `constraint`
- `stakeholder`
- `gate`
- `assistant_recommendation`
- `assistant_commitment`
- `assistant_claim`
- `user_fact`
- `user_preference`
- `reversal`
- `changed_stance`
- `dropped_thread`
- `open_question`
- `uncertainty`
- `evidence_gap`
- `audit_hinge`
- `other`

Recommended `facet` values:

- `factual`
- `preference`
- `recommendation`
- `constraint`
- `question`
- `option`
- `inference`
- `commitment`
- `domain_claim`
- `process`
- `other`

Recommended `state` values:

- `current`
- `superseded`
- `contradicted`
- `unresolved`
- `dropped`
- `unknown`

Recommended `visibility` values:

- `public`
- `private`
- `review_only`

Recommended `confidence` values:

- `high`
- `medium`
- `low`
- `uncertain`

The `other`, `unknown`, `uncertain`, and `needs_review` escape hatches are not
cosmetic. They prevent the ontology from forcing false precision.

### Relations

Relations should be simple in v0. The point is lineage, not graph-theory
completeness.

```json
{
  "id": "rel_001",
  "source_id": "recommendation_001",
  "relation": "depends_on",
  "target_id": "constraint_001",
  "source_turn_ids": ["turn_015"],
  "confidence": "medium",
  "state": "current",
  "needs_review": false
}
```

Recommended relation values:

- `depends_on`
- `contradicts`
- `supersedes`
- `supports`
- `weakens`
- `qualifies`
- `raises`
- `answers`
- `ignores`
- `related_to`

`related_to` should remain available as a low-precision fallback.

### Coverage

Coverage should summarize what the IR claims to cover and what it knows it may
have missed.

```json
{
  "turn_count": 30,
  "captured_turn_count": 30,
  "omitted_turn_count": 0,
  "semantic_item_count": 42,
  "item_counts_by_type": {
    "constraint": 6,
    "assistant_recommendation": 3,
    "audit_hinge": 4
  },
  "source_turns_with_items": ["turn_001", "turn_004", "turn_015"],
  "source_turns_without_items": ["turn_002", "turn_003"],
  "omitted_windows": [],
  "known_limitations": [
    "Semantic extraction is not proof of correctness."
  ]
}
```

### Validation

Validation must stay deterministic and modest. It can check custody and
structural claims. It cannot check whether a semantic item is truly wise,
important, or complete.

Recommended checks:

- `schema_version` is expected.
- source conversation exists and hash matches.
- source extraction exists and hash matches.
- every `source_turn_id` exists.
- every claimed quote span exists inside its source turn.
- every relation endpoint exists.
- each item has an allowed type/facet/state/confidence/visibility value.
- no item stores raw system/tool dumps.
- no item stores provider reasoning details.
- extracted quote text is bounded in length.
- unknown/uncertain/needs-review states are allowed and counted.
- cost metadata is present.

Validation should not claim:

- "all important constraints were found,"
- "the revised answer improved,"
- "this run is agent-usable,"
- "the extracted item is semantically correct,"
- "the answer is domain-safe."

Those belong to human review, future calibrated checks, or external domain
systems.

## Cost Model

The first implementation should be offline and diagnostic.

Recommended cost posture:

1. Start with deterministic adequacy over current artifacts.
   - Count which existing extraction fields have turn references.
   - Count which fields have quote/source evidence.
   - Report missing provenance.
   - Do not call a model.
2. Aggregate extraction adequacy across archived runs before choosing a repair.
   - Reuse existing `extraction_adequacy_report.json` files when present.
   - Build reports in memory for older archives when source artifacts exist.
   - Keep the survey local-only, read-only, and free of raw transcript text.
3. Prototype `conversation_understanding_ir.v0` only if the corpus survey shows
   that a durable projection is the right next repair.
4. Cache future semantic artifacts by conversation hash and by window hash.
5. Use deterministic segmentation before LLM calls:
   - turn parsing,
   - speaker windows,
   - capture windows,
   - assistant-final-position windows,
   - constraint-bearing user-turn candidates.
6. Use LLMs only for semantic interpretation, not for source matching.
7. Verify quotes and spans deterministically after extraction.
8. Store token/cost metadata before considering live integration.
9. Keep embeddings optional and later. They may help candidate retrieval, but
   they should not become the trust mechanism.

This gives Lolla a way to learn whether richer conversation understanding is
useful before putting cost into the hot path.

## Brittleness Model

The dangerous failure modes are predictable:

| Failure mode | What it looks like | Mitigation |
|---|---|---|
| Over-extraction | The IR fills with trivia and becomes expensive/noisy. | Type allowlist, item count caps, importance/needs-review fields, review corpus checks. |
| Under-extraction | The middle-turn hinge is still missing. | Coverage reports, omitted-window flags, human review labels, fixture tests with known hinges. |
| Hallucinated item | LLM invents a constraint or claim. | Required source turn and quote/span verification where possible. |
| Assistant commitment loss | The system records user facts but not what the assistant promised or recommended. | First-class `assistant_recommendation`, `assistant_commitment`, and `assistant_claim` types. |
| Stale/superseded item | Old facts remain current after the user changes stance. | `state`, `supersedes`, `contradicts`, and append-only lineage. |
| False ontology precision | The extractor forces an ambiguous item into the wrong type. | `other`, `related_to`, `uncertain`, `needs_review`. |
| Broken provenance | A reviewer cannot find where an item came from. | Deterministic source-turn and quote-span validation. |
| Cost creep | Semantic extraction silently moves into every live run. | Offline-first artifact, cost metadata, cache by hash, no live-blocking v0. |
| Privacy leak | The IR copies raw transcript, tool dumps, provider reasoning details, or control arguments. | Bounded excerpts only, visibility flags, deterministic banned-surface checks. |

## What To Copy, Adapt, And Avoid

Copy:

- Graphiti/Zep's episode-first provenance and invalidation-over-deletion.
- LangMem's distinction between semantic, episodic, and procedural memory.
- LlamaIndex's block separation and priority/cost thinking.
- Letta's memory hierarchy, especially raw recall versus processed archival
  memory.
- Mem0/Supermemory's practical extraction/retrieval ergonomics and graceful
  degradation.
- Karpathy's compiled artifact pattern: raw sources remain immutable, derived
  knowledge compounds, and linting keeps it honest.
- GBrain's split between raw retrieval and synthesized answers with gap
  analysis.
- Dialogue-history graph layering: turns first, semantic units second,
  entities/relations third.

Adapt:

- Temporal validity becomes `current/superseded/contradicted/unresolved`, not a
  full graph DB in v0.
- Entity resolution becomes stable ids and simple relations, not broad
  cross-run personal memory.
- Search can start with JSON/Markdown/corpus exports before embeddings.
- Gap analysis becomes extraction adequacy and evidence-gap reporting.

Avoid:

- Graph DB integration before evidence.
- Embeddings-first capture.
- A broad user profile memory.
- Assistant self-editing of the audit record.
- Freeform wiki pages as the only machine-readable artifact.
- Hot-path extraction cost before offline pilots prove value.
- LLM judges for answer quality.
- Automatic human labels.
- Hard ontology gates that make uncertain material disappear.

## Phased Implementation Plan

### PR20: Deterministic Extraction Adequacy Report

Goal: measure current extraction's source-grounding before adding new semantic
extraction.

Scope:

- Add a deterministic report over the existing transformation chain:
  `conversation.txt -> extraction.json -> ConversationContext ->
  ConversationIR`.
- Count extraction fields, turn references, quote-validated fields, missing or
  invalid turn refs, and omitted-window exposure.
- Surface whether `live_constraints` and `dropped_threads` are only turn-linked
  or also quote-linked.
- Build `ConversationContext` and `ConversationIR` in the same default mode as
  production, then report provenance tiers from the constructed IR.
- Answer where provenance is preserved, weakened, or lost between raw
  extraction, `ConversationContext`, and `ConversationIR`.
- Report which existing specialist extractors could fill each gap:
  `live_constraints_extraction`, `dropped_threads_extraction`, and
  `stance_extraction`.
- Add the report as an optional archive artifact, e.g.
  `extraction_adequacy_report.json`.
- Index it in `reasoning_trace.json` only if present.
- Add deterministic tests with synthetic conversations.

Non-goals:

- no model calls,
- no new extraction prompt,
- no runtime behavior change,
- no answer-quality evaluation,
- no graph DB,
- no embeddings.

This is the safest next PR because it tells us exactly how much provenance the
current system already has, including what the runtime IR already preserves.

### PR21: Extraction Adequacy Corpus Survey

Goal: aggregate the per-run adequacy reports across the local archive corpus
before building any new extraction intelligence.

Scope:

- Add a read-only corpus exporter that scans archived runs and writes a local
  JSONL record plus aggregate manifest.
- Prefer existing `extraction_adequacy_report.json` when present.
- For older archives, build the report in memory from `conversation.txt`,
  `extraction.json`, `ConversationContext`, and `ConversationIR` when possible,
  without mutating the archive.
- Count adequacy statuses, capture adequacy statuses, capture strategies,
  invalid/missing/speaker-mismatched turn refs, quote-fabrication counts,
  omitted turns, ConversationContext availability, ConversationIR availability,
  and specialist-extractor opportunity counts.
- Bucket runs deterministically into review groups such as
  `critical_extraction_review`, `warning_extraction_review`,
  `legacy_missing_report_review`, `clean_baseline_sample`, and
  `not_reviewable`.
- Keep the export local-only and privacy-bounded: no raw transcript text, memo
  text, revised-answer text, raw model messages, provider reasoning details,
  raw exception strings, fabricated passage text, or control-action argument
  values.

Non-goals:

- no model calls,
- no new extraction prompt,
- no archive mutation by default,
- no new IR,
- no answer-quality evaluation,
- no graph DB,
- no embeddings.

This PR should answer which extraction/provenance failures are common enough to
deserve engineering before Lolla adds smarter extraction, specialist-extractor
reuse, chunking changes, or a durable conversation-understanding projection.

### PR22: Extraction Adequacy Findings And Drilldown

Goal: read the PR21 corpus map before building new extraction machinery.

Scope:

- Add a deterministic analyzer for the PR21 JSONL corpus and manifest.
- Produce a compact Markdown findings report and machine-readable JSON summary.
- List critical and warning records by case/run/path without raw transcript,
  memo, revised-answer, model-message, provider-reasoning, or control-argument
  text.
- Identify invalid turn-ref records, quote-fabrication records, legacy metadata
  limits, specialist-extractor opportunities, and whether warning patterns are
  concentrated or spread.
- Choose one narrow next slice from the measured evidence.

Non-goals:

- no model calls,
- no new extraction prompt,
- no runtime behavior change,
- no new IR,
- no answer-quality evaluation,
- no graph DB,
- no embeddings,
- no human-review automation.

This PR should answer what the 11 warning records and 1 critical record teach us
before Lolla commits to quote repair, turn-ref repair, specialist extraction, or
any durable conversation-understanding projection.

### PR23: Quote Validation Failure Classifier

Goal: classify quote-validation failures before repairing matcher tolerance,
retry prompting, or extraction prompting.

Scope:

- Read the PR22 findings JSON to identify records with quote fabrication.
- Inspect only those local archive folders.
- Compare stored failed passages against the archived conversation text using
  current `find_substring_tolerant(...)` first, then diagnostic-only
  normalization checks.
- Classify failures as current-matcher accepted, linebreak/whitespace/unicode
  formatting mismatch, high-token-overlap near match, true paraphrase/no match,
  or empty/invalid passage.
- Export only hashes, lengths, counts, turn indexes/speakers, token-overlap
  scores, retry metadata, and repair recommendations.

Non-goals:

- no runtime quote-validation change,
- no matcher loosening,
- no prompt change,
- no model calls,
- no LLM judge,
- no answer-quality evaluation,
- no graph DB,
- no embeddings,
- no new IR,
- no human-review automation.

This PR should decide whether the quote-validation repair should target matcher
tolerance, retry prompting, extraction prompting, legacy-only no-op plus a new
smoke, or a split repair plan.

### PR24: Modern Extraction Baseline Findings

Goal: record the modern current-main baseline before moving beyond quote
validation diagnostics.

Scope:

- Document the four modern clean baseline runs.
- Record that quote fabrication stayed historical and did not reproduce in the
  modern samples.
- Close quote-validation runtime repair for now.
- Keep provider-boundary degradation on a separate policy track.
- Explicitly state that clean quote/capture/turn-ref mechanics do not prove
  full conversation understanding.

Non-goals:

- no runtime quote-validation change,
- no matcher loosening,
- no prompt change,
- no provider-boundary policy change,
- no `conversation_understanding_ir.v0`,
- no graph DB, embeddings, chunking, or LLM judge.

### PR25: Semantic Extraction Review Pilot

Goal: review whether the current artifacts preserve the important reasoning
work from a small set of modern conversations before building a new durable IR.

Status: completed/current evidence note. See
[semantic-extraction-review-pilot-v0.md](semantic-extraction-review-pilot-v0.md).

Outcome: Decision B. Current artifacts preserve quote/capture/turn-reference
mechanics, but important semantic hinges are scattered across extraction,
result cards, revised answer, memo, and agent/evaluation artifacts, or only
partially preserved.

Scope:

- Compare `conversation.txt`, `extraction.json`,
  `extraction_adequacy_report.json`, `result.json`, `revised.txt`, and
  `memo.md` for a small modern sample.
- Review whether extraction captured the real decision, live constraints, user
  values, changed constraints, dropped threads, assistant overconfidence,
  counter-pressure, revised-answer change reason, unanswered dimensions, and
  actionability boundaries.
- Keep the review evidence-local and custody-bounded.
- Use findings to decide whether the next slice should be documentation,
  deterministic coverage reporting, specialist-extractor evaluation, or a later
  offline conversation-understanding prototype.

Non-goals:

- no production extraction rewrite,
- no new runtime prompt,
- no graph DB or embeddings,
- no answer-quality judge,
- no automatic human-review labels.

### PR26: Semantic Coverage Report v0

Goal: build a deterministic, offline report over existing archive artifacts
that shows where semantic evidence lives, how strongly it is grounded, and what
is missing.

Design note:
[semantic-coverage-report-v0.md](semantic-coverage-report-v0.md).

Scope:

- Read only existing local archive artifacts.
- Report coverage for decision, live constraints, user values/priorities
  signal, changed constraints or later pushback, dropped threads, assistant
  stance lineage, counter-pressure, revised-answer change reason, unanswered
  dimensions, and actionability boundaries.
- Emit hashes, counts, artifact ownership, grounding type, status, and
  review-needed flags.
- Keep the report offline/local before any archive integration.

Non-goals:

- no runtime behavior change,
- no model calls,
- no prompt changes,
- no new IR,
- no graph DB, embeddings, or chunking,
- no `SKILL.md` change,
- no provider-boundary policy change.

### PR27: Semantic Coverage Corpus Survey v0

Goal: run the PR26 semantic coverage report across archived runs and aggregate
the repeated status, grounding, artifact-availability, and review-bucket
patterns.

Design note:
[semantic-coverage-corpus-survey-v0.md](semantic-coverage-corpus-survey-v0.md).

Scope:

- Prefer existing `semantic_coverage_report.json` when present.
- Otherwise build semantic coverage reports in memory without mutating
  archives.
- Export local JSONL corpus records and an aggregate manifest.
- Count semantic element statuses and grounding types by element.
- Keep the survey offline/local and privacy-bounded.

Non-goals:

- no runtime behavior change,
- no archive integration,
- no prompt changes,
- no model calls,
- no new IR,
- no graph DB, embeddings, or chunking,
- no provider-boundary policy change,
- no `SKILL.md` change.

### PR28: Existing Specialist Extractor Offline Probe v0

Goal: inspect whether existing specialist extractors can close repeated
semantic coverage gaps before adding new IR, new extractors, or runtime
integration.

Design note:
[specialist-extractor-offline-probe-v0.md](specialist-extractor-offline-probe-v0.md).

Scope:

- Review `live_constraints_extraction`, `stance_extraction`, and
  `dropped_threads_extraction`.
- Confirm whether each extractor can improve grounding from `turn_ref` or
  `artifact_present_only` to span-grounded IR objects.
- Identify model-call, cost, validation, and custody requirements for a future
  offline runner.
- Keep this PR docs-only because the current specialist APIs require LLM
  boundary calls to generate candidate events.

Non-goals:

- no runtime behavior change,
- no model calls,
- no prompt changes,
- no new user-values extractor,
- no new IR,
- no graph DB, embeddings, or chunking,
- no provider-boundary policy change,
- no `SKILL.md` change.

### PR29A: Specialist Extractor Probe Runner Harness v0

Goal: build the local/offline runner contract for probing existing specialist
extractors without making real model calls.

Design note:
[specialist-extractor-probe-runner-v0.md](specialist-extractor-probe-runner-v0.md).

Scope:

- Load one archive run directory.
- Build baseline semantic coverage in memory.
- Load `ConversationContext` from existing archive artifacts.
- Run selected specialist extractors through an injected fake boundary.
- Rebuild `ConversationIR` with existing injection hooks.
- Compare baseline and specialist-enhanced semantic coverage.
- Export deterministic JSON with candidate counts, validation counts,
  grounding counts, improvement flags, and zero model-call counters.
- Keep the harness read-only and custody-bounded.

Non-goals:

- no real model calls,
- no OpenRouter calls,
- no runtime behavior change,
- no archive mutation,
- no archive integration,
- no prompt changes,
- no new user-values extractor,
- no new IR,
- no graph DB, embeddings, or chunking,
- no provider-boundary policy change,
- no `SKILL.md` change.

### PR29B: Real Specialist Extractor Probe On Four Modern Runs

Goal: only after explicit model-call approval, run the existing specialists on
the four modern baseline archives and measure whether real specialist outputs
improve semantic coverage enough to justify later integration.

Status: completed local evidence note. See
[real-specialist-extractor-probe-v0.md](real-specialist-extractor-probe-v0.md).

Outcome: Decision A plus Decision D. The existing `live_constraints`, `stance`,
and `dropped_threads` specialists improved their target semantic coverage
elements on all four modern sampled runs. The user-values/priorities gap remains
unsolved by current specialists and should stay a separate future design
question. The probe also observed provider-boundary reasoning-detail warnings
on all 12 calls; keep that separate from extractor validation quality.

Scope:

- Use the PR29A runner contract.
- Record actual model-call counts, requested/served model where available,
  estimated cost, candidate counts, validation drop rates, grounding counts,
  and coverage deltas.
- Keep outputs local-only and free of raw transcript, memo, revised-answer,
  model-message, provider-reasoning, failed-quote, and absolute-path content.
- Decide whether existing specialists materially improve live constraints,
  stance lineage, or dropped-thread coverage.

Non-goals:

- no runtime integration,
- no prompt changes,
- no new user-values extractor,
- no graph DB, embeddings, or chunking,
- no `conversation_understanding_ir.v0`,
- no LLM judge,
- no answer-quality scoring,
- no provider-boundary policy change.

### PR29C: Specialist Runtime Design Without Integration

Goal: design whether and how specialist extraction should ever move from an
offline probe into a product path, without changing runtime behavior yet.

Design note:
[specialist-runtime-design-without-integration-v0.md](specialist-runtime-design-without-integration-v0.md).

Outcome: specialist extraction should not run during normal `$lolla` by default.
The safe product path is explicit, operator-approved offline or deeper review
first. Specialist success should make runs more inspectable, not automatically
more usable, and should not override provider-boundary degradation. The
user-values/priorities gap remains out of scope for the current specialist set.
Any runtime integration proposal remains blocked until a broader approved
modern sample, at least 15-20 varied archives, repeats the PR29B coverage
improvement with bounded cost, validation failures, provider-boundary warnings,
and custody-safe outputs.

Scope:

- Use the PR29B measurement result as input.
- Specify candidate execution points, cost gates, output custody, failure
  modes, provider-boundary handling, and whether outputs remain offline or
  become archived artifacts.
- Preserve semantic coverage delta measurement as the acceptance surface.
- Keep user-values/priorities extraction out of scope unless separately
  designed.
- Keep normal `$lolla` unchanged unless a later PR explicitly approves runtime
  integration.

Non-goals:

- no `$lolla` runtime integration,
- no prompt changes,
- no archive integration,
- no semantic coverage archive integration,
- no new user-values extractor,
- no graph DB, embeddings, or chunking,
- no `conversation_understanding_ir.v0`,
- no LLM judge,
- no answer-quality scoring,
- no provider-boundary policy change.

### PR29D: Broader Specialist Evidence Gate v0

Goal: run a broader offline specialist probe before any runtime or archive
integration work is allowed to proceed.

Evidence note:
[broader-specialist-evidence-gate-v0.md](broader-specialist-evidence-gate-v0.md).

Outcome: Decision B plus Decision D, with an E caution. The existing
specialists improved 56 of 57 target semantic elements across a 19-run
reasoning-trace sample, but the sample was mixed-custody rather than 19
full-modern archives. Stance validation failed to improve one run, and all 57
model calls repeated the provider-boundary reasoning-detail warning. Runtime
integration remains blocked.

Scope:

- Use the existing real specialist probe runner.
- Probe the same three specialists: `live_constraints`, `stance`, and
  `dropped_threads`.
- Write generated outputs outside archive folders.
- Report model calls, cost, provider-boundary warnings, validation failures,
  grounding counts, semantic coverage deltas, privacy scan, and archive
  mutation check.
- Label sample-custody limits explicitly.

Non-goals:

- no `$lolla` runtime integration,
- no prompt changes,
- no archive integration,
- no semantic coverage archive integration,
- no new user-values extractor,
- no graph DB, embeddings, or chunking,
- no `conversation_understanding_ir.v0`,
- no LLM judge,
- no answer-quality scoring,
- no provider-boundary policy change.

### Evidence Gate: Six Complex Conversation Baseline v0

Goal: test whether normal `$lolla` handles longer, messier, manually pasted
conversations before adding new runtime machinery.

Evidence note:
[complex-conversation-baseline-v0.md](complex-conversation-baseline-v0.md).

Outcome: six clean complex runs now exist. Each run used a 12-user / 12-assistant
turn scenario from `plans/lolla-complex-test-conversations-2026-06-27/`. All six
captured full transcripts, produced the full modern artifact chain, had healthy
run health, clean provider-boundary status, clean product output, zero quote
fabrication, and `caller_action: use_revised_answer`.

The product result is encouraging but bounded:

- Lolla repeatedly changed the operating shape of the advice rather than merely
  adding generic caution.
- The deterministic artifacts can show capture, quote, custody, and run-health
  integrity.
- The semantic coverage reports still show repeated gaps: user
  values/priorities are not measured, stance lineage is artifact-level, and live
  constraints / dropped threads are mostly turn-reference grounded rather than
  span-grounded.

This evidence does not unlock runtime specialist integration, archive
integration, a new IR, graph memory, embeddings, or judges. It unlocked PR30:
the human/product review seed over real complex traces. With PR30 complete, the
next slice is PR31 Actionable Delta Rubric v0.

### PR30: Complex Baseline Human Review v0

Status: completed as
[complex-baseline-human-review-v0.md](../evals/complex-baseline-human-review-v0.md).

Goal: turn the six complex runs into the first explicit Lolla-specific
evaluation seed set.

Recommended scope:

- Review the six clean complex runs with the existing
  `lolla.human_review.v0` contract.
- For each run, label whether the revised answer passed answer-level review.
- Identify useful, noisy, and missing friction.
- Record the first upstream failure if the run fails.
- Name the action-changing delta: action, threshold, sequence, evidence gate,
  stop rule, or user question.
- Record whether the current artifacts are enough to justify the label.
- Extract candidate adversarial pairs where the smoother original answer may be
  worse than the rougher revised answer.

Non-goals:

- no LLM judge,
- no automatic human labels,
- no answer-quality score,
- no prompt rewrite,
- no runtime behavior change,
- no specialist integration,
- no new user-values extractor,
- no `conversation_understanding_ir.v0`,
- no graph DB, embeddings, or chunking.

Acceptance:

- The six-run review produces a short findings note and optional local review
  sheet.
- The review says what Lolla did well, what it missed, and which failure modes
  or judge traps appear.
- Any future judge proposal cites these human labels instead of generic
  helpfulness/coherence scoring.

Outcome:

- all six answer-level reviews passed;
- all six revised answers were labeled improved;
- all six remain `safe_for_agent_use: with_human_review` because saved
  artifacts are reviewable but live output is not independently checked;
- the next slice is an actionable-delta rubric, not a judge or runtime change.

### PR31: Actionable Delta Rubric v0

Goal: define what counts as a real Lolla improvement before creating
adversarial pairs or any calibrated judge prototype.

The rubric should use PR30's recurring unit of improvement:

- action changed,
- threshold changed,
- sequence changed,
- evidence gate added,
- stop rule added,
- written term added,
- user question added,
- no-op prose change rejected.

It should reject these as improvement by themselves:

- smoother prose,
- more warmth,
- longer answer,
- generic comprehensiveness,
- more caveats without action change,
- judge-palatable blandness.

Non-goals:

- no generic helpfulness/coherence scoring,
- no LLM judge,
- no automatic labels,
- no prompt rewrite,
- no runtime behavior change.

### PR32+ Or Later: Decision-Aware Capture And Runtime Integration

Goal: only after offline evidence, use the IR to improve capture or audit input.

Possible later work:

- long-conversation candidate-window selection,
- middle-turn hinge preservation fixtures,
- high-stakes capture strictness,
- rerun/deeper-mode triggers,
- Observatory inspection for conversation-understanding IR.

Do not do this until semantic coverage reporting shows repeated missing fields
that justify capture or runtime integration.

## Do Not Build Yet

- graph database integration,
- embeddings-first memory,
- production extraction rewrite,
- live prompt changes,
- live runtime cost increase,
- duplicate durable ontology before measuring existing `ConversationIR`,
- hard ontology gate,
- answer-quality judge,
- automatic human-review labels,
- human-exception or omitted-hinge annotation workflow,
- Observatory redesign,
- SKILL.md expansion.

## Expected Conclusion

Lolla should not become a generic memory layer.

It should build a reasoning-specific conversation record: enough structure to
preserve constraints, commitments, options, reversals, claims, dropped threads,
and audit-relevant hinges, while the raw transcript remains source of truth and
deterministic custody keeps the LLM honest.

The current evidence says the next move should still be boring, but the boring
thing has changed. Extraction adequacy, semantic coverage, and PR30's six-run
human review seed now exist. The next step is PR31 Actionable Delta Rubric v0:
define what useful friction changed in real traces before adding judges,
runtime specialist calls, a new IR, graph memory, embeddings, or prompt changes.

## Sources

- [Graphiti GitHub README](https://github.com/getzep/graphiti)
- [Graphiti/Zep overview](https://help.getzep.com/graphiti/getting-started/overview)
- [Zep temporal knowledge graph paper](https://arxiv.org/html/2501.13956v1)
- [Mem0 GitHub README](https://github.com/mem0ai/mem0)
- [Mem0 OSS migration/new algorithm docs](https://docs.mem0.ai/migration/oss-v2-to-v3)
- [Mem0 graph memory docs](https://docs.mem0.ai/platform/features/graph-memory)
- [Supermemory GitHub README](https://github.com/supermemoryai/supermemory)
- [LangMem conceptual guide](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)
- [LlamaIndex agent memory docs](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/)
- [Letta agent memory overview](https://www.letta.com/blog/agent-memory/)
- [Cognee GitHub README](https://github.com/topoteretes/cognee)
- [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [GBrain GitHub README](https://github.com/garrytan/gbrain)
- [GraphWOZ conversational knowledge graph paper](https://arxiv.org/abs/2211.12852)
- [Integrating Conversational Entities and Dialogue Histories with Knowledge Graphs](https://aclanthology.org/2025.iwsds-1.31.pdf)

## Local Code And Docs Inspected

- [ir.py](../../engine/system_b/ir.py)
- [ir_constructor.py](../../engine/system_b/ir_constructor.py)
- [conversation_context.py](../../engine/system_b/conversation_context.py)
- [conversation_loader.py](../../engine/system_b/conversation_loader.py)
- [live_constraints_extraction.py](../../engine/system_b/live_constraints_extraction.py)
- [dropped_threads_extraction.py](../../engine/system_b/dropped_threads_extraction.py)
- [stance_extraction.py](../../engine/system_b/stance_extraction.py)
- [capture_adequacy.py](../../engine/system_b/capture_adequacy.py)
- [agent_result.py](../../engine/system_b/agent_result.py)
- [reasoning_trace.py](../../engine/system_b/reasoning_trace.py)
- [evaluation.py](../../engine/system_b/evaluation.py)
- [review_corpus.py](../../engine/system_b/review_corpus.py)
- [run_extract.py](../../scripts/run_extract.py)
- [Lolla PRD](../lolla-reasoning-audit-harness-prd.md)
- [Evaluation methodology](../lolla-evaluation-methodology.md)
- [Public pitch](../lolla-pitch-and-invitation.md)
- [Skill steps](../skill/STEPS.md)
