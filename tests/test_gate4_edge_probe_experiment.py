from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.judge_gate4_edge_probes import (  # noqa: E402
    blind_arm_mapping,
    normalize_judge_payload,
    summarize_judge_outputs,
    validate_judge_output,
)
from scripts.run_gate4_edge_probe_experiment import (  # noqa: E402
    REPO_ROOT,
    RouteMaterial,
    build_arm_b_packet,
    build_arm_c_packet,
    expected_activation_affordances,
    load_affordance_index,
    main as run_gate4_main,
    validate_edge_probe_output,
    validate_trace_ids,
)


AFFORDANCES_V3 = REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v3.json"


def _route(*, candidate_model_ids: tuple[str, ...] = ("base-rates",)) -> RouteMaterial:
    return RouteMaterial(
        case_id="case-one",
        run_id="20260505T000000Z",
        result_path=Path("/tmp/result.json"),
        route_id="resource-allocation",
        route_name="Resource Allocation",
        candidate_model_ids=candidate_model_ids,
        covered_candidate_count=1,
        total_candidate_count=len(candidate_model_ids),
        baseline_questions=("What tradeoff is being hidden?",),
        case_context={
            "query": "Should the founder grant equity now?",
            "vanilla_answer": "Grant equity only after a clear reference class is named.",
        },
    )


def _fake_compiled_artifact(path: Path) -> None:
    payload = {
        "artifact": "test_affordances",
        "model_records": [
            {
                "model_id": "base-rates",
                "status": "supported",
                "source_file": "base-rates.md",
                "affordances": [
                    {
                        "affordance_id": "base-rates.reference-class-anchor",
                        "mechanism": "Anchor the decision in a reference class.",
                        "activation_shape": {
                            "use_when": ["A decision needs an outside view."],
                            "do_not_use_when": ["No historical comparison is relevant."],
                            "case_evidence_needed": ["A candidate reference class."],
                        },
                        "misuse_guards": ["Do not use a fake denominator."],
                        "diagnostic_questions": ["What is the reference class?"],
                        "treatment_requirements": [
                            {
                                "requirement_id": "define-reference-class",
                                "description": "Name the reference class.",
                            }
                        ],
                    }
                ],
                "absence_records": [],
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fake_archive(root: Path) -> None:
    run_dir = root / "case-one" / "20260505T000000Z"
    run_dir.mkdir(parents=True)
    result = {
        "query": "Should the founder grant equity now?",
        "vanilla_answer": "Grant equity only after a clear reference class is named.",
        "structural_coverage_card": {
            "gap_routes": [
                {
                    "dimension_id": "resource-allocation",
                    "dimension_name": "Resource Allocation",
                    "candidate_model_ids": ["base-rates", "missing-model"],
                }
            ],
            "gap_questions": [
                {
                    "dimension_id": "resource-allocation",
                    "dimension_name": "Resource Allocation",
                    "questions": [
                        "What tradeoff is being hidden?",
                        "What tradeoff is being hidden?",
                    ],
                }
            ],
        },
    }
    (run_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_packet_assembly_keeps_python_as_lookup_layer() -> None:
    affordance_index = load_affordance_index(AFFORDANCES_V3)
    route = _route(candidate_model_ids=("base-rates", "missing-model", "comparative-advantage"))

    arm_b = build_arm_b_packet(route, affordance_index)
    assert "affordance_records" not in arm_b.packet
    assert arm_b.packet["available_model_records"] == [
        {"model_id": "base-rates", "has_v3_record": True},
        {"model_id": "missing-model", "has_v3_record": False},
        {"model_id": "comparative-advantage", "has_v3_record": True},
    ]

    arm_c = build_arm_c_packet(route, affordance_index, token_budget=100_000)
    included_ids = [record["model_id"] for record in arm_c.packet["affordance_records"]]
    assert included_ids == ["base-rates", "comparative-advantage"]
    assert arm_c.omitted_model_ids == ("missing-model",)


def test_trace_validation_accepts_real_v3_requirement_id() -> None:
    affordance_index = load_affordance_index(AFFORDANCES_V3)
    record = affordance_index["base-rates"]
    affordance = record["affordances"][0]
    requirement = affordance["treatment_requirements"][0]
    trace = {
        "model_id": "base-rates",
        "affordance_id": affordance["affordance_id"],
        "field_source": "treatment_requirement",
        "treatment_requirement_id": requirement["requirement_id"],
    }
    assert validate_trace_ids(trace, affordance_index) == []

    bad_trace = dict(trace)
    bad_trace["treatment_requirement_id"] = "not-a-real-requirement"
    assert validate_trace_ids(bad_trace, affordance_index)


def test_arm_c_output_requires_valid_traces_and_activation_calls() -> None:
    affordance_index = load_affordance_index(AFFORDANCES_V3)
    route = _route(candidate_model_ids=("base-rates",))
    packet = build_arm_c_packet(route, affordance_index, token_budget=100_000).packet
    affordance = affordance_index["base-rates"]["affordances"][0]
    requirement = affordance["treatment_requirements"][0]
    payload = {
        "case_id": route.case_id,
        "route_id": route.route_id,
        "arm": "C",
        "call_metadata": {
            "provider": "openrouter",
            "model": "test-model",
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": 0.0,
        },
        "activation_calls": [],
        "edge_probes": [
            {
                "edge_probe": "What reference class would make this equity grant ordinary?",
                "trace": {
                    "model_id": "base-rates",
                    "affordance_id": affordance["affordance_id"],
                    "field_source": "treatment_requirement",
                    "treatment_requirement_id": requirement["requirement_id"],
                },
                "why_this_is_edge": "The answer may be using inside-view urgency.",
                "if_true_changes": "Equity size and vesting should be benchmarked.",
                "dismissal_condition": "Dismiss if no comparable cases exist.",
                "clarity_cost": "low",
            }
        ],
        "set_asides": [],
    }

    errors = validate_edge_probe_output(
        payload,
        expected_arm="C",
        affordance_index=affordance_index,
        require_verified_traces=True,
        expected_activation_ids=expected_activation_affordances(packet),
        case_context=route.case_context,
    )
    assert any("missing activation_calls" in error for error in errors)

    payload["activation_calls"] = [
        {
            "model_id": "base-rates",
            "affordance_id": aff["affordance_id"],
            "activation_status": "activated",
            "case_quote": "reference class",
            "rationale": "The current answer already names this need.",
        }
        for aff in affordance_index["base-rates"]["affordances"]
    ]
    assert (
        validate_edge_probe_output(
            payload,
            expected_arm="C",
            affordance_index=affordance_index,
            require_verified_traces=True,
            expected_activation_ids=expected_activation_affordances(packet),
            case_context=route.case_context,
        )
        == []
    )


def test_dry_run_writes_packets_and_case_selection_without_llm_calls(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    affordances_path = tmp_path / "affordances.json"
    output_dir = tmp_path / "out"
    report_path = tmp_path / "selection.md"
    _fake_archive(archive_root)
    _fake_compiled_artifact(affordances_path)

    exit_code = run_gate4_main(
        [
            "--archive-root",
            str(archive_root),
            "--affordances-path",
            str(affordances_path),
            "--output-dir",
            str(output_dir),
            "--case-selection-report",
            str(report_path),
            "--cases",
            "case-one",
            "--dry-run",
        ]
    )
    assert exit_code == 0
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["route_count"] == 1
    assert summary["expected_llm_call_count"] == 2
    assert (output_dir / "arm_a" / "case-one_resource-allocation.json").exists()
    assert (output_dir / "packets" / "arm_b" / "case-one_resource-allocation.json").exists()
    assert (output_dir / "packets" / "arm_c" / "case-one_resource-allocation.json").exists()
    assert not (output_dir / "arm_b").exists()
    assert "`case-one`" in report_path.read_text(encoding="utf-8")


def test_blinded_judge_shuffle_and_schema_validation_are_deterministic() -> None:
    first = blind_arm_mapping("case-one", "resource-allocation", 42)
    second = blind_arm_mapping("case-one", "resource-allocation", 42)
    assert first == second
    assert sorted(first.keys()) == ["A", "B", "C"]
    assert sorted(first.values()) == ["A", "B", "C"]

    packet = {
        "case_id": "case-one",
        "route_id": "resource-allocation",
    }
    normalized = normalize_judge_payload(
        {
            "winner": "A",
            "constructive_edge": "B",
            "out_of_distribution": "A",
            "out_of_distribution_arms": ["A"],
            "edge_source": "treatment_requirement",
            "baseline_likely_would_reach": "no",
            "generic_prompt_likely_would_reach": "unclear",
            "decision_relevance_if_true": "high",
            "dismissal_path": "clear",
            "clarity_cost": "low",
            "theater_flag": "no",
            "rationale": "A adds the strongest bounded pressure.",
        },
        packet=packet,
        blind_map=first,
        metadata={
            "provider": "openrouter",
            "model": "test-judge",
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": 0.0,
        },
    )
    assert validate_judge_output(normalized) == []
    assert normalized["unblinded"]["winner"] == first["A"]
    assert normalized["unblinded"]["constructive_edge"] == first["B"]
    assert normalized["unblinded"]["out_of_distribution"] == first["A"]
    assert normalized["unblinded"]["out_of_distribution_arms"] == [first["A"]]

    both = normalize_judge_payload(
        {
            "winner": "tie",
            "constructive_edge": "none",
            "out_of_distribution": "both",
            "out_of_distribution_arms": ["A", "C"],
            "edge_source": "diagnostic_question",
            "baseline_likely_would_reach": "unclear",
            "generic_prompt_likely_would_reach": "unclear",
            "decision_relevance_if_true": "medium",
            "dismissal_path": "clear",
            "clarity_cost": "medium",
            "theater_flag": "no",
            "rationale": "Two labeled outputs add different non-obvious pressures.",
        },
        packet=packet,
        blind_map=first,
        metadata={
            "provider": "openrouter",
            "model": "test-judge",
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": 0.0,
        },
    )
    assert validate_judge_output(both) == []
    assert both["unblinded"]["out_of_distribution"] == "both"
    assert both["unblinded"]["out_of_distribution_arms"] == sorted([first["A"], first["C"]])

    invalid = dict(normalized)
    invalid["out_of_distribution"] = "C"
    invalid["out_of_distribution_arms"] = ["B"]
    assert any("out_of_distribution_arms" in error for error in validate_judge_output(invalid))


def test_judge_summary_tracks_ood_separately_from_constructive_edge() -> None:
    affordance_index = load_affordance_index(AFFORDANCES_V3)
    records = [
        {
            "case_id": "case-one",
            "route_id": "resource-allocation",
            "winner": "C",
            "constructive_edge": "B",
            "out_of_distribution": "C",
            "out_of_distribution_arms": ["C"],
            "edge_source": "treatment_requirement",
            "theater_flag": "no",
            "clarity_cost": "low",
            "unblinded": {
                "winner": "C",
                "constructive_edge": "B",
                "out_of_distribution": "C",
                "out_of_distribution_arms": ["C"],
            },
            "judge_call_metadata": {
                "provider": "openrouter",
                "model": "test-judge",
                "input_tokens": 1,
                "output_tokens": 1,
                "cost_usd": 0.0,
            },
        }
    ]
    summary = summarize_judge_outputs(
        judge_records=records,
        arm_c_outputs=[],
        affordance_index=affordance_index,
        dry_run=False,
        seed=42,
        judge_provider="openrouter",
        judge_model="test-judge",
        route_count=1,
    )
    assert summary["constructive_edge_counts_unblinded"] == {"B": 1}
    assert summary["out_of_distribution_counts_unblinded"] == {"C": 1}
    assert summary["out_of_distribution_arm_counts_unblinded"] == {"C": 1}
    assert summary["out_of_distribution_by_arm_source_counts"] == {
        "C": {"treatment_requirement": 1}
    }
    assert summary["c_only_ood_source_counts"] == {"treatment_requirement": 1}
    assert summary["c_included_ood_source_counts"] == {"treatment_requirement": 1}
    assert summary["case_level_c_ood_count"] == 1
    assert summary["case_level_c_only_ood_count"] == 1
    assert summary["case_level_high_value_c_ood_count"] == 1
    assert summary["high_value_c_only_ood_count"] == 1
    assert summary["high_value_c_included_ood_count"] == 1


def test_gate4_scripts_do_not_import_runtime_engine_or_add_semantic_helpers() -> None:
    scripts = [
        REPO_ROOT / "scripts" / "run_gate4_edge_probe_experiment.py",
        REPO_ROOT / "scripts" / "judge_gate4_edge_probes.py",
    ]
    forbidden_function_fragments = ("keyword", "semantic", "rank", "score", "regex")
    for script in scripts:
        source = script.read_text(encoding="utf-8")
        assert "from engine" not in source
        assert "import engine" not in source
        tree = ast.parse(source)
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert not any(
            fragment in name.lower()
            for name in function_names
            for fragment in forbidden_function_fragments
        )
