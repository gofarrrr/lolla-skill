# Case 02 conversation-state microtask probe v1

Status: **closed informative failure**  
Provider calls: 2 of 3 authorized; 0 retries  
Observed estimated cost: **$0.00153075**

## What happened

The smaller-task design helped us see two different failure classes clearly.

The positions call reached Gemini and returned a schema-shaped answer. It
understood the broad conditional pilot direction, but it removed the `span-`
prefix from every source identifier. Deterministic custody therefore rejected
all three proposed candidates. It also repeated the substantive ownership
failure: the source-reviewed joint position was split into a user-owned pilot
and a separately assistant-owned “ready enough” proposal, losing the single
multi-turn trajectory.

The thread call did not reach inference. Google AI Studio rejected its frozen
schema through OpenRouter with HTTP 400 `INVALID_ARGUMENT`. The prospectively
frozen stop rule then prevented the constraints call. No retry, fallback,
response healing, graph call, evaluator, full pipeline, or runtime change was
used.

## What this tells us

Decomposition did not automatically solve conversation understanding. It made
failure attribution better:

- the deterministic ledger correctly prevented invalid source identities from
  becoming accepted observations;
- position semantics still need work on joint multi-turn composition;
- provider compatibility cannot be inferred from local JSON-Schema checks;
- thread and constraint quality remain unknown because they were not observed.

The accepted positions schema is larger than the rejected thread schema and
both have the same measured depth, so generic size or depth is not the leading
explanation. The distinctive thread feature is the nullable string represented
as `type: ["string", "null"]`. Current direct Gemini documentation says this is
supported, so the strongest hypothesis is an interoperability issue in the
OpenRouter-to-Google-AI-Studio path, not proof that the schema is invalid in
Gemini generally.

## Next boundary

Do not retry Case 02 or run the missing constraints call under this contract.
A prospective repair should:

1. keep the current direct-Gemini projection intact;
2. add an OpenRouter-Gemini projection using the already accepted `anyOf`
   nullable representation;
3. constrain `span_id` to the complete source-specific ID set in the provider
   schema, while still validating the selected ID against its exact excerpt;
4. tell the position reader not to split a qualification from the focal plan it
   modifies;
5. transfer-test on Case 05, not the cases that exposed the repair;
6. remain three calls maximum, zero retry, no graph or pipeline.

That would be a new experiment and requires a new authorization.
