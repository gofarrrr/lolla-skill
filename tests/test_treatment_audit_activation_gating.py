from __future__ import annotations

import ast
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_treatment_audit import (  # noqa: E402
    MERGE_GATE_GAP_STATUSES,
    ModelTreatmentAuditValidationError,
    compute_evidence_tier,
    validate_treatment_audit_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "data" / "treatment_audits"
BASE_REF = "feature/knowledge-substrate-pr3-compiler"
CASE_CATEGORY_TERMS = (
    "family",
    "negotiation",
    "equity",
    "startup",
    "phd",
    "whistleblower",
    "consulting",
    "consultant",
)
PRODUCTION_AUDIT_FILES = (
    REPO_ROOT / "engine/system_b/model_treatment_audit.py",
    REPO_ROOT / "scripts/run_model_treatment_audit.py",
)


def _audit_paths() -> list[Path]:
    return sorted(
        path for path in AUDIT_DIR.glob("*__*.json") if not path.name.endswith(".v1.json")
    )


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_item(payload: dict[str, object], predicate) -> dict[str, object]:
    for item in payload["items"]:
        if predicate(item):
            return item
    raise AssertionError("fixture item not found")


def test_v2_schema_fields_validate_for_all_committed_audits() -> None:
    for path in _audit_paths():
        payload = _load(path)
        validate_treatment_audit_payload(payload)
        for item in payload["items"]:
            assert item["activation_status"]
            assert len(item["activation_note"]) >= 40
            assert "activation_quote" in item
            assert item["evidence_tier"] == compute_evidence_tier(item)


def test_gap_status_requires_activated_affordance() -> None:
    payload = _load(_audit_paths()[0])
    broken = copy.deepcopy(payload)
    item = _first_item(
        broken,
        lambda row: row["treatment_status"] in MERGE_GATE_GAP_STATUSES
        and row["activation_status"] == "activated",
    )
    item["activation_status"] = "not_activated"
    item["activation_quote"] = ""
    item["evidence_tier"] = compute_evidence_tier(item)

    with pytest.raises(ModelTreatmentAuditValidationError, match="requires activation_status activated"):
        validate_treatment_audit_payload(broken)


def test_evidence_tier_must_match_deterministic_rules() -> None:
    payload = _load(_audit_paths()[0])
    broken = copy.deepcopy(payload)
    item = _first_item(
        broken,
        lambda row: row["evidence_tier"] == "tier_1_net_new_decision_gap",
    )
    item["evidence_tier"] = "excluded"

    with pytest.raises(ModelTreatmentAuditValidationError, match="evidence_tier .* should be"):
        validate_treatment_audit_payload(broken)


def test_output_and_activation_quotes_are_exact_substrings() -> None:
    for path in _audit_paths():
        payload = _load(path)
        case_context = str(payload["case_context"])
        audited_output = str(payload["audited_output"])
        for item in payload["items"]:
            output_quote = str(item["output_quote"])
            if item["treatment_status"] in {
                "treated",
                "partially_treated",
                "set_aside_with_reason",
                "duplicate_of_existing_pressure",
            }:
                assert output_quote
            if output_quote:
                assert output_quote in str(item.get("audited_output_slice") or audited_output)

            activation_quote = str(item["activation_quote"])
            if item["activation_status"] == "activated":
                assert activation_quote
                assert activation_quote in case_context


def test_production_audit_code_has_no_case_category_string_literals() -> None:
    found: list[str] = []
    for path in PRODUCTION_AUDIT_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            lowered = node.value.lower()
            for term in CASE_CATEGORY_TERMS:
                if term in lowered:
                    found.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}:{term}")

    assert found == []


def test_affordance_records_unchanged_from_compiler_branch() -> None:
    paths = [
        *sorted((REPO_ROOT / "data/model_affordances/pilot").glob("*.json")),
        REPO_ROOT / "data/compiled/model_affordances/affordances_v1.json",
    ]
    assert paths

    for path in paths:
        rel = path.relative_to(REPO_ROOT).as_posix()
        expected = subprocess.run(
            ["git", "show", f"{BASE_REF}:{rel}"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        assert path.read_text(encoding="utf-8") == expected
