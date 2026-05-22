from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_payload_omission_gate import (  # noqa: E402
    CATEGORIES,
    build_payload_omission_gate,
    build_payload_omission_payload_from_answers,
    load_payload_omission_payload,
    validate_payload_omission_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_payload_omission_gate_is_diff_based_and_per_category() -> None:
    payload = build_payload_omission_gate(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_payload_omission_payload(payload)

    assert payload["schema_version"] == "pre_step6_payload_omission.v1"
    assert [item["category"] for item in payload["categories"]] == list(CATEGORIES)
    assert payload["visibility_decision"] == "not_decided_by_omission_gate"
    assert payload["gate_result"] in {"preserved", "introduced_omission", "case_n_a"}
    assert payload["gate_action"] in {"promote_eligible", "retest", "defer"}
    for item in payload["categories"]:
        assert set(item) == {
            "category",
            "anchor_present",
            "deck_present",
            "case_live",
            "judgment",
            "detector",
            "anchor_evidence",
            "deck_evidence",
            "missing_anchor_evidence",
        }
        if item["anchor_present"] is False and item["deck_present"] is False:
            assert item["judgment"] == "case_n_a"
        if item["anchor_present"] is True and item["deck_present"] is False:
            assert item["judgment"] == "introduced_omission"


def test_payload_omission_gate_flags_only_anchor_present_deck_absent_rows() -> None:
    payload = build_payload_omission_payload_from_answers(
        case_id="synthetic-date-omission",
        anchor_ref="research/synthetic/anchor",
        deck_ref="research/synthetic/deck",
        anchor_answer=(
            "On Friday, tell Magda through email that you cannot approve the "
            "plan unless the document is verified."
        ),
        deck_answer=(
            "Tell Magda that you cannot approve the plan unless the document is verified."
        ),
    )

    validate_payload_omission_payload(payload)

    by_category = {item["category"]: item for item in payload["categories"]}
    assert by_category["dates_or_dated_windows"]["judgment"] == "introduced_omission"
    assert by_category["dates_or_dated_windows"]["detector"] == "regex_date_window_v0"
    assert by_category["dates_or_dated_windows"]["anchor_evidence"] == ["Friday"]
    assert by_category["dates_or_dated_windows"]["deck_evidence"] == []
    assert payload["gate_result"] == "introduced_omission"
    assert payload["gate_action"] == "retest"
    assert by_category["evidence_checks"]["judgment"] == "preserved"


def test_named_resource_detector_does_not_count_ordinary_capitalized_words() -> None:
    payload = build_payload_omission_payload_from_answers(
        case_id="synthetic-resource-noise",
        anchor_ref="research/synthetic/anchor",
        deck_ref="research/synthetic/deck",
        anchor_answer=(
            "The point is simple. Use RAINN and phone access guidance before "
            "sending screenshots."
        ),
        deck_answer=(
            "The point is simple. Use RAINN and phone access guidance before "
            "sending screenshots."
        ),
    )

    by_category = {item["category"]: item for item in payload["categories"]}
    evidence = by_category["named_resources_or_channels"]["anchor_evidence"]

    assert "RAINN" in evidence
    assert "phone access" in evidence
    assert "screenshots" in evidence
    assert "The" not in evidence
    assert "Use" not in evidence


def test_payload_omission_fixed_suite_fixtures_validate() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-payload-omission-gates"
    paths = sorted(fixture_dir.glob("*.payload-omission.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.payload-omission.v1.json",
        "mid-level-consultant-report-2.payload-omission.v1.json",
        "mother-address-year.payload-omission.v1.json",
        "third-year-phd-student.v2.payload-omission.v1.json",
    ]
    for path in paths:
        payload = load_payload_omission_payload(path)
        validate_payload_omission_payload(payload, path=path)
        assert payload["visibility_decision"] == "not_decided_by_omission_gate"
        assert [item["category"] for item in payload["categories"]] == list(CATEGORIES)
