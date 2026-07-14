# Case 08 Stage A — quote-custody gate failure

Status: **stopped; no retry**

The fresh extraction captured all 18 messages with good health and no
truncation. Its one allowed quote-repair call ran, but two reasoning passages
still failed character-exact substring validation. The pipeline and Stage B
therefore did not run.

Source review found a narrow mechanical cause: the passages preserved the
source words but changed double quotation marks around internal phrases to
single quotation marks. The frozen matcher correctly treated them as failures
under its then-current contract. The case remains failed and will not be
rerun.

Prospectively, the shared matcher now treats only quote delimiters as
equivalent and returns the literal source substring with source punctuation.
Apostrophes inside words remain significant, and word substitution,
reordering, missing text, and paraphrase remain invalid. The focused matcher
and extraction suite passes.

After one artifact-persistence failure and one frozen quote-gate failure, the
program stops selecting additional cases in this cycle. Continuing until a
case passes would burn calls and bias case selection.
