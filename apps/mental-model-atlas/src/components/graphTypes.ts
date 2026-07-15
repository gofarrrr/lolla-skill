import type {
  AtlasModelRecord,
  AtlasProjection,
  AtlasRelationRecord,
} from "../projection";

export interface GraphRendererProps {
  projection: AtlasProjection;
  relations: AtlasRelationRecord[];
  selectedModelId: string | null;
  selectedRelationId: string | null;
  hoveredModelId: string | null;
  relatedModelIds: Set<string>;
  visibleModelIds: Set<string>;
  onSelectModel: (modelId: string) => void;
  onSelectRelation: (relationId: string) => void;
  onHoverModel: (modelId: string | null) => void;
}

export interface PositionedModel {
  model: AtlasModelRecord;
  x: number;
  y: number;
}

export interface PositionedRelation {
  relation: AtlasRelationRecord;
  source: PositionedModel;
  target: PositionedModel;
  curveOffset: number;
}
