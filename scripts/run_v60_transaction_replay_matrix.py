#!/usr/bin/env python3
"""Run expanded dry-run configurations for the v60 transaction replay lab.

This matrix runner does not call models. It varies card caps, packet snippet
caps, decoder snippet caps, and decoder solution modes so we can see where the
transaction packet becomes too thin, too wide, or too arbitrary before paid
OpenRouter replay.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.card_transaction_ledger import (  # noqa: E402
    RUNTIME_POLICY,
    STATUS,
    validate_card_transaction_ledger_payload,
)
from system_b.reasoning_substrate_packet import (  # noqa: E402
    build_reasoning_substrate_packet_from_files,
)

from scripts.run_v60_transaction_replay_lab import (  # noqa: E402
    DEFAULT_AFFORDANCES_PATH,
    LAB_VERSION,
    ReplayLabError,
    build_arm_b,
    build_arm_c,
    build_case_artifact,
    build_dry_run_ledger_template,
    estimate_tokens,
    extract_nominations_from_result,
    load_case_specs,
    merge_nominations,
    packet_quality_counts,
)


MATRIX_VERSION = "v60_transaction_replay_matrix.v1"
DEFAULT_OUTPUT_DIR = Path("data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix")


@dataclass(frozen=True)
class MatrixConfig:
    config_id: str
    card_cap: int
    snippet_cap: int
    decoder_snippet_cap: int
    max_nominations: int
    intent: str


@dataclass(frozen=True)
class SolutionMode:
    mode_id: str
    role: str
    system_suffix: str
    output_contract: Mapping[str, Any]


MATRIX_CONFIGS = (
    MatrixConfig(
        config_id="cap4_tiny",
        card_cap=4,
        snippet_cap=1,
        decoder_snippet_cap=1,
        max_nominations=18,
        intent="Minimum viable packet: tests whether high-selectivity loses too many useful lanes.",
    ),
    MatrixConfig(
        config_id="cap8_focused",
        card_cap=8,
        snippet_cap=2,
        decoder_snippet_cap=1,
        max_nominations=18,
        intent="Focused packet: tests a likely product default for cost and attention.",
    ),
    MatrixConfig(
        config_id="cap12_default_compact",
        card_cap=12,
        snippet_cap=2,
        decoder_snippet_cap=1,
        max_nominations=18,
        intent="Current local preflight default with compact decoder projection.",
    ),
    MatrixConfig(
        config_id="cap16_wide_compact",
        card_cap=16,
        snippet_cap=2,
        decoder_snippet_cap=1,
        max_nominations=24,
        intent="Wide packet: tests whether the previous 12-card cap hides important nominations.",
    ),
    MatrixConfig(
        config_id="cap16_wide_rich",
        card_cap=16,
        snippet_cap=3,
        decoder_snippet_cap=2,
        max_nominations=24,
        intent="Upper-burden packet: tests cost and attention risk when preserving more source texture.",
    ),
)


SOLUTION_MODES = (
    SolutionMode(
        mode_id="answer_revision",
        role="revise_final_answer",
        system_suffix=(
            "Mode: revise the final answer. Keep it user-useful and concise. "
            "The ledger is audit material, not user copy."
        ),
        output_contract={
            "mode_output": "revised final answer plus transaction ledger",
        },
    ),
    SolutionMode(
        mode_id="edge_audit",
        role="surface_non_obvious_edges",
        system_suffix=(
            "Mode: do not rewrite the whole answer. Identify the non-obvious "
            "edges, missed risks, and unsupported assumptions that should change the answer."
        ),
        output_contract={
            "edge_findings": [
                "non-obvious edge",
                "why it matters",
                "whether the original answer should change",
            ],
            "rewrite_required": "yes / no / only small caveat",
        },
    ),
    SolutionMode(
        mode_id="question_gate",
        role="gate_on_missing_evidence",
        system_suffix=(
            "Mode: separate what can be answered now from what should be gated "
            "behind missing evidence. Prefer useful questions over forced certainty."
        ),
        output_contract={
            "answerable_now": ["claims or recommendations that can be made now"],
            "gated_questions": ["missing evidence that should block stronger claims"],
            "confidence_shift": "how the substrate changes confidence",
        },
    ),
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = REPO_ROOT
    manifest_path = _resolve(root, args.case_manifest)
    affordances_path = _resolve(root, args.affordances_path)
    output_dir = _resolve(root, args.output_dir)
    if not args.dry_run:
        raise ReplayLabError("Matrix testing is dry-run only")
    if affordances_path.name != "affordances_v60.json":
        raise ReplayLabError("The v60 replay matrix requires explicit affordances_v60.json")

    configs = _selected_configs(args.config_id)
    manifest = _load_json(manifest_path)
    cases = load_case_specs(manifest, root=root)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_results = []
    for config in configs:
        rows = [
            _run_case_config(
                case=case,
                config=config,
                root=root,
                affordances_path=affordances_path,
            )
            for case in cases
        ]
        config_results.append(
            {
                "config_id": config.config_id,
                "intent": config.intent,
                "card_cap": config.card_cap,
                "snippet_cap": config.snippet_cap,
                "decoder_snippet_cap": config.decoder_snippet_cap,
                "max_nominations": config.max_nominations,
                "aggregate": _aggregate_config(rows),
                "cases": rows,
            }
        )

    summary = {
        "matrix_version": MATRIX_VERSION,
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "case_count": len(cases),
        "config_count": len(config_results),
        "solution_modes": [
            {"mode_id": mode.mode_id, "role": mode.role}
            for mode in SOLUTION_MODES
        ],
        "configs": config_results,
    }
    _write_json(output_dir / "summary.json", summary)
    (output_dir / "matrix_report.md").write_text(render_matrix_report(summary), encoding="utf-8")
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'matrix_report.md'}")
    return 0


def _run_case_config(
    *,
    case: Any,
    config: MatrixConfig,
    root: Path,
    affordances_path: Path,
) -> dict[str, Any]:
    case_artifact = build_case_artifact(case, root=root)
    nominations = (
        *case.explicit_nominations,
        *extract_nominations_from_result(
            case_artifact.get("result", {}),
            max_nominations=config.max_nominations,
        ),
    )
    nominations = merge_nominations(nominations)[: config.max_nominations]
    packet = build_reasoning_substrate_packet_from_files(
        root=root,
        packet_id=f"matrix-{config.config_id}-{case.file_stem}",
        transaction_context={
            "case_id": case.case_id,
            "lab_version": LAB_VERSION,
            "matrix_version": MATRIX_VERSION,
            "config_id": config.config_id,
            "include_reason": case.include_reason,
            "risk_notes": list(case.risk_notes),
            "tags": list(case.tags),
            "dry_run": True,
        },
        nominations=list(nominations),
        affordances_path=affordances_path,
        candidate_card_target_max=config.card_cap,
        snippet_target_max_per_card=config.snippet_cap,
    )
    ledger = build_dry_run_ledger_template(packet)
    validate_card_transaction_ledger_payload(ledger, packet=packet)
    arm_b = build_arm_b(case_artifact)
    mode_estimates = {
        mode.mode_id: estimate_tokens(
            _arm_c_for_mode(
                case_artifact,
                packet,
                config=config,
                mode=mode,
            )
        )
        for mode in SOLUTION_MODES
    }
    packet_view_estimate = estimate_tokens(
        build_arm_c(
            case_artifact,
            packet,
            decoder_snippet_cap=config.decoder_snippet_cap,
        )["user_packet"]["reasoning_substrate_packet"]
    )
    candidate_model_ids = [
        _text(card.get("model_id"))
        for card in (_mapping(item) for item in _list(packet.get("candidate_cards")))
    ]
    suppressed = [_mapping(item) for item in _list(packet.get("suppressed_candidates"))]
    suppressed_model_ids = [_text(item.get("model_id")) for item in suppressed]
    explicit_probe_ids = [_text(nomination.model_id) for nomination in case.explicit_nominations]
    quality = packet_quality_counts(packet)
    coverage = _mapping(packet.get("coverage_summary"))
    return {
        "case_id": case.case_id,
        "tags": list(case.tags),
        "nomination_count": len(nominations),
        "candidate_card_count": len(candidate_model_ids),
        "candidate_model_ids": candidate_model_ids,
        "suppressed_candidate_count": len(suppressed),
        "suppressed_model_ids": suppressed_model_ids,
        "suppressed_by_reason": dict(Counter(_text(item.get("suppression_reason")) for item in suppressed)),
        "suppressed_by_coverage": dict(Counter(_text(item.get("coverage_status")) for item in suppressed)),
        "explicit_probe_ids": explicit_probe_ids,
        "missing_explicit_probe_ids": [
            model_id for model_id in explicit_probe_ids if model_id not in candidate_model_ids
        ],
        "coverage_summary": coverage,
        "packet_quality_counts": quality,
        "token_estimates": {
            "stored_packet": estimate_tokens(packet),
            "arm_b_prompt_packet": estimate_tokens(arm_b),
            "arm_c_packet_view": packet_view_estimate,
            "arm_c_modes": mode_estimates,
        },
        "requirements_flags": _requirements_flags(
            case_id=case.case_id,
            candidate_model_ids=candidate_model_ids,
            suppressed=suppressed,
            quality=quality,
            coverage=coverage,
            mode_estimates=mode_estimates,
            arm_b_tokens=estimate_tokens(arm_b),
        ),
    }


def _arm_c_for_mode(
    case_artifact: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    config: MatrixConfig,
    mode: SolutionMode,
) -> dict[str, Any]:
    arm = build_arm_c(
        case_artifact,
        packet,
        decoder_snippet_cap=config.decoder_snippet_cap,
    )
    arm["solution_mode"] = mode.mode_id
    arm["role"] = mode.role
    arm["system_prompt"] = f"{arm['system_prompt'].rstrip()}\n\n{mode.system_suffix}\n"
    arm["user_packet"]["output_contract"] = {
        **_mapping(arm["user_packet"].get("output_contract")),
        **mode.output_contract,
    }
    return arm


def _requirements_flags(
    *,
    case_id: str,
    candidate_model_ids: list[str],
    suppressed: list[Mapping[str, Any]],
    quality: Mapping[str, int],
    coverage: Mapping[str, Any],
    mode_estimates: Mapping[str, int],
    arm_b_tokens: int,
) -> list[str]:
    flags: list[str] = []
    if suppressed:
        flags.append("cap_selects_not_all_nominations")
    if any(int(value) > 20000 for value in mode_estimates.values()):
        flags.append("prompt_payload_above_20k_estimate")
    if any(int(value) > max(arm_b_tokens * 3, 1) for value in mode_estimates.values()):
        flags.append("arm_c_more_than_3x_arm_b")
    if case_id == "user_has_plan" and len(candidate_model_ids) > 8:
        flags.append("narrow_control_overburdened")
    if int(quality.get("weak_support_affordance_count") or 0) > 0:
        flags.append("weak_support_visible")
    if int(coverage.get("conflicting_or_weak_support_count") or 0) > 0:
        flags.append("weak_or_conflicting_card_visible")
    if int(quality.get("absence_record_count") or 0) < len(candidate_model_ids):
        flags.append("absence_visibility_thin")
    return flags


def _aggregate_config(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    mode_ids = [mode.mode_id for mode in SOLUTION_MODES]
    all_flags = Counter(
        flag
        for row in rows
        for flag in _strings(row.get("requirements_flags"))
    )
    mode_tokens = {
        mode_id: [
            int(_mapping(_mapping(row.get("token_estimates")).get("arm_c_modes")).get(mode_id) or 0)
            for row in rows
        ]
        for mode_id in mode_ids
    }
    return {
        "total_nominations": sum(int(row.get("nomination_count") or 0) for row in rows),
        "total_cards": sum(int(row.get("candidate_card_count") or 0) for row in rows),
        "total_suppressed": sum(int(row.get("suppressed_candidate_count") or 0) for row in rows),
        "cases_with_suppression": sum(
            1 for row in rows if int(row.get("suppressed_candidate_count") or 0) > 0
        ),
        "cases_with_missing_explicit_probe": sum(
            1 for row in rows if _list(row.get("missing_explicit_probe_ids"))
        ),
        "weak_support_affordance_count": sum(
            int(_mapping(row.get("packet_quality_counts")).get("weak_support_affordance_count") or 0)
            for row in rows
        ),
        "medium_confidence_affordance_count": sum(
            int(_mapping(row.get("packet_quality_counts")).get("medium_confidence_affordance_count") or 0)
            for row in rows
        ),
        "absence_record_count": sum(
            int(_mapping(row.get("packet_quality_counts")).get("absence_record_count") or 0)
            for row in rows
        ),
        "arm_c_mode_token_ranges": {
            mode_id: {
                "min": min(tokens) if tokens else 0,
                "max": max(tokens) if tokens else 0,
                "avg": round(sum(tokens) / len(tokens), 1) if tokens else 0,
            }
            for mode_id, tokens in mode_tokens.items()
        },
        "requirements_flags": dict(all_flags),
    }


def render_matrix_report(summary: Mapping[str, Any]) -> str:
    lines = [
        "# V60 Transaction Replay Matrix",
        "",
        "## Boundary",
        "",
        "- Dry run only; no model calls were made.",
        f"- Runtime policy: `{_text(summary.get('runtime_policy'))}`.",
        f"- Affordance artifact: `{_text(summary.get('affordances_path'))}`.",
        "- This compares packet and prompt configurations, not answer quality.",
        "",
        "## Configuration Summary",
        "",
        "| Config | Cap | Max Noms | Snippet | Decoder Snippet | Noms | Cards | Suppressed | Cases Suppressed | Weak Aff. | Medium Aff. | Absences | Answer Mode Tokens | Edge Mode Tokens | Gate Mode Tokens |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for raw_config in _list(summary.get("configs")):
        config = _mapping(raw_config)
        aggregate = _mapping(config.get("aggregate"))
        ranges = _mapping(aggregate.get("arm_c_mode_token_ranges"))
        lines.append(
            "| "
            f"`{_text(config.get('config_id'))}` | "
            f"{int(config.get('card_cap') or 0)} | "
            f"{int(config.get('max_nominations') or 0)} | "
            f"{int(config.get('snippet_cap') or 0)} | "
            f"{int(config.get('decoder_snippet_cap') or 0)} | "
            f"{int(aggregate.get('total_nominations') or 0)} | "
            f"{int(aggregate.get('total_cards') or 0)} | "
            f"{int(aggregate.get('total_suppressed') or 0)} | "
            f"{int(aggregate.get('cases_with_suppression') or 0)} | "
            f"{int(aggregate.get('weak_support_affordance_count') or 0)} | "
            f"{int(aggregate.get('medium_confidence_affordance_count') or 0)} | "
            f"{int(aggregate.get('absence_record_count') or 0)} | "
            f"{_range_text(_mapping(ranges.get('answer_revision')))} | "
            f"{_range_text(_mapping(ranges.get('edge_audit')))} | "
            f"{_range_text(_mapping(ranges.get('question_gate')))} |"
        )

    lines.extend(
        [
            "",
            "## Requirement Signals",
            "",
            "| Config | Signals |",
            "| --- | --- |",
        ]
    )
    for raw_config in _list(summary.get("configs")):
        config = _mapping(raw_config)
        aggregate = _mapping(config.get("aggregate"))
        flags = _mapping(aggregate.get("requirements_flags"))
        signal_text = ", ".join(
            f"`{key}` x{value}" for key, value in sorted(flags.items())
        )
        lines.append(f"| `{_text(config.get('config_id'))}` | {signal_text or 'none'} |")

    lines.extend(
        [
            "",
            "## Case Pressure",
            "",
            "| Config | Case | Cards | Suppressed | Missing Probe | Flags |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for raw_config in _list(summary.get("configs")):
        config = _mapping(raw_config)
        for raw_case in _list(config.get("cases")):
            case = _mapping(raw_case)
            lines.append(
                "| "
                f"`{_text(config.get('config_id'))}` | "
                f"`{_text(case.get('case_id'))}` | "
                f"{int(case.get('candidate_card_count') or 0)} | "
                f"{int(case.get('suppressed_candidate_count') or 0)} | "
                f"{', '.join(f'`{item}`' for item in _strings(case.get('missing_explicit_probe_ids'))) or 'none'} | "
                f"{', '.join(f'`{item}`' for item in _strings(case.get('requirements_flags'))) or 'none'} |"
            )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- `cap4_tiny` is useful as a stress lower bound, but it suppresses too much lane evidence for broad replay.",
            "- `cap8_focused` is the first plausible product-shaped candidate if narrow-control burden matters.",
            "- `cap12_default_compact` preserves more reasoning surface, but keeps overburden risk on narrow cases.",
            "- `cap16_*` configurations test hidden nomination loss, not product readiness; they are pressure diagnostics.",
            "- Solution modes should be evaluated separately: answer revision, edge audit, and question gate can all be useful products.",
            "",
            "## Next Test",
            "",
            "Before paid replay, choose whether the pilot should test a focused product packet (`cap8_focused`) or a broader research packet (`cap12_default_compact`). Do not mix that decision with model-quality evaluation.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", required=True, type=Path)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--config-id", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _selected_configs(config_ids: list[str]) -> tuple[MatrixConfig, ...]:
    if not config_ids:
        return MATRIX_CONFIGS
    by_id = {config.config_id: config for config in MATRIX_CONFIGS}
    missing = sorted(set(config_ids) - set(by_id))
    if missing:
        raise ReplayLabError(f"unknown matrix config_id: {missing}")
    return tuple(by_id[config_id] for config_id in config_ids)


def _resolve(root: Path, path: Path) -> Path:
    path = Path(path).expanduser()
    return path if path.is_absolute() else root / path


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayLabError(f"{path}: expected JSON object")
    return payload


def _range_text(row: Mapping[str, Any]) -> str:
    if not row:
        return "0-0"
    return f"{int(row.get('min') or 0)}-{int(row.get('max') or 0)}"


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
