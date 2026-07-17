import { describe, expect, it } from "vitest";

import { atlasStateHref, parseAtlasState } from "./atlasState";

describe("Atlas URL state", () => {
  it("round-trips durable state while preserving fixture and renderer switches", () => {
    const current = new URL(
      "https://atlas.test/atlas?fixture=mixed-parallel-relations&renderer=canvas&model=abstraction&relations=ally,tension&q=first&page=2&view=list",
    );
    const state = parseAtlasState(current);

    expect(state).toEqual({
      selectedModelId: "abstraction",
      selectedRelationId: null,
      relationTypes: ["ally", "tension"],
      query: "first",
      relationPage: 2,
      view: "list",
    });

    const href = atlasStateHref(current, {
      selectedRelationId: "abstraction__first-principles-thinking__ally",
    });
    const next = new URL(href, "https://atlas.test");
    expect(next.searchParams.get("fixture")).toBe("mixed-parallel-relations");
    expect(next.searchParams.get("renderer")).toBe("canvas");
    expect(next.searchParams.get("model")).toBe("abstraction");
    expect(next.searchParams.get("relation")).toBe(
      "abstraction__first-principles-thinking__ally",
    );
  });

  it("quarantines malformed controlled values instead of repairing them", () => {
    const state = parseAtlasState(
      new URL(
        "https://atlas.test/atlas?relations=ally,proof,tension&page=-3&view=unknown",
      ),
    );
    expect(state.relationTypes).toEqual(["ally", "tension"]);
    expect(state.relationPage).toBe(1);
    expect(state.view).toBe("graph");
  });
});
