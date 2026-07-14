import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/evals/build_independent_useful_fresh_pressure_pair.py"


def module():
    spec = importlib.util.spec_from_file_location("build_independent_useful_pair", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_provider_projection_becomes_no_deletion_canonical_portfolio():
    mod = module()
    portfolio = mod.build_portfolio(mod.load(mod.MECHANISM_RESULT), mod.load(mod.ROUTING), mod.load(mod.GRAPH))
    assert portfolio["unresolved_mechanism_ids"] == [
        "counterpressure_acknowledged_not_integrated",
        "missing_reversal_condition",
        "status_signal_used_as_evidence",
    ]
    assert [row["model_id"] for row in portfolio["candidates"]] == [
        "active-listening",
        "commitment-bias",
        "confirmation-bias",
        "intellectual-humility",
        "premortem",
        "signaling",
        "social-proof",
        "sunk-cost-fallacy",
    ]
    assert portfolio["candidate_deletion_performed"] is False
    assert portfolio["semantic_applicability_certified"] is False
    assert portfolio["fact_free_routing_projection"] is True


def test_pair_is_reproducible_and_control_has_no_portfolio(tmp_path):
    mod = module()
    first = mod.build(tmp_path / "first")
    second = mod.build(tmp_path / "second")
    assert first["portfolio"]["candidate_ids"] == second["portfolio"]["candidate_ids"]
    assert first["arms"]["pressure"]["user_prompt_sha256"] == second["arms"]["pressure"]["user_prompt_sha256"]
    assert first["arms"]["control"]["user_prompt_sha256"] == second["arms"]["control"]["user_prompt_sha256"]
    control = mod.load(tmp_path / "first/control-packet.json")
    pressure = mod.load(tmp_path / "first/pressure-packet.json")
    assert "pressure_portfolio" not in control
    assert len(pressure["pressure_portfolio"]) == 8
    assert control["authoritative_conversation"] == pressure["authoritative_conversation"]
