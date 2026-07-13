#!/usr/bin/env python3
"""Build role-specific carry-forward exploration-local v2 artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_local_packets,
    compile_local_response,
    validate_local_response,
)
from engine.system_b.reasoning_process_view_specific import (  # noqa: E402
    VIEW_QUESTIONS,
    build_annotated_reader_packet,
)
from scripts.evals.build_reasoning_process_exploration_local import (  # noqa: E402
    _display,
    _write,
    build,
)


def _alias_with_text(annotated: str, phrase: str) -> str:
    matches = [
        line.split("\t", 1)[0]
        for line in annotated.splitlines()
        if "\t" in line and phrase in line
    ]
    if len(matches) != 1:
        raise RuntimeError(f"adversarial phrase did not resolve once: {phrase}")
    return matches[0]


def build_v2(*, root: Path, output: Path) -> dict:
    contract_path = (
        root / "docs/evals/reasoning-process-exploration-local-harvester-contract-v2.json"
    )
    report = build(
        root=root,
        output=output,
        allow_prior_alternative_citation=True,
        contract_path=contract_path,
    )
    source_path = (
        "tests/fixtures/reasoning_process_exploration_local/cross_turn_relationship.txt"
    )
    source_text = (root / source_path).read_text(encoding="utf-8")
    full = build_annotated_reader_packet(
        case_id="exploration-local-cross-turn",
        view_kind="exploration_and_alternatives",
        question=VIEW_QUESTIONS["exploration_and_alternatives"],
        source_path=source_path,
        source_text=source_text,
        base_observations=[],
    )
    packets = build_local_packets(
        case_id="exploration-local-cross-turn",
        source_path=source_path,
        source_text=source_text,
        global_alias_map=full["evidence_alias_map"],
        allow_prior_alternative_citation=True,
    )
    wrapper = packets[1]
    alternative_alias = _alias_with_text(
        wrapper["packet"]["prior_context"]["annotated_sentence_text"],
        "small pilot next month",
    )
    limit_alias = _alias_with_text(
        wrapper["packet"]["focal_pair"]["annotated_sentence_text"],
        "only works if a named operator commits",
    )
    response = {
        "status": "supported",
        "records": [
            {
                "alternative_interpretation": "Launch a small pilot next month.",
                "alternative_evidence_ids": [alternative_alias],
                "attached_condition_or_limit_interpretation": "A named operator must commit before announcement.",
                "attached_condition_or_limit_evidence_ids": [limit_alias],
                "relationship_type": "condition",
                "status": "supported",
                "limitations": "Provider-free cross-turn relationship fixture.",
            }
        ],
        "global_limitations": "Synthetic boundary fixture; not product evidence.",
    }
    validated = validate_local_response(response, wrapper=wrapper)
    compiled = compile_local_response(
        response=response,
        wrapper=wrapper,
        producer_kind="source_reviewer",
        producer_id="exploration-local-v2-adversarial-review",
        record_identity="cross-turn-alternative-limit",
    )
    adversarial_dir = output / "adversarial-cross-turn"
    _write(adversarial_dir / "turn-002-packet.json", wrapper)
    _write(
        adversarial_dir / "fixture.json",
        {
            "status": "cross_turn_relationship_pass",
            "response": response,
            "validation": validated,
            "compiled": compiled,
            "boundary": {
                "prior_context_used_only_for_alternative": True,
                "attached_limit_is_focal": True,
                "semantic_inference_performed_by_code": False,
                "provider_calls": 0,
            },
        },
    )
    report["summary"]["cross_turn_adversarial_fixture_count"] = 1
    report["summary"]["cross_turn_adversarial_fixture_pass_count"] = 1
    report["adversarial_cross_turn"] = {
        "source_path": source_path,
        "focal_turn_index": 2,
        "alternative_alias_region": "prior_context",
        "attached_limit_alias_region": "focal_pair",
        "packet_path": _display(adversarial_dir / "turn-002-packet.json", root),
        "fixture_path": _display(adversarial_dir / "fixture.json", root),
        "status": "pass",
    }
    report["decision"] = {
        "provider_free_representation_gate": "pass",
        "same_pair_and_one_pair_later_relationships_representable": True,
        "semantic_model_behavior_validated": False,
        "next_required_gate": "final cold-reader review and full adversarial suite",
        "provider_call_authorized": False,
        "phase4_transfer_authorized": False,
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-exploration-local-v2-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = build_v2(root=root, output=root / args.output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
