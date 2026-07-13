from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.replay_reasoning_process_view_specific_probe import replay


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "research/reasoning-process-view-specific-probe-2026-07-11"
REPLAY_DIR = ROOT / "research/reasoning-process-view-specific-replay-2026-07-11"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_compiler_only_replay_preserves_payloads_and_adds_no_calls(
    tmp_path: Path,
) -> None:
    report = replay(
        root=ROOT, probe_dir=PROBE_DIR, output_dir=tmp_path / "replay"
    )
    assert report["status"] == "compiler_only_replay_complete"
    assert report["summary"] == {
        "preserved_payload_count": 5,
        "typed_and_compiled_count_after_replay": 5,
        "response_change_count": 0,
        "provider_calls": 0,
        "embedding_calls": 0,
        "evaluator_calls": 0,
        "graph_calls": 0,
        "runtime_calls": 0,
    }
    for item in report["results"]:
        compiled = _load(Path(item["compiled_path"]))
        assert compiled["response_changed"] is False
        assert compiled["view_validation"]["semantic_correctness_validated"] is False
        assert all(
            disposition["authority"] == "probabilistic_reader"
            for disposition in compiled["view"]["dispositions"]
        )
        assert all(
            observation["provenance"]["producer_kind"] == "model"
            for observation in compiled["model_addendum"]["observations"]
        )


def test_source_review_keeps_semantic_failure_separate_from_custody_repair() -> None:
    review = _load(REPLAY_DIR / "source-review.json")
    assert review["status"] == "source_review_complete_gate_failed"
    assert review["compiler_failure_classification"]["response_change_count"] == 0
    assert review["compiler_failure_classification"]["additional_provider_call_count"] == 0
    assert review["evidence_vector"]["stable_alias_references"] == "61/61"
    assert review["evidence_vector"]["protected_target_visibility"] == "4/5"
    assert review["evidence_vector"]["semantic_view_pass"] == "2/5"
    assert review["evidence_vector"]["critical_dimension_zero_count"] == 1
    assert review["decision"]["development_gate_passed"] is False
    assert review["decision"]["phase4_transfer_authorized"] is False
    assert review["decision"]["another_model_repair_authorized"] is False
