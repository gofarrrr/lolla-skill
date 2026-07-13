# Case 02 Stage A — infrastructure failure

Status: **stopped; no retry**

The fresh extraction provider call completed, but the configured output parent
directory had not been created. `run_extract.py` attempted to persist the
response after the call and raised `FileNotFoundError`. The extraction and its
usage metadata were lost.

The frozen contract forbids experiment retries. Case 02 therefore receives no
second extraction, no pipeline run, and no downstream pair.

This is a custody/operability failure, not a semantic result. Prospectively,
the runner now prepares or rejects the output path before provider
initialization. Regression tests prove that:

- nested output parents exist before a provider client is initialized;
- an invalid output parent stops without initializing the provider;
- ordinary stdout mode remains unchanged.

The next holdout must use a different case and a new contract containing the
repaired runner hash.
