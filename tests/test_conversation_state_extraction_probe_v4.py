from __future__ import annotations

from scripts.evals import run_conversation_state_extraction_probe as v1
from scripts.evals import run_conversation_state_extraction_probe_v4 as v4


def test_schema_is_visible_in_prompt_without_changing_system_prompt() -> None:
    contract = {
        "system_prompt": "system",
        "extraction_instruction": "extract",
    }
    case = {
        "source_path": "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/amb1-case03-creative-partnership.txt"
    }
    old = v4._V1_BUILD_PROMPTS(contract, case)
    new = v4.build_prompts(contract, case)
    assert new["system_prompt"] == old["system_prompt"]
    assert new["user_prompt"].startswith(old["user_prompt"])
    assert "LOCAL TYPED RESPONSE SCHEMA" in new["user_prompt"]
    assert '"schema_version":{"enum":["lolla.conversation_state_probe_raw.v1"]' in new["user_prompt"]


def test_invalid_response_never_exposes_empty_sealed_packet(monkeypatch) -> None:
    monkeypatch.setattr(
        v1,
        "_call_openrouter",
        lambda *_args, **_kwargs: {
            "status": "invalid_contract",
            "sealed_packet": {},
            "custody_violation_count": 0,
        },
    )
    result = v4._call_without_empty_packet({}, {})
    assert "sealed_packet" not in result
    assert result["custody_violation_count"] is None
