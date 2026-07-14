from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRACTICES = (
    ROOT
    / "docs/conversation-understanding/structured-extraction-practices-july-2026.md"
)
PRACTICES_AMENDMENT = (
    ROOT
    / "docs/conversation-understanding/structured-extraction-practices-amendment-2026-07-11.md"
)
RECOVERY = ROOT / "plans/conversation-state-extraction-recovery-2026-07-11.md"
ROADMAP = ROOT / "docs/evals/lolla-eight-gate-roadmap-v0.md"


def test_practice_review_preserves_current_sources_and_freeze_gate() -> None:
    text = PRACTICES.read_text(encoding="utf-8")
    for source in (
        "developers.openai.com/api/docs/guides/structured-outputs",
        "ai.google.dev/gemini-api/docs/structured-output",
        "openrouter.ai/docs/guides/features/structured-outputs",
        "pydantic.dev/docs/ai/core-concepts/output",
        "github.com/567-labs/instructor",
        "github.com/dottxt-ai/outlines",
    ):
        assert source in text
    for rule in (
        "one typed source of truth",
        "provider-specific schema projection",
        "explicit abstention/ambiguity",
        "no deterministic component makes a semantic relevance decision",
        "No extraction call is authorized",
    ):
        assert rule in text


def test_recovery_plan_is_provider_free_and_cross_case_before_calls() -> None:
    text = RECOVERY.read_text(encoding="utf-8")
    for stage in ("R1", "R2", "R3", "R4", "R5"):
        assert f"### {stage}" in text
    assert "Include all five designed cases" in text
    assert "only then decide whether a bounded provider call is justified" in text
    assert "no graph calls" in text
    assert "no hidden correction loop" in text


def test_active_roadmap_links_practices_and_recovery_plan() -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    assert "structured-extraction-practices-july-2026.md" in text
    assert "conversation-state-extraction-recovery-2026-07-11.md" in text


def test_practices_amendment_preserves_locked_base_and_adds_fan_in_rules() -> None:
    text = PRACTICES_AMENDMENT.read_text(encoding="utf-8")
    assert "without modifying that" in text
    assert "bounded probabilistic consolidation" in text
    assert "Budget fan-in, not only fan-out" in text
    assert "Label only what the task context can support" in text
    assert "global synthesis must not silently strengthen it" in text
