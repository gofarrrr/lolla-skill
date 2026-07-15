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
            <dt>Direction</dt>
            <dd>{humanize(relation.direction)}</dd>
          </div>
          <div>
            <dt>Reciprocal</dt>
            <dd>{relation.is_reciprocal ? "Explicitly yes" : "No"}</dd>
          </div>
          <div>
            <dt>Confidence</dt>
            <dd>
              {relation.confidence === "medium"
                ? "Medium — stronger caution: inspect the source; this is not certification"
                : "High — still not certification"}
            </dd>
          </div>
          <div>
            <dt>Curation</dt>
            <dd>{humanize(relation.curation_status)}</dd>
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
        <p className="canonical-id">{model.model_id}</p>
        <h2>{model.display_name}</h2>
        <p className="panel-summary">{model.summary.text}</p>
        <p className="helps-notice">
          <strong>Helps you notice</strong>
          {model.helps_notice.text}
        </p>
        <p className="count-scope">Loaded relation records on this page</p>
        <div className="count-cluster" aria-label="Loaded incident relation counts on this page">
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
        <dl className="compact-facts">
          <div>
            <dt>Source</dt>
            <dd>{humanize(model.status.source)}</dd>
          </div>
          <div>
            <dt>Human review</dt>
            <dd>{humanize(model.status.human_review)}</dd>
          </div>
          <div>
            <dt>Publication</dt>
            <dd>{humanize(model.status.publication)}</dd>
          </div>
        </dl>
        <AppLink className="button panel-action" href={`/models/${model.slug}`}>
          Open full model page
        </AppLink>
      </aside>
    );
  }

  return (
    <aside className="selection-panel idle-panel" aria-label="Atlas orientation">
      <p className="eyebrow">No semantic focus selected</p>
      <h2>See the territory, then choose one exact object.</h2>
      <p>
        Node position is a stable navigation layout. It does not mean importance,
        relevance, correctness, or mastery. Idle view draws no relation edges.
      </p>
      <ul className="legend-list">
        <li className="relation-ally">Ally — supportive or complementary</li>
        <li className="relation-antagonist">Antagonist — counteracting or opposed</li>
        <li className="relation-tension">Tension — a productive tradeoff or boundary</li>
      </ul>
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
      <p>Preview — selection unchanged</p>
      <strong>{model.display_name}</strong>
      <span>{model.summary.text}</span>
      <span>{model.model_id}</span>
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
