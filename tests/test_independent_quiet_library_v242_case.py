import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/evals/build_independent_quiet_library_v242_case.py"
OUTPUT = ROOT / "research/independent-phase5-quiet-library-v242-role-case-2026-07-12"


def module():
    spec = importlib.util.spec_from_file_location("build_independent_quiet_v242", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_new_quiet_case_has_complete_source_custody():
    mod = module()
    wrapper = mod.build_wrapper()
    assert wrapper["packet"]["source"]["conversation_message_count"] == 14
    assert wrapper["packet"]["focal_turn_indices"] == [1, 7]
    assert len(wrapper["focal_alias_map"]) == 11
    assert wrapper["packet"]["boundary"]["protected_target_included"] is False


def test_source_target_uses_explicit_negative_review_without_qualification_record():
    target = module().load(OUTPUT / "source-review-target.json")
    assert [row["role"] for row in target["paired_response"]["records"]] == ["current"]
    assert target["paired_response"]["qualification_review"]["outcome"] == "no_unresolved_qualification_observed"
    assert set(target["mechanism_targets"].values()) == {"not_observed"}
