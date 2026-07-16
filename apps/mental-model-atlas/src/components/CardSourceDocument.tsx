import { Fragment, useEffect, useRef, useState, type ReactNode } from "react";

import type {
  CardFirstModelPage,
  CardLineMapEntry,
  ReaderChapter,
} from "../cardFirstModelPage";

type SourceCard = CardFirstModelPage["source_card"];

export function CardSourceDocument({ sourceCard }: { sourceCard: SourceCard }) {
  const lines = sourceCard.source_text.slice(0, -1).split("\n");
  const projection = sourceCard.reader_projection;
  const [activeChapterId, setActiveChapterId] = useState<string>(projection.default_chapter_id);
  const [readerMode, setReaderMode] = useState<"guided" | "full">("guided");
  const chapterStartRef = useRef<HTMLDivElement>(null);
  const shouldOrientRef = useRef(false);
  const activeIndex = projection.chapters.findIndex(
    (chapter) => chapter.chapter_id === activeChapterId,
  );
  const activeChapter = projection.chapters[activeIndex];

  useEffect(() => {
    if (!shouldOrientRef.current) return;
    shouldOrientRef.current = false;
    chapterStartRef.current?.scrollIntoView?.({ block: "start", behavior: "auto" });
  }, [activeChapterId]);

  function selectChapter(chapterId: string) {
    if (chapterId === activeChapterId && readerMode === "guided") return;
    shouldOrientRef.current = true;
    setReaderMode("guided");
    setActiveChapterId(chapterId);
  }

  return (
    <div className="guided-reader" id="guided-reader-start">
      <nav className="reader-journey-nav" aria-label="Guided model chapters">
        <div className="reader-progress-copy" aria-live="polite">
          <p className="eyebrow">Your place in the model</p>
          <strong>{readerMode === "guided" ? `Step ${activeChapter.step} of ${projection.chapters.length}` : "Complete source view"}</strong>
          <span>{readerMode === "guided" ? activeChapter.navigation_label : "All five chapters"}</span>
        </div>
        <ol>
          {projection.chapters.map((chapter) => {
            const isActive = chapter.chapter_id === activeChapterId;
            return (
              <li key={chapter.chapter_id}>
                <button
                  type="button"
                  className={isActive ? "is-active" : undefined}
                  aria-current={isActive ? "step" : undefined}
                  aria-controls={`reader-chapter-${chapter.chapter_id}`}
                  onClick={() => selectChapter(chapter.chapter_id)}
                >
                  <span>{chapter.step}</span>
                  {chapter.navigation_label}
                </button>
              </li>
            );
          })}
        </ol>
        <button
          type="button"
          className="reader-source-mode"
          aria-pressed={readerMode === "full"}
          onClick={() => setReaderMode(readerMode === "guided" ? "full" : "guided")}
        >
          {readerMode === "guided" ? "View exact source as one document" : "Return to guided reading"}
        </button>
      </nav>

      <div className={`reader-stage ${readerMode === "full" ? "is-full-source" : ""}`} ref={chapterStartRef}>
        <div className="reader-stage-orientation">
          <p className="eyebrow">{readerMode === "guided" ? `Step ${activeChapter.step} of ${projection.chapters.length}` : "Source inspection mode"}</p>
          <p>{readerMode === "guided" ? activeChapter.orientation : "All original learning chapters are open in source order for search, copy, print, and audit."}</p>
        </div>

        {projection.chapters.slice(0, 4).map((chapter) => (
          <ReaderChapterPanel
            key={chapter.chapter_id}
            chapter={chapter}
            isActive={readerMode === "full" || chapter.chapter_id === activeChapterId}
            lineMap={sourceCard.line_map}
            lines={lines}
          />
        ))}

        <details
          className="source-curation-appendix"
          hidden={readerMode !== "full" && activeChapterId !== "connect"}
          open={readerMode === "full" ? true : undefined}
        >
          <summary>{projection.source_appendix.label}</summary>
          <p>{projection.source_appendix.reason}</p>
          <div className="source-card source-card-technical">
            <SourceCardNodes
              lineMap={sourceCard.line_map}
              lines={lines}
              startLine={projection.source_appendix.start_line}
              endLine={projection.source_appendix.end_line}
            />
          </div>
        </details>

        {projection.chapters.slice(4).map((chapter) => (
          <ReaderChapterPanel
            key={chapter.chapter_id}
            chapter={chapter}
            isActive={readerMode === "full" || chapter.chapter_id === activeChapterId}
            lineMap={sourceCard.line_map}
            lines={lines}
          />
        ))}

        {readerMode === "guided" ? <div className="reader-chapter-actions">
          <button
            type="button"
            className="button secondary"
            disabled={activeIndex === 0}
            onClick={() => selectChapter(projection.chapters[activeIndex - 1].chapter_id)}
          >
            Previous step
          </button>
          <p>{chapterBridge(activeChapter)}</p>
          <button
            type="button"
            className="button"
            disabled={activeIndex === projection.chapters.length - 1}
            onClick={() => selectChapter(projection.chapters[activeIndex + 1].chapter_id)}
          >
            Next step
          </button>
        </div> : null}
      </div>
    </div>
  );
}

function chapterBridge(chapter: ReaderChapter): string {
  if (chapter.chapter_id === "connect") {
    return "After the source journey, explore the exact connection neighborhood below.";
  }
  if (chapter.chapter_id === "apply-safely") {
    return "You have completed the source journey. Continue into practical guidance when ready.";
  }
  return "Continue when this chapter feels clear.";
}

function ReaderChapterPanel({
  chapter,
  isActive,
  lineMap,
  lines,
}: {
  chapter: ReaderChapter;
  isActive: boolean;
  lineMap: CardLineMapEntry[];
  lines: string[];
}) {
  return (
    <section
      className="reader-chapter"
      id={`reader-chapter-${chapter.chapter_id}`}
      aria-labelledby={`source-line-${chapter.heading_line}`}
      hidden={!isActive}
    >
      <article className="source-card" aria-label={`${chapter.navigation_label} source chapter`}>
        <SourceCardNodes
          lineMap={lineMap}
          lines={lines}
          startLine={chapter.start_line}
          endLine={chapter.end_line}
        />
      </article>
    </section>
  );
}

function SourceCardNodes({
  lineMap,
  lines,
  startLine,
  endLine,
}: {
  lineMap: CardLineMapEntry[];
  lines: string[];
  startLine: number;
  endLine: number;
}) {
  const boundedLineMap = lineMap.filter(
    (entry) => entry.line_number >= startLine && entry.line_number <= endLine,
  );
  const nodes: ReactNode[] = [];
  let index = 0;
  while (index < boundedLineMap.length) {
    const entry = boundedLineMap[index];
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
      while (scan < boundedLineMap.length) {
        const candidate = boundedLineMap[scan];
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
      while (scan < boundedLineMap.length) {
        const candidate = boundedLineMap[scan];
        if (candidate.kind === "table_delimiter") {
          scan += 1;
          continue;
        }
        if (candidate.kind !== "table_text_row") break;
        rows.push({ entry: candidate, cells: splitTableLine(lines[candidate.line_number - 1]) });
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
