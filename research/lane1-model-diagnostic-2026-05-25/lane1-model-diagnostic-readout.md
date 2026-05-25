# Lane 1 Model Diagnostic Readout — 2026-05-25

## Purpose

The May 22 Marcus live run produced an empty Delta Card on a case that historically produced Lane 1 findings. This diagnostic asks whether the silence was caused by the new pre-Step-6 wiring, the changed conversation, Pass 2 strictness, or model behavior.

This is a Lane-1-only diagnostic. It runs Pass 1, embedding-trigger promotion, and Pass 2, then stops. It does not test Lane 2/3/4, BI, V60, cached Bevelin/Polya cards, Step 6, or Step 7.

## Reference

Historical founder archived runs under `x-ai/grok-4.1-fast` produced Lane 1 findings:

- `20260429T141920Z`: 5 detected tendencies
- `20260428T064421Z`: 5 detected tendencies
- `20260422T155622Z`: 7 detected tendencies

The May 22 live run served `x-ai/grok-4.3` and produced 0 findings after 4 Pass 2 checks.

## Primary Four-Arm Diagnostic

| Arm | Conversation | Model | Boundary | Pass 1 Nominations | Pass 2 Detected | Boundary Health |
|---|---:|---|---|---:|---:|---|
| A | historical founder | `deepseek/deepseek-v4-flash` | off | 2 | 0 | clean |
| B | May 22 founder | `deepseek/deepseek-v4-flash` | off | 0 | 0 | 4 timeouts |
| C | May 22 founder | `deepseek/deepseek-v4-flash` | step6_private label | 1 | 0 | clean |
| D | May 22 founder | `x-ai/grok-4.3` | step6_private label | 3 | 0 | clean |

Read: this is not a pre-Step-6 wiring regression. Lane 1 is upstream of pre-Step-6 table rendering, and the clean C/D arms still reject all Pass 2 candidates. The deeper finding is model/prompt compatibility: Pass 1 still sees candidate pressure, but Pass 2 rejects everything under DeepSeek Flash and Grok 4.3 on this case shape.

The B arm is incomplete because DeepSeek timed out on 4 boundary calls even with `LOLLA_LLM_TIMEOUT=120`. That timeout instability is itself a product concern for using DeepSeek Flash as the default.

## Candidate Screen

| Arm | Conversation | Model | Pass 1 Nominations | Pass 2 Detected | Cost Estimate | Attribution |
|---|---:|---|---:|---:|---:|---|
| E | historical founder | `qwen/qwen3.5-flash-02-23` | 8 | 5 | partial, $0.001913 | served `qwen/qwen3.5-flash-20260224`, true mismatch under current classifier |
| F | historical founder | `google/gemini-3.1-flash-lite` | 7 | 6 | complete, $0.035938 | served version alias, no true mismatch |
| G | historical founder | `deepseek/deepseek-v4-pro` | 3 | 1 | complete, $0.041326 | served version alias, no true mismatch |
| H | May 22 founder | `google/gemini-3.1-flash-lite` | 4 | 5 | complete, $0.028510 | served version alias, no true mismatch |
| I | May 22 founder | `google/gemini-3.1-flash-lite` | 3 | 5 | complete, $0.024922 | served version alias, no true mismatch |

Read: Gemini Flash Lite is the best default candidate from this screen. It recovers the historical founder signal, recovers the May 22 founder signal, has complete pricing, and OpenRouter serves it as a provider version alias rather than a materially different model.

Qwen is promising on quality and cost, but OpenRouter served `qwen/qwen3.5-flash-20260224` when `qwen/qwen3.5-flash-02-23` was requested. Until the pricing and attribution classifier understand that route, it is not the clean default.

## Decision

Switch the production default from `deepseek/deepseek-v4-flash` to `google/gemini-3.1-flash-lite`.

This is a product-default correction, not a skill-flow redesign. Step 6, Step 7 resting, pre-Step-6 private table behavior, and the five-gate dormant foundation remain unchanged.

## Follow-Up

Run the next live `/lolla` check under Gemini Flash Lite before continuing to process hardening. If Lane 1 now produces findings on Marcus and the cost/attribution summary is complete, proceed to the process hardening PR. If it does not, stop and review Lane 1 Pass 2 prompt compatibility before touching pre-Step-6 or Step 7.
