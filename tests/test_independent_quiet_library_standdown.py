import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/evals/seal_independent_quiet_library_standdown.py"


def module():
    spec = importlib.util.spec_from_file_location("seal_quiet_standdown", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_empty_projection_seals_explicit_no_force_standdown(tmp_path):
    result = module().seal(tmp_path)
    assert result["candidate_count"] == 0
    assert result["candidates"] == []
    assert result["candidate_deletion_performed"] is False
    assert result["semantic_prefilter_performed"] is False
    assert result["graph_calls"] == 0
    assert result["standdown"]["fresh_pressure_call_required"] is False
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "deterministic_empty_portfolio_standdown"
