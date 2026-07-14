from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

from engine.system_b.r4_complementary_readers import canonical_json_bytes
from scripts.evals import build_r4_residual_task_contract as builder
from scripts.evals import build_r4_semantic_distinction_contract as historical_builder
from scripts.evals import finalize_r4_semantic_distinction_execution as finalizer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-residual-task-contract-2026-07-14"
CASES = (
    "v1-case01-flood-infrastructure",
    "v1-case04-component-sourcing",
)
FROZEN_ROOT = ROOT / "research/lolla-r4-semantic-distinction-contract-2026-07-14"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_provider_free_residual_contract_rebuilds_byte_exactly() -> None:
    files = builder.build_files(OUTPUT)
    contract = builder.validate(OUTPUT)

    assert files[str((OUTPUT / "contract.json").relative_to(ROOT))] == (
        OUTPUT / "contract.json"
    ).read_bytes()
    assert contract["status"] == "provider_free_residual_contract_complete"
    assert contract["provider_calls"] == 0
    assert contract["provider_cost_usd"] == 0.0
    assert contract["provider_call_authorized"] is False
    assert contract["holdout_prepared"] is False
    assert contract["model_semantic_validation"] is False
    assert contract["runtime_or_graph_integration"] is False
    assert contract["completion_decision"] == (
        "residual_contract_ready_for_new_holdout_design"
    )


def test_full_case_previews_preserve_a3_source_prior_and_request_dimensions() -> None:
    for case_id in CASES:
        prospective_root = OUTPUT / "cases" / case_id
        frozen_root = FROZEN_ROOT / "cases" / case_id
        packet = _load(frozen_root / "uncertainty-packet.json")
        preview = _load(prospective_root / "residual-request-preview.json")
        frozen_preview = _load(frozen_root / "uncertainty-request-preview.json")
        context = _load(prospective_root / "context-manifest.json")
        body = preview["body"]

        source = canonical_json_bytes(packet["source"]).decode("utf-8")
        prior = canonical_json_bytes(packet["prior_interpretation_context"]).decode(
            "utf-8"
        )
        user = body["messages"][1]["content"]
        provider_visible_contract = "\n".join(
            (
                body["messages"][0]["content"],
                user,
                json.dumps(
                    body["response_format"]["json_schema"]["schema"],
                    sort_keys=True,
                ),
            )
        )
        assert user.count(source) == 1
        assert user.count(prior) == 1
        assert user.index(source) < user.index(prior) < user.index("<task>")
        assert user.rstrip().endswith("</task>")
        assert "unresolved_matter" not in provider_visible_contract
        assert "reopen_condition" not in provider_visible_contract

        frozen_body = frozen_preview["body"]
        frozen_user = frozen_body["messages"][1]["content"]
        assert frozen_user.count(source) == 1
        assert frozen_user.count(prior) == 1
        assert frozen_user.index(source) < frozen_user.index(prior) < frozen_user.index(
            "<task>"
        )
        unchanged_projection = copy.deepcopy(body)
        unchanged_projection["messages"] = copy.deepcopy(frozen_body["messages"])
        unchanged_projection["response_format"]["json_schema"]["name"] = frozen_body[
            "response_format"
        ]["json_schema"]["name"]
        unchanged_projection["response_format"]["json_schema"]["schema"] = copy.deepcopy(
            frozen_body["response_format"]["json_schema"]["schema"]
        )
        assert unchanged_projection == frozen_body
        assert body["model"] == frozen_body["model"]
        assert body["provider"] == frozen_body["provider"]
        assert body["seed"] == frozen_body["seed"]
        assert body["max_tokens"] == frozen_body["max_tokens"]
        assert body["reasoning"] == frozen_body["reasoning"]
        assert body["stream"] == frozen_body["stream"]
        assert body["response_format"]["type"] == frozen_body["response_format"][
            "type"
        ]
        assert body["response_format"]["json_schema"]["strict"] is True

        assert context["section_order"] == [
            "system_instruction",
            "authoritative_source",
            "fallible_prior_interpretation_context",
            "task",
        ]
        assert context["task_at_end_invariant"] is True
        assert context["complete_source_inclusion"] is True
        assert context["source"]["artifact_sha256"] == packet["source"]["sha256"]
        assert context["source"]["canonical_context_sha256"] == hashlib.sha256(
            canonical_json_bytes(packet["source"])
        ).hexdigest()
        assert context["prior"]["artifact_sha256"] == packet[
            "prior_interpretation_context"
        ]["artifact_sha256"]
        assert context["prior"]["canonical_context_sha256"] == hashlib.sha256(
            canonical_json_bytes(packet["prior_interpretation_context"])
        ).hexdigest()
        assert context["source_and_prior_unchanged_from_consumed_a3"] is True
        assert context["fallible_prior_declaration"] is True
        assert context["request_estimate"]["schema_utf8_bytes"] > 0
        assert context["request_estimate"]["estimated_input_tokens"] > 0
        assert context["provider_calls"] == 0
        assert context["provider_cost_usd"] == 0.0
        assert set(context["request_body_top_level_components"]) == set(body)
        assert all(
            row["utf8_bytes"] >= 0 and row["estimated_tokens"] >= 0
            for row in context["prompt_components"]
        )


def test_prompt_delta_is_exact_shorter_and_schema_increase_is_explained() -> None:
    contract = _load(OUTPUT / "contract.json")
    delta = contract["prompt_delta_against_v2"]

    assert delta["estimator"] == (
        "ceil(utf8_bytes/2); deterministic conservative estimate, not provider tokenization"
    )
    assert delta["system_prompt"]["utf8_byte_delta"] == -137
    assert delta["user_prompt"]["utf8_byte_delta"] == -54
    assert delta["total_prompt"]["utf8_byte_delta"] == -191
    assert delta["total_prompt"]["estimated_token_delta"] < 0
    assert delta["response_schema"]["utf8_byte_delta"] == 122
    assert delta["material_increase_explanations"] == [
        {
            "component": "response_schema",
            "reason": (
                "Longer residual surface identifiers and the exact dual-basis evidence "
                "description add schema bytes while leaving its structure and bounds unchanged."
            ),
            "utf8_byte_increase": 122,
        }
    ]


def test_historical_execution_and_relationship_evidence_remain_hash_exact() -> None:
    contract = _load(OUTPUT / "contract.json")
    assert historical_builder.validate()["run_id"] == (
        "lolla-r4-semantic-distinction-holdout-a3"
    )
    assert finalizer.validate()["run_id"] == "lolla-r4-semantic-distinction-holdout-a3"

    for record in contract["frozen_history"]:
        path = ROOT / record["path"]
        assert path.is_file()
        assert _sha(path) == record["sha256"]
    assert contract["relationship_boundary"]["changed"] is False
    for record in contract["relationship_boundary"]["frozen_prompt_files"]:
        assert _sha(ROOT / record["path"]) == record["sha256"]


def test_builder_has_no_transport_or_environment_dependency() -> None:
    source = Path(builder.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {"anthropic", "google", "httpx", "openai", "requests", "urllib"}
    )
    assert "os.environ" not in source
    assert "urlopen(" not in source
