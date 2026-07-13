import json
from pathlib import Path
import pytest
from engine.system_b.canonical_model_selection import CanonicalSelectionError,build_challenge_cards,build_challenge_prompts,build_challenge_selection_packet
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
ROOT=Path(__file__).resolve().parents[1]
def models():return json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"]
def role():return json.loads((ROOT/"research/role-record-pattern-invariance-corpus-2026-07-12/packets/housing_source_first.json").read_text())
def packet(recalled=None,mode="graph_recalled_canonical"):
 cards=build_challenge_cards(models());recalled=recalled or {"premortem":["missing_reversal_condition"]};return build_challenge_selection_packet(arm_id="x",role_packet=role(),cards=cards,candidate_ids=sorted(recalled),selection_mode=mode,recalled_by=recalled,controlled_mechanism_ids=set(MECHANISMS),source_refs=[])

def test_all_222_challenge_cards_have_consistent_pressure_fields():
 cards=build_challenge_cards(models());assert len(cards)==222
 for mid,card in cards.items():
  assert card["model_id"]==mid;assert set(card)=={"schema_version","model_id","display_name","challenge_when","do_not_apply_when","pressure_question"};assert all(card.values());assert "Do not apply without source support" in card["do_not_apply_when"]

def test_commitment_card_no_longer_inverts_harmful_lock_in_into_avoidance():
 card=build_challenge_cards(models())["commitment-bias"]
 assert "dead path" in card["challenge_when"]
 assert "reverse course" in card["pressure_question"]
 assert "Prior public commitment" not in card["do_not_apply_when"]

def test_graph_candidate_requires_controlled_fact_free_recall_provenance():
 with pytest.raises(CanonicalSelectionError,match="lacks recall provenance"):packet({"premortem":[]})
 with pytest.raises(CanonicalSelectionError,match="provenance is invalid"):packet({"premortem":["invented"]})
 p=packet();assert p["candidate_cards"][0]["recalled_by_mechanism_ids"]==["missing_reversal_condition"]
 assert p["boundary"]["fact_free_recall_provenance_included"] is True

def test_direct_candidate_cannot_falsely_claim_graph_provenance():
 with pytest.raises(CanonicalSelectionError,match="direct candidate"):
  packet({"premortem":["missing_reversal_condition"]},mode="direct_all_canonical")

def test_prompt_treats_recall_as_hypothesis_and_preserves_abstention():
 prompts=build_challenge_prompts(packet());text=prompts["system_prompt"]+prompts["user_prompt"]
 assert "not proof" in text and "Every candidate may be rejected" in text and "six is a hard cap, not a target" in text
