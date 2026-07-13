#!/usr/bin/env python3
"""Build the self-contained two-case minimum viable Lolla loop receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
USEFUL_CASE = ROOT / "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
USEFUL_ROLE = ROOT / "research/independent-phase5-role-extraction-probe-2026-07-12/result.json"
USEFUL_ROLE_REVIEW = ROOT / "research/independent-phase5-role-extraction-probe-2026-07-12/source-review.json"
USEFUL_MECHANISM = ROOT / "research/independent-useful-mechanism-probe-2026-07-12/result.json"
USEFUL_MECHANISM_REVIEW = ROOT / "docs/conversation-understanding/independent-useful-mechanism-probe-result-2026-07-12.md"
USEFUL_PORTFOLIO = ROOT / "research/independent-useful-fresh-pressure-pair-2026-07-12/portfolio.json"
USEFUL_FRESH = ROOT / "research/independent-useful-fresh-pressure-pair-probe-2026-07-12/result.json"
USEFUL_FRESH_REVIEW = ROOT / "research/independent-useful-fresh-pressure-pair-probe-2026-07-12/source-review.json"
QUIET_CASE = ROOT / "research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt"
QUIET_ROLE = ROOT / "research/independent-quiet-library-v242-role-probe-2026-07-12/result.json"
QUIET_ROLE_REVIEW = ROOT / "research/independent-quiet-library-v242-role-probe-2026-07-12/source-review.json"
QUIET_MECHANISM = ROOT / "research/independent-quiet-library-mechanism-probe-2026-07-12/result.json"
QUIET_MECHANISM_REVIEW = ROOT / "research/independent-quiet-library-mechanism-probe-2026-07-12/source-review.json"
QUIET_STANDDOWN = ROOT / "research/independent-quiet-library-standdown-2026-07-12/result.json"
ROUTING = ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
CONSTITUTION = ROOT / "docs/conversation-understanding/lolla-product-constitution-v5.md"
EVAL_DOCTRINE = ROOT / "docs/conversation-understanding/lolla-evaluation-doctrine-v0.md"


ARTIFACTS = [
    ("useful_conversation", USEFUL_CASE),
    ("useful_role_result", USEFUL_ROLE),
    ("useful_role_source_review", USEFUL_ROLE_REVIEW),
    ("useful_mechanism_result", USEFUL_MECHANISM),
    ("useful_mechanism_source_review", USEFUL_MECHANISM_REVIEW),
    ("useful_portfolio", USEFUL_PORTFOLIO),
    ("useful_fresh_pair", USEFUL_FRESH),
    ("useful_fresh_source_review", USEFUL_FRESH_REVIEW),
    ("quiet_conversation", QUIET_CASE),
    ("quiet_role_result", QUIET_ROLE),
    ("quiet_role_source_review", QUIET_ROLE_REVIEW),
    ("quiet_mechanism_result", QUIET_MECHANISM),
    ("quiet_mechanism_source_review", QUIET_MECHANISM_REVIEW),
    ("quiet_standdown", QUIET_STANDDOWN),
    ("deterministic_routing", ROUTING),
    ("product_constitution", CONSTITUTION),
    ("evaluation_doctrine", EVAL_DOCTRINE),
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def call_summary(call: dict[str, Any], stage: str) -> dict[str, Any]:
    return {
        "stage": stage,
        "task_id": call.get("task_id", ""),
        "requested_model": call.get("model", ""),
        "served_model": call.get("served_model", ""),
        "served_provider": call.get("served_provider", ""),
        "operational_status": call.get("operational_status", ""),
        "prompt_tokens": call.get("prompt_tokens"),
        "completion_tokens": call.get("completion_tokens"),
        "total_tokens": call.get("total_tokens"),
        "estimated_cost_usd": call.get("estimated_cost_usd"),
        "automatic_retries": call.get("automatic_retries", 0),
        "fallback_models": call.get("fallback_models", 0),
    }


def useful_receipt() -> dict[str, Any]:
    role_result = load(USEFUL_ROLE)
    role_case = next(row for row in role_result["cases"] if row["case_id"] == "phase5-independent-useful-retailer-pilot")
    roles = role_case["joined"]["records"][0]["role_observations"]
    mechanism_result = load(USEFUL_MECHANISM)
    mechanism_call = next(row for row in mechanism_result["calls"] if row["task_id"] == "independent_useful_provider")
    fresh_result = load(USEFUL_FRESH)
    fresh_by_arm = {row["task_id"]: row["compiled"] for row in fresh_result["calls"]}
    portfolio = load(USEFUL_PORTFOLIO)
    source_review = load(USEFUL_FRESH_REVIEW)
    calls = [call_summary(row, "role_interpretation") for row in role_case["calls"]]
    calls += [call_summary(row, "mechanism_invariance_experiment") for row in mechanism_result["calls"]]
    calls += [call_summary(row, "fresh_control_pressure_pair") for row in fresh_result["calls"]]
    return {
        "case_id": "phase5-independent-useful-retailer-pilot",
        "case_kind": "independent_useful_pressure",
        "complete_conversation": USEFUL_CASE.read_text(encoding="utf-8"),
        "role_interpretation": {
            "starting": roles["starting"],
            "current": roles["current"],
            "qualification": roles["qualification"],
            "relationship": role_case["joined"]["records"][0]["relation_observation"],
            "status": "source_reviewed_pass_with_semantic_variance_visible",
        },
        "fact_free_mechanism_interpretation": {
            "assessments": mechanism_call["candidate_payload"]["assessments"],
            "routing_projection": mechanism_call["compiled"]["routing_projection"],
            "fact_boundary": mechanism_call["compiled"]["fact_boundary"],
            "protected_causal_result": {
                "mechanism": "status_signal_used_as_evidence",
                "survived_source_provider_variation": True,
                "removed_by_status_meaning_ablation": True,
            },
            "full_frozen_contract_status": mechanism_result["evaluation"]["status"],
            "full_contract_failures": [
                "secondary mechanism readings were not invariant",
                "the source-authored arm exceeded the additional unresolved-noise cap",
            ],
        },
        "deterministic_pressure_portfolio": portfolio,
        "fresh_context_reconsideration": {
            "control": fresh_by_arm["control"],
            "pressure": fresh_by_arm["pressure"],
            "mechanical_evaluation": fresh_result["evaluation"],
            "source_review": source_review,
        },
        "observed_value": {
            "status": "non_obvious_useful_pressure_observed_with_answer_integrity_failure",
            "control_limit": "The control preserved the validation gap but did not operationalize an outside-channel test.",
            "pressure_delta": "The pressure answer added an outside-channel demand test and a generalization check on retailer audience and merchandising context.",
            "lineage": ["social-proof", "confirmation-bias", "status_signal_used_as_evidence"],
            "answer_integrity_failure": "The pressure answer invented precise example thresholds unsupported by the conversation.",
            "invented_precision_examples": ["12 percent returns", "week 6", "20 percent of operating cash", "50 percent of pilot inventory"],
        },
        "call_ledger": calls,
        "call_totals": {
            "provider_calls": len(calls),
            "estimated_cost_usd": round(sum(float(row["estimated_cost_usd"] or 0) for row in calls), 12),
        },
        "claim_boundary": {
            "supported": [
                "The protected status mechanism survived source/provider role-record variation and disappeared under a status-meaning ablation.",
                "All eight deterministic candidates reached the fresh reasoner and received apply, reject, or park dispositions.",
                "The pressure arm introduced a source-reviewable outside-channel validation condition absent from the control.",
            ],
            "not_supported": [
                "The whole pressure answer was better, safe, or correct.",
                "Secondary mechanism interpretations are broadly invariant.",
                "One useful case establishes general product reliability.",
            ],
        },
    }


def quiet_receipt() -> dict[str, Any]:
    role_result = load(QUIET_ROLE)
    mechanism_result = load(QUIET_MECHANISM)
    standdown = load(QUIET_STANDDOWN)
    calls = [call_summary(row, "role_interpretation") for row in role_result["calls"]]
    calls.append(call_summary(mechanism_result["call"], "mechanism_interpretation"))
    return {
        "case_id": "phase5-independent-quiet-library-laptop-pilot",
        "case_kind": "independent_quiet_standdown",
        "complete_conversation": QUIET_CASE.read_text(encoding="utf-8"),
        "role_interpretation": {
            "starting": role_result["joined"]["role_observations"]["starting"],
            "current": role_result["joined"]["role_observations"]["current"],
            "qualification": None,
            "qualification_review": role_result["joined"]["qualification_review"],
            "source_review": load(QUIET_ROLE_REVIEW),
        },
        "fact_free_mechanism_interpretation": {
            "assessments": mechanism_result["call"]["candidate_payload"]["assessments"],
            "routing_projection": mechanism_result["call"]["compiled"]["routing_projection"],
            "fact_boundary": mechanism_result["call"]["compiled"]["fact_boundary"],
            "source_review": load(QUIET_MECHANISM_REVIEW),
        },
        "deterministic_pressure_portfolio": standdown,
        "fresh_context_reconsideration": {
            "status": "not_called_by_design",
            "reason": "The probabilistic mechanism review produced an empty fact-free routing projection, so deterministic recall had no candidate to present.",
            "candidate_dispositions_required": 0,
            "public_revision_required": False,
            "current_reasoning_preserved": True,
        },
        "observed_value": {
            "status": "correct_quiet_standdown_observed",
            "what_was_not_done": "No weakness, mental-model candidate, fresh pressure call, or public answer expansion was manufactured.",
            "modal_force_caveat": "The role model captured the full adopted plan but understated 'we will run' as conditional willingness and marked current semantic status unclear.",
        },
        "call_ledger": calls,
        "call_totals": {
            "provider_calls": len(calls),
            "estimated_cost_usd": round(sum(float(row["estimated_cost_usd"] or 0) for row in calls), 12),
        },
        "claim_boundary": {
            "supported": [
                "The model explicitly authored a source-linked no-unresolved-qualification outcome without a qualification record.",
                "All nine mechanisms were reviewed and none became unresolved or ambiguous.",
                "Deterministic routing emitted an explicit zero-candidate stand-down without deletion or semantic prefiltering.",
            ],
            "not_supported": [
                "The role interpretation preserved modal force perfectly.",
                "Every quiet conversation will stand down correctly.",
                "No future evidence could reopen the library decision.",
            ],
        },
    }


def artifact_manifest() -> list[dict[str, str]]:
    return [{"role": role, "path": str(path.relative_to(ROOT)), "sha256": sha(path)} for role, path in ARTIFACTS]


def build_receipt() -> dict[str, Any]:
    useful = useful_receipt()
    quiet = quiet_receipt()
    return {
        "schema_version": "lolla.minimum_viable_reasoning_pressure_loop_receipt.v1",
        "status": "frozen_for_cold_reader",
        "date": "2026-07-12",
        "purpose": "Show what happened in two independent Lolla reasoning-pressure paths, what each stage produced, what failed, and what is and is not earned.",
        "reader_guide": [
            "The complete conversations are source authority.",
            "Role and mechanism interpretations are probabilistic, source-linked hypotheses rather than facts.",
            "The graph mapping is deterministic and canonical but candidate recall is pressure, not relevance proof.",
            "Fresh reasoner dispositions are probabilistic judgments; apply does not prove truth and reject does not prove graph error.",
            "Hashes, calls, tokens, and receipt completeness prove custody shape, not reasoning quality.",
            "Failures are part of the receipt and must not be silently repaired or averaged away.",
        ],
        "architecture": [
            "authoritative conversation",
            "probabilistic source-linked role interpretation",
            "probabilistic controlled fact-free mechanism review",
            "deterministic canonical no-deletion recall",
            "fresh-context apply/reject/park reconsideration when candidates exist",
            "source review and self-explanatory receipt",
        ],
        "cases": {"useful_pressure": useful, "quiet_standdown": quiet},
        "cross_case_read": {
            "earned": [
                "A protected mechanism showed survival under harmless extraction variation and sensitivity to meaningful ablation.",
                "Canonical deterministic recall preserved all eight useful-case candidates without semantic prefiltering.",
                "One independent case produced a specific non-obvious pressure delta absent from its control.",
                "One independent case produced a correct empty-portfolio stand-down without forced pressure.",
            ],
            "not_earned": [
                "A clean, generally reliable pressured answer.",
                "Perfect role modal fidelity.",
                "Broad mechanism invariance.",
                "Human usefulness, production readiness, or runtime integration authority.",
            ],
            "next_gate": "A fresh cold reader must reconstruct both cases, the useful delta, the false-precision failure, the quiet stand-down, and the authorization boundary from this receipt alone.",
        },
        "artifact_manifest": artifact_manifest(),
        "total_recorded_calls": useful["call_totals"]["provider_calls"] + quiet["call_totals"]["provider_calls"],
        "total_estimated_cost_usd": round(useful["call_totals"]["estimated_cost_usd"] + quiet["call_totals"]["estimated_cost_usd"], 12),
        "scalar_quality_score": None,
        "authorizations": {
            "allowed": ["research review", "new prospective holdout experiments", "receipt transfer testing"],
            "blocked": ["runtime integration", "graph mutation", "deterministic semantic gating", "candidate prefiltering", "production claims", "quality badge"],
        },
    }


def escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def role_markdown(roles: dict[str, Any]) -> str:
    lines = []
    for role in ("starting", "current", "qualification"):
        record = roles.get(role)
        if record is None:
            lines.append(f"- {role}: no record")
            continue
        evidence = "; ".join(f"{row['alias']}: {row['text']}" for row in record.get("source_evidence", []))
        lines.append(f"- {role}: {record['role_interpretation']} Evidence: {evidence}")
    review = roles.get("qualification_review")
    if review:
        lines.append(f"- qualification review: {review['outcome']} — {review['interpretation']}")
    return "\n".join(lines)


def mechanism_table(rows: Iterable[dict[str, Any]]) -> str:
    lines = ["| Mechanism | Status | State | Source role records |", "| --- | --- | --- | --- |"]
    for row in rows:
        lines.append(f"| {escape(row['mechanism_id'])} | {escape(row['joint_status'])} | {escape(row['pattern_state'])} | {escape(', '.join(row['source_role_record_ids']))} |")
    return "\n".join(lines)


def call_table(rows: Iterable[dict[str, Any]]) -> str:
    lines = ["| Stage | Task | Served model/provider | Tokens | Estimated cost USD |", "| --- | --- | --- | ---: | ---: |"]
    for row in rows:
        lines.append(f"| {escape(row['stage'])} | {escape(row['task_id'])} | {escape(row['served_model'])} / {escape(row['served_provider'])} | {escape(row['total_tokens'])} | {escape(row['estimated_cost_usd'])} |")
    return "\n".join(lines)


def render_markdown(receipt: dict[str, Any]) -> str:
    useful = receipt["cases"]["useful_pressure"]
    quiet = receipt["cases"]["quiet_standdown"]
    portfolio_lines = "\n".join(
        f"- {row['model_id']} — recalled by {', '.join(row['recalled_by_mechanism_ids'])}"
        for row in useful["deterministic_pressure_portfolio"]["candidates"]
    )
    dispositions = "\n".join(
        f"- {row['model_id']}: {row['disposition']} / {row['effect']} — {row['disposition_note']}"
        for row in useful["fresh_context_reconsideration"]["pressure"]["candidate_dispositions"]
    )
    manifest = "\n".join(f"- {row['role']}: `{row['path']}` sha256 `{row['sha256']}`" for row in receipt["artifact_manifest"])
    return f"""# Minimum viable Lolla reasoning-pressure loop receipt

Status: frozen for cold-reader reconstruction  
Date: {receipt['date']}

## How to read this receipt

{chr(10).join('- ' + item for item in receipt['reader_guide'])}

The architecture tested was: {' → '.join(receipt['architecture'])}.

## Case A — independent useful pressure

### Complete authoritative conversation

```text
{useful['complete_conversation'].rstrip()}
```

### Source-linked role interpretation

{role_markdown(useful['role_interpretation'])}

### Fact-free mechanism interpretation

{mechanism_table(useful['fact_free_mechanism_interpretation']['assessments'])}

The protected `status_signal_used_as_evidence` mechanism survived source/provider role-record variation and disappeared when status meaning was ablated. The full frozen mechanism contract still failed because secondary readings varied and the source-authored arm exceeded its noise cap.

### Deterministic no-deletion portfolio

All eight candidates below were preserved. Their presence is pressure, not certified relevance.

{portfolio_lines}

### Fresh-context control

{useful['fresh_context_reconsideration']['control']['reconsidered_answer']}

Control change summary: {useful['fresh_context_reconsideration']['control']['change_summary']}

### Fresh-context pressure dispositions

{dispositions}

Pressure answer:

{useful['fresh_context_reconsideration']['pressure']['reconsidered_answer']}

Pressure change summary: {useful['fresh_context_reconsideration']['pressure']['change_summary']}

### Source review and failure boundary

Useful pressure was observed: the pressure answer operationalized an outside-channel demand test and a generalization check absent from the control. The full answer is not a clean reference. It invented unsupported quantitative examples: {', '.join(useful['observed_value']['invented_precision_examples'])}. This run was frozen without retry.

Supported claims:
{chr(10).join('- ' + item for item in useful['claim_boundary']['supported'])}

Claims not supported:
{chr(10).join('- ' + item for item in useful['claim_boundary']['not_supported'])}

### Useful-case call ledger

{call_table(useful['call_ledger'])}

Recorded calls: {useful['call_totals']['provider_calls']}; estimated cost: USD {useful['call_totals']['estimated_cost_usd']}.

## Case B — independent quiet stand-down

### Complete authoritative conversation

```text
{quiet['complete_conversation'].rstrip()}
```

### Source-linked role interpretation

{role_markdown(quiet['role_interpretation'])}

The negative qualification outcome was provider-authored and source-linked; code did not infer absence. The current plan was captured, but the provider understated `we will run` as conditional willingness and marked current status unclear. That modal-force caveat remains visible.

### Fact-free mechanism interpretation

{mechanism_table(quiet['fact_free_mechanism_interpretation']['assessments'])}

All nine mechanisms were `not_observed`. The fact-free routing projection was empty.

### Deterministic stand-down

Candidate count: 0. No candidate was deleted or semantically prefiltered. No graph traversal or fresh pressure call was needed. The current reasoning was preserved without public revision.

Supported claims:
{chr(10).join('- ' + item for item in quiet['claim_boundary']['supported'])}

Claims not supported:
{chr(10).join('- ' + item for item in quiet['claim_boundary']['not_supported'])}

### Quiet-case call ledger

{call_table(quiet['call_ledger'])}

Recorded calls: {quiet['call_totals']['provider_calls']}; estimated cost: USD {quiet['call_totals']['estimated_cost_usd']}.

## Cross-case conclusion

Earned:
{chr(10).join('- ' + item for item in receipt['cross_case_read']['earned'])}

Not earned:
{chr(10).join('- ' + item for item in receipt['cross_case_read']['not_earned'])}

Next gate: {receipt['cross_case_read']['next_gate']}

Total recorded provider calls: {receipt['total_recorded_calls']}. Total estimated cost: USD {receipt['total_estimated_cost_usd']}. No scalar quality score is issued.

Allowed: {', '.join(receipt['authorizations']['allowed'])}.  
Blocked: {', '.join(receipt['authorizations']['blocked'])}.

## Artifact manifest

{manifest}
"""


def validate(receipt: dict[str, Any], markdown: str) -> None:
    if receipt.get("schema_version") != "lolla.minimum_viable_reasoning_pressure_loop_receipt.v1":
        raise ValueError("receipt schema invalid")
    for row in receipt["artifact_manifest"]:
        path = ROOT / row["path"]
        if not path.is_file() or sha(path) != row["sha256"]:
            raise ValueError(f"artifact hash drifted: {row['role']}")
    useful = receipt["cases"]["useful_pressure"]
    quiet = receipt["cases"]["quiet_standdown"]
    if useful["complete_conversation"] != USEFUL_CASE.read_text(encoding="utf-8") or quiet["complete_conversation"] != QUIET_CASE.read_text(encoding="utf-8"):
        raise ValueError("complete conversation drifted")
    for case in (useful, quiet):
        conversation = case["complete_conversation"]
        for role in ("starting", "current", "qualification"):
            record = case["role_interpretation"].get(role)
            if record:
                for evidence in record.get("source_evidence", []):
                    if evidence["text"] not in conversation:
                        raise ValueError("role evidence is not in authoritative conversation")
    portfolio_ids = {row["model_id"] for row in useful["deterministic_pressure_portfolio"]["candidates"]}
    disposition_ids = {row["model_id"] for row in useful["fresh_context_reconsideration"]["pressure"]["candidate_dispositions"]}
    if portfolio_ids != disposition_ids or len(portfolio_ids) != 8:
        raise ValueError("useful candidate disposition custody is incomplete")
    if quiet["deterministic_pressure_portfolio"]["candidate_count"] != 0 or quiet["fresh_context_reconsideration"]["candidate_dispositions_required"] != 0:
        raise ValueError("quiet stand-down is not empty")
    if receipt["scalar_quality_score"] is not None:
        raise ValueError("receipt must not issue scalar score")
    if useful["complete_conversation"].rstrip() not in markdown or quiet["complete_conversation"].rstrip() not in markdown:
        raise ValueError("markdown does not contain both conversations")
    for phrase in ("unsupported quantitative", "modal-force caveat", "runtime integration"):
        if phrase.lower() not in markdown.lower():
            raise ValueError(f"markdown omitted required boundary: {phrase}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    receipt = build_receipt()
    markdown = render_markdown(receipt)
    validate(receipt, markdown)
    write_json(output / "receipt.json", receipt)
    (output / "receipt.md").write_text(markdown, encoding="utf-8")
    report = {
        "schema_version": "lolla.minimum_viable_reasoning_pressure_loop_receipt_report.v1",
        "status": "provider_free_receipt_pass",
        "receipt_json_sha256": sha(output / "receipt.json"),
        "receipt_markdown_sha256": sha(output / "receipt.md"),
        "markdown_bytes": len(markdown.encode()),
        "full_conversations_included": 2,
        "useful_candidate_dispositions": 8,
        "quiet_candidate_count": 0,
        "provider_calls": 0,
    }
    write_json(output / "report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
