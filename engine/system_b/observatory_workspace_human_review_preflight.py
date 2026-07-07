"""Read-only preflight for Observatory workspace human-review launch.

The preflight checks whether a reviewer has enough local inputs to start the
Observatory workspace review. It does not launch Observatory, run Lolla, call
providers, create runs, mutate archives, write sidecars, complete human review,
or claim product proof.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PREFLIGHT_SCHEMA_VERSION = "lolla.observatory_workspace_human_review_preflight.v0"
DEFAULT_REVIEW_PATH = Path("reviews/human/observatory-workspace/review.json")
DEFAULT_INTAKE_PATH = Path("reviews/human/observatory-workspace/intake.json")
DEFAULT_FORM_PATH = Path(
    "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json"
)
DEFAULT_PORT = 8080

PRODUCT_JOURNEY = ("Outcome", "Learn", "Models", "Relations", "Map", "Receipts")
REVIEW_CLICKTHROUGH = (
    "Review Guide",
    "Outcome",
    "Learn",
    "Models",
    "model detail",
    "Relations",
    "relation detail",
    "Map",
    "Receipts",
)
OPTIONAL_INSPECTION = ("Extraction audit", "Usage", "Advanced audit")

BOUNDARY = {
    "runs_lolla": False,
    "invokes_lolla_skill": False,
    "calls_provider_or_model": False,
    "creates_new_run": False,
    "launches_observatory": False,
    "generates_sidecars": False,
    "wires_skill_runtime_behavior": False,
    "mutates_archives": False,
    "writes_review_or_intake": False,
    "compiled_spa_bundle_changed": False,
    "touches_skill_md": False,
    "touches_scripts_skill": False,
    "touches_archive_run": False,
}
NON_CLAIMS = {
    "product_proof": False,
    "human_validated": False,
    "answer_correctness": False,
    "advice_correctness": False,
    "runtime_integration_authorized": False,
    "action_authorized": False,
    "graph_edges_are_proof": False,
    "relation_confidence_is_certification": False,
}


class ObservatoryWorkspaceHumanReviewPreflightError(ValueError):
    """Raised when the preflight request is malformed."""


def build_observatory_workspace_human_review_preflight(
    *,
    result_path: Path | str,
    case_id: str,
    port: int = DEFAULT_PORT,
    review_path: Path | str = DEFAULT_REVIEW_PATH,
    intake_path: Path | str = DEFAULT_INTAKE_PATH,
    form_path: Path | str = DEFAULT_FORM_PATH,
) -> dict[str, Any]:
    """Return a safe, deterministic launch-readiness report."""

    selected_case_id = _required_text(case_id, "case_id")
    selected_port = _valid_port(port)
    result = Path(result_path)
    review = Path(review_path)
    intake = Path(intake_path)
    form = Path(form_path)

    result_status = _result_status(result)
    artifact_status = _artifact_status(review, intake)
    preflight_status = _preflight_status(result_status["status"], artifact_status)
    ready_to_launch = preflight_status == "ready_to_launch_review"

    return {
        "schema_version": PREFLIGHT_SCHEMA_VERSION,
        "preflight_status": preflight_status,
        "ready_to_launch_review": ready_to_launch,
        "selected_case_id": selected_case_id,
        "result": result_status,
        "review_artifacts": artifact_status,
        "launch": {
            "server_command": [
                "python3",
                "observatory/serve_result.py",
                "--result",
                "$LOLLA_OBSERVATORY_REVIEW_RESULT",
                "--port",
                str(selected_port),
            ],
            "review_guide_url": (
                f"http://localhost:{selected_port}/review/observatory-workspace"
                f"?case_id={selected_case_id}"
            ),
            "workspace_url": (
                f"http://localhost:{selected_port}/workspace"
                f"?case_id={selected_case_id}#outcome"
            ),
            "normal_product_journey": list(PRODUCT_JOURNEY),
            "review_clickthrough_order": list(REVIEW_CLICKTHROUGH),
            "optional_inspection_after_receipts": list(OPTIONAL_INSPECTION),
        },
        "review_output": {
            "blank_form": _relative_ref(form),
            "completed_review": _relative_ref(review),
            "captured_intake": _relative_ref(intake),
            "capture_command": [
                "python3",
                "scripts/evals/capture_observatory_workspace_human_review.py",
                "--review",
                _relative_ref(review),
                "--out",
                _relative_ref(intake),
                "--source-ref",
                _relative_ref(review),
            ],
        },
        "next_action": _next_action(preflight_status),
        "boundary": dict(BOUNDARY),
        "non_claims": dict(NON_CLAIMS),
    }


def render_observatory_workspace_human_review_preflight_json(
    payload: dict[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Serialize a preflight payload as stable JSON."""

    kwargs: dict[str, Any] = {"sort_keys": True}
    if pretty:
        kwargs["indent"] = 2
    return json.dumps(payload, **kwargs) + "\n"


def write_observatory_workspace_human_review_preflight_json(
    path: Path | str,
    payload: dict[str, Any],
    *,
    pretty: bool = False,
) -> None:
    """Write a preflight report without creating runtime artifacts."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_observatory_workspace_human_review_preflight_json(
            payload,
            pretty=pretty,
        ),
        encoding="utf-8",
    )


def _result_status(path: Path) -> dict[str, Any]:
    exists = path.exists()
    payload_kind = "not_read"
    status = "missing"
    if exists:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload_kind = "invalid_json"
            status = "invalid_json"
        except OSError:
            payload_kind = "unreadable"
            status = "unreadable"
        else:
            payload_kind = "object" if isinstance(payload, dict) else type(payload).__name__
            status = "ready" if isinstance(payload, dict) else "invalid_root"

    return {
        "status": status,
        "exists": exists,
        "json_root": payload_kind,
        "safe_ref": path.name or "result.json",
        "absolute_path_recorded": False,
    }


def _artifact_status(review: Path, intake: Path) -> dict[str, Any]:
    review_exists = review.exists()
    intake_exists = intake.exists()
    if review_exists and intake_exists:
        status = "intake_ready_to_inspect"
    elif review_exists:
        status = "review_ready_to_capture"
    elif intake_exists:
        status = "blocked_intake_without_review"
    else:
        status = "awaiting_review_response"
    return {
        "status": status,
        "review_exists": review_exists,
        "intake_exists": intake_exists,
        "review_ref": _relative_ref(review),
        "intake_ref": _relative_ref(intake),
    }


def _preflight_status(result_status: str, artifacts: dict[str, Any]) -> str:
    if result_status == "missing":
        return "blocked_missing_result"
    if result_status in {"invalid_json", "invalid_root", "unreadable"}:
        return f"blocked_{result_status}"
    artifact_status = str(artifacts["status"])
    if artifact_status == "blocked_intake_without_review":
        return artifact_status
    if artifact_status == "review_ready_to_capture":
        return "review_ready_to_capture"
    if artifact_status == "intake_ready_to_inspect":
        return "intake_ready_to_inspect"
    return "ready_to_launch_review"


def _next_action(status: str) -> str:
    return {
        "blocked_missing_result": "provide_existing_completed_run_result_json",
        "blocked_invalid_json": "repair_or_choose_different_result_json",
        "blocked_invalid_root": "provide_result_json_object",
        "blocked_unreadable": "repair_result_file_permissions_or_choose_another_result",
        "blocked_intake_without_review": "repair_human_review_artifact_state",
        "review_ready_to_capture": "run_capture_observatory_workspace_human_review",
        "intake_ready_to_inspect": "inspect_captured_human_review_intake",
        "ready_to_launch_review": "open_review_guide_and_collect_human_response",
    }.get(status, "inspect_preflight_status")


def _required_text(value: object, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ObservatoryWorkspaceHumanReviewPreflightError(f"{field} is required")
    return text


def _valid_port(value: int) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ObservatoryWorkspaceHumanReviewPreflightError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise ObservatoryWorkspaceHumanReviewPreflightError("port must be between 1 and 65535")
    return port


def _relative_ref(path: Path) -> str:
    if path.is_absolute():
        return path.name
    return path.as_posix()
