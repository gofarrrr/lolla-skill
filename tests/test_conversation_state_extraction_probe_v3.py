from __future__ import annotations

import json
from urllib import request

from scripts.evals import run_conversation_state_extraction_probe_v3 as v3


def test_wire_repair_changes_only_response_format(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(req, *args, **kwargs):
        captured["body"] = json.loads(req.data)
        return "sentinel"

    monkeypatch.setattr(v3, "_ORIGINAL_URLOPEN", fake_urlopen)
    original = {
        "model": "google/gemini-3.1-flash-lite",
        "messages": [{"role": "user", "content": "x"}],
        "response_format": {"type": "json_schema", "json_schema": {"x": 1}},
        "reasoning": {"enabled": False},
    }
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(original).encode(),
        headers={"Authorization": "Bearer test"},
        method="POST",
    )
    assert v3._json_object_urlopen(req) == "sentinel"
    expected = dict(original)
    expected["response_format"] = {"type": "json_object"}
    assert captured["body"] == expected
