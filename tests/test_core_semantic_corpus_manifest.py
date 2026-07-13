from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
)
REQUIRED_DIMENSIONS = {
    "operative_question",
    "user_corrections_and_pressure",
    "assistant_positions_and_revisions",
    "constraints_and_options",
    "uncertainty_and_evidence_boundaries",
}


def _turns(source: str) -> dict[tuple[int, str], str]:
    marker = re.compile(r"\[Turn (\d+)\] (USER|ASSISTANT):\n")
    matches = list(marker.finditer(source))
    result: dict[tuple[int, str], str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        result[(int(match.group(1)), match.group(2).lower())] = source[start:end].strip()
    return result


def test_corpus_manifest_locks_twelve_complete_source_first_cases() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "lolla.core_semantic_corpus.v0"
    assert manifest["repeat_contract"] == {
        "compact_runs_per_case": 3,
        "shadow_runs_per_case": 3,
        "exact_source_spans_required_for_recall": True,
        "graph_runtime_may_be_modified": False,
    }

    cases = manifest["cases"]
    assert len(cases) == 12
    assert len({case["case_id"] for case in cases}) == 12
    assert len({case["stratum"] for case in cases}) == 12

    corpus_dimensions: set[str] = set()
    for case in cases:
        source_path = REPO_ROOT / case["source_path"]
        context_path = REPO_ROOT / case["context_extraction_path"]
        gold_path = REPO_ROOT / case["gold_path"]
        assert source_path.is_file(), case["case_id"]
        assert context_path.is_file(), case["case_id"]
        assert gold_path.is_file(), case["case_id"]

        source_bytes = source_path.read_bytes()
        assert hashlib.sha256(source_bytes).hexdigest() == case["source_file_sha256"]
        source = source_bytes.decode("utf-8")
        turn_map = _turns(source)
        assert any(speaker == "user" for _, speaker in turn_map)
        assert any(speaker == "assistant" for _, speaker in turn_map)

        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        assert gold["schema_version"] == "lolla.core_semantic_gold.v0"
        assert gold["case_id"] == case["case_id"]
        assert gold["source_file_sha256"] == case["source_file_sha256"]
        observations = gold["required_observations"]
        assert observations
        assert len({item["observation_id"] for item in observations}) == len(observations)

        case_dimensions = {item["dimension"] for item in observations}
        assert REQUIRED_DIMENSIONS <= case_dimensions, case["case_id"]
        corpus_dimensions.update(case_dimensions)

        for observation in observations:
            assert observation["evidence"], observation["observation_id"]
            for evidence in observation["evidence"]:
                key = (evidence["turn_index"], evidence["speaker"])
                assert key in turn_map, (case["case_id"], observation["observation_id"])
                assert evidence["quote"] in turn_map[key], (
                    case["case_id"],
                    observation["observation_id"],
                    evidence["quote"],
                )

    assert "dropped_or_under_carried_threads" in corpus_dimensions

