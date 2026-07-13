"""Provider-free canonical reasoning-process ledger construction.

This module imports already-reviewed conversation-event artifacts without
calling a model or re-reading prose for meaning. It preserves raw records,
source artifact identity, original state history, explicit scoped absence, and
deterministic custody. The frozen family projection uses only declared source
families; it is an index hint, not a relevance decision or semantic proof.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .conversation_state_candidates import SourceCatalog, build_source_catalog
from .reasoning_process_contracts import OBSERVATION_FAMILIES


LEDGER_SCHEMA_VERSION = "lolla.reasoning_process_ledger.v1"
REPORT_SCHEMA_VERSION = "lolla.reasoning_process_ledger_report.v1"
AGGREGATE_SCHEMA_VERSION = "lolla.reasoning_process_phase1_aggregate.v1"
LEDGER_STATUS = "provider_free_reviewed_import"
FAMILY_PROJECTION_STATUS = (
    "inherited_from_declared_source_family_not_semantically_validated"
)

SOURCE_FAMILY_PROJECTION = {
    ("harvest_event", "contributions"): "position_and_decision_trajectory",
    ("harvest_event", "thread_events"): "exploration_and_alternatives",
    ("harvest_event", "constraint_claims"): "evidence_and_assumption_discipline",
    ("synthesis", "positions"): "position_and_decision_trajectory",
    ("synthesis", "threads"): "uncertainty_and_unresolved_state",
    ("synthesis", "constraints"): "evidence_and_assumption_discipline",
}

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")
_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_NORMALIZED_TERMINAL_STATES = {
    "admitted",
    "quarantined_invalid_source",
    "quarantined_schema",
}
_SEMANTIC_STATUSES = {"supported", "mixed", "unclear", "not_observed"}

_TOP_FIELDS = {
    "schema_version",
    "status",
    "ledger_id",
    "source",
    "imports",
    "scope_outcomes",
    "observations",
    "failures",
    "metrics",
    "boundary",
}
_SOURCE_FIELDS = {
    "conversation_id",
    "source_path",
    "source_sha256",
    "message_count",
    "source_span_count",
    "authoritative_conversation_attached",
}
_IMPORT_FIELDS = {
    "artifact_id",
    "artifact_path",
    "artifact_sha256",
    "artifact_schema_version",
    "record_kind",
    "record_count",
    "scope_outcome_count",
    "status",
}
_SCOPE_FIELDS = {
    "scope_outcome_id",
    "source_artifact_id",
    "source_family",
    "scope_kind",
    "scope_id",
    "status",
    "candidate_count",
    "absence_is_observed",
    "ambiguity_is_observed",
    "raw_record_sha256",
    "raw_record",
}
_OBSERVATION_FIELDS = {
    "observation_id",
    "family",
    "family_projection_status",
    "interpretation",
    "semantic_status",
    "source_span_ids",
    "source_artifact_id",
    "source_record_id",
    "source_family",
    "raw_record_sha256",
    "raw_record",
    "provenance",
    "state_history",
    "terminal_state",
    "terminal_reason",
    "relations",
    "graph_routing_eligible",
}
_PROVENANCE_FIELDS = {
    "producer_kind",
    "producer_id",
    "call_id",
    "model",
    "prompt_sha256",
}
_STATE_FIELDS = {"state", "reason", "actor"}
_RELATION_FIELDS = {"relation_type", "target_observation_id", "authority"}
_FAILURE_FIELDS = {
    "failure_id",
    "source_artifact_id",
    "source_record_id",
    "observation_id",
    "stage",
    "code",
    "detail",
    "terminal",
}
_BOUNDARY_FIELDS = {
    "authoritative_conversation_referenced",
    "raw_import_records_preserved",
    "source_absence_and_ambiguity_preserved",
    "semantic_relevance_inferred_by_code",
    "family_projection_is_exclusive_gate",
    "metrics_treated_as_quality_evidence",
    "final_output_evaluated",
    "quality_score_included",
    "direct_graph_routing_allowed",
}


class ReasoningProcessLedgerError(ValueError):
    """Raised when Phase-1 source or ledger custody is invalid."""


def artifact_ref(*, artifact_id: str, path: str, raw_bytes: bytes) -> dict[str, str]:
    if not _ID_RE.fullmatch(artifact_id):
        raise ReasoningProcessLedgerError("artifact_id must be a stable lowercase ID")
    if not path or Path(path).is_absolute() or ".." in Path(path).parts:
        raise ReasoningProcessLedgerError("artifact path must be repo-relative")
    return {
        "artifact_id": artifact_id,
        "path": path,
        "sha256": "sha256:" + hashlib.sha256(raw_bytes).hexdigest(),
    }


def build_case_ledger(
    *,
    case_id: str,
    source_text: str,
    source_path: str,
    event_ledger: Mapping[str, Any],
    event_artifact: Mapping[str, str],
    synthesis_ledger: Mapping[str, Any],
    synthesis_artifact: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Import one reviewed case without semantic reclassification."""

    if not _ID_RE.fullmatch(case_id):
        raise ReasoningProcessLedgerError("case_id must be a stable lowercase ID")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    _validate_source_artifacts(
        case_id=case_id,
        source_path=source_path,
        catalog=catalog,
        event_ledger=event_ledger,
        synthesis_ledger=synthesis_ledger,
    )
    event_import_id = str(event_artifact["artifact_id"])
    synthesis_import_id = str(synthesis_artifact["artifact_id"])
    events = event_ledger.get("events")
    syntheses = synthesis_ledger.get("syntheses")
    if not isinstance(events, list) or not isinstance(syntheses, list):
        raise ReasoningProcessLedgerError("source ledgers must contain record arrays")

    known_spans = catalog.by_id()
    observations: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    event_observations: dict[str, dict[str, Any]] = {}

    for record in events:
        observation, failure = _import_event_record(
            record=record,
            artifact_id=event_import_id,
            artifact_path=str(event_artifact["path"]),
            known_spans=known_spans,
        )
        observations.append(observation)
        event_observations[observation["observation_id"]] = observation
        if failure:
            failures.append(failure)

    for record in syntheses:
        observation, failure = _import_synthesis_record(
            record=record,
            artifact_id=synthesis_import_id,
            artifact_path=str(synthesis_artifact["path"]),
            event_observations=event_observations,
        )
        observations.append(observation)
        if failure:
            failures.append(failure)

    scope_outcomes = _import_scope_outcomes(
        event_ledger=event_ledger,
        event_artifact_id=event_import_id,
        synthesis_ledger=synthesis_ledger,
        synthesis_artifact_id=synthesis_import_id,
    )
    imports = [
        _import_summary(
            artifact=event_artifact,
            payload=event_ledger,
            record_kind="harvest_event",
            record_count=len(events),
            scope_outcome_count=sum(
                item["source_artifact_id"] == event_import_id
                for item in scope_outcomes
            ),
        ),
        _import_summary(
            artifact=synthesis_artifact,
            payload=synthesis_ledger,
            record_kind="synthesis",
            record_count=len(syntheses),
            scope_outcome_count=sum(
                item["source_artifact_id"] == synthesis_import_id
                for item in scope_outcomes
            ),
        ),
    ]
    source_hash = "sha256:" + catalog.source_sha256
    ledger: dict[str, Any] = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "status": LEDGER_STATUS,
        "ledger_id": f"reasoning-process-ledger-{case_id}",
        "source": {
            "conversation_id": case_id,
            "source_path": source_path,
            "source_sha256": source_hash,
            "message_count": catalog.message_count,
            "source_span_count": len(catalog.spans),
            "authoritative_conversation_attached": True,
        },
        "imports": imports,
        "scope_outcomes": scope_outcomes,
        "observations": observations,
        "failures": failures,
        "metrics": _compute_metrics(
            observations=observations,
            failures=failures,
            scope_outcomes=scope_outcomes,
            import_count=len(imports),
        ),
        "boundary": {
            "authoritative_conversation_referenced": True,
            "raw_import_records_preserved": True,
            "source_absence_and_ambiguity_preserved": True,
            "semantic_relevance_inferred_by_code": False,
            "family_projection_is_exclusive_gate": False,
            "metrics_treated_as_quality_evidence": False,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }
    validation = validate_case_ledger(
        ledger,
        known_span_ids=known_spans,
        expected_source_sha256=source_hash,
    )
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "provider_free_pass" if not failures else "provider_free_quarantined",
        "case_id": case_id,
        "ledger_validation": validation,
        "metrics": ledger["metrics"],
        "known_gaps": _known_family_gaps(observations),
        "provider_calls": 0,
        "embedding_calls": 0,
        "evaluator_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "non_claims": [
            "reviewed_fixture_import_is_not_automatic_extraction_quality",
            "family_projection_is_not_semantic_placement_proof",
            "ledger_breadth_is_not_reasoning_quality",
            "no_bounded_view_or_process_assessment_was_generated",
            "no_graph_or_runtime_integration_authority",
        ],
    }
    return ledger, report


def build_phase1_aggregate(case_reports: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    reports = list(case_reports)
    totals: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    terminal_counts: Counter[str] = Counter()
    gaps: set[str] = set()
    for report in reports:
        metrics = report.get("metrics", {})
        if not isinstance(metrics, Mapping):
            raise ReasoningProcessLedgerError("case report metrics are missing")
        for field in (
            "observation_count",
            "scope_outcome_count",
            "failure_count",
            "source_span_reference_count",
            "unique_source_span_reference_count",
            "relation_count",
            "raw_record_utf8_bytes",
        ):
            totals[field] += int(metrics.get(field, 0))
        family_counts.update(metrics.get("counts_by_family", {}))
        terminal_counts.update(metrics.get("counts_by_terminal_state", {}))
        gaps.update(report.get("known_gaps", []))
    all_passed = all(report.get("status") == "provider_free_pass" for report in reports)
    return {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "status": "provider_free_pass" if all_passed else "provider_free_quarantined",
        "case_count": len(reports),
        "case_ids": [str(report.get("case_id", "")) for report in reports],
        "totals": dict(sorted(totals.items())),
        "counts_by_family": dict(sorted(family_counts.items())),
        "counts_by_terminal_state": dict(sorted(terminal_counts.items())),
        "known_family_gaps": sorted(gaps),
        "source_and_candidate_custody_complete": all(
            bool(report.get("ledger_validation", {}).get("candidate_terminal_custody_complete"))
            for report in reports
        ),
        "raw_import_records_preserved": all(
            bool(report.get("ledger_validation", {}).get("raw_import_records_preserved"))
            for report in reports
        ),
        "direct_graph_seed_count": 0,
        "provider_calls": 0,
        "embedding_calls": 0,
        "evaluator_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "next_phase_authorized": all_passed,
        "paid_calls_authorized": False,
        "non_claims": [
            "phase1_pass_is_not_semantic_extraction_quality",
            "phase1_pass_is_not_bounded_view_quality",
            "phase1_pass_is_not_reasoning_process_quality",
            "phase1_pass_is_not_final_output_quality",
            "phase1_pass_is_not_graph_or_runtime_authority",
        ],
    }


def validate_case_ledger(
    ledger: Mapping[str, Any],
    *,
    known_span_ids: Iterable[str],
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    _exact_fields(ledger, _TOP_FIELDS, "ledger", errors)
    if errors:
        raise ReasoningProcessLedgerError("; ".join(errors))
    if ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        errors.append("ledger.schema_version is invalid")
    if ledger.get("status") != LEDGER_STATUS:
        errors.append("ledger.status is invalid")
    _require_id(ledger.get("ledger_id"), "ledger.ledger_id", errors)

    source = ledger.get("source")
    if not isinstance(source, Mapping):
        errors.append("ledger.source must be an object")
    else:
        _exact_fields(source, _SOURCE_FIELDS, "ledger.source", errors)
        _require_id(source.get("conversation_id"), "ledger.source.conversation_id", errors)
        _require_text(source.get("source_path"), "ledger.source.source_path", errors)
        _require_sha(source.get("source_sha256"), "ledger.source.source_sha256", errors)
        if expected_source_sha256 and source.get("source_sha256") != expected_source_sha256:
            errors.append("ledger source hash does not match custody")
        for field in ("message_count", "source_span_count"):
            if not _positive_int(source.get(field)):
                errors.append(f"ledger.source.{field} must be a positive integer")
        if source.get("authoritative_conversation_attached") is not True:
            errors.append("authoritative conversation must remain attached")

    imports = ledger.get("imports")
    if not isinstance(imports, list) or not imports:
        errors.append("ledger.imports must be a non-empty array")
        imports = []
    import_ids: list[str] = []
    for index, item in enumerate(imports):
        prefix = f"ledger.imports[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _exact_fields(item, _IMPORT_FIELDS, prefix, errors)
        _require_id(item.get("artifact_id"), f"{prefix}.artifact_id", errors)
        import_ids.append(str(item.get("artifact_id")))
        _require_repo_path(item.get("artifact_path"), f"{prefix}.artifact_path", errors)
        _require_sha(item.get("artifact_sha256"), f"{prefix}.artifact_sha256", errors)
        _require_text(item.get("artifact_schema_version"), f"{prefix}.artifact_schema_version", errors)
        if item.get("record_kind") not in {"harvest_event", "synthesis"}:
            errors.append(f"{prefix}.record_kind is invalid")
        for field in ("record_count", "scope_outcome_count"):
            if not _nonnegative_int(item.get(field)):
                errors.append(f"{prefix}.{field} must be a nonnegative integer")
        if item.get("status") != "imported_complete":
            errors.append(f"{prefix}.status must be imported_complete")
    if len(import_ids) != len(set(import_ids)):
        errors.append("import artifact IDs must be unique")
    import_id_set = set(import_ids)

    known_spans = set(known_span_ids)
    observations = ledger.get("observations")
    if not isinstance(observations, list):
        errors.append("ledger.observations must be an array")
        observations = []
    observation_ids: list[str] = []
    observation_failure_required: set[str] = set()
    for index, observation in enumerate(observations):
        prefix = f"ledger.observations[{index}]"
        if not isinstance(observation, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _exact_fields(observation, _OBSERVATION_FIELDS, prefix, errors)
        if set(observation) != _OBSERVATION_FIELDS:
            continue
        observation_id = str(observation.get("observation_id", ""))
        _require_id(observation_id, f"{prefix}.observation_id", errors)
        observation_ids.append(observation_id)
        source_artifact_id = str(observation.get("source_artifact_id", ""))
        if source_artifact_id not in import_id_set:
            errors.append(f"{prefix}.source_artifact_id is unknown")
        source_record_id = observation.get("source_record_id")
        _require_id(source_record_id, f"{prefix}.source_record_id", errors)
        source_family = str(observation.get("source_family", ""))
        _require_text(source_family, f"{prefix}.source_family", errors)
        record_kind = _record_kind_for_artifact(imports, source_artifact_id)
        expected_family = SOURCE_FAMILY_PROJECTION.get((record_kind, source_family))
        if observation.get("family") != expected_family:
            errors.append(f"{prefix}.family does not match the frozen source-family projection")
        if observation.get("family_projection_status") != FAMILY_PROJECTION_STATUS:
            errors.append(f"{prefix}.family_projection_status is invalid")
        _require_text(observation.get("interpretation"), f"{prefix}.interpretation", errors)
        if observation.get("semantic_status") not in _SEMANTIC_STATUSES:
            errors.append(f"{prefix}.semantic_status is invalid")
        _require_sha(observation.get("raw_record_sha256"), f"{prefix}.raw_record_sha256", errors)
        if not isinstance(observation.get("raw_record"), Mapping):
            errors.append(f"{prefix}.raw_record must be an object")
        elif observation.get("raw_record_sha256") != _prefixed_json_hash(observation["raw_record"]):
            errors.append(f"{prefix}.raw_record hash mismatch")
        source_span_ids = _string_array(
            observation.get("source_span_ids"), f"{prefix}.source_span_ids", errors
        )
        terminal_state = observation.get("terminal_state")
        if terminal_state not in _NORMALIZED_TERMINAL_STATES:
            errors.append(f"{prefix}.terminal_state is invalid")
        if terminal_state == "admitted":
            if not source_span_ids:
                errors.append(f"{prefix} admitted observation requires source spans")
            if any(span_id not in known_spans for span_id in source_span_ids):
                errors.append(f"{prefix} admitted observation references an unknown source span")
        else:
            observation_failure_required.add(observation_id)
        _require_text(observation.get("terminal_reason"), f"{prefix}.terminal_reason", errors)
        _validate_provenance(observation.get("provenance"), prefix, errors)
        _validate_state_history(observation.get("state_history"), terminal_state, prefix, errors)
        _validate_relations(observation.get("relations"), prefix, errors)
        if observation.get("graph_routing_eligible") is not False:
            errors.append(f"{prefix}.graph_routing_eligible must be false")
    if len(observation_ids) != len(set(observation_ids)):
        errors.append("observation IDs must be unique")
    observation_id_set = set(observation_ids)
    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            continue
        for relation in observation.get("relations", []):
            if not isinstance(relation, Mapping):
                continue
            target = relation.get("target_observation_id")
            if target not in observation_id_set:
                errors.append(f"ledger.observations[{index}] relation target is unknown")
            if target == observation.get("observation_id"):
                errors.append(f"ledger.observations[{index}] relation cannot target itself")

    scope_outcomes = ledger.get("scope_outcomes")
    if not isinstance(scope_outcomes, list):
        errors.append("ledger.scope_outcomes must be an array")
        scope_outcomes = []
    scope_ids: list[str] = []
    for index, outcome in enumerate(scope_outcomes):
        prefix = f"ledger.scope_outcomes[{index}]"
        if not isinstance(outcome, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _exact_fields(outcome, _SCOPE_FIELDS, prefix, errors)
        if set(outcome) != _SCOPE_FIELDS:
            continue
        _require_id(outcome.get("scope_outcome_id"), f"{prefix}.scope_outcome_id", errors)
        scope_ids.append(str(outcome.get("scope_outcome_id")))
        if outcome.get("source_artifact_id") not in import_id_set:
            errors.append(f"{prefix}.source_artifact_id is unknown")
        _require_text(outcome.get("source_family"), f"{prefix}.source_family", errors)
        if outcome.get("scope_kind") not in {"turn_pair_window", "conversation"}:
            errors.append(f"{prefix}.scope_kind is invalid")
        _require_id(outcome.get("scope_id"), f"{prefix}.scope_id", errors)
        if outcome.get("status") not in {"supported", "unclear", "not_found"}:
            errors.append(f"{prefix}.status is invalid")
        if not _nonnegative_int(outcome.get("candidate_count")):
            errors.append(f"{prefix}.candidate_count must be nonnegative")
        for field in ("absence_is_observed", "ambiguity_is_observed"):
            if not isinstance(outcome.get(field), bool):
                errors.append(f"{prefix}.{field} must be boolean")
        if outcome.get("status") == "not_found" and outcome.get("absence_is_observed") is not True:
            errors.append(f"{prefix} not_found must preserve observed absence")
        if outcome.get("status") == "unclear" and outcome.get("ambiguity_is_observed") is not True:
            errors.append(f"{prefix} unclear must preserve observed ambiguity")
        _require_sha(outcome.get("raw_record_sha256"), f"{prefix}.raw_record_sha256", errors)
        if not isinstance(outcome.get("raw_record"), Mapping):
            errors.append(f"{prefix}.raw_record must be an object")
        elif outcome.get("raw_record_sha256") != _prefixed_json_hash(outcome["raw_record"]):
            errors.append(f"{prefix}.raw_record hash mismatch")
    if len(scope_ids) != len(set(scope_ids)):
        errors.append("scope outcome IDs must be unique")

    failures = ledger.get("failures")
    if not isinstance(failures, list):
        errors.append("ledger.failures must be an array")
        failures = []
    failed_observation_ids: set[str] = set()
    for index, failure in enumerate(failures):
        prefix = f"ledger.failures[{index}]"
        if not isinstance(failure, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _exact_fields(failure, _FAILURE_FIELDS, prefix, errors)
        if set(failure) != _FAILURE_FIELDS:
            continue
        _require_id(failure.get("failure_id"), f"{prefix}.failure_id", errors)
        if failure.get("source_artifact_id") not in import_id_set:
            errors.append(f"{prefix}.source_artifact_id is unknown")
        _require_id(failure.get("source_record_id"), f"{prefix}.source_record_id", errors)
        observation_id = str(failure.get("observation_id", ""))
        if observation_id not in observation_id_set:
            errors.append(f"{prefix}.observation_id is unknown")
        failed_observation_ids.add(observation_id)
        for field in ("stage", "code", "detail"):
            _require_text(failure.get(field), f"{prefix}.{field}", errors)
        if failure.get("terminal") is not True:
            errors.append(f"{prefix}.terminal must be true")
    if failed_observation_ids != observation_failure_required:
        errors.append("every quarantined observation must have exactly one terminal failure")

    _validate_import_counts(imports, observations, scope_outcomes, errors)
    expected_metrics = _compute_metrics(
        observations=observations,
        failures=failures,
        scope_outcomes=scope_outcomes,
        import_count=len(imports),
    )
    if ledger.get("metrics") != expected_metrics:
        errors.append("ledger.metrics do not match deterministic recomputation")
    _validate_boundary(ledger.get("boundary"), errors)
    if errors:
        raise ReasoningProcessLedgerError("; ".join(errors))
    return {
        "status": "structurally_valid_provider_free_ledger",
        "observation_count": len(observations),
        "scope_outcome_count": len(scope_outcomes),
        "failure_count": len(failures),
        "candidate_terminal_custody_complete": True,
        "raw_import_records_preserved": True,
        "source_absence_and_ambiguity_preserved": True,
        "semantic_correctness_validated": False,
        "family_placement_validated": False,
        "final_output_evaluated": False,
        "quality_score_emitted": False,
        "direct_graph_seed_count": 0,
        "provider_calls": 0,
        "runtime_integration_authorized": False,
    }


def load_case_inputs(
    *,
    root: Path,
    case_id: str,
    source_path: str,
    event_ledger_path: str,
    synthesis_ledger_path: str,
) -> tuple[str, Mapping[str, Any], dict[str, str], Mapping[str, Any], dict[str, str]]:
    source = (root / source_path).read_text(encoding="utf-8")
    event_bytes = (root / event_ledger_path).read_bytes()
    synthesis_bytes = (root / synthesis_ledger_path).read_bytes()
    return (
        source,
        json.loads(event_bytes),
        artifact_ref(artifact_id=f"{case_id}-events", path=event_ledger_path, raw_bytes=event_bytes),
        json.loads(synthesis_bytes),
        artifact_ref(
            artifact_id=f"{case_id}-syntheses",
            path=synthesis_ledger_path,
            raw_bytes=synthesis_bytes,
        ),
    )


def _validate_source_artifacts(
    *,
    case_id: str,
    source_path: str,
    catalog: SourceCatalog,
    event_ledger: Mapping[str, Any],
    synthesis_ledger: Mapping[str, Any],
) -> None:
    errors: list[str] = []
    if event_ledger.get("case_id") != case_id or synthesis_ledger.get("case_id") != case_id:
        errors.append("source artifact case_id mismatch")
    source = event_ledger.get("source")
    if not isinstance(source, Mapping):
        errors.append("event ledger source custody is missing")
    else:
        if source.get("path") != source_path:
            errors.append("event ledger source path mismatch")
        if source.get("sha256") != catalog.source_sha256:
            errors.append("event ledger source hash mismatch")
        if source.get("message_count") != catalog.message_count:
            errors.append("event ledger source message count mismatch")
    if synthesis_ledger.get("event_ledger_sha256") != _unprefixed_json_hash(event_ledger):
        errors.append("synthesis ledger event-ledger hash mismatch")
    if errors:
        raise ReasoningProcessLedgerError("; ".join(errors))


def _import_event_record(
    *,
    record: object,
    artifact_id: str,
    artifact_path: str,
    known_spans: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    issues: list[str] = []
    row = dict(record) if isinstance(record, Mapping) else {}
    record_id = str(row.get("event_id", ""))
    family = str(row.get("family", ""))
    snapshot = row.get("event_snapshot")
    raw_proposal = row.get("raw_proposal")
    if not _ID_RE.fullmatch(record_id):
        issues.append("record_id_invalid")
        record_id = "invalid-event-" + _json_hash(row)[:12]
    projected_family = SOURCE_FAMILY_PROJECTION.get(("harvest_event", family))
    if projected_family is None:
        issues.append("source_family_unknown")
        projected_family = "exploration_and_alternatives"
    if not isinstance(snapshot, Mapping):
        issues.append("event_snapshot_missing")
        snapshot = {}
    if not isinstance(raw_proposal, Mapping):
        issues.append("raw_proposal_missing")
    elif row.get("raw_proposal_sha256") != _unprefixed_json_hash(raw_proposal):
        issues.append("raw_proposal_hash_mismatch")
    validation_issues = row.get("validation_issues")
    if validation_issues not in ([], None):
        issues.append("source_validation_issues_present")
    source_span_ids, source_issues = _validated_event_source_spans(snapshot, known_spans)
    issues.extend(source_issues)
    interpretation = _event_interpretation(family, snapshot)
    if not interpretation:
        issues.append("interpretation_missing")
        interpretation = f"Invalid imported event {record_id}"
    terminal_state = (
        "admitted"
        if not issues
        else "quarantined_invalid_source"
        if any("source" in issue or "span" in issue for issue in issues)
        else "quarantined_schema"
    )
    raw_record = _json_copy(row)
    observation = {
        "observation_id": record_id,
        "family": projected_family,
        "family_projection_status": FAMILY_PROJECTION_STATUS,
        "interpretation": interpretation,
        "semantic_status": "supported" if not issues else "unclear",
        "source_span_ids": source_span_ids,
        "source_artifact_id": artifact_id,
        "source_record_id": record_id,
        "source_family": family or "unknown",
        "raw_record_sha256": _prefixed_json_hash(raw_record),
        "raw_record": raw_record,
        "provenance": _fixture_provenance(artifact_path),
        "state_history": _preserve_state_history(
            row.get("state_history"), terminal_state, issues
        ),
        "terminal_state": terminal_state,
        "terminal_reason": (
            "source artifact, raw proposal, and exact source custody validated"
            if not issues
            else "import quarantined: " + ",".join(sorted(set(issues)))
        ),
        "relations": [],
        "graph_routing_eligible": False,
    }
    return observation, _failure_for(observation, issues) if issues else None


def _import_synthesis_record(
    *,
    record: object,
    artifact_id: str,
    artifact_path: str,
    event_observations: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    issues: list[str] = []
    row = dict(record) if isinstance(record, Mapping) else {}
    record_id = str(row.get("synthesis_id", ""))
    family = str(row.get("family", ""))
    snapshot = row.get("event_snapshot")
    raw_proposal = row.get("raw_proposal")
    if not _ID_RE.fullmatch(record_id):
        issues.append("record_id_invalid")
        record_id = "invalid-synthesis-" + _json_hash(row)[:12]
    projected_family = SOURCE_FAMILY_PROJECTION.get(("synthesis", family))
    if projected_family is None:
        issues.append("source_family_unknown")
        projected_family = "uncertainty_and_unresolved_state"
    if not isinstance(snapshot, Mapping):
        issues.append("event_snapshot_missing")
        snapshot = {}
    if not isinstance(raw_proposal, Mapping):
        issues.append("raw_proposal_missing")
    elif row.get("raw_proposal_sha256") != _unprefixed_json_hash(raw_proposal):
        issues.append("raw_proposal_hash_mismatch")
    validation_issues = row.get("validation_issues")
    if validation_issues not in ([], None):
        issues.append("source_validation_issues_present")
    event_ids = _synthesis_event_ids(family, snapshot)
    if not event_ids:
        issues.append("synthesis_event_lineage_missing")
    source_span_ids: list[str] = []
    for event_id in event_ids:
        event = event_observations.get(event_id)
        if event is None:
            issues.append("synthesis_event_reference_unknown")
            continue
        if event.get("terminal_state") != "admitted":
            issues.append("synthesis_event_reference_quarantined")
        for span_id in event.get("source_span_ids", []):
            if span_id not in source_span_ids:
                source_span_ids.append(span_id)
    interpretation = str(snapshot.get("text", "")).strip()
    if not interpretation:
        issues.append("interpretation_missing")
        interpretation = f"Invalid imported synthesis {record_id}"
    terminal_state = "admitted" if not issues else "quarantined_schema"
    raw_record = _json_copy(row)
    observation = {
        "observation_id": record_id,
        "family": projected_family,
        "family_projection_status": FAMILY_PROJECTION_STATUS,
        "interpretation": interpretation,
        "semantic_status": "supported" if not issues else "unclear",
        "source_span_ids": source_span_ids,
        "source_artifact_id": artifact_id,
        "source_record_id": record_id,
        "source_family": family or "unknown",
        "raw_record_sha256": _prefixed_json_hash(raw_record),
        "raw_record": raw_record,
        "provenance": _fixture_provenance(artifact_path),
        "state_history": _preserve_synthesis_state(row, terminal_state, issues),
        "terminal_state": terminal_state,
        "terminal_reason": (
            "source artifact, raw proposal, event lineage, and exact source custody validated"
            if not issues
            else "import quarantined: " + ",".join(sorted(set(issues)))
        ),
        "relations": [
            {
                "relation_type": "develops",
                "target_observation_id": event_id,
                "authority": "source_reviewer",
            }
            for event_id in event_ids
            if event_id in event_observations
        ],
        "graph_routing_eligible": False,
    }
    return observation, _failure_for(observation, issues) if issues else None


def _import_scope_outcomes(
    *,
    event_ledger: Mapping[str, Any],
    event_artifact_id: str,
    synthesis_ledger: Mapping[str, Any],
    synthesis_artifact_id: str,
) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    harvest = event_ledger.get("family_window_outcomes", [])
    if not isinstance(harvest, list):
        raise ReasoningProcessLedgerError("event family_window_outcomes must be an array")
    for row in harvest:
        if not isinstance(row, Mapping):
            raise ReasoningProcessLedgerError("harvest scope outcome must be an object")
        raw = _json_copy(row)
        family = str(row.get("family", ""))
        window_id = str(row.get("window_id", ""))
        outcomes.append(
            {
                "scope_outcome_id": f"scope-{family}-{window_id}",
                "source_artifact_id": event_artifact_id,
                "source_family": family,
                "scope_kind": "turn_pair_window",
                "scope_id": window_id,
                "status": row.get("status"),
                "candidate_count": int(row.get("event_count", 0)),
                "absence_is_observed": row.get("absence_is_observed"),
                "ambiguity_is_observed": row.get("ambiguity_is_observed"),
                "raw_record_sha256": _prefixed_json_hash(raw),
                "raw_record": raw,
            }
        )
    synthesis = synthesis_ledger.get("family_outcomes", {})
    if not isinstance(synthesis, Mapping):
        raise ReasoningProcessLedgerError("synthesis family_outcomes must be an object")
    for family, row in synthesis.items():
        if not isinstance(row, Mapping):
            raise ReasoningProcessLedgerError("synthesis scope outcome must be an object")
        raw = _json_copy(row)
        outcomes.append(
            {
                "scope_outcome_id": f"scope-{family}-conversation",
                "source_artifact_id": synthesis_artifact_id,
                "source_family": str(family),
                "scope_kind": "conversation",
                "scope_id": "conversation",
                "status": row.get("status"),
                "candidate_count": int(row.get("candidate_count", 0)),
                "absence_is_observed": row.get("absence_is_observed"),
                "ambiguity_is_observed": row.get("ambiguity_is_observed"),
                "raw_record_sha256": _prefixed_json_hash(raw),
                "raw_record": raw,
            }
        )
    return outcomes


def _import_summary(
    *,
    artifact: Mapping[str, str],
    payload: Mapping[str, Any],
    record_kind: str,
    record_count: int,
    scope_outcome_count: int,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact["artifact_id"],
        "artifact_path": artifact["path"],
        "artifact_sha256": artifact["sha256"],
        "artifact_schema_version": str(payload.get("schema_version", "")),
        "record_kind": record_kind,
        "record_count": record_count,
        "scope_outcome_count": scope_outcome_count,
        "status": "imported_complete",
    }


def _validated_event_source_spans(
    snapshot: Mapping[str, Any], known_spans: Mapping[str, Any]
) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    resolved = snapshot.get("resolved_source")
    if not isinstance(resolved, list) or not resolved:
        return [], ["resolved_source_missing"]
    span_ids: list[str] = []
    for row in resolved:
        if not isinstance(row, Mapping):
            issues.append("resolved_source_shape_invalid")
            continue
        span_id = str(row.get("span_id", ""))
        span = known_spans.get(span_id)
        if span is None:
            issues.append("source_span_unknown")
            continue
        if row.get("text") != span.text:
            issues.append("source_text_mismatch")
        if row.get("speaker") != span.speaker:
            issues.append("source_speaker_mismatch")
        if row.get("turn_index") != span.turn_index:
            issues.append("source_turn_mismatch")
        if span_id not in span_ids:
            span_ids.append(span_id)
    evidence_ids = _collect_span_ids(snapshot.get("evidence"))
    if sorted(evidence_ids) != sorted(span_ids):
        issues.append("source_evidence_resolution_mismatch")
    return span_ids, issues


def _event_interpretation(family: str, snapshot: Mapping[str, Any]) -> str:
    field = {
        "contributions": "position_fragment",
        "thread_events": "thread_hint",
        "constraint_claims": "claim_text",
    }.get(family, "")
    return str(snapshot.get(field, "")).strip() if field else ""


def _synthesis_event_ids(family: str, snapshot: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    if family == "positions":
        candidates = [
            row.get("event_id")
            for row in snapshot.get("contributions", [])
            if isinstance(row, Mapping)
        ]
    elif family == "threads":
        candidates = snapshot.get("event_ids", [])
    elif family == "constraints":
        candidates = snapshot.get("claim_event_ids", [])
    else:
        candidates = []
    if not isinstance(candidates, list):
        return []
    for value in candidates:
        if isinstance(value, str) and value and value not in values:
            values.append(value)
    return values


def _fixture_provenance(artifact_path: str) -> dict[str, str]:
    return {
        "producer_kind": "fixture",
        "producer_id": "phase-a-v2-source-reviewed",
        "call_id": artifact_path,
        "model": "",
        "prompt_sha256": "",
    }


def _preserve_state_history(
    source_history: object, terminal_state: str, issues: list[str]
) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    if isinstance(source_history, list):
        for row in source_history:
            if isinstance(row, Mapping):
                history.append(
                    {
                        "state": str(row.get("state", "unknown_source_state")),
                        "reason": str(row.get("reason", "source reason missing")),
                        "actor": str(row.get("actor", "source actor missing")),
                    }
                )
    if not history:
        history.append(
            {
                "state": "proposed",
                "reason": "source state history missing during import",
                "actor": "deterministic_importer",
            }
        )
        issues.append("source_state_history_missing")
    history.append(
        {
            "state": terminal_state,
            "reason": "provider-free canonical ledger import",
            "actor": "deterministic_importer",
        }
    )
    return history


def _preserve_synthesis_state(
    row: Mapping[str, Any], terminal_state: str, issues: list[str]
) -> list[dict[str, str]]:
    source_terminal = str(row.get("terminal_state", ""))
    if not source_terminal:
        issues.append("source_terminal_state_missing")
        source_terminal = "unknown_source_state"
    return [
        {
            "state": "proposed",
            "reason": "recorded from source-reviewed synthesis artifact",
            "actor": "semantic_synthesizer_or_reviewed_fixture",
        },
        {
            "state": source_terminal,
            "reason": str(row.get("terminal_reason", "source reason missing")),
            "actor": "semantic_synthesizer_or_reviewed_fixture",
        },
        {
            "state": terminal_state,
            "reason": "provider-free canonical ledger import",
            "actor": "deterministic_importer",
        },
    ]


def _failure_for(observation: Mapping[str, Any], issues: list[str]) -> dict[str, Any]:
    observation_id = str(observation["observation_id"])
    invalid_source = any("source" in issue or "span" in issue for issue in issues)
    return {
        "failure_id": f"failure-{observation_id}",
        "source_artifact_id": observation["source_artifact_id"],
        "source_record_id": observation["source_record_id"],
        "observation_id": observation_id,
        "stage": "provider_free_import",
        "code": "RP1" if invalid_source else "RP0",
        "detail": ",".join(sorted(set(issues))),
        "terminal": True,
    }


def _compute_metrics(
    *,
    observations: Iterable[Mapping[str, Any]],
    failures: Iterable[Mapping[str, Any]],
    scope_outcomes: Iterable[Mapping[str, Any]],
    import_count: int,
) -> dict[str, Any]:
    rows = list(observations)
    failure_rows = list(failures)
    scope_rows = list(scope_outcomes)
    family_counts = Counter(str(row.get("family", "")) for row in rows)
    source_family_counts = Counter(str(row.get("source_family", "")) for row in rows)
    terminal_counts = Counter(str(row.get("terminal_state", "")) for row in rows)
    span_ids = [
        str(span_id)
        for row in rows
        for span_id in row.get("source_span_ids", [])
    ]
    raw_bytes = sum(
        len(_canonical_json(row.get("raw_record", {})).encode("utf-8"))
        for row in rows
    ) + sum(
        len(_canonical_json(row.get("raw_record", {})).encode("utf-8"))
        for row in scope_rows
    )
    return {
        "source_artifact_count": import_count,
        "observation_count": len(rows),
        "scope_outcome_count": len(scope_rows),
        "observed_absence_count": sum(
            row.get("absence_is_observed") is True for row in scope_rows
        ),
        "observed_ambiguity_count": sum(
            row.get("ambiguity_is_observed") is True for row in scope_rows
        ),
        "failure_count": len(failure_rows),
        "counts_by_family": dict(sorted(family_counts.items())),
        "counts_by_source_family": dict(sorted(source_family_counts.items())),
        "counts_by_terminal_state": dict(sorted(terminal_counts.items())),
        "source_span_reference_count": len(span_ids),
        "unique_source_span_reference_count": len(set(span_ids)),
        "relation_count": sum(len(row.get("relations", [])) for row in rows),
        "raw_record_utf8_bytes": raw_bytes,
        "candidate_terminal_custody_complete": len(rows)
        == sum(terminal_counts.values()),
        "raw_import_records_preserved": all(
            isinstance(row.get("raw_record"), Mapping) for row in rows
        ),
        "direct_graph_seed_count": sum(
            row.get("graph_routing_eligible") is not False for row in rows
        ),
    }


def _known_family_gaps(observations: Iterable[Mapping[str, Any]]) -> list[str]:
    present = {str(row.get("family", "")) for row in observations}
    return sorted(set(OBSERVATION_FAMILIES) - present)


def _validate_import_counts(
    imports: Iterable[Mapping[str, Any]],
    observations: Iterable[Mapping[str, Any]],
    scope_outcomes: Iterable[Mapping[str, Any]],
    errors: list[str],
) -> None:
    observation_counts = Counter(
        str(row.get("source_artifact_id", "")) for row in observations
    )
    scope_counts = Counter(
        str(row.get("source_artifact_id", "")) for row in scope_outcomes
    )
    for item in imports:
        artifact_id = str(item.get("artifact_id", ""))
        if item.get("record_count") != observation_counts[artifact_id]:
            errors.append(f"import {artifact_id} record_count does not match observations")
        if item.get("scope_outcome_count") != scope_counts[artifact_id]:
            errors.append(f"import {artifact_id} scope_outcome_count does not match")


def _validate_provenance(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{prefix}.provenance must be an object")
        return
    _exact_fields(value, _PROVENANCE_FIELDS, f"{prefix}.provenance", errors)
    if value.get("producer_kind") != "fixture":
        errors.append(f"{prefix}.provenance.producer_kind must be fixture")
    _require_id(value.get("producer_id"), f"{prefix}.provenance.producer_id", errors)
    _require_repo_path(value.get("call_id"), f"{prefix}.provenance.call_id", errors)
    if value.get("model") != "" or value.get("prompt_sha256") != "":
        errors.append(f"{prefix}.provenance must not invent model or prompt custody")


def _validate_state_history(
    value: object, terminal_state: object, prefix: str, errors: list[str]
) -> None:
    if not isinstance(value, list) or len(value) < 2:
        errors.append(f"{prefix}.state_history must preserve source and import states")
        return
    for index, row in enumerate(value):
        row_prefix = f"{prefix}.state_history[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{row_prefix} must be an object")
            continue
        _exact_fields(row, _STATE_FIELDS, row_prefix, errors)
        for field in _STATE_FIELDS:
            _require_text(row.get(field), f"{row_prefix}.{field}", errors)
    if isinstance(value[-1], Mapping) and value[-1].get("state") != terminal_state:
        errors.append(f"{prefix}.state_history must end with terminal_state")


def _validate_relations(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix}.relations must be an array")
        return
    for index, relation in enumerate(value):
        relation_prefix = f"{prefix}.relations[{index}]"
        if not isinstance(relation, Mapping):
            errors.append(f"{relation_prefix} must be an object")
            continue
        _exact_fields(relation, _RELATION_FIELDS, relation_prefix, errors)
        if relation.get("relation_type") != "develops":
            errors.append(f"{relation_prefix}.relation_type is invalid")
        _require_id(
            relation.get("target_observation_id"),
            f"{relation_prefix}.target_observation_id",
            errors,
        )
        if relation.get("authority") != "source_reviewer":
            errors.append(f"{relation_prefix}.authority must be source_reviewer")


def _validate_boundary(value: object, errors: list[str]) -> None:
    expected = {
        "authoritative_conversation_referenced": True,
        "raw_import_records_preserved": True,
        "source_absence_and_ambiguity_preserved": True,
        "semantic_relevance_inferred_by_code": False,
        "family_projection_is_exclusive_gate": False,
        "metrics_treated_as_quality_evidence": False,
        "final_output_evaluated": False,
        "quality_score_included": False,
        "direct_graph_routing_allowed": False,
    }
    if not isinstance(value, Mapping):
        errors.append("ledger.boundary must be an object")
        return
    _exact_fields(value, _BOUNDARY_FIELDS, "ledger.boundary", errors)
    for field, expected_value in expected.items():
        if value.get(field) is not expected_value:
            errors.append(f"ledger.boundary.{field} must be {str(expected_value).lower()}")


def _record_kind_for_artifact(
    imports: Iterable[Mapping[str, Any]], artifact_id: str
) -> str:
    for item in imports:
        if item.get("artifact_id") == artifact_id:
            return str(item.get("record_kind", ""))
    return ""


def _collect_span_ids(value: object) -> list[str]:
    if isinstance(value, Mapping):
        direct = value.get("span_id")
        return [direct] if isinstance(direct, str) and direct else []
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            for span_id in _collect_span_ids(item):
                if span_id not in values:
                    values.append(span_id)
        return values
    return []


def _exact_fields(
    value: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]
) -> None:
    missing = sorted(fields - set(value))
    extra = sorted(set(value) - fields)
    if missing:
        errors.append(f"{prefix} missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix} unknown fields: {', '.join(extra)}")


def _require_id(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        errors.append(f"{prefix} must be a stable lowercase ID")


def _require_sha(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        errors.append(f"{prefix} must be a prefixed lowercase SHA-256")


def _require_text(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix} must be a non-empty string")


def _require_repo_path(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{prefix} must be a repo-relative path")
        return
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{prefix} must be a repo-relative path")


def _string_array(value: object, prefix: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        errors.append(f"{prefix} must be an array of non-empty strings")
        return []
    return list(value)


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _json_hash(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _unprefixed_json_hash(value: object) -> str:
    return _json_hash(value)


def _prefixed_json_hash(value: object) -> str:
    return "sha256:" + _json_hash(value)


def _json_copy(value: object) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))
