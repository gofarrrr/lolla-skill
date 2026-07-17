import type { RelationType } from "./atlasState";

export const RELATION_PRESENTATION: Record<
  RelationType,
  {
    canonicalLabel: string;
    humanLabel: string;
    lineLabel: string;
    explanation: string;
  }
> = {
  ally: {
    canonicalLabel: "Ally",
    humanLabel: "Works with",
    lineLabel: "Solid line",
    explanation:
      "Authored as complementary or mutually supporting in the described respect.",
  },
  antagonist: {
    canonicalLabel: "Antagonist",
    humanLabel: "Pushes against",
    lineLabel: "Dashed line",
    explanation:
      "Authored as opposing or counteracting in the described respect.",
  },
  tension: {
    canonicalLabel: "Tension",
    humanLabel: "Compare the tradeoff",
    lineLabel: "Double line",
    explanation:
      "Authored as a tradeoff, boundary, disagreement, or conflict worth comparing.",
  },
};

export const LEARNING_RELATION_ORDER = [
  "ally",
  "tension",
  "antagonist",
] as const satisfies readonly RelationType[];
