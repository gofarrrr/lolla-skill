import { describe, expect, it } from "vitest";

import navigationIndex from "../public/data/navigation-v1/neighborhood-index.json";
import {
  buildNeighborhoodProjection,
  validateNavigationIndex,
} from "./navigation";
import { positionModelLabels, positionModels } from "./components/graphGeometry";


describe("canonical neighborhood navigation", () => {
  const index = validateNavigationIndex(navigationIndex);

  it("loads the complete sanitized canonical relationship index", () => {
    expect(index.models).toHaveLength(222);
    expect(index.relations).toHaveLength(1_358);
    expect(index.scope.selection_operation).toBe("exact_incident_edge_filter_only");
    expect(index.scope.browser_semantic_inference).toBe(false);
  });

  it("expands a model beyond the ordinary fixture page", async () => {
    const rootCause = await buildNeighborhoodProjection(index, "root-cause-analysis", 1);

    expect(rootCause.fixture_id).toBe("canonical_neighborhood");
    expect(rootCause.scope.focus_model_id).toBe("root-cause-analysis");
    expect(rootCause.page.eligible_count).toBe(14);
    expect(rootCause.page.shown_count).toBe(14);
    expect(rootCause.relations.every((relation) =>
      relation.source_model_id === "root-cause-analysis" ||
      relation.target_model_id === "root-cause-analysis",
    )).toBe(true);
    expect(rootCause.models.some((model) => model.model_id === "five-whys-method")).toBe(true);
  });

  it("pages a high-fan-in neighborhood without losing exact counts", async () => {
    const first = await buildNeighborhoodProjection(index, "confirmation-bias", 1);
    const sixth = await buildNeighborhoodProjection(index, "confirmation-bias", 6);

    expect(first.page).toMatchObject({
      eligible_count: 233,
      shown_count: 40,
      before_count: 0,
      after_count: 193,
    });
    expect(sixth.page).toMatchObject({
      eligible_count: 233,
      shown_count: 33,
      before_count: 200,
      after_count: 0,
    });
    expect(new Set([
      ...first.page.relation_ids,
      ...sixth.page.relation_ids,
    ]).size).toBe(73);
    for (const projection of [first, sixth]) {
      const labels = [...positionModelLabels(positionModels(projection)).values()];
      expect(labels).toHaveLength(projection.models.length);
      expect(countOverlaps(labels)).toBe(0);
      expect(labels.every((label) =>
        label.x >= 0 && label.y >= 0 &&
        label.x + label.width <= 1_000 && label.y + label.height <= 700,
      )).toBe(true);
    }
  });

  it("rejects an unknown model and an out-of-range page", async () => {
    await expect(buildNeighborhoodProjection(index, "not-a-model", 1)).rejects.toThrow(
      /not present in the canonical navigation index/,
    );
    await expect(buildNeighborhoodProjection(index, "abstraction", 2)).rejects.toThrow(
      /outside the neighborhood page range/,
    );
  });
});

function countOverlaps(
  labels: Array<{ x: number; y: number; width: number; height: number }>,
): number {
  let overlaps = 0;
  for (let left = 0; left < labels.length; left += 1) {
    for (let right = left + 1; right < labels.length; right += 1) {
      const a = labels[left];
      const b = labels[right];
      if (
        Math.min(a.x + a.width, b.x + b.width) > Math.max(a.x, b.x) &&
        Math.min(a.y + a.height, b.y + b.height) > Math.max(a.y, b.y)
      ) {
        overlaps += 1;
      }
    }
  }
  return overlaps;
}
