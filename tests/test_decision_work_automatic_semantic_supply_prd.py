from __future__ import annotations

from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
BRIEF_PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
RUNTIME_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"

REQUIRED_NEXT_PRS = {
    "PR178 Decision Work Automatic Semantic Supply PRD v0",
    "PR179 Offline Interpretation Queue Contract v0",
    "PR180 Offline Interpretation Queue Packet Builder v0",
    "PR181 Operator/Codex Interpretation Prompt Packet v0",
    "PR182 Generated Interpretation Read Intake And Validator v0",
    "PR183 Three-Case Generated Interpretation Read Intake Review v0",
    "PR184 Operator/Codex Generated Read Pilot v0",
    "PR185 Generated Read To Brief Supply Plan v0",
    "PR186 Decision Work Generated Read Brief Supply Adapter v0",
    "PR187 Decision Work Generated Read Brief Rendering Pilot v0",
    "PR188 Decision Work Generated Read Brief vs Existing Brief Review v0",
    "PR189 Second Generated Read Brief Rendering Pilot v0",
    "PR190 Two-Case Generated Read Brief Pattern Review v0",
    "PR191 Decision Work Generated Read Triage Supply Plan v0",
}
REQUIRED_REUSED_ARTIFACTS = {
    "Decision Work Conversation Interpretation Offline Packet",
    "Decision Work Conversation Interpretation Read Schema",
    "Decision Work Brief Enrichment Rules Contract",
    "Decision Work Automatic Triage Contract",
    "Decision Work Brief Runtime Safe Supply Resolver",
    "Decision Work Brief Runtime Bundle Resolver Integration",
    "Decision Work Brief Runtime-Attached Internal v1 Package Refresh",
}
STOP_LINES = {
    "make runtime attachment default-on",
    "perform direct runtime interpretation",
    "copy raw/private conversation text into checked-in artifacts",
    "score answer quality",
    "create approval labels",
    "claim human validation",
    "claim product proof",
    "claim advice correctness",
    "authorize agent or automatic action",
}
PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prd_exists_and_names_finished_product_target() -> None:
    text = _text(PRD_PATH)

    assert "# Decision Work Automatic Semantic Supply PRD v0" in text
    assert "Finished Product Target" in text
    assert "newly completed Lolla run" in text
    assert "offline interpretation queue" in text
    assert "runtime sidecar update or deferred/blocked state" in text
    assert "The runtime hook should remain a sidecar writer" in text


def test_prd_is_not_theater_about_curated_cases() -> None:
    text = _text(PRD_PATH)

    assert "The three current known cases are useful regression fixtures" in text
    assert "They prove the evidence chain and runtime sidecar path can work" in text
    assert "The system does not yet automatically create useful Decision Work material for" in text
    assert "For a new completed run" in text
    assert "Without those refs, the correct behavior is to defer" in text


def test_prd_reuses_existing_artifacts_instead_of_parallel_system() -> None:
    text = _text(PRD_PATH)

    for artifact in REQUIRED_REUSED_ARTIFACTS:
        assert artifact in text
    assert "reuse existing work instead of inventing a" in text


def test_prd_contains_ordered_next_pr_sequence() -> None:
    text = _text(PRD_PATH)

    for pr in REQUIRED_NEXT_PRS:
        assert pr in text
    assert text.index("PR178 Decision Work Automatic Semantic Supply PRD v0") < text.index(
        "PR191 Decision Work Generated Read Triage Supply Plan v0"
    )


def test_prd_keeps_direct_runtime_interpretation_and_authority_out_of_scope() -> None:
    text = _text(PRD_PATH)

    for stop_line in STOP_LINES:
        assert stop_line in text
    assert "runtime hook -> raw conversation -> model call -> user-facing claim" in text
    assert "Do not make this shape" in text
    assert "completed archive" in text
    assert "bounded LLM/Codex interpretation read" in text
    assert "deterministic validation" in text


def test_front_door_docs_link_the_prd() -> None:
    rel = "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
    conversation_rel = "decision-work-automatic-semantic-supply-prd-v0.md"
    board_rel = (
        "../conversation-understanding/"
        "decision-work-automatic-semantic-supply-prd-v0.md"
    )

    assert conversation_rel in _text(BRIEF_PRD_PATH)
    assert conversation_rel in _text(RUNTIME_PRD_PATH)
    assert rel in _text(README_PATH)
    assert rel in _text(HOW_IT_WORKS_PATH)
    assert board_rel in _text(BOARD_README_PATH)
    assert rel in _text(PROGRESS_PATH)


def test_prd_and_touched_docs_pass_boundary_lint() -> None:
    result = lint_product_delta_paths(
        [
            PRD_PATH,
            BRIEF_PRD_PATH,
            RUNTIME_PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            BOARD_README_PATH,
            PROGRESS_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_prd_has_no_private_markers() -> None:
    text = _text(PRD_PATH)

    for marker in PRIVATE_MARKERS:
        assert marker not in text
