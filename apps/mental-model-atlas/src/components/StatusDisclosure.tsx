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
  collapseTechnical = false,
}: {
  status?: AtlasPublicationStatus;
  missingness: AtlasMissingness;
  sourceRefs: AtlasSourceRef[];
  nonClaims: string[];
  collapseTechnical?: boolean;
}) {
  return (
    <aside className="custody-card" aria-label="Source and status">
      <div className="custody-heading">
        <div>
          <p className="eyebrow">About this page</p>
          <h2>{collapseTechnical ? "A local learning preview" : "What this page can claim"}</h2>
        </div>
        <span className={`status-pill status-${safeClass(missingness.status)}`}>
          {humanize(missingness.status)}
        </span>
      </div>

      {collapseTechnical ? (
        <>
          <p className="custody-human-summary">
            The source is verified, but this page is still under human review and
            is not cleared for publication.
          </p>
          <details>
            <summary>Review status, exact sources, and boundaries</summary>
            <StatusGrid status={status} />
            <SourceAndBoundaryDetails
              missingness={missingness}
              nonClaims={nonClaims}
              sourceRefs={sourceRefs}
            />
          </details>
        </>
      ) : (
        <>
          <StatusGrid status={status} />
          <details>
            <summary>Inspect sources and boundaries</summary>
            <SourceAndBoundaryDetails
              missingness={missingness}
              nonClaims={nonClaims}
              sourceRefs={sourceRefs}
            />
          </details>
        </>
      )}
    </aside>
  );
}

function StatusGrid({ status }: { status?: AtlasPublicationStatus }) {
  return status ? (
    <dl className="status-grid">
      {Object.entries(status).map(([label, value]) => (
        <div key={label}>
          <dt>{humanize(label)}</dt>
          <dd>{humanize(value)}</dd>
        </div>
      ))}
    </dl>
  ) : null;
}

function SourceAndBoundaryDetails({
  missingness,
  sourceRefs,
  nonClaims,
}: {
  missingness: AtlasMissingness;
  sourceRefs: AtlasSourceRef[];
  nonClaims: string[];
}) {
  return (
    <>
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
    </>
  );
}

export function humanize(value: string): string {
  return value.replaceAll("_", " ").replaceAll("-", " ");
}

function safeClass(value: string): string {
  return value.replace(/[^a-z0-9-]/gi, "-").toLowerCase();
}
