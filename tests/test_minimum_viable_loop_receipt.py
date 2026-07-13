import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/evals/build_minimum_viable_loop_receipt.py"


def module():
    spec = importlib.util.spec_from_file_location("build_minimum_loop_receipt", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_receipt_is_self_contained_and_preserves_both_failure_modes():
    mod = module()
    receipt = mod.build_receipt()
    markdown = mod.render_markdown(receipt)
    mod.validate(receipt, markdown)
    assert receipt["cases"]["useful_pressure"]["complete_conversation"].rstrip() in markdown
    assert receipt["cases"]["quiet_standdown"]["complete_conversation"].rstrip() in markdown
    assert "12 percent returns" in markdown
    assert "modal-force caveat" in markdown
    assert receipt["scalar_quality_score"] is None


def test_receipt_candidate_and_standdown_custody_are_exact():
    receipt = module().build_receipt()
    useful = receipt["cases"]["useful_pressure"]
    quiet = receipt["cases"]["quiet_standdown"]
    assert len(useful["deterministic_pressure_portfolio"]["candidates"]) == 8
    assert len(useful["fresh_context_reconsideration"]["pressure"]["candidate_dispositions"]) == 8
    assert quiet["deterministic_pressure_portfolio"]["candidate_count"] == 0
    assert quiet["fresh_context_reconsideration"]["status"] == "not_called_by_design"


def test_builder_writes_hash_report(tmp_path):
    mod = module()
    receipt = mod.build_receipt()
    markdown = mod.render_markdown(receipt)
    mod.validate(receipt, markdown)
    mod.write_json(tmp_path / "receipt.json", receipt)
    (tmp_path / "receipt.md").write_text(markdown)
    assert json.loads((tmp_path / "receipt.json").read_text())["status"] == "frozen_for_cold_reader"
