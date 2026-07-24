#!/usr/bin/env python3
"""Validate the repository-contained Lolla skill without provider calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.compilation_bundle import KnowledgeCompiler  # noqa: E402
from engine.system_b.constitutional_pressure_survival import (  # noqa: E402
    build_constitutional_graph_survival_from_snapshot,
)
from engine.system_b.constitutional_pressure_planner import (  # noqa: E402
    ConstitutionalPressurePolicy,
)
from engine.system_b.published_knowledge_substrate import (  # noqa: E402
    PublishedKnowledgeSubstrate,
)
from engine.system_b.source_custody import build_source_custody_report  # noqa: E402
from scripts.evals.validate_repository_local_authority import (  # noqa: E402
    build_repository_local_authority_register,
)
from scripts.product.adopt_graph_compiler_inputs import (  # noqa: E402
    validate as validate_compiler_inputs,
)
from scripts.product.adopt_relation_semantics_authoring import (  # noqa: E402
    validate as validate_relation_authoring,
)


SCHEMA_VERSION = "lolla.self_contained_skill_readiness.v1"
DEFAULT_REGISTER = Path("docs/evals/lolla-self-contained-skill-readiness-v1.json")
REQUIRED_PACKAGE_FILES = (
    "SKILL.md",
    "README.md",
    "HOW_IT_WORKS.md",
    "agents/openai.yaml",
    "docs/skill/STEPS.md",
    "docs/skill/CODEX_LIVE_RUN_BOUNDARY.md",
    "references/knowledge-substrate-operations.md",
    "engine/system_b/private_runtime.py",
    "scripts/skill/setup.sh",
    "scripts/skill/load_run_state.sh",
    "scripts/skill/capture_step.sh",
    "scripts/skill/run_extract_step.sh",
    "scripts/skill/run_pipeline_step.sh",
    "scripts/skill/persist_private_step.sh",
    "scripts/skill/persist_private_artifact.py",
    "scripts/skill/prepare_consumer_step.sh",
    "scripts/skill/prepare_consumer_packet.py",
    "scripts/skill/persist_default_pressure_step.sh",
    "scripts/skill/persist_default_off_pressure_check.py",
    "scripts/skill/render_memo_step.sh",
    "scripts/skill/finalize_and_archive.sh",
    "data/knowledge_graph.json",
    "data/relationship_graph.json",
    "data/model_sources/manifest.json",
    "data/curation/relation_semantics_manifest.json",
    "data/curation/relation_source_anchor_register.json",
    "data/curation/compiler_inputs_manifest.json",
    "data/curation/graph_compiler_contract.json",
    "data/curation/published_substrate_release.json",
    "data/curation/constitutional_pressure_policy_v1.json",
    "docs/evals/lolla-graph-substrate-baseline-v1.json",
)
SOURCE_CUSTODY_ERROR_FIELDS = (
    "missing_manifest_model_ids",
    "manifest_model_ids_outside_runtime_graph",
    "duplicate_manifest_model_ids",
    "missing_local_source_model_ids",
    "source_file_mismatch_model_ids",
    "local_sha256_mismatch_model_ids",
    "local_byte_mismatch_model_ids",
    "missing_canonical_source_model_ids",
    "canonical_sha256_mismatch_model_ids",
)


class SelfContainedSkillError(RuntimeError):
    """Raised when the distributable skill package is incomplete or drifts."""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_value(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _candidate_rows(model_ids: Sequence[str]) -> list[dict[str, object]]:
    return [
        {
            "model_id": model_id,
            "model_name": model_id,
            "recall_source": "self_contained_skill_readiness",
            "final_rank": index,
        }
        for index, model_id in enumerate(model_ids, start=1)
    ]


def _skill_structure(root: Path) -> dict[str, Any]:
    missing = [relative for relative in REQUIRED_PACKAGE_FILES if not (root / relative).is_file()]
    if missing:
        raise SelfContainedSkillError(
            "required repository-contained skill files are missing: " + ", ".join(missing)
        )

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", skill_text, re.DOTALL)
    if match is None:
        raise SelfContainedSkillError("SKILL.md has no valid YAML frontmatter boundary")
    frontmatter = match.group(1)
    if not re.search(r"^name:\s*lolla\s*$", frontmatter, re.MULTILINE):
        raise SelfContainedSkillError("SKILL.md does not declare the canonical lolla name")
    if not re.search(r"^description:\s*>\s*$", frontmatter, re.MULTILINE):
        raise SelfContainedSkillError("SKILL.md has no folded trigger description")
    if "references/knowledge-substrate-operations.md" not in skill_text:
        raise SelfContainedSkillError("SKILL.md does not expose the substrate reference directly")

    steps_text = (root / "docs/skill/STEPS.md").read_text(encoding="utf-8")
    contract_text = skill_text + "\n" + steps_text
    invoked = sorted(
        set(
            re.findall(
                r"\$SKILL_DIR/([A-Za-z0-9_./-]+)",
                contract_text,
            )
        )
        | set(
            re.findall(
                r"(?<![A-Za-z0-9_./-])(scripts/skill/[A-Za-z0-9_.-]+)",
                contract_text,
            )
        )
    )
    missing_invoked = [relative for relative in invoked if not (root / relative).is_file()]
    if missing_invoked:
        raise SelfContainedSkillError(
            "skill-invoked files are missing: " + ", ".join(missing_invoked)
        )

    setup_text = (root / "scripts/skill/setup.sh").read_text(encoding="utf-8")
    if "${BASH_SOURCE[0]}" not in setup_text or "_LOLLA_SCRIPT_DIR/../.." not in setup_text:
        raise SelfContainedSkillError("setup.sh does not self-resolve its bundled skill root")
    forbidden_setup_fragments = (
        'SKILL_DIR="$HOME/.codex/skills/lolla"',
        'SKILL_DIR="$HOME/.claude/skills/lolla"',
        'SKILL_DIR=".codex/skills/lolla"',
        'SKILL_DIR=".claude/skills/lolla"',
    )
    if any(fragment in setup_text for fragment in forbidden_setup_fragments):
        raise SelfContainedSkillError("setup.sh still searches for a separate skill copy")

    metadata_text = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if "$lolla" not in metadata_text:
        raise SelfContainedSkillError("Codex skill metadata has no explicit $lolla prompt")

    return {
        "status": "complete",
        "canonical_skill_count": 1,
        "canonical_skill_path": "SKILL.md",
        "direct_substrate_reference": "references/knowledge-substrate-operations.md",
        "required_package_file_count": len(REQUIRED_PACKAGE_FILES),
        "invoked_repository_file_count": len(invoked),
        "missing_required_files": [],
        "missing_invoked_files": [],
        "setup_root_resolution": "bundled_script_location",
        "claude_invocation": "/lolla",
        "codex_invocation": "$lolla",
    }


def _source_and_curation(root: Path) -> dict[str, Any]:
    source = build_source_custody_report(root)
    bad_fields = [field for field in SOURCE_CUSTODY_ERROR_FIELDS if source[field]]
    if bad_fields:
        raise SelfContainedSkillError(
            "repository-local source custody failed: " + ", ".join(bad_fields)
        )

    relations = validate_relation_authoring(root, write_manifest=False)
    compiler_inputs = validate_compiler_inputs(root, write=False)
    return {
        "status": "complete",
        "canonical_markdown_count": source["runtime_model_count"],
        "source_manifest_count": source["manifest_model_count"],
        "relation_authoring_record_count": relations["coverage"]["active_record_count"],
        "rich_relation_count": relations["coverage"]["relation_count"],
        "relation_authoring_set_sha256": relations["coverage"][
            "active_record_set_sha256"
        ],
        "compiler_input_set_count": len(compiler_inputs["input_sets"]),
        "other_repository_required": False,
    }


def _compile_and_load(root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="lolla-skill-readiness-") as temporary:
        output = Path(temporary) / "candidate"
        result = KnowledgeCompiler.load(root).compile(output_dir=output)
        if not result.is_valid:
            raise SelfContainedSkillError(
                "candidate graph compilation failed: " + "; ".join(result.errors)
            )
        manifest = _load_json(output / "compilation_manifest.json")
        comparisons = manifest["published_comparison"]
        if not all(bool(row["byte_equivalent"]) for row in comparisons.values()):
            raise SelfContainedSkillError("candidate graph is not byte-equivalent to publication")

    load = PublishedKnowledgeSubstrate.open(root)
    snapshot = load.require_snapshot()
    if load.status != "complete":
        raise SelfContainedSkillError(f"published substrate load is {load.status}")
    return {
        "status": "complete",
        "candidate_only": True,
        "published_overwrite_performed": False,
        "published_byte_equivalent": True,
        "model_count": result.bundle.model_count,
        "knowledge_edge_count": result.bundle.knowledge_edge_count,
        "rich_relation_count": result.bundle.relationship_edge_count,
        "embedding_staleness": manifest["embedding_staleness"]["status"],
        "published_load_state": load.status,
        "published_release_id": snapshot.release_id,
        "runtime_generation_attempted": load.runtime_generation_attempted,
    }


def _policy_replay(root: Path) -> dict[str, Any]:
    policy = ConstitutionalPressurePolicy()
    checked_policy = _load_json(root / "data/curation/constitutional_pressure_policy_v1.json")
    if checked_policy != policy.contract():
        raise SelfContainedSkillError("checked-in constitutional policy differs from code")

    baseline = _load_json(root / "docs/evals/lolla-graph-substrate-baseline-v1.json")
    frozen = baseline["current_portfolio_characterization"]
    snapshot = PublishedKnowledgeSubstrate.open(root).require_snapshot()
    model_ids = sorted(snapshot.models)
    replayed_hashes: list[str] = []
    for expected in frozen["windows"]:
        start = int(expected["window_index"])
        window = model_ids[start : start + int(frozen["window_size"])]
        portfolio = build_constitutional_graph_survival_from_snapshot(
            candidates=_candidate_rows(window),
            substrate=snapshot,
        )
        if portfolio["portfolio_sha256"] != expected["portfolio_sha256"]:
            raise SelfContainedSkillError(
                f"pressure-policy baseline drifted at window {start}"
            )
        replayed_hashes.append(portfolio["portfolio_sha256"])

    return {
        "status": "complete",
        "policy_id": policy.policy_id,
        "policy_version": policy.version,
        "policy_sha256": policy.identity_sha256,
        "direction": policy.direction,
        "hop_depth": policy.hop_depth,
        "expansion_seed_rule": policy.expansion_seed_rule,
        "window_count": len(replayed_hashes),
        "portfolio_hashes_sha256": _sha256_value(replayed_hashes),
        "provider_calls": policy.provider_calls_allowed,
    }


def _runtime_import_boundary(root: Path) -> dict[str, Any]:
    """Prove the bundled live pipeline imports without caller-cwd assistance."""

    pipeline_script = root / "scripts/run_pipeline.py"
    probe = (
        "import runpy\n"
        f"runpy.run_path({str(pipeline_script)!r}, "
        "run_name='lolla_runtime_import_probe')\n"
        "from system_b.pipeline import SystemBPipeline\n"
        "print(SystemBPipeline.__name__)\n"
    )
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.update(
        {
            "OPENROUTER_API_KEY": "",
            "LOLLA_OPENROUTER_API_KEY": "",
            "OPENAI_API_KEY": "",
        }
    )
    with tempfile.TemporaryDirectory(prefix="lolla-runtime-import-") as temporary:
        result = subprocess.run(
            [sys.executable, "-I", "-c", probe],
            cwd=temporary,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    if result.returncode != 0 or result.stdout.strip() != "SystemBPipeline":
        diagnostic = result.stderr.strip()[-1200:] or result.stdout.strip()[-1200:]
        raise SelfContainedSkillError(
            "bundled pipeline import depends on caller working directory: "
            + diagnostic
        )
    return {
        "status": "complete",
        "caller_working_directory_required": False,
        "python_isolated_mode": True,
        "provider_calls": 0,
    }


def build_readiness_report(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    authority = build_repository_local_authority_register(root)
    if authority["status"] != "complete":
        raise SelfContainedSkillError("current repository surfaces contain retired paths")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
        "created_date": "2026-07-22",
        "evidence_type": "provider_free_isolated_package_readiness",
        "skill_structure": _skill_structure(root),
        "source_and_curation": _source_and_curation(root),
        "compiled_and_published_substrate": _compile_and_load(root),
        "pressure_policy_replay": _policy_replay(root),
        "runtime_import_boundary": _runtime_import_boundary(root),
        "repository_authority": {
            "status": authority["status"],
            "repository_role": authority["authority"]["repository_role"],
            "other_repository_required": authority["authority"]["other_repository_required"],
            "active_path_violations": authority["active_scan"]["violation_count"],
            "frozen_historical_metadata_exceptions": len(
                authority["frozen_artifact_exceptions"]
            ),
        },
        "provider_calls": 0,
        "embedding_calls": 0,
        "runtime_semantics_changed_by_validation": False,
        "non_claims": [
            "packaging_readiness_is_not_semantic_correctness",
            "byte_equivalence_is_not_product_usefulness",
            "policy_replay_is_not_relevance_proof",
            "provider_free_validation_does_not_authorize_a_live_run",
        ],
    }


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--register", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    payload = build_readiness_report(root)
    register = args.register or args.output
    register = register if register.is_absolute() else root / register
    if args.validate_only:
        if not register.is_file():
            raise SelfContainedSkillError(f"readiness register is missing: {register}")
        if _load_json(register) != payload:
            raise SelfContainedSkillError(
                "readiness register differs from the current provider-free package"
            )
    else:
        output = args.output if args.output.is_absolute() else root / args.output
        _write(output, payload)

    print(
        json.dumps(
            {
                "status": "valid" if args.validate_only else "written",
                "register": str(register.relative_to(root)),
                "model_count": payload["source_and_curation"]["canonical_markdown_count"],
                "relation_count": payload["source_and_curation"]["rich_relation_count"],
                "policy_window_count": payload["pressure_policy_replay"]["window_count"],
                "published_byte_equivalent": payload[
                    "compiled_and_published_substrate"
                ]["published_byte_equivalent"],
                "provider_calls": payload["provider_calls"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
