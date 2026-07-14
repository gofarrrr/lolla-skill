from pathlib import Path

from scripts.evals.run_simulated_reliability_naturalization_v1 import _load_json, _proposal_review


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    REPO_ROOT
    / "research/simulated-reliability-corpus-v1-2026-07-12/naturalization-contract.json"
)


def _message(role: str, words: int) -> dict[str, str]:
    return {"role": role, "text": " ".join(f"word{i}" for i in range(words))}


def test_completed_naturalization_calls_match_the_frozen_source_contract() -> None:
    contract = _load_json(CONTRACT)
    by_id = {row["case_id"]: row for row in contract["cases"]}
    run_dir = CONTRACT.parent / "naturalization-run"

    assert contract["status"] == "frozen_before_at_most_twelve_no_retry_source_calls"
    assert len(by_id) == 12
    for index in range(1, 13):
        call = _load_json(run_dir / f"call-{index:02d}-result.json")
        frozen = by_id[call["case_id"]]
        assert call["source_path"] == frozen["source_path"]
        assert call["source_sha256"] == frozen["source_sha256"]
        assert call["user_prompt_sha256"] == frozen["user_prompt_sha256"]
        assert call["automatic_retries"] == 0


def test_shape_review_accepts_varied_alternating_dialogue() -> None:
    user_lengths = [25, 50, 65, 80, 110, 55, 150, 35, 70, 95, 45, 125]
    assistant_lengths = [30, 55, 75, 95, 120, 45, 105, 35, 65, 85, 50, 115]
    messages = []
    for user, assistant in zip(user_lengths, assistant_lengths):
        messages.extend([_message("USER", user), _message("ASSISTANT", assistant)])

    result = _proposal_review({"messages": messages})

    assert result["status"] == "provider_free_shape_pass_semantic_review_required"
    assert result["issues"] == []


def test_shape_review_rejects_uniform_dialogue() -> None:
    messages = []
    for _ in range(12):
        messages.extend([_message("USER", 70), _message("ASSISTANT", 65)])

    result = _proposal_review({"messages": messages})

    assert result["status"] == "reject"
    assert "user_length_variation_below_diagnostic_floor" in result["issues"]
    assert "assistant_length_variation_below_diagnostic_floor" in result["issues"]
