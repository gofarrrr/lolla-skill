import type { AtlasProjection, AtlasRelationRecord } from "../projection";
import type { PositionedModel, PositionedRelation } from "./graphTypes";

const WIDTH = 1000;
const HEIGHT = 700;
const PADDING_X = 72;
const PADDING_Y = 64;

export function positionModels(projection: AtlasProjection): PositionedModel[] {
  const coordinates = new Map(
    projection.layout.coordinates.map((coordinate) => [
      coordinate.model_id,
      coordinate,
    ]),
  );
  const available = projection.models
    .map((model) => ({ model, coordinate: coordinates.get(model.model_id) }))
    .filter(
      (
        value,
      ): value is {
        model: (typeof projection.models)[number];
        coordinate: { model_id: string; x: number; y: number };
      } => Boolean(value.coordinate),
    );
  if (available.length === 0) {
    return [];
  }
  const xs = available.map(({ coordinate }) => coordinate.x);
  const ys = available.map(({ coordinate }) => coordinate.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const xSpan = Math.max(1, maxX - minX);
  const ySpan = Math.max(1, maxY - minY);

  return available.map(({ model, coordinate }) => ({
    model,
    x: PADDING_X + ((coordinate.x - minX) / xSpan) * (WIDTH - PADDING_X * 2),
    y: PADDING_Y + ((coordinate.y - minY) / ySpan) * (HEIGHT - PADDING_Y * 2),
  }));
}

export function positionRelations(
  models: PositionedModel[],
  relations: AtlasRelationRecord[],
): PositionedRelation[] {
  const modelMap = new Map(models.map((model) => [model.model.model_id, model]));
  const pairCounts = new Map<string, number>();
  const pairIndices = new Map<string, number>();
  for (const relation of relations) {
    const key = pairKey(relation.source_model_id, relation.target_model_id);
    pairCounts.set(key, (pairCounts.get(key) ?? 0) + 1);
  }

  const positioned: PositionedRelation[] = [];
  for (const relation of relations) {
    const source = modelMap.get(relation.source_model_id);
    const target = modelMap.get(relation.target_model_id);
    if (!source || !target) {
      continue;
    }
    const key = pairKey(relation.source_model_id, relation.target_model_id);
    const count = pairCounts.get(key) ?? 1;
    const index = pairIndices.get(key) ?? 0;
    pairIndices.set(key, index + 1);
    positioned.push({
      relation,
      source,
      target,
      curveOffset: (index - (count - 1) / 2) * 24,
    });
  }
  return positioned;
}

export function curveGeometry(relation: PositionedRelation) {
  const { source, target, curveOffset } = relation;
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const distance = Math.max(1, Math.hypot(dx, dy));
  const perpendicularX = -dy / distance;
  const perpendicularY = dx / distance;
  const controlX = (source.x + target.x) / 2 + perpendicularX * curveOffset;
  const controlY = (source.y + target.y) / 2 + perpendicularY * curveOffset;
  return {
    controlX,
    controlY,
    midpointX: quadratic(source.x, controlX, target.x, 0.5),
    midpointY: quadratic(source.y, controlY, target.y, 0.5),
  };
}

export const GRAPH_VIEWBOX = `0 0 ${WIDTH} ${HEIGHT}`;
export const GRAPH_WIDTH = WIDTH;
export const GRAPH_HEIGHT = HEIGHT;

function pairKey(source: string, target: string): string {
  return [source, target].sort().join("\u0000");
}

function quadratic(start: number, control: number, end: number, t: number): number {
  return (1 - t) ** 2 * start + 2 * (1 - t) * t * control + t ** 2 * end;
}
