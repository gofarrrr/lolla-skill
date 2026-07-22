import { useEffect } from "react";

import { cardFirstModelPageUrl } from "../cardFirstModelPage";
import { ProjectionFailure, ProjectionLoading } from "../components/ProjectionFailure";
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
          <span>Search models</span>
          <input
            type="search"
            value={query}
            onChange={(event) => updateQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key !== "Enter" || filteredModels.length === 0) return;
              event.preventDefault();
              navigate(`/models/${filteredModels[0].slug}`);
            }}
            placeholder="Try ‘abstraction’ or ‘systems’"
          />
        </label>
        <AppLink className="library-featured" href="/models/abstraction">
          <span>Complete reading page</span>
          <strong>Read Abstraction</strong>
        </AppLink>
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
                <h2>{model.display_name}</h2>
                <p className="model-summary">{model.summary.text}</p>
                <div className="card-actions">
                  {cardFirstModelPageUrl(model.slug) ? (
                    <AppLink href={`/models/${model.slug}`}>Read complete model</AppLink>
                  ) : (
                    <AppLink href={`/models/${model.slug}`}>
                      Full page coming later
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
        <h1>Browse mental models.</h1>
        <p>
          Find an idea by name, read its summary, then open the full page or see how
          it connects to the wider landscape.
        </p>
      </header>
      {children}
    </main>
  );
}
