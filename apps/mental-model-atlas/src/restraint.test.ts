import { describe, expect, it } from "vitest";

// The application intentionally excludes Node types. Vitest still runs in Node,
// so this test may read the exact source stylesheet rather than a transformed
// CSS module that exports an empty string.
// @ts-expect-error -- test-only Node built-in
import { readFileSync } from "node:fs";

declare const process: { cwd: () => string };

const restraintCss: string = readFileSync(`${process.cwd()}/src/restraint.css`, "utf8");

function channels(hex: string): [number, number, number] {
  const value = hex.slice(1);
  const expanded = value.length === 3
    ? value.split("").map((character) => character.repeat(2)).join("")
    : value.slice(0, 6);
  return [
    Number.parseInt(expanded.slice(0, 2), 16),
    Number.parseInt(expanded.slice(2, 4), 16),
    Number.parseInt(expanded.slice(4, 6), 16),
  ];
}

describe("monochrome structural study", () => {
  it("contains only achromatic hexadecimal color literals", () => {
    const literals = restraintCss.match(/#[0-9a-f]{3,8}\b/gi) ?? [];

    expect(literals.length).toBeGreaterThan(0);
    expect(
      literals.filter((literal) => {
        const [red, green, blue] = channels(literal);
        return red !== green || green !== blue;
      }),
    ).toEqual([]);
  });

  it("does not assign separate hues to relationship types", () => {
    expect(restraintCss).toContain("--ally: #171717");
    expect(restraintCss).toContain("--antagonist: #171717");
    expect(restraintCss).toContain("--tension: #171717");
    expect(restraintCss).toContain("--relationship-stroke: #171717");
  });

  it("removes the former decorative section accents", () => {
    expect(restraintCss).toMatch(
      /\.derived-layer-heading::before\s*\{\s*display:\s*none;/,
    );
    expect(restraintCss).not.toContain(".source-layer-heading::before");
  });
});
