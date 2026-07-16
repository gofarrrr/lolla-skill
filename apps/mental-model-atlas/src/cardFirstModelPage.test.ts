import { describe, expect, it, vi } from "vitest";

import cardFirstPage from "../public/data/card-first-v1/pages/model-abstraction.json";
import {
  CARD_FIRST_RELATION_INDICES,
  CardFirstContractError,
  loadCardFirstModelPage,
  validateCardFirstModelPage,
} from "./cardFirstModelPage";

describe("card-first model page contract", () => {
  it("accepts the frozen v2 artifact while the v1 validator remains separate", () => {
    const page = validateCardFirstModelPage(cardFirstPage);
    expect(page.model.model_id).toBe("abstraction");
    expect(page.source_card.coverage.status).toBe("complete");
    expect(page.coverage.status).toBe("partial");
    expect(page.connections.records.map((record) => record.source_record_index)).toEqual(
      CARD_FIRST_RELATION_INDICES,
    );
  });

  it.each([
    ["line gap", (page: any) => page.source_card.line_map.splice(4, 1)],
    ["line duplicate", (page: any) => page.source_card.line_map.splice(4, 0, structuredClone(page.source_card.line_map[4]))],
    ["line reorder", (page: any) => page.source_card.line_map.splice(6, 2, page.source_card.line_map[7], page.source_card.line_map[6])],
    ["heading level", (page: any) => { page.source_card.line_map[6].heading_level = 3; }],
    ["false source count", (page: any) => { page.source_card.coverage.rendered_substantive_line_count = 59; }],
    ["KG field drop", (page: any) => { delete page.operational_curation.record.heuristics; }],
    ["relation index", (page: any) => { page.connections.records[0].source_record_index = 2; }],
    ["relation direction", (page: any) => { page.connections.records[0].focus_direction = "incoming"; }],
    ["blanket complete", (page: any) => { page.coverage.status = "complete"; }],
  ])("fails closed on %s drift", (_label, mutate) => {
    const page = structuredClone(cardFirstPage);
    mutate(page);
    expect(() => validateCardFirstModelPage(page)).toThrow(CardFirstContractError);
  });

  it("hash-verifies the exact source and full KG record in the async loader", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(cardFirstPage), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })),
    );
    await expect(loadCardFirstModelPage("abstraction")).resolves.toMatchObject({
      model: { model_id: "abstraction" },
    });
  });

  it("rejects source text that passes shape but fails the byte hash", async () => {
    const changed = structuredClone(cardFirstPage);
    changed.source_card.source_text = changed.source_card.source_text.replace(
      "Comprehensive",
      "ComprehensivX",
    );
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(changed), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })),
    );
    await expect(loadCardFirstModelPage("abstraction")).rejects.toThrow(
      /source hash/i,
    );
  });
});
