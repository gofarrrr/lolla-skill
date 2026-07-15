import { useEffect } from "react";

import { ProjectionFailure, ProjectionLoading } from "../components/ProjectionFailure";
import { humanize } from "../components/StatusDisclosure";
import { modelPageUrl } from "../projection";
import { useProjection } from "../projectionContext";
import { AppLink, navigate, useLocation } from "../router";

export default function LibraryPage() {
  const projectionState = useProjection();
  const location = useLocation();
  const query = location.searchParams.get("q")?.trim() ?? "";

  useEffect(() => {
    document.title = "Model Library · Lolla Atlas";
  }, []);

  if (projectionState.status === "loading") {
    return <LibraryFrame><ProjectionLoading /></LibraryFrame>;
  }
  if (projectionState.status === "failed") {
    return (
      <LibraryFrame>
        <ProjectionFailure message={projectionState.message} retry={projectionState.retry} />
      </LibraryFrame>
    );
  }

  const models = projectionState.projection.models;
  const needle = query.toLocaleLowerCase();
  const filteredModels = models.filter((model) =>
    needle
      ? `${model.display_name} ${model.model_id} ${model.slug}`
          .toLocaleLowerCase()
          .includes(needle)
      : true,
  );
  const completePageCount = models.filter((model) => modelPageUrl(model.slug)).length;
  const unavailablePageCount = models.length - completePageCount;

  function updateQuery(value: string): void {
    const params = new URLSearchParams(location.searchParams);
    if (value) {
      params.set("q", value);
    } else {
      params.delete("q");
    }
    navigate(`/models${params.size ? `?${params.toString()}` : ""}`, {
      replace: true,
    });
  }

  return (
    <LibraryFrame>
      <section className="library-toolbar">
        <label className="search-field">
          <span>Search this frozen slice</span>
          <input
            type="search"
            value={query}
            onChange={(event) => updateQuery(event.target.value)}
            placeholder="Model name or canonical ID"
          />
        </label>
        <p role="status">
          {filteredModels.length} of {models.length} model records · {completePageCount}{" "}
          complete page · {unavailablePageCount} page artifacts unavailable in Phase 1
        </p>
      </section>

      {filteredModels.length === 0 ? (
        <section className="zero-state" role="status">
          <strong>Completed zero</strong>
          <p>The verified projection loaded and this text search has no matches.</p>
          <button type="button" onClick={() => updateQuery("")}>
            Clear search
          </button>
        </section>
      ) : (
        <ul className="model-card-grid">
          {filteredModels.map((model) => (
            <li key={model.model_id}>
              <article className="model-card">
                <div className="card-index" aria-hidden="true">
                  {model.display_name.slice(0, 1)}
                </div>
                <p className="canonical-id">{model.model_id}</p>
                <h2>{model.display_name}</h2>
                <p className="model-summary">{model.summary.text}</p>
                <p className="card-status">
                  {humanize(model.status.human_review)} ·{" "}
                  {humanize(model.status.publication)}
                </p>
                <div className="card-actions">
                  {modelPageUrl(model.slug) ? (
                    <AppLink href={`/models/${model.slug}`}>Read complete model</AppLink>
                  ) : (
                    <AppLink href={`/models/${model.slug}`}>
                      Page unavailable — inspect status
                    </AppLink>
                  )}
                  <AppLink href={`/atlas?model=${encodeURIComponent(model.model_id)}`}>
                    Show in Atlas
                  </AppLink>
                </div>
              </article>
            </li>
          ))}
        </ul>
      )}
    </LibraryFrame>
  );
}

function LibraryFrame({ children }: { children: React.ReactNode }) {
  return (
    <main id="main" className="content-route library-route">
      <header className="content-hero">
        <p className="eyebrow">The non-canvas entrance</p>
        <h1>Model Library</h1>
        <p>
          Browse the same stable identities without relying on spatial navigation.
          Search is deterministic text matching, not an opaque relevance score.
        </p>
      </header>
      {children}
    </main>
  );
}
