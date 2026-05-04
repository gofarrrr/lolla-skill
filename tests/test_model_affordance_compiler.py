from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.compile_model_affordances import (  # noqa: E402
    COMPILED_FILENAME,
    DO_NOT_PROMOTE_FLAGS,
    QUALITY_REPORT_FILENAME,
    ModelAffordanceCompilationError,
    compile_model_affordances,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_RECORD_DIR = REPO_ROOT / "data" / "model_affordances" / "pilot"
PILOT_MANIFEST_PATH = REPO_ROOT / "data" / "model_affordances" / "pilot_manifest.json"
SOURCE_DIR = REPO_ROOT / "data" / "model_sources"
SOURCE_MANIFEST_PATH = REPO_ROOT / "data" / "model_sources" / "manifest.json"
PILOT_MODEL_IDS = {
    "base-rates",
    "confidence-calibration",
    "inversion",
    "optionality",
    "power-dynamics",
    "premortem",
    "problem-framing-and-reframing",
    "second-order-thinking",
    "systems-thinking",
    "theory-of-constraints",
}


def _copy_compiler_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    record_dir = tmp_path / "records"
    source_dir = tmp_path / "sources"
    shutil.copytree(PILOT_RECORD_DIR, record_dir)
    shutil.copytree(SOURCE_DIR, source_dir)

    pilot_manifest_path = tmp_path / "pilot_manifest.json"
    source_manifest_path = tmp_path / "source_manifest.json"
    shutil.copy2(PILOT_MANIFEST_PATH, pilot_manifest_path)
    shutil.copy2(SOURCE_MANIFEST_PATH, source_manifest_path)
    return record_dir, pilot_manifest_path, source_dir, source_manifest_path


def test_compiler_runs_deterministically(tmp_path: Path) -> None:
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"

    first = compile_model_affordances(root=REPO_ROOT, output_dir=first_output)
    second = compile_model_affordances(root=REPO_ROOT, output_dir=second_output)

    assert (first_output / COMPILED_FILENAME).read_bytes() == (
        second_output / COMPILED_FILENAME
    ).read_bytes()
    assert (first_output / QUALITY_REPORT_FILENAME).read_bytes() == (
        second_output / QUALITY_REPORT_FILENAME
    ).read_bytes()
    assert first.compiled == second.compiled
    assert first.quality_report == second.quality_report


def test_compiler_rejects_non_exact_source_quote(tmp_path: Path) -> None:
    record_dir, pilot_manifest_path, source_dir, source_manifest_path = _copy_compiler_inputs(
        tmp_path
    )
    record_path = record_dir / "theory-of-constraints.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["affordances"][0]["source_evidence"][0][
        "source_quote"
    ] = "This quote is intentionally not present in the canonical source file."
    record_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ModelAffordanceCompilationError,
        match="source_quote_rejection_count=1",
    ):
        compile_model_affordances(
            root=REPO_ROOT,
            record_dir=record_dir,
            pilot_manifest_path=pilot_manifest_path,
            source_dir=source_dir,
            source_manifest_path=source_manifest_path,
            output_dir=tmp_path / "compiled",
        )


def test_compiler_rejects_source_hash_mismatch(tmp_path: Path) -> None:
    record_dir, pilot_manifest_path, source_dir, source_manifest_path = _copy_compiler_inputs(
        tmp_path
    )
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    source_manifest["files"][0]["sha256"] = "0" * 64
    source_manifest_path.write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ModelAffordanceCompilationError, match="sha256 mismatch"):
        compile_model_affordances(
            root=REPO_ROOT,
            record_dir=record_dir,
            pilot_manifest_path=pilot_manifest_path,
            source_dir=source_dir,
            source_manifest_path=source_manifest_path,
            output_dir=tmp_path / "compiled",
        )


def test_quality_report_contains_required_sections(tmp_path: Path) -> None:
    result = compile_model_affordances(
        root=REPO_ROOT,
        output_dir=tmp_path / "compiled",
    )

    for heading in (
        "## Honesty Signals",
        "## Do Not Runtime Promote Without Rewrite Review",
        "## Per-Model Summary",
        "## Cross-Model Deterministic Observations",
        "## What This Report Deliberately Omits",
    ):
        assert heading in result.quality_report


def test_compiled_artifact_includes_only_contributing_source_files(
    tmp_path: Path,
) -> None:
    result = compile_model_affordances(
        root=REPO_ROOT,
        output_dir=tmp_path / "compiled",
    )
    source_files = result.compiled["compile_metadata"]["source_files"]
    assert {entry["model_id"] for entry in source_files} == PILOT_MODEL_IDS


def test_quality_report_avoids_scorecard_language(tmp_path: Path) -> None:
    result = compile_model_affordances(
        root=REPO_ROOT,
        output_dir=tmp_path / "compiled",
    )
    report = result.quality_report.lower()

    assert "completeness percentage" not in report
    assert "coverage score" not in report


def test_quality_report_surfaces_do_not_promote_flags(tmp_path: Path) -> None:
    result = compile_model_affordances(
        root=REPO_ROOT,
        output_dir=tmp_path / "compiled",
    )

    for flag in DO_NOT_PROMOTE_FLAGS:
        assert flag["affordance_id"] in result.quality_report
