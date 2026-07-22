import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ordinaryProjection from "../../public/data/phase1-v2/ordinary-navigation.json";
import { ProjectionProvider } from "../projectionContext";
import LibraryPage from "./LibraryPage";

describe("model library visitor language", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/models");
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(ordinaryProjection), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })),
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("presents the preview as a human library rather than a projection debugger", async () => {
    render(
      <ProjectionProvider>
        <LibraryPage />
      </ProjectionProvider>,
    );

    expect(await screen.findByRole("heading", { name: /browse mental models/i })).toBeTruthy();
    expect(screen.getByRole("searchbox", { name: /search models/i })).toBeTruthy();
    expect(screen.queryByText(/frozen slice/i)).toBeNull();
    expect(screen.queryByText(/phase 1/i)).toBeNull();
    expect(screen.queryByText(/canonical id/i)).toBeNull();
  });
});
