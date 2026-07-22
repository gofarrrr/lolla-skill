import type {
  AtlasMissingness,
  AtlasPublicationStatus,
  AtlasRelationRecord,
  AtlasSourceRef,
} from "./projection";

export const CARD_FIRST_MODEL_PAGE_SCHEMA = "lolla.atlas_model_page.v2";
export const CARD_FIRST_SOURCE_SHA256 =
  "6d689abd7ae1f8022e2450b045b0f03ffc57700f8298ff858018d808845f5650";
export const CARD_FIRST_KG_RECORD_SHA256 =
  "ec28ee731944e7760dd574a401593d4dac1373ad69d3d080f9e58a4ebd19daef";

const H2_LINES = new Set([7, 25, 47, 77, 101]);
const H3_LINES = new Set([15, 29, 37, 49, 65, 81, 91, 109, 120]);
const PARAGRAPH_LINES = new Set([3, 9, 11, 13, 27, 51, 79, 111]);
const ORDERED_LINES = new Set([17, 19, 21, 53, 55, 57, 59, 61, 63, 67, 69, 71, 73]);
const BULLET_LINES = new Set([31, 33, 35, 39, 41, 43, 83, 85, 87, 89, 93, 95, 97, 103, 105, 107, 122, 124, 126]);
const TABLE_LINES = new Set([113, 115, 116, 117, 118]);
const RULE_LINES = new Set([5, 23, 45, 75, 99]);
export const CARD_FIRST_SUBSTANTIVE_LINES = [
  1,
  ...H2_LINES,
  ...H3_LINES,
  ...PARAGRAPH_LINES,
  ...ORDERED_LINES,
  ...BULLET_LINES,
  ...TABLE_LINES,
].sort((left, right) => left - right);
export const CARD_FIRST_RELATION_INDICES = [0, 1, 2, 3, 4, 51, 456, 534, 810, 1115, 1151, 1283];
export const CARD_FIRST_READER_CHAPTERS = [
  ["understand", 1, 3, 23, 7],
  ["use", 2, 25, 45, 25],
  ["judge", 3, 47, 75, 47],
  ["connect", 4, 77, 99, 77],
  ["apply-safely", 5, 109, 126, 109],
] as const;

export type CardLineKind =
  | "title"
  | "heading"
  | "paragraph"
  | "ordered_list_item"
  | "unordered_list_item"
  | "table_text_row"
  | "horizontal_rule"
  | "table_delimiter"
  | "blank";

export interface CardLineMapEntry {
  line_number: number;
  kind: CardLineKind;
  render_disposition:
    | "rendered_verbatim"
    | "rendered_as_rule"
    | "consumed_as_table_structure"
    | "spacing_normalized";
  heading_level?: 1 | 2 | 3;
}

export interface CardSourceCoverage {
  status: "complete";
  physical_line_count: number;
  accounted_line_count: number;
  substantive_line_count: number;
  rendered_substantive_line_count: number;
  omitted_substantive_line_count: number;
  title_and_heading_count: number;
  rendered_title_and_heading_count: number;
  omitted_title_and_heading_count: number;
  word_count: number;
  presentation_normalization: string[];
}

export interface CardSourceRef extends AtlasSourceRef {
  bytes: number;
  encoding: "utf-8";
  line_ending: "LF";
  terminal_newline: true;
  line_count: number;
}

export interface ReaderOrientationCue {
  label: string;
  text: string;
  source_line: number;
}

export interface ReaderChapter {
  chapter_id: string;
  step: number;
  navigation_label: string;
  orientation: string;
  start_line: number;
  end_line: number;
  heading_line: number;
  after_chapter_action?: string;
}

export interface HumanReaderProjection {
  schema_version: "lolla.atlas_human_reader_projection.v1";
  status: "reviewed_for_abstraction_local_founder_validation";
  interaction_mode: "single_open_chapter_with_persistent_orientation";
  default_chapter_id: "understand";
  orientation_cues: ReaderOrientationCue[];
  chapters: ReaderChapter[];
  source_appendix: {
    appendix_id: "source-curation-notes";
    label: string;
    start_line: 101;
    end_line: 107;
    heading_line: 101;
    default_state: "collapsed";
    reason: string;
    review_authority: "founder_product_feedback_2026-07-16";
  };
  substantive_line_accounting: {
    total: 60;
    hero: number[];
    primary_learning_sequence: number[];
    source_appendix: number[];
    unassigned: number[];
    duplicated: number[];
  };
  non_claims: string[];
}

export interface OperationalMetadataRecord {
  confidence: string;
  description: string;
  extraction_type: string;
  source_quote: string;
}

export interface OperationalFailureMode extends OperationalMetadataRecord {
  mode: string;
  mitigation: string;
}

export interface OperationalRecord {
  name: string;
  display_name: string;
  slug: string;
  source_file: string;
  select_when: string[];
  danger_when: string[];
  input_type: string;
  output_type: string;
  reasoning_types: string[];
  failure_modes: OperationalFailureMode[];
  premortem_questions: OperationalMetadataRecord[];
  heuristics: OperationalMetadataRecord[];
}

export interface CardFirstRelation extends AtlasRelationRecord {
  source_record_index: number;
  focus_direction: "incoming" | "outgoing";
}

export interface CoverageComponent {
  component: string;
  status: "complete" | "partial" | "missing" | "available_not_projected";
  render_disposition?: string;
}

export interface CardFirstModelPage {
  schema_version: typeof CARD_FIRST_MODEL_PAGE_SCHEMA;
  page_id: string;
  page_status: string;
  predecessor: { path: string; schema_version: string; sha256: string };
  model: { model_id: "abstraction"; slug: "abstraction"; display_name: "Abstraction" };
  source_card: {
    label: string;
    content_role: "authoritative_educational_source";
    source_ref: CardSourceRef;
    source_text: string;
    line_map: CardLineMapEntry[];
    reader_projection: HumanReaderProjection;
    coverage: CardSourceCoverage;
  };
  operational_curation: {
    label: string;
    content_role: "compiled_operational_projection";
    not_source_card: true;
    description: string;
    source_ref: AtlasSourceRef;
    record_sha256: string;
    record: OperationalRecord;
    field_coverage: {
      status: "complete";
      source_field_count: number;
      projected_field_count: number;
      omitted_fields: string[];
    };
  };
  connections: {
    label: string;
    content_role: "exact_curated_relation_index";
    description: string;
    focus_model_id: "abstraction";
    source_ref: AtlasSourceRef;
    ordering: "source_record_index";
    eligible_record_count: number;
    shown_record_count: number;
    omitted_record_count: number;
    incoming_count: number;
    outgoing_count: number;
    relation_type_counts: Record<"ally" | "antagonist" | "tension", number>;
    records: CardFirstRelation[];
    record_coverage: { status: "complete" };
    source_field_projection: {
      status: "partial";
      included_or_transformed_fields: string[];
      omitted_fields: Array<{ field: string; reason: string }>;
    };
  };
  coverage: { status: "partial"; components: CoverageComponent[] };
  source_custody: Record<string, unknown>;
  status: AtlasPublicationStatus & { content_generation: string };
  missingness: AtlasMissingness;
  non_claims: string[];
}

export function cardFirstModelPageUrl(slug: string): string | null {
  return slug === "abstraction"
    ? assetUrl("data/card-first-v2/pages/model-abstraction.json")
    : null;
}

export async function loadCardFirstModelPage(
  slug: string,
  signal?: AbortSignal,
): Promise<CardFirstModelPage | null> {
  const url = cardFirstModelPageUrl(slug);
  if (!url) return null;
  const response = await fetch(url, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) {
    throw new CardFirstContractError(
      `Card-first model request failed (${response.status} ${response.statusText})`,
    );
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new CardFirstContractError("Card-first model data is not valid JSON");
  }
  const page = validateCardFirstModelPage(payload);
  if (page.model.slug !== slug) {
    fail("card-first model route identity mismatch");
  }
  const sourceHash = await sha256(new TextEncoder().encode(page.source_card.source_text));
  if (sourceHash !== page.source_card.source_ref.sha256) {
    fail("card-first source hash does not match exact embedded bytes");
  }
  const recordHash = await sha256(
    new TextEncoder().encode(canonicalJson(page.operational_curation.record)),
  );
  if (recordHash !== page.operational_curation.record_sha256) {
    fail("card-first knowledge-graph record hash does not match exact record");
  }
  return page;
}

export function validateCardFirstModelPage(value: unknown): CardFirstModelPage {
  const root = object(value, "card-first model page");
  if (root.schema_version !== CARD_FIRST_MODEL_PAGE_SCHEMA) fail("invalid card-first schema");
  const model = object(root.model, "model");
  if (
    model.model_id !== "abstraction" ||
    model.slug !== "abstraction" ||
    model.display_name !== "Abstraction"
  ) fail("card-first model identity drift");

  const card = object(root.source_card, "source_card");
  if (card.content_role !== "authoritative_educational_source") fail("invalid source-card role");
  strings(card, ["label", "source_text"], "source_card");
  const sourceRef = validateSourceRef(card.source_ref, "source_card.source_ref") as CardSourceRef;
  if (
    sourceRef.sha256 !== CARD_FIRST_SOURCE_SHA256 ||
    sourceRef.bytes !== 14518 ||
    sourceRef.encoding !== "utf-8" ||
    sourceRef.line_ending !== "LF" ||
    sourceRef.terminal_newline !== true ||
    sourceRef.line_count !== 126
  ) fail("source-card byte and line custody drift");
  const sourceText = card.source_text as string;
  if (!sourceText.endsWith("\n") || sourceText.endsWith("\n\n")) fail("source must end in one LF");
  const sourceLines = sourceText.slice(0, -1).split("\n");
  if (sourceLines.length !== 126) fail("source must contain exactly 126 physical lines");
  const lineMap = array(card.line_map, "source_card.line_map").map(validateLineMapEntry);
  if (lineMap.length !== 126) fail("line map must contain exactly 126 entries");
  lineMap.forEach((entry, index) => {
    if (entry.line_number !== index + 1) fail("line map has gap, duplicate, or reorder");
    validateFrozenLineRole(entry, sourceLines[index]);
  });
  validateSourceCoverage(card.coverage, lineMap);
  validateReaderProjection(card.reader_projection, sourceLines);

  const operational = object(root.operational_curation, "operational_curation");
  if (
    operational.content_role !== "compiled_operational_projection" ||
    operational.not_source_card !== true
  ) fail("operational curation must remain a separate compiled layer");
  strings(operational, ["label", "description", "record_sha256"], "operational_curation");
  if (operational.record_sha256 !== CARD_FIRST_KG_RECORD_SHA256) fail("KG record hash drift");
  validateSourceRef(operational.source_ref, "operational_curation.source_ref");
  validateOperationalRecord(operational.record);
  const fieldCoverage = object(operational.field_coverage, "operational_curation.field_coverage");
  if (
    fieldCoverage.status !== "complete" ||
    fieldCoverage.source_field_count !== 12 ||
    fieldCoverage.projected_field_count !== 12 ||
    array(fieldCoverage.omitted_fields, "operational_curation.field_coverage.omitted_fields").length
  ) fail("operational record field coverage is not complete");

  validateConnections(root.connections);
  const coverage = object(root.coverage, "coverage");
  if (coverage.status !== "partial") fail("overall page coverage must remain partial");
  const components = array(coverage.components, "coverage.components").map((value, index) => {
    const item = object(value, `coverage.components[${index}]`);
    strings(item, ["component", "status"], `coverage.components[${index}]`);
    return item;
  });
  if (!components.some((item) => ["partial", "missing", "available_not_projected"].includes(item.status as string))) {
    fail("partial page must name partial, missing, or unprojected components");
  }
  validateMissingness(root.missingness, "missingness");
  if ((object(root.missingness, "missingness").status) !== "partial") fail("page missingness must be partial");
  stringArray(root.non_claims, "non_claims");
  object(root.source_custody, "source_custody");
  object(root.status, "status");
  object(root.predecessor, "predecessor");
  return root as unknown as CardFirstModelPage;
}

function validateReaderProjection(value: unknown, sourceLines: string[]): void {
  const projection = object(value, "source_card.reader_projection");
  if (
    projection.schema_version !== "lolla.atlas_human_reader_projection.v1" ||
    projection.status !== "reviewed_for_abstraction_local_founder_validation" ||
    projection.interaction_mode !== "single_open_chapter_with_persistent_orientation" ||
    projection.default_chapter_id !== "understand"
  ) fail("human reader projection identity drift");

  const chapters = array(projection.chapters, "source_card.reader_projection.chapters");
  if (chapters.length !== CARD_FIRST_READER_CHAPTERS.length) fail("reader chapter count drift");
  chapters.forEach((value, index) => {
    const chapter = object(value, `source_card.reader_projection.chapters[${index}]`);
    strings(chapter, ["chapter_id", "navigation_label", "orientation"], `source_card.reader_projection.chapters[${index}]`);
    const expected = CARD_FIRST_READER_CHAPTERS[index];
    if (
      chapter.chapter_id !== expected[0] || chapter.step !== expected[1] ||
      chapter.start_line !== expected[2] || chapter.end_line !== expected[3] ||
      chapter.heading_line !== expected[4]
    ) fail(`reader chapter ${index} identity or line range drift`);
  });

  const appendix = object(projection.source_appendix, "source_card.reader_projection.source_appendix");
  if (
    appendix.appendix_id !== "source-curation-notes" || appendix.start_line !== 101 ||
    appendix.end_line !== 107 || appendix.heading_line !== 101 ||
    appendix.default_state !== "collapsed" ||
    appendix.review_authority !== "founder_product_feedback_2026-07-16"
  ) fail("reader source appendix boundary drift");
  strings(appendix, ["label", "reason"], "source_card.reader_projection.source_appendix");

  const cues = array(projection.orientation_cues, "source_card.reader_projection.orientation_cues");
  if (cues.length !== 3) fail("reader orientation cue count drift");
  cues.forEach((value, index) => {
    const cue = object(value, `source_card.reader_projection.orientation_cues[${index}]`);
    strings(cue, ["label", "text"], `source_card.reader_projection.orientation_cues[${index}]`);
    positiveInteger(cue.source_line, `source_card.reader_projection.orientation_cues[${index}].source_line`);
    if (!sourceLines[(cue.source_line as number) - 1]?.includes(cue.text as string)) {
      fail(`reader orientation cue ${index} no longer matches its source line`);
    }
  });

  const accounting = object(
    projection.substantive_line_accounting,
    "source_card.reader_projection.substantive_line_accounting",
  );
  if (accounting.total !== 60) fail("reader substantive total drift");
  const hero = numberArray(accounting.hero, "reader accounting hero");
  const primary = numberArray(accounting.primary_learning_sequence, "reader accounting primary");
  const sourceAppendix = numberArray(accounting.source_appendix, "reader accounting appendix");
  if (array(accounting.unassigned, "reader accounting unassigned").length) fail("reader projection has unassigned lines");
  if (array(accounting.duplicated, "reader accounting duplicated").length) fail("reader projection duplicates lines");
  const combined = [...hero, ...primary, ...sourceAppendix].sort((left, right) => left - right);
  if (!sameNumbers(combined, CARD_FIRST_SUBSTANTIVE_LINES) || new Set(combined).size !== 60) {
    fail("reader projection substantive line partition drift");
  }
  stringArray(projection.non_claims, "source_card.reader_projection.non_claims");
}

function validateLineMapEntry(value: unknown, index: number): CardLineMapEntry {
  const path = `source_card.line_map[${index}]`;
  const entry = object(value, path);
  positiveInteger(entry.line_number, `${path}.line_number`);
  strings(entry, ["kind", "render_disposition"], path);
  return entry as unknown as CardLineMapEntry;
}

function validateFrozenLineRole(entry: CardLineMapEntry, sourceLine: string): void {
  const number = entry.line_number;
  let expectedKind: CardLineKind;
  let disposition: CardLineMapEntry["render_disposition"];
  let level: number | undefined;
  if (number === 1) [expectedKind, disposition, level] = ["title", "rendered_verbatim", 1];
  else if (H2_LINES.has(number)) [expectedKind, disposition, level] = ["heading", "rendered_verbatim", 2];
  else if (H3_LINES.has(number)) [expectedKind, disposition, level] = ["heading", "rendered_verbatim", 3];
  else if (PARAGRAPH_LINES.has(number)) [expectedKind, disposition] = ["paragraph", "rendered_verbatim"];
  else if (ORDERED_LINES.has(number)) [expectedKind, disposition] = ["ordered_list_item", "rendered_verbatim"];
  else if (BULLET_LINES.has(number)) [expectedKind, disposition] = ["unordered_list_item", "rendered_verbatim"];
  else if (TABLE_LINES.has(number)) [expectedKind, disposition] = ["table_text_row", "rendered_verbatim"];
  else if (RULE_LINES.has(number)) [expectedKind, disposition] = ["horizontal_rule", "rendered_as_rule"];
  else if (number === 114) [expectedKind, disposition] = ["table_delimiter", "consumed_as_table_structure"];
  else {
    expectedKind = "blank";
    disposition = "spacing_normalized";
    if (sourceLine !== "") fail(`unreviewed substantive text at line ${number}`);
  }
  if (entry.kind !== expectedKind || entry.render_disposition !== disposition) {
    fail(`source line ${number} has wrong kind or render disposition`);
  }
  if (entry.heading_level !== level) fail(`source line ${number} has wrong heading level`);
}

function validateSourceCoverage(value: unknown, lineMap: CardLineMapEntry[]): void {
  const coverage = object(value, "source_card.coverage");
  const exact: Record<string, unknown> = {
    status: "complete",
    physical_line_count: 126,
    accounted_line_count: 126,
    substantive_line_count: 60,
    rendered_substantive_line_count: 60,
    omitted_substantive_line_count: 0,
    title_and_heading_count: 15,
    rendered_title_and_heading_count: 15,
    omitted_title_and_heading_count: 0,
  };
  for (const [key, expected] of Object.entries(exact)) {
    if (coverage[key] !== expected) fail(`source-card coverage drift: ${key}`);
  }
  const rendered = lineMap.filter((entry) => entry.render_disposition === "rendered_verbatim").map((entry) => entry.line_number);
  if (!sameNumbers(rendered, CARD_FIRST_SUBSTANTIVE_LINES)) fail("rendered source-line set drift");
  positiveInteger(coverage.word_count, "source_card.coverage.word_count");
  stringArray(coverage.presentation_normalization, "source_card.coverage.presentation_normalization");
}

function validateOperationalRecord(value: unknown): void {
  const record = object(value, "operational_curation.record");
  const exactKeys = [
    "danger_when", "display_name", "failure_modes", "heuristics", "input_type", "name",
    "output_type", "premortem_questions", "reasoning_types", "select_when", "slug", "source_file",
  ];
  if (Object.keys(record).sort().join("|") !== exactKeys.join("|")) fail("KG record key set drift");
  strings(record, ["display_name", "input_type", "name", "output_type", "slug", "source_file"], "operational_curation.record");
  stringArray(record.select_when, "operational_curation.record.select_when");
  stringArray(record.danger_when, "operational_curation.record.danger_when");
  stringArray(record.reasoning_types, "operational_curation.record.reasoning_types");
  array(record.failure_modes, "operational_curation.record.failure_modes").forEach((item, index) => {
    const failure = object(item, `operational_curation.record.failure_modes[${index}]`);
    strings(failure, ["mode", "description", "mitigation", "source_quote", "extraction_type", "confidence"], `operational_curation.record.failure_modes[${index}]`);
  });
  for (const key of ["premortem_questions", "heuristics"]) {
    array(record[key], `operational_curation.record.${key}`).forEach((item, index) => {
      const recordItem = object(item, `operational_curation.record.${key}[${index}]`);
      strings(recordItem, ["description", "source_quote", "extraction_type", "confidence"], `operational_curation.record.${key}[${index}]`);
    });
  }
}

function validateConnections(value: unknown): void {
  const connections = object(value, "connections");
  if (
    connections.content_role !== "exact_curated_relation_index" ||
    connections.focus_model_id !== "abstraction" ||
    connections.ordering !== "source_record_index"
  ) fail("connection layer identity drift");
  strings(connections, ["label", "description"], "connections");
  validateSourceRef(connections.source_ref, "connections.source_ref");
  const records = array(connections.records, "connections.records").map((value, index) => {
    const relation = validateRelation(value, index);
    if (relation.source_record_index !== CARD_FIRST_RELATION_INDICES[index]) fail("relation source index drift");
    const expectedDirection = relation.source_model_id === "abstraction" ? "outgoing" : "incoming";
    if (relation.focus_direction !== expectedDirection) fail("relation focus direction drift");
    return relation;
  });
  if (records.length !== 12 || new Set(records.map((item) => item.relation_id)).size !== 12) fail("connection membership drift");
  const countPairs: Array<[string, number]> = [
    ["eligible_record_count", 12], ["shown_record_count", 12], ["omitted_record_count", 0],
    ["incoming_count", 7], ["outgoing_count", 5],
  ];
  countPairs.forEach(([key, expected]) => { if (connections[key] !== expected) fail(`connection count drift: ${key}`); });
  const counts = object(connections.relation_type_counts, "connections.relation_type_counts");
  const expectedCounts = { ally: 7, antagonist: 1, tension: 4 };
  Object.entries(expectedCounts).forEach(([key, expected]) => { if (counts[key] !== expected) fail(`connection type count drift: ${key}`); });
  const fieldProjection = object(connections.source_field_projection, "connections.source_field_projection");
  if (fieldProjection.status !== "partial") fail("relation source-field projection must remain partial");
  const omittedFields = array(fieldProjection.omitted_fields, "connections.source_field_projection.omitted_fields").map((value, index) => object(value, `connections.source_field_projection.omitted_fields[${index}]`));
  if (!omittedFields.some((item) => item.field === "composition_affinity")) fail("relation projection must disclose omitted affinity");
  if (object(connections.record_coverage, "connections.record_coverage").status !== "complete") fail("connection record membership must be complete");
}

function validateRelation(value: unknown, index: number): CardFirstRelation {
  const path = `connections.records[${index}]`;
  const relation = object(value, path);
  strings(relation, ["relation_id", "source_model_id", "target_model_id", "relation_type", "direction", "summary", "confidence", "curation_status", "focus_direction"], path);
  nonNegativeInteger(relation.source_record_index, `${path}.source_record_index`);
  if (!(["ally", "antagonist", "tension"] as string[]).includes(relation.relation_type as string)) fail(`${path} relation type drift`);
  if (relation.source_model_id !== "abstraction" && relation.target_model_id !== "abstraction") fail(`${path} is not incident to Abstraction`);
  if (typeof relation.is_reciprocal !== "boolean") fail(`${path}.is_reciprocal must be boolean`);
  array(relation.source_refs, `${path}.source_refs`).forEach((ref, refIndex) => validateSourceRef(ref, `${path}.source_refs[${refIndex}]`));
  validateMissingness(relation.missingness, `${path}.missingness`);
  for (const forbidden of ["composition_affinity", "rank", "score", "weight"]) {
    if (forbidden in relation) fail(`${path} contains forbidden visual weight`);
  }
  return relation as unknown as CardFirstRelation;
}

function validateSourceRef(value: unknown, path: string): AtlasSourceRef | CardSourceRef {
  const source = object(value, path);
  strings(source, ["path", "sha256"], path);
  if (!/^[a-f0-9]{64}$/.test(source.sha256 as string)) fail(`${path}.sha256 must be lowercase SHA-256`);
  return source as unknown as AtlasSourceRef;
}

function validateMissingness(value: unknown, path: string): void {
  const missingness = object(value, path);
  strings(missingness, ["status"], path);
  stringArray(missingness.missing_fields, `${path}.missing_fields`);
  stringArray(missingness.notes, `${path}.notes`);
}

async function sha256(bytes: Uint8Array): Promise<string> {
  if (!globalThis.crypto?.subtle) fail("Web Crypto SHA-256 is unavailable");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes as BufferSource);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function canonicalJson(value: unknown): string {
  return `${JSON.stringify(sortDeep(value), null, 2)}\n`;
}

function sortDeep(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, item]) => [key, sortDeep(item)]),
    );
  }
  return value;
}

function sameNumbers(left: number[], right: number[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function positiveInteger(value: unknown, path: string): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 1) fail(`${path} must be a positive safe integer`);
  return value;
}

function nonNegativeInteger(value: unknown, path: string): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) fail(`${path} must be a non-negative safe integer`);
  return value;
}

function stringArray(value: unknown, path: string): string[] {
  const values = array(value, path);
  if (values.some((item) => typeof item !== "string")) fail(`${path} must contain strings`);
  return values as string[];
}

function numberArray(value: unknown, path: string): number[] {
  const values = array(value, path);
  if (values.some((item) => typeof item !== "number" || !Number.isSafeInteger(item))) {
    fail(`${path} must contain safe integers`);
  }
  return values as number[];
}

function strings(value: Record<string, unknown>, keys: string[], path: string): void {
  for (const key of keys) if (typeof value[key] !== "string" || !(value[key] as string).trim()) fail(`${path}.${key} must be a non-empty string`);
}

function object(value: unknown, path: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(`${path} must be an object`);
  return value as Record<string, unknown>;
}

function array(value: unknown, path: string): unknown[] {
  if (!Array.isArray(value)) fail(`${path} must be an array`);
  return value;
}

function fail(message: string): never {
  throw new CardFirstContractError(message);
}

function assetUrl(path: string): string {
  const base = import.meta.env.BASE_URL.endsWith("/") ? import.meta.env.BASE_URL : `${import.meta.env.BASE_URL}/`;
  return new URL(`${base}${path}`, window.location.origin).toString();
}

export class CardFirstContractError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CardFirstContractError";
  }
}
