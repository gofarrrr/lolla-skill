import { useState } from "react";

import type { CardFirstModelPage, CardFirstRelation } from "../cardFirstModelPage";
import { AppLink } from "../router";
import { humanize } from "./StatusDisclosure";

const COMPLETE_RELATION_ID = "abstraction__first-principles-thinking__ally";
const GROUPS = [
  { id: "ally", label: "Works with", explanation: "Models that can strengthen or extend abstraction." },
  { id: "tension", label: "Productive tensions", explanation: "Models that challenge abstraction and keep it honest." },
  { id: "antagonist", label: "Direct conflicts", explanation: "Models whose default logic pushes in the opposite direction." },
] as const;

export function ModelConnections({
  connections,
}: {
  connections: CardFirstModelPage["connections"];
}) {
  const [activeGroup, setActiveGroup] = useState<(typeof GROUPS)[number]["id"]>("ally");

  return (
    <section className="derived-layer connections-layer" aria-labelledby="connections-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">Continue learning · exact graph neighborhood</p>
          <h2 id="connections-title">See what Abstraction connects to</h2>
        </div>
        <p>
          Connections are different kinds of intellectual relationships—not a
          ranking of which models matter most.
        </p>
      </header>

      <div className="connection-explorer">
        <div className="connection-group-tabs" aria-label="Connection types">
          {GROUPS.map((group) => (
            <button
              type="button"
              aria-pressed={activeGroup === group.id}
              aria-controls={`connection-panel-${group.id}`}
              id={`connection-tab-${group.id}`}
              key={group.id}
              onClick={() => setActiveGroup(group.id)}
            >
              <strong>{connections.relation_type_counts[group.id]}</strong>
              <span>{group.label}</span>
            </button>
          ))}
        </div>

        {GROUPS.map((group) => {
          const records = connections.records.filter((record) => record.relation_type === group.id);
          return (
            <section
              id={`connection-panel-${group.id}`}
              aria-labelledby={`connection-tab-${group.id}`}
              hidden={activeGroup !== group.id}
              className="connection-group-panel"
              key={group.id}
            >
              <header>
                <h3>{group.label}</h3>
                <p>{group.explanation}</p>
              </header>
              <ul className="model-connections-list">
                {records.map((relation) => <ConnectionCard relation={relation} key={relation.relation_id} />)}
              </ul>
            </section>
          );
        })}
      </div>

      <div className="connections-footer">
        <p>
          All {connections.shown_record_count} exact connections remain available across
          the three views. Parallel relationships stay separate and graph order does not
          imply importance.
        </p>
        <AppLink className="button" href="/atlas?model=abstraction">
          Explore the full graph
        </AppLink>
      </div>
      <details className="technical-review-disclosure connection-set-custody">
        <summary>Connection-set custody and technical fields</summary>
        <p>{connections.description}</p>
        <dl className="connection-custody">
          <div><dt>Outgoing</dt><dd>{connections.outgoing_count}</dd></div>
          <div><dt>Incoming</dt><dd>{connections.incoming_count}</dd></div>
          <div><dt>Exact records</dt><dd>{connections.shown_record_count} of {connections.eligible_record_count}</dd></div>
          <div><dt>Omitted records</dt><dd>{connections.omitted_record_count}</dd></div>
        </dl>
      </details>
    </section>
  );
}

function ConnectionCard({ relation }: { relation: CardFirstRelation }) {
  const otherModel = relation.focus_direction === "outgoing"
    ? relation.target_model_id
    : relation.source_model_id;
  const directionCopy = relation.focus_direction === "outgoing"
    ? "Abstraction points to"
    : "Points to Abstraction";
  return (
    <li className={`model-connection relation-${relation.relation_type}`}>
      <div className="connection-title-row">
        <span className="relation-mark" aria-hidden="true" />
        <div>
          <span className="connection-direction">{directionCopy}</span>
          <h4>{humanize(otherModel)}</h4>
        </div>
        <span>{relation.relation_type}</span>
      </div>
      <p>{relation.summary}</p>
      {relation.relation_id === COMPLETE_RELATION_ID ? (
        <AppLink className="text-link" href={`/relations/${relation.relation_id}`}>
          Read this relationship in depth
        </AppLink>
      ) : null}
      <details className="compiled-source-detail">
        <summary>Direction and record details</summary>
        <dl className="connection-custody">
          <div><dt>Relative to Abstraction</dt><dd>{humanize(relation.focus_direction)}</dd></div>
          <div><dt>Authored direction</dt><dd>{humanize(relation.direction)}</dd></div>
          <div><dt>Confidence</dt><dd>{humanize(relation.confidence)} — not certification</dd></div>
          <div><dt>Source record</dt><dd><code>/{relation.source_record_index}</code></dd></div>
        </dl>
      </details>
    </li>
  );
}
