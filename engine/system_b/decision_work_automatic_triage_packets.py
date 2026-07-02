"""Offline Decision Work automatic triage packet construction.

PR155 prepares a checked-in-safe dossier for later provisional triage. It is
deterministic and read-only: it gathers source refs, custody status, field
group policy, known limits, and future triage tasks. It does not interpret,
call models, run Lolla, mutate archives, score advice, create labels, approve
anything, or authorize agent action.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


DECISION_WORK_AUTOMATIC_TRIAGE_PACKETS_SCHEMA_VERSION = (
    "lolla.decision_work_automatic_triage_packets.v0"
)
DECISION_WORK_AUTOMATIC_TRIAGE_CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_automatic_triage_contract.v0"
)
DEFAULT_TRIAGE_CONTRACT_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-automatic-triage-contract-v0.json"
)
REPO_ROOT = Path(__file__).resolve().parents[2]

TRIAGE_PACKET_MODE = "checked_in_safe"
TRIAGE_FIELD_PACKET_STATUS = "not_evaluated"

CASE_REFS: tuple[dict[str, Any], ...] = (
    {
        "case_id": "launch-public-enterprise-beta",
        "case_ref": "launch-public-enterprise-beta/20260627T104146Z_7bfe79",
        "decision_family": "GTM / enterprise launch timing",
        "enriched_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
        ),
        "original_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
        ),
        "interpretation_read_ref": (
            "reviews/codex-assisted/"
            "decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
        ),
        "source_review_refs": (
            "reviews/codex-assisted/"
            "decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json",
            "reviews/codex-assisted/"
            "decision-work-brief-three-builder-case-pattern-review-v0/review.json",
        ),
        "known_limit": (
            "Checked-in-safe launch and buyer-context evidence remains "
            "compressed; private buyer reality and rollout nuance are not "
            "available in the packet."
        ),
    },
    {
        "case_id": "deploy-assisted-intake-routing",
        "case_ref": "deploy-assisted-intake-routing/20260627T130339Z_4cd3cb",
        "decision_family": "healthcare operations / deployment controls",
        "enriched_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md"
        ),
        "original_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
        ),
        "interpretation_read_ref": (
            "reviews/codex-assisted/"
            "decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json"
        ),
        "source_review_refs": (
            "reviews/codex-assisted/"
            "decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json",
            "reviews/codex-assisted/"
            "decision-work-brief-three-builder-case-pattern-review-v0/review.json",
        ),
        "known_limit": (
            "Healthcare workflow and compliance stakes remain source-limited; "
            "domain review may be needed before any user-facing or operational use."
        ),
    },
    {
        "case_id": "ceo-remove-founding-cofounder",
        "case_ref": "ceo-remove-founding-cofounder/20260627T093131Z_59d153",
        "decision_family": "founder governance / relationship-sensitive authority transition",
        "enriched_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md"
        ),
        "original_brief_ref": (
            "docs/conversation-understanding/"
            "decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
        ),
        "interpretation_read_ref": (
            "reviews/codex-assisted/"
            "decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json"
        ),
        "source_review_refs": (
            "reviews/codex-assisted/"
            "decision-work-brief-third-builder-case-output-v0/review.json",
            "reviews/codex-assisted/"
            "decision-work-brief-three-builder-case-pattern-review-v0/review.json",
        ),
        "known_limit": (
            "Governance, legal, relationship, and authority-transition nuance "
            "is especially risky to smooth into operational confidence."
        ),
    },
)

SHARED_SOURCE_REVIEW_REFS = (
    "reviews/codex-assisted/"
    "decision-work-brief-three-builder-case-pattern-review-v0/review.json",
)
HUMAN_CALIBRATION_REFS = (
    "reviews/codex-assisted/"
    "decision-work-brief-human-review-awaiting-response-gate-v0/review.json",
    "docs/conversation-understanding/"
    "decision-work-brief-human-review-response-template-v0.json",
)
NON_CLAIMS = (
    "packet_is_not_triage",
    "packet_is_not_interpretation",
    "packet_is_not_a_decision_work_brief",
    "packet_is_not_product_proof",
    "packet_is_not_human_validation",
    "packet_does_not_score_answer_quality",
    "packet_does_not_authorize_agent_action",
    "packet_does_not_authorize_automatic_action",
    "packet_does_not_run_lolla",
    "packet_does_not_call_models",
    "packet_does_not_change_runtime",
    "packet_does_not_mutate_archives",
    "clean_artifacts_do_not_imply_good_advice",
    "future_triage_required",
)


class DecisionWorkAutomaticTriagePacketInputError(ValueError):
    """Sanitized packet input error."""


def build_decision_work_automatic_triage_packets(
    *,
    triage_contract_path: Path | str = DEFAULT_TRIAGE_CONTRACT_RELPATH,
    repo_root: Path | str = REPO_ROOT,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a checked-in-safe automatic triage packet from existing refs."""

    root = Path(repo_root)
    contract_ref = _repo_relative_ref(triage_contract_path, repo_root=root)
    contract = _load_json_object(root / contract_ref)
    _validate_triage_contract(contract)

    source_cases = [_case_packet(case, repo_root=root) for case in CASE_REFS]
    triage_field_groups = _triage_field_group_packets(contract["triage_fields"])

    return {
        "schema_version": DECISION_WORK_AUTOMATIC_TRIAGE_PACKETS_SCHEMA_VERSION,
        "packet_metadata": {
            "packet_id": "decision_work_automatic_triage_packet:v0",
            "created_at": created_at or _utc_now(),
            "builder": "engine.system_b.decision_work_automatic_triage_packets",
            "builder_mode": "deterministic_offline_metadata_only",
            "case_count": len(source_cases),
            "semantic_triage_fields_filled": False,
        },
        "mode": TRIAGE_PACKET_MODE,
        "triage_contract_ref": contract_ref,
        "source_cases": source_cases,
        "source_artifacts": {
            "triage_contract_ref": contract_ref,
            "three_case_pattern_review_refs": list(SHARED_SOURCE_REVIEW_REFS),
            "human_calibration_refs": list(HUMAN_CALIBRATION_REFS),
        },
        "enriched_brief_refs": [case["enriched_brief_ref"] for case in source_cases],
        "original_brief_refs": [case["original_brief_ref"] for case in source_cases],
        "interpretation_read_refs": [
            case["interpretation_read_ref"] for case in source_cases
        ],
        "source_review_refs": sorted(
            {
                ref
                for case in source_cases
                for ref in case["source_review_refs"]
            }
            | set(SHARED_SOURCE_REVIEW_REFS)
        ),
        "human_calibration_refs": list(HUMAN_CALIBRATION_REFS),
        "custody_flags": _custody_flags(),
        "triage_field_groups": triage_field_groups,
        "future_triage_tasks": _future_triage_tasks(contract),
        "known_limits": [
            "The packet is checked-in-safe metadata only and contains no raw or private content.",
            "The packet does not evaluate triage categories or route values.",
            "The packet carries provisional Codex-assisted interpretation-read refs without converting them into human validation.",
            "Human calibration is explicitly deferred because no real human response exists yet.",
            "Runtime and customer-facing use remain blocked until later review and explicit integration work.",
        ],
        "non_claims": list(NON_CLAIMS),
    }


def render_decision_work_automatic_triage_packets_json(
    packet: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render packet JSON deterministically."""

    indent = 2 if pretty else None
    return json.dumps(packet, indent=indent, sort_keys=True) + "\n"


def write_decision_work_automatic_triage_packets_output(
    output_path: Path | str,
    payload: str,
) -> None:
    """Write a packet JSON payload to an explicit output path."""

    path = Path(output_path).expanduser()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkAutomaticTriagePacketInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def validate_output_path(
    *,
    output_path: Path | str,
    triage_contract_path: Path | str = DEFAULT_TRIAGE_CONTRACT_RELPATH,
) -> Path:
    """Refuse obviously unsafe output destinations."""

    output = Path(output_path).expanduser().resolve()
    contract = Path(triage_contract_path).expanduser().resolve()
    if output == contract:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "output path must be different from the triage contract"
        )
    return output


def _case_packet(case: Mapping[str, Any], *, repo_root: Path) -> dict[str, Any]:
    refs = {
        "enriched_brief_ref": case["enriched_brief_ref"],
        "original_brief_ref": case["original_brief_ref"],
        "interpretation_read_ref": case["interpretation_read_ref"],
        "source_review_refs": list(case["source_review_refs"]),
    }
    for ref in _flatten_refs(refs):
        _require_existing_repo_ref(repo_root, ref)
    return {
        "case_id": case["case_id"],
        "case_ref": case["case_ref"],
        "decision_family": case["decision_family"],
        **refs,
        "local_private_context_status": "not_included_checked_in_safe_packet",
        "semantic_triage_status": TRIAGE_FIELD_PACKET_STATUS,
        "known_limit": case["known_limit"],
    }


def _triage_field_group_packets(
    triage_fields: Any,
) -> list[dict[str, Any]]:
    if not isinstance(triage_fields, list):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract fields were missing"
        )
    packets = []
    for field in triage_fields:
        if not isinstance(field, Mapping):
            raise DecisionWorkAutomaticTriagePacketInputError(
                "triage contract field was malformed"
            )
        packets.append(
            {
                "field_group": field.get("field_group"),
                "owner": field.get("owner"),
                "status_vocabulary": field.get("status_vocabulary"),
                "allowed_values": field.get("allowed_values"),
                "source_refs_required": field.get("source_refs_required"),
                "uncertainty_required": field.get("uncertainty_required"),
                "privacy_handling": field.get("privacy_handling"),
                "can_feed_user_surface": field.get("can_feed_user_surface"),
                "can_feed_agent_inspection": field.get("can_feed_agent_inspection"),
                "blocks_runtime_attachment": field.get("blocks_runtime_attachment"),
                "requires_human_or_domain_review": field.get(
                    "requires_human_or_domain_review"
                ),
                "must_not_be_used_as_quality_label": field.get(
                    "must_not_be_used_as_quality_label"
                ),
                "current_packet_status": TRIAGE_FIELD_PACKET_STATUS,
                "semantic_triage_filled": False,
                "value": None,
                "source_refs": [],
                "uncertainty": "not_evaluated",
                "future_triage_question": (
                    "How should this field route attention or escalation for "
                    "the three checked-in-safe Decision Work Brief examples?"
                ),
            }
        )
    return packets


def _future_triage_tasks(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    route_values = contract.get("route_value_vocabulary")
    if not isinstance(route_values, list):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract route vocabulary was missing"
        )
    return [
        {
            "task": "assign_case_triage_categories",
            "owner": "llm_interpretation",
            "status": "not_evaluated",
            "source_refs_required": True,
            "must_not_be_used_as_quality_label": True,
        },
        {
            "task": "route_user_surface_agent_inspection_human_domain_and_runtime",
            "owner": "mixed",
            "status": "not_evaluated",
            "allowed_route_values": route_values,
            "source_refs_required": True,
            "uncertainty_required": True,
            "must_not_authorize_action": True,
        },
        {
            "task": "surface_source_depth_private_context_and_overtrust_risks",
            "owner": "mixed",
            "status": "not_evaluated",
            "source_refs_required": True,
            "privacy_handling": "summaries_and_status_only_no_private_content",
            "must_not_be_used_as_quality_label": True,
        },
    ]


def _validate_triage_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != DECISION_WORK_AUTOMATIC_TRIAGE_CONTRACT_SCHEMA_VERSION:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract schema version was unsupported"
        )
    custody = contract.get("custody_flags")
    if not isinstance(custody, Mapping):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract custody flags were missing"
        )
    if custody.get("model_calls") != 0:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract model calls were not conservative"
        )
    for flag in (
        "human_validated",
        "human_review_completed",
        "product_proof",
        "runtime_invoked",
        "skill_invoked",
        "archive_mutated",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
        "raw_private_content_included",
    ):
        if custody.get(flag) is not False:
            raise DecisionWorkAutomaticTriagePacketInputError(
                "triage contract custody flags were not conservative"
            )
    if not isinstance(contract.get("triage_fields"), list):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract field groups were missing"
        )
    if not isinstance(contract.get("triage_categories"), list):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "triage contract categories were missing"
        )


def _custody_flags() -> dict[str, Any]:
    return {
        "checked_in_safe": True,
        "human_validated": False,
        "human_review_completed": False,
        "human_response_collected": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "semantic_triage_performed": False,
        "triage_fields_filled": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "raw_transcript_included": False,
        "raw_revised_answer_included": False,
        "raw_memo_included": False,
        "private_ledger_content_included": False,
        "local_absolute_paths_included": False,
        "secrets_included": False,
        "automatic_labels_created": False,
        "broad_judge_used": False,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "input JSON file was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "input JSON file was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "input JSON file was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkAutomaticTriagePacketInputError(
            f"input JSON file could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "input JSON root was not an object"
        )
    return payload


def _repo_relative_ref(path: Path | str, *, repo_root: Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        raise DecisionWorkAutomaticTriagePacketInputError(
            "local absolute paths are not allowed in packet refs"
        )
    ref = candidate.as_posix()
    _require_existing_repo_ref(repo_root, ref)
    return ref


def _require_existing_repo_ref(repo_root: Path, ref: str) -> None:
    if ref.startswith("/") or ".." in Path(ref).parts:
        raise DecisionWorkAutomaticTriagePacketInputError(
            "unsafe repository ref was rejected"
        )
    if ref.startswith(("SKILL.md", "scripts/skill/", "plans/", "archive/")):
        raise DecisionWorkAutomaticTriagePacketInputError(
            "forbidden repository ref was rejected"
        )
    if not (repo_root / ref).exists():
        raise DecisionWorkAutomaticTriagePacketInputError(
            f"required repository ref was missing:{ref}"
        )


def _flatten_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        refs: list[str] = []
        for child in value.values():
            refs.extend(_flatten_refs(child))
        return refs
    if isinstance(value, (list, tuple)):
        refs = []
        for child in value:
            refs.extend(_flatten_refs(child))
        return refs
    return []


def _utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
