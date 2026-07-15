import { navigate } from "./router";

export const RELATION_TYPES = ["ally", "antagonist", "tension"] as const;
export type RelationType = (typeof RELATION_TYPES)[number];
export type AtlasView = "graph" | "list";

export interface DurableAtlasState {
  selectedModelId: string | null;
  selectedRelationId: string | null;
  familyId: string | null;
  relationTypes: RelationType[];
  query: string;
  relationPage: number;
  view: AtlasView;
}

export interface EphemeralAtlasState {
  hoveredModelId: string | null;
  hoveredRelationId: string | null;
}

export const EMPTY_EPHEMERAL_STATE: EphemeralAtlasState = {
  hoveredModelId: null,
  hoveredRelationId: null,
};

export function parseAtlasState(url: URL): DurableAtlasState {
  const params = url.searchParams;
  const relationTypes = normalizeRelationTypes(params.get("relations"));
  const relationPage = Number.parseInt(params.get("page") ?? "1", 10);
  return {
    selectedModelId: clean(params.get("model")),
    selectedRelationId: clean(params.get("relation")),
    familyId: clean(params.get("family")),
    relationTypes,
    query: params.get("q")?.trim() ?? "",
    relationPage:
      Number.isSafeInteger(relationPage) && relationPage > 0 ? relationPage : 1,
    view: params.get("view") === "list" ? "list" : "graph",
  };
}

export function atlasStateHref(
  currentUrl: URL,
  patch: Partial<DurableAtlasState>,
): string {
  const state = { ...parseAtlasState(currentUrl), ...patch };
  const params = new URLSearchParams(currentUrl.searchParams);
  for (const key of [
    "model",
    "relation",
    "family",
    "relations",
    "q",
    "page",
    "view",
  ]) {
    params.delete(key);
  }
  setOptional(params, "model", state.selectedModelId);
  setOptional(params, "relation", state.selectedRelationId);
  setOptional(params, "family", state.familyId);
  if (state.relationTypes.length > 0) {
    params.set("relations", state.relationTypes.join(","));
  }
  if (state.query) {
    params.set("q", state.query);
  }
  if (state.relationPage > 1) {
    params.set("page", String(state.relationPage));
  }
  if (state.view === "list") {
    params.set("view", "list");
  }
  const search = params.toString();
  return `/atlas${search ? `?${search}` : ""}`;
}

export function updateAtlasState(
  currentUrl: URL,
  patch: Partial<DurableAtlasState>,
  options: { replace?: boolean } = {},
): void {
  navigate(atlasStateHref(currentUrl, patch), options);
}

function normalizeRelationTypes(value: string | null): RelationType[] {
  if (!value) {
    return [];
  }
  const allowed = new Set<string>(RELATION_TYPES);
  return [...new Set(value.split(","))].filter((item): item is RelationType =>
    allowed.has(item),
  );
}

function clean(value: string | null): string | null {
  const cleaned = value?.trim();
  return cleaned ? cleaned : null;
}

function setOptional(
  params: URLSearchParams,
  key: string,
  value: string | null,
): void {
  if (value) {
    params.set(key, value);
  }
}
