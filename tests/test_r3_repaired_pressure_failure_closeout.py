from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.r3_fresh_consumer import value_sha256
from scripts.evals.finalize_r3_repaired_pressure_failure import (
    _redact_payload,
    collect_mechanical_findings,
)
from scripts.evals.run_r3_repaired_pressure import validate_execution_contract


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r3-repaired-pressure-execution-contract-v1.json"
AUTHORIZATION = ROOT / "docs/evals/lolla-r3-repaired-pressure-authorization-v1.json"
RESULT_DIR = (
    ROOT
    / "research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired"
)


def _load(name: str) -> dict:
    return json.loads((RESULT_DIR / name).read_text(encoding="utf-8"))


def test_checked_in_failure_closeout_is_hash_linked_and_terminal() -> None:
    closeout = _load("failure-closeout.json")
    terminal = _load("r3-terminal-result.json")
    redacted = _load("provider-payload-redacted.json")

    closeout_hash = closeout.pop("closeout_sha256")
    terminal_hash = terminal.pop("result_sha256")
    redacted_hash = redacted.pop("redacted_payload_sha256")
    assert closeout_hash == value_sha256(closeout)
    assert terminal_hash == value_sha256(terminal)
    assert redacted_hash == value_sha256(redacted)
    assert terminal["status"] == (
        "r3_closed_repaired_transport_pass_mechanical_response_fail"
    )
    assert terminal["closeout_sha256"] == closeout_hash
    assert terminal["next_call_authorized"] is False
    assert closeout["decision"]["quiet_control_authorized"] is False
    assert closeout["mechanical_result"]["candidate_modified_or_healed"] is False
    assert closeout["mechanical_result"]["finding_count"] == 1
    assert closeout["mechanical_result"]["findings"][0]["code"] == (
        "park_contract_violation"
    )
    semantic_verdicts = {
        item["verdict"] for item in closeout["source_review"]["dimensions"][:-1]
    }
    assert semantic_verdicts == {"not_evaluable_mechanical_contract_failed"}
    assert closeout["source_review"]["dimensions"][-1]["verdict"] == "pass"


def test_failure_finding_reproduces_without_healing_candidate() -> None:
    _contract, bundle = validate_execution_contract(
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )
    candidate = _load("pressure-call-result.json")["candidate"]
    exact_before = json.loads(json.dumps(candidate))

    findings = collect_mechanical_findings(
        candidate=candidate,
        packet=bundle["packet"],
    )

    assert candidate == exact_before
    assert findings == [
        {
            "path": "/candidate_dispositions/2",
            "code": "park_contract_violation",
            "observed": {
                "effect": "uncertainty_change",
                "visible_effect": "",
                "private_guardrail": "",
            },
            "expected": "no material effect, empty effects, and reopen condition",
        }
    ]


def test_opaque_reasoning_signature_is_removed_from_commit_safe_payload() -> None:
    raw = {
        "choices": [
            {
                "message": {
                    "content": "{}",
                    "reasoning_details": [
                        {"type": "reasoning.text", "text": "", "signature": "opaque"}
                    ],
                }
            }
        ]
    }

    redacted, redactions = _redact_payload(raw)

    assert raw["choices"][0]["message"]["reasoning_details"][0]["signature"] == (
        "opaque"
    )
    assert redacted["choices"][0]["message"]["reasoning_details"][0][
        "signature"
    ] == "[redacted-opaque-reasoning-signature]"
    assert redactions == [
        {
            "json_pointer": "/choices/0/message/reasoning_details/0/signature",
            "reason": "opaque provider reasoning-continuation metadata",
        }
    ]
