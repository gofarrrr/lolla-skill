from __future__ import annotations

from engine.system_b.output_hygiene import (
    LIVE_OUTPUT_LEAK_ISSUE,
    LIVE_OUTPUT_MISSING_ISSUE,
    LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE,
    LIVE_OUTPUT_UNVERIFIED_ISSUE,
    PRODUCT_OUTPUT_LEAK_ISSUE,
    finalize_live_output_hygiene,
    finalize_product_output_hygiene,
    scan_output_hygiene,
)


def test_product_hygiene_flags_internal_terms_on_product_surfaces() -> None:
    report = scan_output_hygiene(
        {
            "revised_answer": "The V60 chunk should become a user-facing evidence gate.",
            "memo_markdown": "Two points survived independent review.",
        }
    )

    assert report["status"] == "unsafe"
    assert report["leak_count"] >= 3
    leaked_terms = {leak["term"] for leak in report["leaks"]}
    assert {"V60", "chunk", "independent review"}.issubset(leaked_terms)


def test_product_hygiene_allows_external_due_diligence_independent_review() -> None:
    report = scan_output_hygiene(
        {
            "revised_answer": (
                "B needs gates: the equity and runway must survive independent "
                "review before the user treats the offer as a calculated risk."
            ),
        }
    )

    assert report["status"] == "clean"
    assert report["leaks"] == []


def test_product_hygiene_allows_internal_terms_on_operator_surfaces() -> None:
    report = scan_output_hygiene(
        {
            "observatory_v60": "V60 selected an affordance chunk and ledger row.",
            "revised_answer": "Ask what evidence would change the decision.",
        },
        surface_roles={"observatory_v60": "operator", "revised_answer": "product"},
    )

    assert report["status"] == "clean"
    assert report["leak_count"] == 0
    assert report["leaks"] == []


def test_product_hygiene_allows_domain_pipeline_but_flags_internal_pipeline() -> None:
    clean = scan_output_hygiene(
        {
            "revised_answer": (
                "Before committing, define the minimum qualified sales pipeline "
                "needed after 60 days."
            ),
        }
    )

    assert clean["status"] == "clean"
    assert clean["leaks"] == []

    unsafe = scan_output_hygiene(
        {
            "revised_answer": "The pipeline flagged an additional pressure point.",
        }
    )

    assert unsafe["status"] == "unsafe"
    assert any(leak["term"] == "pipeline" for leak in unsafe["leaks"])


def test_product_hygiene_flags_live_orchestration_narration() -> None:
    report = scan_output_hygiene(
        {
            "live_narration": (
                "Beat 2 is done. Now launching pressure-check agents before "
                "debugging the V60 ledger."
            ),
        }
    )

    assert report["status"] == "unsafe"
    terms = {leak["term"] for leak in report["leaks"]}
    assert {"Beat", "pressure-check agents", "V60", "ledger"}.issubset(terms)


def test_product_hygiene_flags_live_reader_and_model_orchestration_narration() -> None:
    report = scan_output_hygiene(
        {
            "live_narration": (
                "Spawning pressure-check readers in parallel now.\n"
                "All three readers are in.\n"
                "Orchestrator: Sonnet — phrasing quality may be mildly degraded "
                "vs Opus (see Model Requirements).\n"
                "Now persisting the pressure check and rendering the memo."
            ),
        }
    )

    assert report["status"] == "unsafe"
    terms = {leak["term"] for leak in report["leaks"]}
    assert {
        "pressure-check readers",
        "reader status",
        "orchestrator",
        "Model Requirements",
        "Now persisting",
        "rendering the memo",
    }.issubset(terms)


def test_product_hygiene_allows_public_pressure_check_language() -> None:
    report = scan_output_hygiene(
        {
            "pressure_check": (
                "One more pressure check: define the reversal trigger before "
                "the sprint starts. This needs to outperform 2 incumbent workflows."
            ),
        }
    )

    assert report["status"] == "clean"
    assert report["leaks"] == []


def test_finalize_product_output_hygiene_degrades_unsafe_product_output() -> None:
    result = finalize_product_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        {
            "revised_answer": "The ledger says this affordance should be surfaced.",
        },
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["product_output_health"] == "unsafe"
    assert result["run_health"]["product_output_leak_count"] >= 2
    assert PRODUCT_OUTPUT_LEAK_ISSUE in result["run_health"]["issues"]
    detail = next(
        item
        for item in result["run_health"]["issue_details"]
        if item["code"] == PRODUCT_OUTPUT_LEAK_ISSUE
    )
    assert detail["severity"] == "degraded"
    assert detail["axis"] == "product_output"


def test_finalize_product_output_hygiene_records_clean_product_output() -> None:
    result = finalize_product_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": []},
        },
        {
            "revised_answer": "Ask what evidence would change the decision.",
            "memo_markdown": "## What changed\n\nThe answer is less confident where evidence is thin.",
        },
    )

    assert result["run_health"]["overall"] == "healthy"
    assert result["run_health"]["product_output_health"] == "clean"
    assert result["run_health"]["product_output_leak_count"] == 0
    assert result["product_output_hygiene"]["status"] == "clean"
    assert result["run_health"]["provider_boundary_health"]["status"] == "clean"


def test_provider_boundary_health_marks_clean_product_output_as_contained_warning() -> None:
    result = finalize_product_output_hygiene(
        {
            "run_health": {
                "overall": "partial",
                "issues": ["vendor_boundary_reasoning_leak"],
                "issue_details": [
                    {
                        "code": "vendor_boundary_reasoning_leak",
                        "severity": "partial",
                        "axis": "vendor_boundary",
                        "leak_count": 2,
                        "models": ["google/gemini-3.1-flash-lite-20260507"],
                        "stages": ["extraction", "lane2.companion"],
                    }
                ],
                "boundary_reasoning_leak_detected": True,
                "boundary_reasoning_leak_count": 2,
                "boundary_reasoning_leak_models": [
                    "google/gemini-3.1-flash-lite-20260507"
                ],
                "boundary_reasoning_leak_stages": ["extraction", "lane2.companion"],
            },
        },
        {
            "revised_answer": "Ask what evidence would change the decision.",
            "memo_markdown": "## What changed\n\nThe answer now requires a diligence gate.",
        },
    )

    provider_health = result["run_health"]["provider_boundary_health"]
    assert result["run_health"]["overall"] == "partial"
    assert provider_health["status"] == "warning_contained"
    assert provider_health["affected_call_count"] == 2
    assert provider_health["affected_models"] == [
        "google/gemini-3.1-flash-lite-20260507"
    ]
    assert provider_health["product_output_health"] == "clean"
    assert provider_health["product_contamination_detected"] is False
    assert provider_health["archive_custody_contamination_status"] == "not_detected"
    assert provider_health["raw_reasoning_details_persisted"] is False


def test_provider_boundary_health_marks_product_contamination_separately() -> None:
    result = finalize_product_output_hygiene(
        {
            "run_health": {
                "overall": "partial",
                "issues": ["vendor_boundary_reasoning_leak"],
                "issue_details": [
                    {
                        "code": "vendor_boundary_reasoning_leak",
                        "severity": "partial",
                        "axis": "vendor_boundary",
                        "leak_count": 1,
                    }
                ],
                "boundary_reasoning_leak_detected": True,
                "boundary_reasoning_leak_count": 1,
            },
        },
        {
            "revised_answer": "The V60 chunk should be surfaced.",
        },
    )

    provider_health = result["run_health"]["provider_boundary_health"]
    assert result["run_health"]["overall"] == "degraded"
    assert provider_health["status"] == "confirmed_contamination"
    assert provider_health["product_output_health"] == "unsafe"
    assert provider_health["product_contamination_detected"] is True
    assert provider_health["live_output_contamination_detected"] is False


def test_finalize_product_output_hygiene_clears_stale_leak_issue_after_clean_rerun() -> None:
    unsafe = finalize_product_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        {
            "revised_answer": "The ledger says this affordance should be surfaced.",
        },
    )

    cleaned = finalize_product_output_hygiene(
        unsafe,
        {
            "revised_answer": "Ask what evidence would change the decision.",
        },
    )

    assert cleaned["run_health"]["overall"] == "healthy"
    assert cleaned["run_health"]["product_output_health"] == "clean"
    assert PRODUCT_OUTPUT_LEAK_ISSUE not in cleaned["run_health"]["issues"]
    assert all(
        item["code"] != PRODUCT_OUTPUT_LEAK_ISSUE
        for item in cleaned["run_health"]["issue_details"]
    )


def test_finalize_live_output_hygiene_records_manual_clean_transcript_as_not_checked() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "I have the counterargument; I am folding it into the revised answer now.",
    )

    assert result["run_health"]["overall"] == "healthy"
    assert result["run_health"]["live_output_health"] == "not_checked"
    assert result["run_health"]["live_output_leak_count"] == 0
    assert result["run_health"]["live_output_leaks"] == []
    assert result["live_output_hygiene"]["status"] == "not_checked"
    assert result["live_output_hygiene"]["transcript_status"] == "clean"
    assert result["live_output_hygiene"]["capture_mode"] == "manual_unverified"


def test_finalize_live_output_hygiene_records_clean_trusted_live_transcript() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "I have the counterargument; I am folding it into the revised answer now.",
        trusted_capture=True,
    )

    assert result["run_health"]["overall"] == "healthy"
    assert result["run_health"]["live_output_health"] == "clean"
    assert result["run_health"]["live_output_leak_count"] == 0
    assert result["run_health"]["live_output_leaks"] == []
    assert result["live_output_hygiene"]["status"] == "clean"
    assert result["live_output_hygiene"]["transcript_status"] == "clean"
    assert result["live_output_hygiene"]["capture_mode"] == "trusted"
    assert len(result["live_output_hygiene"]["transcript_sha256"]) == 64


def test_finalize_live_output_hygiene_degrades_unsafe_live_transcript() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "Beat 2 is done. Now debugging the V60 ledger.",
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["live_output_health"] == "unsafe"
    assert result["run_health"]["live_output_leak_count"] >= 3
    assert LIVE_OUTPUT_LEAK_ISSUE in result["run_health"]["issues"]
    assert result["run_health"]["issue_axis_counts"]["live_output"] == 1
    detail = next(
        item
        for item in result["run_health"]["issue_details"]
        if item["code"] == LIVE_OUTPUT_LEAK_ISSUE
    )
    assert detail["severity"] == "degraded"
    assert detail["axis"] == "live_output"


def test_provider_boundary_health_marks_live_contamination_separately() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {
                "overall": "partial",
                "issues": ["vendor_boundary_reasoning_leak"],
                "issue_details": [
                    {
                        "code": "vendor_boundary_reasoning_leak",
                        "severity": "partial",
                        "axis": "vendor_boundary",
                        "leak_count": 1,
                    }
                ],
                "boundary_reasoning_leak_detected": True,
                "boundary_reasoning_leak_count": 1,
                "product_output_health": "clean",
            },
        },
        "Beat 2 is done. Now debugging the V60 ledger.",
    )

    provider_health = result["run_health"]["provider_boundary_health"]
    assert result["run_health"]["overall"] == "degraded"
    assert provider_health["status"] == "confirmed_contamination"
    assert provider_health["product_contamination_detected"] is False
    assert provider_health["live_output_health"] == "unsafe"
    assert provider_health["live_output_contamination_detected"] is True


def test_finalize_live_output_hygiene_degrades_cross_case_updated_position() -> None:
    pivot_revised = """## Updated position

### What survived

I would still keep the main spine of the advice: do not keep grinding the current product just because pivoting is scary, and do not pivot on conversational enthusiasm alone.

### What actually shifted

The next 14 days should be a paid-discovery sprint, not just a pre-buy test. Ask for money, but also force the workflow into concrete shape.
"""
    contaminated_live = """## Updated position

### What survived

The core sequence survives: document what was personally observed, do not investigate, do not confront the partner, do not use work systems for private notes, do not tell colleagues, and get a specialized whistleblower lawyer urgently.

### What actually shifted

I would reframe the recommendation as counsel-first, not regulator-first. Let counsel decide whether the first protected move is regulator, internal, both, or a preservation-oriented disclosure.

## Updated position

### What survived

I would still keep the main spine of the advice: do not keep grinding the current product just because pivoting is scary, and do not pivot on conversational enthusiasm alone.

### What actually shifted

The next 14 days should be a paid-discovery sprint, not just a pre-buy test. Ask for money, but also force the workflow into concrete shape.
"""

    result = finalize_live_output_hygiene(
        {
            "revised_answer": pivot_revised,
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        contaminated_live,
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["live_output_health"] == "unsafe"
    assert result["run_health"]["live_output_semantic_mismatch_count"] == 1
    assert LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE in result["run_health"]["issues"]
    assert LIVE_OUTPUT_LEAK_ISSUE not in result["run_health"]["issues"]
    mismatch = result["live_output_hygiene"]["semantic_mismatches"][0]
    assert mismatch["kind"] == "updated_position_mismatch"
    assert mismatch["line"] == 1


def test_finalize_live_output_hygiene_recomputes_existing_health_summaries() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {
                "overall": "partial",
                "issues": ["vendor_boundary_reasoning_leak"],
                "issue_details": [
                    {
                        "code": "vendor_boundary_reasoning_leak",
                        "severity": "partial",
                        "axis": "vendor_boundary",
                    }
                ],
                "issue_axis_counts": {"vendor_boundary": 1},
                "partial_health_causes": ["vendor_boundary_reasoning_leak"],
            },
        },
        "Beat 2 is done. Now debugging the V60 ledger.",
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["issue_axis_counts"] == {
        "live_output": 1,
        "vendor_boundary": 1,
    }
    assert result["run_health"]["partial_health_causes"] == [
        "vendor_boundary_reasoning_leak"
    ]


def test_finalize_live_output_hygiene_clears_stale_leak_issue_after_clean_rerun() -> None:
    unsafe = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "Beat 2 is done. Now debugging the V60 ledger.",
    )

    cleaned = finalize_live_output_hygiene(
        unsafe,
        "I have the counterargument; I am folding it into the revised answer now.",
        trusted_capture=True,
    )

    assert cleaned["run_health"]["overall"] == "healthy"
    assert cleaned["run_health"]["live_output_health"] == "clean"
    assert LIVE_OUTPUT_LEAK_ISSUE not in cleaned["run_health"]["issues"]
    assert all(
        item["code"] != LIVE_OUTPUT_LEAK_ISSUE
        for item in cleaned["run_health"]["issue_details"]
    )


def test_finalize_live_output_hygiene_marks_manual_clean_transcript_partial_when_required() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "I have the counterargument; I am folding it into the revised answer now.",
        require_live_output_clean=True,
    )

    assert result["run_health"]["overall"] == "partial"
    assert result["run_health"]["live_output_health"] == "not_checked"
    assert LIVE_OUTPUT_UNVERIFIED_ISSUE in result["run_health"]["issues"]
    detail = next(
        item
        for item in result["run_health"]["issue_details"]
        if item["code"] == LIVE_OUTPUT_UNVERIFIED_ISSUE
    )
    assert detail["severity"] == "partial"
    assert detail["axis"] == "live_output"


def test_finalize_live_output_hygiene_records_missing_without_degrading_by_default() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        None,
    )

    assert result["run_health"]["overall"] == "healthy"
    assert result["run_health"]["live_output_health"] == "missing"
    assert result["run_health"]["live_output_leak_count"] == 0
    assert result["run_health"]["live_output_leaks"] == []
    assert LIVE_OUTPUT_MISSING_ISSUE not in result["run_health"]["issues"]
    assert result["live_output_hygiene"]["status"] == "missing"


def test_finalize_live_output_hygiene_marks_missing_partial_when_required() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        None,
        require_live_output_clean=True,
    )

    assert result["run_health"]["overall"] == "partial"
    assert result["run_health"]["live_output_health"] == "missing"
    assert LIVE_OUTPUT_MISSING_ISSUE in result["run_health"]["issues"]
    detail = next(
        item
        for item in result["run_health"]["issue_details"]
        if item["code"] == LIVE_OUTPUT_MISSING_ISSUE
    )
    assert detail["severity"] == "partial"
    assert detail["axis"] == "live_output"
