import { useEffect, useMemo, useState } from "react";

import {
  EMPTY_EPHEMERAL_STATE,
  parseAtlasState,
  updateAtlasState,
} from "../atlasState";
import { relationCoverageText, selectAtlasView } from "../atlasSelectors";
import { AccessibleAtlas } from "../components/AccessibleAtlas";
import { AtlasControls } from "../components/AtlasControls";
import {
  GraphSurface,
  type RendererKind,
} from "../components/GraphSurface";
import {
  ProjectionFailure,
  ProjectionLoading,
} from "../components/ProjectionFailure";
import { HoverPreview, SelectionPanel } from "../components/SelectionPanel";
import type { AtlasProjection, FixtureId } from "../projection";
import { useProjection } from "../projectionContext";
import { navigate, useLocation } from "../router";

export default function AtlasPage({ motionPaused }: { motionPaused: boolean }) {
  const location = useLocation();
  const projectionState = useProjection();
  const durableState = parseAtlasState(location);
  const [ephemeralState, setEphemeralState] = useState(EMPTY_EPHEMERAL_STATE);
  const renderer: RendererKind =
    location.searchParams.get("renderer") === "canvas" ? "canvas" : "svg";
  const projection =
    projectionState.status === "ready" ? projectionState.projection : null;
  const selection = useMemo(
    () =>
      projection
        ? selectAtlasView(
            projection,
            durableState,
            ephemeralState.hoveredModelId,
          )
        : null,
    [projection, durableState, ephemeralState.hoveredModelId],
  );

  useEffect(() => {
    document.title = "Atlas · Lolla Mental Models";
  }, []);

  useEffect(() => {
    if (projectionState.status !== "ready") {
      return undefined;
    }
    performance.clearMarks("lolla-atlas-useful");
    const frame = requestAnimationFrame(() => {
      performance.mark("lolla-atlas-useful");
    });
    return () => cancelAnimationFrame(frame);
  }, [projectionState.status, projectionState.fixtureId]);

  if (projectionState.status === "loading") {
    return (
      <main id="main" className="atlas-route">
        <AtlasHero />
        <ProjectionLoading />
      </main>
    );
  }
  if (projectionState.status === "failed") {
    return (
      <main id="main" className="atlas-route">
        <AtlasHero />
        <ProjectionFailure
          message={projectionState.message}
          retry={projectionState.retry}
        />
      </main>
    );
  }

  if (!projection || !selection) {
    throw new Error("Ready Atlas state is missing its validated projection");
  }

  function changeState(
    patch: Parameters<typeof updateAtlasState>[1],
    replace = false,
  ): void {
    updateAtlasState(location, patch, { replace });
  }

  function selectModel(modelId: string): void {
    changeState({
      selectedModelId: modelId,
      selectedRelationId: null,
      relationPage: 1,
    });
  }

  function selectRelation(relationId: string): void {
    changeState({ selectedRelationId: relationId });
  }

  function clearSelection(): void {
    const focusModelId =
      selection?.selectedModel?.model_id ??
      selection?.selectedRelation?.source_model_id ??
      null;
    changeState({
      selectedModelId: null,
      selectedRelationId: null,
      relationPage: 1,
    });
    if (focusModelId) {
      requestAnimationFrame(() => {
        document
          .querySelector<SVGGElement>(`[data-model-id="${focusModelId}"]`)
          ?.focus();
      });
    }
  }

  function switchFixture(fixtureId: FixtureId): void {
    const params = new URLSearchParams(location.searchParams);
    params.set("fixture", fixtureId);
    params.delete("model");
    params.delete("relation");
    params.delete("page");
    navigate(`/atlas?${params.toString()}`);
  }

  function switchRenderer(nextRenderer: RendererKind): void {
    const params = new URLSearchParams(location.searchParams);
    if (nextRenderer === "canvas") {
      params.set("renderer", "canvas");
    } else {
      params.delete("renderer");
    }
    navigate(`/atlas${params.size ? `?${params.toString()}` : ""}`);
  }

  const focusActive = Boolean(
    selection.selectedModel || selection.selectedRelation,
  );
  const scopeText = focusActive
    ? relationCoverageText(selection)
    : `${selection.visibleModels.length} of ${projection.models.length} canonical models in this frozen slice; no relation focus selected.`;

  return (
    <main id="main" className="atlas-route">
      <AtlasHero />
      <AtlasControls
        state={durableState}
        fixtureId={projectionState.fixtureId}
        renderer={renderer}
        onStateChange={changeState}
        onFixtureChange={switchFixture}
        onRendererChange={switchRenderer}
      />
      <PageNavigation
        projection={projection}
        onPageChange={(pageNumber) =>
          changeState({ relationPage: pageNumber })
        }
      />

      <section
        className="atlas-workspace"
        data-motion-paused={motionPaused ? "true" : "false"}
        data-projection-id={projection.projection_id}
        data-coordinate-sha256={projection.layout.coordinate_sha256}
        data-atlas-ready="true"
        aria-labelledby="atlas-scope"
      >
        <div className="graph-column">
          <div className="scope-strip">
            <p id="atlas-scope" role="status">
              {scopeText}
            </p>
            <span>
              {renderer === "canvas" ? "Canvas 2D comparison" : "SVG editorial"}
            </span>
          </div>

          {durableState.view === "graph" ? (
            <div className="mobile-atlas-entry">
              <p className="eyebrow">Compact-screen entry</p>
              <h2>Start with the source-backed list.</h2>
              <p>
                The dense visual neighborhood is held back on narrow screens. The
                same model identities, exact directed relations, selection state,
                and full pages remain available below.
              </p>
              <a className="button" href="#accessible-atlas">
                Browse models and relations
              </a>
            </div>
          ) : null}

          {selection.visibleModels.length === 0 ? (
            <div className="graph-zero-state" role="status">
              <span aria-hidden="true">0</span>
              <h2>Completed zero</h2>
              <p>
                The source projection loaded. This text filter matches no model;
                the map has not failed and no source object was deleted.
              </p>
              <button
                type="button"
                onClick={() => changeState({ query: "" })}
              >
                Clear text filter
              </button>
            </div>
          ) : durableState.view === "list" ? (
            <div className="text-view-intro">
              <p className="eyebrow">Text Atlas selected</p>
              <h2>The semantic list is the primary navigation view.</h2>
              <p>
                The same durable selection, filters, records, counts, and routes are
                available below without a visual renderer.
              </p>
              <a className="button" href="#accessible-atlas">
                Jump to models and relations
              </a>
            </div>
          ) : (
            <div className="graph-stage">
              <GraphSurface
                renderer={renderer}
                projection={projection}
                relations={selection.focusedRelations}
                selectedModelId={selection.selectedModel?.model_id ?? null}
                selectedRelationId={selection.selectedRelation?.relation_id ?? null}
                hoveredModelId={selection.hoveredModel?.model_id ?? null}
                relatedModelIds={selection.relatedModelIds}
                visibleModelIds={new Set(
                  selection.visibleModels.map((model) => model.model_id),
                )}
                onSelectModel={selectModel}
                onSelectRelation={selectRelation}
                onHoverModel={(modelId) =>
                  setEphemeralState((current) => ({
                    ...current,
                    hoveredModelId: modelId,
                  }))
                }
                fallback={
                  <div className="renderer-fallback" role="alert">
                    <p className="eyebrow">Visual renderer failed</p>
                    <h2>The text Atlas remains available.</h2>
                    <p>
                      This local rendering failure does not become a zero-result or
                      alter the projection.
                    </p>
                    <a className="button" href="#accessible-atlas">
                      Use accessible model and relation view
                    </a>
                  </div>
                }
              />
              <HoverPreview selection={selection} />
            </div>
          )}
        </div>
        <SelectionPanel
          projection={projection}
          selection={selection}
          onClear={clearSelection}
        />
      </section>

      <AccessibleAtlas
        projection={projection}
        selection={selection}
        onSelectModel={selectModel}
        onSelectRelation={selectRelation}
      />

      <footer className="atlas-boundary">
        <p>
          Stable position and visual salience support navigation. They do not prove
          importance, relevance, correctness, usefulness, or mastery.
        </p>
        <p>
          Projection <code>{projection.projection_id}</code> · layout{" "}
          <code>{projection.layout.coordinate_sha256.slice(0, 12)}…</code>
        </p>
      </footer>
    </main>
  );
}

function PageNavigation({
  projection,
  onPageChange,
}: {
  projection: AtlasProjection;
  onPageChange: (pageNumber: number) => void;
}) {
  const pageCount = Math.ceil(
    projection.page.eligible_count / projection.page.page_size,
  );
  if (pageCount <= 1) {
    return null;
  }
  const currentPage = projection.page.page_number;
  return (
    <nav className="page-navigation" aria-label="Relation record pages">
      <div>
        <p className="eyebrow">Exact deterministic paging</p>
        <strong>
          Page {currentPage} of {pageCount}
        </strong>
        <span>
          {projection.page.before_count + 1}–
          {projection.page.before_count + projection.page.shown_count} of{" "}
          {projection.page.eligible_count} source-authored relation records
        </span>
      </div>
      <div className="button-row">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={currentPage >= pageCount}
          onClick={() => onPageChange(currentPage + 1)}
        >
          Next
        </button>
      </div>
    </nav>
  );
}

function AtlasHero() {
  return (
    <header className="atlas-hero">
      <p className="eyebrow">A source-backed territory of thinking tools</p>
      <h1>
        See the landscape.
        <span>Follow one exact relation.</span>
      </h1>
      <p>
        Explore canonical mental models without turning graph position, connection
        count, or confidence into authority.
      </p>
    </header>
  );
}
