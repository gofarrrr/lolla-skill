import { describe, expect, it, vi } from "vitest";

import hubProjection from "../public/data/phase1-v2/confirmation-bias-hub-page-1.json";
import hubProjectionPage2 from "../public/data/phase1-v2/confirmation-bias-hub-page-2.json";
import hubProjectionPage6 from "../public/data/phase1-v2/confirmation-bias-hub-page-6.json";
import bidirectionalProjection from "../public/data/phase1-v2/explicit-bidirectionality.json";
import mediumConfidenceProjection from "../public/data/phase1-v2/medium-confidence-relation.json";
import parallelProjection from "../public/data/phase1-v2/mixed-parallel-relations.json";
import ordinaryProjection from "../public/data/phase1-v2/ordinary-navigation.json";
import modelPage from "../public/data/phase1-v2/pages/model-abstraction.json";
import relationPage from "../public/data/phase1-v2/pages/relation-abstraction-first-principles-thinking-ally.json";
import {
  ProjectionContractError,
  loadProjection,
  projectionUrl,
  validateModelPage,
  validateProjection,
  validateRelationPage,
} from "./projection";

describe("Atlas app-side contract", () => {
  it("accepts every frozen Phase 1 projection without collapsing semantic fixtures", () => {
    const ordinary = validateProjection(ordinaryProjection);
    const parallel = validateProjection(parallelProjection);
    const bidirectional = validateProjection(bidirectionalProjection);
    const hub = validateProjection(hubProjection);
    const hubPage2 = validateProjection(hubProjectionPage2);
    const hubPage6 = validateProjection(hubProjectionPage6);
    const mediumConfidence = validateProjection(mediumConfidenceProjection);

    expect(ordinary.models).toHaveLength(16);
    expect(
      parallel.relations.filter(
        (relation) =>
          relation.source_model_id === "abstraction" &&
          relation.target_model_id === "first-principles-thinking",
      ).map((relation) => relation.relation_type),
    ).toEqual(["ally", "tension"]);
    expect(
      new Set(
        bidirectional.relations.map(
          (relation) => `${relation.source_model_id}->${relation.target_model_id}`,
        ),
      ),
    ).toEqual(
      new Set([
        "active-listening->prisoners-dilemma",
        "prisoners-dilemma->active-listening",
      ]),
    );
    expect(hub.page.eligible_count).toBe(233);
    expect(hub.page.shown_count).toBe(40);
    expect(hub.page.omitted_count).toBe(193);
    expect(hubPage2.page.page_number).toBe(2);
    expect(hubPage2.page.before_count).toBe(40);
    expect(hubPage6.page.page_number).toBe(6);
    expect(hubPage6.page.shown_count).toBe(33);
    expect(hubPage6.page.after_count).toBe(0);
    expect(hub.page.relation_ids).not.toEqual(hubPage2.page.relation_ids);
    expect(mediumConfidence.relations[0].confidence).toBe("medium");
    expect(mediumConfidence.non_claims).toContain(
      "not_relation_truth_certification",
    );
  });

  it("maps durable hub pages to distinct frozen projection assets", () => {
    expect(projectionUrl("confirmation-bias-hub", 1)).toContain(
      "confirmation-bias-hub-page-1.json",
    );
    expect(projectionUrl("confirmation-bias-hub", 2)).toContain(
      "confirmation-bias-hub-page-2.json",
    );
  });

  it("accepts the source-copied model and relation page contracts", () => {
    expect(validateModelPage(modelPage).model.model_id).toBe("abstraction");
    const relation = validateRelationPage(relationPage);
    expect(relation.sections.why_it_matters.text).toContain("Corrective complement");
    expect(relation.sections.parallel_record_context.parallel_relation_ids).toHaveLength(2);
  });

  it("fails closed when the public schema identity drifts", () => {
    expect(() =>
      validateProjection({ ...ordinaryProjection, schema_version: "unknown" }),
    ).toThrow(ProjectionContractError);
  });

  it("fails closed on page custody and confidence drift", () => {
    const reordered = structuredClone(hubProjection);
    reordered.page.relation_ids = [...reordered.page.relation_ids].reverse();
    expect(() => validateProjection(reordered)).toThrow(ProjectionContractError);

    const zeroPage = structuredClone(hubProjection);
    zeroPage.page.page_number = 0;
    expect(() => validateProjection(zeroPage)).toThrow(ProjectionContractError);

    const wrongBound = structuredClone(hubProjection);
    wrongBound.page.page_size = 41;
    expect(() => validateProjection(wrongBound)).toThrow(ProjectionContractError);

    const wrongCounts = structuredClone(hubProjection);
    wrongCounts.page.before_count = 1;
    wrongCounts.page.after_count = 192;
    expect(() => validateProjection(wrongCounts)).toThrow(ProjectionContractError);

    const unknownConfidence = structuredClone(mediumConfidenceProjection);
    unknownConfidence.relations[0].confidence = "medium-ish";
    expect(() => validateProjection(unknownConfidence)).toThrow(
      ProjectionContractError,
    );
  });

  it("binds a returned projection to the requested fixture identity", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify(ordinaryProjection), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    try {
      await expect(loadProjection("confirmation-bias-hub", 1)).rejects.toThrow(
        ProjectionContractError,
      );
    } finally {
      vi.unstubAllGlobals();
    }
  });
});
