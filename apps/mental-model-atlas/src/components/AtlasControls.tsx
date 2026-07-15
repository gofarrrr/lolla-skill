import type { DurableAtlasState, RelationType } from "../atlasState";
import { RELATION_TYPES } from "../atlasState";
import { FIXTURES, type FixtureId } from "../projection";
import type { RendererKind } from "./GraphSurface";

export function AtlasControls({
  state,
  fixtureId,
  renderer,
  onStateChange,
  onFixtureChange,
  onRendererChange,
}: {
  state: DurableAtlasState;
  fixtureId: FixtureId;
  renderer: RendererKind;
  onStateChange: (patch: Partial<DurableAtlasState>, replace?: boolean) => void;
  onFixtureChange: (fixture: FixtureId) => void;
  onRendererChange: (renderer: RendererKind) => void;
}) {
  function toggleRelationType(type: RelationType): void {
    const relationTypes = state.relationTypes.includes(type)
      ? state.relationTypes.filter((item) => item !== type)
      : [...state.relationTypes, type];
    onStateChange({ relationTypes, relationPage: 1 });
  }

  return (
    <section className="atlas-controls" aria-label="Atlas controls">
      <label className="search-field">
        <span>Find a model</span>
        <input
          type="search"
          value={state.query}
          placeholder="Name or canonical ID"
          onChange={(event) =>
            onStateChange({ query: event.target.value, relationPage: 1 }, true)
          }
        />
      </label>

      <fieldset className="relation-filter">
        <legend>Relation focus</legend>
        {RELATION_TYPES.map((type) => (
          <label key={type} className={`relation-choice relation-${type}`}>
            <input
              type="checkbox"
              checked={state.relationTypes.includes(type)}
              onChange={() => toggleRelationType(type)}
            />
            <span className="relation-swatch" aria-hidden="true" />
            {type}
          </label>
        ))}
      </fieldset>

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
