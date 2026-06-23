from __future__ import annotations

from engine.system_b.output_hygiene import (
    LIVE_OUTPUT_LEAK_ISSUE,
    LIVE_OUTPUT_MISSING_ISSUE,
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
