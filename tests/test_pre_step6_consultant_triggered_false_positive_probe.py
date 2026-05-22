from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "research"))

from pre_step6_consultant_triggered_false_positive_probe import (  # noqa: E402
    build_consultant_triggered_contract,
    write_consultant_triggered_contract,
)
from pre_step6_false_positive_visibility_probe import (  # noqa: E402
    validate_false_positive_probe_contract,
)


def test_consultant_triggered_contract_pins_consultant_as_positive_seed_under_probe() -> None:
    contract = build_consultant_triggered_contract(root=REPO_ROOT)

    validate_false_positive_probe_contract(contract)

    case_ids = [case["case_id"] for case in contract["probe_cases"]]
    assert case_ids == [
        "mid-level-consultant-report-2",
        "fp-marker-preserved-entity-lost",
        "fp-bevelin-irrelevant-incentives",
    ]
    consultant = contract["probe_cases"][0]
    assert consultant["shape_id"] == "consultant_shadow_triggered_positive_seed"
    assert "pre-registered classification: positive_seed" in consultant["case_brief"]
    assert "shadow harness fired deck_visible_shadow_only" in consultant["case_brief"]
    assert "If both reviewers prefer the anchor" in consultant["pre_run_failure_hypothesis"]
    assert "manifest previously mislabeled this as negative_control_seed" in (
        " ".join(consultant["false_positive_risk"])
    )
    assert consultant["answer_candidates"]["anchor_visible"].startswith(
        "Do not confront the partner"
    )
    assert consultant["answer_candidates"]["deck_pressure"].startswith(
        "Do not confront your partner"
    )


def test_consultant_triggered_contract_writes_probe_artifact(tmp_path: Path) -> None:
    contract = build_consultant_triggered_contract(root=REPO_ROOT)

    path = write_consultant_triggered_contract(payload=contract, out_dir=tmp_path)

    assert path == tmp_path / "false-positive-visibility-probe.v1.json"
    assert path.read_text(encoding="utf-8").startswith("{")
