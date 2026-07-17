import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ordinaryProjection from "../../public/data/phase1/ordinary-navigation.json";
import type { AtlasProjection } from "../projection";
import { GraphSurface } from "./GraphSurface";

const projection = ordinaryProjection as AtlasProjection;

describe("Graph renderer boundary", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("preserves a non-canvas route when Canvas initialization fails", async () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);

    render(
      <GraphSurface
        renderer="canvas"
        projection={projection}
        relations={[]}
        selectedModelId={null}
        selectedRelationId={null}
        hoveredModelId={null}
        relatedModelIds={new Set()}
        visibleModelIds={new Set(projection.models.map((model) => model.model_id))}
        onSelectModel={() => undefined}
        onSelectRelation={() => undefined}
        onHoverModel={() => undefined}
        fallback={
          <section role="alert">
            <h2>The text Atlas remains available.</h2>
            <a href="#accessible-atlas">Use accessible view</a>
          </section>
        }
      />,
    );

    expect(
      await screen.findByRole(
        "heading",
        { name: "The text Atlas remains available." },
        { timeout: 5_000 },
      ),
    ).toBeTruthy();
    expect(screen.getByRole("link", { name: "Use accessible view" })).toBeTruthy();
  }, 10_000);
});
