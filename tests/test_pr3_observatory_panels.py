"""PR 3 — Observatory audit_summary panels.

Exercises six new server-rendered HTML panels at /audit/* plus the index
at /audit and the cross-link added to /usage. Tests run two ways:

1. **Function-level** (bulk): import the renderer functions directly and
   feed them a fixture _RESULT dict. Fast, deterministic, covers
   degrade-gracefully behaviour.
2. **End-to-end** (one smoke test): start serve_result.py on a free
   port via threading.Thread, hit the routes via urllib.request, assert
   200 + content. Proves the do_GET wiring and the do-not-need-SPA
   portability gate.
"""

from __future__ import annotations

import json
import socket
import sys
import threading
import time
import urllib.parse
import urllib.request
from contextlib import closing
from http.server import HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "observatory"))

import serve_result  # noqa: E402  (path manipulation above)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _fixture_result() -> dict:
    """Synthetic result.json that exercises every panel branch.

    Carries every audit_summary field the panels render — including PR 1
    + PR 2 fields that are absent on origin/main but populated in real
    runs after those PRs merge. Panels must render correctly with these
    present and (separately, see ``_minimal_result``) when absent.
    """
    return {
        "audit_summary": {
            "triage_scores": [
                {"tendency_id": "anchoring-tendency", "score": 6, "evidence": "evidence A"},
                {"tendency_id": "authority-misinfluence-tendency", "score": 4, "evidence": "evidence B"},
                {"tendency_id": "doubt-avoidance-tendency", "score": 2, "evidence": "weak"},
                {"tendency_id": "overoptimism-tendency", "score": 0, "evidence": ""},
            ],
            "triggered_tendencies": [
                "anchoring-tendency",
                "authority-misinfluence-tendency",
                "stress-influence-tendency",
            ],
            "triggered_tendency_sources": [
                {"tendency_id": "anchoring-tendency", "source": "triage", "score": 6},
                {"tendency_id": "authority-misinfluence-tendency", "source": "triage", "score": 4},
                {"tendency_id": "stress-influence-tendency", "source": "embedding", "score": 0.34},
            ],
            "deep_check_results": [
                {
                    "tendency_id": "anchoring-tendency",
                    "tendency_name": "Anchoring",
                    "detected": True,
                    "confidence": 0.7,
                    "evidence": "Evidence quote",
                    "sub_pattern": "general",
                    "specific_passage": "we should plan around the $50k budget",
                    "severity": "medium",
                    "reason": "The first numerical anchor dominated subsequent reasoning.",
                },
                {
                    "tendency_id": "authority-misinfluence-tendency",
                    "tendency_name": "Authority Misinfluence",
                    "detected": False,
                    "confidence": 0.1,
                    "evidence": "",
                    "sub_pattern": "",
                    "specific_passage": "",
                    "severity": "",
                    "reason": "The assistant explicitly questioned the partner claim.",
                },
            ],
            "routing_decisions": [
                {
                    "tendency_id": "anchoring-tendency",
                    "primary_model_id": "first-principles-thinking",
                    "sub_pattern": "general",
                    "antidote_model_ids": ["base-rates", "comparative-advantage"],
                    "tiebreaker_supporting": {
                        "fired": False,
                        "abort_reason": "outside_epsilon_window",
                        "top1_model_id": "first-principles-thinking",
                        "top2_model_id": "base-rates",
                        "top1_affinity": 0.91,
                        "top2_affinity": 0.62,
                        "delta": 0.29,
                    },
                    "tiebreaker_risk": None,
                },
            ],
            "companion_candidates": [
                {
                    "model_id": "checklists",
                    "model_name": "Checklists",
                    "recall_source": "keyword",
                    "keyword_rank": 1,
                    "embedding_rank": None,
                    "final_rank": 1,
                    "activation_trigger": "repeatable execution",
                    "danger_when": "novel situation",
                },
                {
                    "model_id": "second-order-thinking",
                    "model_name": "Second-Order Thinking",
                    "recall_source": "keyword",
                    "keyword_rank": 2,
                    "embedding_rank": None,
                    "final_rank": 2,
                    "activation_trigger": "downstream effects",
                    "danger_when": "speculation",
                },
                {
                    "model_id": "cognitive-dissonance",
                    "model_name": "Cognitive Dissonance",
                    "recall_source": "keyword",
                    "keyword_rank": 3,
                    "embedding_rank": None,
                    "final_rank": 3,
                    "activation_trigger": "conflicting beliefs",
                    "danger_when": "rationalisation",
                },
            ],
            "companion_verification_accepted_before_cap": [
                {
                    "model_id": "checklists",
                    "model_name": "Checklists",
                    "evidence_quote": "we ran through the checklist",
                    "presence_mode": "executed",
                    "presence_explanation": "structured execution",
                    "detection_confidence": "structural",
                },
            ],
            "companion_rejected_models": [
                {
                    "model_id": "second-order-thinking",
                    "rejection_reason": "too generic",
                    "original_evidence_quote": "downstream",
                },
            ],
            "companion_verification_capped_models": [],
            "companion_verification_duplicate_accepts": [],
            "companion_verification_quote_repairs": [],
            "companion_verification_silently_omitted": [
                {"model_id": "cognitive-dissonance", "drop_reason": "not_in_verifier_response"},
            ],
            "companion_candidate_cap": 60,
            "embedding_mode": "on",
            "embedding_tendency_ranks": [
                {"tendency_id": "anchoring-tendency", "score": 0.42, "promoted": True},
                {"tendency_id": "stress-influence-tendency", "score": 0.34, "promoted": True},
                {"tendency_id": "doubt-avoidance-tendency", "score": 0.28, "promoted": False},
                {"tendency_id": "sunk-cost-tendency", "score": 0.18, "promoted": False},
            ],
        },
        "delta_card": {
            "findings": [
                {
                    "tendency_id": "anchoring-tendency",
                    "selected_model_ids": ["first-principles-thinking", "base-rates"],
                },
            ],
        },
        "companion_cheat_sheet": {
            "anchors": [
                {"model_id": "checklists"},
            ],
        },
        "companion_card": {
            "expansions": [
                {
                    "source_model_id": "checklists",
                    "model_id": "premortem",
                    "relation_type": "ally",
                    "activation_condition": "before commitments",
                    "affinity_rationale": "structural-imagination complement",
                    "substrate_chunk": "Premortem helps imagine failure modes.",
                    "why_relevant": "Pairs with checklist execution.",
                },
                {
                    "source_model_id": "checklists",
                    "model_id": "swiss-cheese-model",
                    "relation_type": "ally",
                    "activation_condition": "layered defences",
                    "affinity_rationale": "shared-failure-mode lens",
                    "substrate_chunk": "Swiss cheese surfaces overlapping holes.",
                    "why_relevant": "Layered checks reduce single-point failure.",
                },
            ],
        },
        "frame_pressure_card": {
            "frame_elements": [
                {
                    "element_text": "Only one pilot path is being considered.",
                    "element_type": "assumption",
                    "evidence_quote": "Should we test it on one team first?",
                    "frame_pattern": "binary_collapse",
                    "fragility_signal": "A reversible multi-team probe may exist.",
                    "inquiry_stage": "what_if",
                    "likely_default": "inertia",
                },
            ],
            "routes": [
                {
                    "element_index": 0,
                    "frame_pattern": "binary_collapse",
                    "candidate_model_ids": ["premortem", "inversion"],
                    "excluded_model_ids": ["base-rates"],
                },
            ],
            "reframings": [
                {
                    "reframed_question": "Should we test it on one team first?",
                    "grounding_model": "premortem",
                    "source_element_index": 0,
                },
            ],
        },
        "structural_coverage_card": {
            "question_type": "decision-evaluation",
            "dimensions": [
                {
                    "dimension_id": "incentive-alignment",
                    "dimension_name": "Incentive alignment",
                    "covered": False,
                    "coverage_evidence": "",
                    "materiality_note": "Senior partner has revenue interest.",
                },
                {
                    "dimension_id": "stakeholder-alignment",
                    "dimension_name": "Stakeholder alignment",
                    "covered": True,
                    "coverage_evidence": "Junior staff voices considered.",
                    "materiality_note": "",
                },
            ],
            "gap_routes": [
                {
                    "dimension_id": "incentive-alignment",
                    "dimension_name": "Incentive alignment",
                    "candidate_model_ids": ["principal-agent-problem", "moral-hazard"],
                    "excluded_model_ids": ["incentives"],
                },
            ],
            "gap_questions": [
                {
                    "dimension_id": "incentive-alignment",
                    "questions": ["Whose incentive is at stake here?"],
                },
            ],
            "anti_echo_model_ids": [
                "checklists",         # from Lane 2 anchor
                "first-principles-thinking",  # from Lane 1 finding
                "base-rates",         # from Lane 1 finding
                "premortem",          # from Lane 3 grounding model
                "unknown-model",      # not attributable to any upstream lane
            ],
        },
        "stakeholder_assumption_check": {
            "status": "completed",
            "triggered": True,
            "trigger_reason": "material stakeholder dependency via stakeholder-alignment",
            "surface": True,
            "summary": "Share general evidence, not screenshots.",
            "critical_actors": [
                {
                    "display_name": "ex-husband",
                    "role": "co-parent with 50% custody",
                    "power_or_dependency": ["custody", "counter-messaging"],
                    "advice_assumption": "He can be moved by evidence without weaponizing it.",
                    "grounding": "plausible",
                    "known_to_actor": ["Mother thinks the Instagram contact is serious."],
                    "unknown_to_actor": ["Exact surveillance details unless disclosed."],
                    "bridging_facts": ["He has 50% custody."],
                    "risk_if_wrong": "He reframes evidence as overreaction.",
                    "plan_change": "Share general legal and grooming-pattern facts; do not forward screenshots.",
                    "open_question": "What evidence moves him without giving him ammunition?",
                }
            ],
        },
    }


def _minimal_result() -> dict:
    """Result with no audit_summary block — a very old artifact."""
    return {}


@pytest.fixture(autouse=True)
def _stub_result(monkeypatch):
    """Each test reloads its own fixture into the module-level _RESULT."""
    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)


# ---------------------------------------------------------------------------
# Panel 1 — /audit/lane1 (Pass 1 + Pass 2 funnel)
# ---------------------------------------------------------------------------


def test_lane1_panel_renders_24_triage_scores_with_threshold():
    html = serve_result._render_lane1_html()
    assert "anchoring-tendency" in html
    assert "authority-misinfluence-tendency" in html
    assert "doubt-avoidance-tendency" in html
    assert "overoptimism-tendency" in html
    assert "Triage threshold" in html  # threshold value rendered


def test_lane1_panel_renders_triggered_sources_with_attribution():
    html = serve_result._render_lane1_html()
    assert "triage" in html
    assert "embedding" in html  # embedding-promoted entry surfaces
    assert "stress-influence-tendency" in html


def test_lane1_panel_distinguishes_threshold_from_embedding_promotion():
    html = serve_result._render_lane1_html()
    assert "crossed the triage threshold" in html
    assert "were embedding-promoted" in html
    assert "Pass 2 checked" in html
    assert "Advanced set" in html
    assert "crossed the Pass 1 threshold" not in html


def test_lane1_panel_renders_pass2_outcomes_with_reason():
    html = serve_result._render_lane1_html()
    assert "Pass 2" in html
    assert "Anchoring" in html or "anchoring-tendency" in html
    # The Pass 2 reason field (added in PR 2) must appear when populated:
    assert "first numerical anchor" in html
    assert "explicitly questioned" in html


def test_lane1_panel_renders_embedding_close_calls_when_present():
    html = serve_result._render_lane1_html()
    # Sub-threshold rows from PR 2's embedding_tendency_ranks should be
    # visible as "close calls" — operators want to see who almost made it.
    assert "doubt-avoidance-tendency" in html
    assert "0.28" in html or "0.280" in html


def test_lane1_panel_handles_empty_audit_summary(monkeypatch):
    monkeypatch.setattr(serve_result, "_RESULT", {})
    html = serve_result._render_lane1_html()
    assert "Lane 1" in html
    assert "no audit_summary" in html.lower() or "empty" in html.lower() or "no triage" in html.lower()


# ---------------------------------------------------------------------------
# Panel 2 — /audit/lane2 (Companion selection funnel)
# ---------------------------------------------------------------------------


def test_lane2_panel_renders_candidates_with_rank():
    html = serve_result._render_lane2_html()
    assert "checklists" in html
    assert "second-order-thinking" in html
    assert "cognitive-dissonance" in html
    assert "Candidates" in html


def test_lane2_panel_renders_accepted_capped_rejected_buckets():
    html = serve_result._render_lane2_html()
    assert "accepted" in html.lower()
    assert "rejected" in html.lower()
    assert "too generic" in html


def test_lane2_panel_renders_silently_omitted_bucket():
    """PR 2 Fix #3 surface: silently_omitted candidates need their own bucket in the panel."""
    html = serve_result._render_lane2_html()
    # cognitive-dissonance was sent in but never mentioned by verifier
    assert "cognitive-dissonance" in html
    assert "not_in_verifier_response" in html


def test_lane2_panel_renders_funnel_totals():
    html = serve_result._render_lane2_html()
    # Totals: 3 candidates → 1 accepted → 1 final
    assert "3" in html  # candidate count
    assert "1" in html  # accepted/final


# ---------------------------------------------------------------------------
# Panel 4 — /audit/lane4 (Dimension coverage)
# ---------------------------------------------------------------------------


def test_lane4_panel_renders_question_type_and_detected_dimensions():
    html = serve_result._render_lane4_html()
    assert "decision-evaluation" in html
    assert "incentive-alignment" in html
    assert "stakeholder-alignment" in html


def test_lane4_panel_distinguishes_gap_from_covered():
    html = serve_result._render_lane4_html()
    # incentive-alignment is uncovered (gap); stakeholder-alignment is covered
    assert "Senior partner has revenue interest" in html
    assert "Junior staff voices" in html


def test_lane4_panel_renders_gap_route_candidates_and_exclusions():
    html = serve_result._render_lane4_html()
    assert "principal-agent-problem" in html
    assert "moral-hazard" in html
    assert "incentives" in html  # excluded


def test_lane4_panel_renders_gap_questions():
    html = serve_result._render_lane4_html()
    assert "Whose incentive is at stake" in html


# ---------------------------------------------------------------------------
# Panel — /audit/anti-echo (cascade attribution)
# ---------------------------------------------------------------------------


def test_anti_echo_panel_attributes_each_excluded_model_to_lane_of_origin():
    html = serve_result._render_anti_echo_html()
    # checklists → Lane 2 anchor
    assert "checklists" in html
    assert "Lane 2" in html
    # first-principles-thinking → Lane 1 finding
    assert "first-principles-thinking" in html
    assert "Lane 1" in html
    # premortem → Lane 3 grounding model
    assert "premortem" in html
    assert "Lane 3" in html


def test_anti_echo_panel_handles_unattributed_model():
    """If a model isn't found in any upstream lane, it still renders — tagged 'unknown'."""
    html = serve_result._render_anti_echo_html()
    assert "unknown-model" in html
    # Should show some "no source detected" / "unattributed" marker — check
    # the rendered string contains an indicator:
    assert "unattributed" in html.lower() or "unknown source" in html.lower() or "—" in html


# ---------------------------------------------------------------------------
# Panel — /audit/routing (Routing decisions + tiebreaker traces)
# ---------------------------------------------------------------------------


def test_routing_panel_renders_primary_and_antidote_models_per_tendency():
    html = serve_result._render_routing_html()
    assert "anchoring-tendency" in html
    assert "first-principles-thinking" in html  # primary
    assert "base-rates" in html  # antidote
    assert "comparative-advantage" in html  # antidote


def test_routing_panel_renders_tiebreaker_trace_with_abort_reason():
    html = serve_result._render_routing_html()
    assert "outside_epsilon_window" in html or "Outside near-tie window" in html


def test_routing_panel_renders_route_trace_sections():
    html = serve_result._render_routing_html()
    assert "Lane 1 Route" in html
    assert "Lane 2 Route" in html
    assert "Lane 3 Route" in html
    assert "Lane 4 Route" in html
    assert "Anti-Echo / Why-Not" in html
    assert "not_in_verifier_response" in html
    assert "anti_echo_lane1_overlap" in html
    assert "anti_echo_upstream_lane_overlap" in html


def test_routing_panel_falls_back_to_computed_anti_echo_rows(monkeypatch):
    r = _fixture_result()
    r["audit_summary"]["route_trace"] = {
        "schema_version": "route_trace.v1",
        "summary": {
            "lane1_route_count": 0,
            "lane3_route_count": 0,
            "lane4_route_count": 0,
            "anti_echo_exclusion_count": 0,
        },
        "lanes": {
            "lane1": {"routes": []},
            "lane2": {"candidate_count": 0, "candidates": []},
            "lane3": {"routes": []},
            "lane4": {"routes": []},
        },
        "anti_echo": {"exclusions": []},
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_routing_html()

    assert "0</strong> recorded anti-echo exclusions" in html
    assert "5</strong> computed Lane 4 exclusions" in html
    assert "computed_from_structural_coverage_card.anti_echo_model_ids" in html
    assert "checklists" in html
    assert "Lane 4 structural coverage" in html


def test_routing_panel_preserves_lane2_rejection_vs_lane4_gap_candidate_from_marcus_2d(monkeypatch):
    """Regression guard for the route trace's concrete operator-value case.

    In the Marcus phase 2d archive, Lane 2 verifier rejects opportunity-cost
    while Lane 4 still routes it as a Resource Allocation gap candidate. The
    Observatory must keep that decision separation visible.
    """
    fixture_path = (
        Path(__file__).resolve().parents[1]
        / "research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24"
        / "marcus_new_path_result.json"
    )
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    monkeypatch.setattr(serve_result, "_RESULT", payload)

    trace = serve_result._route_trace()
    lane2_rejections = trace["lanes"]["lane2"]["rejected_candidates"]
    assert any(
        item.get("model_id") == "opportunity-cost"
        and item.get("rejection_reason") == "mechanism absent"
        and item.get("stage") == "verification"
        for item in lane2_rejections
    )

    lane4_routes = trace["lanes"]["lane4"]["routes"]
    assert any(
        item.get("dimension_name") == "Resource Allocation"
        and "opportunity-cost" in (item.get("candidate_model_ids") or [])
        for item in lane4_routes
    )

    html = serve_result._render_routing_html()
    assert "opportunity-cost: mechanism absent (verification)" in html
    assert "Resource Allocation" in html
    assert "<code>opportunity-cost</code>" in html


def test_routing_panel_handles_empty_routing_decisions(monkeypatch):
    r = _fixture_result()
    r["audit_summary"]["routing_decisions"] = []
    monkeypatch.setattr(serve_result, "_RESULT", r)
    html = serve_result._render_routing_html()
    # Empty state must point operators back to Lane 1
    assert "Lane 1" in html or "/audit/lane1" in html


# ---------------------------------------------------------------------------
# Panel — /audit/expansions (Companion expansions grouped by anchor)
# ---------------------------------------------------------------------------


def test_expansions_panel_groups_by_source_anchor():
    html = serve_result._render_expansions_html()
    assert "checklists" in html
    assert "premortem" in html
    assert "swiss-cheese-model" in html


def test_expansions_panel_renders_relation_type_and_why_relevant():
    html = serve_result._render_expansions_html()
    assert "ally" in html
    assert "Pairs with checklist execution" in html


def test_expansions_panel_handles_empty_expansions(monkeypatch):
    r = _fixture_result()
    r["companion_card"]["expansions"] = []
    monkeypatch.setattr(serve_result, "_RESULT", r)
    html = serve_result._render_expansions_html()
    assert "Lane 2" in html or "/audit/lane2" in html


# ---------------------------------------------------------------------------
# Index page + /usage cross-link
# ---------------------------------------------------------------------------


def test_audit_index_links_to_all_panels():
    html = serve_result._render_audit_index_html()
    for href in ("/audit/extraction", "/audit/memo", "/audit/lane1", "/audit/lane2",
                 "/audit/lane4", "/audit/anti-echo", "/audit/routing",
                 "/audit/expansions", "/audit/stakeholders",
                 "/audit/graph-survival", "/audit/reasoning-trace",
                 "/audit/events"):
        assert href in html, f"index missing link to {href}"


def test_audit_index_renders_structured_run_health_issue_details(monkeypatch):
    r = _fixture_result()
    r["run_health"] = {
        "overall": "healthy",
        "issues": ["embeddings_off"],
        "issue_details": [
            {
                "code": "embeddings_off",
                "severity": "optional_off",
                "axis": "retrieval",
                "trust_impact": "Embedding recall was unavailable by mode; deterministic paths still ran.",
                "mode": "auto",
            }
        ],
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_audit_index_html()

    assert "Run Health" in html
    assert "embeddings_off" in html
    assert "optional_off" in html
    assert "retrieval" in html
    assert "Embedding recall was unavailable by mode" in html


def test_audit_index_renders_product_output_health(monkeypatch):
    r = _fixture_result()
    r["run_health"] = {
        "overall": "healthy",
        "product_output_health": "clean",
        "product_output_leak_count": 0,
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_audit_index_html()

    assert "product output" in html
    assert "clean" in html


def test_stakeholder_panel_renders_assumptions_and_plan_change():
    html = serve_result._render_stakeholder_html()
    assert "Stakeholder Assumption Check" in html
    assert "ex-husband" in html
    assert "plausible" in html
    assert "weaponizing" in html
    assert "do not forward screenshots" in html


def test_stakeholder_panel_absent_for_skipped_check(monkeypatch):
    r = _fixture_result()
    r["stakeholder_assumption_check"] = {"status": "skipped", "triggered": False}
    monkeypatch.setattr(serve_result, "_RESULT", r)
    html = serve_result._render_stakeholder_html()
    assert "No stakeholder assumption check" in html


def test_case_api_includes_stakeholder_assumption_check():
    response = serve_result._build_case_response()
    assert response["stakeholder_assumption_check"]["status"] == "completed"


def test_cases_api_lists_local_archived_runs(tmp_path, monkeypatch):
    current = _fixture_result()
    current["usage_summary"] = {"run_id": "current-run"}
    archive_root = tmp_path / "runs"
    run_dir = archive_root / "archive-case" / "20260624T010203Z_archive"
    run_dir.mkdir(parents=True)

    archived = json.loads(json.dumps(_fixture_result()))
    archived["usage_summary"] = {"run_id": "20260624T010203Z_archive"}
    archived["extraction"] = {
        "decision_situation": "Whether archived local history should open.",
        "turns": [
            {"speaker": "user", "text": "Archived user question"},
            {"speaker": "assistant", "text": "Archived assistant answer"},
        ],
    }
    (run_dir / "result.json").write_text(json.dumps(archived), encoding="utf-8")

    monkeypatch.setenv("LOLLA_ARCHIVE_DIR", str(archive_root))
    monkeypatch.setattr(serve_result, "_RESULT", current)
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Current active run")

    cases = serve_result._build_cases_index()

    assert cases[0]["id"] == "lolla-audit"
    archive_cases = [item for item in cases if item["source"] == "archive"]
    assert len(archive_cases) == 1
    assert archive_cases[0]["id"] == "archive:archive-case:20260624T010203Z_archive"
    assert "Whether archived local history should open." in archive_cases[0]["name"]
    assert archive_cases[0]["run_id"] == "20260624T010203Z_archive"
    assert archive_cases[0]["has_audit_trace"] is True


def test_archived_case_api_loads_selected_result_and_graph(
    tmp_path,
    monkeypatch,
    running_server,
):
    archive_root = tmp_path / "runs"
    run_dir = archive_root / "archive-case" / "20260624T010203Z_archive"
    run_dir.mkdir(parents=True)

    archived = json.loads(json.dumps(_fixture_result()))
    archived["usage_summary"] = {"run_id": "20260624T010203Z_archive"}
    archived["extraction"] = {
        "decision_situation": "Whether selected archived case renders.",
        "turns": [
            {"speaker": "user", "text": "Archived user question"},
            {"speaker": "assistant", "text": "Archived assistant answer"},
        ],
    }
    archived["companion_cheat_sheet"] = {
        "anchors": [{"model_id": "archive-only-model", "chunks": []}]
    }
    (run_dir / "result.json").write_text(json.dumps(archived), encoding="utf-8")
    monkeypatch.setenv("LOLLA_ARCHIVE_DIR", str(archive_root))

    status, body = _http_get(f"{running_server}/api/cases")
    assert status == 200
    cases = json.loads(body)
    archived_id = "archive:archive-case:20260624T010203Z_archive"
    assert any(item["id"] == archived_id for item in cases)

    encoded = urllib.parse.quote(archived_id, safe="")
    status, body = _http_get(f"{running_server}/api/case/{encoded}")
    assert status == 200
    payload = json.loads(body)
    assert payload["case"]["case_id"] == archived_id
    assert "Archived user question" in payload["case"]["query"]
    assert payload["usage_summary"]["run_id"] == "20260624T010203Z_archive"

    status, body = _http_get(f"{running_server}/api/case/{encoded}/graph")
    assert status == 200
    graph = json.loads(body)
    assert any(node["id"] == "archive-only-model" for node in graph["nodes"])


def test_v60_panel_renders_process_telemetry(monkeypatch):
    r = _fixture_result()
    r["v60_enrichment"] = {
        "status": "active",
        "artifact": {
            "artifact_id": "model_affordances_v60",
            "status": "draft_review_only",
            "model_record_count": 222,
            "affordance_count": 306,
            "absence_record_count": 697,
            "sha256": "abc123def4567890",
        },
        "candidate_pool": {
            "lane_candidate_count": 2,
            "raw_lane_signal_count": 3,
            "embedding_mode": "on",
            "lane_source_counts": {"lane1_selected": 1, "lane2_companion_anchor": 1},
            "lane_candidates": [
                {
                    "model_id": "opportunity-cost",
                    "source": "lane1_selected",
                    "lane_order": 1,
                    "reason": "The choice displaces alternatives.",
                    "evidence": "accept the offer",
                }
            ],
            "embedding_model_hits": [
                {
                    "rank": 1,
                    "model_id": "optionality",
                    "score": 0.91,
                    "signal_type": "select_when",
                }
            ],
        },
        "selected_cards": [
            {
                "model_id": "opportunity-cost",
                "selection_source": "lane_preserved",
                "selection_reason": "Preserve high-provenance lane candidate.",
                "record_status": "supported",
                "source_file": "Opportunity_Cost.md",
                "selected_affordance_cards": [
                    {
                        "chunk_id": "aff::opportunity-cost.displaced-alternative-commitment-gate",
                        "confidence": "high",
                        "activation_shape": {
                            "use_when": ["A choice commits scarce resources."]
                        },
                        "selection_method": "local_relevance",
                        "selection_effect_type": "missing_option",
                        "selection_score": 5,
                        "selection_reason": "Selected affordance by local relevance on terms: alternative, displaced.",
                        "sibling_alternatives_considered": 1,
                    }
                ],
                "selected_absence_records": [
                    {
                        "chunk_id": "abs::opportunity-cost::generic-pro-con-list",
                        "status": "not_supported_by_source",
                        "reason": "Do not promote generic pro/con lists.",
                        "selection_method": "record_order_first",
                        "selection_effect_type": "overclaim_blocker",
                        "selection_score": 0,
                        "selection_reason": "No local lexical match; selected first absence record as explicit fallback.",
                        "sibling_alternatives_considered": 0,
                    }
                ],
            }
        ],
        "telemetry": {
            "selected_chunk_count": 2,
            "selection_source_counts": {"lane_preserved": 1},
            "selected_chunk_selection_methods": {
                "local_relevance": 1,
                "record_order_first": 1,
            },
            "selected_chunk_effect_types": {
                "missing_option": 1,
                "overclaim_blocker": 1,
            },
            "selected_chunk_record_order_fallback_count": 1,
            "skipped_candidate_count": 1,
            "skipped_candidates": [
                {
                    "model_id": "premortem",
                    "source": "embedding_fill",
                    "reason": "not_presented_packet_cap",
                    "stage": "fill",
                }
            ],
            "not_presented_model_ids": ["premortem"],
        },
    }
    r["v60_consideration_ledger"] = {
        "transactions": [
            {
                "chunk_id": "aff::opportunity-cost.displaced-alternative-commitment-gate",
                "model_id": "opportunity-cost",
                "disposition": "used",
                "route": "updated_position",
                "strongest_plausible_application": "Name the displaced alternative.",
                "risk_if_forced": "",
                "why": "It changed the trade-off threshold.",
                "visible_effect": "Named the displaced alternative.",
            },
            {
                "chunk_id": "abs::opportunity-cost::generic-pro-con-list",
                "model_id": "opportunity-cost",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con framing.",
                "risk_if_forced": "Would add ceremony.",
                "why": "The answer did not rely on a generic pro/con list.",
                "visible_effect": "",
            },
        ]
    }
    r["v60_consideration_validation"] = {
        "status": "valid",
        "transaction_count": 2,
        "selected_chunk_count": 2,
        "disposition_counts": {"used": 1, "rejected": 1},
        "used_chunk_ids": ["aff::opportunity-cost.displaced-alternative-commitment-gate"],
        "presented_but_not_used_chunk_ids": [
            "abs::opportunity-cost::generic-pro-con-list"
        ],
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_v60_html()

    assert "Selection source counts" in html
    assert "Lane source counts" in html
    assert "Lane Candidates" in html
    assert "Embedding Hits" in html
    assert "retrieval/rank signal" in html
    assert "Chunk selection methods" in html
    assert "Selected effect types" in html
    assert "missing_option" in html
    assert "overclaim_blocker" in html
    assert "local_relevance" in html
    assert "record_order_first" in html
    assert "Selected affordance by local relevance" in html
    assert "opportunity-cost.displaced-alternative-commitment-gate" in html
    assert "not_presented_packet_cap" in html
    assert "Disposition counts" in html
    assert "Name the displaced alternative." in html
    assert "Would add ceremony." in html


def test_pre_step6_shadow_panel_renders_shadow_decision(monkeypatch):
    r = _fixture_result()
    r["pre_step6_shadow_portfolio"] = {
        "schema_version": "pre_step6_shadow_portfolio.v1",
        "status": "shadow_resolved",
        "mode": "shadow",
        "compiled_card_deck_key": "pre-step6-shadow-card-deck-abc123",
        "cache": {
            "state": "cache_hit",
            "cache_ref": "/tmp/cache/pre-step6-shadow-card-deck-abc123.pre-step6-shadow-card-deck.v1.json",
            "live_card_generation_allowed": False,
        },
        "step6_ledger_signal": "additive_pressure_present",
        "payload_gate": {"status": "preserved"},
        "custody_validation": {"status": "valid"},
        "shadow_visibility_decision": {
            "result": "deck_visible_shadow_only",
            "why": "Step 6 recorded additive pressure and guards passed.",
            "cognitive_signal_source": "step6_private_ledger",
            "normal_runtime_reviewer_calls": 0,
            "applied_to_user_visible_output": False,
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
            "visible_behavior_change_allowed": False,
        },
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_pre_step6_shadow_html()

    assert "Pre-Step-6 Shadow Portfolio" in html
    assert "deck_visible_shadow_only" in html
    assert "additive_pressure_present" in html
    assert "applied: false" in html
    assert "live generation: false" in html


def test_pre_step6_panel_renders_private_table_and_ledger(monkeypatch):
    r = _fixture_result()
    r["pre_step6_private_table"] = {
        "schema_version": "pre_step6_private_table.v1",
        "status": "ready",
        "compiled_card_deck_key": "pre-step6-private-card-deck-abc123",
        "promotion_effect": "stand_down_to_current_step6",
        "table_char_count": 1234,
        "table_section_count": 4,
        "cache": {
            "state": "cache_miss",
            "resolution": "exact_key",
            "cache_ref": "",
            "miss_behavior": "stand_down_to_current_step6",
            "live_card_generation_allowed": False,
        },
        "key_material": {
            "decision_situation": "Whether to report suspected document destruction.",
            "v60_selected_chunk_ids": ["aff::inversion.anti-goal-failure-mechanism-map"],
        },
        "deterministic_role": ["render_current_run_private_table"],
        "gates": {
            "step6_private_context_allowed": True,
            "live_card_generation_allowed": False,
        },
        "sidecars": {
            "markdown": "/tmp/lolla_run_pre_step6_private_table.md",
            "json": "/tmp/lolla_run_pre_step6_private_table.json",
        },
        "source_items": [
            {
                "source_id": "lane2::inversion",
                "source_kind": "lane2_anchor",
                "title": "Inversion",
                "section_id": "lane2_anchor_pressure",
                "source_atom_id": "inversion",
            },
            {
                "source_id": "v60::card::v60-card-001-inversion",
                "source_kind": "v60_selected_card",
                "title": "Inversion",
                "section_id": "v60_private_enrichment",
                "source_atom_id": "v60-card-001-inversion",
            },
        ],
    }
    r["pre_step6_private_table_ledger"] = {
        "schema_version": "pre_step6_private_table_ledger.v1",
        "status": "completed",
        "items": [
            {
                "source_id": "lane2::inversion",
                "source_kind": "lane2_anchor",
                "title": "Inversion",
                "disposition": "used",
                "why": "It changed the answer from reporting-path choice to failure avoidance.",
                "visible_effect": "Counsel became the gatekeeper.",
                "private_guardrail": "Avoid optimizing for reporting speed before privilege safety.",
            },
            {
                "source_id": "v60::card::v60-card-001-inversion",
                "source_kind": "v60_selected_card",
                "title": "Inversion",
                "disposition": "private_guardrail",
                "why": "It stayed private as a constraint.",
                "visible_effect": "",
                "private_guardrail": "Keep failure avoidance tied to a positive next action.",
            },
        ],
    }
    r["run_health"] = {}
    r["run_health"]["pre_step6_private_table_source_item_count"] = 2
    r["run_health"]["pre_step6_private_table_ledger_item_count"] = 2
    r["run_health"]["pre_step6_private_table_unaccounted_source_count"] = 0
    r["run_health"]["pre_step6_private_table_ledger_disposition_counts"] = {
        "private_guardrail": 1,
        "used": 1,
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    html = serve_result._render_pre_step6_shadow_html()

    assert "Pre-Step-6 Private Table" in html
    assert "Source items" in html
    assert "ledger: completed" in html
    assert "cache: cache_miss" in html
    assert "Disposition counts" in html
    assert "private_guardrail" in html
    assert "Counsel became the gatekeeper." in html
    assert "render_current_run_private_table" in html
    assert "pre_step6_private_table.md" in html
    assert "This run has no" not in html


def test_extraction_panel_follows_archive_path_from_run_events(tmp_path, monkeypatch):
    r = _fixture_result()
    r["usage_summary"] = {"run_id": "extraction-test"}
    result_path = tmp_path / "lolla_extraction_test_result.json"
    result_path.write_text(json.dumps(r), encoding="utf-8")

    archive_dir = tmp_path / "archive" / "extraction-test"
    archive_dir.mkdir(parents=True)
    run_events_path = tmp_path / "lolla_extraction_test_run_events.json"
    run_events_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v0.1",
                "run_id": "extraction-test",
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "archive_completed",
                        "occurred_at": "2026-06-24T10:05:00Z",
                        "actor": "operator",
                        "details": {"archive_path": str(archive_dir)},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    extraction_path = archive_dir / "extraction.json"
    extraction_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "capture_health": "good",
                "capture_manifest": {
                    "actual_user_turns": 2,
                    "actual_assistant_turns": 2,
                    "last_turn_role": "ASSISTANT",
                },
                "capture_warnings": [],
                "extraction": {
                    "is_strategic": True,
                    "decision_situation": "Whether to report suspected misconduct.",
                    "original_framing": "The user framed reporting as moral duty versus career risk.",
                    "synthesized_position": "The assistant recommended counsel-first reporting.",
                    "live_constraints": [
                        {
                            "constraint": "Active regulatory audit",
                            "introduced_turn": 1,
                            "status": "active",
                            "weight": "structural",
                            "canonical_key": "active-regulatory-audit",
                        }
                    ],
                    "reasoning_passages": [
                        "External-with-counsel is the defensible path."
                    ],
                    "dropped_threads": [
                        {
                            "thread": "Former colleague may have seen similar conduct",
                            "raised_by": "user",
                            "raised_turn": 7,
                            "status": "acknowledged_then_dropped",
                            "superseded_by": "focus shifted to user's own obligation",
                        }
                    ],
                    "_quote_validation": {
                        "total": 1,
                        "verified": 1,
                        "fabricated": 0,
                        "fabricated_passages": [],
                        "retry_attempted": False,
                        "retry_succeeded": False,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_extraction_html()

    assert "Extraction" in html
    assert str(extraction_path) in html
    assert "Whether to report suspected misconduct." in html
    assert "Active regulatory audit" in html
    assert "External-with-counsel is the defensible path." in html
    assert "Former colleague may have seen similar conduct" in html
    assert "Quote Validation" in html
    assert "actual_user_turns" in html
    assert "active-regulatory-audit" in html


def test_extraction_panel_handles_missing_sidecar(tmp_path, monkeypatch):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.setattr(serve_result, "_RESULT", {})
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_extraction_html()

    assert "Extraction" in html
    assert "No <code>extraction.json</code> sidecar" in html


def test_memo_panel_follows_archive_path_from_run_events(tmp_path, monkeypatch):
    r = _fixture_result()
    r["usage_summary"] = {"run_id": "memo-test"}
    result_path = tmp_path / "lolla_memo_test_result.json"
    result_path.write_text(json.dumps(r), encoding="utf-8")

    archive_dir = tmp_path / "archive" / "memo-test"
    archive_dir.mkdir(parents=True)
    run_events_path = tmp_path / "lolla_memo_test_run_events.json"
    run_events_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v0.1",
                "run_id": "memo-test",
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "archive_completed",
                        "occurred_at": "2026-06-24T10:05:00Z",
                        "actor": "operator",
                        "details": {"archive_path": str(archive_dir)},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    memo_path = archive_dir / "memo.md"
    memo_path.write_text(
        "# Counsel is the gate before reporting\n\n"
        "The shareable answer says to preserve optionality before picking a channel.\n\n"
        "## What changed in the advice\n\n"
        "Internal versus external reporting became a counsel-led sequence.\n",
        encoding="utf-8",
    )
    memo_note_path = archive_dir / "memo_note.json"
    memo_note_path.write_text(
        json.dumps(
            {
                "memo_substantive_title": "Counsel is the gate before reporting",
                "memo_orientation_note": "Use this memo as the product artifact.",
                "memo_what_changed": "The route became counsel-led.",
                "memo_what_still_holds": "Do not confront the partner.",
                "memo_take_back_or_set_aside": "Drop false precision.",
                "memo_pressure_check": "",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_memo_html()

    assert "Memo" in html
    assert str(memo_path) in html
    assert str(memo_note_path) in html
    assert "Counsel is the gate before reporting" in html
    assert "The shareable answer says to preserve optionality" in html
    assert "What changed in the advice" in html
    assert "memo_note.json" in html
    assert "memo_pressure_check" in html
    assert "empty" in html


def test_memo_panel_handles_missing_sidecar(tmp_path, monkeypatch):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")
    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_memo_html()

    assert "Memo" in html
    assert "No <code>memo.md</code> sidecar" in html


def test_run_events_panel_renders_tmp_sidecar(tmp_path, monkeypatch):
    r = _fixture_result()
    r["usage_summary"] = {"run_id": "run-events-test"}
    result_path = tmp_path / "lolla_run_events_test_result.json"
    result_path.write_text(json.dumps(r), encoding="utf-8")
    sidecar_path = tmp_path / "lolla_run_events_test_run_events.json"
    sidecar_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v1",
                "run_id": "run-events-test",
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "run_initialized",
                        "occurred_at": "2026-06-24T10:00:00Z",
                        "actor": "operator",
                        "details": {"latest_env_pointer": "/tmp/lolla_latest_env.sh"},
                    },
                    {
                        "event_id": "event_002",
                        "event_type": "observatory_live",
                        "occurred_at": "2026-06-24T10:05:00Z",
                        "actor": "operator",
                        "details": {"url": "http://localhost:8084", "pid": "123"},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_run_events_html()

    assert "Run Events" in html
    assert str(sidecar_path) in html
    assert "lolla.run_events.v1" in html
    assert "run_initialized" in html
    assert "observatory_live" in html
    assert "http://localhost:8084" in html
    assert "event_002" in html


def test_run_events_panel_handles_missing_sidecar(tmp_path, monkeypatch):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")
    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_run_events_html()

    assert "Run Events" in html
    assert "No <code>run_events.json</code> sidecar" in html


def test_reasoning_trace_panel_follows_archive_path_from_run_events(tmp_path, monkeypatch):
    r = _fixture_result()
    r["usage_summary"] = {"run_id": "trace-test"}
    result_path = tmp_path / "lolla_trace_test_result.json"
    result_path.write_text(json.dumps(r), encoding="utf-8")

    archive_dir = tmp_path / "archive" / "trace-test"
    archive_dir.mkdir(parents=True)
    run_events_path = tmp_path / "lolla_trace_test_run_events.json"
    run_events_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v0.1",
                "run_id": "trace-test",
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "archive_completed",
                        "occurred_at": "2026-06-24T10:05:00Z",
                        "actor": "operator",
                        "details": {"archive_path": str(archive_dir)},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    trace_path = archive_dir / "reasoning_trace.json"
    trace_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.reasoning_trace.v0.1",
                "trace_id": "trace-test",
                "created_at": "2026-06-24T10:06:00Z",
                "trace_adequacy": {
                    "status": "thin",
                    "future_review_ready": False,
                    "error_analysis_ready": True,
                    "coverage": {"source_conversation": "present"},
                    "missing_context": ["live_output_health is not_checked"],
                    "commitment_detection": {
                        "status": "heuristic_v0",
                        "candidate_count": 1,
                    },
                    "outcome_review": {"status": "not_started"},
                },
                "surface_divergence": {
                    "status": "matched",
                    "revised_artifact_present": True,
                    "live_transcript_present": True,
                    "result_revised_answer_present": True,
                    "revised_artifact_matches_result": True,
                    "revised_artifact_found_in_live_transcript": True,
                    "source_refs": {"revised": "revised.txt"},
                },
                "artifacts": [
                    {
                        "path": "conversation.txt",
                        "role": "source_conversation",
                        "sha256": "sha256:abcdef",
                        "bytes": 123,
                        "content_type": "text/plain",
                    }
                ],
                "missing_artifacts": [
                    {
                        "path": "pre_step6_shadow_portfolio.json",
                        "role": "shadow_portfolio_trace",
                    }
                ],
                "model_calls": [
                    {
                        "index": 0,
                        "stage": "pass1_cluster_authority",
                        "provider_name": "openrouter",
                        "model": "google/gemini-3.1-flash-lite",
                        "status": "ok",
                        "total_tokens": 6312,
                        "call_count": 1,
                        "reasoning_disabled": True,
                        "reasoning_details_present": True,
                    }
                ],
                "reasoning_lenses": [
                    {
                        "lens_id": "inversion",
                        "selected": True,
                        "surfaced": True,
                        "disposition": "selected",
                    }
                ],
                "candidate_commitments": [
                    {
                        "candidate_id": "commitment_001",
                        "source_actor": "assistant",
                        "kind": "recommendation",
                        "impact": "medium",
                        "evidence_status": "evidence_missing",
                        "correction_status": "observed",
                        "claim": "Call counsel before reporting.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_reasoning_trace_html()

    assert "Reasoning Trace" in html
    assert str(trace_path) in html
    assert "thin" in html
    assert "live_output_health is not_checked" in html
    assert "pre_step6_shadow_portfolio.json" in html
    assert "pass1_cluster_authority" in html
    assert "Model-call telemetry rows" in html
    assert "Model-Call Telemetry" in html
    assert "Rows may summarize multiple raw provider calls" in html
    assert "<th>Model calls</th>" not in html
    assert "<h2>Model Calls</h2>" not in html
    assert "Reasoning-boundary leaks" in html
    assert "commitment_001" in html
    assert "Call counsel before reporting." in html


def test_reasoning_trace_panel_handles_missing_sidecar(tmp_path, monkeypatch):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")
    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_reasoning_trace_html()

    assert "Reasoning Trace" in html
    assert "No <code>reasoning_trace.json</code> sidecar" in html


def test_graph_survival_panel_follows_archive_path_from_run_events(tmp_path, monkeypatch):
    r = _fixture_result()
    r["usage_summary"] = {"run_id": "survival-test"}
    result_path = tmp_path / "lolla_survival_test_result.json"
    result_path.write_text(json.dumps(r), encoding="utf-8")

    archive_dir = tmp_path / "archive" / "survival-test"
    archive_dir.mkdir(parents=True)
    run_events_path = tmp_path / "lolla_survival_test_run_events.json"
    run_events_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v0.1",
                "run_id": "survival-test",
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "archive_completed",
                        "occurred_at": "2026-06-24T10:05:00Z",
                        "actor": "operator",
                        "details": {"archive_path": str(archive_dir)},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    survival_path = archive_dir / "graph_survival_report.json"
    survival_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.graph_survival_report.v0.1",
                "status": "ready",
                "summary": {
                    "candidate_survival_count": 2,
                    "selected_card_count": 1,
                    "selected_chunk_count": 2,
                    "answer_delta_model_count": 1,
                    "private_guardrail_model_count": 1,
                    "suppressed_model_count": 1,
                    "suppressed_signal_count": 1,
                    "unadjudicated_candidate_count": 0,
                    "embedding_mode": "on",
                    "embedding_hit_count": 2,
                    "selected_model_ids": ["inversion", "moral-hazard"],
                },
                "source_refs": {
                    "result": "result.json",
                    "v60_ledger": "v60_ledger.json",
                },
                "noise_policy": {
                    "unselected_does_not_mean_noise": True,
                    "unknown_noise_status": True,
                    "reason": "Budget suppression is not irrelevance.",
                },
                "candidate_survival": [
                    {
                        "display_name": "Inversion",
                        "model_id": "inversion",
                        "survival_state": "answer_delta",
                        "selected_for_v60": True,
                        "selection_source": "lane_preserved",
                        "embedding_rank": None,
                        "embedding_score": None,
                        "selected_chunk_count": 2,
                        "pre_step6_disposition_counts": {"used": 1},
                        "v60_disposition_counts": {"used": 2},
                        "visible_effects": ["Counsel became the gatekeeper."],
                        "private_guardrails": ["Avoid optimizing report speed first."],
                    },
                    {
                        "display_name": "Moral Hazard",
                        "model_id": "moral-hazard",
                        "survival_state": "budget_suppressed",
                        "selected_for_v60": False,
                        "selection_source": "embedding_fill",
                        "embedding_rank": 8,
                        "embedding_score": 0.0299,
                        "selected_chunk_count": 0,
                        "skipped_reasons": ["not_presented_packet_cap"],
                    },
                ],
                "suppressed_signals": [
                    {
                        "model_id": "moral-hazard",
                        "research_status": "plausible_budget_suppressed",
                        "reason": "not_presented_packet_cap",
                        "source": "embedding_fill",
                        "stage": "fill",
                        "score": 0.0299,
                        "unknown_noise_status": True,
                    }
                ],
                "private_table_survival": [
                    {
                        "source_id": "lane2::inversion",
                        "source_kind": "lane2_anchor",
                        "title": "Inversion",
                        "disposition": "used",
                        "why": "Failure avoidance changed the public answer.",
                        "visible_effect": "Counsel became the gatekeeper.",
                        "private_guardrail": "Avoid premature evidence moves.",
                    }
                ],
                "embedding_selection": {
                    "hits": [
                        {
                            "embedding_rank": 8,
                            "model_id": "moral-hazard",
                            "score": 0.0299,
                            "selected_for_v60": False,
                            "selection_source": "",
                            "research_status": "unadjudicated",
                            "ledger_disposition_counts": {},
                            "skipped_reasons": ["not_presented_packet_cap"],
                        }
                    ]
                },
                "v60_ledger_summary": {
                    "transaction_count": 2,
                    "disposition_counts": {"used": 2},
                    "route_counts": {"updated_position": 1},
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_graph_survival_html()

    assert "Graph Survival" in html
    assert str(survival_path) in html
    assert "lolla.graph_survival_report.v0.1" in html
    assert "answer_delta" in html
    assert "Budget suppression is not irrelevance." in html
    assert "Counsel became the gatekeeper." in html
    assert "moral-hazard" in html
    assert "not_presented_packet_cap" in html
    assert "Private Table Survival" in html
    assert "V60 Ledger Summary" in html


def test_graph_survival_panel_handles_missing_sidecar(tmp_path, monkeypatch):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")
    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    html = serve_result._render_graph_survival_html()

    assert "Graph Survival" in html
    assert "No <code>graph_survival_report.json</code> sidecar" in html


def test_case_api_includes_pre_step6_shadow_portfolio(monkeypatch):
    r = _fixture_result()
    r["pre_step6_shadow_portfolio"] = {
        "schema_version": "pre_step6_shadow_portfolio.v1",
        "status": "shadow_cache_miss",
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    response = serve_result._build_case_response()

    assert response["pre_step6_shadow_portfolio"]["status"] == "shadow_cache_miss"


def test_case_api_includes_pre_step6_private_table(monkeypatch):
    r = _fixture_result()
    r["pre_step6_private_table"] = {
        "schema_version": "pre_step6_private_table.v1",
        "status": "ready",
    }
    r["pre_step6_private_table_ledger"] = {
        "schema_version": "pre_step6_private_table_ledger.v1",
        "status": "completed",
    }
    monkeypatch.setattr(serve_result, "_RESULT", r)

    response = serve_result._build_case_response()

    assert response["pre_step6_private_table"]["status"] == "ready"
    assert response["pre_step6_private_table_ledger"]["status"] == "completed"


def test_graph_api_reports_rendered_counts_separately_from_catalog_stats():
    graph = serve_result._build_graph_response()
    stats = graph["stats"]

    assert stats["companion_count"] == sum(
        1 for node in graph["nodes"] if node.get("role") == "companion"
    )
    assert stats["total_nodes"] == len(graph["nodes"])
    assert stats["rendered_node_count"] == len(graph["nodes"])
    assert stats["rendered_edge_count"] == len(graph["edges"])
    assert stats["catalog_tendency_count"] >= stats["tendency_count"]


def test_dashboard_run_inspector_labels_threshold_count_not_triggered():
    bundle = (
        Path(__file__).resolve().parents[1]
        / "observatory"
        / "build"
        / "assets"
        / "index-H3UEopEj.js"
    ).read_text(encoding="utf-8")

    assert ">threshold</span>" in bundle
    assert ">triggered</span>" not in bundle


def test_audit_index_handles_no_audit_summary(monkeypatch):
    monkeypatch.setattr(serve_result, "_RESULT", _minimal_result())
    html = serve_result._render_audit_index_html()
    # Polite "no audit_summary" message; do not crash; do not expose broken links
    assert "audit_summary" in html.lower() or "no audit data" in html.lower()


def test_usage_page_links_to_audit_index():
    """The /usage page gains a one-line link to /audit (operator discovery surface)."""
    html = serve_result._render_usage_html()
    assert "/audit" in html


# ---------------------------------------------------------------------------
# HTML escaping — every panel must escape user-derived strings
# ---------------------------------------------------------------------------


def test_panels_escape_script_tags_in_user_derived_strings(monkeypatch):
    """Defence against a crafted result.json injecting HTML/JS."""
    r = _fixture_result()
    r["audit_summary"]["companion_rejected_models"][0]["rejection_reason"] = (
        "<script>alert('xss')</script>"
    )
    monkeypatch.setattr(serve_result, "_RESULT", r)
    html = serve_result._render_lane2_html()
    # Raw <script> tag must NOT be present; it must be escaped
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# End-to-end smoke — start a real server and hit the routes
# ---------------------------------------------------------------------------


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    """Spin up serve_result.py on a free port with the fixture result.json.

    Yields the base URL. Tears down via server.shutdown(). Confirms the
    server starts even when STATIC_DIR (the SPA bundle) is absent — the
    portability gate from PR 3.
    """
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")

    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)

    # Force STATIC_DIR to a non-existent path so the test proves the server
    # still serves /audit/* and /usage when the SPA bundle is missing.
    bogus_static = tmp_path / "_no_spa_here"
    monkeypatch.setattr(serve_result, "STATIC_DIR", bogus_static)

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), serve_result.ResultHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # Tiny pause so the listening socket is ready before the first request.
    time.sleep(0.05)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def _http_get(url: str) -> tuple[int, str]:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8")


def test_smoke_all_panels_serve_200_without_spa_bundle(running_server):
    """End-to-end: every /audit/* route + /audit + /usage returns HTTP 200
    even when ``STATIC_DIR`` doesn't exist (skill-portability gate)."""
    paths = [
        "/audit",
        "/audit/extraction",
        "/audit/memo",
        "/audit/lane1",
        "/audit/lane2",
        "/audit/lane4",
        "/audit/anti-echo",
        "/audit/routing",
        "/audit/expansions",
        "/audit/stakeholders",
        "/audit/graph-survival",
        "/audit/reasoning-trace",
        "/audit/events",
        "/usage",
    ]
    for p in paths:
        status, body = _http_get(f"{running_server}{p}")
        assert status == 200, f"{p} returned {status}"
        assert "<html" in body or "<!doctype" in body.lower(), f"{p} did not return HTML"


# ---------------------------------------------------------------------------
# Telemetry FAB injection — bridge from / (SPA) to /audit
# ---------------------------------------------------------------------------


def test_telemetry_fab_injection_inserts_before_body_close():
    """The root injection must place the anchor, style, and patch before </body>."""
    src = b"<html><head></head><body><div id='root'></div></body></html>"
    out = serve_result._inject_telemetry_fab(src).decode("utf-8")
    assert "telemetry-fab" in out
    assert 'href="/audit"' in out
    assert "lolla-main-surface-copy-patch" in out
    assert "Optional Pressure Check" in out
    assert "no Step-7 divergences" in out
    assert "boundary calls" in out
    assert "boundary tokens" in out
    assert "PARTIAL" in out
    # Injected before </body>, not after
    assert out.index("telemetry-fab") < out.index("</body>")
    assert out.index("lolla-main-surface-copy-patch") < out.index("</body>")


def test_telemetry_fab_injection_is_idempotent():
    """Serving the same bytes twice must not double-inject the FAB."""
    src = b"<html><body><div id='root'></div></body></html>"
    once = serve_result._inject_telemetry_fab(src)
    twice = serve_result._inject_telemetry_fab(once)
    assert once == twice
    # Marker appears exactly once
    assert twice.decode("utf-8").count('class="telemetry-fab"') == 1


def test_telemetry_fab_injection_appends_when_no_body_close():
    """Edge case: malformed bundle without </body> — injection still happens."""
    src = b"<html><body><div id='root'></div>"
    out = serve_result._inject_telemetry_fab(src).decode("utf-8")
    assert "telemetry-fab" in out


def test_root_serves_spa_with_fab_injected(tmp_path, monkeypatch):
    """End-to-end: GET / returns the SPA index.html with the Telemetry FAB
    injected. Confirms the do_GET wiring intercepts / before the static-file
    fallback, and that the injection runs on a fresh request."""
    # Stand up a synthetic SPA bundle with a placeholder index.html
    fake_static = tmp_path / "build"
    fake_static.mkdir()
    (fake_static / "index.html").write_bytes(
        b"<html><head><title>SPA</title></head>"
        b"<body><div id='root'>SPA app mount</div></body></html>"
    )
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_fixture_result()), encoding="utf-8")

    monkeypatch.setattr(serve_result, "_RESULT", _fixture_result())
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_RESULT_MTIME", result_path.stat().st_mtime)
    monkeypatch.setattr(serve_result, "STATIC_DIR", fake_static)

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), serve_result.ResultHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    try:
        status, body = _http_get(f"http://127.0.0.1:{port}/")
        assert status == 200
        assert "SPA app mount" in body  # original bundle still there
        assert "telemetry-fab" in body  # FAB injected
        assert 'href="/audit"' in body  # FAB navigates to /audit
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)
