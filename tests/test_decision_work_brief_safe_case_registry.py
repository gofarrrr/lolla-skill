from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_runtime_bundle import (
    build_decision_work_brief_runtime_bundle,
)
from engine.system_b.decision_work_brief_safe_case_registry import (
    REGISTRY_SCHEMA_VERSION,
    DecisionWorkBriefSafeCaseRegistryError,
    load_safe_case_registry,
    render_safe_case_registry_entry_json,
    resolve_safe_case_registry_entry,
    resolver_kwargs_from_case_registry,
)
from engine.system_b.decision_work_brief_safe_supply_resolver import (
    resolve_decision_work_brief_safe_supply,
    write_resolver_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.md"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/resolve_decision_work_brief_safe_case_registry.py"
)
SUPPLY_SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/resolve_decision_work_brief_safe_supply.py"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FALSE_FLAGS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
}


def _write_completed_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"schema_version": "fixture.v0", "artifact": name}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe fixture revised answer placeholder.",
        encoding="utf-8",
    )


def _registry_with_ref(
    tmp_path: Path,
    *,
    ref_name: str,
    ref_value: str,
) -> Path:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["entries"] = [dict(registry["entries"][0])]
    registry["entries"][0]["safe_artifact_refs"] = dict(
        registry["entries"][0]["safe_artifact_refs"]
    )
    registry["entries"][0]["safe_artifact_refs"][ref_name] = ref_value
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    return path


def _load_registry() -> dict[str, Any]:
    return load_safe_case_registry(REGISTRY_PATH)


def test_registry_json_parses_and_lists_expected_cases() -> None:
    registry = _load_registry()

    assert registry["schema_version"] == REGISTRY_SCHEMA_VERSION
    assert {entry["case_id"] for entry in registry["entries"]} == EXPECTED_CASES
    assert registry["excluded_candidates"] == []


def test_registry_entries_use_relative_existing_safe_refs() -> None:
    registry = _load_registry()

    for entry in registry["entries"]:
        refs = entry["safe_artifact_refs"]
        for ref in refs.values():
            assert isinstance(ref, str)
            assert ref
            candidate = Path(ref)
            assert not candidate.is_absolute()
            assert ".." not in candidate.parts
            assert (REPO_ROOT / ref).exists()


def test_registry_entries_have_conservative_flags_and_non_claims() -> None:
    registry = _load_registry()

    for entry in registry["entries"]:
        for field in FALSE_FLAGS:
            assert entry[field] is False
        assert entry["allowed_resolver_mode"] == "checked_in_safe_case_registry"
        assert "not_product_proof" in entry["non_claims"]
        assert "not_human_validation" in entry["non_claims"]
        assert "not_advice_correctness" in entry["non_claims"]
        assert "not_answer_quality_scoring" in entry["non_claims"]
        assert "not_agent_action_authorization" in entry["non_claims"]
        assert "not_general_arbitrary_run_solution" in entry["non_claims"]


def test_registry_contains_no_private_markers() -> None:
    rendered = (
        REGISTRY_PATH.read_text(encoding="utf-8")
        + "\n"
        + DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + Path(__file__).read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_registry_loader_resolves_entry_and_resolver_kwargs() -> None:
    entry = resolve_safe_case_registry_entry(
        case_key="launch-public-enterprise-beta",
        registry_path=REGISTRY_PATH,
    )
    kwargs = resolver_kwargs_from_case_registry(
        case_key="launch-public-enterprise-beta",
        registry_path=REGISTRY_PATH,
    )
    rendered = render_safe_case_registry_entry_json(entry, pretty=True)

    assert entry["schema_version"].endswith("checked_in_safe_case_registry_entry.v0")
    assert entry["entry"]["case_id"] == "launch-public-enterprise-beta"
    assert set(kwargs) == {
        "brief_markdown_path",
        "enriched_brief_path",
        "interpretation_read_path",
        "triage_read_path",
    }
    assert str(REPO_ROOT) not in rendered


def test_registry_loader_rejects_missing_ref(tmp_path: Path) -> None:
    registry = _registry_with_ref(
        tmp_path,
        ref_name="rendered_brief_markdown_ref",
        ref_value="docs/conversation-understanding/missing-safe-brief.md",
    )

    try:
        load_safe_case_registry(registry)
    except DecisionWorkBriefSafeCaseRegistryError as exc:
        assert "ref was missing" in str(exc)
    else:
        raise AssertionError("registry with missing ref should fail")


def test_registry_loader_rejects_local_absolute_path(tmp_path: Path) -> None:
    unsafe_ref = tmp_path / "brief.md"
    unsafe_ref.write_text("safe text\n", encoding="utf-8")
    registry = _registry_with_ref(
        tmp_path,
        ref_name="rendered_brief_markdown_ref",
        ref_value=str(unsafe_ref),
    )

    try:
        load_safe_case_registry(registry)
    except DecisionWorkBriefSafeCaseRegistryError as exc:
        assert "relative repo refs" in str(exc)
    else:
        raise AssertionError("registry with local absolute ref should fail")


def test_registry_loader_rejects_privacy_marker_content(tmp_path: Path) -> None:
    unsafe_repo_ref = "docs/conversation-understanding/unsafe-registry-fixture.md"
    unsafe_path = REPO_ROOT / unsafe_repo_ref
    unsafe_path.write_text("unsafe " + "raw_message" + "_content\n", encoding="utf-8")
    registry = _registry_with_ref(
        tmp_path,
        ref_name="rendered_brief_markdown_ref",
        ref_value=unsafe_repo_ref,
    )

    try:
        try:
            load_safe_case_registry(registry)
        except DecisionWorkBriefSafeCaseRegistryError as exc:
            assert "private-marker content" in str(exc)
        else:
            raise AssertionError("registry with privacy marker content should fail")
    finally:
        unsafe_path.unlink(missing_ok=True)


def test_resolver_consumes_checked_in_safe_case_registry(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    result = resolve_decision_work_brief_safe_supply(
        run_dir=run_dir,
        contract_path=CONTRACT_PATH,
        mode="checked_in_safe_case_registry",
        case_registry_path=REGISTRY_PATH,
        case_key="launch-public-enterprise-beta",
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["resolver_mode"] == "checked_in_safe_case_registry"
    assert result["resolver_status"] == "resolved"
    assert result["feeds_runtime_bundle"] is True
    assert result["case_registry"]["case_key"] == "launch-public-enterprise-beta"
    assert result["case_registry"]["case_registry_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
    )
    resolved = {item["input_name"] for item in result["resolved_inputs"]}
    assert "rendered_brief_markdown_ref" in resolved
    assert "enriched_brief_markdown_ref" in resolved
    assert "interpretation_read_json_ref" in resolved
    assert "automatic_triage_read_json_ref" in resolved


def test_registry_resolver_output_feeds_runtime_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    resolver_output = tmp_path / "resolver.json"
    _write_completed_run(run_dir)

    result = resolve_decision_work_brief_safe_supply(
        run_dir=run_dir,
        contract_path=CONTRACT_PATH,
        mode="checked_in_safe_case_registry",
        case_registry_path=REGISTRY_PATH,
        case_key="launch-public-enterprise-beta",
        created_at="2026-07-02T00:00:00Z",
    )
    write_resolver_json(resolver_output, result, pretty=True)
    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver_output,
        created_at="2026-07-02T00:00:00Z",
    )
    receipt = (output_dir / "decision_work/user_receipt.md").read_text(
        encoding="utf-8"
    )

    assert status["attachment_state"] == "generated"
    assert status["resolver_summary"]["resolver_status"] == "resolved"
    assert status["resolver_summary"]["resolver_mode"] == (
        "checked_in_safe_case_registry"
    )
    assert "Decision Work Brief: available" in receipt


def test_registry_does_not_change_runtime_hook_default() -> None:
    from engine.system_b.decision_work_brief_runtime_attachment import (
        decision_work_runtime_attachment_enabled,
    )

    assert decision_work_runtime_attachment_enabled({}) is False


def test_registry_cli_writes_entry(tmp_path: Path) -> None:
    out = tmp_path / "entry.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--case-registry",
            str(REGISTRY_PATH),
            "--case-key",
            "launch-public-enterprise-beta",
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_key"] == "launch-public-enterprise-beta"
    assert payload["resolver_mode"] == "checked_in_safe_case_registry"


def test_safe_supply_cli_accepts_registry_mode(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    out = tmp_path / "resolver.json"
    _write_completed_run(run_dir)

    result = subprocess.run(
        [
            sys.executable,
            str(SUPPLY_SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--contract",
            str(CONTRACT_PATH),
            "--mode",
            "checked_in_safe_case_registry",
            "--case-registry",
            str(REGISTRY_PATH),
            "--case-key",
            "launch-public-enterprise-beta",
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["resolver_status"] == "resolved"
    assert payload["feeds_runtime_bundle"] is True


def test_pr175_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, REGISTRY_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
