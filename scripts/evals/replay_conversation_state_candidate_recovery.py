#!/usr/bin/env python3
"""Provider-free replay of the conversation-state candidate recovery path."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_candidate_pipeline import (
    build_candidate_ledger,
    compile_handoff_from_ledger,
    decompose_reviewed_handoff,
)
from engine.system_b.conversation_state_candidates import (
    ConstraintExtraction,
    PositionExtraction,
    ThreadExtraction,
    build_micro_contract,
    build_source_catalog,
    parse_typed,
    provider_compatibility_report,
    validate_extraction_state,
)
from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


CONTRACT_SCHEMA = "lolla.conversation_state_candidate_recovery_contract.v1"
RESULT_SCHEMA = "lolla.conversation_state_candidate_recovery_result.v1"


class CandidateRecoveryReplayError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CandidateRecoveryReplayError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _repo_path(value: object, *, repo_root: Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        raise CandidateRecoveryReplayError("contract paths must be repo-relative")
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise CandidateRecoveryReplayError("contract path escapes repository") from exc
    return resolved


def _verify_lock(record: Mapping[str, Any], *, repo_root: Path, label: str) -> Path:
    path = _repo_path(record.get("path"), repo_root=repo_root)
    if not path.is_file():
        raise CandidateRecoveryReplayError(f"{label} file missing: {path}")
    if _sha(path) != record.get("sha256"):
        raise CandidateRecoveryReplayError(f"{label} hash mismatch: {path}")
    return path


def _candidate_counts(ledger: Mapping[str, Any]) -> Counter[str]:
    return Counter(
        str(row.get("family"))
        for row in ledger.get("candidates", [])
        if isinstance(row, Mapping)
    )


def _replay_adversarial_fixture(
    fixture: Mapping[str, Any], *, catalog: Any
) -> dict[str, Any]:
    family = str(fixture.get("family"))
    classes = {
        "positions": PositionExtraction,
        "threads": ThreadExtraction,
        "constraints": ConstraintExtraction,
    }
    if family not in classes:
        raise CandidateRecoveryReplayError("unknown adversarial fixture family")
    parsed, parse_issues = parse_typed(classes[family], fixture.get("payload"))
    expected_issue = fixture.get("expected_issue")
    issue_codes = [issue.code for issue in parse_issues]
    if fixture.get("expected_stage") == "typed_parser":
        passed = expected_issue in issue_codes
        if not passed:
            raise CandidateRecoveryReplayError(
                f"adversarial parser fixture did not fail as expected: {fixture.get('fixture_id')}"
            )
        return {
            "fixture_id": fixture.get("fixture_id"),
            "status": "passed",
            "terminal_outcome": "parser_rejected",
            "expected_issue": expected_issue,
            "observed_issue_codes": issue_codes,
            "accepted_observed_path_allowed": False,
        }
    if parse_issues or parsed is None:
        raise CandidateRecoveryReplayError(
            f"adversarial fixture shape unexpectedly invalid: {fixture.get('fixture_id')}"
        )
    state_issues = validate_extraction_state(parsed)
    if state_issues:
        raise CandidateRecoveryReplayError(
            f"adversarial fixture state unexpectedly invalid: {fixture.get('fixture_id')}"
        )
    extractions = {
        "positions": PositionExtraction(
            status="not_found", decision_summary=None, positions=()
        ),
        "threads": ThreadExtraction(status="not_found", threads=()),
        "constraints": ConstraintExtraction(status="not_found", constraints=()),
    }
    extractions[family] = parsed
    ledger = build_candidate_ledger(
        case_id=f"adversarial-{fixture.get('fixture_id')}",
        catalog=catalog,
        extractions=extractions,
    )
    compiled, compiler = compile_handoff_from_ledger(
        ledger=ledger, catalog=catalog
    )
    observed_issues = [
        issue["code"]
        for row in ledger["candidates"]
        for issue in row["validation_issues"]
    ]
    if expected_issue is not None and expected_issue not in observed_issues:
        raise CandidateRecoveryReplayError(
            f"adversarial ledger issue missing: {fixture.get('fixture_id')}"
        )
    if compiled is not None or compiler.get("accepted_observed_path_allowed") is not False:
        raise CandidateRecoveryReplayError(
            f"adversarial fixture entered accepted path: {fixture.get('fixture_id')}"
        )
    family_outcome = ledger["family_outcomes"][family]
    terminal = (
        "absence_preserved"
        if family_outcome["absence_is_observed"]
        else "ledger_quarantined"
    )
    return {
        "fixture_id": fixture.get("fixture_id"),
        "status": "passed",
        "terminal_outcome": terminal,
        "expected_issue": expected_issue,
        "observed_issue_codes": observed_issues,
        "accepted_observed_path_allowed": False,
    }


def run_replay(
    contract: Mapping[str, Any], *, repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise CandidateRecoveryReplayError("unexpected recovery contract schema")
    if contract.get("status") != "frozen_provider_free":
        raise CandidateRecoveryReplayError("recovery contract is not frozen")

    locks = contract.get("artifact_locks")
    if not isinstance(locks, list) or not locks:
        raise CandidateRecoveryReplayError("artifact locks are missing")
    for index, record in enumerate(locks):
        if not isinstance(record, Mapping):
            raise CandidateRecoveryReplayError("artifact lock row is invalid")
        _verify_lock(record, repo_root=repo_root, label=f"artifact_locks[{index}]")

    migration_record = contract.get("atomic_migration")
    if not isinstance(migration_record, Mapping):
        raise CandidateRecoveryReplayError("atomic migration lock is missing")
    migration_path = _verify_lock(
        migration_record, repo_root=repo_root, label="atomic_migration"
    )
    migrations = _load(migration_path)

    cases = contract.get("cases")
    if not isinstance(cases, list) or not cases:
        raise CandidateRecoveryReplayError("cases must be a non-empty array")

    compatibility = {
        provider: provider_compatibility_report(provider=provider)
        for provider in ("openai", "gemini")
    }
    if not all(report["all_compatible"] for report in compatibility.values()):
        raise CandidateRecoveryReplayError("a provider schema projection is incompatible")

    aggregate = Counter()
    dispositions: Counter[str] = Counter()
    ownership: Counter[str] = Counter()
    case_results: list[dict[str, Any]] = []
    prompt_contract_hashes: list[dict[str, str]] = []
    replay_catalog = None

    for index, record in enumerate(cases):
        if not isinstance(record, Mapping):
            raise CandidateRecoveryReplayError(f"cases[{index}] is invalid")
        case_id = str(record.get("case_id"))
        packet_record = record.get("packet")
        source_record = record.get("source")
        if not isinstance(packet_record, Mapping) or not isinstance(source_record, Mapping):
            raise CandidateRecoveryReplayError(f"case locks missing: {case_id}")
        packet_path = _verify_lock(
            packet_record, repo_root=repo_root, label=f"{case_id}.packet"
        )
        source_path = _verify_lock(
            source_record, repo_root=repo_root, label=f"{case_id}.source"
        )
        packet = _load(packet_path)
        source_text = source_path.read_text(encoding="utf-8")
        if packet.get("case_id") != case_id:
            raise CandidateRecoveryReplayError(f"case identity mismatch: {case_id}")

        source_repo_path = str(source_path.relative_to(repo_root))
        catalog = build_source_catalog(
            source_text=source_text, source_path=source_repo_path
        )
        if case_id == contract.get("adversarial_source_case_id"):
            replay_catalog = catalog
        if catalog.source_sha256 != source_record.get("sha256"):
            raise CandidateRecoveryReplayError(f"source catalog hash mismatch: {case_id}")
        if catalog.message_count != int(record.get("message_count", -1)):
            raise CandidateRecoveryReplayError(f"message count mismatch: {case_id}")

        extractions = decompose_reviewed_handoff(
            packet, catalog=catalog, atomic_migrations=migrations
        )
        ledger = build_candidate_ledger(
            case_id=case_id, catalog=catalog, extractions=extractions
        )
        compiled, compiler = compile_handoff_from_ledger(
            ledger=ledger, catalog=catalog
        )
        if compiler.get("status") != "compiled" or compiled is None:
            raise CandidateRecoveryReplayError(f"compiler quarantined reviewed case: {case_id}")
        if compiler.get("accepted_observed_path_allowed") is not True:
            raise CandidateRecoveryReplayError(f"compiled path was not accepted: {case_id}")
        violations = validate_conversation_state_handoff(
            compiled, source_text=source_text
        )
        if violations:
            raise CandidateRecoveryReplayError(
                f"compiled handoff validation failed: {case_id}: {violations}"
            )

        projection = build_fact_free_routing_boundary(compiled)
        direct_graph_seed_count = int(projection["direct_graph_seed_count"])
        counts = _candidate_counts(ledger)
        expected_constraints = int(record.get("atomic_constraint_count", -1))
        observed_constraints = counts.get("constraints", 0)
        if observed_constraints != expected_constraints:
            raise CandidateRecoveryReplayError(
                f"atomic constraint count mismatch: {case_id}"
            )
        if counts.get("decision_summary", 0) != 1 or counts.get("positions", 0) != 1:
            raise CandidateRecoveryReplayError(f"position projection incomplete: {case_id}")
        if counts.get("threads", 0) != 1:
            raise CandidateRecoveryReplayError(f"thread projection incomplete: {case_id}")
        if ledger["metrics"]["invalid_candidate_count"] != 0:
            raise CandidateRecoveryReplayError(f"reviewed candidate invalid: {case_id}")
        if any(item.claim_mode == "mixed" for item in extractions["constraints"].constraints):
            raise CandidateRecoveryReplayError(f"mixed constraint survived: {case_id}")

        position = extractions["positions"].positions[0]
        thread = extractions["threads"].threads[0]
        if position.ownership != record.get("position_ownership"):
            raise CandidateRecoveryReplayError(f"ownership mismatch: {case_id}")
        if thread.disposition != record.get("thread_disposition"):
            raise CandidateRecoveryReplayError(f"disposition mismatch: {case_id}")
        contribution_turns = Counter()
        for contribution in position.contributions:
            span = catalog.by_id()[contribution.evidence.span_id]
            contribution_turns[span.speaker] = max(
                contribution_turns[span.speaker], span.turn_index
            )
        late_trajectory_preserved = (
            contribution_turns.get("user") == 7
            and contribution_turns.get("assistant") == 7
        )

        for provider in ("openai", "gemini"):
            for kind in ("positions", "threads", "constraints"):
                prompt = build_micro_contract(
                    kind, catalog=catalog, provider=provider
                )
                prompt_contract_hashes.append(
                    {
                        "case_id": case_id,
                        "provider": provider,
                        "kind": kind,
                        "system_prompt_sha256": prompt["system_prompt_sha256"],
                        "user_prompt_sha256": prompt["user_prompt_sha256"],
                        "schema_sha256": prompt["schema_sha256"],
                    }
                )

        candidate_count = int(ledger["metrics"]["proposal_count"])
        aggregate.update(
            {
                "case_count": 1,
                "message_count": catalog.message_count,
                "position_count": counts.get("positions", 0),
                "thread_count": counts.get("threads", 0),
                "constraint_count": observed_constraints,
                "candidate_count": candidate_count,
                "invalid_candidate_count": int(
                    ledger["metrics"]["invalid_candidate_count"]
                ),
                "direct_graph_seed_count": direct_graph_seed_count,
                "late_trajectory_case_count": int(late_trajectory_preserved),
            }
        )
        ownership.update([position.ownership])
        dispositions.update([thread.disposition])
        case_results.append(
            {
                "case_id": case_id,
                "status": "passed",
                "message_count": catalog.message_count,
                "source_span_count": len(catalog.spans),
                "candidate_count": candidate_count,
                "atomic_constraint_count": observed_constraints,
                "position_ownership": position.ownership,
                "thread_disposition": thread.disposition,
                "late_trajectory_preserved": late_trajectory_preserved,
                "invalid_candidate_count": ledger["metrics"]["invalid_candidate_count"],
                "direct_graph_seed_count": direct_graph_seed_count,
                "compiler_status": compiler["status"],
            }
        )

    fixture_records = contract.get("adversarial_fixtures")
    if not isinstance(fixture_records, list) or not fixture_records:
        raise CandidateRecoveryReplayError("adversarial fixtures are missing")
    if replay_catalog is None:
        raise CandidateRecoveryReplayError("no source catalog available for fixtures")
    adversarial_results: list[dict[str, Any]] = []
    for index, record in enumerate(fixture_records):
        if not isinstance(record, Mapping):
            raise CandidateRecoveryReplayError("adversarial fixture lock is invalid")
        fixture_path = _verify_lock(
            record, repo_root=repo_root, label=f"adversarial_fixtures[{index}]"
        )
        fixture = _load(fixture_path)
        if fixture.get("fixture_id") != record.get("fixture_id"):
            raise CandidateRecoveryReplayError("adversarial fixture identity mismatch")
        adversarial_results.append(
            _replay_adversarial_fixture(fixture, catalog=replay_catalog)
        )

    aggregate.update(
        {
            "adversarial_fixture_count": len(adversarial_results),
            "adversarial_parser_rejection_count": sum(
                row["terminal_outcome"] == "parser_rejected"
                for row in adversarial_results
            ),
            "adversarial_ledger_quarantine_count": sum(
                row["terminal_outcome"] == "ledger_quarantined"
                for row in adversarial_results
            ),
            "adversarial_absence_preserved_count": sum(
                row["terminal_outcome"] == "absence_preserved"
                for row in adversarial_results
            ),
        }
    )

    observed = dict(sorted(aggregate.items()))
    observed["position_ownership_counts"] = dict(sorted(ownership.items()))
    observed["thread_disposition_counts"] = dict(sorted(dispositions.items()))
    observed["prompt_contract_count"] = len(prompt_contract_hashes)
    required = contract.get("required_aggregate")
    if not isinstance(required, Mapping):
        raise CandidateRecoveryReplayError("required aggregate is missing")
    gates = {
        key: observed.get(key) == expected for key, expected in required.items()
    }
    gates.update(
        {
            "all_cases_passed": all(row["status"] == "passed" for row in case_results),
            "all_provider_projections_compatible": all(
                report["all_compatible"] for report in compatibility.values()
            ),
            "all_late_trajectories_preserved": all(
                row["late_trajectory_preserved"] for row in case_results
            ),
            "no_invalid_candidate_entered_current_view": observed.get(
                "invalid_candidate_count"
            )
            == 0,
            "no_case_context_seeded_graph": observed.get("direct_graph_seed_count") == 0,
            "provider_calls_zero": True,
            "all_adversarial_fixtures_passed": all(
                row["status"] == "passed"
                and row["accepted_observed_path_allowed"] is False
                for row in adversarial_results
            ),
        }
    )
    failed = sorted(key for key, passed in gates.items() if not passed)
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "passed" if not failed else "failed",
        "comparison_kind": "source_reviewed_decomposition_ledger_and_reassembly_replay",
        "contract_sha256": _canonical_sha(contract),
        "observed": observed,
        "case_results": case_results,
        "adversarial_results": adversarial_results,
        "provider_compatibility": compatibility,
        "prompt_contracts_sha256": _canonical_sha(prompt_contract_hashes),
        "gates": gates,
        "failed_gates": failed,
        "provider_calls": 0,
        "graph_calls": 0,
        "runtime_modified": False,
        "interpretation": {
            "typed_representation_and_composition_work": not failed,
            "automatic_extraction_quality": "not_tested",
            "semantic_label_correctness": "source_reviewed_same_session_not_independent_gold",
            "provider_acceptance": "not_tested",
            "graph_or_downstream_value": "not_tested",
        },
        "non_claims": [
            "not_automatic_extraction_improvement",
            "not_independent_gold",
            "not_provider_acceptance_proof",
            "not_graph_value",
            "not_downstream_answer_value",
            "not_runtime_authority",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args()
    contract = _load(Path(args.contract))
    print(json.dumps(run_replay(contract), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
