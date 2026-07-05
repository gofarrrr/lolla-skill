"""UX review packet builder for the Mental Model Teacher product lane.

This PR-P10 builder assembles review-facing Markdown and a blank human review
form from checked-in product pilot artifacts. It does not fill human judgments,
call providers, run Lolla, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT


PILOT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
SOURCE_ROOT = (
    REPO_ROOT / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-ux-review-packet-v0"
UX_REVIEW_PACKET_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.ux_review_packet_manifest.v0"
)
HUMAN_REVIEW_FORM_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.human_review_form.v0"
)
REVIEW_CRITERIA = (
    "educational_value",
    "clarity",
    "relation_understanding",
    "practice_usefulness",
    "non_overclaiming",
    "separation_from_decision_work",
)
REQUIRED_DECISION_WORK_BRIEFS = {
    "launch-public-enterprise-beta": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
    ),
    "deploy-assisted-intake-routing": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
    ),
    "ceo-remove-founding-cofounder": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
    ),
}


class MentalModelTeacherUxReviewPacketError(ValueError):
    """Raised when UX review packet assembly cannot complete safely."""


def build_ux_review_packet(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else REPO_ROOT
    target_dir = Path(output_dir)
    pilot_dir = repo_root / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
    source_root = (
        repo_root / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
    )
    manifest_path = pilot_dir / "manifest.json"
    pilot_manifest = _load_json(manifest_path)
    cases = [_case_review_item(repo_root, pilot_dir, source_root, item) for item in pilot_manifest["objects"]]
    form = _human_review_form(cases)

    _write(target_dir / "index.md", render_review_packet(cases))
    _write(target_dir / "human-review-form.md", render_human_review_form_markdown(form))
    _write_json(target_dir / "human-review-form.json", form)

    manifest = {
        "schema_version": UX_REVIEW_PACKET_MANIFEST_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_ux_review_packet",
        "status": "ux_review_packet_ready_for_human_review",
        "output_dir": _safe_display_path(target_dir),
        "source_pilot_manifest": _repo_rel(manifest_path),
        "case_count": len(cases),
        "criteria": list(REVIEW_CRITERIA),
        "packet": "index.md",
        "human_review_form_markdown": "human-review-form.md",
        "human_review_form_json": "human-review-form.json",
        "human_review_prefilled": False,
        "human_review_completed": False,
        "synthetic_review_diagnostic_only": True,
        "product_proof": False,
        "human_validated": False,
        "runtime_integration_authorized": False,
        "case_artifacts": [
            {
                "case_id": case["case_id"],
                "product_lesson_page": case["product_lesson_page"],
                "teacher_card": case["teacher_card"],
                "teacher_note": case["teacher_note"],
                "relation_page": case["relation_page"],
                "graph_neighborhood": case["graph_neighborhood"],
                "decision_work_boundary_reference": case[
                    "decision_work_boundary_reference"
                ],
            }
            for case in cases
        ],
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "synthetic_review_is_human_validation": False,
            "agent_or_automatic_action_authorized": False,
        },
        "stop_before": [
            "product readiness claim",
            "human validation claim",
            "package gate",
            "runtime integration",
            "provider or model calls",
        ],
    }
    _assert_no_local_paths(manifest)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def render_review_packet(cases: list[dict[str, Any]]) -> str:
    lines = [
        "# Mental Model Teacher UX Review Packet v0",
        "",
        "Status: ready for human review; not human-validated.",
        "",
        "This packet compares productized Teacher lesson pages, current Teacher cards and notes, relation source views, and graph-neighborhood JSON for the three Teacher pilot cases.",
        "",
        "The reviewer should judge learning value, not decision correctness.",
        "",
        "## Review Criteria",
        "",
    ]
    for criterion in REVIEW_CRITERIA:
        lines.append(f"- `{criterion}`")
    lines.extend(
        [
            "",
            "## Case Review Links",
            "",
            "| Case | Product lesson | Teacher card | Teacher note | Relation page | Graph neighborhood | Decision Work boundary reference |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for case in cases:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case['case_id']}`",
                    _md_link("lesson", case["product_lesson_page"], DEFAULT_OUTPUT_DIR / "index.md"),
                    _md_link("card", case["teacher_card"], DEFAULT_OUTPUT_DIR / "index.md"),
                    _md_link("note", case["teacher_note"], DEFAULT_OUTPUT_DIR / "index.md"),
                    _md_link("relation", case["relation_page"], DEFAULT_OUTPUT_DIR / "index.md"),
                    _md_link("graph", case["graph_neighborhood"], DEFAULT_OUTPUT_DIR / "index.md"),
                    _md_link(
                        "Decision Work brief",
                        case["decision_work_boundary_reference"],
                        DEFAULT_OUTPUT_DIR / "index.md",
                    ),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## What To Compare",
            "",
            "- Productized lesson pages should make the thinking move, model relationship, worked example, practice rep, source trail, and non-claims easier to inspect than raw Teacher cards or notes.",
            "- Current Teacher cards and notes are comparison artifacts, not product pages.",
            "- Relation pages in this packet are imported OKF source views, not full product relation pages for every case model.",
            "- Graph neighborhoods are JSON review artifacts, not browser graph UI and not proof of relation truth.",
            "- Decision Work briefs are boundary references only; they ask what decision artifact changed, while Teacher asks what reasoning move can be learned.",
            "",
            "## Human Review Form",
            "",
            "Use [the blank human review form](human-review-form.md). The form intentionally contains no positive defaults.",
            "",
            "## Non-Claims",
            "",
            "- `not_product_proof`",
            "- `not_human_validation`",
            "- `not_answer_correctness`",
            "- `not_advice_correctness`",
            "- `not_runtime_integration`",
            "- `not_action_authorization`",
            "- `synthetic_review_is_diagnostic_only`",
        ]
    )
    return _finish(lines)


def render_human_review_form_markdown(form: dict[str, Any]) -> str:
    lines = [
        "# Mental Model Teacher Human Review Form v0",
        "",
        "Status: blank form for human review.",
        "",
        "Do not complete this form synthetically. A synthetic or automated review is diagnostic only and is not human validation.",
        "",
        "Review question: does the productized Teacher surface teach the reasoning move better than the raw Teacher artifacts while preserving non-claims and separation from Decision Work?",
        "",
        "## Overall Decision",
        "",
        "- [ ] ready to package with caveats",
        "- [ ] needs model/page revision",
        "- [ ] needs relation/page revision",
        "- [ ] needs graph UX revision",
        "- [ ] needs human review before expansion",
        "- [ ] cannot judge from this packet",
        "",
        "Overall notes:",
        "",
        "```text",
        "",
        "```",
        "",
    ]
    for case in form["cases"]:
        lines.extend(
            [
                f"## Case: `{case['case_id']}`",
                "",
                f"- Product lesson: {_md_link('lesson', case['artifacts']['product_lesson_page'], DEFAULT_OUTPUT_DIR / 'human-review-form.md')}",
                f"- Teacher card: {_md_link('card', case['artifacts']['teacher_card'], DEFAULT_OUTPUT_DIR / 'human-review-form.md')}",
                f"- Teacher note: {_md_link('note', case['artifacts']['teacher_note'], DEFAULT_OUTPUT_DIR / 'human-review-form.md')}",
                f"- Relation page: {_md_link('relation', case['artifacts']['relation_page'], DEFAULT_OUTPUT_DIR / 'human-review-form.md')}",
                f"- Graph neighborhood: {_md_link('graph', case['artifacts']['graph_neighborhood'], DEFAULT_OUTPUT_DIR / 'human-review-form.md')}",
                "",
            ]
        )
        for criterion in REVIEW_CRITERIA:
            lines.extend(
                [
                    f"### `{criterion}`",
                    "",
                    "- [ ] strong",
                    "- [ ] adequate",
                    "- [ ] weak",
                    "- [ ] cannot judge",
                    "",
                    "Evidence or notes:",
                    "",
                    "```text",
                    "",
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "### Case Decision",
                "",
                "- [ ] productized page is more educational",
                "- [ ] raw Teacher card/note is more educational",
                "- [ ] no clear difference",
                "- [ ] cannot judge",
                "",
                "Case notes:",
                "",
                "```text",
                "",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary Acknowledgement",
            "",
            "- [ ] I did not treat this form as product proof.",
            "- [ ] I did not treat this form as answer correctness.",
            "- [ ] I did not treat graph edges as proof.",
            "- [ ] I did not authorize runtime or automatic action.",
        ]
    )
    return _finish(lines)


def _human_review_form(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": HUMAN_REVIEW_FORM_SCHEMA_VERSION,
        "status": "blank_pending_human_review",
        "human_review_completed": False,
        "human_validated": False,
        "product_proof": False,
        "prefilled_positive": False,
        "synthetic_review_diagnostic_only": True,
        "criteria": list(REVIEW_CRITERIA),
        "overall_decision": {
            "selected": None,
            "allowed_values": [
                "ready_to_package_with_caveats",
                "needs_model_page_revision",
                "needs_relation_page_revision",
                "needs_graph_ux_revision",
                "needs_human_review_before_expansion",
                "cannot_judge_from_packet",
            ],
            "notes": "",
        },
        "cases": [
            {
                "case_id": case["case_id"],
                "artifacts": {
                    "product_lesson_page": case["product_lesson_page"],
                    "teacher_card": case["teacher_card"],
                    "teacher_note": case["teacher_note"],
                    "relation_page": case["relation_page"],
                    "graph_neighborhood": case["graph_neighborhood"],
                    "decision_work_boundary_reference": case[
                        "decision_work_boundary_reference"
                    ],
                },
                "criteria": {
                    criterion: {
                        "selected": None,
                        "allowed_values": [
                            "strong",
                            "adequate",
                            "weak",
                            "cannot_judge",
                        ],
                        "evidence": "",
                        "notes": "",
                    }
                    for criterion in REVIEW_CRITERIA
                },
                "case_decision": {
                    "selected": None,
                    "allowed_values": [
                        "productized_page_more_educational",
                        "raw_teacher_card_or_note_more_educational",
                        "no_clear_difference",
                        "cannot_judge",
                    ],
                    "notes": "",
                },
            }
            for case in cases
        ],
        "boundary_acknowledgement": {
            "not_product_proof": False,
            "not_answer_correctness": False,
            "graph_edges_not_proof": False,
            "runtime_not_authorized": False,
        },
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "agent_or_automatic_action_authorized": False,
        },
    }


def _case_review_item(
    repo_root: Path,
    pilot_dir: Path,
    source_root: Path,
    object_item: dict[str, str],
) -> dict[str, str]:
    case_id = object_item["case_id"]
    lesson = _load_json(pilot_dir / object_item["path"])
    graph_path = _find_graph_path(pilot_dir, case_id)
    graph = _load_json(graph_path)
    relation_page = graph["edges"][0]["href"]
    return {
        "case_id": case_id,
        "product_lesson_page": _repo_rel(
            repo_root / "docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons"
            / f"{case_id}.md"
        ),
        "product_lesson_object": _repo_rel(pilot_dir / object_item["path"]),
        "teacher_card": _repo_rel(source_root / case_id / "mental_model_teacher_card.md"),
        "teacher_note": _repo_rel(source_root / case_id / "mental_model_teacher.md"),
        "relation_page": _normalize_graph_href(graph_path, relation_page),
        "graph_neighborhood": _repo_rel(graph_path),
        "decision_work_boundary_reference": REQUIRED_DECISION_WORK_BRIEFS[case_id],
        "thinking_move": lesson["thinking_move"],
    }


def _find_graph_path(pilot_dir: Path, case_id: str) -> Path:
    path = pilot_dir / "graphs" / f"{case_id}.graph.json"
    if not path.exists():
        raise MentalModelTeacherUxReviewPacketError(f"missing graph for {case_id}")
    return path


def _normalize_graph_href(graph_path: Path, href: str) -> str:
    path = (graph_path.parent / href).resolve()
    return _repo_rel(path)


def _md_link(label: str, repo_relative_path: str, from_path: Path) -> str:
    return f"[{label}]({_relative_link(from_path, repo_relative_path)})"


def _relative_link(from_path: Path, repo_relative_path: str) -> str:
    try:
        from_path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return repo_relative_path
    return os.path.relpath(REPO_ROOT / repo_relative_path, from_path.parent)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MentalModelTeacherUxReviewPacketError("JSON root must be an object")
    return payload


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finish(lines: list[str]) -> str:
    return "\n".join(str(line).rstrip() for line in lines).rstrip() + "\n"


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherUxReviewPacketError(
            "path must stay inside the repository"
        ) from exc


def _safe_display_path(path: Path) -> str:
    try:
        return _repo_rel(path)
    except MentalModelTeacherUxReviewPacketError:
        return path.name


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherUxReviewPacketError(
            "UX review packet contains a local path marker"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Mental Model Teacher UX review packet.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    manifest = build_ux_review_packet(args.root, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
