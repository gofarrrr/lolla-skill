import { Fragment, type ReactNode } from "react";

import type {
  CardFirstModelPage,
  CardLineMapEntry,
} from "../cardFirstModelPage";

type SourceCard = CardFirstModelPage["source_card"];

export function CardSourceDocument({ sourceCard }: { sourceCard: SourceCard }) {
  const lines = sourceCard.source_text.slice(0, -1).split("\n");
  const headings = sourceCard.line_map.filter(
    (entry) => entry.kind === "heading",
  );

  return (
    <div className="card-document-layout">
      <nav className="card-contents" aria-label="Model card contents">
        <p className="eyebrow">In this source card</p>
        <ol>
          {headings.map((entry) => (
            <li className={`toc-level-${entry.heading_level}`} key={entry.line_number}>
              <a href={`#source-line-${entry.line_number}`}>
                {trimHeading(lines[entry.line_number - 1])}
              </a>
            </li>
          ))}
        </ol>
        <dl className="coverage-mini-facts">
          <div><dt>Source words</dt><dd>{sourceCard.coverage.word_count.toLocaleString()}</dd></div>
          <div><dt>Physical lines</dt><dd>{sourceCard.coverage.physical_line_count}</dd></div>
          <div><dt>Substantive omissions</dt><dd>{sourceCard.coverage.omitted_substantive_line_count}</dd></div>
        </dl>
      </nav>

      <article className="source-card" aria-label="Complete canonical Abstraction card">
        <SourceCardNodes lineMap={sourceCard.line_map} lines={lines} />
      </article>
    </div>
  );
}

function SourceCardNodes({
  lineMap,
  lines,
}: {
  lineMap: CardLineMapEntry[];
  lines: string[];
}) {
  const nodes: ReactNode[] = [];
  let index = 0;
  while (index < lineMap.length) {
    const entry = lineMap[index];
    const line = lines[entry.line_number - 1];
    if (entry.kind === "title" || entry.kind === "blank" || entry.kind === "table_delimiter") {
      index += 1;
      continue;
    }
    if (entry.kind === "horizontal_rule") {
      nodes.push(<hr data-source-structure-line={entry.line_number} key={entry.line_number} />);
      index += 1;
      continue;
    }
    if (entry.kind === "heading") {
      const content = <InlineSourceText text={line} />;
      nodes.push(
        entry.heading_level === 2 ? (
          <h2 data-source-line={entry.line_number} id={`source-line-${entry.line_number}`} key={entry.line_number}>{content}</h2>
        ) : (
          <h3 data-source-line={entry.line_number} id={`source-line-${entry.line_number}`} key={entry.line_number}>{content}</h3>
        ),
      );
      index += 1;
      continue;
    }
    if (entry.kind === "paragraph") {
      nodes.push(<p data-source-line={entry.line_number} key={entry.line_number}><InlineSourceText text={line} /></p>);
      index += 1;
      continue;
    }
    if (entry.kind === "ordered_list_item" || entry.kind === "unordered_list_item") {
      const kind = entry.kind;
      const items: Array<{ entry: CardLineMapEntry; line: string }> = [];
      let scan = index;
      while (scan < lineMap.length) {
        const candidate = lineMap[scan];
        if (candidate.kind === "blank") {
          scan += 1;
          continue;
        }
        if (candidate.kind !== kind) break;
        items.push({ entry: candidate, line: lines[candidate.line_number - 1] });
        scan += 1;
      }
      const renderedItems = items.map((item) => (
        <li data-source-line={item.entry.line_number} key={item.entry.line_number}>
          <InlineSourceText text={stripListMarker(item.line, kind)} />
        </li>
      ));
      nodes.push(
        kind === "ordered_list_item" ? (
          <ol className="source-card-list" key={`list-${entry.line_number}`}>{renderedItems}</ol>
        ) : (
          <ul className="source-card-list" key={`list-${entry.line_number}`}>{renderedItems}</ul>
        ),
      );
      index = scan;
      continue;
    }
    if (entry.kind === "table_text_row") {
      const rows: Array<{ entry: CardLineMapEntry; cells: string[] }> = [];
      let scan = index;
      while (scan < lineMap.length) {
        const candidate = lineMap[scan];
        if (candidate.kind === "table_delimiter") {
          scan += 1;
          continue;
        }
        if (candidate.kind !== "table_text_row") break;
        rows.push({
          entry: candidate,
          cells: splitTableLine(lines[candidate.line_number - 1]),
        });
        scan += 1;
      }
      const [header, ...body] = rows;
      nodes.push(
        <Fragment key={`table-${entry.line_number}`}>
          <p className="source-table-scroll-cue" id="source-table-scroll-cue">
            Scroll horizontally to read every column <span aria-hidden="true">→</span>
          </p>
          <div className="source-table-wrap" role="region" aria-label="Risks and mitigations table" aria-describedby="source-table-scroll-cue" tabIndex={0}>
            <table className="source-card-table">
              <thead><tr data-source-line={header.entry.line_number}>{header.cells.map((cell, cellIndex) => <th key={cellIndex} scope="col"><InlineSourceText text={cell} /></th>)}</tr></thead>
              <tbody>{body.map((row) => (
                <tr data-source-line={row.entry.line_number} key={row.entry.line_number}>
                  {row.cells.map((cell, cellIndex) => cellIndex === 0
                    ? <th key={cellIndex} scope="row"><InlineSourceText text={cell} /></th>
                    : <td key={cellIndex}><InlineSourceText text={cell} /></td>)}
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Fragment>,
      );
      index = scan;
      continue;
    }
    index += 1;
  }
  return <>{nodes}</>;
}

export function InlineSourceText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return <>{parts.map((part, index): ReactNode =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={index}>{part.slice(2, -2)}</strong>
      : <Fragment key={index}>{part}</Fragment>,
  )}</>;
}

function stripListMarker(line: string, kind: CardLineMapEntry["kind"]): string {
  return kind === "ordered_list_item"
    ? line.replace(/^\s*\d+\.\s+/, "")
    : line.replace(/^\s*(?:•|-|\*)\s+/, "");
}

function splitTableLine(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function trimHeading(value: string): string {
  return value.replace(/:$/, "");
}
