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
    expect(screen.queryByText("Comprehensive Briefing Document on Abstraction")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /read the full article/i }));
    const sourceNodes = [...container.querySelectorAll("[data-source-line]")];
    expect(sourceNodes.map((node) => Number(node.getAttribute("data-source-line")))).toEqual(
      CARD_FIRST_SUBSTANTIVE_LINES,
    );
    const sourceHeadings = sourceNodes.filter((node) => /^H[1-3]$/.test(node.tagName));
    expect(sourceHeadings).toHaveLength(14);
    expect(sourceHeadings.map((node) => node.tagName)).toEqual([
      "H2", "H3", "H2", "H3", "H3", "H2", "H3", "H3", "H2", "H3", "H3", "H2", "H3", "H3",
    ]);
    expect(container.querySelector(".full-source-title")?.textContent).toContain(
      "Comprehensive Briefing Document on Abstraction",
    );
    expect(screen.getByRole("heading", { level: 1, name: "Abstraction" })).toBeTruthy();
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
    expect(screen.getByRole("region", { name: /understand abstraction/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /put abstraction to work/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /read the lines around abstraction/i })).toBeTruthy();
    expect(container.querySelectorAll(".model-connection")).toHaveLength(12);
    expect(screen.getByRole("tab", { name: /7 ally.*works with/i })).toBeTruthy();
    expect(screen.getByRole("tab", { name: /4 tension.*compare the tradeoff/i })).toBeTruthy();
    expect(screen.getByRole("tab", { name: /1 antagonist.*pushes against/i })).toBeTruthy();
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

  it("makes relationship type and direction legible without depending on color", () => {
    const { container } = render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    expect(screen.getByText(/how to read the line styles/i)).toBeTruthy();
    expect(screen.getByText(/solid line/i)).toBeTruthy();
    expect(screen.getByText(/double line/i)).toBeTruthy();
    expect(screen.getByText(/dashed line/i)).toBeTruthy();

    const paths = [...container.querySelectorAll(".relationship-path")];
    expect(paths).toHaveLength(3);
    expect(paths[0].getAttribute("aria-label")).toMatch(
      /authored relationship: abstraction works with systems thinking/i,
    );
    expect(container.querySelectorAll("[data-focus-direction='outgoing']")).toHaveLength(5);
    expect(container.querySelectorAll("[data-focus-direction='incoming']")).toHaveLength(7);
    expect(container.querySelectorAll(".relationship-nonclaim")).toHaveLength(1);
    expect(screen.getByText(/not scores, recommendations, or proof/i)).toBeTruthy();

    fireEvent.click(screen.getByRole("tab", { name: /4 tension.*compare the tradeoff/i }));
    expect(screen.getByLabelText(/abstraction stays in productive tension with first principles thinking/i)).toBeTruthy();
  });

  it("offers a functional four-stop page path without changing source or relation identity", () => {
    const { container } = render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    const pagePath = screen.getByRole("navigation", { name: /on this model page/i });
    expect(within(pagePath).getByRole("link", { name: /01 understand/i }).getAttribute("href")).toBe("#guided-reader-start");
    expect(within(pagePath).getByRole("link", { name: /02 use it/i }).getAttribute("href")).toBe("#model-practice");
    expect(within(pagePath).getByRole("link", { name: /03 connections/i }).getAttribute("href")).toBe("#model-relations");
    expect(within(pagePath).getByRole("link", { name: /04 perspective/i }).getAttribute("href")).toBe("#model-boundary");
    expect(container.querySelectorAll(".model-connection")).toHaveLength(12);
  });

  it("keeps the primary learning journey human-facing", () => {
    render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    expect(screen.getAllByText(/simplify reality, extract patterns/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/reality is too noisy to reason about directly/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/no longer stays anchored to concrete evidence/i).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: /read the full article/i })).toBeTruthy();
    expect(screen.queryByRole("heading", { name: /learn abstraction/i })).toBeNull();
    expect(screen.queryByText(/comprehensive briefing document on abstraction/i)).toBeNull();
    expect(screen.queryByText(/read one chapter at a time/i)).toBeNull();
    expect(screen.queryByText(/compiled curation/i)).toBeNull();
    expect(screen.queryByText(/normalized · high confidence/i)).toBeNull();
    expect(screen.queryByText(/source-file locator/i)).toBeNull();
    expect(screen.queryByText(/record name/i)).toBeNull();
  });

  it("uses keyboard-operable tabs for relationship types", () => {
    render(<RenderedModelPage page={validateCardFirstModelPage(cardFirstPage)} />);
    const allyTab = screen.getByRole("tab", { name: /7 ally.*works with/i });
    const tensionTab = screen.getByRole("tab", { name: /4 tension.*compare the tradeoff/i });
    expect(allyTab.getAttribute("aria-selected")).toBe("true");
    expect(tensionTab.getAttribute("tabindex")).toBe("-1");

    fireEvent.keyDown(allyTab, { key: "ArrowRight" });
    expect(tensionTab.getAttribute("aria-selected")).toBe("true");
    expect(screen.getByRole("tabpanel", { name: /tension.*compare the tradeoff/i })).toBeTruthy();
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

    fireEvent.click(screen.getByRole("button", { name: /read the full article/i }));
    expect(screen.getAllByText(/full article/i).length).toBeGreaterThan(0);
    expect(appendix?.hasAttribute("open")).toBe(true);
    expect(screen.queryByRole("button", { name: /next step/i })).toBeNull();
  });
});
