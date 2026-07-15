import { AppLink } from "../router";

export function ProjectionLoading() {
  return (
    <section className="data-state" aria-live="polite" aria-busy="true">
      <span className="loading-orbit" aria-hidden="true" />
      <div>
        <p className="eyebrow">Loading source-bound projection</p>
        <h2>Placing the frozen neighborhood…</h2>
      </div>
    </section>
  );
}

export function ProjectionFailure({
  message,
  retry,
}: {
  message: string;
  retry: () => void;
}) {
  return (
    <section className="data-state failure-state" role="alert">
      <div className="failure-glyph" aria-hidden="true">
        !
      </div>
      <div>
        <p className="eyebrow">Projection failed</p>
        <h2>The Atlas data could not be verified.</h2>
        <p>{message}</p>
        <p>
          This is a failed data state, not a valid zero-result search. No missing
          identity or meaning has been inferred.
        </p>
        <div className="button-row">
          <button type="button" onClick={retry}>
            Retry projection
          </button>
          <AppLink className="button secondary" href="/learn">
            Open product boundary
          </AppLink>
        </div>
      </div>
    </section>
  );
}
