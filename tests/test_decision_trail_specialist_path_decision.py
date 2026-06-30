from __future__ import annotations

from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-path-decision-v0.md"
)


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_pr94_selects_local_private_packet_mode_next() -> None:
    text = _doc_text()

    assert "Selected outcome: **Outcome A: implement local-private Decision Trail packet" in text
    assert "PR95 Decision Trail Local-Private Packet Mode v0" in text
    assert "The main bottleneck is now source access, not contract shape." in text


def test_pr94_rejects_wrong_next_paths() -> None:
    text = _doc_text()

    for heading in (
        "Rejected Outcome B: Tiny Specialist Batch Over Current Packets",
        "Rejected Outcome C: Simplify Or Stop The Specialist Lane",
        "Rejected Outcome D: Pause Until Human Review",
        "Rejected Outcome E: Runtime Integration",
        "Rejected Outcome F: Broad Conversation Understanding IR",
    ):
        assert heading in text


def test_pr95_boundary_mentions_required_do_and_do_not_items() -> None:
    text = _doc_text()

    for required in (
        "require explicit `--mode local_private_mode`",
        "refuse output inside the archive run directory",
        "record `raw_private_content_included` truthfully",
        "record a read manifest of local private artifacts inspected",
        "test local-private behavior only with synthetic temp run directories",
        "document that local-private packets are not safe for commit by default",
    ):
        assert required in text
    for forbidden in (
        "run `$lolla`",
        "invoke the Lolla skill",
        "call providers or models",
        "mutate archives",
        "touch `SKILL.md`",
        "touch `scripts/skill/*`",
        "create specialist outputs",
        "execute fan-in",
        "score answer quality",
        "authorize agent action",
    ):
        assert forbidden in text


def test_pr94_preserves_non_claims_and_falsification() -> None:
    text = _doc_text()

    for non_claim in (
        "Lolla improves decisions",
        "Decision Trail is product-ready",
        "local-private mode will solve interpretation",
        "human validation exists",
        "clean artifacts imply good advice",
        "an agent may act",
    ):
        assert non_claim in text
    assert "What Would Falsify The Selected Path" in text
    assert "local-private packets require copying too much raw/private content" in text


def test_pr94_has_no_forbidden_authority_language_or_privacy_markers() -> None:
    text = _doc_text()

    for forbidden in (
        "safe" + "_for_" + "agent" + "_use",
        "quality_score",
        "answer_quality_score",
        "improvement_score",
        "judge_score",
        "winner",
        "approved",
        "certified",
        "pass_fail",
        "/User" + "s/",
        "SEC" + "RET",
        "raw_message_" + "content",
        "client_" + "secret",
        "api_" + "key",
        "pass" + "word",
    ):
        assert forbidden not in text


def test_pr78_lint_passes_pr94_doc() -> None:
    report = lint_product_delta_paths([DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
