import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
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

  it("guides one chapter at a time while keeping the exact source available", () => {
    const { container } = render(
      <RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />,
    );
    expect(screen.getAllByText("Step 1 of 5")).toHaveLength(2);
    expect(container.querySelector("#reader-chapter-understand")?.hasAttribute("hidden")).toBe(false);
    expect(container.querySelector("#reader-chapter-judge")?.hasAttribute("hidden")).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: /3 know its limits/i }));
    expect(screen.getAllByText("Step 3 of 5")).toHaveLength(2);
    expect(container.querySelector("#reader-chapter-understand")?.hasAttribute("hidden")).toBe(true);
    expect(container.querySelector("#reader-chapter-judge")?.hasAttribute("hidden")).toBe(false);
    expect(screen.getByRole("button", { name: /3 know its limits/i }).getAttribute("aria-current")).toBe("step");

    fireEvent.click(screen.getByRole("button", { name: /5 apply it safely/i }));
    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(5);
    expect(screen.getByText(/scroll horizontally to read every column/i)).toBeTruthy();
    expect(table.closest("[role='region']")?.getAttribute("aria-describedby")).toBe(
      "source-table-scroll-cue",
    );
    expect(screen.getByRole("heading", { name: /learn abstraction/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /put abstraction to work/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /what abstraction connects to/i })).toBeTruthy();
    expect(container.querySelectorAll(".model-connection")).toHaveLength(12);
    expect(screen.getByRole("button", { name: /7 works with/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /4 productive tensions/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /1 direct conflicts/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /use the model; keep judging the situation/i })).toBeTruthy();
    expect(screen.getByText(/what remains outside this local learning preview/i)).toBeTruthy();
    expect(screen.getByRole("heading", { name: /a local learning preview/i })).toBeTruthy();
    const reviewSummary = screen.getByText(/review status, exact sources, and boundaries/i);
    const reviewDetails = reviewSummary.closest("details");
    expect(reviewDetails?.hasAttribute("open")).toBe(false);
    expect(within(reviewDetails as HTMLElement).getByText(/content generation/i)).toBeTruthy();
  });

  it("preserves the parallel ally and tension records as separate cards", () => {
    const { container } = render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    const matching = [...container.querySelectorAll(".model-connection")].filter((node) =>
      node.textContent?.toLowerCase().includes("first principles thinking"),
    );
    expect(matching).toHaveLength(2);
  });

  it("keeps technical source residue outside the primary journey and offers full-source inspection", () => {
    render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    const residue = screen.getByText(/structured tension curation/i);
    const appendix = residue.closest("details");
    expect(appendix?.hasAttribute("hidden")).toBe(true);
    expect(appendix?.hasAttribute("open")).toBe(false);
    fireEvent.click(screen.getByRole("button", { name: /4 see the connections/i }));
    expect(screen.getByText(/original relationship curation notes/i)).toBeTruthy();
    expect(appendix?.hasAttribute("hidden")).toBe(false);
    expect(appendix?.hasAttribute("open")).toBe(false);

    fireEvent.click(screen.getByRole("button", { name: /view exact source as one document/i }));
    expect(screen.getByText(/complete source view/i)).toBeTruthy();
    expect(appendix?.hasAttribute("open")).toBe(true);
    expect(screen.queryByRole("button", { name: /next step/i })).toBeNull();
  });
});
