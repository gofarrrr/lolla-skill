import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/evals/build_independent_quiet_library_mechanism_packet.py"


def module():
    spec = importlib.util.spec_from_file_location("build_independent_quiet_mechanism", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_packet_uses_actual_provider_join_and_no_gold(tmp_path):
    report = module().build(tmp_path)
    packet = json.loads((tmp_path / "packet.json").read_text())
    assert report["status"] == "provider_free_quiet_mechanism_packet_pass"
    assert [row["role"] for row in packet["role_records"]] == ["starting", "current"]
    assert packet["qualification_review"]["outcome"] == "no_unresolved_qualification_observed"
    assert packet["boundary"]["expected_patterns_included"] is False
    assert report["provider_calls"] == 0
