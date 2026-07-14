import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"research/controlled-vocabulary-boundary-audit-2026-07-12/report.json"

def test_canonical_registry_has_222_unique_collision_free_ids():
    value=json.loads(REPORT.read_text())
    assert value["canonical"]["model_count"] == 222
    assert value["canonical"]["canonical_id_unique"] is True
    assert value["canonical"]["normalized_display_name_collision_count"] == 0
    assert value["graph"]["model_count_with_any_edge"] == 222

def test_current_mechanism_bridge_is_narrow_but_not_mislabeled_as_total_reachability():
    value=json.loads(REPORT.read_text())
    assert value["mechanism_bridge"]["mechanism_count"] == 9
    assert value["mechanism_bridge"]["direct_seed_model_count"] == 19
    assert "not total graph reachability" in value["mechanism_bridge"]["note"]

def test_names_fit_but_full_operational_menu_is_materially_larger():
    value=json.loads(REPORT.read_text())["menu_size"]
    assert value["names_and_ids_utf8_bytes"] < 20000
    assert value["names_ids_select_and_danger_utf8_bytes"] > 150000
    assert "not an adequate semantic selection contract" in value["warning"]

def test_existing_families_are_overlapping_not_a_ready_selector():
    value=json.loads(REPORT.read_text())["hierarchy"]
    assert value["reasoning_family_count"] == 9
    assert value["multi_family_model_count"] == 222
    assert value["zero_family_model_count"] == 0

def test_stale_unknown_chunk_id_is_exposed_and_never_silently_normalized():
    value=json.loads(REPORT.read_text())
    assert value["integrity"]["unknown_chunk_ids"] == ["commitment-and-consistency-bias"]
    assert value["status"] == "provider_free_audit_integrity_fail"


def test_post_migration_audit_resolves_all_selection_facing_ids():
    value=json.loads((ROOT/"research/controlled-vocabulary-boundary-audit-after-migration-2026-07-12/report.json").read_text())
    assert value["status"] == "provider_free_audit_pass"
    assert value["integrity"] == {"unknown_chunk_ids": [], "unknown_edge_ids": [], "unknown_seed_ids": []}


def test_reasoning_signals_has_one_canonical_commitment_key():
    raw=(ROOT/"data/curated/reasoning_signals.json").read_text()
    assert raw.count('"commitment-bias":') == 1
    assert '"commitment-and-consistency-bias":' not in raw
