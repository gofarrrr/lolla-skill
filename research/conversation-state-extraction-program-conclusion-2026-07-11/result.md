# Conversation-state extraction experiment conclusion

## Conclusion

The current design—one full-conversation model call for positions, one for
threads, and one for constraints—**does not meet Lolla's required semantic
reliability**. It should not be integrated into the live skill, graph, or full
pipeline.

This is not a failure of the hybrid idea. The deterministic half worked:
transport became reliable, invalid evidence was quarantined, every proposal
received custody, and nothing leaked into the graph. The failure is narrower:
each probabilistic microtask is still too broad internally.

Across Case 05 and two prospectively frozen transfer cases after the single
allowed generic repair, zero cases passed every family. Constraint recall stayed
near 0.20–0.22 under strict matching, source strength was repeatedly inflated,
thread trajectories were truncated or falsely resolved, and current positions
were fragmented or polluted by adjacent disagreements.

The program stopped after 9 of 12 allowed calls and $0.02172925 of the $0.08
ceiling. No retries, evaluator, graph, pipeline, or runtime calls occurred.

## What should survive

- stable source catalogs and model-facing source IDs;
- typed internal candidates;
- JSON transport plus local typed validation;
- exact deterministic evidence resolution;
- complete candidate ledger and fail-closed quarantine;
- zero direct factual graph routing.

## What must change

The semantic work needs another decomposition, but not brittle deterministic
gating. LLMs should still interpret messy conversation:

1. harvest possible contribution, thread-event, and constraint candidates per
   turn or small window;
2. return span IDs only while deterministic code retrieves exact excerpts;
3. preserve every candidate before fan-in;
4. use fresh-context semantic synthesis over ordered candidates for ownership
   and trajectory;
5. classify source strength in a separate narrow semantic step;
6. evaluate each stage before final handoff composition.

This is a material architecture change. More prompt tuning on the current
one-call-per-family design is not justified by the evidence.

