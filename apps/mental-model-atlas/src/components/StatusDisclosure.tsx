import type {
  AtlasMissingness,
  AtlasPublicationStatus,
  AtlasSourceRef,
} from "../projection";

export function StatusDisclosure({
  status,
  missingness,
  sourceRefs,
  nonClaims,
}: {
  status?: AtlasPublicationStatus;
  missingness: AtlasMissingness;
  sourceRefs: AtlasSourceRef[];
  nonClaims: string[];
}) {
  return (
    <aside className="custody-card" aria-label="Source and status">
      <div className="custody-heading">
        <div>
          <p className="eyebrow">Source custody</p>
          <h2>What this page can claim</h2>
        </div>
        <span className={`status-pill status-${safeClass(missingness.status)}`}>
          {humanize(missingness.status)}
        </span>
      </div>

      {status ? (
        <dl className="status-grid">
          {Object.entries(status).map(([label, value]) => (
            <div key={label}>
              <dt>{humanize(label)}</dt>
              <dd>{humanize(value)}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      <details>
        <summary>Inspect sources and boundaries</summary>
        <h3>Source references</h3>
        <ul className="source-list">
          {sourceRefs.map((source) => (
            <li key={`${source.path}:${source.json_pointer ?? ""}`}>
              <code>{source.path}</code>
              {source.json_pointer ? <code>{source.json_pointer}</code> : null}
              <span>sha256 {source.sha256.slice(0, 12)}…</span>
            </li>
          ))}
        </ul>
        {missingness.missing_fields.length > 0 ? (
          <>
            <h3>Named missing fields</h3>
            <ul>
              {missingness.missing_fields.map((field) => (
                <li key={field}>{humanize(field)}</li>
              ))}
            </ul>
          </>
        ) : null}
        <h3>Non-claims</h3>
        <ul>
          {nonClaims.map((claim) => (
            <li key={claim}>{humanize(claim)}</li>
          ))}
        </ul>
      </details>
    </aside>
  );
}

export function humanize(value: string): string {
  return value.replaceAll("_", " ").replaceAll("-", " ");
}

function safeClass(value: string): string {
  return value.replace(/[^a-z0-9-]/gi, "-").toLowerCase();
}
