# Quote Handling Issues (A, B, C) — Investigation Memo (2026-04-28)

**Purpose.** Three anomalies in how Lolla handles LLM-produced quotes — two in Lane 3 (Frame Pressure), one in extraction. All three surfaced during verification audits of two consecutive runs (`mother-deciding-protect-year/20260428T093545Z` and `mid-level-consultant-report-1/20260428T110004Z`). This memo documents root causes, the evidence behind each claim, and a reproduction recipe so anyone can confirm — or disconfirm — the findings before we change code. The intent is to fix them for good, not patch around them.

**Authoring constraint.** Every claim has either a file/line citation or a reproducible command. If you can't verify a claim from the artifacts, the claim is suspect.

**Status.** This memo is the working to-do list for these three issues. No code changes will be made until each finding is independently verified on more runs and the user (or another investigator) approves the fix shape. Pick up where the "Open items" section at the bottom leaves off.

**TL;DR.**

- **Issue A** (Lane 3 — `dropped_frame_elements` opacity) is a confirmed, mechanical bug in `_parse_frame_extraction_from_packet`. Confidence ≥ 95 %. Fix is mechanical (~5 lines).
- **Issue B** (Lane 3 — `_evidence_in_text` rejects LLM ellipsis compression) is a real interaction problem between LLM compression behaviour and a strict validator, not a bug in any single component. Confidence in mechanism ≥ 90 %. Fix is a design choice with a tradeoff to weigh.
- **Issue C** (extraction — `_validate_passages` rejects LLM quote-style substitution) is the same *class* of issue as Issue B but in a different code path with a stricter validator. Confidence in mechanism ≥ 95 % on the specific case observed. Whether the same kind of drift recurs on other runs needs more data.

**One thing worth knowing up front.** B and C are the same meta-pattern: the LLM produces a quote that is semantically identical to the source but with minor character-level drift (ellipsis, quote style, possibly more), and a strict substring validator rejects it. Lane 3 has 4 tolerance tiers; extraction has 1. So extraction is structurally more sensitive to this drift class than Lane 3. The unifying-fix candidate is at the bottom under "Open items."

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

## Issue C — extraction `quote_fabrication` rejected a real quote with substituted quote characters

### Symptom

In `mid-level-consultant-report-1/20260428T110004Z`, the run finished with `run_health.overall = "degraded"`, `issues = ["quote_fabrication"]`, `quote_fabrication_count = 1`, `quote_retry_attempted = True`. The chat output flagged this upfront ("Audit partially degraded: extraction had 1 reasoning passage that couldn't be verified..."). One of the LLM-extracted `reasoning_passages` couldn't be matched as a literal substring of the transcript even after the retry, so it was dropped from the persisted extraction and the audit ran on 4 passages instead of 5.

Unlike Lane 3 (Issue A), the extraction layer **does preserve** the rejected passages: they live in `extraction._quote_validation.fabricated_passages` in the result JSON. That's what allowed this investigation to proceed without re-running.

### Root cause

The single rejected passage from this run:

```
"the weight of institutional inertia at firms like yours usually produces 'quiet handling' for senior partners even when GCs mean well."
```

The corresponding text on transcript line 67:

```
the weight of institutional inertia at firms like yours usually produces "quiet handling" for senior partners even when GCs mean well.
```

Byte-level diff (using `difflib.SequenceMatcher`):

```
replace: LLM[73:74]="'"  → transcript[73:74]='"'
replace: LLM[88:89]="'"  → transcript[88:89]='"'
```

Two characters differ. The LLM substituted single quotes (`'`) for the transcript's double quotes (`"`) around `quiet handling`. The rest matches character-for-character. After normalizing single→double on the LLM output, the passage IS a literal substring of the transcript.

The extraction validator is `scripts/run_extract.py:_validate_passages` (lines 653-669), which calls `engine/system_b/text_matching.py:find_substring_tolerant`. That helper has **only one tolerance tier** — case-insensitive — explicitly documented at the top of the file:

> The helper intentionally tolerates ONLY case differences. Whitespace, punctuation, and word-substitution differences are all rejected — those are paraphrase or hallucination signatures that the substring validation is supposed to catch.

A quote-character substitution is not "case difference" — it's a punctuation difference. So the validator rejected it. Correct by the helper's documented contract; wrong for the actual semantic content.

### Evidence

Three independent confirmations:

1. **The persisted artifact carries the rejected text.** `extraction._quote_validation.fabricated_passages[0]` is the LLM-produced string above. Pulled directly from the result JSON (no stderr capture needed).

2. **The transcript contains the source text on line 67.** Verified by `grep -n "institutional inertia" conversation.txt`. The fragment on either side of the differing characters matches verbatim.

3. **Byte-level diff confirms only the two quote characters differ.** Programmatic `difflib.SequenceMatcher` over the two strings produced exactly two `replace` operations, each at a single character position, both replacing `'` with `"`. After `replace("'", '"')` normalization on the LLM string, `string in transcript` returns `True`.

### Reproduction recipe

To confirm Issue C in any future run:

```bash
# After /lolla finishes, pull the rejected passages from the run's extraction
python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
qv = d.get('extraction', {}).get('_quote_validation', {})
if qv.get('fabricated', 0) > 0:
    print(f'fabricated={qv[\"fabricated\"]}/{qv[\"total\"]}, retry_succeeded={qv[\"retry_succeeded\"]}')
    for p in qv.get('fabricated_passages', []):
        print(f'  REJECTED: {p!r}')
" ~/.local/share/lolla/runs/<case>/<run_id>/result.json
```

Then for each rejected passage, look for a near-match in the transcript:

```bash
# Try increasingly specific substrings until you find one that matches
grep -n "<some-fragment-of-the-rejected-text>" ~/.local/share/lolla/runs/<case>/<run_id>/conversation.txt
```

If you find a near-match, run `difflib.SequenceMatcher` to see exactly which characters differ:

```python
import difflib, json
d = json.load(open("/path/to/result.json"))
fab = d['extraction']['_quote_validation']['fabricated_passages'][0]
tx = open("/path/to/conversation.txt").read()
# Pull a window around the suspected match and diff
import re
m = re.search(r"<a-distinctive-prefix-from-the-rejected-text>.*?<a-distinctive-suffix>", tx, re.DOTALL)
if m:
    sm = difflib.SequenceMatcher(None, fab, m.group(0))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"{tag}: LLM[{i1}:{i2}]={fab[i1:i2]!r} → transcript[{j1}:{j2}]={m.group(0)[j1:j2]!r}")
```

**Confirms Issue C** if the diff shows only minor character drift (quote style, ellipsis, smart quotes, dashes, whitespace) and the LLM string is otherwise a literal substring after normalization.

**Disconfirms Issue C** if the diff shows actual word substitutions or multi-character paraphrase. In that case the validator was correctly rejecting a paraphrase, not over-rejecting a near-literal quote.

### Predicted drift modes (in priority order)

If you see more `quote_fabrication` events on future runs, the most likely culprits — in roughly the order I'd expect, given today's data point and what's documented in LLM behaviour:

1. **Quote-style substitution** (`'` ↔ `"`) — confirmed today
2. **Smart-quote ↔ ASCII** (`“”` ↔ `"`, `‘’` ↔ `'`) — common when LLM "polishes" quoted text
3. **Em-dash ↔ hyphen-hyphen** (`—` ↔ `--`)
4. **Trailing/leading whitespace** drift
5. **`\\n` ↔ `\n` ↔ literal newline** in multi-line quotes

If the next runs surface non-quote drift modes, add them to this list with the byte-level diff that proves it.

### Proposed fix shape (parked until the rate is known)

Same shape as Issue B's validator-tier fix, applied to the extraction validator. Two reasonable scopes:

| Scope | What | When to choose |
|---|---|---|
| **Local** | Add a `_normalize_quotes` tier (and possibly more) directly to `find_substring_tolerant`, mirroring Lane 3's `_evidence_in_text` tolerance ladder. | If you only want to fix Issue C without touching Lane 3. |
| **Unified** | Extract the tolerance-ladder logic into a shared helper that both `_validate_passages` (extraction) and `_evidence_in_text` (Lane 3) consume. Eliminates the strictness drift between the two validators and gives Issue B's eventual fix one place to land. | If you're touching either validator. |

I'd recommend **Unified**. The current divergence (Lane 3 has 4 tiers; extraction has 1) is exactly the kind of structural inconsistency that produces drift bugs over time. One shared validator with documented tiers, one set of tests, one decision point.

### Confidence

**≥ 95 % on the specific case observed.** I have a byte-level diff and the validator's documented contract — both align with the rejection. **Lower on rate.** This is one observed event. Whether quote-style substitution is the dominant drift mode, or whether other drift modes will surface, requires more runs.

---

## How they relate

Visualizing A, B, C in one table makes the structure clear:

| Issue | Surface | Validator | What's strict about it | Tolerates |
|---|---|---|---|---|
| **A** | Lane 3 dropped record persistence | n/a (data-loss bug) | Stores only `element_text` + `drop_reason` when dropping; discards `evidence_quote`, `element_type`, `frame_pattern`, etc. | nothing — it's an opacity bug, not a strictness issue |
| **B** | Lane 3 quote validator (`_evidence_in_text`) | LLM ellipsis (`...`) for compression | exact substring, JSON-escape normalize, wrapping-quote strip, case-insensitive (4 tiers) |
| **C** | Extraction quote validator (`find_substring_tolerant` via `_validate_passages`) | LLM quote-style substitution (`'` ↔ `"`) | case-insensitive only (1 tier) |

**B and C share a meta-pattern.** Both are "LLM produces text that's semantically identical to the source but has minor character-level drift; strict validator rejects." The drift modes differ (compression vs. quote style) but the underlying class is the same. **A is structurally different** — it's about what the system records when validation fails, not about whether validation should succeed.

**Extraction is the more sensitive surface.** Lane 3 has 4 tolerance tiers; extraction has 1. So a quote that survives Lane 3 might still be rejected by extraction. If you encounter a drift class that hits extraction but not Lane 3, that's the signal that extraction's validator is the more urgent one to fix.

**A's data-loss is independent.** Even after B and C are fixed, A's opacity remains useful work because it makes the *next* class of validation failure investigable from persisted artifacts alone, without needing stderr capture or re-runs. Investigators 6 months from now will thank you.

---

## How to use this memo

1. **Run another conversation through `/lolla`.** Pick something different from cases already archived. Multiple runs of the same case (with fresh `LOLLA_RUN_ID` each time so the cache rotates) give you a rate per drift mode.
2. **Try a different LLM** (set `LOLLA_OPENROUTER_MODEL` to something other than `x-ai/grok-4.1-fast`). If a different model never produces ellipsis-compressed or quote-substituted quotes, that confirms LLM-behaviour theory and lowers urgency on the validator fixes; if other models also do it, the unified-validator fix becomes more important. Either way it isolates whether B/C are Grok-specific quirks or a general LLM character-drift pattern.
3. **Inspect the persisted artifacts on every run.** Run the Issue A check on `dropped_frame_elements` and the Issue C check on `_quote_validation.fabricated_passages`. Log what you find — over 5-10 runs, you'll have a rate for each.
4. **Look for new drift modes.** If a future `quote_fabrication` rejection isn't quote-style or ellipsis, add it to Issue C's "Predicted drift modes" list with the byte-level diff. This memo grows as data grows.
5. **Decide on fixes once the rate justifies them.** If A fires every few runs, fix it (mechanical, ~5 lines, no risk). If B and C combined fire less than once every 10-20 runs and only on specific content, the cost of building a unified validator may exceed the benefit — keep watching. If they fire often, the unified validator becomes worth the work.

If during verification you see anything that contradicts these claims — different `dropped_frame_elements` shape, no ellipsis or quote drift in the rejected quotes, validators rejecting actual paraphrases — please flag it. The whole point of writing this as a verifiable memo rather than a declarative one is so disconfirming evidence has somewhere to land.

---

## Open items (the working to-do list)

Tracked here so the memo functions as a single source of truth for these three issues. Strike through items as they're resolved; add new items as data comes in.

### Verification before any fix

- [ ] Issue A — confirm `dropped_frame_elements` opacity reproduces on at least one more run with non-empty drops. Reproduction recipe is in Issue A's section.
- [ ] Issue B — confirm rate of LLM ellipsis insertion across 5-10 runs (different cases, different conversation lengths). Reproduction recipe is in Issue B's section.
- [ ] Issue C — confirm rate of LLM quote-style substitution (and any other drift modes) across 5-10 runs. Reproduction recipe is in Issue C's section.
- [ ] Cross-model — run any one case with a non-Grok model (`LOLLA_OPENROUTER_MODEL=anthropic/claude-...`, `openai/gpt-...`) to test whether B and C are Grok-specific or general LLM behaviour.

### When verification justifies a fix

- [ ] **Issue A fix** — preserve `evidence_quote`, `element_type`, `frame_pattern`, `fragility_signal`, `inquiry_stage`, `likely_default` in every dropped record in `_parse_frame_extraction_from_packet`. Backward-compatible (additive). Mechanical, low-risk, 5 lines. Open as standalone PR whenever convenient.
- [ ] **Issues B + C unified fix** — extract the tolerance-ladder logic into a shared validator that both Lane 3 (`_evidence_in_text`) and extraction (`_validate_passages`) consume. Tiers documented and tested. The list of tolerated drift modes (case, JSON-escape, wrapping quotes, ellipsis, quote style, smart quotes, dashes, whitespace) is the design surface. **Don't bundle with A** — different code path, different review concerns.
- [ ] **Prompt hardening** (parallel to validator fixes, not replacement) — add explicit "do not use ellipsis" / "preserve quote characters exactly" instructions to the frame_extraction and extraction prompts, with negative examples. Cheap, partial, brittle on its own; useful as a rate-reducer alongside the validator fix.

### Adjacent observations to keep an eye on

- The extraction layer's `_quote_validation` block (which made Issue C investigable) is a good pattern; consider whether Lane 3 should adopt it when fixing Issue A.
- The `find_substring_tolerant` helper is also used by `engine/system_b/live_constraints_extraction.py` and `engine/system_b/stance_extraction.py` (per repo grep). Any change to its tolerance behaviour affects all four call sites — that's a feature for the unified fix but worth knowing before changing it.

### Disconfirming evidence to add as it appears

If any future verification produces a result that contradicts a claim in this memo, append it here with the run_id and the contradicting evidence. The memo's value depends on staying honest as data accumulates.

(none yet)
