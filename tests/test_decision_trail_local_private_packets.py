from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_trail_specialist_packets import (
    DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION,
    SPECIALIST_ROLES,
    DecisionTrailSpecialistPacketInputError,
    build_decision_trail_specialist_packets,
    load_json_object,
    render_decision_trail_specialist_packets_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
)
CONTRACT_SCHEMA = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md"
)


def _write_synthetic_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / "sample-local-private-run"
    run_dir.mkdir()
    (run_dir / "conversation.txt").write_text(
        "Synthetic conversation: choose staged rollout or immediate launch.\n"
        "The user worries about buyer proof, team load, and reversibility.\n",
        encoding="utf-8",
    )
    (run_dir / "revised.txt").write_text(
        "Synthetic revised answer: prefer staged rollout with a stop rule.\n",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text(
        "# Synthetic memo\n\nPressure added a gate and preserved uncertainty.\n",
        encoding="utf-8",
    )
    (run_dir / "operator.log").write_text(
        "synthetic operator event: local-private packet smoke\n",
        encoding="utf-8",
    )
    (run_dir / "evaluation.json").write_text(
        json.dumps({"schema_version": "synthetic.evaluation.v0"}),
        encoding="utf-8",
    )
    (run_dir / "agent_result.json").write_text(
        json.dumps({"schema_version": "synthetic.agent_result.v0"}),
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text(
        json.dumps(
            {
                "schema_version": "synthetic.extraction.v0",
                "extraction": {
                    "decision_situation": "Choose rollout path",
                    "live_constraints": ["team load", "buyer proof"],
                },
            }
        ),
        encoding="utf-8",
    )
    return run_dir


def _write_conversation_only_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / "conversation-only-local-private-run"
    run_dir.mkdir()
    (run_dir / "conversation.txt").write_text(
        "Synthetic conversation only.\n",
        encoding="utf-8",
    )
    return run_dir


def _build_local_packets(
    *,
    run_dir: Path,
    out: Path,
    content_inclusion_mode: str = "metadata_only",
    max_text_chars: int = 12000,
) -> dict[str, Any]:
    return build_decision_trail_specialist_packets(
        fixture_review=load_json_object(FIXTURE_REVIEW),
        contract_schema=load_json_object(CONTRACT_SCHEMA),
        fixture_review_relpath=(
            "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
        ),
        contract_schema_relpath=(
            "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
        ),
        mode="local_private_mode",
        local_run_dirs=[run_dir],
        content_inclusion_mode=content_inclusion_mode,
        output_path=out,
        repo_root=REPO_ROOT,
        max_text_chars=max_text_chars,
    )


def test_local_private_metadata_only_records_manifest_without_text(tmp_path: Path) -> None:
    run_dir = _write_synthetic_run(tmp_path)
    packets = _build_local_packets(run_dir=run_dir, out=tmp_path / "packets.json")

    assert packets["schema_version"] == DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert packets["mode"] == "local_private_mode"
    assert packets["boundary"]["raw_private_content_included"] is False
    assert packets["packet_policy"]["commit_safety"] == "unsafe_for_commit_by_default"
    assert packets["packet_policy"]["content_inclusion_mode"] == "metadata_only"
    assert packets["packet_policy"]["specialist_reads_filled"] is False
    assert packets["packet_policy"]["fan_in_executed"] is False
    assert packets["report_count"] == 1

    report = packets["reports"][0]
    assert set(report["packets"]) == set(SPECIALIST_ROLES)
    context = report["available_context"]
    assert context["private_context_policy"]["mode"] == "local_private_mode"
    assert context["private_context_policy"]["local_absolute_paths_included"] is False
    assert context["local_private_artifacts_read"]

    rendered = render_decision_trail_specialist_packets_json(packets)
    assert "Synthetic conversation" not in rendered
    assert str(run_dir) not in rendered
    assert "/User" + "s/" not in rendered


def test_local_private_include_text_marks_output_unsafe_and_includes_text(
    tmp_path: Path,
) -> None:
    run_dir = _write_synthetic_run(tmp_path)
    packets = _build_local_packets(
        run_dir=run_dir,
        out=tmp_path / "packets.json",
        content_inclusion_mode="include_text",
        max_text_chars=60,
    )

    assert packets["boundary"]["raw_private_content_included"] is True
    assert packets["packet_policy"]["raw_transcripts_included"] is True
    assert packets["packet_policy"]["raw_revised_answers_included"] is True
    assert packets["packet_policy"]["raw_memos_included"] is True
    assert packets["packet_policy"]["requires_operator_review_before_share"] is True

    artifacts = packets["reports"][0]["available_context"][
        "local_private_artifacts_read"
    ]
    conversation = next(
        artifact for artifact in artifacts if artifact["artifact"] == "conversation.txt"
    )
    assert conversation["raw_content_read"] is True
    assert conversation["content_included"] is True
    assert conversation["text_truncated"] is True
    assert "Synthetic conversation" in conversation["content_text"]

    rendered = render_decision_trail_specialist_packets_json(packets)
    assert "Synthetic conversation" in rendered
    assert str(run_dir) not in rendered


def test_local_private_include_text_derives_raw_family_booleans_from_artifacts(
    tmp_path: Path,
) -> None:
    run_dir = _write_conversation_only_run(tmp_path)
    packets = _build_local_packets(
        run_dir=run_dir,
        out=tmp_path / "packets.json",
        content_inclusion_mode="include_text",
    )

    assert packets["boundary"]["raw_private_content_included"] is True
    assert packets["packet_policy"]["raw_transcripts_included"] is True
    assert packets["packet_policy"]["raw_revised_answers_included"] is False
    assert packets["packet_policy"]["raw_memos_included"] is False


def test_local_private_fixture_ref_is_lineage_only_not_explicit_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_synthetic_run(tmp_path)
    packets = build_decision_trail_specialist_packets(
        fixture_review={"not": "a-pr88-review"},
        contract_schema=load_json_object(CONTRACT_SCHEMA),
        fixture_review_relpath="bad-pr88-review.json",
        contract_schema_relpath=(
            "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
        ),
        mode="local_private_mode",
        local_run_dirs=[run_dir],
        output_path=tmp_path / "packets.json",
        repo_root=REPO_ROOT,
    )

    fixture_ref = packets["reports"][0]["source_refs"][0]
    assert fixture_ref["artifact_ref"] == "bad-pr88-review.json"
    assert fixture_ref["source_status"] == "not_supplied"
    assert "lineage only" in fixture_ref["content_policy"]


def test_local_private_rejects_output_inside_run_dir(tmp_path: Path) -> None:
    run_dir = _write_synthetic_run(tmp_path)

    with pytest.raises(
        DecisionTrailSpecialistPacketInputError,
        match="outside local run directory",
    ):
        _build_local_packets(run_dir=run_dir, out=run_dir / "packets.json")


def test_local_private_rejects_output_inside_repo(tmp_path: Path) -> None:
    run_dir = _write_synthetic_run(tmp_path)

    with pytest.raises(
        DecisionTrailSpecialistPacketInputError,
        match="outside repository",
    ):
        _build_local_packets(
            run_dir=run_dir,
            out=REPO_ROOT / "decision-trail-local-private-packets.json",
        )


def test_local_private_cli_requires_explicit_output(tmp_path: Path) -> None:
    run_dir = _write_synthetic_run(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_trail_specialist_packets.py",
            "--fixture-review",
            str(FIXTURE_REVIEW),
            "--contract-schema",
            str(CONTRACT_SCHEMA),
            "--mode",
            "local_private_mode",
            "--local-run-dir",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "requires an explicit output path" in result.stderr


def test_local_private_cli_rejects_external_fixture_review_path(
    tmp_path: Path,
) -> None:
    run_dir = _write_synthetic_run(tmp_path)
    external_review = tmp_path / "external-review.json"
    external_review.write_text("{}", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_trail_specialist_packets.py",
            "--fixture-review",
            str(external_review),
            "--contract-schema",
            str(CONTRACT_SCHEMA),
            "--mode",
            "local_private_mode",
            "--local-run-dir",
            str(run_dir),
            "--out",
            str(tmp_path / "packets.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "requires fixture review inside repository" in result.stderr


def test_local_private_cli_writes_temp_output_with_include_text(tmp_path: Path) -> None:
    run_dir = _write_synthetic_run(tmp_path)
    out = tmp_path / "local-private-packets.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_trail_specialist_packets.py",
            "--fixture-review",
            str(FIXTURE_REVIEW),
            "--contract-schema",
            str(CONTRACT_SCHEMA),
            "--mode",
            "local_private_mode",
            "--local-run-dir",
            str(run_dir),
            "--content-inclusion",
            "include_text",
            "--max-text-chars",
            "80",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["mode"] == "local_private_mode"
    assert payload["boundary"]["raw_private_content_included"] is True
    assert payload["reports"][0]["source_run_ref"].endswith("-1")
    rendered = json.dumps(payload, sort_keys=True)
    assert "Synthetic conversation" in rendered
    assert str(run_dir) not in rendered


def test_pr78_lint_passes_checked_in_pr95_doc_and_safe_fixture() -> None:
    packet_fixture = (
        REPO_ROOT
        / "reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json"
    )
    report = lint_product_delta_paths([DOC_PATH, packet_fixture])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
