from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.assemble_extraction_packet import assemble_extraction_packet  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = SOURCE_DIR / "manifest.json"
PACKET_SCRIPT_PATH = REPO_ROOT / "scripts" / "assemble_extraction_packet.py"

APPROVED_BATCH_MODEL_IDS = {
    "anchoring",
    "expected-value",
    "decomposition",
    "decision-trees",
    "sunk-cost-fallacy",
    "complex-adaptive-systems",
    "emergence",
    "leverage-points",
    "network-effects",
    "multi-criteria-decision-analysis",
    "circle-of-control",
    "lindy-effect",
    "johari-window",
    "occams-razor",
    "flow",
    "calculated-risk-taking",
    "risk-assessment",
    "incentives",
    "trade-offs",
    "information-asymmetry",
}


def _source_manifest() -> dict[str, object]:
    return json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))


def test_pr7_batch_sources_are_manifested_and_hashed() -> None:
    manifest = _source_manifest()
    entries = {
        str(entry["model_id"]): entry
        for entry in manifest["files"]
        if str(entry["model_id"]) in APPROVED_BATCH_MODEL_IDS
    }

    assert set(entries) == APPROVED_BATCH_MODEL_IDS
    for entry in entries.values():
        path = REPO_ROOT / str(entry["path"])
        data = path.read_bytes()
        assert path.exists()
        assert path.parent == SOURCE_DIR
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert len(data) == entry["bytes"]


def test_packet_helper_assembles_source_backed_packet(tmp_path: Path) -> None:
    packet = assemble_extraction_packet(
        "circle-of-control",
        output_dir=tmp_path,
        copy_source=False,
    )
    packet_path = tmp_path / "circle-of-control.json"

    assert packet_path.exists()
    assert packet["packet_schema_version"] == "model_affordance_extraction_packet.v1"
    assert packet["model_id"] == "circle-of-control"
    assert packet["source"]["source_file"] == "Circle_Of_Control_rag.md"
    assert packet["source"]["markdown"] == (
        SOURCE_DIR / "Circle_Of_Control_rag.md"
    ).read_text(encoding="utf-8")
    assert packet["curation"]["activation"]["present"] is True
    assert packet["curation"]["intervention_semantics"]["present"] is True
    assert packet["curation"]["relation_semantics"]["present"] is True
    assert packet["expected_output"] == {
        "record_path": "data/model_affordances/batch_1/circle-of-control.json",
        "review_required_before_commit": True,
        "validator": (
            "engine.system_b.model_affordance_validation."
            "validate_model_affordance_file"
        ),
        "validator_source_roots": ["data/model_sources"],
    }


def test_packet_helper_can_target_batch2_record_dir(tmp_path: Path) -> None:
    packet = assemble_extraction_packet(
        "black-swan-events",
        output_dir=tmp_path,
        record_dir=Path("data/model_affordances/batch_2"),
        copy_source=False,
    )

    assert packet["model_id"] == "black-swan-events"
    assert packet["expected_output"]["record_path"] == (
        "data/model_affordances/batch_2/black-swan-events.json"
    )


def test_packet_helper_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = assemble_extraction_packet(
        "trade-offs",
        output_dir=first_dir,
        copy_source=False,
    )
    second = assemble_extraction_packet(
        "trade-offs",
        output_dir=second_dir,
        copy_source=False,
    )

    assert first == second
    assert (first_dir / "trade-offs.json").read_bytes() == (
        second_dir / "trade-offs.json"
    ).read_bytes()


def test_packet_helper_does_not_encode_case_category_rules() -> None:
    script = PACKET_SCRIPT_PATH.read_text(encoding="utf-8")
    string_literals = re.findall(r"(['\"])(.*?)\1", script, flags=re.DOTALL)
    literal_text = "\n".join(match[1].lower() for match in string_literals)

    for forbidden in (
        "family",
        "negotiation",
        "equity",
        "startup",
        "phd",
        "whistleblower",
        "consulting",
        "consultant",
    ):
        assert forbidden not in literal_text
