import copy,json
from pathlib import Path
import pytest
from engine.system_b.reasoning_process_position_role_first_v24 import build_position_starting_packet_v24,compile_position_starting_response_v24
from engine.system_b.reasoning_process_position_role_first_v242 import build_packet_v242,build_prompts_v242,compile_response_v242,join_v242,response_schema_v242
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
ROOT=Path(__file__).resolve().parents[1];CASE=ROOT/"research/independent-phase5-quiet-role-case-2026-07-12"
def data():return json.loads((CASE/"position-endpoint.json").read_text()),json.loads((CASE/"source-review-target.json").read_text())
def quiet_response():
 _,t=data();return {"records":[copy.deepcopy(t["paired_response"]["records"][0])],"qualification_review":{"outcome":"no_unresolved_qualification_observed","evidence_ids":["e036","e038","e039"],"interpretation":"No material unresolved qualification remains; predefined gates already govern reopening.","limitations":"Bounded to the endpoint capture."},"allocation_note":"Current contains adopted safeguards; no unresolved qualification record is emitted.","global_limitations":"One endpoint review."}
def test_schema_requires_explicit_source_linked_qualification_review():
 s=response_schema_v242();assert "qualification_review"in s["required"];assert set(s["properties"]["qualification_review"]["properties"]["outcome"]["enum"])=={"unresolved_qualification_present","no_unresolved_qualification_observed","ambiguous_qualification_review"}
def test_quiet_source_target_compiles_without_manufactured_qualification():
 w,_=data();c=compile_response_v242(response=quiet_response(),wrapper=w,producer_kind="source_reviewer",producer_id="test");assert c["qualification_review"]["outcome"]=="no_unresolved_qualification_observed";assert c["role_compiled"]["qualification"]["observations"]==[];assert c["derived_envelope_status"]["qualification"]=="not_found"
def test_quiet_join_preserves_negative_review_and_null_qualification():
 w,t=data();sp=build_position_starting_packet_v24(wrapper=w,role="starting");start=compile_position_starting_response_v24(response=t["starting_response"],packet=sp,producer_kind="source_reviewer",producer_id="test");paired=compile_response_v242(response=quiet_response(),wrapper=w,producer_kind="source_reviewer",producer_id="test");joined=join_v242(starting_compiled=start,paired_compiled=paired);assert joined["status"]=="quiet_capable_position_join_complete";assert joined["role_observations"]["qualification"]is None;assert joined["boundary"]["deterministic_semantic_inference"]is False
def test_negative_outcome_conflicting_with_qualification_record_fails():
 w,t=data();r=quiet_response();r["records"].append(t["paired_response"]["records"][1])
 with pytest.raises(ViewSpecificInterfaceError,match="conflicts"):compile_response_v242(response=r,wrapper=w,producer_kind="test",producer_id="test")
def test_missing_or_unknown_review_evidence_fails_closed():
 w,_=data();r=quiet_response();r["qualification_review"]["evidence_ids"]=["e999"]
 with pytest.raises(ViewSpecificInterfaceError,match="custody"):compile_response_v242(response=r,wrapper=w,producer_kind="test",producer_id="test")
def test_prompt_distinguishes_adopted_rules_from_unresolved_matters():
 w,_=data();text=" ".join(build_prompts_v242(build_packet_v242(wrapper=w)).values());assert "adopted condition, safeguard, stop rule, or reopen rule"in text and"Omission alone is never interpreted"in text
