# PR56 Canonical Corpus Custody Check

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: deterministic custody check; no extraction, runtime, prompt, memo, Observatory, or `/lolla` behavior changed

Canonical source root:

`/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`

Local working source root:

`data/model_sources/`

## Verdict

The canonical corpus and the local `data/model_sources/` corpus are byte-identical for Markdown sources.

This matters because PR56 source-adequacy review can safely compare v18 records against `data/model_sources/` while treating `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` as the source of truth.

## Counts

| Corpus surface | Markdown files |
| --- | ---: |
| Canonical `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` | 222 |
| Local `data/model_sources/` | 222 |
| Compiled v18 source metadata | 222 |
| Compiled v18 model records | 222 |

## Hash Check

Result:

| Check | Result |
| --- | --- |
| Canonical file missing from local source copy | 0 |
| Extra local source file not in canonical corpus | 0 |
| Canonical/local SHA-256 mismatch | 0 |
| Canonical file missing from v18 compile metadata | 0 |
| v18 metadata SHA-256 mismatch against canonical file | 0 |
| v18 model record source file not in canonical corpus | 0 |

## Compile Metadata Validation

From `data/compiled/model_affordances/affordances_v18.json`:

```json
{
  "schema_validation_failure_count": 0,
  "source_hash_failure_count": 0,
  "source_quote_rejection_count": 0
}
```

## Commands Used

```bash
find data/model_sources -maxdepth 1 -type f -name '*.md' | wc -l
find /Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216 -maxdepth 1 -type f -name '*.md' | wc -l
python3 -c "from pathlib import Path; import hashlib; a=Path('/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216'); b=Path('data/model_sources'); ah={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in a.glob('*.md')}; bh={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.glob('*.md')}; print('canonical',len(ah),'local',len(bh)); print('missing_local',sorted(set(ah)-set(bh))[:20],len(set(ah)-set(bh))); print('extra_local',sorted(set(bh)-set(ah))[:20],len(set(bh)-set(ah))); mism=[n for n in sorted(set(ah)&set(bh)) if ah[n]!=bh[n]]; print('mismatches',len(mism)); print(mism[:30])"
python3 -c "from pathlib import Path; import json,hashlib; c=Path('/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216'); d=json.load(open('data/compiled/model_affordances/affordances_v18.json')); meta={x['filename']:x for x in d['compile_metadata']['source_files']}; hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in c.glob('*.md')}; misses=[n for n in sorted(hashes) if n not in meta]; mism=[n for n,h in sorted(hashes.items()) if n in meta and meta[n]['sha256']!=h]; print('metadata_source_files',len(meta)); print('canonical_hashes',len(hashes)); print('missing_in_metadata',len(misses),misses[:10]); print('hash_mismatches',len(mism),mism[:10])"
python3 -c "from pathlib import Path; import json; d=json.load(open('data/compiled/model_affordances/affordances_v18.json')); by_source={r['source_file']:r['model_id'] for r in d['model_records']}; names={p.name for p in Path('/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216').glob('*.md')}; print('missing_record_for_source', sorted(names-set(by_source))[:20], len(names-set(by_source))); print('record_source_not_canonical', sorted(set(by_source)-names)[:20], len(set(by_source)-names))"
```

## Interpretation

This check does not prove extraction quality.

It proves source custody:

- PR56 is not auditing a stale or partial copy;
- every canonical Markdown file has a v18 model record source file;
- every v18 model record source file exists in the canonical corpus;
- the compiled metadata hashes match the canonical files.

The remaining question is semantic:

> Did v18 extract each canonical source at the right transaction granularity?

That requires source-reading loss audit, not just hash comparison.

## Audit Implication

The PR56 adequacy ledger should cite canonical files and may use local paths interchangeably because the bytes match.

Future reviewers should still treat `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` as the conceptual source of truth and `data/model_sources/` as the verified working copy used by the compiler.
