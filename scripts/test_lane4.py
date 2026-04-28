#!/usr/bin/env python3
"""Standalone Lane 4 test harness.

Runs structural_coverage directly against crafted scenarios without the full
pipeline. Each scenario has a question, a vanilla answer, and expected gaps
(dimensions that SHOULD be flagged uncovered).

Usage:
    python scripts/test_lane4.py                    # run all scenarios
    python scripts/test_lane4.py --scenario 2       # run one scenario
    python scripts/test_lane4.py --list              # list scenario names
    python scripts/test_lane4.py --verbose           # show full card details
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

# ── path setup ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.system_b.boundary_provider import OpenAICompatibleBoundaryClient
from engine.system_b.conversation_context import ConversationContext, ExtractionPayload, Turn
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.structural_coverage import run_structural_coverage_from_ir

# ── logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s  %(levelname)s  %(message)s",
)

# ── load KG ─────────────────────────────────────────────────────────────
_KG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_graph.json")

def _load_structural_routing() -> dict:
    with open(_KG_PATH) as f:
        kg = json.load(f)
    return kg["structural_coverage_routing"]


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

# ── boundary client ─────────────────────────────────────────────────────
def _make_boundary() -> OpenAICompatibleBoundaryClient:
    """Use the same provider/model the real pipeline uses: OpenRouter + grok-4.1-fast."""
    client = OpenAICompatibleBoundaryClient.openrouter_from_env()
    if not client.api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    print(f"Using: {client.provider_name} / {client.model}")
    return client

# ── test scenarios ──────────────────────────────────────────────────────
# Each scenario: (name, question, vanilla_answer, expected_gaps, notes)
# expected_gaps = set of dimension_ids that SHOULD be flagged uncovered
# The answer is intentionally written to cover some dimensions and miss others.

SCENARIOS: list[dict] = [
    # ──────────────────────────────────────────────────────────────────
    # 1. Classic M&A — deliberate gaps in commitment-reversibility,
    #    stakeholder-alignment, information-quality
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "M&A acquisition — missing reversibility, stakeholders, info quality",
        "question": (
            "We're a 200-person SaaS company ($28M ARR). Our biggest mid-market "
            "competitor (40-person startup, $4M ARR) is running out of runway and "
            "their CEO reached out about acquisition at $12M (3x revenue). "
            "We have $18M cash. Should we do this deal?"
        ),
        "vanilla_answer": (
            "Yes, acquire them. At $12M you're paying 3x revenue for a distressed "
            "company — negotiate down to $8-9M given their weak position. You'd "
            "absorb $4M ARR (net ~$3.2M after overlap), remove your primary "
            "competitor, and push past $30M ARR. Their 40-person team includes "
            "engineers with features you want. Plan for 60-70% team retention. "
            "Keep both products running 12-18 months, then migrate their customers "
            "to your platform. The $800K on-prem accounts may churn since you "
            "don't offer that capability, so price accordingly. Structure as "
            "$7M upfront + $1.5M earnout tied to customer retention."
        ),
        "expected_gaps": {
            "commitment-reversibility",
            "stakeholder-alignment",
            "information-quality",
        },
        "notes": (
            "The answer proposes a deal but never asks: What if we want out? "
            "Who needs to approve this internally? How reliable is their reported ARR?"
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 2. Pricing overhaul — deliberate gaps in feedback-system-dynamics,
    #    incentive-alignment, uncertainty-type
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Pricing overhaul — missing feedback loops, incentives, uncertainty",
        "question": (
            "Our B2B SaaS product is priced at $99/seat/month. Competitors are "
            "moving to usage-based pricing. Our sales team is pushing us to switch. "
            "Should we move to usage-based pricing?"
        ),
        "vanilla_answer": (
            "Consider a hybrid model: keep a base seat fee ($49/seat) and add "
            "usage tiers on top. This protects your revenue floor while capturing "
            "upside from heavy users. The base fee covers your fixed costs, usage "
            "tiers align price with value delivered. Roll it out to new customers "
            "first, then migrate existing ones over 6 months. Grandfather current "
            "contracts until renewal. The competitive pressure is real — if you "
            "don't offer usage-based options, you'll lose deals to companies that "
            "do. Your sales team is right that the market is shifting."
        ),
        "expected_gaps": {
            "feedback-system-dynamics",
            "incentive-alignment",
            "uncertainty-type",
        },
        "notes": (
            "Answer proposes mechanics but never explores: How does pricing change "
            "feed back into customer behavior? How are sales team incentives affected? "
            "What kind of uncertainty are we facing — is this a measurable risk or "
            "genuine ambiguity about market direction?"
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 3. Org restructure — deliberate gaps in timing-sequencing,
    #    scope-boundary, behavioral-intervention
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Org restructure — missing timing, scope, behavioral levers",
        "question": (
            "Our engineering org has grown from 30 to 120 people in 18 months. "
            "Velocity has dropped, cross-team dependencies are causing delays, "
            "and the architecture is becoming a bottleneck. We're thinking of "
            "reorganizing from functional teams to product-aligned squads. "
            "How should we approach this?"
        ),
        "vanilla_answer": (
            "Reorganize into product-aligned squads of 6-8 engineers, each owning "
            "a specific product area end-to-end. Each squad gets a product manager, "
            "a tech lead, and full-stack ownership. Create a platform team for shared "
            "infrastructure. Move from a shared monolith to domain-bounded services "
            "that squads own independently. Establish architecture review boards "
            "for cross-cutting decisions. Staff the squads by letting engineers "
            "express preferences, then balance for skill distribution. Allocate "
            "20% of each squad's capacity to tech debt reduction."
        ),
        "expected_gaps": {
            "timing-sequencing",
            "scope-boundary",
            "behavioral-intervention",
        },
        "notes": (
            "Answer gives the target state but not: In what order do you do this? "
            "What's inside vs outside the reorg (does it touch hiring, perf reviews, "
            "on-call)? What behavioral incentives change — will people game the new "
            "structure?"
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 4. Revenue decline diagnosis — deliberate gaps in
    #    causal-diagnosis, information-quality, scaling-dynamics
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Revenue decline — missing causal depth, info quality, scaling",
        "question": (
            "Our SaaS revenue growth has slowed from 80% YoY to 25% YoY over "
            "two quarters. Sales pipeline is actually up 15%. Our average deal "
            "size dropped from $45K to $32K. What's going on?"
        ),
        "vanilla_answer": (
            "The pipeline-revenue disconnect suggests a conversion or deal quality "
            "problem, not a demand problem. The shrinking deal size points to "
            "either moving downmarket or discounting to close. Check if your sales "
            "team is pulling in smaller accounts to hit pipeline targets. Look at "
            "win rates by deal size — if large deals are stalling while small ones "
            "close, your product may have hit a feature ceiling for enterprise. "
            "Also check if competitor pressure is forcing discounts. The 15% "
            "pipeline growth masks the quality decline because pipeline volume "
            "doesn't equal pipeline value."
        ),
        "expected_gaps": {
            "causal-diagnosis",
            "information-quality",
            "scaling-dynamics",
        },
        "notes": (
            "Answer suggests correlations but doesn't distinguish root cause from "
            "symptoms. Doesn't question whether the data is reliable (is pipeline "
            "inflated? are deal sizes measured consistently?). Doesn't consider "
            "whether this is a natural scaling ceiling."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 5. Market expansion — deliberate gaps in competitive-dynamics,
    #    resource-allocation, existing-vs-new
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "Market expansion — missing competitive dynamics, resources, base erosion",
        "question": (
            "We dominate the US market for our vertical SaaS product (65% share). "
            "The European market is underserved with no clear leader. Should we "
            "expand into Europe?"
        ),
        "vanilla_answer": (
            "Yes, expand. The European market is greenfield for your category and "
            "you have the product maturity to win. Start with UK and Germany — "
            "they have the largest TAM and English/English-adjacent business culture. "
            "Hire a GM for EMEA and a small go-to-market team (5-7 people). "
            "Adapt the product for GDPR compliance and local payment methods. "
            "Expect 18-24 months to reach product-market fit in each geography. "
            "Budget $3-4M for the first year including hiring, localization, and "
            "marketing. Use your US customer logos as social proof — many European "
            "companies follow US tech trends."
        ),
        "expected_gaps": {
            "competitive-dynamics",
            "resource-allocation",
            "existing-vs-new",
        },
        "notes": (
            "Answer says 'greenfield' but never analyzes who else might enter "
            "(or is already there locally). Doesn't address opportunity cost — "
            "what happens to the US base while leadership focuses on Europe? "
            "Doesn't weigh protecting 65% share vs chasing new geography."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 6. CONTROL: Well-covered answer — expect FEW or NO gaps
    #    This validates we don't over-flag
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "CONTROL — thorough answer, expect minimal gaps",
        "question": (
            "We're a 50-person startup considering whether to accept a $15M "
            "Series B from a strategic investor (a large enterprise in our space) "
            "vs. a $12M offer from a traditional VC firm. Which should we take?"
        ),
        "vanilla_answer": (
            "This is fundamentally a lock-in vs optionality decision. The strategic "
            "investor's $15M comes with strings: they'll want board seats, right of "
            "first refusal on acquisition, and integration into their ecosystem. "
            "That's $3M more cash but you're trading future exit flexibility. If "
            "the relationship sours, you can't easily unwind their influence.\n\n"
            "The VC's $12M preserves your independence. You keep full control of "
            "M&A decisions, product direction, and future fundraising. The trade-off "
            "is less capital and no built-in distribution channel.\n\n"
            "Who decides matters here: your co-founder and CTO has veto power on "
            "strategic direction, and your lead investor from Series A has pro-rata "
            "rights they'll exercise either way. Both need to agree. The strategic "
            "investor's enterprise sales team would unlock accounts you can't reach "
            "alone, but that dependency creates principal-agent risk — their "
            "incentives (lock you into their platform) diverge from yours (stay "
            "acquirable by anyone).\n\n"
            "The uncertainty here is genuine ambiguity, not measurable risk. You "
            "can't model the probability that the strategic investor's priorities "
            "shift in 2 years. What you CAN do is structure protective terms: "
            "sunset clauses on the ROFR, independent board majority, data "
            "portability guarantees.\n\n"
            "On evidence quality: the strategic investor's customer pipeline "
            "projections ($8M in year 2) are based on their internal forecasts "
            "which you can't verify independently. Discount them 50% and see if "
            "the deal still works at $4M incremental revenue.\n\n"
            "My recommendation: take the VC money unless the strategic investor "
            "agrees to remove the ROFR and accept a minority board seat. The "
            "optionality premium is worth $3M."
        ),
        "expected_gaps": set(),  # should be mostly covered
        "notes": (
            "This answer deliberately engages with commitment-reversibility "
            "(lock-in/optionality), stakeholder-alignment (who approves), "
            "incentive-alignment (principal-agent), uncertainty-type "
            "(ambiguity vs risk), information-quality (evidence scrutiny). "
            "Expect few or no gaps."
        ),
    },
    # ──────────────────────────────────────────────────────────────────
    # 7. All surface, no depth — many mentions but no structural
    #    engagement. Should flag MANY gaps despite long answer.
    # ──────────────────────────────────────────────────────────────────
    {
        "name": "SURFACE — buzzword-heavy answer, expect many gaps despite length",
        "question": (
            "Our 300-person company is evaluating whether to build our own ML "
            "infrastructure or buy a platform license from a major cloud provider. "
            "The build option costs $2M/year in engineering; the buy option is "
            "$800K/year but locks us into their ecosystem. What should we do?"
        ),
        "vanilla_answer": (
            "This is a classic build vs buy decision. You need to consider the "
            "total cost of ownership, including hidden costs of both options. "
            "Building gives you more control and customization. Buying saves time "
            "and lets you focus on your core product. The cloud provider's platform "
            "is mature and well-supported. Your engineering team would need 6-12 "
            "months to build something comparable. Consider the opportunity cost "
            "of those engineers not working on product features. There are also "
            "scaling considerations as your ML workloads grow. The vendor lock-in "
            "risk is real but manageable with good abstraction layers. Stakeholders "
            "across engineering, product, and finance should weigh in. Think about "
            "the timing — is now the right moment to invest in infrastructure? "
            "You should also evaluate the competitive implications and make sure "
            "your data governance meets compliance requirements. Consider starting "
            "with the buy option and migrating later if needed. The reversibility "
            "of this decision matters — can you switch vendors if the relationship "
            "doesn't work out? Overall, I'd lean toward buying given the cost "
            "difference, but do your due diligence on the contract terms."
        ),
        "expected_gaps": {
            "commitment-reversibility",
            "stakeholder-alignment",
            "resource-allocation",
            "scaling-dynamics",
            "competitive-dynamics",
            "uncertainty-type",
        },
        "notes": (
            "This answer MENTIONS reversibility, stakeholders, scaling, competition, "
            "etc. but never engages with the structural tension of any dimension. "
            "Every dimension is name-dropped but none is analyzed. This is the "
            "calibration stress test — can the prompt distinguish mention from engagement?"
        ),
    },
]


# ── runner ──────────────────────────────────────────────────────────────

def run_scenario(
    idx: int,
    scenario: dict,
    boundary: OpenAIBoundaryClient,
    routing: dict,
    verbose: bool = False,
) -> dict:
    """Run one scenario and return results dict."""
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
        structural_coverage_routing=routing,
        anti_echo_model_ids=set(),  # no anti-echo in isolation test
    )
    elapsed = time.time() - t0

    if card is None:
        print("  !! Lane 4 returned None (hard failure)")
        return {"name": name, "status": "FAIL", "reason": "returned None"}

    # Classify results
    present_dims = [d for d in card.dimensions if getattr(d, "present", True)]
    actual_gaps = {d.dimension_id for d in present_dims if not d.covered}
    actual_covered = {d.dimension_id for d in present_dims if d.covered}
    detected = {d.dimension_id for d in present_dims}

    # Expected gaps that were correctly flagged
    true_positives = expected_gaps & actual_gaps
    # Expected gaps that were wrongly marked covered
    false_negatives = expected_gaps & actual_covered
    # Expected gaps that weren't even detected
    missed_entirely = expected_gaps - detected
    # Dimensions marked as gaps that we expected to be covered (or control)
    false_positives = actual_gaps - expected_gaps

    print(f"  Question type: {card.question_type}")
    print(f"  Dimensions present: {len(present_dims)} (of {len(card.dimensions)} catalog)")
    print(f"  Gaps found: {len(actual_gaps)}  |  Covered: {len(actual_covered)}")
    print(f"  Gap questions: {len(card.gap_questions)}")
    print(f"  Time: {elapsed:.1f}s")
    print()

    # Detailed dimension breakdown
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

    # Scorecard
    print(f"  SCORECARD:")
    print(f"    True positives (correct gaps):    {sorted(true_positives)}")
    print(f"    False negatives (missed gaps):     {sorted(false_negatives)}")
    print(f"    Missed entirely (not detected):    {sorted(missed_entirely)}")
    print(f"    False positives (unexpected gaps): {sorted(false_positives)}")

    # Grade
    if not expected_gaps:
        # Control scenario: success = few or no gaps
        fp_count = len(actual_gaps)
        if fp_count == 0:
            grade = "PERFECT"
        elif fp_count <= 1:
            grade = "GOOD"
        else:
            grade = "NOISY"
        print(f"    Grade: {grade} (control — {fp_count} false gaps)")
    else:
        tp_rate = len(true_positives) / len(expected_gaps) if expected_gaps else 0
        if tp_rate >= 0.8 and not false_positives:
            grade = "EXCELLENT"
        elif tp_rate >= 0.6:
            grade = "GOOD"
        elif tp_rate >= 0.4:
            grade = "PARTIAL"
        else:
            grade = "POOR"
        print(f"    Grade: {grade} (recall={tp_rate:.0%}, FP={len(false_positives)})")

    return {
        "name": name,
        "grade": grade,
        "question_type": card.question_type,
        "detected": len(present_dims),
        "true_positives": sorted(true_positives),
        "false_negatives": sorted(false_negatives),
        "missed_entirely": sorted(missed_entirely),
        "false_positives": sorted(false_positives),
        "elapsed": round(elapsed, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Lane 4 standalone test harness")
    parser.add_argument("--scenario", type=int, help="Run only scenario N (1-based)")
    parser.add_argument("--list", action="store_true", help="List scenario names")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full dimension details")
    args = parser.parse_args()

    if args.list:
        for i, s in enumerate(SCENARIOS):
            print(f"  {i+1}. {s['name']}")
            print(f"     Expected gaps: {sorted(s['expected_gaps']) if s['expected_gaps'] else '(control)'}")
        return

    routing = _load_structural_routing()
    boundary = _make_boundary()

    if args.scenario:
        idx = args.scenario - 1
        if idx < 0 or idx >= len(SCENARIOS):
            print(f"ERROR: scenario must be 1-{len(SCENARIOS)}", file=sys.stderr)
            sys.exit(1)
        scenarios_to_run = [(idx, SCENARIOS[idx])]
    else:
        scenarios_to_run = list(enumerate(SCENARIOS))

    results = []
    for idx, scenario in scenarios_to_run:
        result = run_scenario(idx, scenario, boundary, routing, verbose=args.verbose)
        results.append(result)

    # Summary
    if len(results) > 1:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        for r in results:
            fn = r.get("false_negatives", [])
            fp = r.get("false_positives", [])
            print(f"  {r['grade']:10s}  {r['name']}")
            if fn:
                print(f"             Missed: {fn}")
            if fp:
                print(f"             Unexpected: {fp}")
        print()
        grades = [r.get("grade", "?") for r in results]
        excellent = grades.count("EXCELLENT") + grades.count("PERFECT")
        good = grades.count("GOOD")
        partial = grades.count("PARTIAL")
        poor = grades.count("POOR") + grades.count("NOISY")
        print(f"  Excellent/Perfect: {excellent}  |  Good: {good}  |  Partial: {partial}  |  Poor: {poor}")


if __name__ == "__main__":
    main()
