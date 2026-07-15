import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ordinaryProjection from "../../public/data/phase1/ordinary-navigation.json";
import hubPage1 from "../../public/data/phase1/confirmation-bias-hub-page-1.json";
import hubPage2 from "../../public/data/phase1/confirmation-bias-hub-page-2.json";
import { ProjectionProvider } from "../projectionContext";
import AtlasPage from "./AtlasPage";

describe("Atlas interaction state", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/atlas");
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify(ordinaryProjection), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("keeps committed selection while hover previews another model", async () => {
    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    const abstraction = await screen.findByRole("button", {
      name: "Select Abstraction",
    });
    fireEvent.click(abstraction);

    const selectedPanel = screen.getByRole("complementary", {
      name: "Selected model",
    });
    expect(within(selectedPanel).getByRole("heading", { name: "Abstraction" })).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("model")).toBe("abstraction");

    const criticalThinking = screen.getByRole("button", {
      name: "Select Critical Thinking",
    });
    fireEvent.pointerEnter(criticalThinking);

    expect(await screen.findByText("Preview — selection unchanged")).toBeTruthy();
    expect(within(selectedPanel).getByRole("heading", { name: "Abstraction" })).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("model")).toBe("abstraction");
  });

  it("distinguishes a valid zero-result filter from load failure", async () => {
    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );
    const search = await screen.findByRole("searchbox", { name: "Find a model" });
    fireEvent.change(search, { target: { value: "no-such-canonical-model" } });

    await waitFor(() => {
      expect(screen.getAllByText("Completed zero").length).toBeGreaterThan(0);
    });
    expect(screen.queryByText("Projection failed")).toBeNull();
  });

  it("loads a genuinely different frozen hub page from durable URL state", async () => {
    window.history.replaceState(
      null,
      "",
      "/atlas?fixture=confirmation-bias-hub&model=confirmation-bias",
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const payload = url.includes("hub-page-2.json") ? hubPage2 : hubPage1;
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    expect(await screen.findByText("Page 1 of 6")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(await screen.findByText("Page 2 of 6")).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("page")).toBe("2");
    expect(fetchMock.mock.calls.some(([input]) => String(input).includes(
      "confirmation-bias-hub-page-2.json",
    ))).toBe(true);
  });

  it("keeps projection failure distinct and links to a route without projection data", async () => {
    window.history.replaceState(
      null,
      "",
      "/atlas?fixture=medium-confidence-relation",
    );
    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new Error("frozen projection unavailable");
    }));

    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    expect(await screen.findByText("Projection failed")).toBeTruthy();
    expect(screen.queryByText("Completed zero")).toBeNull();
    expect(
      screen
        .getByRole("link", { name: "Open product boundary" })
        .getAttribute("href"),
    ).toBe("/learn");
  });
});
