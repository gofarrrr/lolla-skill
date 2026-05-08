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
BATCH_RECORD_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_1"
BATCH_2_RECORD_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_2"
BATCH_3A_RECORD_DIR = REPO_ROOT / "data" / "model_affordances" / "batch_3a"
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
BATCH_MODEL_IDS = {
    "anchoring",
    "calculated-risk-taking",
    "circle-of-control",
    "complex-adaptive-systems",
    "decision-trees",
    "decomposition",
    "emergence",
    "expected-value",
    "flow",
    "incentives",
    "information-asymmetry",
    "johari-window",
    "leverage-points",
    "lindy-effect",
    "multi-criteria-decision-analysis",
    "network-effects",
    "occams-razor",
    "risk-assessment",
    "sunk-cost-fallacy",
    "trade-offs",
}
BATCH_2_MODEL_IDS = {
    "adverse-selection",
    "aleatory-epistemic-uncertainty-recognition",
    "antifragility",
    "black-swan-events",
    "comparative-advantage",
    "correlation-vs-causation",
    "empathy",
    "experimentation",
    "law-of-large-numbers",
    "margin-of-safety",
    "moral-hazard",
    "optimization-theory",
    "pareto-principle",
    "prioritization",
    "psychological-safety",
    "resilience",
    "six-thinking-hats",
    "social-proof",
    "statistical-discipline",
    "survivorship-bias",
}
BATCH_3A_MODEL_IDS = {
    "falsifiability",
    "opportunity-cost",
    "principal-agent-problem",
    "probabilistic-thinking",
    "true-uncertainty-navigation",
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


def test_compiler_can_compile_pilot_and_batch_records_to_v2(
    tmp_path: Path,
) -> None:
    result = compile_model_affordances(
        root=REPO_ROOT,
        record_dirs=(PILOT_RECORD_DIR, BATCH_RECORD_DIR),
        output_dir=tmp_path / "compiled",
        compiled_filename="affordances_v2.json",
        quality_report_filename="quality_report_v2.md",
        artifact_id="model_affordances_v2",
        report_title="Model Affordance Quality Report v2",
    )

    metadata = result.compiled["compile_metadata"]
    source_files = metadata["source_files"]
    expected_model_ids = PILOT_MODEL_IDS | BATCH_MODEL_IDS

    assert result.compiled_path.name == "affordances_v2.json"
    assert result.quality_report_path.name == "quality_report_v2.md"
    assert result.compiled["artifact"] == "model_affordances_v2"
    assert result.quality_report.startswith("# Model Affordance Quality Report v2\n")
    assert metadata["contributing_record_count"] == 30
    assert metadata["affordance_count"] == 59
    assert metadata["absence_record_count"] == 73
    assert {entry["model_id"] for entry in source_files} == expected_model_ids
    assert "### Repeated Diagnostic Question Openings" in result.quality_report
    assert "`what would you have to`" in result.quality_report


def test_compiler_can_compile_pilot_batch1_batch2_records_to_v3(
    tmp_path: Path,
) -> None:
    extra_sections = "## Gate 3 Status\n\nGate 3: cleared.\n"
    result = compile_model_affordances(
        root=REPO_ROOT,
        record_dirs=(PILOT_RECORD_DIR, BATCH_RECORD_DIR, BATCH_2_RECORD_DIR),
        output_dir=tmp_path / "compiled",
        compiled_filename="affordances_v3.json",
        quality_report_filename="quality_report_v3.md",
        artifact_id="model_affordances_v3",
        report_title="Model Affordance Quality Report v3",
        extra_sections=extra_sections,
    )

    metadata = result.compiled["compile_metadata"]
    source_files = metadata["source_files"]
    expected_model_ids = PILOT_MODEL_IDS | BATCH_MODEL_IDS | BATCH_2_MODEL_IDS

    assert result.compiled_path.name == "affordances_v3.json"
    assert result.quality_report_path.name == "quality_report_v3.md"
    assert result.compiled["artifact"] == "model_affordances_v3"
    assert result.quality_report.startswith("# Model Affordance Quality Report v3\n")
    assert metadata["contributing_record_count"] == 50
    assert metadata["affordance_count"] == 93
    assert metadata["absence_record_count"] == 130
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0
    assert {entry["model_id"] for entry in source_files} == expected_model_ids
    assert "## Gate 3 Status" in result.quality_report
    assert "Gate 3: cleared." in result.quality_report


def test_compiler_can_compile_pilot_batch1_batch2_batch3a_records_to_v4(
    tmp_path: Path,
) -> None:
    extra_sections = "## Batch 3a Status\n\nBatch 3a: targeted coverage patch.\n"
    result = compile_model_affordances(
        root=REPO_ROOT,
        record_dirs=(
            PILOT_RECORD_DIR,
            BATCH_RECORD_DIR,
            BATCH_2_RECORD_DIR,
            BATCH_3A_RECORD_DIR,
        ),
        output_dir=tmp_path / "compiled",
        compiled_filename="affordances_v4.json",
        quality_report_filename="quality_report_v4.md",
        artifact_id="model_affordances_v4",
        report_title="Model Affordance Quality Report v4",
        extra_sections=extra_sections,
    )

    metadata = result.compiled["compile_metadata"]
    source_files = metadata["source_files"]
    expected_model_ids = (
        PILOT_MODEL_IDS | BATCH_MODEL_IDS | BATCH_2_MODEL_IDS | BATCH_3A_MODEL_IDS
    )

    assert result.compiled_path.name == "affordances_v4.json"
    assert result.quality_report_path.name == "quality_report_v4.md"
    assert result.compiled["artifact"] == "model_affordances_v4"
    assert result.quality_report.startswith("# Model Affordance Quality Report v4\n")
    assert metadata["contributing_record_count"] == 55
    assert metadata["affordance_count"] == 98
    assert metadata["absence_record_count"] == 144
    assert metadata["validation"]["schema_validation_failure_count"] == 0
    assert metadata["validation"]["source_quote_rejection_count"] == 0
    assert {entry["model_id"] for entry in source_files} == expected_model_ids
    assert "## Batch 3a Status" in result.quality_report
    assert "Batch 3a: targeted coverage patch." in result.quality_report


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
