# Ambiguous development Case 02 — Stage A result

Date: 2026-07-10  
Status: stopped after extraction; no rerun

## Simple result

The system behaved correctly, but our new test input was packaged incorrectly.
All 14 conversation messages were present, Gemini returned a usable extraction,
seven source quotes were exact, and custody was complete. However, the source
file lacked Lolla's declared `CONVERSATION:` count header. The system therefore
could not independently verify that the visible transcript was the whole
transcript and refused to call capture health good.

The full pressure pipeline made zero calls. The single extraction used 3,224
tokens and is estimated at $0.00153975 using the frozen 2026-05-25 price table.
There was no experiment retry.

## What this taught us

Realistic content is not enough for an accountable evaluation fixture. The
fixture must reproduce the capture envelope that tells Lolla how many user and
assistant messages should exist. We are preserving the original authored files
and deriving separate capture-ready wrappers by adding only that count header.

The Stage A dry run also had a blind spot: it checked hashes and prompts but did
not validate capture completeness before authorizing a paid extraction. That
preflight is now repaired and tested.

The unadmitted extraction still offers a provisional development clue. It found
the broad decision and exact supporting passages, but blurred who originated
the final conditional pilot, strengthened an informal foundation comment into a
funding preference, introduced `volunteer burnout`, compressed several distinct
constraints, and mislabeled a partly addressed thread as never addressed. These
are exactly the joint-process and nuance problems the ambiguous corpus was meant
to expose, but they are not yet independent or frequency evidence.

## Next decision

Case 02 is consumed and will not be rerun. The next bounded Stage A observation
will use the capture-ready version of the next case in the previously frozen
rank: `amb1-case05-family-archive`. No downstream answer generation, graph
ablation, or semantic tuning is authorized by this stopped run.
