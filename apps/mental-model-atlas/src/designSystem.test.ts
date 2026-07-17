import { describe, expect, it } from "vitest";

// The application intentionally excludes Node types. Vitest still runs in Node,
// so these tests read the exact checked-in CSS contract.
// @ts-expect-error -- test-only Node built-ins
import { existsSync, readFileSync } from "node:fs";

declare const process: { cwd: () => string };

const root = process.cwd();
const mainSource = readFileSync(`${root}/src/main.tsx`, "utf8");
const contractPath = `${root}/src/design-system/index.css`;

const activeFiles = [
  "tokens.css",
  "base.css",
  "shell.css",
  "atlas.css",
  "library.css",
  "model.css",
  "relation.css",
  "states.css",
  "responsive.css",
];

function activeCss(): string {
  return activeFiles
    .map((filename) => readFileSync(`${root}/src/design-system/${filename}`, "utf8"))
    .join("\n");
}

function colorToken(source: string, name: string): string {
  const match = source.match(new RegExp(`${name}:\\s*(#[0-9a-f]{6})`, "i"));
  if (!match) throw new Error(`Missing color token ${name}`);
  return match[1];
}

function relativeLuminance(hex: string): number {
  const channels = [1, 3, 5].map((offset) =>
    Number.parseInt(hex.slice(offset, offset + 2), 16) / 255,
  );
  const linear = channels.map((channel) =>
    channel <= 0.04045
      ? channel / 12.92
      : ((channel + 0.055) / 1.055) ** 2.4,
  );
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(first: string, second: string): number {
  const bright = Math.max(relativeLuminance(first), relativeLuminance(second));
  const dark = Math.min(relativeLuminance(first), relativeLuminance(second));
  return (bright + 0.05) / (dark + 0.05);
}

describe("Mental Model Atlas design-system contract", () => {
  it("has one active modular stylesheet entrypoint", () => {
    expect(existsSync(contractPath)).toBe(true);
    expect(mainSource).toContain('import "./design-system/index.css"');
    expect(mainSource).not.toContain('import "./styles.css"');
    expect(mainSource).not.toContain('import "./restraint.css"');
    expect(existsSync(`${root}/src/styles.css`)).toBe(false);
    expect(existsSync(`${root}/src/restraint.css`)).toBe(false);
  });

  it("imports the complete ordered design-system layer", () => {
    const entrypoint = readFileSync(contractPath, "utf8");
    for (const filename of activeFiles) {
      expect(entrypoint).toContain(`@import "./${filename}"`);
    }
  });

  it("declares the geometry, line, type, space, motion, and layout contracts", () => {
    const tokens = readFileSync(`${root}/src/design-system/tokens.css`, "utf8");
    for (const token of [
      "--radius-structure: 0",
      "--radius-control: 0.125rem",
      "--radius-round: 999px",
      "--line-structure: 1px",
      "--line-current: 2px",
      "--line-selected: 3px",
      '--font-display: "Familjen Grotesk Variable"',
      '--font-body: "IBM Plex Sans Variable"',
      '--font-mono: "IBM Plex Mono"',
      "--space-1: 0.25rem",
      "--space-16: 4rem",
      "--duration-fast: 120ms",
      "--duration-structural: 320ms",
      "--shell-reading: 78rem",
      "--shell-wide: 92rem",
    ]) {
      expect(tokens).toContain(token);
    }
  });

  it("does not reactivate superseded type, radius, or color systems", () => {
    const css = activeCss();
    expect(css).not.toMatch(/\bInter\b/);
    expect(css).not.toMatch(/Georgia|Times New Roman/);
    expect(css).not.toMatch(/#060761|#41ffa7|#c4ff4d|#ba8cff/i);
    expect(css).not.toMatch(/border-radius:\s*(?:0\.7|0\.75|0\.8|0\.9|1|1\.25|1\.5|1\.75|1\.8)rem/);
  });

  it("uses only the three canonical viewport breakpoints", () => {
    const breakpoints = [
      ...activeCss().matchAll(/@media\s*\(max-width:\s*([0-9]+)px\)/g),
    ].map((match) => Number(match[1]));
    expect([...new Set(breakpoints)].sort((left, right) => left - right)).toEqual([
      700, 900, 1080,
    ]);
  });

  it("keeps primary and supporting text above WCAG AA contrast", () => {
    const tokens = readFileSync(`${root}/src/design-system/tokens.css`, "utf8");
    const canvas = colorToken(tokens, "--color-canvas");
    const raised = colorToken(tokens, "--color-surface-raised");
    const ink = colorToken(tokens, "--color-ink");
    const muted = colorToken(tokens, "--color-ink-muted");

    expect(contrastRatio(ink, canvas)).toBeGreaterThanOrEqual(7);
    expect(contrastRatio(ink, raised)).toBeGreaterThanOrEqual(7);
    expect(contrastRatio(muted, canvas)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(muted, raised)).toBeGreaterThanOrEqual(4.5);
  });

  it("locks the critical route and responsive visual signatures", () => {
    const shell = readFileSync(`${root}/src/design-system/shell.css`, "utf8");
    const atlas = readFileSync(`${root}/src/design-system/atlas.css`, "utf8");
    const library = readFileSync(`${root}/src/design-system/library.css`, "utf8");
    const model = readFileSync(`${root}/src/design-system/model.css`, "utf8");
    const relation = readFileSync(`${root}/src/design-system/relation.css`, "utf8");
    const states = readFileSync(`${root}/src/design-system/states.css`, "utf8");
    const responsive = readFileSync(`${root}/src/design-system/responsive.css`, "utf8");

    expect(shell).toContain("background: var(--color-surface-raised)");
    expect(atlas).toContain("background-size: 2rem 2rem");
    expect(atlas).toContain('.graph-edge[data-relation="antagonist"] .edge-line');
    expect(atlas).toContain('.graph-edge[data-relation="tension"] .edge-line');
    expect(atlas).toContain(".edge-flow-marker");
    expect(atlas).toContain(".graph-node-label rect");
    expect(atlas).toContain(".semantic-model-list li > a");
    expect(library).toContain("grid-template-rows: auto 1fr auto");
    expect(library).toContain("height: 100%");
    expect(model).toContain("content-visibility: auto");
    expect(model).toContain("box-shadow: inset var(--line-selected) 0 0 var(--color-ink)");
    expect(relation).toContain("background: var(--color-surface-raised)");
    expect(states).toContain("animation: loading-node var(--duration-structural)");
    expect(responsive).toContain(".graph-stage {\n    display: none;");
    expect(responsive).toContain(".mobile-atlas-entry {\n    display: block;");
  });

  it("defines every public route and state in the shared language", () => {
    const css = activeCss();
    for (const selector of [
      ".atlas-route",
      ".library-route",
      ".model-page-route",
      ".relation-page-route",
      ".learn-route",
      ".failure-page",
      ".route-loading",
      ".data-state",
      ".zero-state",
      ".unavailable-page",
      ".custody-card",
    ]) {
      expect(css).toContain(selector);
    }
  });
});
