from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from engine.system_b.product_delta_graph_review_envelope_v2 import (
    FROZEN_INPUT_LOCKS,
    FUTURE_CONSOLIDATION_RELPATH,
    FUTURE_INTERPRETATION_RELPATHS,
    FUTURE_POST_REVEAL_PACKET_RELPATHS,
    FUTURE_REVIEW_FAILURE_RELPATHS,
    FUTURE_REVIEW_RELPATHS,
    INTERPRETATION_IDS,
    INVALID_FIXTURE_RELPATH,
    LANES,
    POST_REVEAL_FIXTURE_RELPATHS,
    REVIEW_IDS,
    VALID_FIXTURE_RELPATH,
    build_artifacts,
    render_json,
)
from engine.system_b.product_delta_graph_review_envelope_v2_result import (
    BLIND_TERMINAL_RECEIPT_RELPATHS,
    POST_TERMINAL_RECEIPT_RELPATHS,
    ProductDeltaGraphReviewEnvelopeV2ResultError,
    build_consolidation,
    build_post_reveal_packets,
    import_blind_review,
    import_post_reveal_interpretation,
    validate_complete_result,
    validate_post_reveal_packets,
    validate_preflight,
    write_consolidation,
    write_post_reveal_packets,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_VERSION = "codex-cli 0.144.5"


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _prepared_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relpath in FROZEN_INPUT_LOCKS:
        _copy_file(REPO_ROOT / relpath, root / relpath)
    for relpath in build_artifacts(repo_root=REPO_ROOT):
        _copy_file(REPO_ROOT / relpath, root / relpath)
    return root


def _external_json(
    tmp_path: Path, name: str, payload: dict[str, object]
) -> Path:
    path = tmp_path / name
    path.write_text(render_json(payload), encoding="utf-8")
    return path


def _valid_blind_payload(lane: str) -> dict[str, object]:
    payload = json.loads(
        (REPO_ROOT / VALID_FIXTURE_RELPATH).read_text(encoding="utf-8")
    )
    payload["review_id"] = REVIEW_IDS[lane]
    return payload


def _valid_post_payload(
    *,
    root: Path,
    lane: str,
) -> dict[str, object]:
    payload = json.loads(
        (
            REPO_ROOT / POST_REVEAL_FIXTURE_RELPATHS[lane]
        ).read_text(encoding="utf-8")
    )
    packet = json.loads(
        (
            root / FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
        ).read_text(encoding="utf-8")
    )
    reveal = {row["case_id"]: row for row in packet["comparison_reveal"]}
    for row in payload["pair_assessments"]:
        frozen = reveal[row["case_id"]]
        row["sealed_pair_role"] = frozen["sealed_pair_role"]
        row["frozen_material_decision_difference"] = frozen[
            "frozen_material_decision_difference"
        ]
        row["cited_frozen_move_ids"] = []
    payload["interpretation_id"] = INTERPRETATION_IDS[lane]
    payload["source_review_id"] = REVIEW_IDS[lane]
    return payload


def _import_valid_blind_pair(root: Path, tmp_path: Path) -> None:
    for lane in LANES:
        source = _external_json(
            tmp_path,
            f"blind-{lane}.json",
            _valid_blind_payload(lane),
        )
        assert (
            import_blind_review(
                repo_root=root,
                lane=lane,
                source_path=source,
                process_exit_code=0,
                codex_cli_version=CODEX_VERSION,
            )
            == "complete"
        )


def test_preflight_validates_frozen_inputs_without_semantic_output() -> None:
    assert validate_preflight(repo_root=REPO_ROOT) == []


def test_valid_blind_pair_opens_post_reveal_gate(tmp_path: Path) -> None:
    root = _prepared_root(tmp_path)
    _import_valid_blind_pair(root, tmp_path)

    packets = build_post_reveal_packets(repo_root=root)
    assert set(packets) == set(LANES)
    for lane in LANES:
        assert packets[lane]["frozen_review"]["review_id"] == REVIEW_IDS[lane]
        assert (
            packets[lane]["mechanical_availability"]["gate_passes"] is True
        )
        assert "sibling" not in packets[lane]["input_refs"]
        receipt = json.loads(
            (
                root / BLIND_TERMINAL_RECEIPT_RELPATHS[lane]
            ).read_text(encoding="utf-8")
        )
        assert receipt["terminal_state"] == "complete"
        assert receipt["process_exit_code"] == 0

    with pytest.raises(
        ProductDeltaGraphReviewEnvelopeV2ResultError,
        match="already frozen",
    ):
        import_blind_review(
            repo_root=root,
            lane="primary",
            source_path=tmp_path / "blind-primary.json",
            process_exit_code=0,
            codex_cli_version=CODEX_VERSION,
        )


def test_invalid_blind_first_terminal_closes_gate_without_salvage(
    tmp_path: Path,
) -> None:
    root = _prepared_root(tmp_path)
    primary = _external_json(
        tmp_path, "primary.json", _valid_blind_payload("primary")
    )
    invalid = copy.deepcopy(
        json.loads(
            (REPO_ROOT / INVALID_FIXTURE_RELPATH).read_text(
                encoding="utf-8"
            )
        )
    )
    skeptical = _external_json(tmp_path, "skeptical.json", invalid)
    assert (
        import_blind_review(
            repo_root=root,
            lane="primary",
            source_path=primary,
            process_exit_code=0,
            codex_cli_version=CODEX_VERSION,
        )
        == "complete"
    )
    assert (
        import_blind_review(
            repo_root=root,
            lane="skeptical",
            source_path=skeptical,
            process_exit_code=0,
            codex_cli_version=CODEX_VERSION,
        )
        == "failed"
    )
    assert (root / FUTURE_REVIEW_RELPATHS["skeptical"]).read_bytes() == (
        skeptical.read_bytes()
    )
    failure = json.loads(
        (
            root / FUTURE_REVIEW_FAILURE_RELPATHS["skeptical"]
        ).read_text(encoding="utf-8")
    )
    assert failure["validation_error_count"] == 58
    assert (
        failure[
            "retry_fallback_healing_replacement_reformatting_or_salvage"
        ]
        is False
    )
    with pytest.raises(
        ProductDeltaGraphReviewEnvelopeV2ResultError,
        match="blind review failed",
    ):
        build_post_reveal_packets(repo_root=root)

    consolidation = build_consolidation(repo_root=root)
    assert consolidation["interpretation"]["state"] == "not_evaluable"
    assert consolidation["boundary"][
        "conditional_post_reveal_contexts_attempted"
    ] == 0


def test_valid_post_reveal_pair_and_non_scalar_consolidation(
    tmp_path: Path,
) -> None:
    root = _prepared_root(tmp_path)
    _import_valid_blind_pair(root, tmp_path)
    write_post_reveal_packets(repo_root=root)
    assert validate_post_reveal_packets(repo_root=root) == []

    for lane in LANES:
        source = _external_json(
            tmp_path,
            f"post-{lane}.json",
            _valid_post_payload(root=root, lane=lane),
        )
        assert (
            import_post_reveal_interpretation(
                repo_root=root,
                lane=lane,
                source_path=source,
                process_exit_code=0,
                codex_cli_version=CODEX_VERSION,
            )
            == "complete"
        )
        assert (
            root / FUTURE_INTERPRETATION_RELPATHS[lane]
        ).read_bytes() == source.read_bytes()
        terminal = json.loads(
            (
                root / POST_TERMINAL_RECEIPT_RELPATHS[lane]
            ).read_text(encoding="utf-8")
        )
        assert terminal["terminal_state"] == "complete"

    consolidation = build_consolidation(repo_root=root)
    assert (
        consolidation["interpretation"]["state"]
        == "mixed_or_reviewer_disagreement"
    )
    assert len(
        consolidation["blind_review_vectors"]["comparison_reviews"]
    ) == 8
    assert len(consolidation["post_reveal_vectors"]) == 2
    assert consolidation["boundary"]["score_vote_winner_or_graph_decision_created"] is False

    write_consolidation(repo_root=root)
    assert (root / FUTURE_CONSOLIDATION_RELPATH).exists()
    assert validate_complete_result(repo_root=root) == []
