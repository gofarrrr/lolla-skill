from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCLUSION = (
    ROOT / "research/conversation-state-extraction-program-conclusion-2026-07-11"
)
RESULT_PACKAGES = [
    ROOT / "research/conversation-state-microtask-probe-v3-2026-07-11",
    ROOT / "research/conversation-state-microtask-transfer-case01-v4-2026-07-11",
    ROOT / "research/conversation-state-microtask-transfer-case04-v4-2026-07-11",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _payload_sha(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_program_concludes_material_redesign_without_runtime_authority() -> None:
    decision = _load(CONCLUSION / "decision.json")
    assert decision["status"] == "complete_material_redesign_required"
    assert decision["program_usage"]["provider_calls"] == 9
    assert decision["program_usage"]["provider_calls"] < decision["program_usage"][
        "maximum_provider_calls"
    ]
    assert decision["program_usage"]["automatic_retries"] == 0
    assert decision["program_usage"]["estimated_cost_usd"] < decision[
        "program_usage"
    ]["cost_ceiling_usd"]
    assert decision["program_usage"]["graph_calls"] == 0
    assert decision["program_usage"]["pipeline_calls"] == 0
    assert decision["program_usage"]["runtime_changes"] == 0
    assert all(case["case_passed"] is False for case in decision["cases"])
    assert "another prompt-repair round" in decision["not_authorized"]


def test_every_preserved_provider_payload_matches_its_recorded_hash() -> None:
    for name in ("threads", "constraints", "positions"):
        result = _load(RESULT_PACKAGES[0] / f"{name}-result.json")
        assert _payload_sha(result["candidate_payload"]) == result[
            "candidate_payload_sha256"
        ]
    for package in RESULT_PACKAGES[1:]:
        result = _load(package / "observed-results.json")
        assert len(result["calls"]) == 3
        for call in result["calls"]:
            assert _payload_sha(call["candidate_payload"]) == call[
                "candidate_payload_sha256"
            ]


def test_redesign_keeps_hybrid_boundary_instead_of_deterministic_semantic_gating() -> None:
    decision = _load(CONCLUSION / "decision.json")
    redesign = decision["redesign_boundary"]
    assert "deterministic evidence resolution" in redesign["keep"]
    assert any(
        "probabilistic turn-level" in item
        for item in redesign["recommended_architecture"]
    )
    assert any(
        "fresh-context probabilistic synthesis" in item
        for item in redesign["recommended_architecture"]
    )
