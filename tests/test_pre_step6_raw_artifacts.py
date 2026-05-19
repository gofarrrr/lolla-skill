from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_raw_artifacts import (  # noqa: E402
    MAX_RENDER_CHARS,
    RawArtifactValidationError,
    render_raw_artifact_handoff,
    score_answer_comparison,
    validate_answer_comparison_payload,
    validate_answer_core_payload,
    validate_public_answer_hygiene,
    validate_raw_artifact_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research" / "pre-step6-raw-artifact-fixtures"
ANSWER_CORE_DIR = REPO_ROOT / "research" / "pre-step6-raw-artifact-answer-cores"
COMPARISON_DIR = REPO_ROOT / "research" / "pre-step6-raw-artifact-comparisons"
FIXTURE_PATH = FIXTURE_DIR / "mother-address-year.raw-artifact-handoff.v1.json"


def _fixture_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.raw-artifact-handoff.v1.json"))


def _load_fixture(path: Path = FIXTURE_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _answer_core_paths() -> list[Path]:
    return sorted(ANSWER_CORE_DIR.glob("*.raw-answer-core.v1.json"))


def _load_answer_core(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _comparison_paths() -> list[Path]:
    return sorted(COMPARISON_DIR.glob("*.raw-vs-control-comparison.v1.json"))


def _load_comparison(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_raw_artifact_fixtures_validate_and_render_under_cap() -> None:
    paths = _fixture_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.raw-artifact-handoff.v1.json",
        "mid-level-consultant-report-2.raw-artifact-handoff.v1.json",
        "mother-address-year.raw-artifact-handoff.v1.json",
        "third-year-phd-student.raw-artifact-handoff.v1.json",
        "user-has-plan-consulting-launch.raw-artifact-handoff.v1.json",
    ]

    for path in paths:
        payload = _load_fixture(path)
        validate_raw_artifact_payload(payload, path=path)
        rendered = render_raw_artifact_handoff(payload)
        assert len(rendered) <= MAX_RENDER_CHARS
        assert "why_provided" not in rendered


def test_all_answer_core_fixtures_validate_and_stay_public() -> None:
    paths = _answer_core_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.raw-answer-core.v1.json",
        "mid-level-consultant-report-2.raw-answer-core.v1.json",
        "mother-address-year.raw-answer-core.v1.json",
        "third-year-phd-student.raw-answer-core.v1.json",
        "user-has-plan-consulting-launch.raw-answer-core.v1.json",
    ]

    for path in paths:
        payload = _load_answer_core(path)
        validate_answer_core_payload(payload, path=path, repo_root=REPO_ROOT)


def test_all_answer_comparisons_validate_and_score_raw_wins() -> None:
    paths = _comparison_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.raw-vs-control-comparison.v1.json",
        "mid-level-consultant-report-2.raw-vs-control-comparison.v1.json",
        "mother-address-year.raw-vs-control-comparison.v1.json",
        "third-year-phd-student.raw-vs-control-comparison.v1.json",
        "user-has-plan-consulting-launch.raw-vs-control-comparison.v1.json",
    ]

    for path in paths:
        payload = _load_comparison(path)
        validate_answer_comparison_payload(payload, path=path, repo_root=REPO_ROOT)
        score = score_answer_comparison(payload)
        assert score["aggregate_decision"] == "raw_wins"
        assert score["raw"] > score["control"]


def test_mother_no_worker_fixture_validates_and_declines_worker() -> None:
    payload = _load_fixture()

    validate_raw_artifact_payload(payload, path=FIXTURE_PATH)

    worker_admission = payload["worker_admission"]
    assert isinstance(worker_admission, dict)
    assert worker_admission["decision"] == "decline_worker"


def test_renderer_preserves_consumption_order_and_stays_capped() -> None:
    rendered = render_raw_artifact_handoff(_load_fixture())

    assert len(rendered) <= MAX_RENDER_CHARS
    assert "why_provided" not in rendered
    assert rendered.index("Grounding:") < rendered.index("Boundary:")
    assert rendered.index("Boundary:") < rendered.index("Relax if:")
    assert rendered.index("Relax if:") < rendered.index("Discard if:")
    assert rendered.index("Discard if:") < rendered.index("Contribution:")
    assert "mother_power_dynamics_worker_decline" in rendered
    assert "Priority hint: discard" in rendered


def test_validator_rejects_missing_source_grounding() -> None:
    payload = _load_fixture()
    artifacts = payload["artifacts"]
    assert isinstance(artifacts, list)
    first = artifacts[0]
    assert isinstance(first, dict)
    del first["source_grounding"]

    with pytest.raises(RawArtifactValidationError, match="source_grounding"):
        validate_raw_artifact_payload(payload)


def test_validator_rejects_too_many_artifacts_and_source_excerpts() -> None:
    payload = _load_fixture()
    artifacts = payload["artifacts"]
    excerpts = payload["source_excerpts"]
    assert isinstance(artifacts, list)
    assert isinstance(excerpts, list)

    extra_a = copy.deepcopy(artifacts[0])
    extra_b = copy.deepcopy(artifacts[1])
    assert isinstance(extra_a, dict)
    assert isinstance(extra_b, dict)
    extra_a["artifact_id"] = "extra_artifact_a"
    extra_b["artifact_id"] = "extra_artifact_b"
    artifacts.extend([extra_a, extra_b])
    excerpts.append({"excerpt_id": "extra-excerpt", "text": "Extra source excerpt."})

    with pytest.raises(RawArtifactValidationError) as exc:
        validate_raw_artifact_payload(payload)

    message = str(exc.value)
    assert "artifacts must not exceed 5" in message
    assert "source_excerpts must not exceed 4" in message


def test_validator_rejects_unknown_source_excerpt_reference() -> None:
    payload = _load_fixture()
    artifacts = payload["artifacts"]
    assert isinstance(artifacts, list)
    first = artifacts[0]
    assert isinstance(first, dict)
    first["source_excerpt_ids"] = ["missing-excerpt"]

    with pytest.raises(RawArtifactValidationError, match="unknown source_excerpt_id"):
        validate_raw_artifact_payload(payload)


def test_public_answer_hygiene_rejects_private_machinery_terms() -> None:
    answer = "Use the first artifact from the bundle and mention the hard_boundary."

    with pytest.raises(RawArtifactValidationError, match="private machinery"):
        validate_public_answer_hygiene(answer)


def test_public_answer_hygiene_allows_normal_prose() -> None:
    validate_public_answer_hygiene(
        "Treat silence in the monitored channel as weak evidence, and keep the "
        "slow plan tied to concrete safety triggers."
    )


def test_answer_core_validation_rejects_missing_expected_pressure() -> None:
    path = ANSWER_CORE_DIR / "third-year-phd-student.raw-answer-core.v1.json"
    payload = _load_answer_core(path)
    payload["expected_inclusions"] = ["a phrase that is not in the answer"]

    with pytest.raises(RawArtifactValidationError, match="expected inclusion"):
        validate_answer_core_payload(payload, repo_root=REPO_ROOT)


def test_answer_core_validation_rejects_forbidden_public_term() -> None:
    path = ANSWER_CORE_DIR / "mother-address-year.raw-answer-core.v1.json"
    payload = _load_answer_core(path)
    payload["answer_core"] = (
        "This answer would leak an artifact into public prose."
    )

    with pytest.raises(RawArtifactValidationError, match="private machinery"):
        validate_answer_core_payload(payload, repo_root=REPO_ROOT)


def test_answer_comparison_rejects_inconsistent_aggregate_decision() -> None:
    path = COMPARISON_DIR / "mother-address-year.raw-vs-control-comparison.v1.json"
    payload = _load_comparison(path)
    payload["aggregate_decision"] = "tie_stop"

    with pytest.raises(RawArtifactValidationError, match="aggregate_decision"):
        validate_answer_comparison_payload(payload, repo_root=REPO_ROOT)


def test_answer_comparison_rejects_unknown_winner() -> None:
    path = COMPARISON_DIR / "founder-grant-marcus-equity.raw-vs-control-comparison.v1.json"
    payload = _load_comparison(path)
    criteria = payload["criteria"]
    assert isinstance(criteria, list)
    first = criteria[0]
    assert isinstance(first, dict)
    first["winner"] = "bundle"

    with pytest.raises(RawArtifactValidationError, match="unknown winner"):
        validate_answer_comparison_payload(payload, repo_root=REPO_ROOT)
