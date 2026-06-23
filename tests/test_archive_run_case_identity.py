from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_PATH = REPO_ROOT / "scripts" / "archive_run.py"


def _load_archive_run_module():
    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_run(
    *,
    tmp_dir: Path,
    run_id: str,
    decision_situation: str,
    conversation: str,
) -> None:
    (tmp_dir / f"lolla_{run_id}_conversation.txt").write_text(
        conversation,
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps({"extraction": {"decision_situation": decision_situation}}),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )


def test_archive_run_matches_identical_conversation_before_extractor_fingerprint(
    tmp_path: Path,
) -> None:
    archive_run = _load_archive_run_module()
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()
    conversation = (
        "CONVERSATION: 7 turns, 7 user messages, 7 assistant responses\n\n"
        "[Turn 1] USER:\n"
        "Solo founder, B2B SaaS for dental offices. I have 22 customers, "
        "$4K MRR, flat growth, and 14 months of runway.\n"
    )
    first_decision = (
        "Whether to pivot a B2B SaaS product to a new workflow tool based on "
        "unverified customer interest, given 14 months of runway and a flat growth curve."
    )
    second_decision = (
        "Whether to pivot a B2B SaaS product to a new workflow tool or continue "
        "pushing the current product given flat growth and 14 months of runway."
    )
    first_fingerprint = archive_run._normalize_fingerprint(first_decision)
    second_fingerprint = archive_run._normalize_fingerprint(second_decision)
    assert (
        archive_run._token_jaccard(first_fingerprint, second_fingerprint)
        < archive_run.FINGERPRINT_MATCH_THRESHOLD
    )

    _seed_run(
        tmp_dir=tmp_dir,
        run_id="runone_aaaaaa",
        decision_situation=first_decision,
        conversation=conversation,
    )
    first = archive_run.archive_run(
        "runone_aaaaaa",
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )
    assert first["how_matched"] == "new_case"

    # Simulate a manifest created before conversation_hashes existed. The
    # matcher should still compute the archived conversation hash from
    # runone_aaaaaa/conversation.txt and avoid creating a case-name suffix.
    manifest_path = Path(first["case_dir"]) / ".case-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("conversation_hashes", None)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    _seed_run(
        tmp_dir=tmp_dir,
        run_id="runtwo_bbbbbb",
        decision_situation=second_decision,
        conversation=conversation,
    )
    second = archive_run.archive_run(
        "runtwo_bbbbbb",
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    assert second["how_matched"] == "conversation_match"
    assert second["case_dir"] == first["case_dir"]
    assert second["case_id"] == first["case_id"]
    assert not (archive_root / f"{first['case_id']}-1").exists()

    updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert updated_manifest["run_count"] == 2
    assert updated_manifest["runs"] == ["runone_aaaaaa", "runtwo_bbbbbb"]
    assert first_fingerprint in updated_manifest["fingerprints"]
    assert second_fingerprint in updated_manifest["fingerprints"]
    assert updated_manifest["conversation_hashes"] == [first["conversation_hash"]]
