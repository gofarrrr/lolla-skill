from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

PACKAGE_DIRECTORIES = (
    "agents",
    "engine",
    "scripts",
    "references",
    "docs/skill",
    "data/model_sources",
    "data/curation",
)
PACKAGE_FILES = (
    "AGENTS.md",
    "HOW_IT_WORKS.md",
    "PROJECT_STATUS.md",
    "README.md",
    "SKILL.md",
    "data/knowledge_graph.json",
    "data/relationship_graph.json",
    "data/embeddings.db",
    "data/compiled/model_affordances/affordances_v60.json",
    "data/curated/canonical_id_migrations.json",
    "data/model_affordances/pilot_manifest.json",
    "docs/evals/lolla-graph-substrate-baseline-v1.json",
    "docs/evals/lolla-self-contained-skill-readiness-v1.json",
)


def _hardlink_copy(source: str, destination: str) -> str:
    os.link(source, destination)
    return destination


def _copy_isolated_package(destination: Path) -> None:
    destination.mkdir()
    for relative in PACKAGE_DIRECTORIES:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            target,
            copy_function=_hardlink_copy,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for relative in PACKAGE_FILES:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(source, target)


def test_checked_in_readiness_register_is_current_and_provider_free() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/validate_self_contained_skill.py",
            "--validate-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "OPENROUTER_API_KEY": "",
            "LOLLA_OPENROUTER_API_KEY": "",
            "OPENAI_API_KEY": "",
        },
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary == {
        "model_count": 222,
        "policy_window_count": 163,
        "provider_calls": 0,
        "published_byte_equivalent": True,
        "register": "docs/evals/lolla-self-contained-skill-readiness-v1.json",
        "relation_count": 1358,
        "status": "valid",
    }


def test_isolated_repository_package_needs_no_original_checkout_or_provider(
    tmp_path: Path,
) -> None:
    isolated = tmp_path / "lolla-clean-clone"
    _copy_isolated_package(isolated)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/validate_self_contained_skill.py",
            "--validate-only",
        ],
        cwd=isolated,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PYTHONPATH": str(isolated),
            "OPENROUTER_API_KEY": "",
            "LOLLA_OPENROUTER_API_KEY": "",
            "OPENAI_API_KEY": "",
        },
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["status"] == "valid"
    assert summary["provider_calls"] == 0
    assert summary["published_byte_equivalent"] is True
