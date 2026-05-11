from __future__ import annotations

from engine.system_b.output_hygiene import (
    PRODUCT_OUTPUT_LEAK_ISSUE,
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


def test_product_hygiene_allows_public_pressure_check_language() -> None:
    report = scan_output_hygiene(
        {
            "pressure_check": (
                "One more pressure check: define the reversal trigger before "
                "the sprint starts. This needs to beat 2 incumbent workflows."
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
