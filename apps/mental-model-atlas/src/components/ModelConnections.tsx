import { useState } from "react";

import type { CardFirstModelPage, CardFirstRelation } from "../cardFirstModelPage";
import {
  LEARNING_RELATION_ORDER,
  RELATION_PRESENTATION,
} from "../relationPresentation";
import { AppLink } from "../router";
import { humanize } from "./StatusDisclosure";

const COMPLETE_RELATION_ID = "abstraction__first-principles-thinking__ally";
const GROUPS = LEARNING_RELATION_ORDER.map((id) => ({
  id,
  canonicalLabel: RELATION_PRESENTATION[id].canonicalLabel,
  label: RELATION_PRESENTATION[id].humanLabel,
  lineLabel: RELATION_PRESENTATION[id].lineLabel,
  explanation: RELATION_PRESENTATION[id].explanation,
}));

export function ModelConnections({
  connections,
}: {
  connections: CardFirstModelPage["connections"];
}) {
  const [activeGroup, setActiveGroup] = useState<(typeof GROUPS)[number]["id"]>("ally");
  const [selectedRelationId, setSelectedRelationId] = useState(
    () => connections.records.find((record) => record.relation_type === "ally")?.relation_id ?? "",
  );

  function selectGroup(groupId: (typeof GROUPS)[number]["id"]) {
    const firstRecord = connections.records.find((record) => record.relation_type === groupId);
    setActiveGroup(groupId);
    if (firstRecord) setSelectedRelationId(firstRecord.relation_id);
  }

  function moveBetweenGroups(currentIndex: number, key: string) {
    const delta = key === "ArrowRight" || key === "ArrowDown"
      ? 1
      : key === "ArrowLeft" || key === "ArrowUp"
        ? -1
        : 0;
    if (!delta) return;
    const nextIndex = (currentIndex + delta + GROUPS.length) % GROUPS.length;
    const nextGroup = GROUPS[nextIndex];
    selectGroup(nextGroup.id);
    requestAnimationFrame(() => document.getElementById(`connection-tab-${nextGroup.id}`)?.focus());
  }

  return (
    <section className="derived-layer connections-layer" id="model-relations" aria-labelledby="connections-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">Relationship map</p>
          <h2 id="connections-title">Read the lines around Abstraction</h2>
        </div>
        <p>
          See which ideas reinforce Abstraction, expose a tradeoff, or push against it.
          Line form and direction carry the meaning.
        </p>
      </header>

      <div className="connection-explorer">
        <p className="connection-summary">
          {connections.shown_record_count} authored connections · {connections.outgoing_count} from Abstraction · {connections.incoming_count} toward it
        </p>

        <details className="relationship-grammar">
          <summary>How to read the line styles</summary>
          <ul>
            {GROUPS.map((group) => (
              <li key={group.id}>
                <strong>{group.canonicalLabel} · {group.label}</strong> — {group.lineLabel}
              </li>
            ))}
          </ul>
        </details>

        <div className="connection-group-tabs" role="tablist" aria-label="Connection types">
          {GROUPS.map((group, groupIndex) => (
            <button
              type="button"
              role="tab"
              className={`relation-${group.id}`}
              data-relation-type={group.id}
              aria-selected={activeGroup === group.id}
              aria-controls={`connection-panel-${group.id}`}
              id={`connection-tab-${group.id}`}
              key={group.id}
              onClick={() => selectGroup(group.id)}
              onKeyDown={(event) => {
                if (event.key.startsWith("Arrow")) {
                  event.preventDefault();
                  moveBetweenGroups(groupIndex, event.key);
                }
              }}
              tabIndex={activeGroup === group.id ? 0 : -1}
            >
              <span className="connection-tab-line" aria-hidden="true" />
              <strong>{connections.relation_type_counts[group.id]}</strong>
              <span>{group.canonicalLabel} · {group.label}</span>
            </button>
          ))}
        </div>

        <p className="relationship-nonclaim">
          These authored relations are not scores, recommendations, or proof that a model applies here.
        </p>

        {GROUPS.map((group) => {
          const records = connections.records.filter((record) => record.relation_type === group.id);
          const selectedRelation = records.find((record) => record.relation_id === selectedRelationId) ?? records[0];
          return (
            <section
              id={`connection-panel-${group.id}`}
              aria-labelledby={`connection-tab-${group.id}`}
              data-relation-type={group.id}
              hidden={activeGroup !== group.id}
              className="connection-group-panel"
              key={group.id}
              role="tabpanel"
              tabIndex={0}
            >
              <header>
                <h3>{group.canonicalLabel} · {group.label}</h3>
                <p>{group.explanation} Choose one row to inspect its meaning and authored direction.</p>
              </header>
              <div className="relationship-workspace">
                <ul className="model-connections-list" aria-label={`${group.label} relationship records`}>
                  {records.map((relation) => (
                    <ConnectionRow
                      isSelected={relation.relation_id === selectedRelation.relation_id}
                      key={relation.relation_id}
                      onSelect={() => setSelectedRelationId(relation.relation_id)}
                      relation={relation}
                      targetId={`connection-detail-${group.id}`}
                    />
                  ))}
                </ul>
                <ConnectionDetail id={`connection-detail-${group.id}`} relation={selectedRelation} />
              </div>
            </section>
          );
        })}
      </div>

      <div className="connections-footer">
        <p>
          All {connections.shown_record_count} exact records remain available across the
          three views. Parallel relationships stay separate: the same pair may cooperate
          in one respect and remain in tension in another.
        </p>
        <AppLink className="button" href="/atlas?model=abstraction">
          Explore the full graph
        </AppLink>
      </div>
    </section>
  );
}

function ConnectionRow({
  isSelected,
  onSelect,
  relation,
  targetId,
}: {
  isSelected: boolean;
  onSelect: () => void;
  relation: CardFirstRelation;
  targetId: string;
}) {
  const otherModel = relation.focus_direction === "outgoing"
    ? humanize(relation.target_model_id)
    : humanize(relation.source_model_id);
  const directionCopy = relation.focus_direction === "outgoing"
    ? "Abstraction → model"
    : "Model → Abstraction";
  return (
    <li
      className={`model-connection relation-${relation.relation_type}`}
      data-focus-direction={relation.focus_direction}
      data-relation-type={relation.relation_type}
    >
      <button
        type="button"
        aria-controls={targetId}
        aria-expanded={isSelected}
        aria-pressed={isSelected}
        onClick={onSelect}
      >
        <span className="relation-row-mark" aria-hidden="true" />
        <span><strong>{otherModel}</strong><small>{directionCopy}</small></span>
        <span>{humanize(relation.relation_type)}</span>
      </button>
    </li>
  );
}

function ConnectionDetail({ id, relation }: { id: string; relation: CardFirstRelation }) {
  const sourceModel = humanize(relation.source_model_id);
  const targetModel = humanize(relation.target_model_id);
  const otherModel = relation.focus_direction === "outgoing" ? targetModel : sourceModel;
  const directionCopy = relation.focus_direction === "outgoing"
    ? "Abstraction points to"
    : "Points to Abstraction";
  const relationCopy = relation.relation_type === "ally"
    ? "works with"
    : relation.relation_type === "tension"
      ? "stays in productive tension with"
      : "pushes against";
  return (
    <article className={`relationship-detail relation-${relation.relation_type}`} id={id}>
      <p className="eyebrow">Selected relationship</p>
      <div
        className="relationship-path"
        aria-label={`Authored relationship: ${sourceModel} ${relationCopy} ${targetModel}`}
      >
        <div className={`relationship-node ${relation.source_model_id === "abstraction" ? "is-focus-model" : ""}`}>
          <span>From</span>
          <strong>{sourceModel}</strong>
        </div>
        <div className="relationship-connector">
          <span className="relationship-line" aria-hidden="true"><i /></span>
          <span>{relation.relation_type === "ally" ? "ally" : relation.relation_type}</span>
        </div>
        <div className={`relationship-node ${relation.target_model_id === "abstraction" ? "is-focus-model" : ""}`}>
          <span>To</span>
          <strong>{targetModel}</strong>
        </div>
      </div>
      <div className="connection-reading">
        <div className="connection-title-row">
          <div>
            <span className="connection-direction">{directionCopy}</span>
            <h4>{otherModel}</h4>
          </div>
          <span>{relation.relation_type}</span>
        </div>
        <p>{relation.summary}</p>
        {relation.relation_id === COMPLETE_RELATION_ID ? (
          <AppLink className="text-link" href={`/relations/${relation.relation_id}`}>
            Read this relationship in depth
          </AppLink>
        ) : null}
      </div>
    </article>
  );
}
