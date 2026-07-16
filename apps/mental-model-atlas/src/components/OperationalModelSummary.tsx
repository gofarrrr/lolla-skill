import type { CardFirstModelPage, OperationalMetadataRecord } from "../cardFirstModelPage";

export function OperationalModelSummary({
  operational,
}: {
  operational: CardFirstModelPage["operational_curation"];
}) {
  const record = operational.record;
  return (
    <section className="derived-layer operational-layer" id="model-practice" aria-labelledby="operational-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">After the source · reviewed practical guidance</p>
          <h2 id="operational-title">Put Abstraction to work</h2>
        </div>
        <p>
          Use the model deliberately, notice its failure modes, and keep a route
          back to concrete evidence.
        </p>
      </header>
      <div className="operational-grid">
        <OperationalList title="Use when" items={record.select_when} />
        <OperationalList title="Avoid or constrain when" items={record.danger_when} />
      </div>
      <div className="operational-toolkit">
        <details>
          <summary>Open the practical toolkit</summary>
          <div className="operational-grid">
            <MetadataList title="Premortem questions" items={record.premortem_questions} />
            <MetadataList title="Practical heuristics" items={record.heuristics} />
            <section className="operational-card operational-card-wide">
              <p className="section-number">Guardrails</p>
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
        </details>
        <details className="technical-review-disclosure">
          <summary>How Lolla curates this guidance</summary>
          <p>{operational.description}</p>
          <p>
            All {operational.field_coverage.source_field_count} checked-in fields are present.
            This reviewed curation has different authority from the source article.
          </p>
          <dl className="compact-facts">
            <div><dt>Input</dt><dd>{record.input_type}</dd></div>
            <div><dt>Output</dt><dd>{record.output_type}</dd></div>
            <div><dt>Reasoning types</dt><dd>{record.reasoning_types.join(", ")}</dd></div>
            <div><dt>Record name</dt><dd>{record.name}</dd></div>
            <div><dt>Display name</dt><dd>{record.display_name}</dd></div>
            <div><dt>Slug</dt><dd><code>{record.slug}</code></dd></div>
            <div><dt>Source-file locator</dt><dd><code>{record.source_file}</code></dd></div>
          </dl>
        </details>
      </div>
    </section>
  );
}

function OperationalList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="operational-card">
      <p className="section-number">Reviewed guidance</p>
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
