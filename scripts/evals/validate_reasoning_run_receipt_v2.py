#!/usr/bin/env python3
"""Provider-free cross-field checks for the Gate 7 reasoning-run receipt v2.

JSON Schema owns static shape. This small companion checks only relationships
that JSON Schema cannot express cleanly: source and artifact references,
source-end action/deadline presence, authorization time scope, audience split,
graph claim levels, bounded custody language, pressure effects, and duplicates.
It never interprets prose, calls a provider, scores quality, or changes runtime.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import re
from typing import Any


RECEIPT_SCHEMA_VERSION = "lolla.reasoning_run_receipt.v2"
VALIDATION_SCHEMA_VERSION = "lolla.reasoning_run_receipt_validation.v2"
REQUIRED_NON_CLAIM_IDS = {
    "not_human_validation",
    "not_answer_quality_proof",
    "not_graph_value_proof",
    "not_runtime_authority",
    "not_autonomous_action_authority",
}

_TOP_LEVEL_FIELDS = {
    "schema_version",
    "status",
    "receipt_metadata",
    "complete_conversation",
    "source_index",
    "source_end_state",
    "reasoning_process",
    "pressure_accountability",
    "comparison_evidence",
    "graph_attribution",
    "custody_boundary",
    "claim_boundary",
    "operability",
    "authorization_snapshot",
    "questions",
    "artifact_manifest",
    "non_claims",
}
_METADATA_FIELDS = {
    "receipt_id",
    "case_id",
    "run_id",
    "frozen_at_utc",
    "as_of_event_id",
    "as_of_event_sequence",
    "artifact_state",
}
_SOURCE_FIELDS = {"source_ref", "turn_index", "speaker", "source_kind"}
_SOURCE_END_FIELDS = {
    "as_of_source_ref",
    "decision_status",
    "stated_next_action",
    "deadline_or_time_constraint",
    "unresolved_items",
}
_EVIDENCE_FIELDS = {"status", "summary", "source_refs"}
_ARTIFACT_FIELDS = {"role", "path", "sha256"}
_PRESSURE_FIELDS = {
    "pressure_id",
    "observed_consumer_pressure_id",
    "identity_status",
    "semantic_hearing_status",
    "effect_consistency_status",
    "origin",
    "admission_status",
    "consumer_disposition",
    "challenge",
    "strongest_plausible_application",
    "why",
    "source_refs",
    "lineage_ids",
    "graph_pressure_ids",
    "visible_effect",
    "private_guardrail",
    "risk_if_forced",
    "risk_if_ignored",
}
_COMPARISON_FIELDS = {
    "status",
    "blind_review_before_key",
    "control_summary",
    "treatment_summary",
    "observed_difference",
    "limits",
    "anonymous_outputs",
    "reveal_mapping",
    "blind_review_summary",
    "artifact_refs",
}
_ANONYMOUS_OUTPUT_FIELDS = {
    "blind_label",
    "status",
    "response",
    "response_sha256",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
}
_REVEAL_MAPPING_FIELDS = {"blind_label", "arm_id"}
_GRAPH_FIELDS = {
    "exposure_status",
    "exposed_graph_pressure_ids",
    "exact_lineage_status",
    "exact_lineage_pressure_ids",
    "individual_disposition_status",
    "individually_dispositioned_graph_pressure_ids",
    "causal_contribution_status",
    "statement_scope",
    "summary",
    "limits",
}
_CUSTODY_FIELDS = {
    "claim_level",
    "summary",
    "artifacts_support",
    "artifacts_do_not_establish",
    "external_execution_independently_verified",
    "reasoning_quality_inferred",
}
_AUTHORIZATION_FIELDS = {
    "scope_label",
    "as_of_event_id",
    "as_of_utc",
    "as_of_event_sequence",
    "authorizations",
    "future_events_not_covered",
    "post_reader_status_artifact_required",
}
_QUESTION_FIELDS = {
    "case_domain_unknowns",
    "reader_reconstruction_checks",
    "human_product_review_questions",
}
_OPERABILITY_FIELDS = {
    "provider_calls",
    "evaluator_calls",
    "automatic_retries",
    "total_tokens",
    "token_evidence_state",
    "token_scope",
    "estimated_cost_usd",
    "cost_evidence_state",
    "wall_time_seconds",
    "notes",
}

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")
_BLIND_LABEL_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_PROOF_RE = re.compile(r"\b(?:proof|prove|proven|proves)\b", re.IGNORECASE)
_ABSOLUTE_GRAPH_RE = re.compile(
    r"\b(?:no graph influence|graph had no influence|graph was not used|"
    r"graph chunks were not used|no graph effect|graph had no effect|"
    r"graph did not contribute)\b",
    re.IGNORECASE,
)


class ReasoningRunReceiptValidationError(ValueError):
    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _normal(value: str) -> str:
    return " ".join(value.casefold().split())


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _object(
    value: object, *, label: str, fields: set[str], errors: list[str]
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{label} must be an object")
        return {}
    if set(value) != fields:
        errors.append(f"{label} fields are invalid")
    return value


def _rows(value: object, *, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    return value


def _strings(
    value: object,
    *,
    label: str,
    errors: list[str],
    maximum: int | None = None,
    required: bool = False,
) -> list[str]:
    rows = _rows(value, label=label, errors=errors)
    if any(not _nonempty(row) for row in rows):
        errors.append(f"{label} must contain non-empty strings")
    result = [str(row).strip() for row in rows if isinstance(row, str) and row.strip()]
    if required and not result:
        errors.append(f"{label} must not be empty")
    if maximum is not None and len(result) > maximum:
        errors.append(f"{label} exceeds maximum {maximum}")
    normalized = [_normal(row) for row in result]
    if len(normalized) != len(set(normalized)):
        errors.append(f"{label} contains duplicates")
    return result


def _ids(
    value: object,
    *,
    label: str,
    errors: list[str],
    required: bool = False,
) -> list[str]:
    result = _strings(value, label=label, errors=errors, required=required)
    if any(not _ID_RE.fullmatch(row) for row in result):
        errors.append(f"{label} contains an invalid id")
    return result


def _validate_ref_list(
    value: object,
    *,
    label: str,
    allowed: set[str],
    errors: list[str],
    required: bool = False,
) -> list[str]:
    result = _ids(value, label=label, errors=errors, required=required)
    unknown = sorted(set(result) - allowed)
    if unknown:
        errors.append(f"{label} contains unknown references: {unknown}")
    return result


def _validate_metadata(receipt: Mapping[str, Any], errors: list[str]) -> Mapping[str, Any]:
    metadata = _object(
        receipt.get("receipt_metadata"),
        label="receipt_metadata",
        fields=_METADATA_FIELDS,
        errors=errors,
    )
    for field in ("receipt_id", "case_id", "run_id", "as_of_event_id"):
        if not _nonempty(metadata.get(field)) or not _ID_RE.fullmatch(str(metadata.get(field))):
            errors.append(f"receipt_metadata.{field} is invalid")
    if not isinstance(metadata.get("frozen_at_utc"), str) or not _UTC_RE.fullmatch(
        str(metadata.get("frozen_at_utc", ""))
    ):
        errors.append("receipt_metadata.frozen_at_utc is invalid")
    sequence = metadata.get("as_of_event_sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        errors.append("receipt_metadata.as_of_event_sequence must be non-negative")
    expected_state = (
        "prospective_fixture"
        if receipt.get("status") == "prospective_fixture"
        else "frozen_immutable_snapshot"
    )
    if metadata.get("artifact_state") != expected_state:
        errors.append("receipt_metadata.artifact_state does not match receipt status")
    return metadata


def _validate_manifest(receipt: Mapping[str, Any], errors: list[str]) -> set[str]:
    rows = _rows(receipt.get("artifact_manifest"), label="artifact_manifest", errors=errors)
    if not rows:
        errors.append("artifact_manifest must not be empty")
    roles: list[str] = []
    paths: list[str] = []
    for index, value in enumerate(rows):
        label = f"artifact_manifest[{index}]"
        row = _object(value, label=label, fields=_ARTIFACT_FIELDS, errors=errors)
        role = row.get("role")
        if not _nonempty(role) or not _ID_RE.fullmatch(str(role)):
            errors.append(f"{label}.role is invalid")
        else:
            roles.append(str(role))
        path = row.get("path")
        if not _nonempty(path):
            errors.append(f"{label}.path is required")
        else:
            text = str(path)
            paths.append(text)
            if Path(text).is_absolute() or ".." in Path(text).parts:
                errors.append(f"{label}.path must be repository-relative")
        if not isinstance(row.get("sha256"), str) or not _SHA_RE.fullmatch(
            str(row.get("sha256", ""))
        ):
            errors.append(f"{label}.sha256 is invalid")
    if len(roles) != len(set(roles)):
        errors.append("artifact_manifest roles must be unique")
    if len(paths) != len(set(paths)):
        errors.append("artifact_manifest paths must be unique")
    return set(roles)


def _validate_source(receipt: Mapping[str, Any], errors: list[str]) -> set[str]:
    rows = _rows(receipt.get("source_index"), label="source_index", errors=errors)
    if not rows:
        errors.append("source_index must not be empty")
    refs: list[str] = []
    turns: list[int] = []
    for index, value in enumerate(rows):
        label = f"source_index[{index}]"
        row = _object(value, label=label, fields=_SOURCE_FIELDS, errors=errors)
        ref = row.get("source_ref")
        if not _nonempty(ref) or not _ID_RE.fullmatch(str(ref)):
            errors.append(f"{label}.source_ref is invalid")
        else:
            refs.append(str(ref))
        turn = row.get("turn_index")
        if not isinstance(turn, int) or isinstance(turn, bool) or turn < 1:
            errors.append(f"{label}.turn_index must be positive")
        else:
            turns.append(turn)
    if len(refs) != len(set(refs)):
        errors.append("source_index source refs must be unique")
    if turns != sorted(turns):
        errors.append("source_index turn indices must be ordered")
    return set(refs)


def _validate_evidence_field(
    value: object,
    *,
    label: str,
    source_refs: set[str],
    errors: list[str],
) -> None:
    row = _object(value, label=label, fields=_EVIDENCE_FIELDS, errors=errors)
    status = row.get("status")
    if status not in {"present", "not_stated", "unknown"}:
        errors.append(f"{label}.status is invalid")
    refs = _validate_ref_list(
        row.get("source_refs"),
        label=f"{label}.source_refs",
        allowed=source_refs,
        errors=errors,
    )
    if status == "present" and (not _nonempty(row.get("summary")) or not refs):
        errors.append(f"{label} present requires a summary and source refs")
    if status in {"not_stated", "unknown"} and (row.get("summary") or refs):
        errors.append(f"{label} {status} must preserve an explicit empty value")


def _validate_source_end(
    receipt: Mapping[str, Any], *, source_refs: set[str], errors: list[str]
) -> None:
    row = _object(
        receipt.get("source_end_state"),
        label="source_end_state",
        fields=_SOURCE_END_FIELDS,
        errors=errors,
    )
    if row.get("as_of_source_ref") not in source_refs:
        errors.append("source_end_state.as_of_source_ref is unknown")
    _validate_evidence_field(
        row.get("stated_next_action"),
        label="source_end_state.stated_next_action",
        source_refs=source_refs,
        errors=errors,
    )
    _validate_evidence_field(
        row.get("deadline_or_time_constraint"),
        label="source_end_state.deadline_or_time_constraint",
        source_refs=source_refs,
        errors=errors,
    )
    _strings(
        row.get("unresolved_items"),
        label="source_end_state.unresolved_items",
        errors=errors,
        maximum=12,
    )


def _walk_refs(
    value: object,
    *,
    source_refs: set[str],
    artifact_refs: set[str],
    errors: list[str],
    path: str = "receipt",
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "source_refs":
                _validate_ref_list(
                    child,
                    label=child_path,
                    allowed=source_refs,
                    errors=errors,
                )
            elif key in {"artifact_refs", "basis_artifact_refs"}:
                _validate_ref_list(
                    child,
                    label=child_path,
                    allowed=artifact_refs,
                    errors=errors,
                )
            else:
                _walk_refs(
                    child,
                    source_refs=source_refs,
                    artifact_refs=artifact_refs,
                    errors=errors,
                    path=child_path,
                )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_refs(
                child,
                source_refs=source_refs,
                artifact_refs=artifact_refs,
                errors=errors,
                path=f"{path}[{index}]",
            )


def _validate_graph(receipt: Mapping[str, Any], errors: list[str]) -> set[str]:
    row = _object(
        receipt.get("graph_attribution"),
        label="graph_attribution",
        fields=_GRAPH_FIELDS,
        errors=errors,
    )
    exposure = row.get("exposure_status")
    exposed = _ids(
        row.get("exposed_graph_pressure_ids"),
        label="graph_attribution.exposed_graph_pressure_ids",
        errors=errors,
    )
    if exposure in {"observed_indirect", "observed_direct", "observed_direct_and_indirect"} and not exposed:
        errors.append("observed graph exposure requires exact ids")
    if exposure == "not_observed" and exposed:
        errors.append("not_observed graph exposure must not contain ids")

    exact = _ids(
        row.get("exact_lineage_pressure_ids"),
        label="graph_attribution.exact_lineage_pressure_ids",
        errors=errors,
    )
    exact_status = row.get("exact_lineage_status")
    if (exact_status == "none" and exact) or (exact_status == "present" and not exact):
        errors.append("graph exact_lineage_status disagrees with exact ids")
    if exposure != "unknown" and not set(exact) <= set(exposed):
        errors.append("exact graph lineage ids must be exposed ids")

    dispositioned = _ids(
        row.get("individually_dispositioned_graph_pressure_ids"),
        label="graph_attribution.individually_dispositioned_graph_pressure_ids",
        errors=errors,
    )
    disposition_status = row.get("individual_disposition_status")
    if disposition_status == "none" and dispositioned:
        errors.append("graph disposition status none must not contain ids")
    if disposition_status == "partial" and (
        not dispositioned or set(dispositioned) == set(exact)
    ):
        errors.append("graph partial disposition must be a strict non-empty subset")
    if disposition_status == "complete" and (
        not exact or set(dispositioned) != set(exact)
    ):
        errors.append("graph complete disposition must equal exact lineage ids")

    causal = row.get("causal_contribution_status")
    scope = row.get("statement_scope")
    if scope == "exact_lineage_only" and not exact:
        errors.append("exact-lineage statement scope requires exact lineage")
    if scope == "causal_ablation" and causal not in {
        "directional_only",
        "identified_with_frozen_ablation",
    }:
        errors.append("causal statement scope requires a frozen ablation result")
    if causal in {"directional_only", "identified_with_frozen_ablation"} and (
        scope != "causal_ablation" or not exact or disposition_status != "complete"
    ):
        errors.append("causal graph claims require exact lineage and complete disposition")
    summary = str(row.get("summary", ""))
    if causal in {"not_tested", "not_identified"} and _ABSOLUTE_GRAPH_RE.search(summary):
        errors.append("graph summary overclaims absent influence")
    _strings(
        row.get("limits"),
        label="graph_attribution.limits",
        errors=errors,
        maximum=12,
        required=True,
    )
    return set(exposed)


def _validate_pressures(
    receipt: Mapping[str, Any],
    *,
    source_refs: set[str],
    graph_ids: set[str],
    errors: list[str],
) -> None:
    rows = _rows(
        receipt.get("pressure_accountability"),
        label="pressure_accountability",
        errors=errors,
    )
    if len(rows) > 12:
        errors.append("pressure_accountability exceeds maximum 12")
    ids: list[str] = []
    for index, value in enumerate(rows):
        label = f"pressure_accountability[{index}]"
        row = _object(value, label=label, fields=_PRESSURE_FIELDS, errors=errors)
        pressure_id = row.get("pressure_id")
        if not _nonempty(pressure_id) or not _ID_RE.fullmatch(str(pressure_id)):
            errors.append(f"{label}.pressure_id is invalid")
        else:
            ids.append(str(pressure_id))
        observed_id = str(row.get("observed_consumer_pressure_id", "")).strip()
        identity_status = row.get("identity_status")
        if observed_id and not _ID_RE.fullmatch(observed_id):
            errors.append(f"{label}.observed_consumer_pressure_id is invalid")
        if identity_status == "exact_match" and observed_id != pressure_id:
            errors.append(f"{label} exact identity must match pressure_id")
        if identity_status == "mismatch" and (
            not observed_id or observed_id == pressure_id
        ):
            errors.append(f"{label} identity mismatch requires a different observed id")
        if identity_status in {"not_returned", "not_applicable"} and observed_id:
            errors.append(f"{label} absent identity must not claim an observed id")
        if row.get("semantic_hearing_status") == "not_reached" and row.get(
            "consumer_disposition"
        ) not in {"not_reached", "not_applicable"}:
            errors.append(f"{label} not-reached hearing cannot claim a disposition")
        _validate_ref_list(
            row.get("source_refs"),
            label=f"{label}.source_refs",
            allowed=source_refs,
            errors=errors,
            required=True,
        )
        pressure_graph_ids = _ids(
            row.get("graph_pressure_ids"),
            label=f"{label}.graph_pressure_ids",
            errors=errors,
        )
        if row.get("origin") in {"graph", "mixed_with_graph"} and not pressure_graph_ids:
            errors.append(f"{label} graph or mixed origin requires graph ids")
        if not set(pressure_graph_ids) <= graph_ids:
            errors.append(f"{label}.graph_pressure_ids are not exposed graph ids")
        admission = row.get("admission_status")
        disposition = row.get("consumer_disposition")
        if admission != "admitted" and disposition not in {"not_reached", "not_applicable"}:
            errors.append(f"{label} non-admitted pressure cannot claim consumer use")
        visible = str(row.get("visible_effect", "")).strip()
        private = str(row.get("private_guardrail", "")).strip()
        if disposition == "used" and not (visible or private):
            errors.append(f"{label} used pressure requires an effect")
        if disposition == "private_guardrail" and (not private or visible):
            errors.append(f"{label} private guardrail disposition is inconsistent")
        if disposition in {"rejected", "deferred", "not_reached", "not_applicable"} and (
            visible or private
        ):
            errors.append(f"{label} non-use disposition must not claim an effect")
        if row.get("effect_consistency_status") == "inconsistent" and row.get(
            "semantic_hearing_status"
        ) == "not_reached":
            errors.append(f"{label} effect inconsistency requires a semantic hearing")
    if len(ids) != len(set(ids)):
        errors.append("pressure ids must be unique")


def _validate_comparison(receipt: Mapping[str, Any], errors: list[str]) -> None:
    row = _object(
        receipt.get("comparison_evidence"),
        label="comparison_evidence",
        fields=_COMPARISON_FIELDS,
        errors=errors,
    )
    outputs = _rows(
        row.get("anonymous_outputs"),
        label="comparison_evidence.anonymous_outputs",
        errors=errors,
    )
    mapping = _rows(
        row.get("reveal_mapping"),
        label="comparison_evidence.reveal_mapping",
        errors=errors,
    )
    if len(outputs) < 2:
        errors.append("comparison_evidence requires at least two anonymous outputs")
    if len(mapping) < 2:
        errors.append("comparison_evidence requires at least two reveal mappings")
    output_labels: list[str] = []
    for index, value in enumerate(outputs):
        label = f"comparison_evidence.anonymous_outputs[{index}]"
        item = _object(
            value, label=label, fields=_ANONYMOUS_OUTPUT_FIELDS, errors=errors
        )
        blind_label = item.get("blind_label")
        if not _nonempty(blind_label) or not _BLIND_LABEL_RE.fullmatch(str(blind_label)):
            errors.append(f"{label}.blind_label is invalid")
        else:
            output_labels.append(str(blind_label))
        if not isinstance(item.get("response"), Mapping):
            errors.append(f"{label}.response must be an object")
    mapping_labels: list[str] = []
    for index, value in enumerate(mapping):
        label = f"comparison_evidence.reveal_mapping[{index}]"
        item = _object(value, label=label, fields=_REVEAL_MAPPING_FIELDS, errors=errors)
        blind_label = item.get("blind_label")
        if not _nonempty(blind_label) or not _BLIND_LABEL_RE.fullmatch(str(blind_label)):
            errors.append(f"{label}.blind_label is invalid")
        else:
            mapping_labels.append(str(blind_label))
    if len(output_labels) != len(set(output_labels)):
        errors.append("anonymous output labels must be unique")
    if len(mapping_labels) != len(set(mapping_labels)):
        errors.append("reveal mapping labels must be unique")
    if set(output_labels) != set(mapping_labels):
        errors.append("anonymous output and reveal mapping labels must match")


def _validate_operability(receipt: Mapping[str, Any], errors: list[str]) -> None:
    row = _object(
        receipt.get("operability"),
        label="operability",
        fields=_OPERABILITY_FIELDS,
        errors=errors,
    )
    state = row.get("token_evidence_state")
    total = row.get("total_tokens")
    scope = str(row.get("token_scope", "")).strip()
    if state in {"complete", "partial"}:
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            errors.append("recorded token evidence requires a non-negative total")
        if not scope:
            errors.append("recorded token evidence requires an explicit scope")
    if state in {"unknown", "not_applicable"} and total is not None:
        errors.append("unknown or not-applicable token evidence must use null total")
    if state in {"unknown", "not_applicable"} and scope:
        errors.append("unknown or not-applicable token evidence must use empty scope")


def _validate_custody(receipt: Mapping[str, Any], errors: list[str]) -> None:
    row = _object(
        receipt.get("custody_boundary"),
        label="custody_boundary",
        fields=_CUSTODY_FIELDS,
        errors=errors,
    )
    support = _strings(
        row.get("artifacts_support"),
        label="custody_boundary.artifacts_support",
        errors=errors,
        maximum=12,
        required=True,
    )
    _strings(
        row.get("artifacts_do_not_establish"),
        label="custody_boundary.artifacts_do_not_establish",
        errors=errors,
        maximum=12,
        required=True,
    )
    if row.get("claim_level") != "recorded_artifact_integrity_only":
        errors.append("custody claim level is invalid")
    if any(_PROOF_RE.search(text) for text in [str(row.get("summary", "")), *support]):
        errors.append("custody support language must not use proof terminology")
    if row.get("external_execution_independently_verified") is not False:
        errors.append("external execution verification must remain false")
    if row.get("reasoning_quality_inferred") is not False:
        errors.append("reasoning quality inference must remain false")


def _validate_claims(receipt: Mapping[str, Any], errors: list[str]) -> None:
    boundary = receipt.get("claim_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("claim_boundary must be an object")
        return
    supported = _rows(boundary.get("supported"), label="claim_boundary.supported", errors=errors)
    forbidden = _rows(
        boundary.get("unsupported_or_forbidden"),
        label="claim_boundary.unsupported_or_forbidden",
        errors=errors,
    )
    ids: list[str] = []
    groups: list[list[str]] = []
    for label, rows in (
        ("claim_boundary.supported", supported),
        ("claim_boundary.unsupported_or_forbidden", forbidden),
    ):
        texts: list[str] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                errors.append(f"{label}[{index}] must be an object")
                continue
            claim_id = row.get("claim_id")
            text = row.get("text")
            if not _nonempty(claim_id) or not _ID_RE.fullmatch(str(claim_id)):
                errors.append(f"{label}[{index}].claim_id is invalid")
            else:
                ids.append(str(claim_id))
            if not _nonempty(text):
                errors.append(f"{label}[{index}].text is required")
            else:
                texts.append(_normal(str(text)))
        if len(texts) != len(set(texts)):
            errors.append(f"{label} contains duplicate claims")
        groups.append(texts)
    if len(ids) != len(set(ids)):
        errors.append("claim ids must be unique")
    if set(groups[0]) & set(groups[1]):
        errors.append("the same claim cannot be supported and forbidden")


def _validate_authorization(
    receipt: Mapping[str, Any], *, metadata: Mapping[str, Any], errors: list[str]
) -> None:
    row = _object(
        receipt.get("authorization_snapshot"),
        label="authorization_snapshot",
        fields=_AUTHORIZATION_FIELDS,
        errors=errors,
    )
    if row.get("scope_label") != "receipt_freeze_snapshot_not_current_state":
        errors.append("authorization snapshot scope is invalid")
    if row.get("as_of_event_id") != metadata.get("as_of_event_id"):
        errors.append("authorization event id must match receipt metadata")
    if row.get("as_of_utc") != metadata.get("frozen_at_utc"):
        errors.append("authorization time must match receipt metadata")
    if row.get("as_of_event_sequence") != metadata.get("as_of_event_sequence"):
        errors.append("authorization sequence must match receipt metadata")
    authorizations = row.get("authorizations")
    if not isinstance(authorizations, Mapping) or not authorizations or any(
        not _ID_RE.fullmatch(str(key)) or not isinstance(value, bool)
        for key, value in authorizations.items()
    ):
        errors.append("authorizations must map valid ids to booleans")
    future = _ids(
        row.get("future_events_not_covered"),
        label="authorization_snapshot.future_events_not_covered",
        errors=errors,
        required=True,
    )
    if not {"reader_call", "human_review"} <= set(future):
        errors.append("authorization snapshot must exclude reader_call and human_review")
    if row.get("post_reader_status_artifact_required") is not True:
        errors.append("post-reader status artifact must be required")


def _validate_questions(receipt: Mapping[str, Any], errors: list[str]) -> None:
    row = _object(
        receipt.get("questions"),
        label="questions",
        fields=_QUESTION_FIELDS,
        errors=errors,
    )
    groups = [
        _strings(
            row.get("case_domain_unknowns"),
            label="questions.case_domain_unknowns",
            errors=errors,
            maximum=12,
        ),
        _strings(
            row.get("reader_reconstruction_checks"),
            label="questions.reader_reconstruction_checks",
            errors=errors,
            maximum=8,
            required=True,
        ),
        _strings(
            row.get("human_product_review_questions"),
            label="questions.human_product_review_questions",
            errors=errors,
            maximum=3,
            required=True,
        ),
    ]
    normalized = [set(map(_normal, group)) for group in groups]
    if any(
        normalized[left] & normalized[right]
        for left in range(3)
        for right in range(left + 1, 3)
    ):
        errors.append("question categories must not overlap")


def _validate_non_claims(receipt: Mapping[str, Any], errors: list[str]) -> None:
    rows = _rows(receipt.get("non_claims"), label="non_claims", errors=errors)
    ids: list[str] = []
    texts: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"non_claims[{index}] must be an object")
            continue
        non_claim_id = row.get("non_claim_id")
        text = row.get("text")
        if not _nonempty(non_claim_id) or not _ID_RE.fullmatch(str(non_claim_id)):
            errors.append(f"non_claims[{index}].non_claim_id is invalid")
        else:
            ids.append(str(non_claim_id))
        if not _nonempty(text):
            errors.append(f"non_claims[{index}].text is required")
        else:
            texts.append(_normal(str(text)))
    if len(ids) != len(set(ids)):
        errors.append("non-claim ids must be unique")
    if len(texts) != len(set(texts)):
        errors.append("non-claim texts must be unique")
    missing = sorted(REQUIRED_NON_CLAIM_IDS - set(ids))
    if missing:
        errors.append(f"required non-claim ids are missing: {missing}")


def validate_reasoning_run_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if set(receipt) != _TOP_LEVEL_FIELDS:
        errors.append("top-level receipt fields are invalid")
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append("schema_version is invalid")
    if receipt.get("status") not in {"prospective_fixture", "frozen_for_reader"}:
        errors.append("receipt status is invalid")
    if not _nonempty(receipt.get("complete_conversation")):
        errors.append("complete_conversation is required")

    metadata = _validate_metadata(receipt, errors)
    artifact_refs = _validate_manifest(receipt, errors)
    source_refs = _validate_source(receipt, errors)
    _validate_source_end(receipt, source_refs=source_refs, errors=errors)
    _walk_refs(
        receipt,
        source_refs=source_refs,
        artifact_refs=artifact_refs,
        errors=errors,
    )
    graph_ids = _validate_graph(receipt, errors)
    _validate_pressures(
        receipt,
        source_refs=source_refs,
        graph_ids=graph_ids,
        errors=errors,
    )
    _validate_comparison(receipt, errors)
    _validate_operability(receipt, errors)
    _validate_custody(receipt, errors)
    _validate_claims(receipt, errors)
    _validate_authorization(receipt, metadata=metadata, errors=errors)
    _validate_questions(receipt, errors)
    _validate_non_claims(receipt, errors)

    if errors:
        raise ReasoningRunReceiptValidationError(errors)
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "cross_field_valid",
        "static_schema_contract": "docs/evals/reasoning-run-receipt-v2.json",
        "provider_calls": 0,
        "semantic_quality_scored": False,
        "runtime_change_authorized": False,
        "checks": {
            "source_end_action_explicit": True,
            "deadline_state_explicit": True,
            "authorization_snapshot_temporally_scoped": True,
            "question_audiences_separated": True,
            "anonymous_outputs_and_reveal_mapping_self_contained": True,
            "expected_and_observed_pressure_identity_separated": True,
            "partial_token_scope_explicit": True,
            "graph_claim_level_bounded": True,
            "custody_claim_level_bounded": True,
            "duplicates_rejected": True,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    value = json.loads(args.receipt.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ReasoningRunReceiptValidationError(["receipt must be an object"])
    print(json.dumps(validate_reasoning_run_receipt(value), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
