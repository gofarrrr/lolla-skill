#!/usr/bin/env python3
"""Lane 4 calibration — Round 2 (fresh scenarios).

Same harness as test_lane4.py but entirely new cases to test generalization.
Covers: prediction, causal-diagnosis, action-planning, decision-evaluation
across different business domains.

Usage:
    python3 scripts/test_lane4_round2.py              # run all
    python3 scripts/test_lane4_round2.py --scenario 3  # run one
    python3 scripts/test_lane4_round2.py --verbose      # full details
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.system_b.boundary_provider import OpenAICompatibleBoundaryClient
from engine.system_b.conversation_context import ConversationContext, ExtractionPayload, Turn
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.structural_coverage import run_structural_coverage_from_ir

logging.basicConfig(level=logging.INFO, format="%(name)s  %(levelname)s  %(message)s")

_KG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_graph.json")

def _load_structural_routing() -> dict:
    with open(_KG_PATH) as f:
        return json.load(f)["structural_coverage_routing"]


def _make_context(question: str, vanilla_answer: str) -> ConversationContext:
    return ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text=question),
            Turn(turn_index=2, speaker="assistant", text=vanilla_answer),
        ),
        extraction=ExtractionPayload(
            decision_situation=question,
            live_constraints=(),
            synthesized_position=vanilla_answer,
            reasoning_passages=(),
            original_framing=question,
            dropped_threads=(),
        ),
    )

def _make_boundary() -> OpenAICompatibleBoundaryClient:
    client = OpenAICompatibleBoundaryClient.openrouter_from_env()
    if not client.api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    print(f"Using: {client.provider_name} / {client.model}")
    return client


# ── FRESH SCENARIOS ─────────────────────────────────────────────────────

SCENARIOS: list[dict] = [
    # ──────────────────────────────────────────────────────────────────
    # 1. PREDICTION — "What happens if we raise prices 20%?"
    #    Answer gives revenue math but misses behavioral/competitive response
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Price increase prediction — missing behavior, competition, feedback",
        "question": (
            "We're a project management SaaS ($15M ARR, 2,200 customers). "
            "We haven't raised prices in 3 years. If we raise all plans by 20%, "
            "what happens?"
        ),
        "vanilla_answer": (
            "A 20% price increase on $15M ARR gives you $3M in incremental "
            "revenue if nobody churns. Realistically, expect 5-10% churn from "
            "price-sensitive customers (mostly small accounts). Net effect: "
            "$1.5-2.5M additional ARR. Your enterprise customers won't blink — "
            "they negotiate custom contracts anyway. The SMB segment will feel "
            "it most. Grandfather existing annual contracts until renewal, then "
            "apply the increase. New customers get the new price immediately. "
            "Communicate the increase 60 days in advance with a clear value "
            "narrative about features you've shipped in 3 years."
        ),
        "expected_gaps": {
            "competitive-dynamics",
            "feedback-system-dynamics",
            "behavioral-intervention",
        },
        "notes": (
            "Answer does revenue math but doesn't model: How do competitors "
            "respond? How does the price change feed back into acquisition and "
            "upsell behavior? What behavior-change mechanism makes customers accept "
            "the increase vs revolt?"
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 2. CAUSAL DIAGNOSIS — "Why is our engineering velocity tanking?"
    #    Answer lists symptoms but no root cause methodology
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Engineering velocity — missing root cause depth, incentives, info quality",
        "question": (
            "Our engineering velocity has dropped 40% over the last two quarters. "
            "We've hired 15 new engineers (team is now 60), but sprint completion "
            "rates are worse than when we were 45. Deployments per week went from "
            "12 to 7. What's going on?"
        ),
        "vanilla_answer": (
            "Classic Brooks's Law situation — adding people to a late project "
            "makes it later. Your 15 new hires need ramp-up time (typically 3-6 "
            "months to full productivity). Meanwhile, senior engineers are spending "
            "time onboarding instead of building. The coordination overhead also "
            "increases quadratically with team size. Check your code review "
            "bottleneck — if PRs are sitting in review for days, that's your "
            "throttle. Also look at your CI/CD pipeline times — if builds take "
            "30+ minutes, engineers context-switch and lose flow state. The "
            "deployment drop from 12 to 7 suggests either risk aversion (bigger "
            "batches, less frequent deploys) or process overhead (more approvals, "
            "more staging gates)."
        ),
        "expected_gaps": {
            "causal-diagnosis",
            "incentive-alignment",
            "information-quality",
        },
        "notes": (
            "Answer cites Brooks's Law (a framework) but doesn't do root cause "
            "analysis — doesn't distinguish which of 5+ hypotheses is actually "
            "driving the drop. Doesn't question whether the metrics are reliable. "
            "Doesn't explore whether incentive structures changed with team growth."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 3. ACTION PLANNING — "How do we migrate 500 enterprise customers
    #    off our legacy API?"
    #    Answer gives steps but no sequencing logic or risk management
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "API migration — missing timing, risk response, stakeholders",
        "question": (
            "We need to sunset our v1 API and migrate 500 enterprise customers "
            "to v2. The v1 API has known security vulnerabilities we can't patch "
            "without breaking changes. Some customers have built deep integrations. "
            "How should we approach this?"
        ),
        "vanilla_answer": (
            "Build a compatibility layer that translates v1 calls to v2 under "
            "the hood. This buys you time while customers migrate at their own "
            "pace. Provide migration tooling — automated request/response format "
            "converters, a migration guide, and dedicated migration support. "
            "Set a sunset date 12 months out. Send quarterly reminders with "
            "migration progress dashboards for each customer. Offer white-glove "
            "migration for your top 50 accounts (by revenue). For the long tail, "
            "provide self-serve tooling and office hours. Kill v1 on the sunset "
            "date — any customer still on v1 gets automatically routed through "
            "the compatibility layer with a deprecation warning header."
        ),
        "expected_gaps": {
            "timing-sequencing",
            "risk-response",
            "stakeholder-alignment",
        },
        "notes": (
            "Answer gives a plan but doesn't sequence WHY this order. Doesn't "
            "size what happens if 20% of customers refuse to migrate (revenue at "
            "risk). Doesn't identify who internally and externally must agree "
            "to the sunset timeline."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 4. DECISION — "Should we hire a CRO?"
    #    Answer focused on role description, misses org dynamics
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "CRO hire — missing scope, incentives, commitment",
        "question": (
            "We're a $22M ARR B2B SaaS. Our VP Sales has been here since $2M "
            "and is great at managing the current team but struggling with "
            "enterprise sales motions. Our CEO is spending 40% of his time on "
            "revenue. Should we hire a CRO?"
        ),
        "vanilla_answer": (
            "Yes, hire a CRO. At $22M ARR you're at the inflection point where "
            "a dedicated revenue leader pays for themselves. The right CRO brings "
            "enterprise sales methodology, board-level revenue forecasting, and "
            "cross-functional alignment between sales, marketing, and customer "
            "success. Look for someone who has taken a company from $20M to $50M+ "
            "before. Expect to pay $350-450K OTE with meaningful equity. The "
            "VP Sales can report to the CRO — if he's as good as you say, the "
            "CRO will value his institutional knowledge and customer relationships. "
            "The CEO time recovery alone justifies the hire — 40% of CEO time "
            "is worth more than $400K in almost any scenario."
        ),
        "expected_gaps": {
            "scope-boundary",
            "incentive-alignment",
            "commitment-reversibility",
        },
        "notes": (
            "Answer assumes the CRO solves the problem without defining scope "
            "(what exactly does the CRO own vs CEO?). Doesn't address VP Sales "
            "incentive misalignment (reports to new boss, may leave). Doesn't "
            "consider what happens if the CRO hire doesn't work out — cost of "
            "a bad C-level hire."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 5. PREDICTION — "What happens to our business if AI agents
    #    replace 30% of knowledge worker tasks in 3 years?"
    #    Answer is speculative, misses uncertainty classification
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "AI disruption prediction — missing uncertainty, scaling, existing-vs-new",
        "question": (
            "We sell a workflow automation platform for legal teams ($18M ARR). "
            "If AI agents can handle 30% of paralegal and associate tasks within "
            "3 years, what happens to our business?"
        ),
        "vanilla_answer": (
            "Your business is directly in the path of disruption. If AI agents "
            "handle 30% of legal tasks, demand for your current workflow tool "
            "drops because there are fewer manual workflows to automate. But "
            "there's an opportunity: pivot from automating human workflows to "
            "orchestrating AI agent workflows. Legal teams will need tools to "
            "manage, audit, and QA what agents produce. Compliance and audit "
            "trails become more important, not less. Your existing relationships "
            "with legal teams are your moat — they trust you for workflow "
            "management. Build agent orchestration features into your platform. "
            "The firms that adopt AI earliest will be your design partners. "
            "Price the new capabilities as a premium tier."
        ),
        "expected_gaps": {
            "uncertainty-type",
            "scaling-dynamics",
            "existing-vs-new",
        },
        "notes": (
            "Answer assumes the 30% premise without questioning it (uncertainty "
            "type). Doesn't consider what happens to unit economics as scale "
            "changes. Doesn't separate protecting existing revenue base from "
            "building the new agent orchestration business."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 6. CONTROL — Thorough decision analysis that should have FEW gaps
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "CONTROL — thorough vendor selection, expect few gaps",
        "question": (
            "We need to choose between building our own billing system or using "
            "Stripe Billing. We're a $10M ARR SaaS with complex pricing (usage + "
            "seat + feature tiers). Our finance team is drowning in manual "
            "reconciliation. Which should we pick?"
        ),
        "vanilla_answer": (
            "Use Stripe Billing. Here's why through the key tensions:\n\n"
            "Lock-in vs optionality: Yes, you're coupling to Stripe's billing "
            "model, but your current technical debt in billing is already a form "
            "of lock-in — you're locked into manual processes that don't scale. "
            "Stripe's API is well-documented enough that migration away is "
            "feasible in 6-9 months if needed. The switching cost is real but "
            "bounded.\n\n"
            "Build cost vs buy cost: Building a billing system that handles "
            "usage + seat + feature tiers takes 2-3 engineers 6+ months. At "
            "your engineering cost, that's $400-600K plus ongoing maintenance. "
            "Stripe Billing costs ~2.9% + fee structure. At $10M ARR, that's "
            "~$290K/year. The build breaks even in 18 months but ties up "
            "engineers who should be building product.\n\n"
            "The finance team's reconciliation pain is your forcing function — "
            "every month of delay costs you in errors and labor. Stripe solves "
            "this in weeks, not months.\n\n"
            "Who needs to agree: finance (primary user), engineering (integration "
            "work), and your CFO (cost approval). Engineering may resist because "
            "they want to build — frame it as freeing them for product work.\n\n"
            "The data quality question: your current billing data is messy. "
            "Migration to Stripe forces a cleanup, which is painful but overdue. "
            "Validate your existing subscription records before importing — "
            "garbage in, garbage out.\n\n"
            "Start with new customers on Stripe immediately, migrate existing "
            "customers in cohorts over 3 months, largest first so you catch "
            "edge cases early."
        ),
        "expected_gaps": set(),
        "notes": (
            "This answer deliberately engages with commitment-reversibility "
            "(lock-in analysis), resource-allocation (build vs buy economics), "
            "stakeholder-alignment (who agrees), information-quality (data "
            "quality), timing-sequencing (phased rollout with reasoning). "
            "Should have minimal gaps."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 7. DECISION — "Should we open-source our core product?"
    #    Answer focuses on marketing benefits, misses deep tensions
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Open-source decision — missing competitive response, resource cost, reversibility",
        "question": (
            "We're a dev tools company ($8M ARR, 35 people). Our main product "
            "is a testing framework. The market is moving toward open-source "
            "alternatives. Should we open-source our core product and monetize "
            "through enterprise features and support?"
        ),
        "vanilla_answer": (
            "Open-sourcing could be a strong strategic move. The developer tools "
            "market increasingly expects open-source — it builds trust, enables "
            "community contributions, and creates a distribution flywheel. Your "
            "enterprise features (SSO, audit logs, team management, advanced "
            "analytics) become the monetization layer. Companies like GitLab, "
            "Elastic, and HashiCorp have proven this model works. The community "
            "becomes your sales funnel: developers adopt free, then convince "
            "their companies to buy enterprise. Keep the core product strong "
            "and open, gate the enterprise features behind a commercial license. "
            "Your existing $8M in revenue won't disappear overnight — most "
            "enterprise customers are paying for support and features they "
            "already depend on."
        ),
        "expected_gaps": {
            "competitive-dynamics",
            "resource-allocation",
            "commitment-reversibility",
        },
        "notes": (
            "Answer cites precedents (GitLab, Elastic) but doesn't model how "
            "current competitors respond to open-sourcing. Doesn't address the "
            "massive resource cost of maintaining an open-source community. "
            "Doesn't discuss that open-sourcing is essentially irreversible — "
            "you can't put the genie back in the bottle."
        ),
    },
]


# ── runner (identical to test_lane4.py) ─────────────────────────────────

def run_scenario(idx, scenario, boundary, routing, verbose=False):
    name = scenario["name"]
    question = scenario["question"]
    answer = scenario["vanilla_answer"]
    expected_gaps = scenario["expected_gaps"]

    print(f"\n{'='*70}")
    print(f"SCENARIO {idx+1}: {name}")
    print(f"{'='*70}")
    print(f"Expected gaps: {sorted(expected_gaps) if expected_gaps else '(none — control)'}")
    print(f"Answer length:  {len(answer)} chars")
    print()

    t0 = time.time()
    card = run_structural_coverage_from_ir(
        boundary=boundary,
        ir=construct_conversation_ir(_make_context(question, answer)),
        structural_coverage_routing=routing, anti_echo_model_ids=set(),
    )
    elapsed = time.time() - t0

    if card is None:
        print("  !! Lane 4 returned None (hard failure)")
        return {"name": name, "status": "FAIL"}

    actual_gaps = {d.dimension_id for d in card.dimensions if not d.covered}
    actual_covered = {d.dimension_id for d in card.dimensions if d.covered}
    detected = {d.dimension_id for d in card.dimensions}

    true_positives = expected_gaps & actual_gaps
    false_negatives = expected_gaps & actual_covered
    missed_entirely = expected_gaps - detected
    false_positives = actual_gaps - expected_gaps

    print(f"  Question type: {card.question_type}")
    print(f"  Dimensions detected: {len(card.dimensions)}")
    print(f"  Gaps found: {len(actual_gaps)}  |  Covered: {len(actual_covered)}")
    print(f"  Gap questions: {len(card.gap_questions)}")
    print(f"  Time: {elapsed:.1f}s")
    print()

    if verbose:
        for d in card.dimensions:
            status = "COVERED" if d.covered else "GAP"
            marker = ""
            if d.dimension_id in expected_gaps:
                if d.covered:
                    marker = " ← FALSE NEGATIVE (should be gap)"
                else:
                    marker = " ← CORRECT"
            elif not d.covered:
                marker = " ← FALSE POSITIVE (unexpected gap)"
            print(f"  [{status}] {d.dimension_name} ({d.dimension_id}){marker}")
            print(f"         Evidence: {d.coverage_evidence[:120]}...")
            print()

    print(f"  SCORECARD:")
    print(f"    True positives (correct gaps):    {sorted(true_positives)}")
    print(f"    False negatives (missed gaps):     {sorted(false_negatives)}")
    print(f"    Missed entirely (not detected):    {sorted(missed_entirely)}")
    print(f"    False positives (unexpected gaps): {sorted(false_positives)}")

    if not expected_gaps:
        fp_count = len(actual_gaps)
        grade = "PERFECT" if fp_count == 0 else "GOOD" if fp_count <= 1 else "NOISY"
        print(f"    Grade: {grade} (control — {fp_count} false gaps)")
    else:
        tp_rate = len(true_positives) / len(expected_gaps) if expected_gaps else 0
        if tp_rate >= 0.8 and len(false_positives) <= 1:
            grade = "EXCELLENT"
        elif tp_rate >= 0.6:
            grade = "GOOD"
        elif tp_rate >= 0.4:
            grade = "PARTIAL"
        else:
            grade = "POOR"
        print(f"    Grade: {grade} (recall={tp_rate:.0%}, FP={len(false_positives)})")

    # Show gap questions if verbose
    if verbose and card.gap_questions:
        print(f"\n  GAP QUESTIONS:")
        for gq in card.gap_questions:
            print(f"    [{gq.dimension_name}]")
            for q in gq.questions:
                print(f"      - {q}")
            print()

    return {
        "name": name, "grade": grade,
        "question_type": card.question_type,
        "detected": len(card.dimensions),
        "true_positives": sorted(true_positives),
        "false_negatives": sorted(false_negatives),
        "missed_entirely": sorted(missed_entirely),
        "false_positives": sorted(false_positives),
        "elapsed": round(elapsed, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Lane 4 round 2 test")
    parser.add_argument("--scenario", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.list:
        for i, s in enumerate(SCENARIOS):
            print(f"  {i+1}. {s['name']}")
            print(f"     Expected: {sorted(s['expected_gaps']) if s['expected_gaps'] else '(control)'}")
        return

    routing = _load_structural_routing()
    boundary = _make_boundary()

    scenarios_to_run = (
        [(args.scenario - 1, SCENARIOS[args.scenario - 1])]
        if args.scenario else list(enumerate(SCENARIOS))
    )

    results = []
    for idx, scenario in scenarios_to_run:
        results.append(run_scenario(idx, scenario, boundary, routing, verbose=args.verbose))

    if len(results) > 1:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        for r in results:
            fn = r.get("false_negatives", [])
            fp = r.get("false_positives", [])
            print(f"  {r.get('grade','?'):10s}  {r['name']}")
            if fn: print(f"             Missed: {fn}")
            if fp: print(f"             Unexpected: {fp}")
        print()
        grades = [r.get("grade", "?") for r in results]
        excellent = grades.count("EXCELLENT") + grades.count("PERFECT")
        good = grades.count("GOOD")
        partial = grades.count("PARTIAL")
        poor = grades.count("POOR") + grades.count("NOISY")
        print(f"  Excellent/Perfect: {excellent}  |  Good: {good}  |  Partial: {partial}  |  Poor: {poor}")


if __name__ == "__main__":
    main()
