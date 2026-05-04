from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.model_affordance_validation import validate_model_affordance_file  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = REPO_ROOT / "data" / "model_affordances" / "pilot"
PILOT_MANIFEST_PATH = REPO_ROOT / "data" / "model_affordances" / "pilot_manifest.json"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
KNOWLEDGE_GRAPH_PATH = REPO_ROOT / "data" / "knowledge_graph.json"
AFFORDANCE_ID_RE = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$"
)

EXPECTED_MODEL_IDS = {
    "theory-of-constraints",
    "second-order-thinking",
    "power-dynamics",
    "base-rates",
    "optionality",
    "premortem",
    "inversion",
    "problem-framing-and-reframing",
    "confidence-calibration",
    "systems-thinking",
}


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pilot_manifest() -> dict[str, object]:
    return _load_json(PILOT_MANIFEST_PATH)


def _pilot_records() -> list[dict[str, object]]:
    manifest = _pilot_manifest()
    records = manifest["records"]
    assert isinstance(records, list)
    return records


def _payload_for(record: dict[str, object]) -> dict[str, object]:
    return _load_json(REPO_ROOT / str(record["record_path"]))


def _iter_evidence(payload: dict[str, object]) -> Iterable[dict[str, object]]:
    for evidence in payload.get("source_evidence", []):
        assert isinstance(evidence, dict)
        yield evidence
    for affordance in payload.get("affordances", []):
        assert isinstance(affordance, dict)
        for evidence in affordance.get("source_evidence", []):
            assert isinstance(evidence, dict)
            yield evidence
    for absence in payload.get("absence_records", []):
        assert isinstance(absence, dict)
        for evidence in absence.get("source_evidence", []):
            assert isinstance(evidence, dict)
            yield evidence


def test_pilot_manifest_enumerates_exactly_ten_existing_records() -> None:
    manifest = _pilot_manifest()

    assert manifest["status"] == "draft_review_only"
    assert manifest["target_base_branch"] == "feature/knowledge-use-schema"
    assert manifest["source_residency"]["decision"] == "A"

    records = _pilot_records()
    assert len(records) == 10
    assert {str(record["model_id"]) for record in records} == EXPECTED_MODEL_IDS

    for record in records:
        record_path = REPO_ROOT / str(record["record_path"])
        source_path = REPO_ROOT / str(record["source_path"])
        assert record_path.exists()
        assert source_path.exists()

        payload = _load_json(record_path)
        assert record["model_id"] == payload["model_id"]
        assert record["source_file"] == payload["source_file"]
        assert record["affordance_count"] == len(payload["affordances"])
        assert record["absence_count"] == len(payload["absence_records"])


def test_all_pilot_records_validate_against_schema_and_sources() -> None:
    for record in _pilot_records():
        validate_model_affordance_file(
            REPO_ROOT / str(record["record_path"]),
            source_roots=(SOURCE_DIR,),
        )


def test_source_quotes_are_exact_substrings_of_named_source_file() -> None:
    source_text_cache: dict[str, str] = {}

    for record in _pilot_records():
        payload = _payload_for(record)
        for evidence in _iter_evidence(payload):
            source_file = str(evidence["source_file"])
            source_quote = str(evidence["source_quote"])
            assert source_file == payload["source_file"]
            if source_file not in source_text_cache:
                source_text_cache[source_file] = (SOURCE_DIR / source_file).read_text(
                    encoding="utf-8"
                )
            assert source_quote in source_text_cache[source_file]


def test_affordance_ids_are_unique_namespaced_slugs() -> None:
    seen: set[str] = set()

    for record in _pilot_records():
        payload = _payload_for(record)
        model_id = str(payload["model_id"])
        for affordance in payload["affordances"]:
            assert isinstance(affordance, dict)
            affordance_id = str(affordance["affordance_id"])
            assert affordance_id not in seen
            assert affordance_id.startswith(f"{model_id}.")
            assert AFFORDANCE_ID_RE.match(affordance_id)
            seen.add(affordance_id)


def test_model_ids_match_active_knowledge_graph() -> None:
    graph = _load_json(KNOWLEDGE_GRAPH_PATH)
    graph_models = graph["models"]
    assert isinstance(graph_models, dict)

    for record in _pilot_records():
        assert record["model_id"] in graph_models


def test_source_manifest_hashes_match_actual_files() -> None:
    source_manifest = _load_json(SOURCE_MANIFEST_PATH)
    assert source_manifest["source_root"] == "data/model_sources"
    assert source_manifest["hash_algorithm"] == "sha256"

    files = source_manifest["files"]
    assert isinstance(files, list)
    model_ids = {str(entry["model_id"]) for entry in files}
    assert EXPECTED_MODEL_IDS.issubset(model_ids)

    for entry in files:
        assert isinstance(entry, dict)
        path = REPO_ROOT / str(entry["path"])
        data = path.read_bytes()
        assert path.exists()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert len(data) == entry["bytes"]


def test_source_and_pilot_manifests_are_consistent() -> None:
    source_manifest = _load_json(SOURCE_MANIFEST_PATH)
    source_by_model = {
        str(entry["model_id"]): entry for entry in source_manifest["files"]
    }

    for record in _pilot_records():
        source_entry = source_by_model[str(record["model_id"])]
        assert record["source_file"] == source_entry["filename"]
        assert record["source_path"] == source_entry["path"]
        assert record["source_sha256"] == source_entry["sha256"]


def test_pilot_keeps_absence_first_class_for_a_thin_one_affordance_record() -> None:
    one_or_zero_with_absence = []
    for record in _pilot_records():
        payload = _payload_for(record)
        if len(payload["affordances"]) <= 1 and payload["absence_records"]:
            one_or_zero_with_absence.append(payload["model_id"])

    assert one_or_zero_with_absence
