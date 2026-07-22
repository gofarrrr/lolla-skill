import {
  type AtlasMissingness,
  type AtlasModelRecord,
  type AtlasProjection,
  type AtlasRelationRecord,
  ProjectionContractError,
  validateMissingness,
  validateModelRecord,
  validateProjection,
  validateRelationRecord,
} from "./projection";

export const ATLAS_NAVIGATION_INDEX_SCHEMA =
  "lolla.atlas_navigation_index.v1" as const;
const PAGE_SIZE = 40;

export interface AtlasNavigationIndex {
  schema_version: typeof ATLAS_NAVIGATION_INDEX_SCHEMA;
  index_id: string;
  index_status: string;
  source_custody: Record<string, unknown>;
  scope: {
    corpus_model_count: number;
    relation_record_count: number;
    relation_types: string[];
    directions: string[];
    selection_operation: string;
    browser_semantic_inference: boolean;
    page_size: number;
  };
  models: AtlasModelRecord[];
  relations: AtlasRelationRecord[];
  missingness: AtlasMissingness;
  non_claims: string[];
}

let navigationIndexPromise: Promise<AtlasNavigationIndex> | null = null;

export function loadNavigationIndex(): Promise<AtlasNavigationIndex> {
  if (!navigationIndexPromise) {
    navigationIndexPromise = fetch(
      assetUrl("data/navigation-v2/neighborhood-index.json"),
      { headers: { Accept: "application/json" } },
    )
      .then(async (response) => {
        if (!response.ok) {
          throw new ProjectionContractError(
            `Atlas neighborhood index request failed (${response.status} ${response.statusText})`,
          );
        }
        try {
          return validateNavigationIndex(await response.json());
        } catch (error) {
          if (error instanceof ProjectionContractError) {
            throw error;
          }
          throw new ProjectionContractError("Atlas neighborhood index is not valid JSON");
        }
      })
      .catch((error: unknown) => {
        navigationIndexPromise = null;
        throw error;
      });
  }
  return navigationIndexPromise;
}

export function validateNavigationIndex(value: unknown): AtlasNavigationIndex {
  const root = record(value, "navigation index");
  if (root.schema_version !== ATLAS_NAVIGATION_INDEX_SCHEMA) {
    fail(`navigation index.schema_version must be ${ATLAS_NAVIGATION_INDEX_SCHEMA}`);
  }
  strings(root, ["index_id", "index_status"], "navigation index");
  record(root.source_custody, "navigation index.source_custody");
  const scope = record(root.scope, "navigation index.scope");
  strings(
    scope,
    ["selection_operation"],
    "navigation index.scope",
  );
  stringArray(scope.relation_types, "navigation index.scope.relation_types");
  stringArray(scope.directions, "navigation index.scope.directions");
  for (const key of ["corpus_model_count", "relation_record_count", "page_size"]) {
    if (!Number.isSafeInteger(scope[key]) || (scope[key] as number) < 0) {
      fail(`navigation index.scope.${key} must be a non-negative integer`);
    }
  }
  if (scope.browser_semantic_inference !== false) {
    fail("navigation index must prohibit browser semantic inference");
  }
  if (scope.page_size !== PAGE_SIZE) {
    fail(`navigation index page size must be ${PAGE_SIZE}`);
  }

  const models = list(root.models, "navigation index.models").map(
    validateModelRecord,
  );
  const relations = list(root.relations, "navigation index.relations").map(
    validateRelationRecord,
  );
  const modelIds = new Set(models.map((model) => model.model_id));
  if (modelIds.size !== models.length) {
    fail("navigation index contains duplicate model IDs");
  }
  const relationIds = new Set<string>();
  const forbidden = new Set(["affinity", "composition_affinity", "rank", "score", "weight"]);
  for (const [index, relation] of relations.entries()) {
    if (relationIds.has(relation.relation_id)) {
      fail("navigation index contains duplicate relation IDs");
    }
    relationIds.add(relation.relation_id);
    if (!modelIds.has(relation.source_model_id) || !modelIds.has(relation.target_model_id)) {
      fail(`navigation relation ${relation.relation_id} references an unknown model`);
    }
    const raw = record((root.relations as unknown[])[index], `navigation index.relations[${index}]`);
    if ([...forbidden].some((field) => field in raw)) {
      fail(`navigation relation ${relation.relation_id} contains a visual score`);
    }
  }
  if (scope.corpus_model_count !== models.length || scope.relation_record_count !== relations.length) {
    fail("navigation index declared counts do not reconcile");
  }
  const missingness = validateMissingness(
    root.missingness,
    "navigation index.missingness",
  );
  const nonClaims = stringArray(root.non_claims, "navigation index.non_claims");
  return {
    ...(root as unknown as AtlasNavigationIndex),
    scope: scope as unknown as AtlasNavigationIndex["scope"],
    models,
    relations,
    missingness,
    non_claims: nonClaims,
  };
}

export async function buildNeighborhoodProjection(
  index: AtlasNavigationIndex,
  modelId: string,
  pageNumber = 1,
): Promise<AtlasProjection> {
  const modelMap = new Map(index.models.map((model) => [model.model_id, model]));
  if (!modelMap.has(modelId)) {
    throw new ProjectionContractError(
      `Model ${modelId} is not present in the canonical navigation index`,
    );
  }
  const eligible = index.relations.filter(
    (relation) =>
      relation.source_model_id === modelId || relation.target_model_id === modelId,
  );
  const pageCount = Math.max(1, Math.ceil(eligible.length / PAGE_SIZE));
  if (!Number.isSafeInteger(pageNumber) || pageNumber < 1 || pageNumber > pageCount) {
    throw new ProjectionContractError(
      `Page ${pageNumber} is outside the neighborhood page range 1–${pageCount}`,
    );
  }
  const beforeCount = (pageNumber - 1) * PAGE_SIZE;
  const relations = eligible.slice(beforeCount, beforeCount + PAGE_SIZE);
  const allNeighborIds = uniqueSorted(
    eligible.map((relation) =>
      relation.source_model_id === modelId
        ? relation.target_model_id
        : relation.source_model_id,
    ),
  );
  const visibleIds = new Set<string>([modelId]);
  for (const relation of relations) {
    visibleIds.add(relation.source_model_id);
    visibleIds.add(relation.target_model_id);
  }
  const orderedVisibleIds = [
    modelId,
    ...allNeighborIds.filter((neighborId) => visibleIds.has(neighborId)),
  ];
  const coordinates = neighborhoodCoordinates(modelId, allNeighborIds).filter(
    (coordinate) => visibleIds.has(coordinate.model_id),
  );
  const configuration = {
    variant: "selected_model_neighborhood",
    relation_weight_policy: "uniform",
    browser_layout_recomputation: true,
    coordinate_precision: 6,
    focus_model_id: modelId,
    layout_universe_count: allNeighborIds.length + 1,
    layout_universe_sha256: await sha256(stableJson([modelId, ...allNeighborIds])),
  };
  const projection: AtlasProjection = {
    schema_version: "lolla.atlas_projection.v1",
    projection_id: `atlas-neighborhood-${modelId}-page-${pageNumber}-v1`,
    fixture_id: "canonical_neighborhood",
    projection_status: "deterministic_navigation_projection",
    source_custody: index.source_custody,
    scope: {
      focus_model_id: modelId,
      model_selection: "founder_review_navigation",
      relation_types: ["ally", "antagonist", "tension"],
      directions: ["incoming", "outgoing"],
      selection_operation: "exact_incident_edge_filter_only",
      browser_semantic_inference: false,
      unique_neighbor_count: allNeighborIds.length,
      corpus_model_count: index.models.length,
    },
    models: orderedVisibleIds.map((id) => modelMap.get(id)!),
    relations,
    page: {
      page_number: pageNumber,
      page_size: PAGE_SIZE,
      eligible_count: eligible.length,
      shown_count: relations.length,
      omitted_count: eligible.length - relations.length,
      before_count: beforeCount,
      after_count: eligible.length - beforeCount - relations.length,
      ordering: "canonical_relationship_graph_source_record_order",
      relation_ids: relations.map((relation) => relation.relation_id),
    },
    layout: {
      layout_id: `atlas-neighborhood-${modelId}-page-${pageNumber}`,
      algorithm: "deterministic_concentric_neighborhood",
      algorithm_version: "1",
      configuration,
      configuration_sha256: await sha256(stableJson(configuration)),
      coordinate_sha256: await sha256(stableJson(coordinates)),
      coordinates,
    },
    missingness: index.missingness,
    non_claims: index.non_claims,
  };
  return validateProjection(projection);
}

function neighborhoodCoordinates(modelId: string, neighborIds: string[]) {
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  return [
    { model_id: modelId, x: 0, y: 0 },
    ...neighborIds.map((neighborId, index) => {
      const ring = 1 + Math.floor(index / 8);
      const radius = 1 + (ring - 1) * 0.82;
      const angle = index * goldenAngle - Math.PI / 2;
      return {
        model_id: neighborId,
        x: round6(Math.cos(angle) * radius),
        y: round6(Math.sin(angle) * radius),
      };
    }),
  ];
}

function round6(value: number): number {
  return Math.round(value * 1_000_000) / 1_000_000;
}

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values)].sort();
}

async function sha256(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function stableJson(value: unknown): string {
  return JSON.stringify(value, (_key, item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) {
      return item;
    }
    return Object.fromEntries(
      Object.entries(item as Record<string, unknown>).sort(([left], [right]) =>
        left.localeCompare(right),
      ),
    );
  });
}

function assetUrl(path: string): string {
  const base = import.meta.env.BASE_URL.endsWith("/")
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`;
  return new URL(`${base}${path}`, window.location.origin).toString();
}

function record(value: unknown, path: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail(`${path} must be an object`);
  }
  return value as Record<string, unknown>;
}

function list(value: unknown, path: string): unknown[] {
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
    if (typeof value[key] !== "string") {
      fail(`${path}.${key} must be a string`);
    }
  }
}

function stringArray(value: unknown, path: string): string[] {
  const values = list(value, path);
  if (values.some((item) => typeof item !== "string")) {
    fail(`${path} must contain only strings`);
  }
  return values as string[];
}

function fail(message: string): never {
  throw new ProjectionContractError(message);
}
