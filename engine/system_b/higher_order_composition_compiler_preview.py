from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from system_b.higher_order_composition import (
    HIGHER_ORDER_COMPOSITION_PILOT_MODEL_IDS,
    build_higher_order_composition_delta_report,
    build_higher_order_composition_preview,
    load_higher_order_composition,
)


REVIEW_FIELD_NAME = "higher_order_composition_review"
EXCEPTION_CONTRACT_ID = "risk-vs-uncertainty--compound_contract--02--decision-trees"


def write_higher_order_composition_compiler_preview_artifacts(
    root: Path,
    *,
    out_dir: Path,
) -> dict[str, Path]:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compiled_preview = build_higher_order_composition_compiled_preview(root)
    diff_report = build_higher_order_composition_compiler_diff_report(
        root,
        compiled_preview=compiled_preview,
    )
    summary = build_higher_order_composition_compiler_preview_summary(
        compiled_preview=compiled_preview,
        diff_report=diff_report,
    )

    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    preview_json_path = out_dir / "composition_compiled_preview.json"
    preview_md_path = out_dir / "composition_compiled_preview.md"
    diff_json_path = out_dir / "diff_report.json"
    diff_md_path = out_dir / "diff_report.md"

    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(
        render_higher_order_composition_compiler_preview_summary_markdown(summary),
        encoding="utf-8",
    )
    preview_json_path.write_text(json.dumps(compiled_preview, indent=2), encoding="utf-8")
    preview_md_path.write_text(
        render_higher_order_composition_compiled_preview_markdown(compiled_preview),
        encoding="utf-8",
    )
    diff_json_path.write_text(json.dumps(diff_report, indent=2), encoding="utf-8")
    diff_md_path.write_text(
        render_higher_order_composition_compiler_diff_markdown(diff_report),
        encoding="utf-8",
    )

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "composition_compiled_preview_json": preview_json_path,
        "composition_compiled_preview_md": preview_md_path,
        "diff_report_json": diff_json_path,
        "diff_report_md": diff_md_path,
    }


def build_higher_order_composition_compiled_preview(root: Path) -> dict[str, object]:
    root = Path(root)
    model_ids = tuple(HIGHER_ORDER_COMPOSITION_PILOT_MODEL_IDS)
    records = load_higher_order_composition(root, model_ids=model_ids)
    preview = build_higher_order_composition_preview(root, model_ids=model_ids)
    review_items = preview["higher_order_review"]["items"]

    contract_review_metadata: dict[str, object] = {}
    topology_review_metadata: dict[str, object] = {}
    models_review_metadata: dict[str, object] = {}

    contested_contract_count = 0
    explanatory_topology_count = 0

    for model_id in model_ids:
        record = records[model_id]
        topology_id = f"{model_id}--topology_semantics"
        topology_review = review_items[topology_id]
        topology_review_metadata[topology_id] = {
            "model_id": model_id,
            "contested": bool(topology_review["contested"]),
            "reasons": list(topology_review["reasons"]),
            "review_status": "guardrail-only",
            "policy_risk": True,
            "must_not_imply": [
                "ranking",
                "readiness",
                "bundle selection policy",
                "runtime defaulting",
            ],
            "note": (
                "Topology semantics are explanatory-only guardrails in preview artifacts and "
                "must not be treated as compiler or runtime policy."
            ),
        }
        explanatory_topology_count += 1
        models_review_metadata[model_id] = {
            "source_file": record.source_file,
            "compound_contract_count": len(record.compound_contracts),
            "multihop_motif_count": len(record.multihop_motifs),
            "topology_semantics_count": 1,
            "open_questions": list(record.curation_notes.get("open_questions", []) or []),
            "donor_drops": list(record.curation_notes.get("donor_drops", []) or []),
        }

    for contract in preview["compound_contracts"]:
        contract_id = str(contract["contract_id"])
        review = review_items[contract_id]
        reasons = list(review["reasons"])
        contested = bool(review["contested"])
        if contested:
            contested_contract_count += 1
        contract_review_metadata[contract_id] = {
            "model_id": contract["model_id"],
            "target_model_id": contract["target_model_id"],
            "contested": contested,
            "reasons": reasons,
            "review_status": "review-visible" if contested else "stable-preview",
            "exception_contract": contract_id == EXCEPTION_CONTRACT_ID,
            "direct_wave3_grounded": bool(contract["source_basis"]["wave3_relation_ids"]),
            "requires_manual_review": contested,
        }

    preview_only_scope = [
        "all reviewed_higher_order compound contracts",
        "the remaining medium-confidence exception contract",
        "all topology semantics as explanatory-only guardrails",
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": (
            "Wave 4 bounded higher-order composition compiled into alternate preview artifacts; "
            "compound contracts lead, multihop remains absent, and topology stays guardrail-only."
        ),
        "pilot_model_ids": list(model_ids),
        "model_count": len(model_ids),
        "contract_family_contract": ["compound_contracts", "multihop_motifs", "topology_semantics"],
        "total_compound_contract_count": preview["total_compound_contract_count"],
        "total_multihop_motif_count": preview["total_multihop_motif_count"],
        "total_topology_semantics_count": preview["total_topology_semantics_count"],
        "extraction_type_counts": preview["extraction_type_counts"],
        "confidence_counts": preview["confidence_counts"],
        "compound_contract_records": preview["compound_contracts"],
        "multihop_motif_records": preview["multihop_motifs"],
        "topology_semantics_records": preview["topology_semantics"],
        REVIEW_FIELD_NAME: {
            "status": "preview_only",
            "reason": (
                "All Wave 4 higher-order items are reviewed composition judgments rather than "
                "canonical compiler truth. The surviving exception contract and the explanatory-only "
                "topology layer should remain visibly reviewable."
            ),
            "preview_only_scope": preview_only_scope,
            "reviewed_higher_order_items_require_review_metadata": True,
            "topology_guardrail_review_required": True,
            "contested_contract_count": contested_contract_count,
            "contested_motif_count": int(preview["higher_order_review"]["contested_motif_count"]),
            "contested_topology_count": int(preview["higher_order_review"]["contested_topology_count"]),
            "exception_contract_ids": [EXCEPTION_CONTRACT_ID],
            "explanatory_topology_ids": sorted(topology_review_metadata),
            "models": models_review_metadata,
            "compound_contracts": contract_review_metadata,
            "topology_semantics": topology_review_metadata,
        },
    }


def build_higher_order_composition_compiler_diff_report(
    root: Path,
    *,
    compiled_preview: dict[str, object] | None = None,
) -> dict[str, object]:
    root = Path(root)
    compiled_preview = compiled_preview or build_higher_order_composition_compiled_preview(root)
    model_ids = tuple(str(model_id) for model_id in compiled_preview["pilot_model_ids"])
    delta_report = build_higher_order_composition_delta_report(
        root,
        model_ids=model_ids,
    )
    review_payload = compiled_preview[REVIEW_FIELD_NAME]

    per_model: dict[str, object] = {}
    for model_id, payload in (delta_report.get("models", {}) or {}).items():
        topology_id = f"{model_id}--topology_semantics"
        per_model[model_id] = {
            "source_file": payload["source_file"],
            "compound_contract_count": payload["compound_contract_count"],
            "multihop_motif_count": payload["multihop_motif_count"],
            "contested_contract_count": payload["contested_contract_count"],
            "topology_review_status": review_payload["topology_semantics"][topology_id]["review_status"],
            "open_questions": payload["open_questions"],
        }

    contested_contract_count = int(review_payload["contested_contract_count"])
    low_confidence_contract_count = len(
        [
            item
            for item in compiled_preview["compound_contract_records"]
            if item["confidence"] != "high"
        ]
    )
    safe = (
        compiled_preview["total_multihop_motif_count"] == 0
        and low_confidence_contract_count <= 1
        and delta_report["did_higher_order_layer_preserve_real_source_backed_or_lower_layer_grounded_composition"]
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "model_count": compiled_preview["model_count"],
        "total_compound_contract_count": compiled_preview["total_compound_contract_count"],
        "total_multihop_motif_count": compiled_preview["total_multihop_motif_count"],
        "total_topology_semantics_count": compiled_preview["total_topology_semantics_count"],
        "contested_contract_count": contested_contract_count,
        "contested_motif_count": int(review_payload["contested_motif_count"]),
        "contested_topology_count": int(review_payload["contested_topology_count"]),
        "low_confidence_contract_count": low_confidence_contract_count,
        "exception_contract_ids": review_payload["exception_contract_ids"],
        "source_first_doctrine_respected": delta_report[
            "did_higher_order_layer_preserve_real_source_backed_or_lower_layer_grounded_composition"
        ],
        "safety_assessment": (
            "safe_for_optional_wave4_compiler_preview"
            if safe
            else "useful_but_hold_until_higher_order_review_issues_are_repaired"
        ),
        "recommendation": (
            "Wave 4 is disciplined enough to become an optional compiler-side preview artifact because the surface is bounded, multihop remains absent, topology stays explanatory-only, and the lone exception contract stays explicitly review-visible."
            if safe
            else "Wave 4 should remain external to compiler outputs until the remaining higher-order review issues are repaired."
        ),
        "models": per_model,
    }


def build_higher_order_composition_compiler_preview_summary(
    *,
    compiled_preview: dict[str, object],
    diff_report: dict[str, object],
) -> dict[str, object]:
    review_payload = compiled_preview[REVIEW_FIELD_NAME]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "pilot_model_count": compiled_preview["model_count"],
        "pilot_anchor_count_is_bounded": compiled_preview["model_count"] == 6,
        "wave4_bounded_pilot_only": True,
        "total_compound_contract_count": compiled_preview["total_compound_contract_count"],
        "total_multihop_motif_count": compiled_preview["total_multihop_motif_count"],
        "total_topology_semantics_count": compiled_preview["total_topology_semantics_count"],
        "extraction_type_counts": compiled_preview["extraction_type_counts"],
        "confidence_counts": compiled_preview["confidence_counts"],
        "preview_artifact_field": REVIEW_FIELD_NAME,
        "reviewed_higher_order_items_require_review_metadata": review_payload[
            "reviewed_higher_order_items_require_review_metadata"
        ],
        "topology_guardrail_review_required": review_payload["topology_guardrail_review_required"],
        "contested_contract_count": diff_report["contested_contract_count"],
        "contested_motif_count": diff_report["contested_motif_count"],
        "contested_topology_count": diff_report["contested_topology_count"],
        "low_confidence_contract_count": diff_report["low_confidence_contract_count"],
        "exception_contract_ids": review_payload["exception_contract_ids"],
        "source_first_doctrine_respected": diff_report["source_first_doctrine_respected"],
        "safe_for_optional_wave4_compiler_preview": diff_report["safety_assessment"]
        == "safe_for_optional_wave4_compiler_preview",
        "preview_only_boundary": True,
    }


def render_higher_order_composition_compiled_preview_markdown(
    preview: dict[str, object],
) -> str:
    review = preview[REVIEW_FIELD_NAME]
    lines = [
        "# Wave 4 Higher-Order Composition Compiled Preview",
        "",
        f"- Generated at: {preview['generated_at']}",
        f"- Pilot models: {', '.join(preview['pilot_model_ids'])}",
        f"- Compound contracts: {preview['total_compound_contract_count']}",
        f"- Multihop motifs: {preview['total_multihop_motif_count']}",
        f"- Topology semantics records: {preview['total_topology_semantics_count']}",
        f"- Preview-only review field: `{REVIEW_FIELD_NAME}`",
        "",
        "## Compound Contracts",
        "",
    ]
    for contract in preview["compound_contract_records"]:
        lines.append(
            f"- `{contract['contract_id']}` | `{contract['model_id']}` -> `{contract['target_model_id']}` | confidence=`{contract['confidence']}`"
        )

    lines.extend(["", "## Topology Semantics", ""])
    for topology in preview["topology_semantics_records"]:
        lines.append(
            f"- `{topology['topology_id']}` | explanatory_only | needs_partner=`{topology['usually_needs_partner_role']}`"
        )

    lines.extend(["", "## Review Metadata", ""])
    lines.append(
        f"- Contested contracts: {review['contested_contract_count']} | exception contracts: {', '.join(review['exception_contract_ids'])}"
    )
    lines.append(
        f"- Explanatory topology records: {len(review['explanatory_topology_ids'])}"
    )
    return "\n".join(lines) + "\n"


def render_higher_order_composition_compiler_diff_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Wave 4 Compiler Preview Diff Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Contested contracts: {report['contested_contract_count']}",
        f"- Contested motifs: {report['contested_motif_count']}",
        f"- Contested topology records: {report['contested_topology_count']}",
        f"- Low-confidence contracts: {report['low_confidence_contract_count']}",
        f"- Safety assessment: `{report['safety_assessment']}`",
        f"- Recommendation: {report['recommendation']}",
        "",
    ]
    return "\n".join(lines)


def render_higher_order_composition_compiler_preview_summary_markdown(
    summary: dict[str, object],
) -> str:
    lines = [
        "# Wave 4 Compiler Preview Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Preview artifact field: `{summary['preview_artifact_field']}`",
        f"- Bounded pilot only: `{summary['wave4_bounded_pilot_only']}`",
        f"- Safe for optional compiler-side preview: `{summary['safe_for_optional_wave4_compiler_preview']}`",
        "- Reviewed higher-order items require preview metadata: "
        f"`{summary['reviewed_higher_order_items_require_review_metadata']}`",
        f"- Topology guardrail review required: `{summary['topology_guardrail_review_required']}`",
        f"- Exception contracts: {', '.join(summary['exception_contract_ids'])}",
        "",
    ]
    return "\n".join(lines)
