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
    for href in ("/audit/lane1", "/audit/lane2", "/audit/lane4",
                 "/audit/anti-echo", "/audit/routing", "/audit/expansions",
                 "/audit/stakeholders"):
        assert href in html, f"index missing link to {href}"


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
        "/audit/lane1",
        "/audit/lane2",
        "/audit/lane4",
        "/audit/anti-echo",
        "/audit/routing",
        "/audit/expansions",
        "/audit/stakeholders",
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
    """The FAB injection must place the anchor + style before </body>."""
    src = b"<html><head></head><body><div id='root'></div></body></html>"
    out = serve_result._inject_telemetry_fab(src).decode("utf-8")
    assert "telemetry-fab" in out
    assert 'href="/audit"' in out
    # Injected before </body>, not after
    assert out.index("telemetry-fab") < out.index("</body>")


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
