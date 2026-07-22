import { describe, expect, it } from "vitest";

import ordinaryProjection from "../../public/data/phase1-v2/ordinary-navigation.json";
import type { AtlasProjection } from "../projection";
import {
  GRAPH_HEIGHT,
  GRAPH_WIDTH,
  positionModelLabels,
  positionModels,
} from "./graphGeometry";

const projection = ordinaryProjection as AtlasProjection;

describe("Atlas label geometry", () => {
  it("keeps every model label inside the full-field graph without collisions", () => {
    const models = positionModels(projection);
    const labels = [...positionModelLabels(models).values()];

    expect(labels).toHaveLength(models.length);
    for (const label of labels) {
      expect(label.x).toBeGreaterThanOrEqual(0);
      expect(label.y).toBeGreaterThanOrEqual(0);
      expect(label.x + label.width).toBeLessThanOrEqual(GRAPH_WIDTH);
      expect(label.y + label.height).toBeLessThanOrEqual(GRAPH_HEIGHT);
    }

    for (const [index, label] of labels.entries()) {
      for (const other of labels.slice(index + 1)) {
        expect(overlapArea(label, other)).toBe(0);
      }
    }
  });
});

function overlapArea(
  first: { x: number; y: number; width: number; height: number },
  second: { x: number; y: number; width: number; height: number },
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
