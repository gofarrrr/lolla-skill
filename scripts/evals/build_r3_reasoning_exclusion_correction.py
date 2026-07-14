#!/usr/bin/env python3
"""Build and validate the provider-free prospective R3 validator result."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402
from engine.system_b.r3_reasoning_exclusion import (  # noqa: E402
    inspect_reasoning_exclusion,
)


CONTRACT = ROOT / (
    "docs/evals/lolla-r3-reasoning-exclusion-prospective-contract-v1.json"
)
RESULT_DIR = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/"
    "prospective-reasoning-validator"
)
RESULT = RESULT_DIR / "validation-result.json"
CALL_RESULT = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
    "pressure-call-result.json"
)
REDACTED_PAYLOAD = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
    "provider-payload-redacted.json"
)
TERMINAL_RESULT = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
    "r3-terminal-result.json"
)
RESULT_SCHEMA = "lolla.r3_reasoning_exclusion_correction_result.v1"
FROZEN_EVIDENCE = {
    "docs/evals/lolla-r3-collapsed-outcome-case-execution-contract-v1.json": (
        "c10cab3a88bf44ee001e43dfd685c0fd4808f3b51197ee529a7e39b222aa20e8"
    ),
    "docs/evals/lolla-r3-collapsed-outcome-case-authorization-v1.json": (
        "46c5d2a0908d653a3679a5ad98b1b242b1cea9e4ffe82c294f8a63c5f408a25c"
    ),
    "scripts/evals/run_r3_collapsed_outcome_case.py": (
        "9d376a4b5857c1c414470f3297b8a250d631a713876cc69197e14d6ca52f2ba0"
    ),
    (
        "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
        "pressure-call-result.json"
    ): "a2b6b8b4bb7eb7ed965ad2881dc32b4d879b589a71efb123e3082150a120f7b4",
    (
        "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
        "provider-payload-redacted.json"
    ): "0ffc9cb6b1ac469fd201a38bece42769de6c811b55e969ac4ed40b55360902e7",
    (
        "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
        "failure-closeout.json"
    ): "3f2d318fb9818e98b261ab77e3be03db640529ad91492233942ed669bfb070d8",
    (
        "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1/"
        "r3-terminal-result.json"
    ): "75076b54bffc61a689ea5796ca95490130315ca72cda02d349a0d5cfe171c2f8",
}
EXPECTED_DECISION = {
    "paid_r3_status": "deferred",
    "new_r3_call_requires": (
        "A separately frozen falsifiable question that existing artifacts and "
        "provider-free tests cannot answer, plus new founder authorization."
    ),
    "next_major_stage": "R4 provider-free corpus and sealed-output replay",
    "provider_backed_r4_authorized": False,
    "runtime_integration_authorized": False,
}


class R3ReasoningCorrectionError(RuntimeError):
    """Raised when prospective validation or frozen custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3ReasoningCorrectionError(f"expected JSON object: {path}")
    return value


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_contract() -> dict[str, Any]:
    contract = _load(CONTRACT)
    invariant = contract.get("prospective_invariant")
    if (
        contract.get("schema_version")
        != "lolla.r3_reasoning_exclusion_prospective_contract.v1"
        or contract.get("status")
        != "provider_free_contract_paid_r3_deferred"
        or contract.get("budget")
        != {
            "provider_calls_authorized": 0,
            "provider_calls_made_by_this_goal": 0,
            "provider_cost_authorized_usd": 0.0,
            "premium_models_authorized": 0,
            "retries_authorized": 0,
            "judges_authorized": 0,
        }
        or contract.get("decision") != EXPECTED_DECISION
        or not isinstance(invariant, Mapping)
        or invariant.get("pass_statuses")
        != [
            "reasoning_absent",
            "reasoning_empty",
            "reasoning_metadata_only",
        ]
        or invariant.get("fail_statuses")
        != ["reasoning_content_present", "reasoning_shape_malformed"]
        or invariant.get("message_content_fields")
        != ["reasoning", "reasoning_content"]
        or invariant.get("detail_content_fields")
        != ["text", "summary", "data", "content", "reasoning"]
        or invariant.get("semantic_inference") is not False
        or invariant.get("provider_specific_routing") is not False
        or invariant.get("provider_values_in_inspection_output") is not False
        or contract.get("historical_non_mutation")
        != {
            "frozen_runner_result_reclassified": False,
            "frozen_mechanical_contract_valid": False,
            "semantic_review_reopened": False,
            "frozen_source_or_candidate_changed": False,
        }
    ):
        raise R3ReasoningCorrectionError("prospective contract boundary drifted")
    frozen = contract.get("frozen_evidence")
    if frozen != FROZEN_EVIDENCE:
        raise R3ReasoningCorrectionError("frozen evidence map drifted")
    for relative, expected_hash in frozen.items():
        path = ROOT / str(relative)
        if not path.is_file() or _file_sha(path) != expected_hash:
            raise R3ReasoningCorrectionError(
                f"frozen evidence hash drifted: {relative}"
            )
    return contract


def _historical_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    call_result = _load(CALL_RESULT)
    redacted = _load(REDACTED_PAYLOAD)
    terminal = _load(TERMINAL_RESULT)
    if (
        call_result.get("status")
        != "pressure_response_valid_reasoning_exclusion_breached"
        or call_result.get("mechanical_contract_valid") is not False
        or call_result.get("source_review_required") is not False
        or call_result.get("reasoning_content_returned") is not True
        or call_result.get("provider_calls") != 1
        or terminal.get("status")
        != "r3_collapsed_attempt_closed_semantic_review_not_evaluable"
        or terminal.get("semantic_review_performed") is not False
        or terminal.get("next_call_authorized") is not False
    ):
        raise R3ReasoningCorrectionError("historical terminal state drifted")
    if redacted.get("redacted_payload_sha256") != value_sha256(
        _without(redacted, "redacted_payload_sha256")
    ):
        raise R3ReasoningCorrectionError("redacted payload self-hash drifted")
    return call_result, redacted, terminal


def _prospective_inspection(redacted: Mapping[str, Any]) -> dict[str, Any]:
    payload = redacted.get("provider_payload")
    choices = payload.get("choices") if isinstance(payload, Mapping) else None
    choice = choices[0] if isinstance(choices, list) and choices else None
    message = choice.get("message") if isinstance(choice, Mapping) else None
    if not isinstance(message, Mapping):
        raise R3ReasoningCorrectionError("redacted provider message is missing")
    inspection = inspect_reasoning_exclusion(message)
    if (
        inspection.status != "reasoning_metadata_only"
        or inspection.exclusion_satisfied is not True
        or inspection.content_present is not False
        or inspection.malformed is not False
        or inspection.detail_count != 1
    ):
        raise R3ReasoningCorrectionError(
            "preserved payload does not match the prospective diagnostic"
        )
    return inspection.to_dict()


def build() -> dict[str, Any]:
    contract = validate_contract()
    call_result, redacted, terminal = _historical_state()
    inspection = _prospective_inspection(redacted)
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "status": "prospective_validator_passed_paid_r3_deferred",
        "contract_file_sha256": _file_sha(CONTRACT),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "frozen_evidence_hashes_verified": len(contract["frozen_evidence"]),
        "historical_result": {
            "call_result_sha256": call_result["call_result_sha256"],
            "terminal_result_sha256": terminal["result_sha256"],
            "frozen_runner_status": call_result["status"],
            "frozen_mechanical_contract_valid": False,
            "semantic_review_performed": False,
            "historical_result_reclassified": False,
        },
        "prospective_diagnostic": {
            "source": "commit_safe_redacted_copy_of_preserved_provider_payload",
            "inspection": inspection,
            "prospective_gate_would_treat_signature_only_envelope_as_content": False,
            "semantic_review_opened": False,
            "provider_response_value_judged": False,
        },
        "privacy_and_custody": {
            "raw_private_payload_read": False,
            "opaque_signature_in_result": False,
            "provider_reasoning_values_in_result": False,
            "redacted_payload_self_hash_verified": True,
            "frozen_file_hashes_verified": True,
        },
        "decision": contract["decision"],
        "next_goal": (
            "Freeze the R4 provider-free corpus/replay manifest and metric vector "
            "before changing extraction or making provider calls."
        ),
    }
    result["result_sha256"] = value_sha256(result)
    _write(RESULT, result)
    return validate()


def validate() -> dict[str, Any]:
    contract = validate_contract()
    _call_result, redacted, _terminal = _historical_state()
    expected_inspection = _prospective_inspection(redacted)
    result = _load(RESULT)
    if result.get("result_sha256") != value_sha256(
        _without(result, "result_sha256")
    ):
        raise R3ReasoningCorrectionError("validation result self-hash drifted")
    if (
        result.get("contract_file_sha256") != _file_sha(CONTRACT)
        or result.get("provider_calls") != 0
        or result.get("provider_cost_usd") != 0.0
        or result.get("frozen_evidence_hashes_verified")
        != len(contract["frozen_evidence"])
        or result.get("historical_result", {}).get(
            "historical_result_reclassified"
        )
        is not False
        or result.get("historical_result", {}).get("semantic_review_performed")
        is not False
        or result.get("prospective_diagnostic", {}).get("inspection")
        != expected_inspection
        or result.get("prospective_diagnostic", {}).get(
            "prospective_gate_would_treat_signature_only_envelope_as_content"
        )
        is not False
        or result.get("prospective_diagnostic", {}).get("semantic_review_opened")
        is not False
        or result.get("prospective_diagnostic", {}).get(
            "provider_response_value_judged"
        )
        is not False
        or result.get("privacy_and_custody")
        != {
            "raw_private_payload_read": False,
            "opaque_signature_in_result": False,
            "provider_reasoning_values_in_result": False,
            "redacted_payload_self_hash_verified": True,
            "frozen_file_hashes_verified": True,
        }
        or result.get("decision") != EXPECTED_DECISION
    ):
        raise R3ReasoningCorrectionError("validation result boundary drifted")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                key: result.get(key)
                for key in (
                    "status",
                    "provider_calls",
                    "provider_cost_usd",
                    "frozen_evidence_hashes_verified",
                    "result_sha256",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
