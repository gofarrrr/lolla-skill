import type { RelationType } from "./atlasState";

export const ATLAS_PROJECTION_SCHEMA = "lolla.atlas_projection.v1";
export const ATLAS_MODEL_PAGE_SCHEMA = "lolla.atlas_model_page.v1";
export const ATLAS_RELATION_PAGE_SCHEMA = "lolla.atlas_relation_page.v1";

export const FIXTURES = [
  {
    id: "ordinary-navigation",
    projectionFixtureId: "ordinary_navigation",
    label: "Ordinary neighborhood",
    filename: "ordinary-navigation.json",
  },
  {
    id: "mixed-parallel-relations",
    projectionFixtureId: "mixed_parallel_relations",
    label: "Parallel ally + tension",
    filename: "mixed-parallel-relations.json",
  },
  {
    id: "explicit-bidirectionality",
    projectionFixtureId: "explicit_bidirectionality",
    label: "Explicit bidirectionality",
    filename: "explicit-bidirectionality.json",
  },
  {
    id: "confirmation-bias-hub",
    projectionFixtureId: "confirmation_bias_hub",
    label: "233-record paged hub",
    filename: "confirmation-bias-hub-page-1.json",
  },
  {
    id: "medium-confidence-relation",
    projectionFixtureId: "medium_confidence_relation",
    label: "Medium-confidence caution",
    filename: "medium-confidence-relation.json",
  },
] as const;

export type FixtureId = (typeof FIXTURES)[number]["id"];
export type ProjectionFixtureId =
  | (typeof FIXTURES)[number]["projectionFixtureId"]
  | "canonical_neighborhood";

export interface AtlasSourceRef {
  path: string;
  sha256: string;
  source_type?: string;
  json_pointer?: string;
}

export interface AtlasMissingness {
  status: string;
  missing_fields: string[];
  notes: string[];
}

export interface AtlasPublicationStatus {
  source: string;
  curation: string;
  human_review: string;
  licensing: string;
  publication: string;
  missingness: string;
}

export interface AtlasModelRecord {
  model_id: string;
  slug: string;
  display_name: string;
  source_ref: AtlasSourceRef;
  summary: AtlasSourcedText;
  helps_notice: AtlasSourcedText;
  curation_refs: {
    activation: AtlasSourceRef;
    intervention: AtlasSourceRef;
    relations: AtlasSourceRef;
  };
  status: AtlasPublicationStatus;
}

export interface AtlasSourcedText {
  text: string;
  provenance: AtlasSourceRef[];
  status: string;
  missingness: AtlasMissingness;
}

export interface AtlasRelationRecord {
  relation_id: string;
  source_model_id: string;
  target_model_id: string;
  relation_type: RelationType;
  direction: string;
  is_reciprocal: boolean;
  summary: string;
  confidence: "high" | "medium";
  curation_status: string;
  source_refs: AtlasSourceRef[];
  missingness: AtlasMissingness;
}

export interface AtlasCoordinate {
  model_id: string;
  x: number;
  y: number;
}

export interface AtlasLayout {
  layout_id: string;
  algorithm: string;
  algorithm_version: string;
  configuration: Record<string, unknown>;
  configuration_sha256: string;
  coordinate_sha256: string;
  coordinates: AtlasCoordinate[];
}

export interface AtlasRelationPageWindow {
  page_number: number;
  page_size: number;
  eligible_count: number;
  shown_count: number;
  omitted_count: number;
  before_count: number;
  after_count: number;
  ordering: string;
  relation_ids: string[];
}

export interface AtlasProjection {
  schema_version: typeof ATLAS_PROJECTION_SCHEMA;
  projection_id: string;
  fixture_id: ProjectionFixtureId;
  projection_status: string;
  source_custody: Record<string, unknown>;
  scope: Record<string, unknown>;
  models: AtlasModelRecord[];
  relations: AtlasRelationRecord[];
  page: AtlasRelationPageWindow;
  layout: AtlasLayout;
  missingness: AtlasMissingness;
  non_claims: string[];
}

export interface AtlasPageSectionBase {
  provenance: AtlasSourceRef[];
  status: string;
  missingness: AtlasMissingness;
}

export interface AtlasTextSection extends AtlasPageSectionBase {
  text: string;
}

export interface AtlasStringListSection extends AtlasPageSectionBase {
  items: string[];
}

export interface AtlasReasoningProfileSection extends AtlasPageSectionBase {
  input_type: string;
  output_type: string;
  reasoning_types: string[];
}

export interface AtlasFailureModeItem {
  text: string;
  mitigation: string;
  source_quote: string;
  extraction_type: string;
  confidence: string;
}

export interface AtlasFailureModesSection extends AtlasPageSectionBase {
  items: AtlasFailureModeItem[];
}

export interface AtlasModelPage {
  schema_version: typeof ATLAS_MODEL_PAGE_SCHEMA;
  page_id: string;
  page_status: string;
  source_custody: Record<string, unknown>;
  model: Pick<
    AtlasModelRecord,
    "model_id" | "slug" | "display_name" | "source_ref"
  >;
  sections: {
    definition: AtlasTextSection;
    use_when: AtlasStringListSection;
    avoid_when: AtlasStringListSection;
    reasoning_profile: AtlasReasoningProfileSection;
    failure_modes: AtlasFailureModesSection;
    premortem_questions: AtlasStringListSection;
    heuristics: AtlasStringListSection;
  };
  status: AtlasPublicationStatus;
  missingness: AtlasMissingness;
  non_claims: string[];
}

export interface AtlasParallelContextSection extends AtlasPageSectionBase {
  parallel_relation_ids: string[];
  reverse_relation_ids: string[];
}

export interface AtlasRelationPage {
  schema_version: typeof ATLAS_RELATION_PAGE_SCHEMA;
  page_id: string;
  page_status: string;
  source_custody: Record<string, unknown>;
  relation: AtlasRelationRecord;
  sections: {
    relation_summary: AtlasTextSection;
    why_it_matters: AtlasTextSection;
    misread_risk: AtlasTextSection;
    activation_condition: AtlasTextSection;
    source_excerpt: AtlasTextSection;
    parallel_record_context: AtlasParallelContextSection;
  };
  status: AtlasPublicationStatus;
  missingness: AtlasMissingness;
  non_claims: string[];
}

export class ProjectionContractError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ProjectionContractError";
  }
}

export function fixtureFromQuery(value: string | null): FixtureId {
  return FIXTURES.some((fixture) => fixture.id === value)
    ? (value as FixtureId)
    : "ordinary-navigation";
}

export function projectionUrl(
  fixtureId: FixtureId,
  pageNumber = 1,
): string {
  if (!Number.isSafeInteger(pageNumber) || pageNumber < 1) {
    throw new ProjectionContractError(
      `Projection page must be a positive safe integer: ${pageNumber}`,
    );
  }
  const fixture = FIXTURES.find((item) => item.id === fixtureId);
  if (!fixture) {
    throw new ProjectionContractError(`Unknown fixture: ${fixtureId}`);
  }
  const filename =
    fixtureId === "confirmation-bias-hub"
      ? `confirmation-bias-hub-page-${pageNumber}.json`
      : fixture.filename;
  return assetUrl(`data/phase1/${filename}`);
}

export function modelPageUrl(slug: string): string | null {
  return slug === "abstraction"
    ? assetUrl("data/phase1/pages/model-abstraction.json")
    : null;
}

export function relationPageUrl(): string {
  return assetUrl(
    "data/phase1/pages/relation-abstraction-first-principles-thinking-ally.json",
  );
}

export async function loadProjection(
  fixtureId: FixtureId,
  pageNumber = 1,
  signal?: AbortSignal,
): Promise<AtlasProjection> {
  const projection = validateProjection(
    await fetchJson(projectionUrl(fixtureId, pageNumber), signal),
  );
  const expectedFixture = FIXTURES.find((fixture) => fixture.id === fixtureId);
  if (!expectedFixture || projection.fixture_id !== expectedFixture.projectionFixtureId) {
    throw new ProjectionContractError(
      `Projection fixture ${projection.fixture_id} does not match requested fixture ${fixtureId}`,
    );
  }
  if (projection.page.page_number !== pageNumber) {
    throw new ProjectionContractError(
      `Projection page ${projection.page.page_number} does not match requested page ${pageNumber}`,
    );
  }
  return projection;
}

export async function loadModelPage(
  slug: string,
  signal?: AbortSignal,
): Promise<AtlasModelPage | null> {
  const url = modelPageUrl(slug);
  if (!url) {
    return null;
  }
  return validateModelPage(await fetchJson(url, signal));
}

export async function loadRelationPage(
  relationId: string,
  signal?: AbortSignal,
): Promise<AtlasRelationPage | null> {
  const page = validateRelationPage(await fetchJson(relationPageUrl(), signal));
  return page.relation.relation_id === relationId ? page : null;
}

export function validateProjection(value: unknown): AtlasProjection {
  const root = object(value, "projection");
  exactSchema(root, ATLAS_PROJECTION_SCHEMA, "projection");
  strings(root, ["projection_id", "fixture_id", "projection_status"], "projection");
  const fixture = FIXTURES.find(
    (candidate) => candidate.projectionFixtureId === root.fixture_id,
  );
  if (!fixture && root.fixture_id !== "canonical_neighborhood") {
    fail(`projection.fixture_id is not a supported Atlas fixture`);
  }
  object(root.source_custody, "projection.source_custody");
  object(root.scope, "projection.scope");
  const models = array(root.models, "projection.models").map(validateModelRecord);
  const relations = array(root.relations, "projection.relations").map(
    validateRelationRecord,
  );
  validatePageWindow(root.page, relations);
  const layout = validateLayout(root.layout);
  validateMissingness(root.missingness, "projection.missingness");
  stringArray(root.non_claims, "projection.non_claims");

  const modelIds = new Set(models.map((model) => model.model_id));
  if (modelIds.size !== models.length) {
    fail("projection.models contains duplicate model_id values");
  }
  const coordinateIds = new Set(
    layout.coordinates.map((coordinate) => coordinate.model_id),
  );
  if (
    coordinateIds.size !== modelIds.size ||
    [...modelIds].some((modelId) => !coordinateIds.has(modelId))
  ) {
    fail("projection.layout.coordinates must cover every displayed model exactly once");
  }
  const relationIds = new Set<string>();
  for (const relation of relations) {
    if (relationIds.has(relation.relation_id)) {
      fail("projection.relations contains duplicate relation_id values");
    }
    relationIds.add(relation.relation_id);
    if (
      !modelIds.has(relation.source_model_id) ||
      !modelIds.has(relation.target_model_id)
    ) {
      fail(`relation ${relation.relation_id} references a model outside the projection`);
    }
  }
  return root as unknown as AtlasProjection;
}

export function validateModelPage(value: unknown): AtlasModelPage {
  const root = object(value, "model page");
  exactSchema(root, ATLAS_MODEL_PAGE_SCHEMA, "model page");
  strings(root, ["page_id", "page_status"], "model page");
  const model = object(root.model, "model page.model");
  strings(model, ["model_id", "slug", "display_name"], "model page.model");
  validateSourceRef(model.source_ref, "model page.model.source_ref");
  const sections = object(root.sections, "model page.sections");
  validateTextSection(sections.definition, "model page.sections.definition");
  validateStringListSection(sections.use_when, "model page.sections.use_when");
  validateStringListSection(sections.avoid_when, "model page.sections.avoid_when");
  validateReasoningProfile(
    sections.reasoning_profile,
    "model page.sections.reasoning_profile",
  );
  validateFailureModes(sections.failure_modes, "model page.sections.failure_modes");
  validateStringListSection(
    sections.premortem_questions,
    "model page.sections.premortem_questions",
  );
  validateStringListSection(sections.heuristics, "model page.sections.heuristics");
  validatePublicationStatus(root.status, "model page.status");
  validateMissingness(root.missingness, "model page.missingness");
  stringArray(root.non_claims, "model page.non_claims");
  return root as unknown as AtlasModelPage;
}

export function validateRelationPage(value: unknown): AtlasRelationPage {
  const root = object(value, "relation page");
  exactSchema(root, ATLAS_RELATION_PAGE_SCHEMA, "relation page");
  strings(root, ["page_id", "page_status"], "relation page");
  validateRelationRecord(root.relation);
  const sections = object(root.sections, "relation page.sections");
  for (const key of [
    "relation_summary",
    "why_it_matters",
    "misread_risk",
    "activation_condition",
    "source_excerpt",
  ]) {
    validateTextSection(sections[key], `relation page.sections.${key}`);
  }
  const parallel = object(
    sections.parallel_record_context,
    "relation page.sections.parallel_record_context",
  );
  validateSectionBase(parallel, "relation page.sections.parallel_record_context");
  stringArray(
    parallel.parallel_relation_ids,
    "relation page.sections.parallel_record_context.parallel_relation_ids",
  );
  stringArray(
    parallel.reverse_relation_ids,
    "relation page.sections.parallel_record_context.reverse_relation_ids",
  );
  validatePublicationStatus(root.status, "relation page.status");
  validateMissingness(root.missingness, "relation page.missingness");
  stringArray(root.non_claims, "relation page.non_claims");
  return root as unknown as AtlasRelationPage;
}

export function validateModelRecord(value: unknown, index = 0): AtlasModelRecord {
  const path = `projection.models[${index}]`;
  const model = object(value, path);
  strings(model, ["model_id", "slug", "display_name"], path);
  validateSourceRef(model.source_ref, `${path}.source_ref`);
  validateSourcedText(model.summary, `${path}.summary`);
  validateSourcedText(model.helps_notice, `${path}.helps_notice`);
  const refs = object(model.curation_refs, `${path}.curation_refs`);
  for (const name of ["activation", "intervention", "relations"]) {
    validateSourceRef(refs[name], `${path}.curation_refs.${name}`);
  }
  validatePublicationStatus(model.status, `${path}.status`);
  return model as unknown as AtlasModelRecord;
}

function validatePageWindow(
  value: unknown,
  relations: AtlasRelationRecord[],
): AtlasRelationPageWindow {
  const page = object(value, "projection.page");
  strings(page, ["ordering"], "projection.page");
  for (const key of [
    "page_number",
    "page_size",
    "eligible_count",
    "shown_count",
    "omitted_count",
    "before_count",
    "after_count",
  ]) {
    if (
      typeof page[key] !== "number" ||
      !Number.isSafeInteger(page[key]) ||
      (page[key] as number) < (key === "page_number" ? 1 : 0)
    ) {
      fail(`projection.page.${key} must be a non-negative integer`);
    }
  }
  const ids = stringArray(page.relation_ids, "projection.page.relation_ids");
  const pageNumber = page.page_number as number;
  const pageSize = page.page_size as number;
  const eligibleCount = page.eligible_count as number;
  const shownCount = page.shown_count as number;
  const omittedCount = page.omitted_count as number;
  const beforeCount = page.before_count as number;
  const afterCount = page.after_count as number;
  if (ids.length !== shownCount) {
    fail("projection.page.relation_ids length must equal shown_count");
  }
  if (shownCount > pageSize) {
    fail("projection.page.shown_count cannot exceed page_size");
  }
  if (pageSize !== 40) {
    fail("projection.page.page_size must equal the frozen Phase 1 bound of 40");
  }
  if (eligibleCount !== shownCount + omittedCount) {
    fail("projection.page eligible, shown, and omitted counts do not reconcile");
  }
  if (omittedCount !== beforeCount + afterCount) {
    fail("projection.page omitted, before, and after counts do not reconcile");
  }
  if (beforeCount !== (pageNumber - 1) * pageSize) {
    fail("projection.page before_count does not match page_number");
  }
  const relationIds = relations.map((relation) => relation.relation_id);
  if (
    relationIds.length !== ids.length ||
    relationIds.some((relationId, index) => relationId !== ids[index])
  ) {
    fail("projection.page.relation_ids must exactly match relation record order");
  }
  return page as unknown as AtlasRelationPageWindow;
}

function validatePublicationStatus(
  value: unknown,
  path: string,
): AtlasPublicationStatus {
  const status = object(value, path);
  strings(
    status,
    ["source", "curation", "human_review", "licensing", "publication", "missingness"],
    path,
  );
  return status as unknown as AtlasPublicationStatus;
}

function validateSectionBase(
  value: Record<string, unknown>,
  path: string,
): void {
  strings(value, ["status"], path);
  array(value.provenance, `${path}.provenance`).forEach((source, index) =>
    validateSourceRef(source, `${path}.provenance[${index}]`),
  );
  validateMissingness(value.missingness, `${path}.missingness`);
}

function validateTextSection(value: unknown, path: string): AtlasTextSection {
  const section = object(value, path);
  validateSectionBase(section, path);
  strings(section, ["text"], path);
  return section as unknown as AtlasTextSection;
}

function validateStringListSection(
  value: unknown,
  path: string,
): AtlasStringListSection {
  const section = object(value, path);
  validateSectionBase(section, path);
  stringArray(section.items, `${path}.items`);
  return section as unknown as AtlasStringListSection;
}

function validateReasoningProfile(
  value: unknown,
  path: string,
): AtlasReasoningProfileSection {
  const section = object(value, path);
  validateSectionBase(section, path);
  strings(section, ["input_type", "output_type"], path);
  stringArray(section.reasoning_types, `${path}.reasoning_types`);
  return section as unknown as AtlasReasoningProfileSection;
}

function validateFailureModes(
  value: unknown,
  path: string,
): AtlasFailureModesSection {
  const section = object(value, path);
  validateSectionBase(section, path);
  array(section.items, `${path}.items`).forEach((rawItem, index) => {
    const item = object(rawItem, `${path}.items[${index}]`);
    strings(
      item,
      ["text", "mitigation", "source_quote", "extraction_type", "confidence"],
      `${path}.items[${index}]`,
    );
  });
  return section as unknown as AtlasFailureModesSection;
}

function validateSourcedText(value: unknown, path: string): AtlasSourcedText {
  const item = object(value, path);
  strings(item, ["text", "status"], path);
  array(item.provenance, `${path}.provenance`).forEach((source, index) =>
    validateSourceRef(source, `${path}.provenance[${index}]`),
  );
  validateMissingness(item.missingness, `${path}.missingness`);
  return item as unknown as AtlasSourcedText;
}

export function validateRelationRecord(value: unknown, index = 0): AtlasRelationRecord {
  const path = `projection.relations[${index}]`;
  const relation = object(value, path);
  strings(
    relation,
    [
      "relation_id",
      "source_model_id",
      "target_model_id",
      "relation_type",
      "direction",
      "summary",
      "confidence",
      "curation_status",
    ],
    path,
  );
  if (!(["ally", "antagonist", "tension"] as string[]).includes(relation.relation_type as string)) {
    fail(`${path}.relation_type is not in the default Atlas layer`);
  }
  if (!(["high", "medium"] as string[]).includes(relation.confidence as string)) {
    fail(`${path}.confidence must be high or medium`);
  }
  if (typeof relation.is_reciprocal !== "boolean") {
    fail(`${path}.is_reciprocal must be boolean`);
  }
  array(relation.source_refs, `${path}.source_refs`).forEach((source, sourceIndex) =>
    validateSourceRef(source, `${path}.source_refs[${sourceIndex}]`),
  );
  validateMissingness(relation.missingness, `${path}.missingness`);
  return relation as unknown as AtlasRelationRecord;
}

function validateLayout(value: unknown): AtlasLayout {
  const layout = object(value, "projection.layout");
  strings(
    layout,
    [
      "layout_id",
      "algorithm",
      "algorithm_version",
      "configuration_sha256",
      "coordinate_sha256",
    ],
    "projection.layout",
  );
  object(layout.configuration, "projection.layout.configuration");
  const coordinateIds = new Set<string>();
  for (const [index, rawCoordinate] of array(
    layout.coordinates,
    "projection.layout.coordinates",
  ).entries()) {
    const coordinate = object(
      rawCoordinate,
      `projection.layout.coordinates[${index}]`,
    );
    strings(coordinate, ["model_id"], `projection.layout.coordinates[${index}]`);
    if (typeof coordinate.x !== "number" || typeof coordinate.y !== "number") {
      fail(`projection.layout.coordinates[${index}] requires numeric x and y`);
    }
    if (coordinateIds.has(coordinate.model_id as string)) {
      fail("projection.layout.coordinates contains duplicate model_id values");
    }
    coordinateIds.add(coordinate.model_id as string);
  }
  return layout as unknown as AtlasLayout;
}

function validateSourceRef(value: unknown, path: string): AtlasSourceRef {
  const source = object(value, path);
  strings(source, ["path", "sha256"], path);
  return source as unknown as AtlasSourceRef;
}

export function validateMissingness(value: unknown, path: string): AtlasMissingness {
  const missingness = object(value, path);
  strings(missingness, ["status"], path);
  stringArray(missingness.missing_fields, `${path}.missing_fields`);
  stringArray(missingness.notes, `${path}.notes`);
  return missingness as unknown as AtlasMissingness;
}

async function fetchJson(url: string, signal?: AbortSignal): Promise<unknown> {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    throw new ProjectionContractError(
      `Atlas data request failed (${response.status} ${response.statusText})`,
    );
  }
  try {
    return await response.json();
  } catch {
    throw new ProjectionContractError("Atlas data is not valid JSON");
  }
}

function assetUrl(path: string): string {
  const base = import.meta.env.BASE_URL.endsWith("/")
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`;
  return new URL(`${base}${path}`, window.location.origin).toString();
}

function exactSchema(
  value: Record<string, unknown>,
  expected: string,
  path: string,
): void {
  if (value.schema_version !== expected) {
    fail(`${path}.schema_version must be ${expected}`);
  }
}

function object(value: unknown, path: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail(`${path} must be an object`);
  }
  return value as Record<string, unknown>;
}

function array(value: unknown, path: string): unknown[] {
  if (!Array.isArray(value)) {
    fail(`${path} must be an array`);
  }
  return value;
}

function strings(
  value: Record<string, unknown>,
  keys: string[],
  path: string,
): void {
  for (const key of keys) {
    if (typeof value[key] !== "string" || !(value[key] as string).trim()) {
      fail(`${path}.${key} must be a non-empty string`);
    }
  }
}

function stringArray(value: unknown, path: string): string[] {
  const values = array(value, path);
  if (values.some((item) => typeof item !== "string")) {
    fail(`${path} must contain only strings`);
  }
  return values as string[];
}

function fail(message: string): never {
  throw new ProjectionContractError(message);
}
