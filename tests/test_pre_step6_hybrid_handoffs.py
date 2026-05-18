from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_hybrid_handoffs import (  # noqa: E402
    MAX_RENDER_CHARS,
    HybridHandoffValidationError,
    render_hybrid_handoff,
    validate_hybrid_handoff_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research" / "pre-step6-hybrid-handoff-fixtures"


def _fixture_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.hybrid-handoff.v1.json"))


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_hybrid_handoff_fixtures_validate_and_render_under_cap() -> None:
    paths = _fixture_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.hybrid-handoff.v1.json",
        "mid-level-consultant-report-2.hybrid-handoff.v1.json",
        "mother-address-year.hybrid-handoff.v1.json",
        "third-year-phd-student.hybrid-handoff.v1.json",
    ]

    for path in paths:
        payload = _load(path)
        validate_hybrid_handoff_payload(payload, path=path, repo_root=REPO_ROOT)
        rendered = render_hybrid_handoff(payload, repo_root=REPO_ROOT)
        assert len(rendered) <= MAX_RENDER_CHARS
        if payload["handoff_mode"] == "card_first":
            assert "Use the card first." in rendered
            assert "Use the card as the default." in rendered
            assert "Preserve the card's risk-if-ignored" in rendered
            assert "Inspect raw only for the named nuance." in rendered
        else:
            assert payload["handoff_mode"] == "no_extra_pressure"
            assert "No extra pressure is authorized" in rendered
            assert "Do not add conceptual pressure" in rendered
            assert "Use no raw inspect-more material." in rendered


def test_renderer_preserves_card_first_ordering() -> None:
    path = FIXTURE_DIR / "mid-level-consultant-report-2.hybrid-handoff.v1.json"
    rendered = render_hybrid_handoff(_load(path), repo_root=REPO_ROOT)

    assert rendered.index("CARD") < rendered.index("INSPECT MORE")
    assert rendered.index("INSPECT MORE") < rendered.index("STEP 6 RULE")
    assert rendered.index("Pressure:") < rendered.index("Raw nuance:")


def test_founder_fixture_authorizes_no_raw_inspection() -> None:
    path = FIXTURE_DIR / "founder-grant-marcus-equity.hybrid-handoff.v1.json"
    payload = _load(path)
    validate_hybrid_handoff_payload(payload, path=path, repo_root=REPO_ROOT)
    rendered = render_hybrid_handoff(payload, repo_root=REPO_ROOT)

    assert payload["inspect_more"] == []
    assert "Raw inspection is not authorized for this fixture." in rendered


def test_mother_quiet_fixture_authorizes_no_card_or_raw_inspection() -> None:
    path = FIXTURE_DIR / "mother-address-year.hybrid-handoff.v1.json"
    payload = _load(path)
    validate_hybrid_handoff_payload(payload, path=path, repo_root=REPO_ROOT)
    rendered = render_hybrid_handoff(payload, repo_root=REPO_ROOT)

    assert payload["handoff_mode"] == "no_extra_pressure"
    assert "source_pressure_card" not in payload
    assert payload["inspect_more"] == []
    assert "CARD" not in rendered
    assert "INSPECT MORE" not in rendered
    assert "Raw nuance:" not in rendered
    assert "Use the card first." not in rendered
    assert "silence in the monitored channel is weak evidence, not reassurance" in rendered
    assert "professional guidance and visible safety triggers" in rendered
    assert "tone remains humane" in rendered
    assert "power-dynamics lens" in rendered
    assert "unsupported grooming probabilities" in rendered
    assert "extra length just because a handoff exists" in rendered


def test_phd_fixture_recovers_base_rate_humility() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.hybrid-handoff.v1.json"
    payload = _load(path)
    rendered = render_hybrid_handoff(payload, repo_root=REPO_ROOT)

    assert "base-rate humility" in rendered
    assert "not calibrated probability claims" in rendered
    assert "numeric success priors" in rendered


def test_consultant_fixture_recovers_counsel_and_wednesday_nuance() -> None:
    path = FIXTURE_DIR / "mid-level-consultant-report-2.hybrid-handoff.v1.json"
    payload = _load(path)
    rendered = render_hybrid_handoff(payload, repo_root=REPO_ROOT)

    assert "counsel's channel bias" in rendered
    assert "audit-committee-first" in rendered
    assert "If the partner raises the encounter Wednesday" in rendered
    assert "do not deny, elaborate, confront, investigate" in rendered


def test_hybrid_handoff_rejects_unknown_inspect_reason() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.hybrid-handoff.v1.json"
    payload = _load(path)
    inspect_more = payload["inspect_more"]
    assert isinstance(inspect_more, list)
    first = inspect_more[0]
    assert isinstance(first, dict)
    first["reason"] = "curious"

    with pytest.raises(HybridHandoffValidationError, match="unknown inspect reason"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)


def test_hybrid_handoff_rejects_too_many_inspect_more_items() -> None:
    path = FIXTURE_DIR / "mid-level-consultant-report-2.hybrid-handoff.v1.json"
    payload = _load(path)
    inspect_more = payload["inspect_more"]
    assert isinstance(inspect_more, list)
    extra = copy.deepcopy(inspect_more[0])
    assert isinstance(extra, dict)
    extra["artifact_id"] = "consultant_internal_channel_distinction"
    inspect_more.append(extra)

    with pytest.raises(HybridHandoffValidationError, match="must not exceed 2"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)


def test_hybrid_handoff_rejects_unknown_raw_artifact_id() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.hybrid-handoff.v1.json"
    payload = _load(path)
    inspect_more = payload["inspect_more"]
    assert isinstance(inspect_more, list)
    first = inspect_more[0]
    assert isinstance(first, dict)
    first["artifact_id"] = "missing_artifact"

    with pytest.raises(HybridHandoffValidationError, match="unknown artifact_id"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)


def test_hybrid_handoff_rejects_overlong_raw_excerpt() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.hybrid-handoff.v1.json"
    payload = _load(path)
    inspect_more = payload["inspect_more"]
    assert isinstance(inspect_more, list)
    first = inspect_more[0]
    assert isinstance(first, dict)
    first["raw_excerpt"] = "x" * 800

    with pytest.raises(HybridHandoffValidationError, match="raw_excerpt"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)


def test_card_first_handoff_requires_source_pressure_card() -> None:
    path = FIXTURE_DIR / "founder-grant-marcus-equity.hybrid-handoff.v1.json"
    payload = _load(path)
    del payload["source_pressure_card"]

    with pytest.raises(HybridHandoffValidationError, match="source_pressure_card"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)


def test_quiet_handoff_rejects_pressure_card_or_raw_inspection() -> None:
    path = FIXTURE_DIR / "mother-address-year.hybrid-handoff.v1.json"
    payload = _load(path)
    payload["source_pressure_card"] = (
        "research/pre-step6-pressure-card-fixtures/"
        "founder-grant-marcus-equity.native.pressure-card.v1.json"
    )

    with pytest.raises(HybridHandoffValidationError, match="must not set source_pressure_card"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)

    payload = _load(path)
    payload["inspect_more"] = [
        {
            "reason": "missing_nuance",
            "source_raw_handoff": (
                "research/pre-step6-raw-artifact-fixtures/"
                "mother-address-year.raw-artifact-handoff.v1.json"
            ),
            "artifact_id": "mother_surveillance_instrument_trust_gate",
            "raw_excerpt": "Silence in the channel you can see is weak evidence.",
            "use_only_to_recover": "Restore monitored-channel caution.",
            "do_not_expand_into": "Do not add a raw-inspection path.",
        }
    ]

    with pytest.raises(HybridHandoffValidationError, match="must be empty"):
        validate_hybrid_handoff_payload(payload, repo_root=REPO_ROOT)
