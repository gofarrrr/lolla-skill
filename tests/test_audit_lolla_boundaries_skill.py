from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".codex/skills/audit-lolla-boundaries"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
METADATA_PATH = SKILL_ROOT / "agents/openai.yaml"
REFERENCE_PATH = SKILL_ROOT / "references/evidence-gates.md"


def _frontmatter_lines() -> list[str]:
    text = SKILL_PATH.read_text(encoding="utf-8")
    _, raw, _ = text.split("---", 2)
    return [line for line in raw.splitlines() if line.strip()]


def test_skill_has_only_supported_frontmatter_and_maintainer_trigger() -> None:
    frontmatter = _frontmatter_lines()

    assert len(frontmatter) == 2
    assert frontmatter[0] == "name: audit-lolla-boundaries"
    assert frontmatter[1].startswith("description: ")
    description = frontmatter[1].removeprefix("description: ")
    assert "knowledge substrate" in description
    assert "parallel systems" in description
    assert "Do not use this maintainer skill to run" in description


def test_skill_is_not_a_second_runtime_or_semantic_authority() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")
    reference = REFERENCE_PATH.read_text(encoding="utf-8")
    text_flat = " ".join(text.split())
    reference_flat = " ".join(reference.split())

    for required in (
        "Do not create a second compiler",
        "human: semantic correction, usefulness, and action authority",
        "Preserve frozen experiment artifacts and PR104's blank human fields",
        "call a provider or rebuild embeddings",
        "same-context self-justification",
        "mandatory absorption in either context",
    ):
        assert required in text_flat
    for required in (
        "The layer after an error cannot certify the layer before it",
        "### A. Pressure now",
        "### B. Understand later",
        "### C. Improve the conversation-to-graph bridge",
        "Candidate survival also cannot prove independent consideration",
        "A lower application rate does not establish domestication",
        "test exactly one alternative",
    ):
        assert required in reference_flat


def test_skill_metadata_invokes_exact_repo_local_skill() -> None:
    metadata = METADATA_PATH.read_text(encoding="utf-8")

    assert 'display_name: "Lolla Boundary Audit"' in metadata
    short = "Audit Lolla without parallel systems"
    assert f'short_description: "{short}"' in metadata
    assert 25 <= len(short) <= 64
    assert "$audit-lolla-boundaries" in metadata
