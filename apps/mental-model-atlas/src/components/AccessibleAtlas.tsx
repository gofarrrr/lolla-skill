import { relationCoverageText, type AtlasSelection } from "../atlasSelectors";
import { modelPageUrl, type AtlasProjection } from "../projection";
import { AppLink } from "../router";

export function AccessibleAtlas({
  projection,
  selection,
  onSelectModel,
  onSelectRelation,
}: {
  projection: AtlasProjection;
  selection: AtlasSelection;
  onSelectModel: (modelId: string) => void;
  onSelectRelation: (relationId: string) => void;
}) {
  const modelNames = new Map(
    projection.models.map((model) => [model.model_id, model.display_name]),
  );
  return (
    <section id="accessible-atlas" className="accessible-atlas" aria-labelledby="text-atlas-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Equivalent non-canvas navigation</p>
          <h2 id="text-atlas-title">Models and exact directed relations</h2>
        </div>
        <p>
          {selection.visibleModels.length} of {projection.models.length} models match
          the current text filter.
        </p>
      </div>

      {selection.visibleModels.length === 0 ? (
        <div className="zero-state" role="status">
          <strong>Completed zero</strong>
          <p>
            The projection loaded successfully; the current deterministic text
            filter matches no model.
          </p>
        </div>
      ) : (
        <ul className="semantic-model-list">
          {selection.visibleModels.map((model) => (
            <li key={model.model_id}>
              <button
                type="button"
                aria-pressed={model.model_id === selection.selectedModel?.model_id}
                onClick={() => onSelectModel(model.model_id)}
              >
                <strong>{model.display_name}</strong>
                <span>{model.model_id}</span>
              </button>
              <AppLink
                href={`/models/${model.slug}`}
                aria-label={
                  modelPageUrl(model.slug)
                    ? `Open complete ${model.display_name} page`
                    : `Inspect unavailable page status for ${model.display_name}`
                }
              >
                {modelPageUrl(model.slug) ? "Read" : "Unavailable"}
              </AppLink>
            </li>
          ))}
        </ul>
      )}

      <div className="relation-table-wrap" tabIndex={0}>
        <table>
          <caption>
            {relationCoverageText(selection)} Omission is a presentation bound, not a
            relevance judgment.
          </caption>
          <thead>
            <tr>
              <th scope="col">Source</th>
              <th scope="col">Direction</th>
              <th scope="col">Target</th>
              <th scope="col">Type</th>
              <th scope="col">Open</th>
            </tr>
          </thead>
          <tbody>
            {selection.focusedRelations.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  Select a model or exact relation to reveal its focused records.
                  Idle view intentionally contains zero edges.
                </td>
              </tr>
            ) : (
              selection.focusedRelations.map((relation) => (
                <tr
                  key={relation.relation_id}
                  className={
                    relation.relation_id === selection.selectedRelation?.relation_id
                      ? "is-selected"
                      : undefined
                  }
                >
                  <td>{modelNames.get(relation.source_model_id) ?? relation.source_model_id}</td>
                  <td>
                    <span className="text-arrow" aria-label="directed to">
                      →
                    </span>
                  </td>
                  <td>{modelNames.get(relation.target_model_id) ?? relation.target_model_id}</td>
                  <td>
                    <span className={`type-label relation-${relation.relation_type}`}>
                      {relation.relation_type}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      aria-pressed={
                        relation.relation_id ===
                        selection.selectedRelation?.relation_id
                      }
                      onClick={() => onSelectRelation(relation.relation_id)}
                    >
                      Select
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
