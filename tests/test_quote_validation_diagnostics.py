from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.quote_validation_diagnostics import (
    QUOTE_VALIDATION_DIAGNOSTIC_RECORD_SCHEMA_VERSION,
    QUOTE_VALIDATION_FINDINGS_SCHEMA_VERSION,
    build_quote_validation_diagnostic_record,
    build_quote_validation_findings,
    render_quote_validation_findings_json,
    render_quote_validation_findings_markdown,
)
from scripts.analyze_quote_validation_failures import main as cli_main


def _write_run(
    archive_root: Path,
    *,
    case_id: str = "case-a",
    run_id: str = "run-a",
    assistant_text: str = "Take this path because revenue is fragile.",
    fabricated_passages: list[object],
    retry_attempted: bool = True,
    retry_succeeded: bool = False,
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    conversation = (
        "CONVERSATION: 2 turns, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\n"
        "What should I do?\n\n"
        "[Turn 1] ASSISTANT:\n"
        f"{assistant_text}\n"
    )
    (run_dir / "conversation.txt").write_text(conversation, encoding="utf-8")
    (run_dir / "extraction.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "extraction": {
                    "decision_situation": "A decision.",
                    "live_constraints": [],
                    "synthesized_position": "Take the path.",
                    "reasoning_passages": [],
                    "original_framing": "What should the user do?",
                    "dropped_threads": [],
                    "_quote_validation": {
                        "total": len(fabricated_passages),
                        "verified": 0,
                        "fabricated": len(fabricated_passages),
                        "fabricated_passages": fabricated_passages,
                        "retry_attempted": retry_attempted,
                        "retry_succeeded": retry_succeeded,
                    },
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_dir


def _first_classification(run_dir: Path, archive_root: Path) -> str:
    record = build_quote_validation_diagnostic_record(run_dir, archive_root=archive_root)
    return record["passage_diagnostics"][0]["classification"]


def test_current_matcher_accepts_exact_passage(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        fabricated_passages=["Take this path because revenue is fragile."],
    )

    record = build_quote_validation_diagnostic_record(run_dir, archive_root=archive_root)

    assert record["schema_version"] == QUOTE_VALIDATION_DIAGNOSTIC_RECORD_SCHEMA_VERSION
    assert record["record_status"] == "valid"
    assert record["classification_counts"]["accepted_by_current_matcher"] == 1
    assert record["passage_diagnostics"][0]["current_matcher_accepts"] is True
    assert record["recommended_repair"] == "legacy_only"


def test_current_matcher_accepts_wrapper_and_casefold(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="Take this path because revenue is fragile.",
        fabricated_passages=['"take this path because revenue is fragile."'],
    )

    assert _first_classification(run_dir, archive_root) == "accepted_by_current_matcher"


def test_whitespace_normalized_diagnostic_match(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="Take this path because revenue is fragile.",
        fabricated_passages=["Take   this path because revenue is fragile."],
    )

    assert _first_classification(run_dir, archive_root) == "whitespace_normalized_match"


def test_linebreak_normalized_diagnostic_match(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="Take this path because revenue is fragile.",
        fabricated_passages=["Take\nthis path because revenue is fragile."],
    )

    assert _first_classification(run_dir, archive_root) == "linebreak_normalized_match"


def test_unicode_punctuation_diagnostic_match(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="It's risky - wait...",
        fabricated_passages=["It’s risky — wait…"],
    )

    assert _first_classification(run_dir, archive_root) == "unicode_punctuation_normalized_match"


def test_high_token_overlap_near_match(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="Take this path because revenue is very fragile.",
        fabricated_passages=["Take this path because revenue is fragile."],
    )

    record = build_quote_validation_diagnostic_record(run_dir, archive_root=archive_root)

    assert record["passage_diagnostics"][0]["classification"] == "high_token_overlap_near_match"
    assert record["passage_diagnostics"][0]["token_overlap"] >= 0.90


def test_true_paraphrase_or_no_match(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        assistant_text="Take this path because revenue is fragile.",
        fabricated_passages=["Choose the opposite plan after the market changes."],
    )

    assert _first_classification(run_dir, archive_root) == "true_paraphrase_or_no_match"


def test_empty_passage(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(archive_root, fabricated_passages=[""])

    record = build_quote_validation_diagnostic_record(run_dir, archive_root=archive_root)

    assert record["classification_counts"]["empty_or_invalid_passage"] == 1
    assert record["passage_diagnostics"][0]["passage_length"] == 0


def test_raw_fabricated_text_and_absolute_paths_do_not_appear(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _write_run(
        archive_root,
        case_id="case-secret",
        run_id="run-secret",
        fabricated_passages=["SECRET FABRICATED PASSAGE 123"],
    )

    record = build_quote_validation_diagnostic_record(
        run_dir,
        archive_root=Path("/Users/marcin/SECRET_HOME/.local/share/lolla/runs"),
    )
    findings = build_quote_validation_findings([record])
    rendered = render_quote_validation_findings_markdown(findings) + render_quote_validation_findings_json(findings)

    assert "SECRET FABRICATED PASSAGE 123" not in rendered
    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "sha256:" in rendered
    assert "case-secret/run-secret" in rendered


def test_findings_ordering_is_deterministic(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_b = _write_run(
        archive_root,
        case_id="z-case",
        run_id="run-b",
        fabricated_passages=["Different text b."],
    )
    run_a = _write_run(
        archive_root,
        case_id="a-case",
        run_id="run-a",
        fabricated_passages=["Different text a."],
    )
    records = [
        build_quote_validation_diagnostic_record(run_b, archive_root=archive_root),
        build_quote_validation_diagnostic_record(run_a, archive_root=archive_root),
    ]

    first = build_quote_validation_findings(records)
    second = build_quote_validation_findings(list(reversed(records)))

    assert [record["case_id"] for record in first["records"]] == ["a-case", "z-case"]
    assert render_quote_validation_findings_json(first) == render_quote_validation_findings_json(second)
    assert render_quote_validation_findings_markdown(first) == render_quote_validation_findings_markdown(second)


def test_single_invalid_record_does_not_override_accepted_current_matcher_majority() -> None:
    findings = build_quote_validation_findings(
        [
            {
                "case_id": "legacy-case",
                "run_id": "run-a",
                "archive_relpath": "legacy-case/run-a",
                "record_status": "valid",
                "fabricated_passage_count_seen": 2,
                "classification_counts": {"accepted_by_current_matcher": 2},
                "retry_attempted": True,
                "retry_succeeded": False,
            },
            {
                "case_id": "old-invalid-case",
                "run_id": "run-b",
                "archive_relpath": "old-invalid-case/run-b",
                "record_status": "invalid",
                "fabricated_passage_count_seen": 1,
                "classification_counts": {"true_paraphrase_or_no_match": 1},
                "retry_attempted": True,
                "retry_succeeded": False,
            },
        ]
    )

    recommendation = findings["recommended_next_slice"]
    assert recommendation["slice"] == "legacy_only_no_runtime_change"
    assert "1 of 2 record(s) were missing or malformed" in recommendation["reason"]


def test_cli_creates_markdown_and_json(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _write_run(
        archive_root,
        case_id="case-cli",
        run_id="run-cli",
        fabricated_passages=["Choose the opposite plan."],
    )
    findings_json = tmp_path / "extraction_findings.json"
    findings_json.write_text(
        json.dumps(
            {
                "quote_fabrication_patterns": {
                    "records": [
                        {
                            "case_id": "case-cli",
                            "run_id": "run-cli",
                            "archive_relpath": "/Users/marcin/SECRET_HOME/runs/case-cli/run-cli",
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    markdown_out = tmp_path / "quote_findings.md"
    json_out = tmp_path / "quote_findings.json"

    exit_code = cli_main(
        [
            str(archive_root),
            "--findings-json",
            str(findings_json),
            "--out",
            str(markdown_out),
            "--json-out",
            str(json_out),
        ]
    )

    rendered = markdown_out.read_text(encoding="utf-8") + json_out.read_text(encoding="utf-8")
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert markdown_out.exists()
    assert json_out.exists()
    assert payload["schema_version"] == QUOTE_VALIDATION_FINDINGS_SCHEMA_VERSION
    assert payload["record_count"] == 1
    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "case-cli/run-cli" in rendered


def test_malformed_archive_is_invalid_without_crashing(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = archive_root / "bad-case" / "bad-run"
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION: 0 turns\n\n[Turn 1] ASSISTANT:\nText.\n",
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text("{not-json", encoding="utf-8")

    record = build_quote_validation_diagnostic_record(run_dir, archive_root=archive_root)

    assert record["record_status"] == "invalid"
    assert record["error_categories"] == ["invalid_json_artifact"]
    assert record["recommended_repair"] == "needs_manual_review"
