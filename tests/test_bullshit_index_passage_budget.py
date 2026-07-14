from __future__ import annotations

from threading import Lock

from engine.system_b.bullshit_index import evaluate_text, merge_passages_to_budget


class _RecordingBoundary:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self._lock = Lock()

    def run_json_with_metadata(self, system_prompt, user_prompt, **kwargs):  # noqa: ANN001, ANN003
        with self._lock:
            self.prompts.append(user_prompt)
        clear = {"detected": False, "reasoning": "", "severity": "clear"}
        return {
            "empty_rhetoric": clear,
            "paltering": clear,
            "weasel_words": clear,
            "unverified_claims": clear,
        }, {}


def test_adjacent_merge_budget_preserves_every_passage_once_and_in_order() -> None:
    passages = [f"passage-{index}" for index in range(25)]
    merged = merge_passages_to_budget(passages, max_passages=12)
    assert len(merged) == 12
    recovered = [part for group in merged for part in group.split("\n\n")]
    assert recovered == passages


def test_bullshit_index_caps_calls_without_dropping_source_text() -> None:
    paragraphs = [
        f"SOURCE-PASSAGE-{index}: " + (f"detail-{index} " * 18)
        for index in range(24)
    ]
    client = _RecordingBoundary()
    profile = evaluate_text(
        "\n\n".join(paragraphs),
        client,
        max_workers=4,
        max_evaluation_passages=12,
    )
    payload = profile.to_payload()
    assert len(client.prompts) == 12
    assert payload["summary"]["source_passage_count"] == 24
    assert payload["summary"]["evaluation_passage_count"] == 12
    assert payload["summary"]["passage_compaction_applied"] is True
    combined_prompts = "\n".join(client.prompts)
    for paragraph in paragraphs:
        assert paragraph.strip() in combined_prompts


def test_merge_budget_rejects_zero_calls() -> None:
    try:
        merge_passages_to_budget(["one"], max_passages=0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("zero call budget should fail")
