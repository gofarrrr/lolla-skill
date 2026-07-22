import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import ordinaryProjection from "../../public/data/phase1-v2/ordinary-navigation.json";
import type { AtlasProjection } from "../projection";
import SvgGraphSurface from "./SvgGraphSurface";

const projection = ordinaryProjection as AtlasProjection;

afterEach(cleanup);

describe("SVG Atlas graph grammar", () => {
  it("keeps the full field visible and exposes type, direction, motion, and labels", () => {
    const relations = projection.relations.slice(0, 8);
    const { container } = render(
      <SvgGraphSurface
        projection={projection}
        relations={relations}
        selectedModelId="critical-thinking"
        selectedRelationId={null}
        hoveredModelId={null}
        relatedModelIds={new Set(projection.models.map((model) => model.model_id))}
        visibleModelIds={new Set(projection.models.map((model) => model.model_id))}
        motionPaused={false}
        onSelectModel={() => undefined}
        onSelectRelation={() => undefined}
        onHoverModel={() => undefined}
      />,
    );

    const graph = container.querySelector("svg[data-renderer='svg']");
    expect(graph?.getAttribute("data-camera-transform")).toBe(
      "translate(0px, 0px) scale(1)",
    );
    expect(container.querySelectorAll(".graph-node")).toHaveLength(16);
    expect(container.querySelectorAll(".graph-node-aura")).toHaveLength(16);
    expect(container.querySelectorAll(".graph-node-label")).toHaveLength(16);
    expect(container.querySelectorAll(".graph-edge")).toHaveLength(relations.length);
    expect(container.querySelectorAll(".edge-flow-marker")).toHaveLength(
      relations.length,
    );
    expect(container.querySelectorAll("animateMotion")).toHaveLength(
      relations.length,
    );
    expect(
      container.querySelectorAll(".graph-edge[data-relation='antagonist']").length,
    ).toBeGreaterThan(0);
    expect(
      container.querySelectorAll(".graph-edge[data-relation='tension']").length,
    ).toBeGreaterThan(0);
    expect(container.querySelectorAll(".edge-line-tension-inner").length).toBeGreaterThan(0);
    expect(container.querySelectorAll(".edge-antagonist-cross").length).toBeGreaterThan(0);
    expect(container.querySelectorAll(".graph-marker")).toHaveLength(3);
  });
});
