import type { CardFirstModelPage, OperationalMetadataRecord } from "../cardFirstModelPage";

export function OperationalModelSummary({
  operational,
}: {
  operational: CardFirstModelPage["operational_curation"];
}) {
  const record = operational.record;
  return (
    <section className="derived-layer operational-layer" aria-labelledby="operational-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">Layer 2 · separate compiled curation</p>
          <h2 id="operational-title">Operational guidance — compiled knowledge graph</h2>
        </div>
        <p>{operational.description}</p>
      </header>
      <div className="layer-coverage-note" role="note">
        <strong>Complete record, different authority.</strong> All {operational.field_coverage.source_field_count} checked-in fields are present. They do not replace or rewrite the Markdown card.
      </div>
      <div className="operational-grid">
        <OperationalList title="Use when" items={record.select_when} />
        <OperationalList title="Avoid or constrain when" items={record.danger_when} />
        <section className="operational-card">
          <p className="section-number">Compiled graph fields</p>
          <h3>Reasoning profile</h3>
          <dl className="compact-facts">
            <div><dt>Input</dt><dd>{record.input_type}</dd></div>
            <div><dt>Output</dt><dd>{record.output_type}</dd></div>
            <div><dt>Types</dt><dd>{record.reasoning_types.join(", ")}</dd></div>
            <div><dt>Record name</dt><dd>{record.name}</dd></div>
            <div><dt>Display name</dt><dd>{record.display_name}</dd></div>
            <div><dt>Slug</dt><dd><code>{record.slug}</code></dd></div>
            <div><dt>Source-file locator</dt><dd><code>{record.source_file}</code></dd></div>
          </dl>
        </section>
        <MetadataList title="Premortem questions" items={record.premortem_questions} />
        <MetadataList title="Practical heuristics" items={record.heuristics} />
        <section className="operational-card operational-card-wide">
          <p className="section-number">Compiled curation</p>
          <h3>Failure modes and mitigations</h3>
          <ul className="failure-mode-list">
            {record.failure_modes.map((item) => (
              <li key={item.mode}>
                <h4>{item.mode}</h4>
                <p>{item.description}</p>
                <p><strong>Mitigation:</strong> {item.mitigation}</p>
                <SourceMetadata item={item} />
              </li>
            ))}
          </ul>
        </section>
      </div>
    </section>
  );
}

function OperationalList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="operational-card">
      <p className="section-number">Compiled curation</p>
      <h3>{title}</h3>
      <ul>{items.map((item, index) => <li key={index}>{item}</li>)}</ul>
    </section>
  );
}

function MetadataList({ title, items }: { title: string; items: OperationalMetadataRecord[] }) {
  return (
    <section className="operational-card">
      <p className="section-number">Compiled curation</p>
      <h3>{title}</h3>
      <ul className="metadata-record-list">
        {items.map((item, index) => (
          <li key={index}>
            <p>{item.description}</p>
            <SourceMetadata item={item} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function SourceMetadata({ item }: { item: OperationalMetadataRecord }) {
  return (
    <details className="compiled-source-detail">
      <summary>{item.extraction_type} · {item.confidence} confidence</summary>
      <blockquote>{item.source_quote}</blockquote>
    </details>
  );
}
