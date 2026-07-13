from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.evals.run_simulated_reliability_case_v1 import load_contract


ROOT = Path(__file__).resolve().parents[1]
V14 = ROOT / "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
CONTINUATION = ROOT / "docs/evals/simulated-reliability-v1-credit-continuation-contract-v1.json"


def test_credit_continuation_preserves_semantic_runtime_and_primary_seed() -> None:
    base = load_contract(V14)
    continuation = load_contract(CONTINUATION)
    raw = json.loads(CONTINUATION.read_text(encoding="utf-8"))
    for field in ("provider_request", "task_limits", "schema_contract", "pipeline", "frozen_inputs"):
        assert continuation[field] == base[field]
    assert continuation["seeds"]["t1_credit_continuation"] == base["seeds"]["primary"] == 101
    assert raw["activation_prerequisites"]["provider_calls_currently_authorized"] == 0
    assert raw["fidelity"]["semantic_changes"] == 0
    assert raw["evaluation"]["scalar_quality_score"] is None


def test_credit_continuation_only_admits_pre_inference_402_cases() -> None:
    raw = json.loads(CONTINUATION.read_text(encoding="utf-8"))
    seal_path = ROOT / raw["continuation_basis"]["sealed_t1_batch"]
    assert hashlib.sha256(seal_path.read_bytes()).hexdigest() == raw["continuation_basis"]["sealed_t1_batch_sha256"]
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    credit_failure = next(
        row for row in seal["preserved_failures"] if row["stage"] == "starting_transport"
    )
    assert set(raw["transfer"]["authorized_case_ids"]) == set(credit_failure["case_ids"])
    assert "v1-case06-industry-funded-lab" not in raw["transfer"]["authorized_case_ids"]
    assert raw["transfer"]["automatic_retries"] == 0
    assert raw["transfer"]["repeat_ids"] == ["t1_credit_continuation"]
