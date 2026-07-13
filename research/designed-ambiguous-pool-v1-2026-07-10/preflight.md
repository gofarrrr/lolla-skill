# Designed ambiguous pool v1 preflight

Status: **one generation call authorized after provider-free preflight**  
Date: 2026-07-10

## Source strategy

The founder confirmed that no unused conversations are available and asked us
to design ambiguous, realistic, multi-turn cases. This is a new source strategy,
not a retry or repair of the closed Gemini pool.

We will freeze the ambiguity requirements and five scenario briefs, then use a
different model family to instantiate the dialogue. Candidate ranking is fixed
before generation and withheld from the source model.

## Frozen rank

```text
1. amb1-case02-nonprofit-scale
2. amb1-case05-family-archive
3. amb1-case04-research-tool-release
4. amb1-case01-product-scope
5. amb1-case03-creative-partnership
```

The ranking is ascending SHA-256 of
`lolla-designed-ambiguous-pool-v1:2026-07-10:selection-order + ":" + case_id`.

## Planned source boundary

- one OpenRouter call to a non-Gemini, non-downstream model family;
- strict JSON Schema response;
- five cases, fourteen alternating messages per case;
- no model-supplied canonical IDs;
- one call, zero retry, zero evaluator;
- no selection order, expected answer, mental-model name, graph target, or
  evaluation rubric passed to the generator;
- source-first safety and realism review in frozen order after mechanical pass;
- no Stage A call until a selected conversation is hash-frozen in a separate
  contract.

The runner and call contract are now frozen. Seventeen focused tests and the
dry run passed, all hash locks are current, and the output directory is absent.
`call-authorization.json` authorizes one generation call, zero retry, and zero
evaluator calls. It does not authorize Stage A.

## Call result

The response stream did not complete before the frozen outer wall ceiling and
the process was interrupted. No generated pool was preserved and no retry is
authorized. The runner also exposed a custody gap because it wrote no attempted-
call sidecar before waiting on network I/O. See `generation-failure.json`.

Work continues provider-free by creating founder-directed development fixtures.
They will be useful for system testing but will not be mislabeled as clean
holdouts or causal evidence.
