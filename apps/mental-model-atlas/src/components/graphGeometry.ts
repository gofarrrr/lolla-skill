import type { AtlasProjection, AtlasRelationRecord } from "../projection";
import type { PositionedModel, PositionedRelation } from "./graphTypes";

const WIDTH = 1000;
const HEIGHT = 700;
const PADDING_X = 72;
const PADDING_Y = 64;

export interface PositionedModelLabel {
  modelId: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

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

  const paddingX = available.length > 20 ? 210 : PADDING_X;
  return available.map(({ model, coordinate }) => ({
    model,
    x: paddingX + ((coordinate.x - minX) / xSpan) * (WIDTH - paddingX * 2),
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

export function positionModelLabels(
  models: PositionedModel[],
): Map<string, PositionedModelLabel> {
  if (models.length > 20) {
    return positionDenseModelLabels(models);
  }
  const labels = new Map<string, PositionedModelLabel>();
  const occupied: PositionedModelLabel[] = [];
  const ordered = [...models].sort(
    (left, right) =>
      right.model.display_name.length - left.model.display_name.length ||
      left.y - right.y ||
      left.x - right.x,
  );

  for (const positioned of ordered) {
    const width = Math.min(
      178,
      Math.max(82, positioned.model.display_name.length * 7.2 + 18),
    );
    const height = 24;
    const preferRight = positioned.x < WIDTH / 2;
    const candidates = [
      preferRight
        ? { x: positioned.x + 16, y: positioned.y - height / 2 }
        : { x: positioned.x - width - 16, y: positioned.y - height / 2 },
      { x: positioned.x - width / 2, y: positioned.y - height - 18 },
      { x: positioned.x - width / 2, y: positioned.y + 18 },
      preferRight
        ? { x: positioned.x - width - 16, y: positioned.y - height / 2 }
        : { x: positioned.x + 16, y: positioned.y - height / 2 },
    ].map((candidate) => ({
      modelId: positioned.model.model_id,
      x: clamp(candidate.x, 8, WIDTH - width - 8),
      y: clamp(candidate.y, 8, HEIGHT - height - 8),
      width,
      height,
    }));

    const otherNodes = models.filter(
      ({ model }) => model.model_id !== positioned.model.model_id,
    );
    const scored = candidates.map((candidate, index) => {
      const labelOverlap = occupied.reduce(
        (total, label) => total + overlapArea(candidate, label),
        0,
      );
      const nodeOverlap = otherNodes.reduce(
        (total, node) =>
          total +
          overlapArea(candidate, {
            x: node.x - 13,
            y: node.y - 13,
            width: 26,
            height: 26,
          }),
        0,
      );
      return {
        candidate,
        score: labelOverlap * 100 + nodeOverlap * 30 + index,
      };
    });
    scored.sort((left, right) => left.score - right.score);
    const selected = scored[0].candidate;
    labels.set(positioned.model.model_id, selected);
    occupied.push(selected);
  }

  return labels;
}

function positionDenseModelLabels(
  models: PositionedModel[],
): Map<string, PositionedModelLabel> {
  const labels = new Map<string, PositionedModelLabel>();
  const left: PositionedModel[] = [];
  const right: PositionedModel[] = [];
  for (const model of [...models].sort((a, b) => a.x - b.x || a.y - b.y)) {
    const preferred = model.x < WIDTH / 2 ? left : right;
    const alternate = preferred === left ? right : left;
    (preferred.length <= alternate.length + 2 ? preferred : alternate).push(model);
  }
  for (const [side, lane] of [["left", left], ["right", right]] as const) {
    lane.sort((a, b) => a.y - b.y || a.x - b.x);
    const availableHeight = HEIGHT - 16 - 24;
    const step = lane.length > 1 ? availableHeight / (lane.length - 1) : 0;
    lane.forEach((positioned, index) => {
      const width = Math.min(
        178,
        Math.max(82, positioned.model.display_name.length * 7.2 + 18),
      );
      labels.set(positioned.model.model_id, {
        modelId: positioned.model.model_id,
        x: side === "left" ? 8 : WIDTH - width - 8,
        y: 8 + index * step,
        width,
        height: 24,
      });
    });
  }
  return labels;
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

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, value));
}

function overlapArea(
  first: Pick<PositionedModelLabel, "x" | "y" | "width" | "height">,
  second: Pick<PositionedModelLabel, "x" | "y" | "width" | "height">,
): number {
  const width = Math.max(
    0,
    Math.min(first.x + first.width, second.x + second.width) -
      Math.max(first.x, second.x),
  );
  const height = Math.max(
    0,
    Math.min(first.y + first.height, second.y + second.height) -
      Math.max(first.y, second.y),
  );
  return width * height;
}
