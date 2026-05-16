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
    validate_public_answer_hygiene,
    validate_raw_artifact_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "research"
    / "pre-step6-raw-artifact-fixtures"
    / "mother-address-year.raw-artifact-handoff.v1.json"
)


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


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
