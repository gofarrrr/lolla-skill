from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "lolla.repository_local_authority_register.v1"
DEFAULT_REGISTER = Path("docs/evals/lolla-repository-local-authority-register-v1.json")
TEXT_SUFFIXES = frozenset({".json", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"})
EXCLUDED_DIRECTORY_NAMES = frozenset(
    {".git", ".pytest_cache", "__pycache__", "node_modules", "artifacts"}
)
ACTIVE_ROOT_FILES = (
    Path("AGENTS.md"),
    Path("HOW_IT_WORKS.md"),
    Path("PROJECT_STATUS.md"),
    Path("README.md"),
    Path("SKILL.md"),
)
ACTIVE_DIRECTORIES = (
    Path("agents"),
    Path("engine"),
    Path("scripts"),
    Path("observatory"),
    Path("references"),
    Path("tests"),
    Path("docs/skill"),
    Path("docs/how-it-works"),
    Path("data/curation"),
    Path(".codex/skills"),
)
ACTIVE_DOCUMENTS = (
    Path("docs/README.md"),
    Path("docs/product/observatory-source-ownership-audit-v0.md"),
    Path("docs/product/mental-model-teacher-observatory-ownership-portability-boundary-v0.md"),
    Path("docs/product/observatory-global-product-experience-and-data-flow-v0.md"),
    Path("docs/conversation-understanding/lolla-graph-substrate-audit-workbook-2026-07-22.md"),
    Path("docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md"),
    Path("docs/conversation-understanding/lolla-pressure-understanding-and-graph-evidence-prd-v0.md"),
    Path("docs/conversation-understanding/lolla-graph-substrate-custody-and-reproducibility-prd-v0.md"),
    Path("docs/conversation-understanding/lolla-constitutional-pressure-portfolio-custody-prd-v0.md"),
    Path("docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md"),
    Path("plans/lolla-self-contained-graph-substrate-and-skill-plan-2026-07-22.md"),
    Path("plans/lolla-pressure-understanding-and-graph-evidence-plan-2026-07-22.md"),
    Path("docs/evals/lolla-pressure-understanding-graph-evidence-package-v1.json"),
    Path("docs/evals/lolla-self-contained-skill-readiness-v1.json"),
    Path("data/model_sources/manifest.json"),
    Path("data/model_affordances/pilot_manifest.json"),
    Path("data/curation/relation_semantics_manifest.json"),
    Path("data/curated/canonical_id_migrations.json"),
    Path("reviews/codex-assisted/observatory-source-ownership-audit-v0/review.json"),
)
FROZEN_CURRENT_ARTIFACT_EXCEPTIONS = {
    Path("data/compiled/model_affordances/affordances_v60.json"): {
        "sha256": "4dea740ecf71894a8b56146502983c4d3e448f24a6628a8430a445b3c47bedc8",
        "reason": (
            "hash-locked live artifact referenced by frozen experiments; its inert "
            "historical source-residency metadata is not an active dependency"
        ),
        "allowed_marker_count": 2,
        "retirement_phase": "phase_6_repository_local_skill_packaging",
    }
}


class RepositoryLocalAuthorityError(RuntimeError):
    pass


def _retired_markers() -> tuple[str, ...]:
    retired_name = "Lolla-" + "system-b"
    return (
        retired_name,
        retired_name.lower(),
        "/Users/" + "marcin/Desktop/Apps/Lolla",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _eligible_text_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for relative in ACTIVE_ROOT_FILES + ACTIVE_DOCUMENTS:
        path = root / relative
        if path.is_file() and path not in seen:
            seen.add(path)
            yield path
    for relative_dir in ACTIVE_DIRECTORIES:
        directory = root / relative_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            relative_parts = path.relative_to(root).parts
            if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative_parts):
                continue
            if path not in seen:
                seen.add(path)
                yield path


def _marker_hits(path: Path, markers: Sequence[str]) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    hits: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        matched = sorted({marker for marker in markers if marker in line})
        if matched:
            hits.append(
                {
                    "line": line_number,
                    "marker_classes": [
                        "retired_project_name"
                        if "system-b" in marker.lower()
                        else "retired_machine_project_path"
                        for marker in matched
                    ],
                }
            )
    return hits


def build_repository_local_authority_register(
    root: Path = REPO_ROOT,
) -> dict[str, Any]:
    root = Path(root).resolve()
    markers = _retired_markers()
    active_violations: list[dict[str, Any]] = []
    active_file_count = 0
    for path in _eligible_text_files(root):
        active_file_count += 1
        hits = _marker_hits(path, markers)
        if hits:
            active_violations.append(
                {
                    "path": str(path.relative_to(root)),
                    "hits": hits,
                }
            )

    exceptions: list[dict[str, Any]] = []
    for relative, contract in sorted(
        FROZEN_CURRENT_ARTIFACT_EXCEPTIONS.items(), key=lambda item: str(item[0])
    ):
        path = root / relative
        if not path.is_file():
            raise RepositoryLocalAuthorityError(
                f"declared frozen exception is missing: {relative}"
            )
        observed_sha = _sha256(path)
        if observed_sha != contract["sha256"]:
            raise RepositoryLocalAuthorityError(
                f"declared frozen exception hash drifted: {relative}"
            )
        hits = _marker_hits(path, markers)
        marker_count = sum(len(hit["marker_classes"]) for hit in hits)
        if marker_count != int(contract["allowed_marker_count"]):
            raise RepositoryLocalAuthorityError(
                f"declared frozen exception marker count drifted: {relative}"
            )
        exceptions.append(
            {
                "path": str(relative),
                "sha256": observed_sha,
                "marker_count": marker_count,
                "reason": contract["reason"],
                "active_dependency": False,
                "retirement_phase": contract["retirement_phase"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "complete" if not active_violations else "failed",
        "created_date": "2026-07-22",
        "authority": {
            "repository_role": "sole_active_project_authority",
            "other_repository_required": False,
            "machine_specific_project_path_allowed": False,
        },
        "active_scan": {
            "scanned_file_count": active_file_count,
            "violation_count": len(active_violations),
            "violations": active_violations,
        },
        "frozen_artifact_exceptions": exceptions,
        "historical_scope_policy": {
            "historical_research_and_hash_locked_outputs_rewritten": False,
            "historical_mentions_are_not_current_instructions": True,
            "new_current_surfaces_may_not_copy_historical_machine_paths": True,
        },
        "non_claims": [
            "absence_of_active_path_references_is_not_complete_source_lineage",
            "repository_locality_is_not_semantic_correctness",
            "frozen_metadata_exception_is_not_an_active_dependency",
        ],
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate that current Lolla surfaces have repository-local authority."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--register", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    payload = build_repository_local_authority_register(root)
    if payload["status"] != "complete":
        raise RepositoryLocalAuthorityError(
            "active project surfaces still reference a retired project location"
        )

    register = args.register or args.output
    register = register if register.is_absolute() else root / register
    if args.validate_only:
        if not register.is_file():
            raise RepositoryLocalAuthorityError(f"authority register is missing: {register}")
        observed = json.loads(register.read_text(encoding="utf-8"))
        if observed != payload:
            raise RepositoryLocalAuthorityError(
                "authority register differs from the current provider-free scan"
            )
    else:
        output = args.output if args.output.is_absolute() else root / args.output
        _write(output, payload)

    print(
        json.dumps(
            {
                "status": "valid" if args.validate_only else "written",
                "register": str(register.relative_to(root)),
                "active_files_scanned": payload["active_scan"]["scanned_file_count"],
                "active_violations": payload["active_scan"]["violation_count"],
                "frozen_artifact_exceptions": len(
                    payload["frozen_artifact_exceptions"]
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
