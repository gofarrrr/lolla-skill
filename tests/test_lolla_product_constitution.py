from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = (
    REPO_ROOT
    / "docs/conversation-understanding/lolla-product-constitution-v0.md"
)
CONSTITUTION_V1 = (
    REPO_ROOT
    / "docs/conversation-understanding/lolla-product-constitution-v1.md"
)
CONSTITUTION_V2 = (
    REPO_ROOT
    / "docs/conversation-understanding/lolla-product-constitution-v2.md"
)
CONSTITUTION_V3 = (
    REPO_ROOT
    / "docs/conversation-understanding/lolla-product-constitution-v3.md"
)
HANDOFF = (
    REPO_ROOT
    / "docs/conversation-understanding/reasoning-pressure-handoff-v0.md"
)


def test_constitution_preserves_breadth_without_context_dumping() -> None:
    text = CONSTITUTION.read_text(encoding="utf-8")
    assert "Cap prose, not possibility" in text
    assert "Broad availability, compact representation, delayed rejection" in text
    assert "active working set" in text
    assert "edge/latticework reserve" in text
    assert "parked-but-preserved" in text
    assert "false stand-down" in text.lower()
    assert "Context dumping" in text
    assert "Discovery noise and visible friction have different bars" in text
    assert "candidate-stage success = preserve inspectable possibility" in text


def test_constitution_keeps_hybrid_and_human_authority_boundaries() -> None:
    text = CONSTITUTION.read_text(encoding="utf-8")
    assert "Freedom of conclusion, not freedom from consideration" in text
    assert "Deterministic code does not understand messy meaning" in text
    assert "questions, not invented facts" in text
    assert "The human retains responsibility for the decision" in text
    assert "A receipt proves process, not wisdom" in text


def test_constitution_requires_dated_current_practice_checks() -> None:
    text = CONSTITUTION_V1.read_text(encoding="utf-8")
    assert "Current practice must be checked, dated, and explicit" in text
    assert "incorporates" in text
    assert "lolla-product-constitution-v0.md" in text
    assert "v0 file remains immutable" in text
    assert "The model's remembered knowledge is not sufficient authority" in text
    assert "current primary documentation and capability metadata" in text
    assert "at least one maintained practitioner implementation" in text
    assert "For provider-backed experiments, this review happens before calls" in text
    assert "practices adopted, practices rejected, and" in text
    assert "Stale-practice certainty" in text
    assert "Training memory is a" in text
    assert "starting hypothesis, not a current technical source" in text
    assert "structured-extraction-practices-july-2026.md" in text


def test_small_handoff_is_only_the_active_slice() -> None:
    constitution = CONSTITUTION.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "active working set only" in constitution
    assert "active working-set slice" in handoff
    assert "It is not the whole" in handoff
    assert "delayed rejection" in handoff


def test_constitution_v2_binds_context_supported_labels_and_fan_in_budget() -> None:
    text = CONSTITUTION_V2.read_text(encoding="utf-8")
    assert "lolla-product-constitution-v1.md" in text
    assert "V0\nand v1 remain immutable" in text
    assert "Semantic responsibility must match visible context" in text
    assert "complementary lenses, not deterministic routing silos" in text
    assert "fan-in is bounded" in text
    assert "Context-invisible labels and hidden fan-in overload" in text


def test_constitution_v3_requires_problem_class_research_before_more_tuning() -> None:
    text = CONSTITUTION_V3.read_text(encoding="utf-8")
    assert "lolla-product-constitution-v2.md" in text
    assert "Persistent failure triggers problem-class research" in text
    assert "same material failure survives two" in text
    assert "exact observed signature" in text
    assert "maintained reference implementations, benchmarks, repositories, or issue" in text
    assert "dated problem-class note" in text
    assert "Another paid call, prompt variant, provider swap, or" in text
    assert "architecture layer is not authorized" in text
    assert "External popularity does not override Lolla's" in text
    assert "Local reinvention loops" in text
