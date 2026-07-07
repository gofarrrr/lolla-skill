from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.observatory_workspace_human_review_preflight import (  # noqa: E402
    PREFLIGHT_SCHEMA_VERSION,
    build_observatory_workspace_human_review_preflight,
    render_observatory_workspace_human_review_preflight_json,
)


SCRIPT = REPO_ROOT / "scripts/evals/preflight_observatory_workspace_human_review.py"
DOC = REPO_ROOT / "docs/product/observatory-workspace-human-review-preflight-v0.md"
CHECKLIST_DOC = (
    REPO_ROOT / "docs/product/observatory-workspace-human-review-launch-checklist-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
HUMAN_README = REPO_ROOT / "reviews/human/observatory-workspace/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-human-review-preflight-v0/review.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _run_preflight(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_preflight_ready_status_uses_safe_refs_and_review_urls(tmp_path: Path) -> None:
    result_path = _write_json(tmp_path / "private-result.json", {"ok": True})

    payload = build_observatory_workspace_human_review_preflight(
        result_path=result_path,
        case_id="launch-public-enterprise-beta",
        port=18181,
        review_path=tmp_path / "review.json",
        intake_path=tmp_path / "intake.json",
    )
    rendered = render_observatory_workspace_human_review_preflight_json(
        payload,
        pretty=True,
    )

    assert payload["schema_version"] == PREFLIGHT_SCHEMA_VERSION
    assert payload["preflight_status"] == "ready_to_launch_review"
    assert payload["ready_to_launch_review"] is True
    assert payload["result"]["status"] == "ready"
    assert payload["result"]["safe_ref"] == "private-result.json"
    assert payload["result"]["absolute_path_recorded"] is False
    assert payload["review_artifacts"]["status"] == "awaiting_review_response"
    assert payload["launch"]["review_guide_url"] == (
        "http://localhost:18181/review/observatory-workspace"
        "?case_id=launch-public-enterprise-beta"
    )
    assert payload["next_action"] == "open_review_guide_and_collect_human_response"
    assert str(tmp_path) not in rendered


def test_preflight_statuses_for_review_capture_and_intake(tmp_path: Path) -> None:
    result_path = _write_json(tmp_path / "result.json", {"ok": True})
    review_path = _write_json(tmp_path / "review.json", {"review": True})
    intake_path = tmp_path / "intake.json"

    review_ready = build_observatory_workspace_human_review_preflight(
        result_path=result_path,
        case_id="launch-public-enterprise-beta",
        review_path=review_path,
        intake_path=intake_path,
    )
    assert review_ready["preflight_status"] == "review_ready_to_capture"
    assert review_ready["ready_to_launch_review"] is False
    assert review_ready["next_action"] == "run_capture_observatory_workspace_human_review"

    _write_json(intake_path, {"intake": True})
    intake_ready = build_observatory_workspace_human_review_preflight(
        result_path=result_path,
        case_id="launch-public-enterprise-beta",
        review_path=review_path,
        intake_path=intake_path,
    )
    assert intake_ready["preflight_status"] == "intake_ready_to_inspect"
    assert intake_ready["next_action"] == "inspect_captured_human_review_intake"


def test_preflight_blocks_missing_invalid_and_incoherent_inputs(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")
    list_path = _write_json(tmp_path / "list.json", [])
    result_path = _write_json(tmp_path / "result.json", {"ok": True})
    intake_path = _write_json(tmp_path / "intake.json", {"intake": True})

    missing = build_observatory_workspace_human_review_preflight(
        result_path=tmp_path / "missing.json",
        case_id="launch-public-enterprise-beta",
    )
    assert missing["preflight_status"] == "blocked_missing_result"
    assert missing["next_action"] == "provide_existing_completed_run_result_json"

    invalid = build_observatory_workspace_human_review_preflight(
        result_path=invalid_path,
        case_id="launch-public-enterprise-beta",
    )
    assert invalid["preflight_status"] == "blocked_invalid_json"
    assert invalid["next_action"] == "repair_or_choose_different_result_json"

    invalid_root = build_observatory_workspace_human_review_preflight(
        result_path=list_path,
        case_id="launch-public-enterprise-beta",
    )
    assert invalid_root["preflight_status"] == "blocked_invalid_root"
    assert invalid_root["next_action"] == "provide_result_json_object"

    incoherent = build_observatory_workspace_human_review_preflight(
        result_path=result_path,
        case_id="launch-public-enterprise-beta",
        review_path=tmp_path / "missing-review.json",
        intake_path=intake_path,
    )
    assert incoherent["preflight_status"] == "blocked_intake_without_review"
    assert incoherent["next_action"] == "repair_human_review_artifact_state"


def test_preflight_cli_prints_and_writes_safe_report(tmp_path: Path) -> None:
    result_path = _write_json(tmp_path / "result.json", {"ok": True})
    out_path = tmp_path / "preflight.json"

    printed = _run_preflight(
        "--result",
        str(result_path),
        "--case-id",
        "launch-public-enterprise-beta",
        "--port",
        "18182",
        "--pretty",
    )
    assert printed.returncode == 0, printed.stderr
    printed_payload = json.loads(printed.stdout)
    assert printed_payload["preflight_status"] == "ready_to_launch_review"
    assert str(tmp_path) not in printed.stdout

    written = _run_preflight(
        "--result",
        str(result_path),
        "--case-id",
        "launch-public-enterprise-beta",
        "--out",
        str(out_path),
        "--pretty",
    )
    assert written.returncode == 0, written.stderr
    assert written.stdout == ""
    payload = _load_json(out_path)
    assert payload["preflight_status"] == "ready_to_launch_review"
    assert str(tmp_path) not in out_path.read_text(encoding="utf-8")


def test_preflight_cli_returns_nonzero_for_blocked_status(tmp_path: Path) -> None:
    result_path = tmp_path / "missing.json"
    out_path = tmp_path / "blocked.json"

    result = _run_preflight(
        "--result",
        str(result_path),
        "--case-id",
        "launch-public-enterprise-beta",
        "--out",
        str(out_path),
        "--pretty",
    )

    assert result.returncode == 2
    payload = _load_json(out_path)
    assert payload["preflight_status"] == "blocked_missing_result"
    assert payload["ready_to_launch_review"] is False


def test_preflight_docs_review_and_indexes_capture_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")
    checklist = CHECKLIST_DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    human_readme = HUMAN_README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Workspace Human Review Preflight" in readme
    assert "observatory-workspace-human-review-preflight-v0.md" in readme
    assert "preflight_observatory_workspace_human_review.py" in checklist
    assert "preflight_observatory_workspace_human_review.py" in human_readme
    assert review["decision_gate"] == (
        "ready_to_preflight_real_human_hierarchy_review_launch"
    )
    assert review["next_gate"] == "awaiting_real_human_hierarchy_review_response"

    for phrase in [
        "read-only preflight for launching a real human hierarchy review",
        "does not launch Observatory",
        "does not write the absolute result path into the report",
        "ready_to_launch_review",
        "review_ready_to_capture",
        "intake_ready_to_inspect",
        "blocked_missing_result",
        "blocked_invalid_json",
        "blocked_invalid_root",
        "blocked_intake_without_review",
        "The preflight does not decide whether the Observatory workspace is good.",
    ]:
        assert phrase in doc

    assert review["implemented"]["read_only_preflight_module"] is True
    assert review["implemented"]["read_only_preflight_cli"] is True
    assert review["implemented"]["safe_preflight_json_output"] is True
    assert review["implemented"]["completed_review_present_in_this_slice"] is False
    assert review["implemented"]["intake_present_in_this_slice"] is False


def test_preflight_boundaries_links_and_private_markers_are_clean() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    review = _load_json(REVIEW)

    for phrase in [
        "does not add a completed review or intake artifact",
        "does not launch Observatory",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create a new run",
        "does not generate or attach sidecars",
        "does not wire skill runtime behavior",
        "does not mutate archives",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize automatic action",
    ]:
        assert phrase in normalized

    assert review["boundary"]["adds_completed_review_or_intake"] is False
    assert review["boundary"]["launches_observatory"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["creates_new_run"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False
    assert review["non_claims"]["action_authorized"] is False

    missing = []
    for path in [DOC, README, HUMAN_README, CHECKLIST_DOC]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, CHECKLIST_DOC, HUMAN_README, REVIEW]
    )
    assert missing == []
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
