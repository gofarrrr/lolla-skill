from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_lens_probes import (  # noqa: E402
    LensProbeValidationError,
    validate_lens_probe_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-lens-probes"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_bevelin_lens_probe_fixture_validates() -> None:
    payload = _load_fixture(
        "founder-grant-marcus-equity.high-clutter.bevelin-lens-probe.v1.json"
    )

    validate_lens_probe_payload(payload)


def test_lens_probe_rejects_final_advice_language() -> None:
    payload = _load_fixture(
        "founder-grant-marcus-equity.high-clutter.bevelin-lens-probe.v1.json"
    )
    payload["lens_candidates"][0]["why_it_might_matter"] = (
        "Step 6 should conclude with the final recommendation."
    )

    with pytest.raises(LensProbeValidationError, match="forbidden language"):
        validate_lens_probe_payload(payload)


def test_lens_probe_requires_source_hooks_risks_and_do_not_force_guidance() -> None:
    payload = _load_fixture(
        "founder-grant-marcus-equity.high-clutter.bevelin-lens-probe.v1.json"
    )
    candidate = payload["lens_candidates"][0]
    candidate["source_hooks"] = []
    candidate["risk_if_forced"] = ""
    candidate["risk_if_ignored"] = ""
    payload["do_not_force"] = []

    with pytest.raises(LensProbeValidationError) as exc:
        validate_lens_probe_payload(payload)

    message = str(exc.value)
    assert "source_hooks" in message
    assert "risk_if_forced" in message
    assert "risk_if_ignored" in message
    assert "do_not_force" in message


def test_static_bevelin_lens_probe_fixtures_validate_fixed_suite() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.bevelin-lens-probe.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.bevelin-lens-probe.v1.json",
        "mid-level-consultant-report-2.bevelin-lens-probe.v1.json",
        "mother-address-year.bevelin-lens-probe.v1.json",
        "third-year-phd-student.v2.bevelin-lens-probe.v1.json",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_probe_payload(payload, path=path)
        assert payload["lens_pack"] == "bevelin_seeking_wisdom_v0"
        assert payload["off_narrative_preservation"]["preserve_as"] in {"scan", "parked"}
        assert payload["do_not_force"]
