import { useEffect, useMemo, useState } from "react";

import {
  EMPTY_EPHEMERAL_STATE,
  parseAtlasState,
  type RelationType,
  updateAtlasState,
} from "../atlasState";
import { selectAtlasView } from "../atlasSelectors";
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
  const reviewMode = location.searchParams.get("review") === "1";
  const renderer: RendererKind =
    reviewMode && location.searchParams.get("renderer") === "canvas"
      ? "canvas"
      : "svg";
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
    if (reviewMode) return;
    if (
      !location.searchParams.has("fixture") &&
      !location.searchParams.has("renderer")
    ) return;
    const params = new URLSearchParams(location.searchParams);
    params.delete("fixture");
    params.delete("renderer");
    navigate(`/atlas${params.size ? `?${params.toString()}` : ""}`, {
      replace: true,
    });
  }, [location, reviewMode]);

  useEffect(() => {
    if (projectionState.status !== "ready") {
      return undefined;
    }
    performance.clearMarks("lolla-atlas-useful");
    const frame = requestAnimationFrame(() => {
      performance.mark("lolla-atlas-useful");
    });
    return () => cancelAnimationFrame(frame);
  }, [projectionState.status, projection?.projection_id]);

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
      query: "",
      relationPage: 1,
    });
  }

  function selectRelation(relationId: string): void {
    changeState({ selectedRelationId: relationId });
  }

  function filterToRelationType(type: RelationType): void {
    const alreadyExclusive =
      durableState.relationTypes.length === 1 &&
      durableState.relationTypes[0] === type;
    changeState({
      relationTypes: alreadyExclusive ? [] : [type],
      relationPage: 1,
    });
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

  const scopeText = selection.selectedModel
    ? `${selection.selectedModel.display_name} neighborhood`
    : selection.selectedRelation
      ? "Selected relationship"
      : null;

  return (
    <main id="main" className="atlas-route">
      <AtlasHero />
      <AtlasControls
        state={durableState}
        fixtureId={projectionState.fixtureId}
        renderer={renderer}
        models={projection.models}
        matchingModels={selection.visibleModels}
        onStateChange={changeState}
        onSelectModel={selectModel}
        onFixtureChange={switchFixture}
        onRendererChange={switchRenderer}
        showPrototypeControls={reviewMode}
      />

      <section
        className="atlas-workspace"
        data-motion-paused={motionPaused ? "true" : "false"}
        data-projection-id={projection.projection_id}
        data-coordinate-sha256={projection.layout.coordinate_sha256}
        data-atlas-ready="true"
        aria-label="Mental model Atlas workspace"
      >
        <SelectionPanel
          projection={projection}
          selection={selection}
          activeRelationTypes={durableState.relationTypes}
          onFilterRelationType={filterToRelationType}
          onClear={clearSelection}
        />
        <div className="graph-column">
          {scopeText || reviewMode ? (
            <div className="scope-strip">
              {scopeText ? <p role="status">{scopeText}</p> : <span />}
              {reviewMode ? (
                <span>
                  {renderer === "canvas" ? "Canvas 2D comparison" : "SVG editorial"}
                </span>
              ) : null}
            </div>
          ) : null}

          <PageNavigation
            projection={projection}
            onPageChange={(pageNumber) =>
              changeState({ relationPage: pageNumber })
            }
          />

          {selection.visibleModels.length === 0 ? (
            <div className="graph-zero-state" role="status">
              <span aria-hidden="true">0</span>
              <h2>No models found</h2>
              <p>
                Nothing matches this search. Try a shorter name or clear the filter.
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
              <p className="eyebrow">List view</p>
              <h2>Browse without the map.</h2>
              <p>
                The same models and connections appear below in a simple list.
              </p>
              <a className="button" href="#accessible-atlas">
                Browse the list
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
                motionPaused={motionPaused}
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
  if (
    !["confirmation_bias_hub", "canonical_neighborhood"].includes(
      projection.fixture_id,
    ) ||
    pageCount <= 1
  ) {
    return null;
  }
  const currentPage = projection.page.page_number;
  return (
    <nav className="page-navigation" aria-label="Relation record pages">
      <div>
        <p className="eyebrow">Connections</p>
        <strong>
          Page {currentPage} of {pageCount}
        </strong>
        <span>
          {projection.page.before_count + 1}–
          {projection.page.before_count + projection.page.shown_count} of{" "}
          {projection.page.eligible_count} in this exact source view
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
      <h1>Explore how ideas connect.</h1>
      <p>
        Choose a model or search by name. Its meaning and exact relationships will
        appear here.
      </p>
    </header>
  );
}
