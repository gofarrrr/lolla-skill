import type { CardFirstModelPage } from "../cardFirstModelPage";
import { AppLink } from "../router";
import { humanize } from "./StatusDisclosure";

const COMPLETE_RELATION_ID = "abstraction__first-principles-thinking__ally";

export function ModelConnections({
  connections,
}: {
  connections: CardFirstModelPage["connections"];
}) {
  return (
    <section className="derived-layer connections-layer" aria-labelledby="connections-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">Layer 3 · separate relationship curation</p>
          <h2 id="connections-title">Curated relationship-graph connections</h2>
        </div>
        <p>{connections.description}</p>
      </header>

      <div className="connection-counts" aria-label="Exact relationship counts">
        <span><strong>{connections.outgoing_count}</strong> outgoing</span>
        <span><strong>{connections.incoming_count}</strong> incoming</span>
        <span><strong>{connections.relation_type_counts.ally}</strong> allies</span>
        <span><strong>{connections.relation_type_counts.antagonist}</strong> antagonist</span>
        <span><strong>{connections.relation_type_counts.tension}</strong> tensions</span>
        <span><strong>{connections.omitted_record_count}</strong> records omitted</span>
      </div>

      <ul className="model-connections-list">
        {connections.records.map((relation) => (
          <li className={`model-connection relation-${relation.relation_type}`} key={relation.relation_id}>
            <div className="connection-title-row">
              <span className="relation-mark" aria-hidden="true" />
              <p>
                <strong>{humanize(relation.source_model_id)}</strong>
                <span aria-label="directed to"> → </span>
                <strong>{humanize(relation.target_model_id)}</strong>
              </p>
              <span>{relation.relation_type}</span>
            </div>
            <p>{relation.summary}</p>
            <dl className="connection-custody">
              <div><dt>Relative to Abstraction</dt><dd>{humanize(relation.focus_direction)}</dd></div>
              <div><dt>Authored direction</dt><dd>{humanize(relation.direction)}</dd></div>
              <div><dt>Confidence</dt><dd>{humanize(relation.confidence)} — not certification</dd></div>
              <div><dt>Source record</dt><dd><code>/{relation.source_record_index}</code></dd></div>
            </dl>
            {relation.relation_id === COMPLETE_RELATION_ID ? (
              <AppLink className="text-link" href={`/relations/${relation.relation_id}`}>
                Read complete relation page
              </AppLink>
            ) : null}
          </li>
        ))}
      </ul>

      <div className="connections-footer">
        <p>
          {connections.shown_record_count} of {connections.eligible_record_count} exact incident records shown.
          None are hidden, ranked, or merged. Raw relationship fields are intentionally
          projected only partially; affinity is not used as importance or visual weight.
        </p>
        <AppLink className="button" href="/atlas?model=abstraction">
          Explore Abstraction in the graph
        </AppLink>
      </div>
    </section>
  );
}
