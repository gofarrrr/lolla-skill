"""Research-only fresh-context reasoning pressure packet and compiler."""
from __future__ import annotations
import hashlib,json,re
from collections.abc import Mapping
from typing import Any
PACKET_SCHEMA="lolla.fresh_reasoning_pressure_input.v1";RESPONSE_SCHEMA="lolla.fresh_reasoning_pressure_response.v1"
CONTROL_PACKET_SCHEMA="lolla.fresh_reasoning_control_input.v1";CONTROL_RESPONSE_SCHEMA="lolla.fresh_reasoning_control_response.v1"
PACKET_SCHEMA_V2="lolla.fresh_reasoning_pressure_input.v2"
CONTROL_PACKET_SCHEMA_V2="lolla.fresh_reasoning_control_input.v2"
class FreshPressureError(ValueError):pass
def _canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v):return hashlib.sha256(_canonical(v).encode()).hexdigest()
def build_packet(*,case_id:str,conversation:str,portfolio:Mapping[str,Any],challenge_cards:Mapping[str,dict],source_refs:list[dict])->dict:
    turns={int(x)for x in re.findall(r"(?m)^\[Turn (\d+)\] (?:USER|ASSISTANT):",conversation)}
    if not turns:raise FreshPressureError("authoritative conversation has no turns")
    candidates=[]
    for item in portfolio["candidates"]:
        mid=item["model_id"]
        if mid not in challenge_cards:raise FreshPressureError("portfolio model is not canonical")
        mechanisms=item["recalled_by_mechanism_ids"]
        if not mechanisms:raise FreshPressureError("candidate lacks recall provenance")
        candidates.append({"model_id":mid,"challenge_card":challenge_cards[mid],"recalled_by_mechanism_ids":mechanisms,"portfolio_status":"intentionally_noisy_pressure_hypothesis"})
    if not candidates or len(candidates)>10 or len({x["model_id"]for x in candidates})!=len(candidates):raise FreshPressureError("portfolio bounds invalid")
    packet={"schema_version":PACKET_SCHEMA,"case_id":case_id,"authoritative_conversation":conversation,"source_turn_numbers":sorted(turns),"pressure_portfolio":candidates,"source_refs":source_refs,"instructions":{"graph_recall_is_applicability_proof":False,"every_candidate_must_be_inspected":True,"allowed_dispositions":["apply","reject","park"],"rejection_is_valid":True,"preserve_strong_original_reasoning":True,"unsupported_case_facts_allowed":False,"candidate_deletion_before_reconsideration":False},"boundary":{"fresh_context_required":True,"case_facts_reattached_after_graph_recall":True,"canonical_ids_only":True,"all_candidates_preserved":True,"graph_runtime_effect":"none","production_authorization":False}}
    packet["packet_sha256"]=_sha(packet);return packet
def response_schema(candidate_ids:list[str])->dict[str,Any]:
    row={"type":"object","properties":{"model_id":{"type":"string","enum":candidate_ids},"disposition":{"type":"string","enum":["apply","reject","park"]},"source_turn_numbers":{"type":"array","minItems":1,"maxItems":7,"items":{"type":"integer","minimum":1,"maximum":100}},"effect":{"type":"string","enum":["reframe","new_condition","new_alternative","uncertainty_change","reversal_rule","reinforces_existing","no_material_effect"]},"disposition_note":{"type":"string","minLength":1,"maxLength":1000}},"required":["model_id","disposition","source_turn_numbers","effect","disposition_note"],"additionalProperties":False}
    return {"type":"object","properties":{"candidate_dispositions":{"type":"array","minItems":len(candidate_ids),"maxItems":len(candidate_ids),"items":row},"reconsidered_answer":{"type":"string","minLength":1,"maxLength":8000},"change_summary":{"type":"string","minLength":1,"maxLength":1500}},"required":["candidate_dispositions","reconsidered_answer","change_summary"],"additionalProperties":False}
def build_prompts(packet:Mapping[str,Any])->dict[str,str]:
    system="You are a fresh-context reasoner. Reconsider the authoritative conversation using every canonical pressure candidate as an intentionally noisy hypothesis. Apply only what changes the reasoning; explicitly reject or park the rest. Graph recall is not proof."
    user="FRESH REASONING PRESSURE PACKET\n"+_canonical(packet)+"\n\nInspect every candidate exactly once. apply means the lens materially changes or sharpens the answer. reject means it does not fit this case. park means plausible but not decision-relevant enough to use now. Cite exact source turn numbers for each disposition. Preserve strong existing reasoning and do not invent facts. Then write a self-contained reconsidered answer and a concise change summary. Candidate dispositions are audit evidence and must not appear as a mechanical checklist in the answer."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}
def compile_response(*,response:Mapping[str,Any],packet:Mapping[str,Any])->dict:
    if set(response)!={"candidate_dispositions","reconsidered_answer","change_summary"}:raise FreshPressureError("response envelope invalid")
    rows=response["candidate_dispositions"];candidates={x["model_id"]for x in packet["pressure_portfolio"]};turns=set(packet["source_turn_numbers"])
    if not isinstance(rows,list)or len(rows)!=len(candidates):raise FreshPressureError("candidate disposition coverage invalid")
    seen=set();compiled=[]
    for row in rows:
        fields={"model_id","disposition","source_turn_numbers","effect","disposition_note"}
        if not isinstance(row,Mapping)or set(row)!=fields:raise FreshPressureError("candidate disposition shape invalid")
        mid=row["model_id"];refs=row["source_turn_numbers"]
        if mid not in candidates or mid in seen or row["disposition"]not in {"apply","reject","park"}:raise FreshPressureError("candidate disposition identity invalid")
        if not isinstance(refs,list)or not refs or set(refs)-turns:raise FreshPressureError("candidate disposition turn custody invalid")
        if row["effect"]not in {"reframe","new_condition","new_alternative","uncertainty_change","reversal_rule","reinforces_existing","no_material_effect"}:raise FreshPressureError("candidate effect invalid")
        if row["disposition"]=="reject"and row["effect"]!="no_material_effect":raise FreshPressureError("rejected candidate claims material effect")
        seen.add(mid);compiled.append(dict(row))
    if seen!=candidates:raise FreshPressureError("candidate disposition coverage incomplete")
    if not isinstance(response["reconsidered_answer"],str)or not response["reconsidered_answer"].strip():raise FreshPressureError("reconsidered answer empty")
    return {"schema_version":RESPONSE_SCHEMA,"case_id":packet["case_id"],"source_packet_sha256":packet["packet_sha256"],"candidate_dispositions":sorted(compiled,key=lambda x:x["model_id"]),"reconsidered_answer":response["reconsidered_answer"],"change_summary":response["change_summary"],"all_candidates_accounted_for":True,"graph_runtime_modified":False,"non_claims":["dispositions_are_probabilistic","revised_answer_is_not_proven_better","not_runtime_authorization"]}

def build_control_packet(*,case_id:str,conversation:str,source_refs:list[dict])->dict:
    turns={int(x)for x in re.findall(r"(?m)^\[Turn (\d+)\] (?:USER|ASSISTANT):",conversation)}
    if not turns:raise FreshPressureError("control conversation has no turns")
    packet={"schema_version":CONTROL_PACKET_SCHEMA,"case_id":case_id,"authoritative_conversation":conversation,"source_turn_numbers":sorted(turns),"source_refs":source_refs,"instructions":{"fresh_context_required":True,"external_pressure_portfolio_included":False,"preserve_strong_original_reasoning":True,"unsupported_case_facts_allowed":False},"boundary":{"treatment":"transcript_only_fresh_reconsideration","graph_candidates_included":False,"graph_runtime_effect":"none","production_authorization":False}}
    packet["packet_sha256"]=_sha(packet);return packet
def control_response_schema()->dict[str,Any]:
    return {"type":"object","properties":{"reconsidered_answer":{"type":"string","minLength":1,"maxLength":8000},"change_summary":{"type":"string","minLength":1,"maxLength":1500}},"required":["reconsidered_answer","change_summary"],"additionalProperties":False}
def build_control_prompts(packet:Mapping[str,Any])->dict[str,str]:
    system="You are a fresh-context reasoner. Reconsider the authoritative conversation from the ground up, preserve strong existing reasoning, and improve it only where the conversation supports a material change."
    user="TRANSCRIPT-ONLY CONTROL PACKET\n"+_canonical(packet)+"\n\nWrite a self-contained reconsidered answer and a concise change summary. Do not invent facts. This control contains no external mental-model pressure portfolio; reason only from the authoritative conversation."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}

def build_packet_v2(*,case_id:str,conversation:str,portfolio:Mapping[str,Any],challenge_cards:Mapping[str,dict],source_refs:list[dict])->dict:
    """Build a v2 packet that explicitly forbids unsupported quantitative precision."""
    packet=build_packet(case_id=case_id,conversation=conversation,portfolio=portfolio,challenge_cards=challenge_cards,source_refs=source_refs)
    packet["schema_version"]=PACKET_SCHEMA_V2
    packet["instructions"]["unsupported_quantitative_thresholds_allowed"]=False
    packet["instructions"]["unknown_thresholds_must_remain_questions_or_selection_tasks"]=True
    packet["packet_sha256"]=_sha({key:value for key,value in packet.items()if key!="packet_sha256"})
    return packet

def build_prompts_v2(packet:Mapping[str,Any])->dict[str,str]:
    if packet.get("schema_version")!=PACKET_SCHEMA_V2:raise FreshPressureError("v2 pressure packet required")
    system="You are a fresh-context reasoner. Reconsider the authoritative conversation using every canonical pressure candidate as an intentionally noisy hypothesis. Apply only what changes the reasoning; explicitly reject or park the rest. Graph recall is not proof. Do not manufacture quantitative precision."
    user="FRESH REASONING PRESSURE PACKET V2\n"+_canonical(packet)+"\n\nInspect every candidate exactly once. apply means the lens materially changes or sharpens the answer. reject means it does not fit this case. park means plausible but not decision-relevant enough to use now. Cite exact source turn numbers for each disposition. Preserve strong existing reasoning and do not invent facts. Never invent a numerical threshold, percentage, date, quantity, or cutoff merely to make a condition sound concrete. If the conversation does not support a value, state the evidence needed or the decision process for choosing it and leave the value unresolved. Then write a self-contained reconsidered answer and a concise change summary. Candidate dispositions are audit evidence and must not appear as a mechanical checklist in the answer."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}

def build_control_packet_v2(*,case_id:str,conversation:str,source_refs:list[dict])->dict:
    packet=build_control_packet(case_id=case_id,conversation=conversation,source_refs=source_refs)
    packet["schema_version"]=CONTROL_PACKET_SCHEMA_V2
    packet["instructions"]["unsupported_quantitative_thresholds_allowed"]=False
    packet["instructions"]["unknown_thresholds_must_remain_questions_or_selection_tasks"]=True
    packet["packet_sha256"]=_sha({key:value for key,value in packet.items()if key!="packet_sha256"})
    return packet

def build_control_prompts_v2(packet:Mapping[str,Any])->dict[str,str]:
    if packet.get("schema_version")!=CONTROL_PACKET_SCHEMA_V2:raise FreshPressureError("v2 control packet required")
    system="You are a fresh-context reasoner. Reconsider the authoritative conversation from the ground up, preserve strong existing reasoning, and improve it only where the conversation supports a material change. Do not manufacture quantitative precision."
    user="TRANSCRIPT-ONLY CONTROL PACKET V2\n"+_canonical(packet)+"\n\nWrite a self-contained reconsidered answer and a concise change summary. Do not invent facts. Never invent a numerical threshold, percentage, date, quantity, or cutoff merely to make a condition sound concrete. If the conversation does not support a value, state the evidence needed or the decision process for choosing it and leave the value unresolved. This control contains no external mental-model pressure portfolio; reason only from the authoritative conversation."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}
def compile_control_response(*,response:Mapping[str,Any],packet:Mapping[str,Any])->dict:
    if set(response)!={"reconsidered_answer","change_summary"}or not all(isinstance(response[x],str)and response[x].strip()for x in response):raise FreshPressureError("control response invalid")
    return {"schema_version":CONTROL_RESPONSE_SCHEMA,"case_id":packet["case_id"],"source_packet_sha256":packet["packet_sha256"],"reconsidered_answer":response["reconsidered_answer"],"change_summary":response["change_summary"],"external_pressure_portfolio_included":False,"graph_runtime_modified":False,"non_claims":["fresh_second_pass_is_not_pressure_effect","revised_answer_is_not_proven_better","not_runtime_authorization"]}
