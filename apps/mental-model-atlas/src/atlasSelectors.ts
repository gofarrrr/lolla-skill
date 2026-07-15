import type {
  AtlasModelRecord,
  AtlasProjection,
  AtlasRelationRecord,
} from "./projection";
import type { DurableAtlasState, RelationType } from "./atlasState";

export const MAX_RENDERED_RELATIONS = 40;

export interface AtlasSelection {
  selectedModel: AtlasModelRecord | null;
  selectedRelation: AtlasRelationRecord | null;
  selectedIdMissing: boolean;
  hoveredModel: AtlasModelRecord | null;
  visibleModels: AtlasModelRecord[];
  focusedRelations: AtlasRelationRecord[];
  relatedModelIds: Set<string>;
  eligibleRelationCount: number;
  shownRelationCount: number;
  omittedRelationCount: number;
  projectionEligibleCount: number;
  projectionShownCount: number;
  projectionOmittedCount: number;
  declaredFocusMatches: boolean;
}

export function selectAtlasView(
  projection: AtlasProjection,
  state: DurableAtlasState,
  hoveredModelId: string | null,
): AtlasSelection {
  const modelMap = new Map(
    projection.models.map((model) => [model.model_id, model] as const),
  );
  const relationMap = new Map(
    projection.relations.map((relation) => [relation.relation_id, relation] as const),
  );
  const selectedModel = state.selectedModelId
    ? modelMap.get(state.selectedModelId) ?? null
    : null;
  const selectedRelation = state.selectedRelationId
    ? relationMap.get(state.selectedRelationId) ?? null
    : null;
  const hoveredModel = hoveredModelId ? modelMap.get(hoveredModelId) ?? null : null;
  const selectedIdMissing = Boolean(
    (state.selectedModelId && !selectedModel) ||
      (state.selectedRelationId && !selectedRelation),
  );

  const query = state.query.toLocaleLowerCase();
  const visibleModels = projection.models.filter((model) =>
    query
      ? `${model.display_name} ${model.model_id} ${model.slug}`
          .toLocaleLowerCase()
          .includes(query)
      : true,
  );

  const relationTypes = new Set<RelationType>(state.relationTypes);
  let candidateRelations: AtlasRelationRecord[] = [];
  if (selectedRelation) {
    candidateRelations = [selectedRelation];
  } else if (selectedModel) {
    candidateRelations = projection.relations.filter(
      (relation) =>
        relation.source_model_id === selectedModel.model_id ||
        relation.target_model_id === selectedModel.model_id,
    );
  }
  if (relationTypes.size > 0) {
    candidateRelations = candidateRelations.filter((relation) =>
      relationTypes.has(relation.relation_type),
    );
  }

  const focusedRelations = candidateRelations.slice(0, MAX_RENDERED_RELATIONS);
  const declaredEligibleCount = projection.page.eligible_count;
  const declaredShownCount = projection.page.shown_count;
  const declaredOmittedCount = projection.page.omitted_count;
  const declaredFocusModelId =
    typeof projection.scope.focus_model_id === "string"
      ? projection.scope.focus_model_id
      : null;
  const declaredFocusMatches = Boolean(
    selectedModel && declaredFocusModelId === selectedModel.model_id,
  );
  const eligibleRelationCount =
    selectedModel || selectedRelation
      ? declaredFocusMatches
        ? declaredEligibleCount
        : candidateRelations.length
      : 0;
  const shownRelationCount =
    selectedModel || selectedRelation
      ? focusedRelations.length
      : 0;
  const omittedRelationCount =
    selectedModel || selectedRelation
      ? declaredFocusMatches
        ? declaredOmittedCount
        : Math.max(0, eligibleRelationCount - shownRelationCount)
      : 0;

  const relatedModelIds = new Set<string>();
  if (selectedModel) {
    relatedModelIds.add(selectedModel.model_id);
  }
  for (const relation of focusedRelations) {
    relatedModelIds.add(relation.source_model_id);
    relatedModelIds.add(relation.target_model_id);
  }

  return {
    selectedModel,
    selectedRelation,
    selectedIdMissing,
    hoveredModel,
    visibleModels,
    focusedRelations,
    relatedModelIds,
    eligibleRelationCount,
    shownRelationCount,
    omittedRelationCount,
    projectionEligibleCount: declaredEligibleCount,
    projectionShownCount: declaredShownCount,
    projectionOmittedCount: declaredOmittedCount,
    declaredFocusMatches,
  };
}

export function relationCoverageText(selection: AtlasSelection): string {
  if (selection.declaredFocusMatches) {
    return `${selection.shownRelationCount} of ${selection.eligibleRelationCount} exact incident relation records shown; ${selection.omittedRelationCount} not rendered on this page.`;
  }
  return `${selection.shownRelationCount} exact incident records drawn from a projection page containing ${selection.projectionShownCount} of ${selection.projectionEligibleCount}; ${selection.projectionOmittedCount} records are outside this fixture page.`;
}

export function relationCounts(
  relations: AtlasRelationRecord[],
  modelId: string,
): Record<RelationType, number> {
  const counts: Record<RelationType, number> = {
    ally: 0,
    antagonist: 0,
    tension: 0,
  };
  for (const relation of relations) {
    if (
      relation.source_model_id === modelId ||
      relation.target_model_id === modelId
    ) {
      counts[relation.relation_type] += 1;
    }
  }
  return counts;
}
