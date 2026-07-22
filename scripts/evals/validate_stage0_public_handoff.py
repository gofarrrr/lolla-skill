#!/usr/bin/env python3
"""Validate the provider-free current public and cold-start handoff."""
from __future__ import annotations

import argparse
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
    "docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md",
    "docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md",
    "references/knowledge-substrate-operations.md",
    "plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md",
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
    "docs/evals/lolla-constitution-stage0-addendum-register-v1.json",
    "docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md",
    "docs/conversation-understanding/lolla-product-constitution-v5.md",
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
    _require_terms(
        (root / "plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md").read_text(encoding="utf-8"),
        (
            "stage 0 and 0.6 are",
            "exact checked-in-safe case packet",
            "no later evidence stage is authorized",
        ),
        "plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md",
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
        errors.append("cold-reader questions must match the sixteen-question orientation contract")
    for item in questions:
        if not item.get("expected_answer"):
            errors.append(f"cold-reader answer missing: {item.get('id')}")
        evidence = item.get("evidence", [])
        if not evidence:
            errors.append(f"cold-reader evidence missing: {item.get('id')}")
        for relative in evidence:
            if not (root / relative).exists():
                errors.append(f"cold-reader evidence path missing: {relative}")

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
        "current_entrypoint_count": len(texts),
        "local_link_count": link_count,
        "provider_calls": packet.get("provider_calls"),
        "provider_cost_usd": float(packet.get("provider_cost_usd", -1)),
        "required_file_count": len(REQUIRED_FILES),
        "schema_version": "lolla.public_handoff_validation.v2",
        "status": "valid" if not errors else "invalid",
    }
    return errors, receipt


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
