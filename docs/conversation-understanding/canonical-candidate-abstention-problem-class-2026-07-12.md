# Canonical candidate selection and blanket abstention — problem-class review

Date: 2026-07-12  
Trigger: two materially different selector contracts returned empty selections across every source, provider, and ablation arm

## Exact local signature

The first experiment compared all 222 compact canonical cards with graph-recalled menus of five to eight cards. All six calls abstained. The transfer experiment replaced those cards with challenge-oriented failure signals and pressure questions and attached fact-free `recalled_by_mechanism_ids`. All three calls still abstained.

The second experiment was operationally clean and inexpensive (`$0.00053781`). Source-first and ablation arms returned `all_not_applicable`; the provider arm returned `insufficient_evidence`. The protected `premortem` pressure was never selected.

## Current research mapping

Recent abstention research treats abstention as a distinct selective-classification decision with its own trade-off, not as a neutral extra label. Madhusudhan et al.'s black-box Abstain-QA evaluation separates answerable from unanswerable cases and reports that prompting strategy materially changes abstention behavior. This supports measuring false abstention explicitly instead of interpreting empty output as ordinary stability: https://aclanthology.org/2025.coling-main.627/

Wen et al.'s TACL survey frames abstention through the query, model, and human-value dimensions, reinforcing that the local result can arise from task framing and evidence availability rather than model confidence alone: https://aclanthology.org/2025.tacl-1.26/

Fu et al. show that distractor options impose cognitive load in multiple-choice reasoning and that explicit elimination can improve selection. This is directly analogous to the 222-card arm and directionally relevant even to the eight-card shortlist: https://aclanthology.org/2025.acl-long.1051/

Ma et al. study candidate selection across both small pools and pools exceeding 10,000 options and find that candidate-probability estimation requires task-specific evaluation. Their decoding-free methods require logits, which OpenRouter's black-box chat route does not expose reliably enough for this experiment, but the work confirms that ordinary autoregressive generation is not a neutral candidate selector: https://aclanthology.org/2025.acl-long.1589/

The 2026 dynamic-abstention framework models abstention as an explicit action whose reward controls the compute/information trade-off. Lolla does not control that trained reward, so adding a permissive global abstention option can dominate a conservative small model's output: https://arxiv.org/abs/2604.18419

## Local contract diagnosis

The graph-provenance repair was incomplete. An ID such as `missing_reversal_condition` is canonical but not an operational explanation. The selector did not receive the mechanism definition, requirements, exclusions, or near-neighbor distinction that made the upstream ontology interpreter materially better.

The output contract also makes blanket abstention one cheap envelope decision while positive selection requires evaluating several cards, establishing evidence custody, and risking an error. That asymmetry can produce safe-looking empty outputs. Removing abstention would hide the problem and create forced false positives.

Finally, the `premortem` challenge card describes when premortem itself becomes superficial; it does not explicitly connect a missing reversal condition to the reason premortem is a useful pressure. The source-reviewed target was defensible at the graph-mapping level but not entailed by the selector's supplied card.

## Adopted next design

Do not retry, force a minimum selection, add a judge, or swap providers.

The next provider-free contract should:

1. include the complete operational mechanism card for every `recalled_by` ID, not merely its name;
2. require one small assessment row for every recalled candidate: `applicable`, `ambiguous`, `not_applicable`, or `insufficient_evidence`;
3. retain per-row exact role-record custody for every non-`not_applicable` decision;
4. derive the active selected set mechanically only from model-declared `applicable` rows;
5. preserve the ability for every row to be negative without offering a one-step global shortcut;
6. evaluate false abstention, false activation, invariance, and ablation sensitivity as separate non-scalar gates;
7. use a new transfer case and pre-review whether the supplied mechanism-plus-model card actually entails the protected pressure.

This remains one probabilistic semantic task with deterministic completeness and custody checks. It is not multi-layer deterministic relevance gating.

## Rejected practices

- forcing at least one candidate;
- treating empty output as evidence that no mental model applies;
- majority voting or repeated sampling without a causal contract repair;
- logits-based selection on a route that does not expose stable logits;
- sending all 222 full cards again;
- adding free-text rationales to graph routing.

