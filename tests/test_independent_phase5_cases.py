import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_independent_cases_are_frozen_realistic_multiturn_holdouts():
 targets=json.loads((ROOT/"docs/evals/independent-phase5-case-targets-v1.json").read_text())
 assert targets["status"]=="prospectively_frozen_before_any_case_calls"
 for case in targets["cases"].values():
  text=(ROOT/case["source_path"]).read_text();assert text.count("] USER:")==7;assert text.count("] ASSISTANT:")==7

def test_useful_case_has_status_signal_target_and_quiet_case_has_no_positive_mechanisms():
 cases=json.loads((ROOT/"docs/evals/independent-phase5-case-targets-v1.json").read_text())["cases"]
 useful=cases["phase5-independent-useful-retailer-pilot"];quiet=cases["phase5-independent-quiet-research-meeting"]
 assert useful["protected_mechanism"]=="status_signal_used_as_evidence";assert useful["mechanism_targets"]["status_signal_used_as_evidence"]=="unresolved"
 assert set(quiet["mechanism_targets"].values())=={"not_observed"};assert quiet["phase5_expected_case_kind"]=="quiet_standdown"

def test_both_source_review_role_targets_compile_without_quarantine():
 for name in("independent-phase5-useful-role-case-2026-07-12","independent-phase5-quiet-role-case-2026-07-12"):
  report=json.loads((ROOT/"research"/name/"target-report.json").read_text());assert report["status"]=="pre_execution_target_gate_pass";assert report["admitted_role_record_count"]==3;assert report["quarantined_record_count"]==0;assert report["provider_calls"]==0
