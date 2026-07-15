#!/usr/bin/env python3
"""Validate the provider-free Constitution Stage 0 addendum register."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDITED_ROOTS = ("engine/system_b", "scripts", "observatory")
DISPOSITIONS = {"keep_active", "keep_bounded", "preserve_research_only", "park", "retire", "abandon", "unknown"}
CONNECTION_TYPES = {"direct_runtime_call", "dynamic_or_indirect_runtime_call", "artifact_handoff", "optional_flagged_hook", "explicit_operator_command", "offline_builder_or_cli", "read_only_projection", "test_or_fixture_only", "research_runner_only", "documentation_only", "no_connection", "unknown"}
CONSTITUTION_STATUSES = {"conforms", "partially_conforms", "current_violation", "not_evaluable", "not_applicable"}
COVERAGE_STATES = {"deterministic_available", "provisional_semantic_available", "human_review_required", "unavailable", "private_or_locator_only", "unsafe_for_action", "unknown"}
REQUIRED_DT_GROUPS = {
    "decision_shape", "starting_direction", "current_direction", "user_questions_and_challenges",
    "assistant_recommendations_and_influence", "user_adoption_rejection_qualification_deferral",
    "option_lifecycle", "changes_of_mind", "constraints", "stakeholders_and_values",
    "evidence_and_supplied_context", "assumptions_and_unknowns", "unresolved_matters",
    "future_reopen_conditions", "pressure_provenance", "apply_reject_park_dispositions",
    "original_to_revised_changes", "preserved_original_value", "lost_value_or_overcorrection",
    "next_action_or_decision_gate", "privacy", "missingness", "source_custody",
    "human_review_requirements", "agent_inspection_suitability", "action_authorization_prohibition",
}


def validate(payload: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    components = payload.get("components", [])
    component_ids = [item.get("id") for item in components]
    if len(component_ids) != len(set(component_ids)):
        errors.append("component IDs must be unique")
    for item in components:
        if item.get("disposition") not in DISPOSITIONS:
            errors.append(f"invalid disposition for {item.get('id')}")
        _check_refs(item, errors)
    known = set(component_ids)
    connections = payload.get("connections", [])
    for edge in connections:
        if edge.get("type") not in CONNECTION_TYPES:
            errors.append(f"invalid connection type for {edge.get('id')}")
        if edge.get("source") not in known or edge.get("destination") not in known:
            errors.append(f"connection endpoint does not resolve: {edge.get('id')}")
        _check_refs(edge, errors)
    findings = payload.get("constitution_findings", [])
    rules = {item.get("rule") for item in findings}
    if rules != set(range(1, 18)):
        errors.append("Constitution findings must represent rules 1 through 17 exactly")
    if any(item.get("status") not in CONSTITUTION_STATUSES for item in findings):
        errors.append("invalid Constitution status")
    coverage = payload.get("decision_trail_coverage", [])
    groups = {item.get("field_group") for item in coverage}
    if groups != REQUIRED_DT_GROUPS:
        errors.append("Decision Trail field groups are incomplete or unexpected")
    if any(item.get("coverage") not in COVERAGE_STATES for item in coverage):
        errors.append("invalid Decision Trail coverage state")
    if payload.get("provider_calls") != 0:
        errors.append("provider_calls must be 0")
    if float(payload.get("provider_cost_usd", -1)) != 0.0:
        errors.append("provider_cost_usd must be 0.00")
    r4 = next((item for item in components if item.get("id") == "r4_incremental_readers"), None)
    if not r4 or r4.get("disposition") not in {"retire", "preserve_research_only"}:
        errors.append("R4 readers cannot be active")
    file_count = _validate_file_coverage(payload, errors)
    for family in payload.get("documentation_families", []):
        _check_refs(family, errors)
    nonclaims = set(payload.get("nonclaims", []))
    for required in {"not_product_usefulness_proof", "not_action_authorization", "not_constitution_v6", "not_r4_integration"}:
        if required not in nonclaims:
            errors.append(f"missing nonclaim: {required}")
    receipt = {
        "component_count": len(components),
        "connection_count": len(connections),
        "constitution_rule_count": len(findings),
        "decision_trail_field_group_count": len(coverage),
        "implementation_file_count": file_count,
        "provider_calls": payload.get("provider_calls"),
        "provider_cost_usd": float(payload.get("provider_cost_usd", -1)),
        "schema_version": "lolla.constitution_stage0_addendum_validation.v1",
        "status": "valid" if not errors else "invalid",
    }
    return errors, receipt


def _check_refs(item: dict, errors: list[str]) -> None:
    refs = item.get("evidence", [])
    if not refs:
        errors.append(f"missing evidence: {item.get('id', item.get('family_id', 'record'))}")
    for ref in refs:
        path = str(ref).split(":", 1)[0]
        if not (ROOT / path).exists():
            errors.append(f"missing referenced path: {path}")


def _validate_file_coverage(payload: dict, errors: list[str]) -> int:
    section = payload.get("implementation_file_coverage", {})
    rules = section.get("ordered_assignment_rules", [])
    paths = sorted({p.as_posix() for root in AUDITED_ROOTS for p in (ROOT / root).rglob("*.py") if p.resolve() != Path(__file__).resolve()})
    relative = [str(Path(path).relative_to(ROOT)) for path in paths]
    assignments: dict[str, str] = {}
    for path in relative:
        for rule in rules:
            if fnmatch.fnmatch(path, rule["pattern"]):
                assignments[path] = rule["component_id"]
                break
        if path not in assignments:
            errors.append(f"unassigned implementation file: {path}")
    if set(assignments.values()) - {item.get("id") for item in payload.get("components", [])}:
        errors.append("implementation assignment references unknown component")
    if section.get("expected_file_count") != len(relative):
        errors.append(f"implementation file count drift: expected {section.get('expected_file_count')}, found {len(relative)}")
    return len(relative)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--register", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"register load failed: {exc}", file=sys.stderr)
        return 2
    errors, receipt = validate(payload)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
