# Structural Navigation Guide: `engine/system_b/pipeline.py`

**File size:** 2200 lines | **Main entry point:** `SystemBPipeline.run()` (lines 375–601, 228 lines)

## 1. Line-Range Map of Major Sections

### Orchestration & Initialization (Core Pipeline)
- **Lines 111–121:** `BoundaryClient` (Protocol) — LLM call interface with metadata capture
- **Lines 122–127:** `CritiqueRequest` — input request schema (query, vanilla_answer, etc.)
- **Lines 128–147:** `PipelineConfig` — 20+ feature flags (enable_deep_checks, triage_threshold, bridges, etc.)
- **Lines 293–330:** `SystemBPipeline.__init__()` — initialize catalog, bridges, embedding retriever, telemetry store
- **Lines 333–359:** `SystemBPipeline.load()` — load from disk: catalog, relation_graph, bridges, companions
- **Lines 362–373:** `SystemBPipeline.load_live()` — convenience: load with boundary client from env
- **Lines 375–601:** `SystemBPipeline.run()` — **MAIN ORCHESTRATOR** (see section 2 for detailed walkthrough)

### Pass 1: Triage (Clustering + Scoring)
- **Lines 943–998:** `_run_pass1_clusters_parallel()` — spawn thread pool for ~10 cluster prompts, merge scores
- **Lines 923–940:** `_run_pass1_cluster_single()` — run one cluster triage call, parse TriageScore list
- **Lines 1212–1250:** `_select_triggered_tendencies()` — filter triage_scores >= threshold + always_include + embedding hits

### Pass 2: Deep Check (if enabled_deep_checks=True)
- **Lines 1024–1070:** `_run_pass2_parallel()` — spawn threads for each triggered_tendency, call boundary
- **Lines 1001–1021:** `_run_pass2_single()` — run one deep check, parse DeepCheckResult

### Routing & Relevance
- **Lines 603–648:** `SystemBPipeline._route_deep_check_results_with_optional_tiebreaker()` — route detected tendencies; with/without embedding tiebreaker
- **Lines 650–666:** `SystemBPipeline._build_lane1_relevance_scores()` — embedding-based model ranking for Lane 1

### Lane Execution (Auxiliary Processors)
- **Lines 668–716:** `SystemBPipeline._run_companion()` — fingerprint recall + model verification
- **Lines 718–769:** `SystemBPipeline._run_frame_pressure()` — extract frame elements, reframe, assemble card
- **Lines 771–803:** `SystemBPipeline._run_structural_coverage()` — classify & detect structural gaps

### Delta Card Assembly (Finding Aggregation)
- **Lines 1253–1388:** `_assemble_delta_card()` — **COMPLEX**: routes → DeltaFinding list, apply promotions, tier findings, build compound groups
  - **Lines 1391–1401:** `_order_findings_for_tiering()` — sort by specificity + severity
  - **Lines 1405–1415:** `_split_tiered_findings()` — top tier (first 3) vs secondary
  - **Lines 1417–1454:** `_build_compound_groups()` — group findings by compound_group_id
  - **Lines 1456–1501:** `_build_presented_secondary_layer()` — filter secondary, apply summarization flag

### Promotion (Pilot bridges for overoptimism, authority, stress)
- **Lines 1528–1545:** `_build_promoted_overoptimism_results()` — call PilotDeepCheckBridge, check flags
- **Lines 1556–1574:** `_build_promoted_authority_results()` — call AuthorityPilotBridge, filter subpatterns
- **Lines 1618–1637:** `_build_promoted_stress_results()` — call StressPilotBridge, observation-only vs active
- **Lines 1580–1615:** `_build_promoted_results_for_tendency()` — **GENERIC BRIDGE WRAPPER** for all three
- **Lines 1640–1650:** `_active_promoted_result_for_tendency()` — select first active promoted result
- **Lines 1653–1701:** `_build_promoted_bundle_traces()` — extract metadata for audit trail
- **Lines 1703–1740:** `_build_promoted_pilot_finding()` — convert bridge result → DeltaFinding
- **Lines 1742–1791:** `_build_trusted_bundle_finding()` — apply bundle_selector, construct finding

### Telemetry
- **Lines 805–828:** `SystemBPipeline._record_telemetry()` — delegate to telemetry module, swallow errors

### Serialization & Boundary Tracing
- **Lines 876–899:** `_capture_boundary_call()` — extract metadata from last call
- **Lines 900–921:** `_metadata_to_boundary_call_trace()` — convert BoundaryCallMetadata → BoundaryCallTrace
- **Lines 1143–1171:** `_serialize_fingerprint_move()`, `_serialize_fingerprint_moves()`, `_serialize_dropped_fingerprint_moves()`
- **Lines 1172–1184:** `_serialize_detected_models()`

### Audit Field Extraction
- **Lines 831–842:** `_frame_audit_fields()` — extract frame_extraction_element_count, fired flag
- **Lines 844–853:** `_extract_companion_model_ids()`, `_extract_frame_model_ids()` — model set aggregation
- **Lines 862–874:** `_structural_coverage_audit_fields()` — extract card firing flags

### Embedding-Based Signals
- **Lines 1186–1209:** `_embedding_tendency_signal()` — semantic matching against vanilla_answer, threshold=0.30

### Finding Helpers
- **Lines 2039–2056:** `_build_challenge_statement()` — format route metadata + deep_result evidence into string
- **Lines 2058–2073:** `_to_sentence_fragment()`, `_ensure_sentence()` — text normalization
- **Lines 2075–2084:** `_dedupe_model_ids()` — remove duplicates, preserve order

### Loading Helpers
- **Lines 1071–1083:** `_load_companion_knowledge_graph()` — load JSON from disk
- **Lines 1085–1097:** `_load_companion_relation_graph()` — load JSON or list
- **Lines 1099–1110:** `_load_companion_reasoning_signals()` — load JSON
- **Lines 1112–1128:** `_load_embedding_retriever()` — instantiate embedding client if config.enable_embeddings
- **Lines 1130–1141:** `_load_telemetry_store()` — instantiate telemetry backend if enabled
- **Lines 2086–2105:** `_load_overoptimism_bridge()`, **Lines 2107–2121:** `_load_authority_bridge()`, **Lines 2123–2137:** `_load_stress_bridge()` — load + warn
- **Lines 2139–2151:** `_load_bundle_selector()` — instantiate bundle selector

### Utilities
- **Lines 1503–1508:** `_display_tendency_label()` — format tendency name for UI
- **Lines 1510–1515:** `_finding_specificity_rank()` — rank by sub_pattern presence
- **Lines 1517–1525:** `_severity_rank()` — map "critical" > "high" > "medium" > "low"
- **Lines 2153–2158:** `_env_truthy()` — parse env var as boolean
- **Lines 2160–2172:** `_provenance_gaps()` — detect missing source quotes
- **Lines 2174–2183:** `_collect_guardrail_tags()` — aggregate across chunks
- **Lines 2186–2199:** `_collect_quality_flags()` — aggregate with lane prefixing

### Data Classes (schema)
- **Lines 165–183:** `PromotedBundleTrace` — audit record for promoted result
- **Lines 185–191:** `TriggeredTendency` — tendency_id + source + score
- **Lines 192–216:** `AuditTrace` — comprehensive run metadata
- **Lines 218–234:** `DeltaFinding` — one finding (tendency + models + evidence)
- **Lines 236–244:** `CompoundGroup` — grouped findings by compound_group_id
- **Lines 246–268:** `DeltaCard` — full set of findings + metadata
- **Lines 270–281:** `PipelineResult` — return type: detected_tendencies + routes + delta_card + audit + cards

---

## 2. The `SystemBPipeline.run()` Method in Detail

### Overall Flow (lines 375–601)

```
run(request: CritiqueRequest) → PipelineResult:
  1. Initialize timing + boundary_calls list
  2. PASS 1: _run_pass1_clusters_parallel() → triage_scores, pass1_calls
  3. EMBEDDING: _embedding_tendency_signal() → embedding hits
  4. TRIAGE: _select_triggered_tendencies() → triggered_tendencies
  5. LANE 1 SETUP: _build_lane1_relevance_scores() → relevance dict
  
  IF triggered_tendencies EMPTY:
    └─ FAST PATH (no Pass 2): companion + frame + structural + return
  ELSE:
    IF NOT enable_deep_checks:
      └─ TRIAGE-ONLY PATH: synthesize DeltaCard from triage scores
    ELSE:
      └─ FULL PATH: PASS 2 + routing + promotions + delta assembly
    
    COMMON: companion + frame + structural + record_telemetry + return
```

### Branch 1: No Triggered Tendencies (lines 403–465)

When all triage scores < threshold AND no always_include:
- **Companion run:** empty lane1_tendency_ids, empty lane1_model_ids
- **Frame pressure run:** anti-echo with empty set
- **Structural coverage run:** anti-echo with empty companion + frame models
- **Result:** empty detected_tendencies tuple, empty routes, empty DeltaCard
- **Telemetry:** pass2_seconds=0.0, companion_candidates recorded
- **Return:** PipelineResult with empty audit trail

### Branch 2: Triage-Only (enable_deep_checks=False, lines 467–495)

When triggered but deep_checks disabled:
1. **Synthetic Pass 2:** map each triggered_tendency → synthetic DeepCheckResult
   - confidence = triage_score / 10.0
   - severity = "medium" if score >= 7 else "low"
   - sub_pattern = "" (no deep check)
2. **Routing:** `_route_deep_check_results_with_optional_tiebreaker()` with synthetic results
3. **Delta assembly:** `_assemble_delta_card()` WITHOUT promotions (promoted dicts = {})
4. **No bridge calls:** promotion_warnings = []
5. **Telemetry:** pass2_seconds=0.0

### Branch 3: Full Pipeline (enable_deep_checks=True, lines 498–551)

When triggered AND deep_checks enabled:
1. **PASS 2:** `_run_pass2_parallel()` → deep_check_results (one per triggered_tendency)
   - Threads: each tendency gets own boundary call
   - Results in triggered_tendencies order
2. **Routing:** `_route_deep_check_results_with_optional_tiebreaker()` 
   - Uses lane1_relevance to rerank neighbors
   - Optional tiebreaker if activation_tiebreaker_enabled
3. **Promotions (if active):**
   - `_build_promoted_overoptimism_results()` — if config.overoptimism_phase1_active
   - `_build_promoted_authority_results()` — if config.authority_phase1_active
   - `_build_promoted_stress_results()` — if config.stress_phase1_active
   - Collect warnings from each bridge
4. **Delta assembly:** `_assemble_delta_card()` WITH promoted dicts passed
   - For each route: check if promoted_result exists; if yes, build promoted finding else build standard finding
5. **Lane 1 model IDs:** extract from delta_card.selected_model_ids
6. **Lane 2 & 3 anti-echo:** companion + frame models

### Common Exit (both branches, lines 536–601)

1. **Companion run:** with triggered_tendency_ids (or empty set)
2. **Frame pressure run:** with lane1_tendency_ids + anti-echo
3. **Structural coverage run:** with triple anti-echo (lane 1, 2, 3)
4. **Build audit:**
   - triage_scores, triggered_tendencies, deep_check_results, routes
   - boundary_calls, promoted_bundle_traces (if full path)
   - Companion fingerprint (raw/validated/dropped), detected/rejected models
   - Frame audit fields, structural audit fields
5. **Build cheat sheet:** `select_companion_cheat_sheet()` with delta_card (or empty)
6. **Record telemetry:** timings + companion_candidates
7. **Return:** PipelineResult with all cards

### Key Branches & Conditions

| Condition | Lines | Action |
|-----------|-------|--------|
| `!triggered_tendencies` | 403–465 | Skip Pass 2, empty routes, empty delta |
| `!config.enable_deep_checks` | 467–495 | Synthetic Pass 2 results from triage scores |
| `config.enable_deep_checks` | 498–551 | Real Pass 2, promotions, full delta |
| `config.activation_tiebreaker_enabled` | 613–648 | Per-tendency neighbor re-ranking |
| `config.enable_embeddings` | 386–397 | Add embedding hits to triggered_tendencies |
| `config.enable_companion` | 673–674 | Return empty CompanionRunResult |
| `config.enable_frame_pressure` | 725–769 | Frame extraction + routing + reframing |
| `config.enable_structural_coverage` | 779–803 | Structural coverage detection |

---

## 3. Data Flow

### Input: `CritiqueRequest`
- **Fields:** query, vanilla_answer, any optional context
- **Consumed by:**
  - **Pass 1:** format_pass1_cluster_prompts(query, vanilla_answer, catalog)
  - **Embedding:** _embedding_tendency_signal(vanilla_answer, ...)
  - **Pass 2:** format_pass2_prompt(query, vanilla_answer, tendency_key, catalog)
  - **Companion:** run_fingerprint_call(query, vanilla_answer, client)
  - **Frame:** run_frame_extraction(boundary, query, vanilla_answer)
  - **Structural:** run_structural_coverage(..., query, vanilla_answer, ...)

### Output: `PipelineResult`
- **detected_tendencies:** tuple of tendency_ids from routes
- **routes:** TendencyRoute list (primary model, supporting, risk)
- **delta_card:** DeltaCard with findings, compound groups, tiering
- **audit:** AuditTrace with all intermediate results
- **companion_card, companion_cheat_sheet:** from companion lane
- **frame_pressure_card, structural_coverage_card:** from lanes 3–4

### Per-Lane Data Flow

| Lane | Input | Boundary Calls | Output | Anti-Echo |
|------|-------|-----------------|--------|-----------|
| **Pass 1** | query + vanilla_answer | ~10 clusters in parallel | triage_scores | N/A |
| **Triage Selection** | triage_scores + always_include | 0 | triggered_tendencies | N/A |
| **Pass 2** | triggered_tendencies | 1 per tendency in parallel | deep_check_results | N/A |
| **Routing** | deep_check_results + catalog | 0 | routes | N/A |
| **Companion** | query + vanilla_answer | fingerprint + verification | companion_card, models | yes (lane1_model_ids) |
| **Frame** | query + vanilla_answer + lanes | extraction + reframing | frame_pressure_card | yes (anti_echo_model_ids) |
| **Structural** | query + vanilla_answer | classification + detection | structural_coverage_card | yes (all 3 lanes) |

### Field Flow Through Delta Assembly

```
routes + deep_check_results
├─ For each route:
│  ├─ Check promoted_result (overoptimism/authority/stress)
│  │  ├─ If yes: _build_promoted_pilot_finding() → DeltaFinding
│  │  └─ If no: check bundle_selector → _build_trusted_bundle_finding()
│  │     └─ If no bundle: standard finding (primary + supporting + risk models)
│  └─ Collect: selected_model_ids, challenge_statements, next_moves, major_tensions
├─ Order findings by specificity + severity
├─ Split: top tier (3) vs secondary
├─ Build compound groups (group by compound_group_id)
└─ Assemble DeltaCard with all metadata
```

---

## 4. Dependencies Between Helpers (Call Graph)

### Orchestration Level (main control flow)
```
run()
├─ _run_pass1_clusters_parallel()
│  └─ _run_pass1_cluster_single() [threaded]
│     └─ parse_pass1_scores()
├─ _embedding_tendency_signal()
│  └─ retriever.rank_tendencies()
├─ _select_triggered_tendencies()
├─ _build_lane1_relevance_scores()
│  └─ retriever.rank_models_expanded()
├─ _run_companion()
│  ├─ run_fingerprint_call()
│  ├─ recall_candidates()
│  ├─ run_verification_call()
│  └─ build_companion_card()
├─ _run_frame_pressure()
│  ├─ run_frame_extraction()
│  ├─ route_frame_elements()
│  ├─ compute_pressure_concept_overlap()
│  ├─ generate_reframings()
│  └─ assemble_frame_card()
├─ _run_structural_coverage()
│  └─ run_structural_coverage()
├─ _route_deep_check_results_with_optional_tiebreaker()
│  ├─ route_deep_check_results() [batch]
│  └─ route_tendency() [per-tendency, with tiebreaker]
├─ _run_pass2_parallel()
│  └─ _run_pass2_single() [threaded]
│     └─ parse_pass2_result()
├─ _assemble_delta_card()
│  ├─ _active_promoted_result_for_tendency()
│  ├─ _build_promoted_pilot_finding()
│  │  └─ _build_challenge_statement()
│  ├─ _build_trusted_bundle_finding()
│  │  ├─ bundle_selector.select()
│  │  ├─ _normalize_trusted_bundle_subpattern_id()
│  │  └─ _build_challenge_statement()
│  ├─ _order_findings_for_tiering()
│  │  ├─ _finding_specificity_rank()
│  │  └─ _severity_rank()
│  ├─ _split_tiered_findings()
│  ├─ _build_compound_groups()
│  └─ _build_presented_secondary_layer()
├─ _build_promoted_overoptimism_results() / authority / stress
│  └─ _build_promoted_results_for_tendency()
│     └─ bridge.run()
├─ _build_promoted_bundle_traces()
│  ├─ _provenance_gaps()
│  ├─ _collect_guardrail_tags()
│  └─ _collect_quality_flags()
├─ _record_telemetry()
│  └─ record_pipeline_run()
└─ select_companion_cheat_sheet()
```

### Top-Level Dependency Chain (Load Time)
```
SystemBPipeline.load()
├─ TendencyCatalog.load()
├─ RelationGraph.load()
├─ _load_bundle_selector()
├─ _load_companion_knowledge_graph()
├─ _load_companion_relation_graph()
├─ _load_companion_reasoning_signals()
├─ _load_overoptimism_bridge()
├─ _load_authority_bridge()
├─ _load_stress_bridge()
├─ _load_embedding_retriever()
└─ _load_telemetry_store()
```

---

## 5. Load-Bearing vs. Auxiliary Code

### CORE ORCHESTRATION (~200–250 lines, DO NOT TOUCH)
- **Lines 375–601:** `run()` — state machine, branch logic, lane sequencing
- **Lines 603–648:** `_route_deep_check_results_with_optional_tiebreaker()` — routing decision logic
- **Lines 650–666:** `_build_lane1_relevance_scores()` — embedding integration
- **Lines 1253–1388:** `_assemble_delta_card()` — finding aggregation & tiering (complex)

### LANE WRAPPERS (~150 lines, STABLE but can be refactored)
- **Lines 668–716:** `_run_companion()` — companion orchestration
- **Lines 718–769:** `_run_frame_pressure()` — frame lane orchestration
- **Lines 771–803:** `_run_structural_coverage()` — structural lane orchestration
- Can be moved to separate modules (companion_orchestration.py, etc.) if needed

### PASS 1 & PASS 2 (~120 lines, STABLE, good for extraction)
- **Lines 943–998:** `_run_pass1_clusters_parallel()` — thread pool + merge
- **Lines 1024–1070:** `_run_pass2_parallel()` — thread pool + merge
- **Lines 923–940, 1001–1021:** Single-run helpers
- These could move to pass1.py, pass2.py without breaking run()

### PROMOTION LOGIC (~200 lines, COMPLEX, test-heavy)
- **Lines 1528–1637:** `_build_promoted_*_results()` functions
- **Lines 1580–1615:** `_build_promoted_results_for_tendency()` — generic wrapper
- **Lines 1640–1701:** `_active_promoted_result_for_tendency()`, `_build_promoted_bundle_traces()`
- **Lines 1703–1791:** `_build_promoted_pilot_finding()`, `_build_trusted_bundle_finding()`
- Candidate for extraction to promotions.py, but tightly coupled with delta assembly

### FINDING & TIERING LOGIC (~150 lines, STRAIGHTFORWARD)
- **Lines 1391–1501:** Ordering, splitting, compound groups, secondary layer
- Clear purpose, low coupling, good extraction target
- Candidate for findings_assembly.py

### UTILITY HELPERS (~200 lines, NO DEPENDENCIES)
- **Lines 2039–2199:** Challenge statement, text normalization, deduplication, loading, env parsing
- Pure functions, zero coupling to orchestration
- Can be moved to helpers.py without any impact

### AUDIT & SERIALIZATION (~70 lines, STRAIGHTFORWARD)
- **Lines 831–921:** Frame/companion/structural audit extraction, boundary tracing
- Pure data mapping, no side effects
- Can move to audit.py

### TOTAL EXTRACTABLE: ~500 lines (utilities + audit + some helpers + some lanes)
### MUST-STAY CORE: ~250 lines (run + routing + delta assembly core)

---

## 6. Tech Debt Observations

### High Priority

1. **Missing type hints on retriever & embedding_api_key (lines 306, 324)**
   - `embedding_retriever=None` should be `EmbeddingRetriever | None`
   - `_embedding_api_key` should have type annotation

2. **Inconsistent error handling in loaders (lines 1071–1151)**
   - No fallback for missing JSON files; relies on exceptions
   - _load_overoptimism_bridge, etc. silently catch exceptions but don't log which file failed

3. **Magic numbers in thresholds (lines 1190, 2085)**
   - `threshold: float = 0.30` hardcoded in _embedding_tendency_signal
   - `max_workers = min(len(cluster_prompts), 8)` hardcoded in _run_pass1_clusters_parallel
   - Should be config fields

4. **Duplicated promotion builder pattern (lines 1528–1637)**
   - Three nearly identical functions (_build_promoted_overoptimism, authority, stress) all call _build_promoted_results_for_tendency
   - Could consolidate to enum-driven dispatch

5. **Complex DeltaCard assembly logic (lines 1253–1388)**
   - 135 lines, deeply nested conditional (promoted vs bundle vs standard finding)
   - No clear separation between promotion, tiering, and compound grouping
   - Candidate for breaking into smaller functions

### Medium Priority

6. **Implicit Lane Ordering (lines 404–551)**
   - Lane execution order is implicit in run() logic
   - If lanes need reordering, must hunt through run() for each conditional
   - Consider explicit lane registry / execution list

7. **Telemetry Swallows Errors (line 827)**
   - `except Exception: _LOGGER.warning(...)` silently drops failures
   - Could mask data quality issues if telemetry breaks

8. **String formatting in audit fields (lines 836–843)**
   - _frame_audit_fields(), _structural_coverage_audit_fields() map card → dict
   - Inconsistent naming (frame_extraction_fired vs enable_frame_pressure)
   - Could use @dataclass or named tuple for audit schema

9. **Companion fingerprint serialization (lines 427–430, 564–568)**
   - Code duplicated in both branches (early return vs. full path)
   - Could extract to helper if needed

10. **No exhaustiveness check for promoted results (lines 1640–1650)**
    - _active_promoted_result_for_tendency() silently returns None if no active result
    - Easy to miss a bridge if adding new promotion type

### Low Priority

11. **Sentence normalization functions (lines 2058–2073)**
    - _to_sentence_fragment() and _ensure_sentence() are underutilized
    - Only called in _build_challenge_statement
    - Could inline if not shared elsewhere

12. **Unused import: CompoundGroup (line 29)**
    - Imported from compound_catalog but only used in delta assembly
    - Not a blocker, just unused at module level

13. **No test coverage markers**
    - No indication which functions are well-tested vs. brittle
    - Would benefit from test fixture comments

---

## 7. How to Modify This File Safely

### Before You Start

1. **Run the existing test suite** to establish baseline
   - Check if pipeline_test.py or system_b_test.py exists
   - Ensure all tests pass before changes

2. **Understand the request schema**
   - Look at CritiqueRequest fields (lines 122–127)
   - Your shim must accept/provide these fields

### Where to Add a ConversationContext Shim

**Option A: Inject as request parameter (safest)**
```python
# Modify CritiqueRequest dataclass (lines 122–127)
@dataclass
class CritiqueRequest:
    query: str
    vanilla_answer: str
    conversation_context: ConversationContext | None = None  # NEW
    ...
```
- **Impact:** Lines 379, 963, 1008 (format prompts) need to accept context
- **Tests:** Pass context through all three format functions
- **Risk:** LOW if format functions already have **kwargs escape hatch

**Option B: Thread through pipeline methods (more invasive)**
```python
def run(self, request: CritiqueRequest, conversation_context: ConversationContext | None = None) -> PipelineResult:
    # Inject into lane methods
    self._run_companion(request, boundary_calls, conversation_context=conversation_context)
```
- **Impact:** Touches all lane methods + format functions
- **Tests:** More integration points to verify
- **Risk:** MEDIUM — every lane must handle new parameter

### Which Parts Are Brittle

**BRITTLE (do NOT touch without deep understanding):**
- **Lines 375–601 (run() state machine)** — any branch change breaks conditions
- **Lines 1253–1388 (_assemble_delta_card)** — promoted/bundle/standard finding logic is tightly coupled
- **Lines 1024–1070 (_run_pass2_parallel)** — thread pool error handling
- **Lines 1580–1615 (_build_promoted_results_for_tendency)** — generic bridge wrapper, easy to break subpattern filtering

**SAFER (ok to modify if careful):**
- **Lines 668–769 (lane wrappers)** — each lane is mostly self-contained
- **Lines 923–998 (pass 1 & 2)** — straightforward thread pool, fallback exists for test mocks
- **Lines 1391–1501 (tiering logic)** — pure functions, no side effects
- **Lines 2039–2199 (helpers)** — zero dependencies, easy to test in isolation

### Testing Strategy After Modification

1. **Unit test your shim**
   - Mock BoundaryClient, test format functions with conversation_context
   - Verify no regression in triage scores

2. **Integration test**
   - Full run() with ConversationContext populated
   - Verify audit trace captures context usage
   - Check that boundary calls still match expected format

3. **Regression test existing paths**
   - Run with conversation_context=None → should behave identically to before
   - Check all branches still execute (empty triggered, triage-only, full path)

4. **Performance check**
   - Measure pass1_seconds, pass2_seconds, companion_seconds
   - If threading is affected, ThreadPoolExecutor.submit() might timeout

### Key Invariants to Preserve

1. **Triggered tendencies list must be ordered consistently** (line 397)
   - Downstream code assumes order matches triage cluster order
   - If you change _select_triggered_tendencies(), verify order preservation

2. **DeltaCard.findings order must match tiering** (line 1341)
   - _order_findings_for_tiering() is deterministic
   - Any change to sorting key breaks reproducibility

3. **Anti-echo must exclude all lanes** (lines 740, 787)
   - lane1_model_ids, lane2_model_ids, lane3_model_ids must not overlap
   - If context adds models, audit that exclusion still works

4. **Boundary calls list must preserve order** (line 377)
   - Audit trace depends on call sequence for debugging
   - ThreadPoolExecutor.submit() order is preserved for futures iteration (line 994)

### Files to Check Before Committing

- **engine/system_b/prompts.py** — format_pass1_cluster_prompts, format_pass2_prompt
  - Your context shim must flow through these
- **engine/system_b/deep_checks.py** — parse_pass2_result
  - If context changes prompt structure, parsing may break
- **engine/system_b/boundary_provider.py** — BoundaryCallMetadata
  - If you add logging of context, verify metadata capture works
- **engine/system_b/telemetry.py** — record_pipeline_run
  - Check if context should be recorded in telemetry

### Avoiding Common Pitfalls

- **❌ DON'T** modify run() logic without running full test suite
- **❌ DON'T** change _assemble_delta_card() signature without updating all 4 callers (lines 490, 528, 1295, 1296)
- **❌ DON'T** add new promoted result type without updating _active_promoted_result_for_tendency() exhaustiveness
- **✅ DO** add type hints for any new parameters
- **✅ DO** log when context is used (for debugging)
- **✅ DO** preserve audit trail (add context metadata to AuditTrace if relevant)

---

**Last Updated:** 2026-04-22 | **File Size:** 2200 lines | **Estimated Read Time:** 30–45 min for this guide + target sections
