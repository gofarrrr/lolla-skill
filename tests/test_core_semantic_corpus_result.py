from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = REPO_ROOT / "research/core-semantic-corpus-2026-07-09"
COMPARISON_PATH = RESULT_DIR / "corpus-comparison.json"
REASSESSMENT_PATH = RESULT_DIR / "field-decisions-corpus-reassessment.json"
FIELD_DECISIONS_PATH = (
    REPO_ROOT / "research/core-semantic-validation-2026-07-09/field-decisions.json"
)


def test_corpus_result_preserves_complete_run_contract() -> None:
    comparison = json.loads(COMPARISON_PATH.read_text(encoding="utf-8"))
    assert comparison["schema_version"] == "lolla.core_semantic_corpus_comparison.v0"
    assert comparison["case_count"] == 12
    assert comparison["head_to_head"] == {
        "case_count": 12,
        "recall_wins": 12,
        "span_repeatability_wins": 11,
        "labeled_repeatability_wins": 11,
    }
    assert comparison["compact_path"]["gold_observation_count"] == 102
    assert comparison["shadow_path"]["gold_observation_count"] == 102
    assert comparison["shadow_path"]["weighted_mean_recall"] > comparison["compact_path"]["weighted_mean_recall"]
    assert comparison["shadow_path"]["stable_observation_count"] == 49
    assert comparison["shadow_path"]["never_observation_count"] == 41
    assert comparison["operational"]["compact"]["artifact_count"] == 36
    assert comparison["operational"]["shadow"]["artifact_count"] == 36
    assert comparison["operational"]["shadow"]["call_count"] == 144
    assert comparison["operational"]["preserved_failed_attempt_count"] == 1


def test_all_case_manifests_keep_graph_runtime_unchanged() -> None:
    manifests = sorted(RESULT_DIR.glob("case-*/manifest.json"))
    assert len(manifests) == 11
    for path in manifests:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["graph_runtime_modified"] is False
        comparison_path = path.parent / payload["comparison"]["path"]
        assert hashlib.sha256(comparison_path.read_bytes()).hexdigest() == payload["comparison"]["sha256"]


def test_all_46_field_decisions_were_reassessed_without_silent_drift() -> None:
    prior = json.loads(FIELD_DECISIONS_PATH.read_text(encoding="utf-8"))
    reassessment = json.loads(REASSESSMENT_PATH.read_text(encoding="utf-8"))
    prior_names = {item["field_name"] for item in prior["fields"]}
    assert reassessment["field_count"] == 46
    assert set(reassessment["audited_field_names"]) == prior_names
    assert reassessment["changed_decisions"] == []
    assert reassessment["prior_decision_counts"] == reassessment["reassessed_decision_counts"]
    assert reassessment["reassessment_conclusion"]["implementation_readiness"] == "blocked_before_graph_integration"
    assert reassessment["graph_runtime_modified"] is False
    assert hashlib.sha256(FIELD_DECISIONS_PATH.read_bytes()).hexdigest() == reassessment["reassessed_contract_sha256"]
    assert hashlib.sha256(COMPARISON_PATH.read_bytes()).hexdigest() == reassessment["corpus_comparison_sha256"]

