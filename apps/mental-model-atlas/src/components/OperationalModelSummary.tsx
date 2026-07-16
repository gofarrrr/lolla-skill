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
                  </li>
                ))}
              </ul>
            </section>
          </div>
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
      <p className="section-number">Practical prompt</p>
      <h3>{title}</h3>
      <ul className="metadata-record-list">
        {items.map((item, index) => (
          <li key={index}>
            <p>{item.description}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
