from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import (  # noqa: E402
    ModelAffordanceValidationError,
    validate_model_affordance_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "model_affordances" / "fixtures"
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "model_affordance.schema.json"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _write_source_for_fixture(payload: dict[str, object], tmp_path: Path) -> Path:
    source_file = str(payload["source_file"])
    quotes: list[str] = []
    for evidence in payload.get("source_evidence", []):
        if isinstance(evidence, dict) and evidence.get("source_quote"):
            quotes.append(str(evidence["source_quote"]))
    for affordance in payload.get("affordances", []):
        if not isinstance(affordance, dict):
            continue
        for evidence in affordance.get("source_evidence", []):
            if isinstance(evidence, dict) and evidence.get("source_quote"):
                quotes.append(str(evidence["source_quote"]))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    (source_root / source_file).write_text("\n\n".join(quotes), encoding="utf-8")
    return source_root


def test_schema_contract_file_exists_and_names_required_statuses() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert set(schema["$defs"]["status"]["enum"]) == {
        "supported",
        "weak_support",
        "not_supported_by_source",
        "source_too_thin",
        "duplicate_of_existing_field",
        "deferred_for_review",
    }


def test_strong_source_backed_record_validates(tmp_path: Path) -> None:
    payload = _load_fixture("theory_of_constraints_valid.json")
    source_root = _write_source_for_fixture(payload, tmp_path)

    validate_model_affordance_payload(
        payload,
        path=FIXTURE_DIR / "theory_of_constraints_valid.json",
        source_roots=(source_root,),
    )


def test_generic_record_fails() -> None:
    payload = _load_fixture("generic_invalid.json")

    with pytest.raises(ModelAffordanceValidationError, match="generic boilerplate"):
        validate_model_affordance_payload(
            payload,
            path=FIXTURE_DIR / "generic_invalid.json",
        )


def test_missing_source_quote_fails() -> None:
    payload = _load_fixture("missing_source_quote_invalid.json")

    with pytest.raises(ModelAffordanceValidationError, match="source_quote"):
        validate_model_affordance_payload(
            payload,
            path=FIXTURE_DIR / "missing_source_quote_invalid.json",
        )


def test_affordance_with_no_source_evidence_fails() -> None:
    payload = _load_fixture("affordance_no_source_evidence_invalid.json")

    with pytest.raises(ModelAffordanceValidationError, match="source_evidence"):
        validate_model_affordance_payload(
            payload,
            path=FIXTURE_DIR / "affordance_no_source_evidence_invalid.json",
        )


def test_unknown_status_fails() -> None:
    payload = _load_fixture("unknown_status_invalid.json")

    with pytest.raises(ModelAffordanceValidationError, match="unknown status"):
        validate_model_affordance_payload(
            payload,
            path=FIXTURE_DIR / "unknown_status_invalid.json",
        )


def test_affordance_with_unknown_status_fails() -> None:
    payload = _load_fixture("theory_of_constraints_valid.json")
    payload["affordances"][0]["status"] = "machine_generated"

    with pytest.raises(ModelAffordanceValidationError, match="unknown status"):
        validate_model_affordance_payload(
            payload,
            path=Path("unknown_affordance_status.json"),
        )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "source_too_thin_valid.json",
        "not_supported_by_source_valid.json",
    ],
)
def test_valid_absence_records_validate(fixture_name: str) -> None:
    payload = _load_fixture(fixture_name)

    validate_model_affordance_payload(payload, path=FIXTURE_DIR / fixture_name)


def test_supported_record_with_zero_affordances_needs_absence_reason() -> None:
    payload = _load_fixture("theory_of_constraints_valid.json")
    unsupported = copy.deepcopy(payload)
    unsupported["affordances"] = []
    unsupported["absence_records"] = []

    with pytest.raises(ModelAffordanceValidationError, match="zero affordances"):
        validate_model_affordance_payload(unsupported, path=Path("unsupported.json"))

    supported_with_absence = copy.deepcopy(unsupported)
    supported_with_absence["absence_records"] = [
        {
            "attempted_field": "affordances",
            "status": "deferred_for_review",
            "reason": "A reviewer intentionally deferred extraction because the source support needs another pass.",
            "runtime_policy": "defer_for_review",
            "source_evidence": [],
        }
    ]
    validate_model_affordance_payload(
        supported_with_absence,
        path=Path("supported_with_absence.json"),
    )


def test_schema_does_not_require_every_model_to_have_affordances() -> None:
    payload = _load_fixture("source_too_thin_valid.json")

    assert payload["affordances"] == []
    validate_model_affordance_payload(
        payload,
        path=FIXTURE_DIR / "source_too_thin_valid.json",
    )
