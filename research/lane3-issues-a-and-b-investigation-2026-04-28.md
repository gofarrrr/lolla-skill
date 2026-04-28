# Lane 3 Issues A & B — Investigation Memo (2026-04-28)

**Purpose.** Two anomalies in Lane 3 (Frame Pressure) surfaced during the verification audit of run `mother-deciding-protect-year/20260428T093545Z`. This memo documents root causes, the evidence behind each claim, and a reproduction recipe so anyone can confirm — or disconfirm — the findings before we change code. The intent is to fix both for good, not patch around them.

**Authoring constraint.** Every claim has either a file/line citation or a reproducible command. If you can't verify a claim from the artifacts, the claim is suspect.

**TL;DR.**

- **Issue A** is a confirmed, mechanical bug in `_parse_frame_extraction_from_packet`. Confidence ≥ 95 %. Fix is mechanical (~5 lines).
- **Issue B** is a real interaction problem between LLM compression behaviour and a strict validator, not a bug in any single component. Confidence in mechanism ≥ 90 %. Fix is a design choice with a tradeoff to weigh.

---

## Issue A — `dropped_frame_elements` is opaque

### Symptom

When Lane 3 drops a frame element that fails validation, the persisted record carries only `element_text` (an LLM-paraphrased description of the element) and `drop_reason`. The original `evidence_quote`, `element_type`, `frame_pattern`, `fragility_signal`, `inquiry_stage`, and `likely_default` fields are **not preserved**. This makes post-hoc investigation of "why did Lane 3 keep dropping things on this case" effectively impossible from the persisted artifact — you have to re-run with stderr capture.

Concrete example from the audited run (`result.json`, `frame_pressure_card.dropped_frame_elements`):

```json
[
  {
    "element_text": "The immediate actions must focus on directly removing or confronting the 19-year-old guy, ...",
    "drop_reason": "evidence_not_in_user_turns"
  },
  {
    "element_text": "Secret surveillance of the daughter's phone is a justified and necessary protective measure that doesn't undermine trust.",
    "drop_reason": "evidence_not_in_user_turns"
  }
]
```

The actual quote that the LLM proposed and the validator rejected is **gone from the JSON**. It only exists in the stderr from that run, which is not captured anywhere persistent.

### Root cause

`engine/system_b/frame_pressure.py:388-409`. The parser computes `evidence` and `pattern` as locals (lines 390-391), inspects them, and on rejection appends a dict that contains only `element_text` and `drop_reason`:

```python
for item in items:
    element_text = coerce_str(item.get("element_text"))
    evidence = coerce_str(item.get("evidence_quote"))
    pattern = coerce_str(item.get("frame_pattern"))

    if not evidence:
        dropped.append({"element_text": element_text, "drop_reason": "missing_evidence"})
        continue
    if not pattern:
        dropped.append({"element_text": element_text, "drop_reason": "missing_pattern"})
        continue
    if not _evidence_in_text(evidence, user_text):
        dropped.append({"element_text": element_text, "drop_reason": "evidence_not_in_user_turns"})
        continue
```

`evidence`, `pattern`, and the other element fields are all available locally. They are simply not put into the dropped record. There is no downstream serialization step that filters them out — `to_payload` at line 101 passes the dropped list through verbatim (`"dropped_frame_elements": list(self.dropped_frame_elements)`).

### Evidence

I verified this by:

1. Reading the exact stored data:
   ```
   python3 -c "import json; d = json.load(open('~/.local/share/lolla/runs/mother-deciding-protect-year/20260428T093545Z/result.json')); \
   print(d['frame_pressure_card']['dropped_frame_elements'])"
   ```
   Confirmed only `element_text` + `drop_reason` are present.

2. Reading every callsite of `dropped_frame_elements` in the codebase (`grep -rn "dropped_frame_elements" engine/system_b/`). The two writers are the parser at frame_pressure.py:395/400/408 and the constructor at line 670; both produce or pass through dicts with only the two fields. No transformation strips fields.

3. Reading `to_payload` and `from_payload` (lines 74-134). The serializer is a verbatim list copy.

### Reproduction recipe

To confirm Issue A in any conversation:

```bash
# Use any past run that has a non-empty dropped_frame_elements
cd ~/.local/share/lolla/runs
for case in */; do
  for run in "$case"*/; do
    file="$run/result.json"
    [ -f "$file" ] || continue
    n=$(python3 -c "import json,sys; print(len(json.load(open('$file'))['frame_pressure_card'].get('dropped_frame_elements', [])))")
    if [ "$n" -gt 0 ]; then
      echo "$run drops=$n"
    fi
  done
done | head -10
```

For any run with drops > 0, inspect:

```bash
python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
for x in d['frame_pressure_card']['dropped_frame_elements']:
    print(json.dumps(x, indent=2))
" /path/to/result.json
```

**Confirms the bug:** every dropped record contains exactly `element_text` and `drop_reason` and nothing else.

**Disconfirms the bug** (i.e., fix is unnecessary): records contain `evidence_quote`, `element_type`, etc. If that happens, my reading of the parser is wrong and I should be told.

### Proposed fix

Preserve every field on the dropped record. The parser already has them in scope:

```python
def _record_drop(item, element_text, evidence, pattern, drop_reason):
    return {
        "element_text": element_text,
        "evidence_quote": evidence,
        "element_type": coerce_str(item.get("element_type")),
        "frame_pattern": pattern,
        "fragility_signal": coerce_str(item.get("fragility_signal", "")),
        "inquiry_stage": coerce_str(item.get("inquiry_stage", "")),
        "likely_default": coerce_str(item.get("likely_default")) or "none",
        "drop_reason": drop_reason,
    }
```

Replace the three `dropped.append({...})` calls with `dropped.append(_record_drop(item, element_text, evidence, pattern, "..."))`. Backward-compatible — existing consumers reading `element_text` and `drop_reason` continue to work; new fields are additive.

### Confidence

**≥ 95 %.** Mechanism is a direct read of the source. The only way I'm wrong is if something downstream rewrites these records before they reach disk, and I read every callsite to confirm nothing does. The 5 % is reserved for "I misread the code" — which is why the reproduction recipe exists.

---

## Issue B — Real user-turn quotes were rejected by the validator

### Symptom

In the audited run, two Lane 3 elements were dropped with `drop_reason="evidence_not_in_user_turns"`. Stderr captured the actual rejected quotes:

```
Frame element evidence_quote not found in user turns, skipping:
  'But what about the guy? Do I call the police? Do I confront him somehow? ... And'
Frame element evidence_quote not found in user turns, skipping:
  "I've been going through her phone for months. She doesn't know this..."
```

The text on either side of the `...` markers is verbatim from the transcript (Turn 3 USER, line 22 and Turn 5 USER, line 50). The literal `...` characters are the LLM's compression markers, not user-typed ellipsis — and they are not in the transcript. The strict validator correctly rejected the quote-with-ellipsis; the result is that two real frame elements were lost.

### Root cause

The interaction of two facts:

1. **The LLM occasionally inserts `...` into `evidence_quote`** to compress a long passage. Confirmed by re-running the same Lane 3 prompt with a fresh `x-grok-conv-id` and observing the LLM produce ellipsis-free quotes that pass validation. This is non-deterministic LLM behaviour, not a deterministic bug.

2. **The validator (`_evidence_in_text`, frame_pressure.py:167-199) has four tolerance tiers but none for ellipsis.** The tiers are: exact substring, JSON-quote-normalized, wrapping-stripped, case-insensitive. A quote containing `...` that doesn't appear literally in user_text fails all four tiers and is rejected. This is the design intent — "literal substring of a user turn, character-for-character" is the contract — but the design contract doesn't account for LLM compression.

The prompt itself (frame_pressure.py:206-243) is explicit:

> Every evidence_quote MUST be a LITERAL SUBSTRING of a user turn from the SOURCE section. Character-for-character match. If a frame element is real but no user-turn substring supports it directly, you MUST OMIT the element — do not paraphrase, do not quote from CONTEXT, do not fabricate.

The LLM violates this on two fronts: (a) by inserting `...`, it produces a string that is not literally in the source; (b) by *also* including the surrounding text verbatim, it signals the violation is compression, not paraphrase. The prompt does not give the LLM an "I want to compress" affordance, so it improvises with ellipsis.

### Evidence

Three independent confirmations:

1. **Stderr text from the original run.** Both rejected quotes contain `...` markers. The text on either side matches the transcript exactly (verified by `grep` against `conversation.txt`).

2. **Transcript verification.** Lines 22 and 50 of `~/.local/share/lolla/runs/mother-deciding-protect-year/20260428T093545Z/conversation.txt` contain:
   - Line 22: `... But what about the guy? Do I call the police? Do I confront him somehow? He lives in a different state I think. And what do I do about the phone ...`
   - Line 50: `... I've been going through her phone for months. She doesn't know this. Every couple of weeks ...`
   The "..." in both stderr quotes correspond exactly to text the LLM elided.

3. **Re-run with a fresh conv_id.** I re-executed `run_frame_extraction_from_packet` with the same extraction + conversation but a new `x-grok-conv-id` so the cached response wouldn't be reused. The LLM produced two clean elements:

   ```
   evidence_quote: 'But what about the guy? Do I call the police? Do I confront him somehow?'   → passes validator
   evidence_quote: "If he's undermining me on this when she eventually does come to talk, ..."  → passes validator
   ```

   Same prompt, different output. This confirms (a) the LLM *can* produce literal quotes when it doesn't choose to compress, and (b) the variability is the LLM's, not the validator's.

### Reproduction recipe

To confirm Issue B exists in your environment, run any case three or four times and watch for `lane3_all_dropped` in `run_health.issues` or non-empty `dropped_frame_elements`:

```bash
# Quick one-line check across all archived runs
for f in ~/.local/share/lolla/runs/*/*/result.json; do
  python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
drops = d.get('frame_pressure_card', {}).get('dropped_frame_elements', [])
elems = d.get('frame_pressure_card', {}).get('frame_elements', [])
issues = d.get('run_health', {}).get('issues', [])
if drops or 'lane3_all_dropped' in issues:
    print(f'{sys.argv[1]}: kept={len(elems)} dropped={len(drops)} issues={issues}')" "$f"
done
```

If you get a non-trivial fraction of runs (say > 1 in 10) with at least one dropped element, the LLM compression behaviour is real in your setup.

To reproduce on a specific case (this is what I did to confirm):

```bash
cd /Users/marcin/Desktop/Apps/lolla-skill
[ -f .env ] && set -a && source .env 2>/dev/null && set +a
python3 << 'PY'
import sys, json, os
sys.path.insert(0, 'engine')
from system_b.boundary_provider import load_boundary_client_from_env
from system_b.conversation_loader import load_conversation_context
from system_b.frame_pressure import (
    _format_frame_extraction_from_packet_user_prompt,
    _FRAME_EXTRACTION_SYSTEM_FROM_CONTEXT,
    _evidence_in_text, _joined_user_turns_text_from_packet,
)
from system_b.packet_builders.lane4 import build_lane4_packet
from system_b.pipeline import construct_conversation_ir
from pathlib import Path

# Pick any archived run
ARCHIVE = "/Users/marcin/.local/share/lolla/runs/mother-deciding-protect-year/20260428T093545Z"
ctx = load_conversation_context(
    extraction_path=Path(f"{ARCHIVE}/extraction.json"),
    conversation_path=Path(f"{ARCHIVE}/conversation.txt"),
)
ir = construct_conversation_ir(ctx)
packet = build_lane4_packet(ir)
user_prompt = _format_frame_extraction_from_packet_user_prompt(packet)
user_text = _joined_user_turns_text_from_packet(packet)

# Use a fresh conv_id each time so xAI doesn't return a cached response
os.environ["LOLLA_RUN_ID"] = "lane3_repro_test"
client = load_boundary_client_from_env("openrouter")
raw = client.run_json(_FRAME_EXTRACTION_SYSTEM_FROM_CONTEXT, user_prompt,
                      stage="frame_extraction_repro")
for el in raw.get("frame_elements", []):
    quote = el.get("evidence_quote", "")
    has_ellipsis = "..." in quote or "…" in quote
    passes = _evidence_in_text(quote, user_text)
    print(f"passes={passes} ellipsis={has_ellipsis} quote={quote!r}")
PY
```

Run it 5-10 times. **Confirms Issue B:** at least one run produces an `evidence_quote` containing `...` that the validator rejects, while other runs produce ellipsis-free quotes that pass. The behaviour is non-deterministic at the LLM layer.

**Disconfirms Issue B:** every run produces ellipsis-free quotes that all pass. If that happens, the rejected quotes from the original run had a different cause and we should re-investigate.

### Proposed fixes (this is where the design choice lives)

| Option | What | Tradeoff |
|---|---|---|
| **Validator tier 5 — ellipsis tolerance** | Treat `...` (and Unicode `…`, U+2026) inside `evidence_quote` as a "skip span" marker. Split on free-standing ellipsis (require surrounding whitespace so we don't break URLs, code, three-dot punctuation in dialog), require each fragment to appear in user_text in order, with the second fragment's start at or after the first fragment's end. | Preserves the "must be grounded in literal text" contract while accepting LLM compression. Slight permissiveness: a paraphrase that happens to contain literal substrings on both sides of a fabricated ellipsis would slip through. Real-world risk: low, because LLMs don't typically combine paraphrase with ellipsis — the ellipsis is the compression signal, paraphrase is what they do *instead* of compression. |
| **Prompt tightening** | Add an explicit "DO NOT use ellipsis (`...` or `…`) in evidence_quote — quote the prefix or the suffix only" instruction, with a negative example. | Cheap, but brittle: even reinforced prompts will fail on this exact pattern occasionally. Doesn't structurally solve the problem. |
| **Both** | Tier 5 as the structural fix; prompt tightening to lower the rate at which the validator has to compensate. | Belt + suspenders. Highest engineering effort but most robust. |

**My recommendation:** Both. The validator-only fix is the safety net (always works), the prompt-tightening is the rate reducer (most LLM responses comply). If you'd prefer one, the validator tier alone is the higher-value intervention because it's deterministic and survives across model changes. Prompt-only is the lower-value intervention because LLM behaviour drifts with model versions.

### One caveat I'm flagging on the validator tier

The split needs to be on a free-standing ellipsis, not the literal three-character substring `...`. Examples that should NOT trigger ellipsis treatment:

- A URL like `http://example.com/path/...` (path notation)
- A code block referencing slicing like `arr[...]`
- A dialog rendition like `"I... I don't know"` (real ellipsis as punctuation, not compression)

The right pattern is roughly `\s+\.\.\.\s+` or `\s+…\s+` — the ellipsis must be a free-standing token between whitespace. I want to verify this empirically against any cases in your archive that contain ellipsis-as-punctuation in user turns before writing the fix, so it doesn't false-trigger on legitimate user content. ~30 minutes of work.

### Confidence

**≥ 90 % on the mechanism** (LLM occasionally inserts `...`, validator correctly rejects, no slack). **Lower on rate** — I have one observed run where it bit, one re-run where it didn't. I don't have data on what fraction of Lolla runs hit this. The reproduction recipe above lets you collect that data.

---

## How to use this memo

1. **Run another conversation through `/lolla`.** Pick something different from the cases already archived — the recipe above lists what to look for. Multiple runs of the same case (with fresh `LOLLA_RUN_ID` each time so conv_id rotates) will give you a rate.
2. **Try a different LLM** (set `LOLLA_OPENROUTER_MODEL` to something other than `x-ai/grok-4.1-fast`) and re-run. If a different model never produces ellipsis-compressed quotes, that confirms the LLM-behaviour theory and lowers urgency on the validator fix; if other models also do it, the validator fix becomes more important. Either way it isolates whether this is a Grok-specific quirk or a general LLM compression pattern.
3. **Inspect the persisted `dropped_frame_elements`.** If they are still empty stubs (`element_text` + `drop_reason` only), Issue A is confirmed. If they carry the original `evidence_quote`, Issue A was already silently fixed somewhere I missed.
4. **Decide on fixes.** Issue A is mechanical and low-risk — open a small PR whenever convenient. Issue B has the design choice; once you've seen the rate of occurrence in your runs, the answer (validator tolerance, prompt tightening, or both) becomes clearer.

If during your verification you see anything that contradicts these claims — different `dropped_frame_elements` shape, no ellipsis in the rejected quotes, the validator rejecting non-ellipsis quotes — please flag it. The whole point of writing this as a verifiable memo rather than a declarative one is so disconfirming evidence has somewhere to land.
