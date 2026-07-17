import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import navigationIndex from "../../public/data/navigation-v1/neighborhood-index.json";
import phase1RelationPage from "../../public/data/phase1/pages/relation-abstraction-first-principles-thinking-ally.json";
import ModelPage from "./ModelPage";
import RelationPage from "./RelationPage";

describe("canonical identity fallback", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/atlas");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const payload = String(input).includes("navigation-v1")
          ? navigationIndex
          : phase1RelationPage;
        return new Response(JSON.stringify(payload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }),
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("keeps a canonical model outside the orientation slice distinct from an unknown model", async () => {
    render(<ModelPage slug="adaptation" />);

    expect(await screen.findByRole("heading", { name: "Adaptation" })).toBeTruthy();
    expect(screen.getByText(/this canonical model exists/i)).toBeTruthy();
    expect(screen.queryByText("Model page not found")).toBeNull();
    expect(
      screen.getByRole("link", { name: /see adaptation in the atlas/i }).getAttribute("href"),
    ).toBe("/atlas?model=adaptation");
  });

  it("keeps an exact canonical relation outside the orientation slice navigable", async () => {
    const relationId =
      "causal-attribution-resistance__root-cause-analysis__ally";
    render(<RelationPage relationId={relationId} />);

    expect(
      await screen.findByRole("heading", {
        name: "Causal Attribution Resistance → Root Cause Analysis",
      }),
    ).toBeTruthy();
    expect(screen.queryByText("Relation not found")).toBeNull();
    const href = screen
      .getByRole("link", { name: /show exact record in atlas/i })
      .getAttribute("href");
    expect(href).toContain("model=causal-attribution-resistance");
    expect(href).toContain(`relation=${relationId}`);
  });
});
