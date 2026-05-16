from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_workpacks import (  # noqa: E402
    MAX_PROMPT_CHARS,
    WorkpackValidationError,
    render_worker_prompt,
    validate_admission_payload,
    validate_worker_output_payload,
    validate_workpack_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research" / "pre-step6-workpack-fixtures"
WORKER_OUTPUT_DIR = REPO_ROOT / "research" / "pre-step6-worker-output-fixtures"


def _admission_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.admission.v1.json"))


def _workpack_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.workpack.v1.json"))


def _worker_output_paths() -> list[Path]:
    return sorted(WORKER_OUTPUT_DIR.glob("*.worker-output.v1.json"))


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_admissions_validate_with_expected_three_to_one_pattern() -> None:
    paths = _admission_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.admission.v1.json",
        "mid-level-consultant-report-2.admission.v1.json",
        "mother-address-year.admission.v1.json",
        "third-year-phd-student.admission.v1.json",
    ]

    decisions = {}
    for path in paths:
        payload = _load(path)
        validate_admission_payload(payload, path=path)
        decisions[payload["case_id"]] = payload["decision"]

    assert decisions == {
        "founder-grant-marcus-equity": "admit_worker",
        "mid-level-consultant-report-2": "admit_worker",
        "mother-deciding-address-year": "decline_worker",
        "third-year-phd-student": "admit_worker",
    }


def test_all_workpacks_validate_render_under_cap_and_skip_mother() -> None:
    paths = _workpack_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json",
        "mid-level-consultant-report-2.boundary-evidence-gate.workpack.v1.json",
        "third-year-phd-student.boundary-evidence-gate.workpack.v1.json",
    ]

    for path in paths:
        payload = _load(path)
        validate_workpack_payload(payload, path=path, repo_root=REPO_ROOT)
        rendered = render_worker_prompt(payload)
        assert len(rendered) <= MAX_PROMPT_CHARS
        assert "Do not edit files." in rendered
        assert "Step 6 is the final reasoner" in rendered
        assert "Do not write final answer prose" in rendered
        assert "Return exactly one JSON object and nothing else." in rendered
        assert "Do not use Markdown fences or prose outside the JSON object." in rendered
        assert "schema_version must be: reasoning_artifact.v1" in rendered
        assert "JSON keys must be exactly:" in rendered
        assert "Compact JSON skeleton:" in rendered
        assert '"why_provided": "<=120 chars"' in rendered
        assert "arrays must have at most 3 items" in rendered
        assert "risk_if_ignored" in rendered


def test_renderer_preserves_prompt_order() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.boundary-evidence-gate.workpack.v1.json"
    rendered = render_worker_prompt(_load(path))

    assert rendered.index("SHARED SITUATION BRIEF") < rendered.index("ADMISSION RECORD")
    assert rendered.index("ADMISSION RECORD") < rendered.index("WORKER QUESTION")
    assert rendered.index("WORKER QUESTION") < rendered.index("LOCAL ARTIFACTS")
    assert rendered.index("LOCAL ARTIFACTS") < rendered.index("SOURCE EXCERPTS")
    assert rendered.index("SOURCE EXCERPTS") < rendered.index("FORBIDDEN MOVES")
    assert rendered.index("FORBIDDEN MOVES") < rendered.index("OUTPUT CONTRACT")


def test_mother_decline_has_no_workpack_fixture() -> None:
    assert not (
        FIXTURE_DIR / "mother-address-year.boundary-evidence-gate.workpack.v1.json"
    ).exists()


def test_all_worker_output_fixtures_validate() -> None:
    paths = _worker_output_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.rendered-replay.worker-output.v1.json",
        "mid-level-consultant-report-2.rendered-replay.worker-output.v1.json",
        "third-year-phd-student.rendered-replay.worker-output.v1.json",
    ]

    for path in paths:
        validate_worker_output_payload(_load(path), path=path)


def test_admission_rejects_decline_with_expected_contribution() -> None:
    path = FIXTURE_DIR / "mother-address-year.admission.v1.json"
    payload = _load(path)
    payload["expected_artifact_contribution"] = "A tempting but wrong artifact."

    with pytest.raises(WorkpackValidationError, match="declined worker must use none"):
        validate_admission_payload(payload)


def test_workpack_rejects_missing_shared_situation_brief() -> None:
    path = FIXTURE_DIR / "founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json"
    payload = _load(path)
    del payload["shared_situation_brief"]

    with pytest.raises(WorkpackValidationError, match="shared_situation_brief"):
        validate_workpack_payload(payload)


def test_workpack_rejects_declined_admission_gate() -> None:
    path = FIXTURE_DIR / "founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json"
    payload = _load(path)
    gate = payload["admission_gate"]
    assert isinstance(gate, dict)
    gate["decision"] = "decline_worker"

    with pytest.raises(WorkpackValidationError, match="admission_gate must be admit_worker"):
        validate_workpack_payload(payload)


def test_workpack_rejects_declined_admission_reference() -> None:
    path = FIXTURE_DIR / "founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json"
    payload = _load(path)
    payload["case_id"] = "mother-deciding-address-year"
    payload["admission_ref"] = (
        "research/pre-step6-workpack-fixtures/mother-address-year.admission.v1.json"
    )

    with pytest.raises(WorkpackValidationError, match="workpacks require admitted admission_ref"):
        validate_workpack_payload(payload, repo_root=REPO_ROOT)


def test_workpack_rejects_too_many_artifacts_and_source_excerpts() -> None:
    path = FIXTURE_DIR / "mid-level-consultant-report-2.boundary-evidence-gate.workpack.v1.json"
    payload = _load(path)
    local_artifacts = payload["local_artifacts"]
    source_excerpts = payload["source_excerpts"]
    assert isinstance(local_artifacts, list)
    assert isinstance(source_excerpts, list)

    while len(local_artifacts) <= 5:
        extra = copy.deepcopy(local_artifacts[0])
        assert isinstance(extra, dict)
        extra["artifact_id"] = f"extra_{len(local_artifacts)}"
        local_artifacts.append(extra)

    while len(source_excerpts) <= 4:
        extra_excerpt = copy.deepcopy(source_excerpts[0])
        assert isinstance(extra_excerpt, dict)
        extra_excerpt["excerpt_id"] = f"extra_{len(source_excerpts)}"
        source_excerpts.append(extra_excerpt)

    with pytest.raises(WorkpackValidationError) as exc:
        validate_workpack_payload(payload)

    message = str(exc.value)
    assert "local_artifacts must not exceed 5" in message
    assert "source_excerpts must not exceed 4" in message


def test_workpack_rejects_incomplete_output_contract() -> None:
    path = FIXTURE_DIR / "third-year-phd-student.boundary-evidence-gate.workpack.v1.json"
    payload = _load(path)
    contract = payload["output_contract"]
    assert isinstance(contract, dict)
    fields = contract["required_fields"]
    assert isinstance(fields, list)
    fields.remove("relaxation_condition")

    with pytest.raises(WorkpackValidationError, match="relaxation_condition"):
        validate_workpack_payload(payload)


def test_worker_output_rejects_missing_required_field() -> None:
    path = WORKER_OUTPUT_DIR / "third-year-phd-student.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    del payload["relation_to_bundle"]

    with pytest.raises(WorkpackValidationError, match="relation_to_bundle"):
        validate_worker_output_payload(payload)


def test_worker_output_allows_grounding_list() -> None:
    path = WORKER_OUTPUT_DIR / "founder-grant-marcus-equity.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    payload["source_grounding"] = ["Marcus drives about 40% of technical capability."]

    validate_worker_output_payload(payload)


def test_worker_output_rejects_list_for_boundary() -> None:
    path = WORKER_OUTPUT_DIR / "founder-grant-marcus-equity.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    payload["hard_boundary"] = ["Do not grant permanent concessions yet."]

    with pytest.raises(WorkpackValidationError, match="hard_boundary"):
        validate_worker_output_payload(payload)


def test_worker_output_rejects_too_many_grounding_items() -> None:
    path = WORKER_OUTPUT_DIR / "founder-grant-marcus-equity.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    payload["source_grounding"] = [
        "one",
        "two",
        "three",
        "four",
        "five",
    ]

    with pytest.raises(WorkpackValidationError, match="source_grounding"):
        validate_worker_output_payload(payload)


def test_worker_output_rejects_over_cap_payload() -> None:
    path = WORKER_OUTPUT_DIR / "third-year-phd-student.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    payload["hard_boundary"] = "x" * 2000

    with pytest.raises(WorkpackValidationError, match="max is 1500"):
        validate_worker_output_payload(payload)


def test_worker_output_rejects_unknown_fields() -> None:
    path = WORKER_OUTPUT_DIR / "mid-level-consultant-report-2.rendered-replay.worker-output.v1.json"
    payload = _load(path)
    payload["final_answer"] = "This should not be in a worker artifact."

    with pytest.raises(WorkpackValidationError, match="unknown field 'final_answer'"):
        validate_worker_output_payload(payload)
