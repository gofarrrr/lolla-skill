import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { StrictMode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ordinaryProjection from "../../public/data/phase1/ordinary-navigation.json";
import navigationIndex from "../../public/data/navigation-v1/neighborhood-index.json";
import hubPage1 from "../../public/data/phase1/confirmation-bias-hub-page-1.json";
import hubPage2 from "../../public/data/phase1/confirmation-bias-hub-page-2.json";
import { ProjectionProvider } from "../projectionContext";
import AtlasPage from "./AtlasPage";

describe("Atlas interaction state", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/atlas");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) =>
        new Response(JSON.stringify(
          String(input).includes("navigation-v1")
            ? navigationIndex
            : ordinaryProjection,
        ), {
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
      <StrictMode>
        <ProjectionProvider>
          <AtlasPage motionPaused />
        </ProjectionProvider>
      </StrictMode>,
    );

    const abstraction = await screen.findByRole(
      "button",
      { name: "Select Abstraction" },
      { timeout: 5_000 },
    );
    fireEvent.click(abstraction);

    const selectedPanel = await screen.findByRole("complementary", {
      name: "Selected model",
    });
    expect(within(selectedPanel).getByRole("heading", { name: "Abstraction" })).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("model")).toBe("abstraction");
    expect(
      document
        .querySelector("svg[data-renderer='svg']")
        ?.getAttribute("data-camera-transform"),
    ).toBe("translate(0px, 0px) scale(1)");

    const firstPrinciples = await screen.findByRole("button", {
      name: "Select First Principles Thinking",
    });
    fireEvent.pointerEnter(firstPrinciples);

    expect(await screen.findByText("Preview")).toBeTruthy();
    expect(within(selectedPanel).getByRole("heading", { name: "Abstraction" })).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("model")).toBe("abstraction");

    fireEvent.click(within(selectedPanel).getByRole("button", { name: "Clear" }));
    await waitFor(() => {
      expect(document.activeElement?.getAttribute("data-model-id")).toBe(
        "abstraction",
      );
    });
  });

  it("rebuilds the exact canonical neighborhood when exploration moves to another model", async () => {
    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    fireEvent.click(await screen.findByRole("button", {
      name: "Select Root Cause Analysis",
    }));

    expect(await screen.findByText("Root Cause Analysis · 14 connections shown.")).toBeTruthy();
    expect(document.querySelectorAll("[data-relation-id]")).toHaveLength(14);
    expect(await screen.findByRole("button", {
      name: "Select Five Whys Method",
    })).toBeTruthy();
    expect(document.querySelector("[data-projection-id*='root-cause-analysis']")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Select Five Whys Method" }));
    expect(await screen.findByText(/Five Whys Method · \d+ connections shown\./)).toBeTruthy();
    expect(new URL(window.location.href).searchParams.get("model")).toBe(
      "five-whys-method",
    );
    expect(document.querySelector("[data-projection-id*='five-whys-method']")).toBeTruthy();
  });

  it("keeps local fixture and renderer plumbing out of the ordinary visitor controls", async () => {
    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    expect(await screen.findByRole("heading", { name: /explore how ideas connect/i })).toBeTruthy();
    expect(screen.queryByRole("combobox", { name: /review fixture/i })).toBeNull();
    expect(screen.queryByRole("combobox", { name: /visual renderer/i })).toBeNull();
    expect(screen.getByRole("searchbox", { name: /find a model/i })).toBeTruthy();
  });

  it("ignores review-only fixture and renderer parameters outside explicit review mode", async () => {
    window.history.replaceState(
      null,
      "",
      "/atlas?fixture=confirmation-bias-hub&renderer=canvas&model=root-cause-analysis",
    );

    render(
      <ProjectionProvider>
        <AtlasPage motionPaused />
      </ProjectionProvider>,
    );

    expect(await screen.findByText("Root Cause Analysis · 14 connections shown.")).toBeTruthy();
    expect(document.querySelector("svg[data-renderer='svg']")).toBeTruthy();
    expect(document.querySelector("canvas[data-renderer='canvas']")).toBeNull();
    expect(screen.queryByRole("combobox", { name: /review fixture/i })).toBeNull();
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
      expect(screen.getAllByText("No models found").length).toBeGreaterThan(0);
    });
    expect(screen.queryByText("Projection failed")).toBeNull();
  });

  it("loads a genuinely different frozen hub page from durable URL state", async () => {
    window.history.replaceState(
      null,
      "",
      "/atlas?review=1&fixture=confirmation-bias-hub&model=confirmation-bias",
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
      "/atlas?review=1&fixture=medium-confidence-relation",
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
