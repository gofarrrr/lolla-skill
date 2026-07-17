import { relationCounts, type AtlasSelection } from "../atlasSelectors";
import type { AtlasProjection } from "../projection";
import { AppLink } from "../router";
import { humanize } from "./StatusDisclosure";

export function SelectionPanel({
  projection,
  selection,
  onClear,
}: {
  projection: AtlasProjection;
  selection: AtlasSelection;
  onClear: () => void;
}) {
  const modelNames = new Map(
    projection.models.map((model) => [model.model_id, model.display_name]),
  );
  if (selection.selectedIdMissing) {
    return (
      <aside className="selection-panel missing-selection" role="alert">
        <p className="eyebrow">Unknown stable ID</p>
        <h2>This selection is not in the loaded projection.</h2>
        <p>
          The Atlas will not repair an unknown model or relation ID into a nearby
          identity.
        </p>
        <button type="button" onClick={onClear}>
          Clear unknown selection
        </button>
      </aside>
    );
  }

  if (selection.selectedRelation) {
    const relation = selection.selectedRelation;
    return (
      <aside className="selection-panel" aria-label="Selected relation">
        <PanelHeader label="Selected relation" onClear={onClear} />
        <p className={`relation-kicker relation-${relation.relation_type}`}>
          <span aria-hidden="true" /> {relation.relation_type}
        </p>
        <h2>
          {modelNames.get(relation.source_model_id) ?? relation.source_model_id}
          <span className="direction-arrow" aria-label="directed to">
            →
          </span>
          {modelNames.get(relation.target_model_id) ?? relation.target_model_id}
        </h2>
        <p className="panel-summary">{relation.summary}</p>
        <dl className="compact-facts">
          <div>
            <dt>Relationship direction</dt>
            <dd>{humanize(relation.direction)}</dd>
          </div>
          <div>
            <dt>Two-way</dt>
            <dd>{relation.is_reciprocal ? "Explicitly yes" : "No"}</dd>
          </div>
        </dl>
        <AppLink
          className="button panel-action"
          href={`/relations/${encodeURIComponent(relation.relation_id)}`}
        >
          Open full relation page
        </AppLink>
      </aside>
    );
  }

  if (selection.selectedModel) {
    const model = selection.selectedModel;
    const counts = relationCounts(projection.relations, model.model_id);
    return (
      <aside className="selection-panel" aria-label="Selected model">
        <PanelHeader label="Selected model" onClear={onClear} />
        <h2>{model.display_name}</h2>
        <p className="panel-summary">{model.summary.text}</p>
        <p className="helps-notice">
          <strong>Helps you notice</strong>
          {model.helps_notice.text}
        </p>
        <p className="count-scope">Connections in this view</p>
        <div className="count-cluster" aria-label="Connection counts in this view">
          <span>
            <strong>{counts.ally}</strong> allies
          </span>
          <span>
            <strong>{counts.antagonist}</strong> antagonists
          </span>
          <span>
            <strong>{counts.tension}</strong> tensions
          </span>
        </div>
        <AppLink className="button panel-action" href={`/models/${model.slug}`}>
          Open full model page
        </AppLink>
      </aside>
    );
  }

  return (
    <aside className="selection-panel idle-panel" aria-label="Atlas orientation">
      <p className="eyebrow">Start anywhere</p>
      <h2>Choose one model to reveal its neighborhood.</h2>
      <p>
        Position helps you navigate; it is not a ranking. Select a model to see the
        ideas that support it, challenge it, or create a useful tradeoff.
      </p>
    </aside>
  );
}

export function HoverPreview({ selection }: { selection: AtlasSelection }) {
  const model = selection.hoveredModel;
  if (!model || model.model_id === selection.selectedModel?.model_id) {
    return null;
  }
  return (
    <div className="hover-preview" aria-live="polite">
      <p>Preview</p>
      <strong>{model.display_name}</strong>
      <span>{model.summary.text}</span>
    </div>
  );
}

function PanelHeader({ label, onClear }: { label: string; onClear: () => void }) {
  return (
    <div className="panel-header">
      <p className="eyebrow">{label}</p>
      <button className="clear-selection" type="button" onClick={onClear}>
        Clear
      </button>
    </div>
  );
}
