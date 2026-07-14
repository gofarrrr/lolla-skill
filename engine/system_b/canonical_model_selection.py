"""Research-only canonical mental-model cards and bounded selection contracts."""
from __future__ import annotations
import hashlib, json
from collections.abc import Mapping
from typing import Any

CARD_SCHEMA="lolla.canonical_model_card.v1"
CHALLENGE_CARD_SCHEMA="lolla.canonical_model_challenge_card.v2"
ASSESSMENT_CARD_SCHEMA="lolla.canonical_model_assessment_card.v3"
PACKET_SCHEMA="lolla.canonical_model_selection_input.v1"
RESPONSE_SCHEMA="lolla.canonical_model_selection_response.v1"
ASSESSMENT_SCHEMA="lolla.canonical_model_candidate_assessment.v1"

class CanonicalSelectionError(ValueError): pass
def _canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v): return hashlib.sha256(_canonical(v).encode()).hexdigest()
def _clip(value,limit):
    value=" ".join(str(value).split())
    return value if len(value)<=limit else value[:limit-1].rstrip()+"…"

def build_cards(models:Mapping[str,Any])->dict[str,dict]:
    cards={}
    for model_id,model in sorted(models.items()):
        select=model.get("select_when") or []; danger=model.get("danger_when") or []
        if not select or not danger: raise CanonicalSelectionError(f"model lacks selection semantics: {model_id}")
        cards[model_id]={"schema_version":CARD_SCHEMA,"model_id":model_id,"display_name":str(model.get("display_name") or model.get("name") or model_id),"use_when":_clip(select[0],190),"avoid_when":_clip(danger[0],150),"input_type":_clip(model.get("input_type",""),80),"output_type":_clip(model.get("output_type",""),80)}
    return cards

def build_challenge_cards(models:Mapping[str,Any])->dict[str,dict]:
    cards={}
    for model_id,model in sorted(models.items()):
        failures=model.get("failure_modes") or []; questions=model.get("premortem_questions") or []
        input_type=_clip(model.get("input_type",""),80); output_type=_clip(model.get("output_type",""),80)
        if not failures or not questions or not input_type or not output_type:
            raise CanonicalSelectionError(f"model lacks challenge semantics: {model_id}")
        failure=failures[0].get("description",""); question=questions[0].get("description","")
        if not failure or not question: raise CanonicalSelectionError(f"model challenge semantics are empty: {model_id}")
        cards[model_id]={"schema_version":CHALLENGE_CARD_SCHEMA,"model_id":model_id,"display_name":str(model.get("display_name") or model.get("name") or model_id),"challenge_when":_clip(f"The records support a {input_type}, and this failure signal remains unresolved: {failure}",300),"do_not_apply_when":_clip(f"Do not apply without source support for a {input_type}, or when asking the pressure question would not materially change the {output_type}.",220),"pressure_question":_clip(question,220)}
    return cards

def build_assessment_cards(models:Mapping[str,Any])->dict[str,dict]:
    cards={}
    for model_id,model in sorted(models.items()):
        failures=model.get("failure_modes") or [];questions=model.get("premortem_questions") or []
        input_type=_clip(model.get("input_type",""),80);output_type=_clip(model.get("output_type",""),80)
        if not failures or not questions or not input_type or not output_type:raise CanonicalSelectionError(f"model lacks assessment semantics: {model_id}")
        failure=failures[0].get("description","");question=questions[0].get("description","")
        cards[model_id]={"schema_version":ASSESSMENT_CARD_SCHEMA,"model_id":model_id,"display_name":str(model.get("display_name") or model.get("name") or model_id),"challenge_when":_clip(f"Use as a pressure lens when the records support a {input_type} and a {output_type} could materially change the unresolved reasoning.",240),"failure_signal":_clip(failure,220),"do_not_apply_when":_clip(f"Do not apply without source support for a {input_type}, or when the pressure question could not materially change the {output_type}.",200),"pressure_question":_clip(question,220)}
    return cards

def build_challenge_selection_packet(*,arm_id:str,role_packet:Mapping[str,Any],cards:Mapping[str,dict],candidate_ids:list[str],selection_mode:str,recalled_by:Mapping[str,list[str]],controlled_mechanism_ids:set[str],source_refs:list[dict])->dict:
    base=build_selection_packet(arm_id=arm_id,role_packet=role_packet,cards=cards,candidate_ids=candidate_ids,selection_mode=selection_mode,source_refs=source_refs)
    enriched=[]
    for card in base["candidate_cards"]:
        ids=list(recalled_by.get(card["model_id"],[]))
        if len(ids)!=len(set(ids)) or set(ids)-controlled_mechanism_ids: raise CanonicalSelectionError("recall provenance is invalid")
        if selection_mode=="graph_recalled_canonical" and not ids: raise CanonicalSelectionError("graph candidate lacks recall provenance")
        if selection_mode=="direct_all_canonical" and ids: raise CanonicalSelectionError("direct candidate cannot claim graph provenance")
        enriched.append({**card,"recalled_by_mechanism_ids":sorted(ids)})
    base["candidate_cards"]=enriched;base["boundary"]["fact_free_recall_provenance_included"]=selection_mode=="graph_recalled_canonical";base["packet_sha256"]=_sha({k:v for k,v in base.items() if k!="packet_sha256"});return base

def build_challenge_prompts(packet:Mapping[str,Any])->dict[str,str]:
    system="Select only canonical mental models whose challenge card pressures an unresolved joint reasoning weakness. recalled_by_mechanism_ids are fact-free deterministic recall provenance: inspect them as hypotheses, not proof. Every candidate may be rejected."
    user="CHALLENGE SELECTION PACKET\n"+_canonical(packet)+"\n\nReturn only outcome and selections. selected requires source support for challenge_when and a pressure_question that could materially change the reasoning. ambiguous preserves a genuinely competing applicability reading without activating it. do_not_apply_when is binding. Graph recall does not certify relevance. Use all_not_applicable or insufficient_evidence with an empty selections array. Cite exact role_record_ids. Never invent an ID, synonym, mechanism, or model. Prefer a small discriminating set; six is a hard cap, not a target."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}

def build_exhaustive_assessment_packet(*,challenge_packet:Mapping[str,Any],mechanism_cards:Mapping[str,dict])->dict:
    packet=json.loads(json.dumps(challenge_packet))
    for candidate in packet["candidate_cards"]:
        refs=[]
        for mechanism_id in candidate["recalled_by_mechanism_ids"]:
            if mechanism_id not in mechanism_cards: raise CanonicalSelectionError("mechanism card custody invalid")
            refs.append({"mechanism_id":mechanism_id,**mechanism_cards[mechanism_id]})
        candidate["recall_mechanism_cards"]=refs
    packet["schema_version"]="lolla.canonical_model_exhaustive_assessment_input.v1"
    packet["boundary"]["global_abstention_shortcut"]=False
    packet["boundary"]["exactly_one_assessment_per_candidate"]=True
    packet["packet_sha256"]=_sha({k:v for k,v in packet.items() if k!="packet_sha256"})
    return packet

def exhaustive_response_schema(candidate_ids:list[str])->dict:
    item={"type":"object","properties":{"model_id":{"type":"string","enum":candidate_ids},"status":{"type":"string","enum":["applicable","ambiguous","not_applicable","insufficient_evidence"]},"source_role_record_ids":{"type":"array","minItems":0,"maxItems":3,"items":{"type":"string","minLength":1,"maxLength":120}}},"required":["model_id","status","source_role_record_ids"],"additionalProperties":False}
    return {"type":"object","properties":{"assessments":{"type":"array","minItems":len(candidate_ids),"maxItems":len(candidate_ids),"items":item}},"required":["assessments"],"additionalProperties":False}

def build_exhaustive_prompts(packet:Mapping[str,Any])->dict[str,str]:
    system="Assess every recalled canonical mental model exactly once against the final joint reasoning trajectory. The operational recall mechanism cards explain why deterministic recall produced the candidate; they are hypotheses, not proof. Negative assessment is valid for every candidate."
    user="EXHAUSTIVE CANDIDATE PACKET\n"+_canonical(packet)+"\n\nReturn exactly one assessment for every candidate model_id, with no omissions or duplicates. applicable means the challenge card and at least one recall mechanism card are source-supported and the pressure question could materially improve the unresolved reasoning. ambiguous means competing applicability readings remain. not_applicable means the supplied evidence does not support this pressure. insufficient_evidence means the role-record capture is too weak to decide. applicable and ambiguous require exact source_role_record_ids; not_applicable requires an empty list; insufficient_evidence may cite the records whose loss or weakness causes uncertainty. Do not rank, invent, or rename anything. Do not treat deterministic recall as relevance proof."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}

def compile_exhaustive_response(*,response:Mapping[str,Any],packet:Mapping[str,Any])->dict:
    rows=response.get("assessments");candidate_ids=[x["model_id"] for x in packet["candidate_cards"]]
    if set(response)!={"assessments"} or not isinstance(rows,list) or len(rows)!=len(candidate_ids): raise CanonicalSelectionError("assessment coverage invalid")
    valid_records={x["role_record_id"] for x in packet["role_records"]};seen=set();compiled=[]
    for row in rows:
        if not isinstance(row,Mapping) or set(row)!={"model_id","status","source_role_record_ids"}:raise CanonicalSelectionError("assessment shape invalid")
        mid,status,ids=row["model_id"],row["status"],row["source_role_record_ids"]
        if mid not in candidate_ids or mid in seen or status not in {"applicable","ambiguous","not_applicable","insufficient_evidence"}:raise CanonicalSelectionError("assessment identity invalid")
        if not isinstance(ids,list) or len(ids)>3 or len(ids)!=len(set(ids)) or set(ids)-valid_records:raise CanonicalSelectionError("assessment evidence custody invalid")
        if status in {"applicable","ambiguous"} and not ids:raise CanonicalSelectionError("positive or ambiguous assessment lacks evidence")
        if status=="not_applicable" and ids:raise CanonicalSelectionError("not-applicable assessment cannot cite evidence")
        seen.add(mid);compiled.append({"model_id":mid,"status":status,"source_role_record_ids":sorted(ids)})
    if seen!=set(candidate_ids):raise CanonicalSelectionError("assessment candidate coverage incomplete")
    active=sorted(x["model_id"] for x in compiled if x["status"]=="applicable")
    return {"schema_version":ASSESSMENT_SCHEMA,"arm_id":packet["arm_id"],"assessments":sorted(compiled,key=lambda x:x["model_id"]),"active_model_ids":active,"canonical_id_validated":True,"invented_ids":[],"graph_runtime_modified":False,"non_claims":["semantic_statuses_are_probabilistic","complete_assessment_is_not_forced_activation","not_runtime_authorization"]}

def build_selection_packet(*,arm_id:str,role_packet:Mapping[str,Any],cards:Mapping[str,dict],candidate_ids:list[str],selection_mode:str,source_refs:list[dict])->dict:
    if selection_mode not in {"direct_all_canonical","graph_recalled_canonical"}: raise CanonicalSelectionError("selection mode invalid")
    if not candidate_ids or len(candidate_ids)!=len(set(candidate_ids)) or set(candidate_ids)-set(cards): raise CanonicalSelectionError("candidate custody invalid")
    records=[]
    for item in role_packet["role_records"]:
        records.append({k:item[k] for k in ("role_record_id","role","semantic_status","role_interpretation","evidence_ids","stance_components","fidelity_note","limitations")})
    packet={"schema_version":PACKET_SCHEMA,"arm_id":arm_id,"selection_mode":selection_mode,"role_records":records,"candidate_cards":[cards[x] for x in candidate_ids],"candidate_count":len(candidate_ids),"source_refs":source_refs,"boundary":{"canonical_ids_only":True,"invented_ids_allowed":False,"all_candidates_may_be_rejected":True,"raw_conversation_included":False,"expected_selection_included":False,"graph_model_names_in_role_records":False,"maximum_selected":6}}
    packet["packet_sha256"]=_sha(packet); return packet

def response_schema(candidate_ids:list[str])->dict:
    item={"type":"object","properties":{"model_id":{"type":"string","enum":candidate_ids},"disposition":{"type":"string","enum":["selected","ambiguous"]},"source_role_record_ids":{"type":"array","minItems":1,"maxItems":3,"items":{"type":"string","minLength":1,"maxLength":120}}},"required":["model_id","disposition","source_role_record_ids"],"additionalProperties":False}
    return {"type":"object","properties":{"outcome":{"type":"string","enum":["candidates_selected","all_not_applicable","insufficient_evidence"]},"selections":{"type":"array","minItems":0,"maxItems":6,"items":item}},"required":["outcome","selections"],"additionalProperties":False}

def build_prompts(packet:Mapping[str,Any])->dict[str,str]:
    system="Select only canonical mental models that provide a justified reasoning lens for the unresolved joint trajectory. Do not match by industry, entity, or topic. Every candidate may be rejected."
    user="SELECTION PACKET\n"+_canonical(packet)+"\n\nReturn only outcome and selections. selected means the card directly pressures an unresolved reasoning weakness supported by the role records. ambiguous means a genuinely competing applicability reading worth preserving but not activating. Use all_not_applicable or insufficient_evidence with an empty selections array. Cite exact role_record_ids. Never invent an ID, synonym, or model outside candidate_cards. Prefer a small discriminating set; six is a hard cap, not a target."
    return {"system_prompt":system,"user_prompt":user,"system_prompt_sha256":hashlib.sha256(system.encode()).hexdigest(),"user_prompt_sha256":hashlib.sha256(user.encode()).hexdigest()}

def compile_response(*,response:Mapping[str,Any],packet:Mapping[str,Any])->dict:
    if set(response)!={"outcome","selections"} or response["outcome"] not in {"candidates_selected","all_not_applicable","insufficient_evidence"} or not isinstance(response["selections"],list) or len(response["selections"])>6: raise CanonicalSelectionError("response envelope invalid")
    if (response["outcome"]=="candidates_selected") != bool(response["selections"]): raise CanonicalSelectionError("outcome and selections disagree")
    candidates={x["model_id"] for x in packet["candidate_cards"]}; records={x["role_record_id"] for x in packet["role_records"]}; seen=set(); compiled=[]
    for row in response["selections"]:
        if not isinstance(row,Mapping) or set(row)!={"model_id","disposition","source_role_record_ids"}: raise CanonicalSelectionError("selection shape invalid")
        mid=row["model_id"]; ids=row["source_role_record_ids"]
        if mid not in candidates or mid in seen: raise CanonicalSelectionError("selection ID custody invalid")
        if row["disposition"] not in {"selected","ambiguous"} or not isinstance(ids,list) or not ids or len(ids)>3 or set(ids)-records: raise CanonicalSelectionError("selection evidence custody invalid")
        seen.add(mid); compiled.append({"model_id":mid,"disposition":row["disposition"],"source_role_record_ids":sorted(set(ids))})
    return {"schema_version":RESPONSE_SCHEMA,"arm_id":packet["arm_id"],"selection_mode":packet["selection_mode"],"outcome":response["outcome"],"selections":sorted(compiled,key=lambda x:x["model_id"]),"canonical_id_validated":True,"invented_ids":[],"graph_runtime_modified":False,"non_claims":["selection_is_probabilistic","canonical_identity_is_not_applicability_proof","not_runtime_authorization"]}
