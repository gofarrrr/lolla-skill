import type { DurableAtlasState } from "../atlasState";
import {
  FIXTURES,
  type AtlasModelRecord,
  type FixtureId,
} from "../projection";
import type { RendererKind } from "./GraphSurface";

export function AtlasControls({
  state,
  fixtureId,
  renderer,
  models,
  matchingModels,
  onStateChange,
  onSelectModel,
  onFixtureChange,
  onRendererChange,
  showPrototypeControls = false,
}: {
  state: DurableAtlasState;
  fixtureId: FixtureId;
  renderer: RendererKind;
  models: AtlasModelRecord[];
  matchingModels: AtlasModelRecord[];
  onStateChange: (patch: Partial<DurableAtlasState>, replace?: boolean) => void;
  onSelectModel: (modelId: string) => void;
  onFixtureChange: (fixture: FixtureId) => void;
  onRendererChange: (renderer: RendererKind) => void;
  showPrototypeControls?: boolean;
}) {
  const starterModels = models.slice(0, 4);
  const searchResults = state.query ? matchingModels.slice(0, 6) : [];

  function selectSearchResult(modelId: string): void {
    onSelectModel(modelId);
  }

  return (
    <section className="atlas-controls" aria-label="Atlas controls">
      <div className="search-field atlas-search">
        <label htmlFor="atlas-model-search">Find a model</label>
        <input
          id="atlas-model-search"
          type="search"
          role="combobox"
          value={state.query}
          placeholder="Name or idea"
          aria-autocomplete="list"
          aria-controls={state.query ? "atlas-search-results" : undefined}
          aria-expanded={state.query ? true : undefined}
          aria-haspopup="listbox"
          onChange={(event) =>
            onStateChange({ query: event.target.value, relationPage: 1 }, true)
          }
          onKeyDown={(event) => {
            if (event.key !== "Enter" || searchResults.length === 0) return;
            event.preventDefault();
            selectSearchResult(searchResults[0].model_id);
          }}
        />
        {state.query ? (
          <div
            className="atlas-search-results"
            id="atlas-search-results"
            role="listbox"
            aria-label="Matching models"
          >
            {searchResults.length ? (
              searchResults.map((model, index) => (
                <button
                  key={model.model_id}
                  type="button"
                  role="option"
                  aria-selected={index === 0}
                  aria-label={`Select ${model.display_name}`}
                  onClick={() => selectSearchResult(model.model_id)}
                >
                  <strong>{model.display_name}</strong>
                  <span>{index === 0 ? "Press Enter" : "Select"}</span>
                </button>
              ))
            ) : (
              <p role="status">No canonical model matches this search.</p>
            )}
          </div>
        ) : null}
      </div>

      <div className="quick-models" role="group" aria-label="Start with a model">
        <span>Start with a model</span>
        <div>
          {starterModels.map((model) => (
            <button
              key={model.model_id}
              type="button"
              aria-label={`Start with ${model.display_name}`}
              onClick={() => onSelectModel(model.model_id)}
            >
              {model.display_name}
            </button>
          ))}
        </div>
      </div>

      {showPrototypeControls ? (
        <div className="prototype-controls">
          <label className="select-field">
            <span>Review fixture</span>
            <select
              value={fixtureId}
              onChange={(event) => onFixtureChange(event.target.value as FixtureId)}
            >
              {FIXTURES.map((fixture) => (
                <option key={fixture.id} value={fixture.id}>
                  {fixture.label}
                </option>
              ))}
            </select>
          </label>

          <label className="select-field">
            <span>Visual renderer</span>
            <select
              value={renderer}
              onChange={(event) =>
                onRendererChange(event.target.value === "canvas" ? "canvas" : "svg")
              }
            >
              <option value="svg">SVG editorial (default)</option>
              <option value="canvas">Canvas 2D comparison</option>
            </select>
          </label>
        </div>
      ) : null}

      <div className="segmented-control" aria-label="Atlas presentation">
        <button
          type="button"
          aria-pressed={state.view === "graph"}
          onClick={() => onStateChange({ view: "graph" })}
        >
          Visual map
        </button>
        <button
          type="button"
          aria-pressed={state.view === "list"}
          onClick={() => onStateChange({ view: "list" })}
        >
          Text atlas
        </button>
      </div>
    </section>
  );
}
