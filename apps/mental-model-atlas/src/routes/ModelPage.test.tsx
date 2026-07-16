import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import cardFirstPage from "../../public/data/card-first-v1/pages/model-abstraction.json";
import {
  CARD_FIRST_SUBSTANTIVE_LINES,
  validateCardFirstModelPage,
} from "../cardFirstModelPage";
import { RenderedModelPage } from "./ModelPage";

afterEach(cleanup);

describe("card-first Abstraction model page", () => {
  it("renders every exact source heading and substantive line from the one source authority", () => {
    const { container } = render(
      <RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />,
    );
    const sourceNodes = [...container.querySelectorAll("[data-source-line]")];
    expect(sourceNodes.map((node) => Number(node.getAttribute("data-source-line")))).toEqual(
      CARD_FIRST_SUBSTANTIVE_LINES,
    );
    const sourceHeadings = sourceNodes.filter((node) => /^H[1-3]$/.test(node.tagName));
    expect(sourceHeadings).toHaveLength(15);
    expect(sourceHeadings.map((node) => node.tagName)).toEqual([
      "H1", "H2", "H3", "H2", "H3", "H3", "H2", "H3", "H3", "H2", "H3", "H3", "H2", "H3", "H3",
    ]);
  });

  it("renders the source table, source labels, full KG layer, and all exact connections", () => {
    const { container } = render(
      <RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />,
    );
    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(5);
    expect(screen.getByText(/scroll horizontally to read every column/i)).toBeTruthy();
    expect(table.closest("[role='region']")?.getAttribute("aria-describedby")).toBe(
      "source-table-scroll-cue",
    );
    expect(screen.getByRole("heading", { name: /full model card/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /compiled knowledge graph/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /relationship-graph connections/i })).toBeTruthy();
    expect(container.querySelectorAll(".model-connection")).toHaveLength(12);
    expect(screen.getByText("5", { selector: ".connection-counts strong" })).toBeTruthy();
    expect(screen.getAllByText("7", { selector: ".connection-counts strong" })).toHaveLength(2);
    expect(screen.getByText(/source card is complete; this learning page is partial/i)).toBeTruthy();
    expect(screen.getByText(/reviewed runtime affordance projection/i)).toBeTruthy();
    expect(screen.getAllByText(/curated teacher journeys/i).length).toBeGreaterThan(0);
  });

  it("preserves the parallel ally and tension records as separate cards", () => {
    const { container } = render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    const matching = [...container.querySelectorAll(".model-connection")].filter((node) =>
      node.textContent?.toLowerCase().includes("abstraction → first principles thinking"),
    );
    expect(matching).toHaveLength(2);
  });
});
