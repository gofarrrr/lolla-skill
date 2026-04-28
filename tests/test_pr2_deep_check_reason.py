"""PR 2 Fix #2 — populate `DeepCheckResult.reason` on both detection branches.

The Pass 2 prompt previously asked for `reason` only on the
`detected: false` branch. The detected-true branch had `evidence` (a
short factual quote of where the tendency fires) but no equivalent
"why this counts" rationale field. This left the audit memo unable to
ask Pass 2 *why* it landed on the verdict it did when scrolling
`audit_summary.deep_check_results`.

The parser already reads `reason` unconditionally — the only fix here
is the prompt template. These tests pin the parser contract so that
when the LLM returns `reason` on either branch, the field survives
into ``DeepCheckResult`` and into the audit-summary serializer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.deep_checks import (
    PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT,
    parse_pass2_result,
)
from engine.system_b.tendency_catalog import TendencyCatalog, TendencyRef


def _stub_catalog() -> TendencyCatalog:
    ref = TendencyRef(
        tendency_id="anchoring-tendency",
        display_name="Anchoring",
        routing_key="anchoring",
        antidote_model_ids=(),
        tendency_number=1,
    )
    return TendencyCatalog(
        tendencies={"anchoring-tendency": ref},
        alias_index={
            "anchoring": "anchoring-tendency",
            "anchoring-tendency": "anchoring-tendency",
        },
    )


def test_parser_captures_reason_on_detected_true_branch():
    payload = {
        "tendency_id": "anchoring-tendency",
        "tendency_number": 1,
        "detected": True,
        "confidence": 0.7,
        "evidence": "The assistant locked onto the user's $50k figure throughout.",
        "sub_pattern": "general",
        "specific_passage": "we should plan around the $50k budget the user mentioned",
        "severity": "medium",
        "reason": "The first numerical anchor introduced by the user dominated all subsequent reasoning without challenge.",
    }

    result = parse_pass2_result(payload, "anchoring-tendency", _stub_catalog())

    assert result.detected is True
    assert result.reason.startswith("The first numerical anchor")


def test_parser_captures_reason_on_detected_false_branch():
    payload = {
        "tendency_id": "anchoring-tendency",
        "tendency_number": 1,
        "detected": False,
        "confidence": 0.1,
        "reason": "The assistant explicitly questioned the user's initial number and proposed a recalibration.",
    }

    result = parse_pass2_result(payload, "anchoring-tendency", _stub_catalog())

    assert result.detected is False
    assert result.reason.startswith("The assistant explicitly questioned")


def test_pass2_prompt_template_requires_reason_on_both_branches():
    """The prompt must explicitly require `reason` on the detected:true branch.

    Forces the prompt to keep asking for it — otherwise we silently regress
    to the half-empty reason field the audit memo flagged.
    """
    template = PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT
    detected_true_block = template.split("If DETECTED:")[1].split("If NOT DETECTED:")[0]
    detected_false_block = template.split("If NOT DETECTED:")[1]

    assert '"reason"' in detected_true_block, (
        "Pass 2 prompt's detected-true branch must request a `reason` field "
        "so audit_summary.deep_check_results carries the LLM's rationale "
        "on both branches"
    )
    assert '"reason"' in detected_false_block
