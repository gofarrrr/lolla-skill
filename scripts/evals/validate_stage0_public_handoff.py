#!/usr/bin/env python3
"""Validate the provider-free current public and cold-start handoff."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CURRENT_ENTRYPOINTS = (
    "README.md",
    "PROJECT_STATUS.md",
    "HOW_IT_WORKS.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "docs/README.md",
)

SUPPORTING_CURRENT_DOCS = (
    "docs/history/README.md",
    "docs/operations/lolla-repository-gardening-audit-2026-07-15.md",
    "docs/evals/lolla-public-handoff-cold-reader-review-2026-07-22.md",
    "docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md",
    "docs/conversation-understanding/lolla-consumer-context-contract-v1-correction-result-2026-07-22.md",
    "docs/conversation-understanding/lolla-pressure-understanding-and-graph-evidence-prd-v0.md",
    "docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md",
    "docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md",
    "references/knowledge-substrate-operations.md",
    "plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md",
    "plans/lolla-pressure-understanding-and-graph-evidence-plan-2026-07-22.md",
)

LIVE_CONTRACTS = (
    "SKILL.md",
    "docs/skill/STEPS.md",
    "scripts/skill/setup.sh",
)

REQUIRED_FILES = CURRENT_ENTRYPOINTS + SUPPORTING_CURRENT_DOCS + (
    *LIVE_CONTRACTS,
    "requirements-dev.txt",
    ".github/workflows/public-handoff.yml",
    "docs/evals/lolla-public-handoff-cold-reader-answers-v2.json",
    "docs/evals/lolla-pressure-understanding-graph-evidence-package-v1.json",
    "docs/evals/lolla-consumer-context-pressure-ablation-contract-v1.json",
    "docs/evals/lolla-constitution-stage0-addendum-register-v1.json",
    "docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md",
    "docs/conversation-understanding/lolla-product-constitution-v5.md",
    ".codex/skills/audit-lolla-boundaries/SKILL.md",
    ".codex/skills/audit-lolla-boundaries/agents/openai.yaml",
    ".codex/skills/audit-lolla-boundaries/references/evidence-gates.md",
)

QUESTION_IDS = (
    "q01_product_job",
    "q02_nonpurpose",
    "q03_strongest_evidence",
    "q04_unproven",
    "q05_live_path",
    "q06_source_boundary",
    "q07_graph_role_and_policy",
    "q08_repository_boundary",
    "q09_r4_status",
    "q10_decision_work_status",
    "q11_atlas_teacher_status",
    "q12_observatory_authority",
    "q13_historical_authority",
    "q14_next_stage",
    "q15_provider_and_data_boundary",
    "q16_host_reasoner_and_codex",
    "q17_pressure_understanding_graph_lanes",
)

FORBIDDEN_CURRENT_PHRASES = (
    "architecture is sound",
    "the system works — but more data",
    "four independent audit lanes",
    "verified model presence",
    "r4 reader is live",
    "decision work automatically understands",
    "provider calls currently authorized: four",
    "local and unpublished",
    "you are a **pure orchestrator**",
    "all semantic judgment runs through openrouter",
    "also use proactively when",
    "add it to your .env for full accuracy",
)

SIZE_LIMITS = {
    "README.md": (280, 3_200),
    "PROJECT_STATUS.md": (330, 4_000),
    "HOW_IT_WORKS.md": (390, 5_500),
    "AGENTS.md": (300, 4_500),
    "CONTRIBUTING.md": (150, 2_000),
    "docs/README.md": (190, 2_500),
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def validate(
    root: Path = ROOT,
    *,
    text_overrides: dict[str, str] | None = None,
    packet_override: dict | None = None,
    evidence_package_override: dict | None = None,
    consumer_context_override: dict | None = None,
) -> tuple[list[str], dict]:
    errors: list[str] = []
    overrides = text_overrides or {}

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            errors.append(f"missing required public-handoff file: {relative}")

    texts: dict[str, str] = {}
    for relative in CURRENT_ENTRYPOINTS:
        if not (root / relative).exists() and relative not in overrides:
            continue
        text = overrides.get(relative, (root / relative).read_text(encoding="utf-8"))
        texts[relative] = text
        max_lines, max_words = SIZE_LIMITS[relative]
        line_count = len(text.splitlines())
        word_count = len(text.split())
        if line_count > max_lines:
            errors.append(f"{relative} exceeds current-entrypoint line limit: {line_count}>{max_lines}")
        if word_count > max_words:
            errors.append(f"{relative} exceeds current-entrypoint word limit: {word_count}>{max_words}")

    contract_texts = {
        relative: overrides.get(relative, (root / relative).read_text(encoding="utf-8"))
        for relative in LIVE_CONTRACTS
        if (root / relative).exists() or relative in overrides
    }
    current_joined = "\n".join((*texts.values(), *contract_texts.values())).lower()
    for phrase in FORBIDDEN_CURRENT_PHRASES:
        if phrase in current_joined:
            errors.append(f"forbidden stale public claim: {phrase}")

    _require_terms(
        texts.get("PROJECT_STATUS.md", ""),
        (
            "live",
            "bounded",
            "experimental",
            "parked",
            "retired",
            "research only",
            "historical evidence",
            "proposal",
            "fixture / test only",
            "unknown",
            "real-user usefulness",
        ),
        "PROJECT_STATUS.md",
        errors,
    )
    _require_terms(
        texts.get("README.md", ""),
        (
            "experimental reasoning-pressure",
            "real-user usefulness",
            "decision work",
            "read-only",
            "r4",
            "stage 1",
        ),
        "README.md",
        errors,
    )
    _require_terms(
        texts.get("HOW_IT_WORKS.md", ""),
        (
            "graph recall is a hypothesis",
            "receipt proves",
            "same conversational context",
            "retired r4",
            "no such development authorization currently exists",
        ),
        "HOW_IT_WORKS.md",
        errors,
    )
    _require_terms(
        texts.get("AGENTS.md", ""),
        (
            "project_status.md",
            "provider calls authorized for repository development: zero",
            "stage 1",
        ),
        "AGENTS.md",
        errors,
    )
    _require_terms(
        contract_texts.get("SKILL.md", ""),
        (
            "host reasoner and",
            "four distinct pressure products",
            "known haiku 4.5",
            "optional step 7 is claude code-specific",
            "audit complete. i'm opening the full breakdown now.",
        ),
        "SKILL.md",
        errors,
    )
    _require_terms(
        contract_texts.get("scripts/skill/setup.sh", ""),
        (
            "optional embedding retrieval and query expansion",
            "skill package or the documented global config",
        ),
        "scripts/skill/setup.sh",
        errors,
    )
    roadmap_relative = "plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md"
    roadmap_text = overrides.get(
        roadmap_relative,
        (root / roadmap_relative).read_text(encoding="utf-8"),
    )
    _require_terms(
        roadmap_text,
        (
            "stage 0 and 0.6 are",
            "exact checked-in-safe case packet",
            "no later evidence stage is authorized",
            "does not supersede the pr104 pause",
        ),
        roadmap_relative,
        errors,
    )
    lineage_relative = "docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md"
    lineage_text = overrides.get(
        lineage_relative,
        (root / lineage_relative).read_text(encoding="utf-8"),
    )
    _require_terms(
        lineage_text,
        (
            "future_human_review_queue_not_filled",
            "pause_until_human_review_capacity_returns",
            "unauthorized and unstarted",
            "could produce a clean interface-truthfulness result",
            "cannot prove that lolla understands conversations correctly",
        ),
        lineage_relative,
        errors,
    )
    maintainer_skill_relative = ".codex/skills/audit-lolla-boundaries/SKILL.md"
    maintainer_skill_text = overrides.get(
        maintainer_skill_relative,
        (root / maintainer_skill_relative).read_text(encoding="utf-8"),
    )
    _require_terms(
        maintainer_skill_text,
        (
            "do not use this maintainer skill to run a user-facing lolla audit",
            "do not create a second compiler",
            "human: semantic correction, usefulness, and action authority",
            "preserve frozen experiment artifacts and pr104's blank human fields",
            "require a product choice between pressure-now and understand-later",
            "same-context self-justification",
            "mandatory absorption in either context",
        ),
        maintainer_skill_relative,
        errors,
    )
    evidence_gates_relative = ".codex/skills/audit-lolla-boundaries/references/evidence-gates.md"
    evidence_gates_text = overrides.get(
        evidence_gates_relative,
        (root / evidence_gates_relative).read_text(encoding="utf-8"),
    )
    _require_terms(
        evidence_gates_text,
        (
            "the layer after an error cannot certify the layer before it",
            "a. pressure now",
            "b. understand later",
            "c. improve the conversation-to-graph bridge",
            "candidate survival also cannot prove independent consideration",
            "lower application rate does not establish domestication",
            "one alternative",
        ),
        evidence_gates_relative,
        errors,
    )

    link_count = 0
    for relative in CURRENT_ENTRYPOINTS + SUPPORTING_CURRENT_DOCS + LIVE_CONTRACTS[:2]:
        path = root / relative
        if not path.exists():
            continue
        text = overrides.get(relative, path.read_text(encoding="utf-8"))
        count, link_errors = _validate_local_links(root, path, text)
        link_count += count
        errors.extend(link_errors)

    packet_path = root / "docs/evals/lolla-public-handoff-cold-reader-answers-v2.json"
    if packet_override is not None:
        packet = packet_override
    elif packet_path.exists():
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            packet = {}
            errors.append(f"cold-reader packet is invalid JSON: {exc}")
    else:
        packet = {}

    if packet.get("schema_version") != "lolla.public_handoff_cold_reader.v2":
        errors.append("unexpected cold-reader schema_version")
    if packet.get("reviewer_class") != "maintainer_and_repository_only_agent_review_not_independent_human_evidence":
        errors.append("cold-reader review must not claim independent human evidence")
    if packet.get("provider_calls") != 0:
        errors.append("cold-reader provider_calls must be 0")
    if float(packet.get("provider_cost_usd", -1)) != 0.0:
        errors.append("cold-reader provider_cost_usd must be 0.00")
    questions = packet.get("questions", [])
    if tuple(item.get("id") for item in questions) != QUESTION_IDS:
        errors.append("cold-reader questions must match the seventeen-question orientation contract")
    for item in questions:
        if not item.get("expected_answer"):
            errors.append(f"cold-reader answer missing: {item.get('id')}")
        evidence = item.get("evidence", [])
        if not evidence:
            errors.append(f"cold-reader evidence missing: {item.get('id')}")
        for relative in evidence:
            if not (root / relative).exists():
                errors.append(f"cold-reader evidence path missing: {relative}")

    evidence_package_path = root / "docs/evals/lolla-pressure-understanding-graph-evidence-package-v1.json"
    if evidence_package_override is not None:
        evidence_package = evidence_package_override
    elif evidence_package_path.exists():
        try:
            evidence_package = json.loads(evidence_package_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            evidence_package = {}
            errors.append(f"pressure/understanding/graph evidence package is invalid JSON: {exc}")
    else:
        evidence_package = {}

    _validate_pressure_understanding_graph_package(root, evidence_package, errors)

    consumer_context_errors, consumer_context_receipt = _validate_consumer_context_contract(
        root,
        contract_override=consumer_context_override,
    )
    errors.extend(consumer_context_errors)

    register_path = root / "docs/evals/lolla-constitution-stage0-addendum-register-v1.json"
    if register_path.exists():
        try:
            register = json.loads(register_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            register = {}
            errors.append(f"Stage 0 register is invalid JSON: {exc}")
        if register.get("provider_calls") != 0 or float(register.get("provider_cost_usd", -1)) != 0.0:
            errors.append("Stage 0 register provider boundary must remain zero")
        r4 = next((item for item in register.get("components", []) if item.get("id") == "r4_incremental_readers"), None)
        if not r4 or r4.get("disposition") != "retire":
            errors.append("Stage 0 register must keep incremental R4 retired")

    receipt = {
        "cold_reader_question_count": len(questions),
        "consumer_context_contract_status": consumer_context_receipt.get("status"),
        "current_entrypoint_count": len(texts),
        "local_link_count": link_count,
        "provider_calls": packet.get("provider_calls"),
        "provider_cost_usd": float(packet.get("provider_cost_usd", -1)),
        "pressure_understanding_graph_package_status": evidence_package.get("status"),
        "required_file_count": len(REQUIRED_FILES),
        "schema_version": "lolla.public_handoff_validation.v2",
        "status": "valid" if not errors else "invalid",
    }
    return errors, receipt


def _validate_pressure_understanding_graph_package(
    root: Path,
    package: dict,
    errors: list[str],
) -> None:
    label = "pressure/understanding/graph evidence package"
    if package.get("schema_version") != "lolla.pressure_understanding_graph_evidence_package.v1":
        errors.append(f"{label} has unexpected schema_version")
    if package.get("status") != "planning_package_complete_evidence_execution_unstarted":
        errors.append(f"{label} must remain planning-complete and execution-unstarted")

    lanes = package.get("product_lanes", {})
    pressure = lanes.get("a_pressure_now", {})
    understanding = lanes.get("b_understand_later", {})
    bridge = lanes.get("c_conversation_to_graph_bridge", {})
    if pressure.get("status") != "live_experimental_core_preserved":
        errors.append(f"{label} must preserve the pressure-now live experimental core")
    if understanding.get("status") != "paused_at_pr104_principal_human_review":
        errors.append(f"{label} must preserve the PR104 human-review pause")
    if understanding.get("human_fields_filled") is not False:
        errors.append(f"{label} must not claim PR104 human fields are filled")
    expected_arms = (
        "transcript_only_strong_reconsideration",
        "current_live_bridge_plus_current_graph",
        "human_controlled_fact_free_direct_only",
        "human_controlled_fact_free_plus_current_graph",
    )
    if tuple(bridge.get("evaluation_arms", ())) != expected_arms:
        errors.append(f"{label} must preserve the four-arm bridge comparison")
    if bridge.get("status") != "planned_unstarted":
        errors.append(f"{label} must keep the conversation-to-graph comparison unstarted")
    context_ablation = bridge.get("consumer_context_ablation", {})
    expected_context_ablation = {
        "status": "provider_free_design_shape_valid_execution_not_ready",
        "contract": "docs/evals/lolla-consumer-context-pressure-ablation-contract-v1.json",
        "predecessor_contract": "docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json",
        "design_shape_valid": True,
        "execution_ready": False,
        "single_draw_evidence_class": "single_draw_case_diagnostic",
        "primary_estimand": "consumer_context_representation_interaction",
        "fresh_graph_supply_output_count": 4,
        "additional_trajectory_continuation_output_count": 2,
        "live_same_context_output_is_causal_evidence": False,
        "context_interaction_identifies_self_justification": False,
        "fresh_context_is_independent_truth": False,
    }
    for key, expected in expected_context_ablation.items():
        if context_ablation.get(key) != expected:
            errors.append(f"{label} consumer_context_ablation.{key} must be {expected!r}")

    lineage = package.get("decision_trail_lineage", {})
    if lineage.get("pr104_state") != "pause_until_human_review_capacity_returns":
        errors.append(f"{label} has incorrect PR104 state")
    if lineage.get("july_stage1_supersedes_pr104") is not False:
        errors.append(f"{label} must keep July Stage 1 separate from PR104")
    if lineage.get("july_stage1_can_validate_semantic_understanding") is not False:
        errors.append(f"{label} must not let July Stage 1 validate semantics")

    connections = {
        item.get("id"): item.get("state")
        for item in package.get("connection_states", [])
        if isinstance(item, dict)
    }
    expected_connections = {
        "live_conversation_to_companion_recall": "live_probabilistic",
        "published_substrate_to_constitutional_planner": "live_deterministic",
        "reasoning_pattern_packet_to_live_graph": "absent_research_only",
        "pr104_human_review_to_runtime": "absent",
        "decision_work_automatic_semantic_supplier": "missing",
        "prospective_complete_paths_to_live_receipt": "absent_candidate_only",
        "fresh_context_consumer_to_live_runtime": "absent_research_only",
    }
    if connections != expected_connections:
        errors.append(f"{label} connection states must preserve live, absent, and missing boundaries")

    graph = package.get("current_graph_policy", {})
    expected_graph = {
        "policy_id": "lolla.constitutional_pressure_planner",
        "version": "1.0.0",
        "model_count": 222,
        "rich_relation_count": 1358,
        "direct_active_cap": 6,
        "expansion_seed_rule": "direct_active_only",
        "direction": "outgoing_authored_relations",
        "hop_depth": 1,
        "provider_calls_allowed": 0,
        "policy_change_authorized": False,
    }
    for key, expected in expected_graph.items():
        if graph.get(key) != expected:
            errors.append(f"{label} current_graph_policy.{key} must be {expected!r}")

    policy_path = root / "data/curation/constitutional_pressure_policy_v1.json"
    if policy_path.exists():
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        for key in (
            "policy_id",
            "version",
            "direct_active_cap",
            "expansion_seed_rule",
            "direction",
            "hop_depth",
            "provider_calls_allowed",
        ):
            if graph.get(key) != policy.get(key):
                errors.append(f"{label} current_graph_policy.{key} must match the published policy")
        if graph.get("relation_slots") != policy.get("graph_relation_slots"):
            errors.append(f"{label} relation slots must match the published policy")

    knowledge_graph_path = root / "data/knowledge_graph.json"
    relationship_graph_path = root / "data/relationship_graph.json"
    if knowledge_graph_path.exists() and relationship_graph_path.exists():
        knowledge_graph = json.loads(knowledge_graph_path.read_text(encoding="utf-8"))
        relationship_graph = json.loads(relationship_graph_path.read_text(encoding="utf-8"))
        if graph.get("model_count") != len(knowledge_graph.get("models", {})):
            errors.append(f"{label} model_count must match the published graph")
        if graph.get("rich_relation_count") != len(relationship_graph):
            errors.append(f"{label} rich_relation_count must match the published graph")

    authorization = package.get("authorization", {})
    expected_authorization = {
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "embedding_calls": 0,
        "private_archive_inspection": False,
        "principal_human_review_completed": False,
        "runtime_change": False,
        "graph_policy_change": False,
        "fresh_context_promotion": False,
        "sidecar_automation": False,
        "atlas_or_interface_work": False,
        "product_usefulness_claim": False,
    }
    for key, expected in expected_authorization.items():
        if authorization.get(key) != expected:
            errors.append(f"{label} authorization.{key} must be {expected!r}")

    artifacts = package.get("artifacts", {})
    for role, relative in artifacts.items():
        if not isinstance(relative, str) or not relative or not (root / relative).exists():
            errors.append(f"{label} artifact missing for {role}: {relative}")

    intake_path = root / "reviews/human/decision-trail-human-review-intake-packet-v0/intake.json"
    if intake_path.exists():
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
        if intake.get("boundary", {}).get("human_fields_filled") is not False:
            errors.append("PR104 historical intake human fields must remain blank")
        if intake.get("scope", {}).get("case_count") != understanding.get("case_count"):
            errors.append(f"{label} PR104 case count must match the historical intake")
        if intake.get("next_state", {}).get("recommended_status") != lineage.get("pr104_state"):
            errors.append(f"{label} PR104 state must match the historical intake")


def _validate_consumer_context_contract(
    root: Path,
    *,
    contract_override: dict | None,
) -> tuple[list[str], dict]:
    validator_path = root / "scripts/evals/validate_consumer_context_pressure_ablation.py"
    if not validator_path.exists():
        return ["missing consumer-context validator"], {"status": "invalid"}
    spec = importlib.util.spec_from_file_location(
        "lolla_consumer_context_pressure_validator",
        validator_path,
    )
    if spec is None or spec.loader is None:
        return ["could not load consumer-context validator"], {"status": "invalid"}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(root, contract_override=contract_override)


def _require_terms(text: str, terms: tuple[str, ...], label: str, errors: list[str]) -> None:
    lowered = re.sub(r"\s+", " ", text.lower())
    for term in terms:
        if term not in lowered:
            errors.append(f"{label} missing required public-handoff term: {term}")


def _validate_local_links(root: Path, path: Path, text: str) -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        local = target.split("#", 1)[0]
        if not local:
            continue
        count += 1
        resolved = (path.parent / local).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"current documentation link escapes repository: {path.relative_to(root)} -> {target}")
            continue
        if not resolved.exists():
            errors.append(f"current documentation link missing: {path.relative_to(root)} -> {target}")
    return count, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, receipt = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
