# V60 Embedding-Assisted Pickup Readout

Date: 2026-05-10
Status: dormant lab evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## The Answer To The Direct Question

No, the earlier C4.3 transaction replay did not use embeddings for v60 pickup.

The broader Lolla system already has an embedding layer documented and
implemented as a low-trust "swiss cheese" recall mechanism. But the C4.3 v60
transaction packet lab used the archived deterministic lane nominations, sorted
by lane order, then capped to 8 candidate cards. It did not semantically search
v60 affordance or absence chunks.

This readout adds two embedding tests:

1. A retrieval-only v60 embedding lab.
2. A paid C4.3 replay using a balanced embedding-assisted packet.

None of this touches live `/lolla`.

## Artifacts

Retrieval-only embedding lab:

- Script: `scripts/run_v60_embedding_retrieval_lab.py`
- Tests: `tests/test_v60_embedding_retrieval_lab.py`
- Output:
  `data/evaluations/v60_transaction_embedding_lab/2026-05-10-v60-embedding-pickup-absence-view/`

Embedding-balanced paid replay:

- Manifest:
  `research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json`
- Output:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-embedding-balanced-4211-paid-edge-all/`

Verification:

```bash
python3 -m py_compile scripts/run_v60_embedding_retrieval_lab.py
python3 -m pytest tests/test_v60_embedding_retrieval_lab.py tests/test_v60_transaction_paid_replay.py -q
```

Result: `37 passed`.

## Test 1: Retrieval-Only V60 Embedding Lab

The lab embedded v60 chunks directly:

- 306 affordance chunks;
- 697 absence chunks;
- 1,003 chunks total.

It embedded each of the same 8 replay cases and compared:

- existing lane-order cap8 packet;
- embedding-only top8 models;
- absence-only top8 models;
- hybrid RRF lane + embedding ranking;
- reserved novelty ranking.

The embedding model was `text-embedding-3-small`.

### Retrieval Results

Aggregate:

- Mean embedding-vs-lane top8 Jaccard: `0.1036`.
- Mean absence-only-vs-lane top8 Jaccard: `0.1075`.
- Suppressed models recovered by embedding top8: `12`.
- Suppressed models recovered by absence-only top8: `9`.
- Models not nominated by lanes but found by embedding top8: `41`.
- Models not nominated by lanes but found by absence-only top8: `43`.
- In the all-chunk ranking, every top8 model's best chunk was an affordance,
  not an absence record.

That last point matters. Absence is present in v60, but if we put affordances
and absences in one semantic pool, richer affordance text tends to win. Absence
needs an explicit lane, reserved slot, or separate score, otherwise it becomes
nominally available but practically muted.

### What Embeddings Found That The Lane Cap Missed

Some embedding picks look productively different:

- `startup_pivot`: `optionality`, `premortem`, `prioritization`,
  `lean-startup-methodology`, `trade-offs`.
- `friendship_money`: `reciprocity-principle`, `empathy`,
  `non-violent-communication`, `trade-offs`.
- `whistleblower`: `critical-thinking`, `moral-hazard`,
  `psychological-safety`, `risk-assessment`, `regulatory-horizon-scanning`.
- `phd_research`: `optionality`, `divergent-vs-convergent-thinking`,
  `true-uncertainty-navigation`, and, through the hybrid RRF rank,
  `survivorship-bias` and `brainstorming`.

Those are not obviously better in every case, but they are not random. They
often correspond to dimensions we already suspected were underrepresented by
the lane-order cap.

### What Looks Fishy In Retrieval

Embedding-only retrieval also pulled broad reusable models:

- `step-back`;
- `opportunity-cost`;
- `sunk-cost-fallacy`;
- `optimization-theory`;
- `trade-offs`;
- `first-principles-thinking`;
- `calculated-risk-taking`.

Those can be useful, but they are also easy to overuse. Embedding similarity is
good at "this sounds adjacent"; it is not good at deciding whether the chunk
adds marginal reasoning value beyond the current answer.

The retrieval query also included the vanilla answer. That makes the test
realistic for "reconsider this output," but it also risks retrieving material
that mirrors the answer's existing frame. We need future tests with multiple
query views:

- user conversation only;
- vanilla answer only;
- query + conversation + vanilla;
- explicit "find missing edge / evidence gate" query.

## Test 2: C4.3 Paid Replay With Embedding-Balanced Packets

The second test used a generated manifest with explicit lab nominations. The
policy was:

> 4 lane-proven cards + 2 embedding-novel affordance cards + 1 absence-only
> novel card + 1 hybrid/RRF novel card.

This tests embeddings as an additive recall layer, not as a replacement for
deterministic lanes.

### Paid Replay Aggregate

Path:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-embedding-balanced-4211-paid-edge-all/`

Results:

- Items: 8
- Paid calls: 23
- Reported cost: `$0.273664`
- Total tokens: `253,892`
- Judge winners: `B: 6`, `C: 1`
- One judge timeout: `real-estate`
- Ledger validation: 3 valid, 1 valid after summary repair, 4 invalid
- Consideration validation: 4 valid, 4 invalid
- Valid consideration usefulness: 3 useful, 1 mixed

Compared with lane-only C4.3:

- Lane-only public judge: `B: 8`, `C: 0`.
- Embedding-balanced public judge: `B: 6`, `C: 1`, 1 judge timeout.
- Lane-only consideration validation: 2 valid, 6 invalid.
- Embedding-balanced consideration validation: 4 valid, 4 invalid.
- Lane-only ledger validation: 2 valid, 6 invalid.
- Embedding-balanced ledger validation: 3 valid, 1 valid-after-repair, 4 invalid.

This is a real improvement in lab behavior, but not product readiness.

Raw private usefulness was almost identical across the two C4.3 runs:

- lane-only: 6 useful, 1 mixed, 1 not useful;
- embedding-balanced: 6 useful, 1 mixed, 1 not useful.

The behavioral difference was route shape:

- lane-only had 0 `public_answer_delta` routes;
- embedding-balanced had 4 `public_answer_delta` routes;
- embedding-balanced also had more duplicate/reject outcomes and fewer high
  usefulness assessments.

So embeddings made the model more willing to create public deltas, but not
reliably better public deltas.

## Case-Level Read

### `startup_pivot`: Best Evidence For Embeddings

Embedding-balanced packet:

- lane-proven: `base-rates`, `statistics-concepts`,
  `scientific-method-evidence-testing`, `boundaries`;
- embedding-added: `optionality`, `premortem`,
  `lean-startup-methodology`, `decision-trees`.

Arm C won.

Why it won:

- It preserved the falsifiable pre-buy test.
- It added a base-rate caution on the thin 3/22 signal.
- It surfaced a hybrid third option rather than treating the choice as binary.
- It avoided Arm B's ungrounded quantitative anchors.

This is the cleanest evidence that embedding-assisted v60 pickup can add
useful cognitive material.

### `friendship_money`: Useful Private Guardrails, No Public Win

Embedding added:

- `trade-offs`;
- `reciprocity-principle`;
- `prospect-theory`;
- `empathy`.

The private report was valid and marked the packet useful. `empathy` was
especially valuable as a guardrail against business-frame overfit. But Arm C
still produced no public delta, and Arm B won by adding concrete affordability
and resource-verification checks.

This is not a pure failure. It is evidence that embeddings can improve private
consideration without creating user-visible value. That distinction matters.

### `whistleblower`: Better Candidate Mix, Still Bad Translation

Embedding added:

- `critical-thinking`;
- `incentives`;
- `moral-hazard`;
- stronger incentive/evidence framing.

The private reasoning looked better than the lane-only packet: the model used
critical thinking as an evidence guardrail and compressed the principal-agent
problem well. But the public output still leaked mechanism language and lost to
Arm B, which produced the more concrete "documentation and attorney intake"
delta.

The lesson is not "embeddings bad"; it is "better recall still needs a
public-safe composer."

### `multi_offer`: Embedding Added Deltas, But Not The Right Edge

Embedding added:

- `opportunity-cost`;
- `calculated-risk-taking`;
- `risk-assessment`;
- `optionality`.

The ledger validated, and the model created two public-answer-delta routes.
But it still missed the dropped leadership-review thread that Arm B surfaced.

This is important: v60 can add reasoning pressure, but it is not a substitute
for raw conversation edge retrieval. The best edge came from a specific
conversation thread, not from the mental-model substrate.

### `real_estate`: Useful Private Caution, Judge Timeout

Embedding added:

- `first-principles-thinking`;
- `sunk-cost-fallacy`;
- `opportunity-cost`;
- `optionality`.

The consideration report was valid and useful. The judge timed out, so no
public comparison is available. Qualitatively, Arm C still mostly restated the
baseline, while Arm B produced concrete debt-buffer questions. The embedding
packet did not obviously solve the domain-specific financing edge.

### `messy_three_problems`: Correct Mixed/No-Delta Behavior

Embedding added:

- `step-back`;
- `opportunity-cost`;
- `decision-trees`;
- `optionality`.

The ledger and consideration report were valid. The packet was marked `mixed`.
All cards were rejected or privately noted, with no public delta. Arm B still
won by using raw case details: boyfriend withdrawal, mother-care math, and DC
preference.

This suggests the model can reject embedding additions when they do not add
enough beyond the baseline.

### `user_has_plan`: Still A No-Op Control

Embedding added:

- `opportunity-cost`;
- `optimization-theory`;
- `comparative-advantage`;
- `prioritization`.

The ledger was valid and all cards were rejected. That is good: the system did
not blindly overfeed the case. The consideration report was invalid only
because public output leaked private scaffold language.

Arm B still won by finding employment/IP/moonlighting risk outside the selected
v60 material.

### `phd_research`: Promising Retrieval, Poor Decoder Use

Embedding-balanced packet included:

- `optionality`;
- `divergent-vs-convergent-thinking`;
- `iteration`;
- `survivorship-bias`.

This is close to the candidate mix we wanted. But Arm C still rubber-stamped
the baseline and leaked mechanism language. Arm B won by adding the public-data
trial and stronger evidence gates.

This case shows that candidate pickup can improve without the decoder using the
pickup well.

## What We Learned

### 1. Embeddings Are Not Redundant

The overlap with lane cap8 was low. Embeddings pull materially different v60
models. This supports using embeddings as an additive recall layer.

### 2. Embeddings Are Not Trustworthy Enough To Rank Alone

Embedding-only top8 had many broad reusable models. Some are useful, some are
generic. Without caps, family diversity, absence slots, and LLM/reviewer
consideration, embedding pickup would create mental-model theater.

### 3. Absence Needs Its Own Retrieval Path

All-chunk retrieval buried absence records. Absence-only retrieval found
interesting blockers, but those would not surface without an explicit view. In
v60, absence cannot be a footer; it needs a first-class packet role.

### 4. Model-Level Packets Lose The Embedding Hit

The embedding lab retrieves specific chunks:

- specific `affordance_id`;
- specific absence `attempted_field`.

But the current packet builder accepts only `model_id` nominations, then emits
the first few affordance cards for that model. That means an embedding hit can
select `lean-startup-methodology.validated-learning-kill-pivot-gate`, but the
packet architecture does not yet guarantee that exact affordance is the one
shown.

This is a critical architecture gap. If we use embeddings, nominations should
be affordance-level and absence-level, not only model-level.

### 5. Public Generation Is Still The Wrong Place To Trust This

Even with better pickup:

- public mechanism leaks remained;
- ledgers still had enum drift;
- judge B still won most cases;
- the strongest edges often came from raw conversation detail, not v60.

The right next architecture is still private consideration trace plus
deterministic validation/composition, not direct v60-to-user prose.

## Recommended Next Step

Do not merge embeddings into product pickup yet.

Do build C4.4 as an affordance/absence-level embedding packet lab:

1. Precompute and version v60 chunk embeddings.
2. Let embedding retrieval nominate `affordance_id` and absence
   `attempted_field`, not only `model_id`.
3. Build packets that preserve the exact selected chunks.
4. Use a balanced cap, not embedding-only:
   - 4 lane-proven cards;
   - 2 embedding-novel affordance chunks;
   - 1 absence blocker chunk;
   - 1 lane4 or hybrid diversity card.
5. Run the decoder in private-trace mode only.
6. Build the ledger deterministically from the trace.
7. Compose any public delta deterministically and conservatively.
8. Evaluate separately:
   - retrieval quality;
   - private usefulness;
   - correct rejection;
   - correct deferral;
   - public leak rate;
   - public answer improvement.

## Bottom Line

Embeddings helped. They recovered different and sometimes better candidate
lenses, and the balanced embedding replay produced one real Arm C win where
lane-only had none.

But embeddings also confirmed the danger: semantic similarity is a recall
instrument, not judgment. It can find promising v60 material, but the system
must still force consideration without forcing use.

The right product doctrine is:

> deterministic lanes provide provenance; embeddings widen recall; v60 provides
> source-backed affordances and absence blockers; the reasoning model considers
> them privately; deterministic validators and composers decide what can safely
> leave the private layer.
