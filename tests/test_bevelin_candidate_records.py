from __future__ import annotations

import hashlib
from pathlib import Path

from engine.system_b.model_affordance_validation import validate_model_affordance_file
from scripts.compile_model_affordances import compile_model_affordances


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
CANDIDATE_DIR = REPO_ROOT / "data" / "model_affordances" / "bevelin_candidate"
DEFAULT_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"
)
ALL_RECORD_DIRS = (
    REPO_ROOT / "data" / "model_affordances" / "pilot",
    REPO_ROOT / "data" / "model_affordances" / "batch_1",
    REPO_ROOT / "data" / "model_affordances" / "batch_2",
    REPO_ROOT / "data" / "model_affordances" / "batch_3a",
    REPO_ROOT / "data" / "model_affordances" / "batch_4",
    REPO_ROOT / "data" / "model_affordances" / "batch_5",
    REPO_ROOT / "data" / "model_affordances" / "batch_6",
    REPO_ROOT / "data" / "model_affordances" / "batch_7",
    REPO_ROOT / "data" / "model_affordances" / "batch_8",
    REPO_ROOT / "data" / "model_affordances" / "batch_9",
    REPO_ROOT / "data" / "model_affordances" / "batch_10",
    REPO_ROOT / "data" / "model_affordances" / "batch_11",
    REPO_ROOT / "data" / "model_affordances" / "batch_12",
    REPO_ROOT / "data" / "model_affordances" / "batch_13",
    REPO_ROOT / "data" / "model_affordances" / "batch_14",
    REPO_ROOT / "data" / "model_affordances" / "batch_15",
    REPO_ROOT / "data" / "model_affordances" / "batch_16",
    REPO_ROOT / "data" / "model_affordances" / "batch_17",
)

APPROVED_CANDIDATE_RECORDS = {
    "baseline-establishment.json",
    "obligations-controls-mapping.json",
}


def test_bevelin_candidate_records_are_scoped_and_source_backed() -> None:
    record_paths = sorted(CANDIDATE_DIR.glob("*.json"))

    assert {path.name for path in record_paths} == APPROVED_CANDIDATE_RECORDS
    for path in record_paths:
        validate_model_affordance_file(path, source_roots=(SOURCE_DIR,))


def test_bevelin_candidate_compiles_without_touching_default_artifact(
    tmp_path: Path,
) -> None:
    before_hash = hashlib.sha256(DEFAULT_AFFORDANCES_PATH.read_bytes()).hexdigest()

    result = compile_model_affordances(
        root=REPO_ROOT,
        record_dirs=ALL_RECORD_DIRS,
        overlay_record_dirs=(CANDIDATE_DIR,),
        output_dir=tmp_path / "bevelin_candidate",
        compiled_filename="affordances_v60.json",
        quality_report_filename="quality_report_v60.md",
        artifact_id="model_affordances_v60",
        report_title="Model Affordance Quality Report v60 Bevelin Candidate",
    )

    after_hash = hashlib.sha256(DEFAULT_AFFORDANCES_PATH.read_bytes()).hexdigest()
    metadata = result.compiled["compile_metadata"]

    assert before_hash == after_hash
    assert result.compiled_path.name == "affordances_v60.json"
    assert result.compiled_path.parent.name == "bevelin_candidate"
    assert result.compiled["artifact"] == "model_affordances_v60"
    assert metadata["contributing_record_count"] == 222
    assert metadata["affordance_count"] == 308
    assert metadata["absence_record_count"] == 697
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0
    source_filenames = [entry["filename"] for entry in metadata["source_files"]]
    assert source_filenames.count("Seeking_Wisdom_Bevelin_rag.md") == 1
    assert "bevelin_candidate/baseline-establishment.json" in metadata["record_paths"][
        "baseline-establishment"
    ]
    assert "bevelin_candidate/obligations-controls-mapping.json" in metadata[
        "record_paths"
    ]["obligations-controls-mapping"]
