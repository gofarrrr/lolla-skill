"""Explicit qualification-review outcome for quiet-path role interpretation."""
from __future__ import annotations
import copy,hashlib,json
from collections.abc import Mapping
from typing import Any
from .reasoning_process_position_role_first_v241 import build_position_current_qualification_packet_v241,compile_position_current_qualification_response_v241,position_current_qualification_response_schema_v241
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes,sha256_bytes
PACKET_SCHEMA="lolla.reasoning_process_position_current_qualification_packet.v2_4_2"
RESPONSE_SCHEMA="lolla.reasoning_process_position_current_qualification_response.v2_4_2"
OUTCOMES=("unresolved_qualification_present","no_unresolved_qualification_observed","ambiguous_qualification_review")
def build_packet_v242(*,wrapper:Mapping[str,Any])->dict[str,Any]:
 p=build_position_current_qualification_packet_v241(wrapper=wrapper);p["schema_version"]=PACKET_SCHEMA;p["response_contract"].update({"explicit_qualification_review_required":True,"record_omission_alone_does_not_mean_no_qualification":True});p["boundary"].update({"negative_qualification_semantics_provider_authored":True,"deterministic_absence_inference":False});return p
def response_schema_v242()->dict[str,Any]:
 s=copy.deepcopy(position_current_qualification_response_schema_v241());review={"type":"object","properties":{"outcome":{"type":"string","enum":list(OUTCOMES)},"evidence_ids":{"type":"array","minItems":1,"maxItems":6,"items":{"type":"string","pattern":"^e[0-9]{3}$"}},"interpretation":{"type":"string","minLength":1,"maxLength":500},"limitations":{"type":"string","maxLength":500}},"required":["outcome","evidence_ids","interpretation","limitations"],"additionalProperties":False};s["properties"]["qualification_review"]=review;s["required"]=["records","qualification_review","allocation_note","global_limitations"];return s
def build_prompts_v242(packet:Mapping[str,Any])->dict[str,str]:
 if packet.get("schema_version")!=PACKET_SCHEMA:raise ViewSpecificInterfaceError("invalid v2.4.2 packet")
 system="You jointly interpret current position and whether any unresolved qualification remains after the complete endpoint. Compare roles before allocating meanings. An adopted condition, safeguard, stop rule, or reopen rule belongs to current; it is not itself unresolved. Return a qualification record only for a matter that remains unresolved and can change or reopen current. Always return a source-linked qualification_review outcome."
 user="PAIRED QUIET-CAPABLE PACKET\n"+canonical_json_bytes(packet).decode()+"\n\nReturn current records and, only when supported, qualification records. qualification_review must state unresolved_qualification_present, no_unresolved_qualification_observed, or ambiguous_qualification_review and cite exact aliases. Explicit user stand-down evidence supports review but does not automatically decide it. Omission alone is never interpreted as semantic absence. Preserve speaker and modal force. Return schema-valid JSON only."
 return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":sha256_bytes(system.encode()),"user_prompt_sha256":sha256_bytes(user.encode())}
def _alias_map(wrapper:Mapping[str,Any])->dict[str,str]:
 result={}
 for region in (wrapper["packet"].get("focal_region",{}),wrapper["packet"].get("prior_context",{})):
  text=region.get("annotated_sentence_text","")
  for line in text.splitlines():
   if "\t"in line and line.split("\t",1)[0].startswith("e"):result[line.split("\t",1)[0]]=line.split("\t",1)[1]
 return result
def compile_response_v242(*,response:Mapping[str,Any],wrapper:Mapping[str,Any],producer_kind:str,producer_id:str)->dict[str,Any]:
 if set(response)!={"records","qualification_review","allocation_note","global_limitations"}:raise ViewSpecificInterfaceError("v2.4.2 response fields invalid")
 review=response["qualification_review"]
 if not isinstance(review,Mapping)or set(review)!={"outcome","evidence_ids","interpretation","limitations"}or review["outcome"]not in OUTCOMES:raise ViewSpecificInterfaceError("qualification review invalid")
 aliases=_alias_map(wrapper);ids=review["evidence_ids"]
 if not isinstance(ids,list)or not ids or len(ids)!=len(set(ids))or set(ids)-set(aliases):raise ViewSpecificInterfaceError("qualification review evidence custody invalid")
 qrecords=[x for x in response["records"]if x.get("role")=="qualification"]
 if review["outcome"]=="unresolved_qualification_present"and not qrecords:raise ViewSpecificInterfaceError("present qualification outcome lacks record")
 if review["outcome"]=="no_unresolved_qualification_observed"and qrecords:raise ViewSpecificInterfaceError("negative qualification outcome conflicts with record")
 projected={k:response[k]for k in("records","allocation_note","global_limitations")};compiled=compile_position_current_qualification_response_v241(response=projected,wrapper=wrapper,producer_kind=producer_kind,producer_id=producer_id);compiled["schema_version"]=RESPONSE_SCHEMA;compiled["qualification_review"]={**dict(review),"source_evidence":[{"alias":x,"text":aliases[x]}for x in ids],"producer_kind":producer_kind,"producer_id":producer_id};compiled["boundary"].update({"qualification_review_provider_authored":True,"negative_outcome_inferred_by_code":False,"adopted_condition_is_not_automatically_qualification":True});return compiled
def join_v242(*,starting_compiled:Mapping[str,Any],paired_compiled:Mapping[str,Any])->dict[str,Any]:
 starts=starting_compiled.get("observations",[]);current=paired_compiled["role_compiled"]["current"].get("observations",[]);qualification=paired_compiled["role_compiled"]["qualification"].get("observations",[]);review=paired_compiled["qualification_review"]
 if len(starts)!=1 or len(current)!=1:raise ViewSpecificInterfaceError("v2.4.2 join requires one starting and current record")
 if review["outcome"]=="unresolved_qualification_present"and not qualification:raise ViewSpecificInterfaceError("v2.4.2 unresolved join lacks qualification")
 if review["outcome"]=="no_unresolved_qualification_observed"and qualification:raise ViewSpecificInterfaceError("v2.4.2 quiet join has qualification record")
 return {"schema_version":"lolla.reasoning_process_position_role_first_join.v2_4_2","status":"quiet_capable_position_join_complete","role_observations":{"starting":starts[0],"current":current[0],"qualification":qualification[0]if qualification else None},"qualification_review":review,"boundary":{"semantic_absence_provider_authored":True,"deterministic_semantic_inference":False,"direct_graph_routing_allowed":False}}
