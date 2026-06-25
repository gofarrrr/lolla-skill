"""Serve a single Lolla pipeline result in the Observatory frontend.

Zero-dependency Python server (stdlib http.server). Takes a pipeline
result JSON file and serves it through the Observatory Svelte app.

Usage:
    python3 observatory/serve_result.py --result /tmp/lolla_result.json
    python3 observatory/serve_result.py --result /tmp/lolla_result.json --port 9000

SPA source: the bundle in ``observatory/build/`` is compiled output from
``Lolla-system-b/observatory/svelte-app`` (separate repo). To change SPA
behaviour, edit the Svelte source there, run ``npm run build``, and copy
``build/`` over the skill's ``observatory/build/``. The ``/audit/*`` and
``/usage`` panels rendered from this Python file are independent of the
SPA bundle and stay portable when ``observatory/build/`` is empty.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "build"
SKILL_DATA_DIR = SCRIPT_DIR.parent / "data"
ENGINE_DIR = SCRIPT_DIR.parent / "engine"
FAMILY_DIR = SKILL_DATA_DIR / "family_semantics"
if (ENGINE_DIR / "system_b" / "__init__.py").exists() and str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

# Loaded at startup, re-read on each request to pick up late writes (e.g. Step 6b)
_RESULT: dict = {}
_RESULT_PATH: Path | None = None
_RESULT_MTIME: float = 0.0
_CASE_ID: str = "lolla-audit"
_CASE_NAME: str = "Lolla Audit"
_KG_CACHE: dict | None = None
_FAMILY_CACHE: list[dict] | None = None
_DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"
_OBSERVATORY_HOST = "127.0.0.1"


# ---------------------------------------------------------------------------
# Module-scope rendering helpers — shared across /usage and /audit/* panels.
# Each helper is small and stable so all server-rendered pages can rely on
# the same primitives without re-importing or wrapping. Lifting them out of
# the original `_render_usage_html` enclosure was the prerequisite for
# adding the audit panel family in PR 3 of the 2026-04-28 visibility roadmap.
# ---------------------------------------------------------------------------


def _esc(value) -> str:
    """HTML-escape any value before interpolation.

    Defends against injection from a crafted result.json: model names,
    rejection reasons, evidence quotes, dimension materiality notes, etc.
    Numeric helpers (``_fmt_int``, ``_fmt_usd``) already produce safe output;
    everything else flows through this.
    """
    return html.escape(str(value), quote=True)


def _short(value, limit: int = 240) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _fmt_int(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


def _fmt_usd(value) -> str:
    try:
        return f"${float(value):.4f}"
    except (TypeError, ValueError):
        return "—"


def _fmt_pct(value, *, fraction: bool = False) -> str:
    """Format a number as a percentage. ``fraction=True`` if input is 0..1."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if fraction:
        n *= 100
    return f"{n:.1f}%"


def _fmt_score(value) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return "—"


# Audit panel routes, ordered for the top nav. The first column is the URL
# fragment (used in href + active-state matching); the second is the label
# the operator sees. Keep the index page (/audit) first so the nav reads
# left-to-right from "everything" to specific panels.
_AUDIT_NAV = (
    ("/audit", "Audit Index"),
    ("/audit/extraction", "Extraction"),
    ("/audit/memo", "Memo"),
    ("/audit/lane1", "Lane 1"),
    ("/audit/lane2", "Lane 2"),
    ("/audit/lane4", "Lane 4"),
    ("/audit/anti-echo", "Anti-echo"),
    ("/audit/routing", "Route Trace"),
    ("/audit/treatment-audit", "Treatment Audit"),
    ("/audit/expansions", "Expansions"),
    ("/audit/stakeholders", "Stakeholders"),
    ("/audit/v60", "V60"),
    ("/audit/pre-step6", "Pre-Step-6"),
    ("/audit/graph-survival", "Survival"),
    ("/audit/reasoning-trace", "Trace"),
    ("/audit/events", "Run Events"),
    ("/usage", "Usage"),
)


_SHARED_PANEL_CSS = """
body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }
h1 { margin: 0 0 0.5rem; }
h2 { margin-top: 2rem; }
h3 { margin-top: 1.5rem; }
.meta { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
.hint { color: #666; font-size: 0.85rem; margin-top: -0.5rem; margin-bottom: 1rem; }
table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; font-size: 0.92rem; }
th, td { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #eee; vertical-align: top; }
th { background: #f6f6f6; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.detected-true { color: #c2410c; font-weight: 600; }
.detected-false { color: #666; }
.empty { color: #777; font-style: italic; padding: 0.75rem 1rem; background: #fafafa; border-left: 3px solid #ccc; }
.tagrow { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag { display: inline-block; padding: 0.05rem 0.5rem; border-radius: 3px; background: #eef; font-size: 0.85rem; color: #336; border: 1px solid #ccd; }
.tag.warn { background: #fdecec; color: #832; border-color: #e5b8b8; }
.tag.ok { background: #eafde9; color: #246; border-color: #b8e5b8; }
blockquote.quote { margin: 0; padding: 0.35rem 0.6rem; background: #fafafa; border-left: 3px solid #ddd; color: #333; }
.memo-doc { max-width: 860px; line-height: 1.58; margin-bottom: 2rem; }
.memo-doc h2 { margin-top: 1.6rem; padding-top: 0.4rem; border-top: 1px solid #eee; }
.memo-doc h2:first-child { border-top: 0; padding-top: 0; }
.memo-doc h3 { margin-top: 1.2rem; }
.memo-doc p { margin: 0.75rem 0; }
.memo-doc ul { margin: 0.75rem 0 1rem 1.4rem; padding: 0; }
.memo-doc li { margin: 0.25rem 0; }
nav.audit-nav { font-size: 0.9rem; padding: 0.5rem 0 1rem; border-bottom: 1px solid #eee; margin-bottom: 1.5rem; }
nav.audit-nav a { color: #336; text-decoration: none; padding: 0.25rem 0.5rem; }
nav.audit-nav a.active { font-weight: 600; color: #222; background: #eef; border-radius: 3px; }
nav.audit-nav a:hover { text-decoration: underline; }
code { background: #f0f0f0; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.9em; }
details { margin: 0.5rem 0; }
details summary { cursor: pointer; color: #336; padding: 0.25rem 0; }
details[open] summary { margin-bottom: 0.5rem; }

/* Headline summary — one sentence after the run-header, before sections */
p.lede { font-size: 1rem; color: #222; margin: 0.5rem 0 1.5rem; line-height: 1.5; }
p.lede strong { color: #111; }

/* Run-header strip — case identity + back-link, on every /audit/* page */
.run-header { color: #666; font-size: 0.9rem; margin: 0 0 1rem; }
.run-header strong { color: #222; }
.run-header a { color: #336; text-decoration: none; }
.run-header a:hover { text-decoration: underline; }

/* Run-vitals strip on /audit index — at-a-glance pulse of this run */
.vitals { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.75rem 0 1.5rem; }
.vitals .tag { background: #f6f6f6; color: #222; border-color: #ddd; font-size: 0.9rem; padding: 0.2rem 0.6rem; }

"""


# Telemetry FAB — injected into the SPA's index.html on /, the *only* bridge
# from the case/factual product surface to the system-reasoning surface at
# /audit. Lives in its own constant (not in _SHARED_PANEL_CSS) because the
# FAB only renders on /; the audit panels and /usage never carry it.
_TELEMETRY_FAB_HTML = (
    '<a href="/audit" class="telemetry-fab" '
    'aria-label="View run telemetry">TELEMETRY <span aria-hidden="true">&rarr;</span></a>'
)

_TELEMETRY_FAB_STYLE = """
<style>
/* Telemetry FAB lives at bottom-right so it never sits in the lane of
   the SPA's right-side .sidebar (which fills the top-right vertical band)
   or its on-demand .drawer-panel close button. z-index 50 keeps it above
   ordinary page content but below any SPA modal/overlay (which sit at
   100/101). The original bug shipped at top-right z=9999 — that visually
   cropped the sidebar's first card and intercepted clicks on the drawer's
   close X. Bottom-right is empty real estate in the SPA bundle. */
/* Match the SPA's design tokens (deep indigo bg, teal accent, mono uppercase
   labels) so the FAB reads as part of the system, not a tacked-on add-on. */
.telemetry-fab {
  position: fixed; bottom: 20px; right: 20px; z-index: 50;
  padding: 0.55rem 1.1rem; border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #41FFA7;
  border: 1px solid rgba(255, 255, 255, 0.22);
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 12px; font-weight: 500; letter-spacing: 0.1em;
  text-transform: uppercase; text-decoration: none;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  transition: background 120ms ease, border-color 120ms ease;
}
.telemetry-fab:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.4);
  color: #41FFA7; text-decoration: none;
}
.telemetry-fab:focus-visible { outline: 2px solid #41FFA7; outline-offset: 2px; }
@media (max-width: 600px) {
  .telemetry-fab { bottom: 14px; right: 14px; padding: 0.45rem 0.85rem; font-size: 11px; }
}
/* Belt-and-suspenders: when the SPA opens its modal drawer, hide the FAB
   entirely so it cannot intercept clicks on the drawer's close button even
   under unusual stacking contexts. */
body:has(.drawer-overlay) .telemetry-fab,
body:has(.drawer-panel) .telemetry-fab {
  display: none;
}
</style>
"""


_MAIN_SURFACE_COPY_PATCH_SCRIPT = """
<script id="lolla-main-surface-copy-patch">
(() => {
  if (window.__lollaMainSurfaceCopyPatch) return;
  window.__lollaMainSurfaceCopyPatch = true;

  let healthOverall = null;

  const patchTextNodes = (root, replacer) => {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      const next = replacer(node.nodeValue || "");
      if (next !== node.nodeValue) node.nodeValue = next;
    }
  };

  const patchPressureCheck = () => {
    for (const section of document.querySelectorAll('[aria-label="Audit Conclusion"]')) {
      section.setAttribute("aria-label", "Optional Pressure Check");
      const title = section.querySelector(".conclusion-title");
      if (title && title.textContent.trim() === "Audit Conclusion") {
        title.textContent = "Optional Pressure Check";
      }
      const stat = section.querySelector(".conclusion-stat");
      if (!stat) continue;
      const text = stat.textContent.trim();
      if (text === "0 lanes reviewed, no divergences") {
        stat.textContent = "Optional pressure check not run; no Step-7 divergences";
      } else {
        stat.textContent = text.replace(
          /^(\\d+) lanes? reviewed,\\s*no divergences$/,
          (_match, count) => `${count} optional lane${count === "1" ? "" : "s"} checked, no Step-7 divergences`
        );
      }
    }
  };

  const patchRunInspector = () => {
    for (const button of document.querySelectorAll(".inspector-toggle")) {
      patchTextNodes(button, (text) => text
        .replace(/(\\d+) calls /g, "$1 boundary calls ")
        .replace(/ tokens/g, " boundary tokens")
      );
    }
  };

  const patchHeaderHealth = () => {
    if (healthOverall !== "partial") return;
    for (const span of document.querySelectorAll(".status-bar span")) {
      if (span.textContent.trim() === "COMPLETE") span.textContent = "PARTIAL";
    }
    for (const dot of document.querySelectorAll(".status-dot")) {
      dot.classList.add("status-dot--degraded");
    }
  };

  const patch = () => {
    patchPressureCheck();
    patchRunInspector();
    patchHeaderHealth();
  };

  const loadSingleRunHealth = async () => {
    try {
      const casesResponse = await fetch("/api/cases");
      if (!casesResponse.ok) return;
      const cases = await casesResponse.json();
      const firstCase = Array.isArray(cases) ? cases[0] : null;
      if (!firstCase || !firstCase.id) return;
      const caseResponse = await fetch(`/api/case/${encodeURIComponent(firstCase.id)}`);
      if (!caseResponse.ok) return;
      const payload = await caseResponse.json();
      healthOverall = payload && payload.run_health && payload.run_health.overall;
      patch();
    } catch (_error) {
      // Best-effort product-copy patch only. The Observatory still works if
      // the health request races the SPA or fails on an older fixture.
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", patch, { once: true });
  } else {
    patch();
  }
  new MutationObserver(patch).observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true,
  });
  loadSingleRunHealth();
})();
</script>
"""


_SELECTED_RUN_CUSTODY_PANEL_STYLE = """
<style id="lolla-selected-run-custody-panel-style">
.lolla-custody-panel {
  margin-top: 0.85rem;
  padding: 0.9rem 0.95rem;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.lolla-custody-panel--floating {
  position: fixed;
  top: 6.25rem;
  right: 1.25rem;
  z-index: 45;
  width: min(23rem, calc(100vw - 2rem));
  max-height: calc(100vh - 8rem);
  overflow: auto;
  background: rgba(6, 7, 97, 0.96);
  box-shadow: 0 18px 46px rgba(0, 0, 0, 0.34);
}
.lolla-custody-panel h3 {
  margin: 0 0 0.6rem;
  color: #fff;
  font-size: 0.78rem;
  font-weight: 650;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.lolla-custody-panel ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
}
.lolla-custody-panel li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.5rem;
  align-items: start;
  min-width: 0;
  padding: 0.45rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.lolla-custody-panel li:first-child { border-top: 0; padding-top: 0; }
.lolla-custody-name {
  display: block;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.8rem;
  font-weight: 600;
  overflow-wrap: anywhere;
}
.lolla-custody-meta {
  display: block;
  margin-top: 0.12rem;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.72rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}
.lolla-custody-status {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  padding: 0.12rem 0.44rem;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.64rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}
.lolla-custody-status.available {
  color: #41FFA7;
  border-color: rgba(65, 255, 167, 0.45);
  background: rgba(65, 255, 167, 0.08);
}
.lolla-custody-status.unavailable {
  color: rgba(255, 255, 255, 0.52);
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.03);
}
.lolla-custody-link {
  color: #41FFA7;
  text-decoration: none;
}
.lolla-custody-link:hover { text-decoration: underline; }
@media (max-width: 900px) {
  .lolla-custody-panel--floating {
    top: auto;
    right: 0.75rem;
    bottom: 5.5rem;
    left: 0.75rem;
    width: auto;
    max-height: 46vh;
  }
}
</style>
"""


_SELECTED_RUN_CUSTODY_PANEL_SCRIPT = """
<script id="lolla-selected-run-custody-panel">
(() => {
  if (window.__lollaSelectedRunCustodyPanel) return;
  window.__lollaSelectedRunCustodyPanel = true;

  const ARTIFACTS = [
    {
      key: "agent-result",
      label: "agent_result.json",
      describe: (payload) => [
        payload && payload.schema_version,
        payload && payload.status ? `status ${payload.status}` : "",
        payload && payload.caller_action ? `caller ${payload.caller_action}` : "",
        payload && payload.risk_mode ? `mode ${payload.risk_mode}` : "",
      ].filter(Boolean).join(" · "),
    },
    {
      key: "reasoning-trace",
      label: "reasoning_trace.json",
      describe: (payload) => {
        const artifacts = Array.isArray(payload && payload.artifacts) ? payload.artifacts.length : null;
        return artifacts === null ? payload && payload.schema_version : `${artifacts} artifacts`;
      },
    },
    {
      key: "events",
      label: "run_events.json",
      describe: (payload) => {
        const count = Array.isArray(payload) ? payload.length : 0;
        return `${count} event${count === 1 ? "" : "s"}`;
      },
    },
    {
      key: "memo",
      label: "memo.md",
      describe: (payload) => {
        const chars = payload && typeof payload.markdown === "string" ? payload.markdown.length : 0;
        return chars ? `${chars.toLocaleString()} chars` : "markdown wrapper";
      },
    },
    {
      key: "graph-survival",
      label: "graph_survival_report.*",
      describe: (payload) => {
        const hasMarkdown = !!(payload && payload.markdown && payload.markdown.markdown);
        return hasMarkdown ? "json + markdown" : "json report";
      },
    },
  ];

  let selectedCaseId = null;
  let requestToken = 0;
  let states = {};

  const encodeCaseId = (caseId) => encodeURIComponent(caseId);

  const caseIdFromRequest = (input) => {
    try {
      const raw = typeof input === "string" ? input : input && input.url;
      if (!raw) return null;
      const url = new URL(raw, window.location.origin);
      const prefix = "/api/case/";
      if (!url.pathname.startsWith(prefix)) return null;
      const rest = url.pathname.slice(prefix.length);
      if (!rest || rest.includes("/")) return null;
      return decodeURIComponent(rest);
    } catch (_error) {
      return null;
    }
  };

  const endpointFor = (caseId, key) => `/api/case/${encodeCaseId(caseId)}/${key}`;

  const escapeHtml = (value) => String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

  const rowHtml = (artifact) => {
    const state = states[artifact.key] || { status: "loading", detail: "checking..." };
    const href = selectedCaseId ? endpointFor(selectedCaseId, artifact.key) : "#";
    const available = state.status === "available";
    const statusClass = available ? "available" : "unavailable";
    const statusText = available ? "available" : state.status === "loading" ? "checking" : "unavailable";
    const label = available
      ? `<a class="lolla-custody-link" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(artifact.label)}</a>`
      : escapeHtml(artifact.label);
    return `
      <li data-custody-artifact="${escapeHtml(artifact.key)}">
        <span>
          <span class="lolla-custody-name">${label}</span>
          <span class="lolla-custody-meta">${escapeHtml(state.detail || "")}</span>
        </span>
        <span class="lolla-custody-status ${statusClass}">${escapeHtml(statusText)}</span>
      </li>
    `;
  };

  const render = () => {
    if (!selectedCaseId) return;
    const sidebar = document.querySelector(".sidebar");
    const target = sidebar || document.body;
    let panel = document.querySelector(".lolla-custody-panel");
    if (!panel) {
      panel = document.createElement("section");
      panel.className = "lolla-custody-panel";
      panel.setAttribute("aria-label", "Selected run custody");
    }
    if (panel.parentElement !== target) {
      target.appendChild(panel);
    }
    panel.classList.toggle("lolla-custody-panel--floating", !sidebar);
    const html = `
      <h3>Run Custody</h3>
      <ul>${ARTIFACTS.map(rowHtml).join("")}</ul>
    `;
    if (panel.__lollaCustodyHtml !== html) {
      panel.__lollaCustodyHtml = html;
      panel.innerHTML = html;
    }
  };

  const loadArtifacts = async (caseId) => {
    const token = ++requestToken;
    selectedCaseId = caseId;
    states = Object.fromEntries(
      ARTIFACTS.map((artifact) => [artifact.key, { status: "loading", detail: "checking..." }])
    );
    render();

    await Promise.all(ARTIFACTS.map(async (artifact) => {
      try {
        const response = await window.__lollaNativeFetch(endpointFor(caseId, artifact.key));
        if (token !== requestToken) return;
        if (!response.ok) {
          states[artifact.key] = { status: "unavailable", detail: response.status === 404 ? "not archived" : `HTTP ${response.status}` };
          render();
          return;
        }
        const payload = await response.json();
        if (token !== requestToken) return;
        states[artifact.key] = { status: "available", detail: artifact.describe(payload) || "ready" };
        render();
      } catch (_error) {
        if (token !== requestToken) return;
        states[artifact.key] = { status: "unavailable", detail: "request failed" };
        render();
      }
    }));
  };

  window.__lollaNativeFetch = window.__lollaNativeFetch || window.fetch.bind(window);
  const nativeFetch = window.__lollaNativeFetch;
  window.fetch = async (...args) => {
    const candidateCaseId = caseIdFromRequest(args[0]);
    if (candidateCaseId) {
      loadArtifacts(candidateCaseId);
    }
    const response = await nativeFetch(...args);
    if (candidateCaseId) {
      response.clone().json().then((payload) => {
        const caseId = payload && payload.case && payload.case.case_id;
        if (caseId && caseId !== candidateCaseId) loadArtifacts(caseId);
      }).catch(() => {});
    }
    return response;
  };

  new MutationObserver(render).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
</script>
"""


def _inject_telemetry_fab(html_bytes: bytes) -> bytes:
    """Insert the Telemetry FAB and root-page copy patch into index.html.

    String-injection at the byte-stream layer — does NOT modify the bundle on
    disk and works whether the SPA was built recently or long ago. Idempotent
    via the ``telemetry-fab`` marker so accidental double-serves don't render
    two buttons. Falls back to appending if the bundle has no ``</body>`` tag.
    """
    try:
        text = html_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return html_bytes
    if "telemetry-fab" in text:
        return html_bytes
    inject = (
        _TELEMETRY_FAB_STYLE
        + _SELECTED_RUN_CUSTODY_PANEL_STYLE
        + _TELEMETRY_FAB_HTML
        + _MAIN_SURFACE_COPY_PATCH_SCRIPT
        + _SELECTED_RUN_CUSTODY_PANEL_SCRIPT
    )
    if "</body>" in text:
        text = text.replace("</body>", inject + "</body>", 1)
    else:
        text = text + inject
    return text.encode("utf-8")


def _render_scaffold(*, title: str, body: str, current_path: str = "") -> str:
    """Wrap a page body in the shared HTML scaffold (header, nav, footer).

    All audit panels and the existing /usage page use the same look so
    operators can move between them without re-orienting. ``current_path``
    is matched exactly against ``_AUDIT_NAV`` URLs to highlight the active
    tab.
    """
    nav_links = "".join(
        f'<a href="{_esc(href)}"'
        f'{" class=\"active\"" if current_path == href else ""}'
        f">{_esc(label)}</a>"
        for href, label in _AUDIT_NAV
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>{_SHARED_PANEL_CSS}</style></head><body>
<nav class="audit-nav">
  <a href="/">Observatory</a> ·
  {nav_links}
</nav>
{body}
</body></html>
"""


def _captured_at_str() -> str:
    """Derive a human run-capture timestamp from the result file path.

    Archived runs live at ``runs/<case-slug>/<UTC-stamp>/result.json`` where
    ``<UTC-stamp>`` is e.g. ``20260425T121607Z``. We surface that as the
    "Captured" field in the run-header. Returns ``""`` when no path is
    known (e.g. fixture-driven tests, ad-hoc result loads).
    """
    if _RESULT_PATH is None:
        return ""
    parent = _RESULT_PATH.parent.name
    if len(parent) == 16 and parent.endswith("Z") and parent[8:9] == "T":
        return f"{parent[0:4]}-{parent[4:6]}-{parent[6:8]} {parent[9:11]}:{parent[11:13]}:{parent[13:15]}Z"
    return parent


def _render_run_header() -> str:
    """Compact run identity strip rendered above the lede on every /audit/* panel.

    Defensive about field availability — older archived runs don't carry
    ``run_id`` or top-level ``fingerprint``. We always show the case name
    and the back-link to the SPA; the rest is best-effort.
    """
    bits: list[str] = []

    case_name = _CASE_NAME or "—"
    bits.append(f"Case: <strong>{_esc(case_name)}</strong>")

    captured = _captured_at_str()
    if captured:
        bits.append(f"Captured: <code>{_esc(captured)}</code>")

    rh = _RESULT.get("run_health") or {}
    overall = rh.get("overall")
    if overall:
        bits.append(f"Health: <code>{_esc(overall)}</code>")

    risk_mode = _risk_mode_for_result(_RESULT, _RESULT_PATH)
    if risk_mode:
        bits.append(f"Risk mode: <code>{_esc(risk_mode)}</code>")

    us = _RESULT.get("usage_summary") or {}
    run_id = us.get("run_id")
    if run_id:
        run_id_str = str(run_id)
        bits.append(
            f'Run: <code title="{_esc(run_id_str)}">{_esc(run_id_str[:24])}</code>'
        )

    bits.append('<a href="/">← back to result</a>')

    return f'<div class="run-header">{" · ".join(bits)}</div>'


def _empty_inline(message: str) -> str:
    """Inline empty-state block — keeps page chrome (nav + run-header + h1)."""
    return f'<div class="empty">{message}</div>'


def _reload_result_if_changed():
    """Re-read the result JSON from disk if the file has been modified."""
    global _RESULT, _RESULT_MTIME
    if _RESULT_PATH is None:
        return
    try:
        mtime = _RESULT_PATH.stat().st_mtime
    except OSError:
        return
    if mtime > _RESULT_MTIME:
        with open(_RESULT_PATH) as f:
            _RESULT = json.load(f)
        _RESULT_MTIME = mtime


def _sidecar_candidates(filename: str) -> list[Path]:
    """Return likely sidecar paths for archive and /tmp result layouts."""
    if _RESULT_PATH is None:
        return []

    candidates = [_RESULT_PATH.parent / filename]
    stem = _RESULT_PATH.stem
    if stem.endswith("_result"):
        prefix = stem[: -len("_result")]
        candidates.append(_RESULT_PATH.parent / f"{prefix}_{filename}")

    if filename != "run_events.json":
        for events_path in _sidecar_candidates("run_events.json"):
            if not events_path.exists():
                continue
            try:
                with open(events_path) as f:
                    run_events = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(run_events, dict):
                continue
            for event in run_events.get("events") or []:
                if not isinstance(event, dict):
                    continue
                details = event.get("details") or {}
                if not isinstance(details, dict):
                    continue
                archive_path = details.get("archive_path")
                if archive_path:
                    candidates.append(Path(archive_path) / filename)

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        if path not in seen:
            unique.append(path)
            seen.add(path)
    return unique


def _load_json_sidecar(filename: str) -> tuple[dict | list | None, Path | None, str]:
    """Load a JSON sidecar next to the served result, returning payload/path/error."""
    last_error = ""
    for path in _sidecar_candidates(filename):
        if not path.exists():
            continue
        try:
            with open(path) as f:
                return json.load(f), path, ""
        except (OSError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            return None, path, last_error
    return None, None, last_error


def _load_text_sidecar(filename: str) -> tuple[str | None, Path | None, str]:
    """Load a UTF-8 text sidecar next to the served result or archive path."""
    last_error = ""
    for path in _sidecar_candidates(filename):
        if not path.exists():
            continue
        try:
            return path.read_text(encoding="utf-8"), path, ""
        except (OSError, UnicodeDecodeError) as exc:
            last_error = str(exc)
            return None, path, last_error
    return None, None, last_error


def _render_simple_markdown(text: str) -> str:
    """Render the memo's small Markdown subset without adding dependencies."""
    blocks: list[str] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(
                "<p>" + "<br>".join(_esc(line) for line in paragraph) + "</p>"
            )
            paragraph = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            blocks.append(
                "<ul>"
                + "".join(f"<li>{_esc(item)}</li>" for item in bullets)
                + "</ul>"
            )
            bullets = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            flush_bullets()
            blocks.append(f"<h3>{_esc(stripped[4:].strip())}</h3>")
        elif stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            blocks.append(f"<h2>{_esc(stripped[3:].strip())}</h2>")
        elif stripped.startswith("# "):
            flush_paragraph()
            flush_bullets()
            blocks.append(f"<h2>{_esc(stripped[2:].strip())}</h2>")
        elif stripped.startswith("- "):
            flush_paragraph()
            bullets.append(stripped[2:].strip())
        else:
            flush_bullets()
            paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    return "\n".join(blocks) if blocks else "<p class='empty'>Memo is empty.</p>"


def _joined_user_turns(extraction: dict) -> str:
    """Concatenate user-turn text from the serialized conversation."""
    return "\n\n".join(
        t.get("text", "")
        for t in extraction.get("turns", [])
        if t.get("speaker") == "user"
    )


def _joined_assistant_turns(extraction: dict) -> str:
    """Concatenate assistant-turn text from the serialized conversation."""
    return "\n\n".join(
        t.get("text", "")
        for t in extraction.get("turns", [])
        if t.get("speaker") == "assistant"
    )


def _derive_case_name(result: dict) -> str:
    """Derive a human-readable case name from the pipeline result.

    Prefers the extraction's decision_situation (a clean one-liner produced by
    the extraction step). Falls back to the first user turn's leading clause.
    """
    extraction = result.get("extraction", {})
    decision_situation = extraction.get("decision_situation", "").strip()
    if decision_situation:
        # decision_situation is already concise; just clip if abnormally long
        if len(decision_situation) > 140:
            return decision_situation[:140].rsplit(" ", 1)[0]
        return decision_situation

    first_user_turn = _joined_user_turns(extraction).split("\n\n", 1)[0].strip()
    if not first_user_turn:
        return "Lolla Audit"
    # Take first line
    first_line = first_user_turn.split("\n")[0].strip()
    # Try to find a natural sentence or clause break within 100 chars
    for sep in [". ", "; "]:
        idx = first_line.find(sep)
        if 20 < idx < 100:
            return first_line[:idx]
    # Try subordinate clause breaks for long sentences
    for sep in [", amid ", ", with stakes", ", with ", " in a "]:
        idx = first_line.find(sep)
        if 30 < idx < 140:
            return first_line[:idx]
    # Fallback: truncate at 90 chars on word boundary
    if len(first_line) > 90:
        truncated = first_line[:90].rsplit(" ", 1)[0]
        return truncated
    return first_line


def _load_kg() -> dict:
    global _KG_CACHE
    if _KG_CACHE is None:
        kg_path = SKILL_DATA_DIR / "knowledge_graph.json"
        if kg_path.exists():
            with open(kg_path) as f:
                _KG_CACHE = json.load(f)
        else:
            _KG_CACHE = {}
    return _KG_CACHE


def _get_kg_stats() -> dict:
    kg = _load_kg()
    models = kg.get("models", {})
    edges = kg.get("edges", [])
    tendencies = kg.get("tendencies", {})
    total_fm = sum(len(m.get("failure_modes", [])) for m in models.values())
    total_pm = sum(len(m.get("premortem_questions", [])) for m in models.values())
    total_h = sum(len(m.get("heuristics", [])) for m in models.values())
    return {
        "model_count": len(models),
        "tendency_count": len(tendencies),
        "edge_count": len(edges),
        "failure_mode_count": total_fm,
        "premortem_count": total_pm,
        "heuristic_count": total_h,
    }


def _get_model_detail(model_id: str) -> dict | None:
    kg = _load_kg()
    models = kg.get("models", {})
    model = models.get(model_id)
    if not model:
        return None

    edges = kg.get("edges", [])
    allies, antagonists, tensions = [], [], []
    seen: set[tuple[str, str]] = set()
    for e in edges:
        etype = e.get("type")
        if etype not in ("ally", "antagonist", "tension"):
            continue
        if e.get("source") == model_id:
            neighbor_id = e.get("target")
        elif e.get("target") == model_id:
            neighbor_id = e.get("source")
        else:
            continue
        dedup_key = (etype, neighbor_id)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        bucket = allies if etype == "ally" else antagonists if etype == "antagonist" else tensions
        neighbor_model = models.get(neighbor_id, {})
        bucket.append({
            "model_id": neighbor_id,
            "display_name": neighbor_model.get("display_name", neighbor_id),
            "affinity": 0.0,
        })

    def _normalize(items: list) -> list[dict]:
        out = []
        for item in items:
            if isinstance(item, str):
                out.append({"description": item})
            elif isinstance(item, dict):
                if "description" not in item:
                    item["description"] = item.get("question") or item.get("text") or str(item)
                out.append(item)
            else:
                out.append({"description": str(item)})
        return out

    raw_fm = model.get("failure_modes", [])
    raw_pm = model.get("premortem_questions", [])
    raw_h = model.get("heuristics", [])
    return {
        "model_id": model_id,
        "display_name": model.get("display_name", model_id),
        "select_when": model.get("select_when"),
        "danger_when": model.get("danger_when"),
        "failure_mode_count": len(raw_fm),
        "failure_modes_sample": raw_fm[:2],
        "premortem_count": len(raw_pm),
        "premortem_sample": _normalize(raw_pm[:2]),
        "heuristic_count": len(raw_h),
        "heuristics_sample": _normalize(raw_h[:2]),
        "reasoning_types": model.get("reasoning_types", []),
        "allies": sorted(allies, key=lambda x: x["display_name"]),
        "antagonists": sorted(antagonists, key=lambda x: x["display_name"]),
        "tensions": sorted(tensions, key=lambda x: x["display_name"]),
    }


def _load_json_safe(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _archive_root() -> Path:
    """Return the local archive root used by archive_run.py."""
    override = os.environ.get("LOLLA_ARCHIVE_DIR")
    if override:
        return Path(override).expanduser()
    return _DEFAULT_ARCHIVE_ROOT


def _run_id_for_result(result: dict, result_path: Path | None = None) -> str:
    usage = result.get("usage_summary") or {}
    if isinstance(usage, dict) and usage.get("run_id"):
        return str(usage.get("run_id"))
    if result_path is not None:
        return result_path.parent.name
    return ""


def _detected_finding_count(result: dict) -> int:
    detected = result.get("detected_tendencies")
    if isinstance(detected, list):
        return len(detected)
    audit = result.get("audit_summary") or {}
    deep_checks = audit.get("deep_check_results") or []
    if isinstance(deep_checks, list):
        return sum(
            1
            for item in deep_checks
            if isinstance(item, dict) and item.get("detected")
        )
    return 0


def _case_summary(
    result: dict,
    *,
    case_id: str,
    name: str,
    source: str,
    result_path: Path | None = None,
) -> dict:
    finding_count = _detected_finding_count(result)
    run_id = _run_id_for_result(result, result_path)
    summary = {
        "id": case_id,
        "name": name,
        "source": source,
        "run_id": run_id,
        "has_delta_card": bool(result.get("delta_card")) or finding_count > 0,
        "has_companion": bool(result.get("companion_cheat_sheet")),
        "has_audit_trace": bool(result.get("audit_summary")),
        "finding_count": finding_count,
    }
    if result_path is not None:
        summary["result_path"] = str(result_path)
    return summary


def _archive_case_id(case_dir: Path, run_dir: Path) -> str:
    return f"archive:{case_dir.name}:{run_dir.name}"


def _archive_result_path_for_case_id(case_id: str) -> Path | None:
    if not case_id.startswith("archive:"):
        return None
    parts = case_id.split(":", 2)
    if len(parts) != 3 or not parts[1] or not parts[2]:
        return None
    root = _archive_root().resolve()
    result_path = (root / parts[1] / parts[2] / "result.json").resolve()
    if root != result_path and root not in result_path.parents:
        return None
    return result_path


def _load_case_result(case_id: str) -> tuple[dict | None, Path | None, bool]:
    """Load the active result or an archived result addressed by API case id."""
    if case_id == _CASE_ID:
        _reload_result_if_changed()
        return _RESULT, _RESULT_PATH, True

    result_path = _archive_result_path_for_case_id(case_id)
    if result_path is None:
        return None, None, False
    result = _load_json_safe(result_path)
    if result is None:
        return None, result_path, False
    return result, result_path, False


def _risk_mode_for_result(result: dict, result_path: Path | None = None) -> str | None:
    """Return risk_mode from result.json, falling back to agent_result.json."""
    risk_mode = result.get("risk_mode")
    if risk_mode:
        return str(risk_mode)
    if result_path is None:
        return None
    agent_result = _load_json_safe(result_path.parent / "agent_result.json")
    if not isinstance(agent_result, dict):
        return None
    risk_mode = agent_result.get("risk_mode")
    return str(risk_mode) if risk_mode else None


def _fixed_sidecar_path(result_path: Path | None, filename: str) -> Path | None:
    """Resolve a fixed sidecar filename inside the selected run directory."""
    if result_path is None:
        return None
    run_dir = result_path.parent.resolve()
    sidecar_path = (run_dir / filename).resolve()
    if run_dir != sidecar_path and run_dir not in sidecar_path.parents:
        return None
    if not sidecar_path.is_file():
        return None
    return sidecar_path


def _append_unique_path(paths: list[Path], seen: set[Path], path: Path) -> None:
    try:
        resolved = path.resolve()
    except OSError:
        return
    if resolved in seen:
        return
    paths.append(resolved)
    seen.add(resolved)


def _sidecar_path_inside_archive(path: Path) -> Path | None:
    """Return path only when it resolves inside the configured archive root."""
    try:
        root = _archive_root().resolve()
        resolved = path.resolve()
    except OSError:
        return None
    if root != resolved and root not in resolved.parents:
        return None
    return resolved


def _events_from_run_events_payload(payload) -> list[dict]:
    if isinstance(payload, dict):
        events = payload.get("events") or []
    elif isinstance(payload, list):
        events = payload
    else:
        events = []
    return [event for event in events if isinstance(event, dict)]


def _active_run_event_paths(result_path: Path) -> list[Path]:
    """Return active-run event sidecars, preferring /tmp prefixed layout."""
    paths: list[Path] = []
    seen: set[Path] = set()
    stem = result_path.stem
    if stem.endswith("_result"):
        prefix = stem[: -len("_result")]
        _append_unique_path(paths, seen, result_path.parent / f"{prefix}_run_events.json")
    _append_unique_path(paths, seen, result_path.parent / "run_events.json")
    return paths


def _case_sidecar_candidates(
    result_path: Path | None,
    filename: str,
    *,
    is_current: bool,
) -> list[Path]:
    """Return fixed sidecar candidates for current or selected archived cases."""
    if result_path is None:
        return []

    if not is_current:
        path = _fixed_sidecar_path(result_path, filename)
        return [path] if path is not None else []

    paths: list[Path] = []
    seen: set[Path] = set()
    stem = result_path.stem

    # Active runs served from /tmp use /tmp/lolla_<run_id>_result.json plus
    # /tmp/lolla_<run_id>_<sidecar>. Prefer that over stale plain filenames.
    if stem.endswith("_result"):
        prefix = stem[: -len("_result")]
        _append_unique_path(paths, seen, result_path.parent / f"{prefix}_{filename}")

    if filename != "run_events.json":
        for events_path in _active_run_event_paths(result_path):
            if not events_path.is_file():
                continue
            payload = _load_json_safe(events_path)
            for event in _events_from_run_events_payload(payload):
                details = event.get("details") or {}
                if not isinstance(details, dict):
                    continue
                archive_path = details.get("archive_path")
                if not archive_path:
                    continue
                archived_sidecar = _sidecar_path_inside_archive(Path(archive_path) / filename)
                if archived_sidecar is not None:
                    _append_unique_path(paths, seen, archived_sidecar)

    # Archive-style active results still use sidecars next to result.json.
    _append_unique_path(paths, seen, result_path.parent / filename)
    return paths


def _case_sidecar_path(
    result_path: Path | None,
    filename: str,
    *,
    is_current: bool,
) -> Path | None:
    for path in _case_sidecar_candidates(result_path, filename, is_current=is_current):
        if path.is_file():
            return path
    return None


def _artifact_metadata(path: Path, *, content_type: str) -> dict:
    return {
        "filename": path.name,
        "path": str(path),
        "content_type": content_type,
        "bytes": path.stat().st_size,
    }


def _archive_case_summaries(limit: int = 200) -> list[dict]:
    """Return newest-first archived runs for the existing SPA Cases tab."""
    root = _archive_root()
    if not root.is_dir():
        return []

    current_run_id = _run_id_for_result(_RESULT, _RESULT_PATH)
    current_path = None
    if _RESULT_PATH is not None:
        try:
            current_path = _RESULT_PATH.resolve()
        except OSError:
            current_path = None

    entries: list[tuple[str, float, dict]] = []
    for case_dir in root.iterdir():
        if not case_dir.is_dir():
            continue
        for run_dir in case_dir.iterdir():
            if not run_dir.is_dir():
                continue
            result_path = run_dir / "result.json"
            if not result_path.is_file():
                continue
            try:
                resolved = result_path.resolve()
                stat_mtime = result_path.stat().st_mtime
            except OSError:
                continue
            if current_path is not None and resolved == current_path:
                continue
            result = _load_json_safe(result_path)
            if result is None:
                continue
            run_id = _run_id_for_result(result, result_path)
            if current_run_id and run_id == current_run_id:
                continue
            base_name = _derive_case_name(result)
            display_name = f"{base_name} [{run_dir.name}]"
            summary = _case_summary(
                result,
                case_id=_archive_case_id(case_dir, run_dir),
                name=display_name,
                source="archive",
                result_path=result_path,
            )
            summary["archive_case_id"] = case_dir.name
            entries.append((run_dir.name, stat_mtime, summary))

    entries.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [summary for _, __, summary in entries[:limit]]


def _build_cases_index() -> list[dict]:
    _reload_result_if_changed()
    return [
        _case_summary(
            _RESULT,
            case_id=_CASE_ID,
            name=_CASE_NAME,
            source="current",
            result_path=_RESULT_PATH,
        ),
        *_archive_case_summaries(),
    ]


def _load_families() -> list[dict]:
    """Load family clusters, enriching members with display names from KG."""
    global _FAMILY_CACHE
    if _FAMILY_CACHE is not None:
        return _FAMILY_CACHE
    if not FAMILY_DIR.is_dir():
        _FAMILY_CACHE = []
        return _FAMILY_CACHE
    kg = _load_kg()
    models_db = kg.get("models", {})
    families = []
    for fp in sorted(FAMILY_DIR.iterdir()):
        if fp.suffix != ".json":
            continue
        data = _load_json_safe(fp)
        if not data or "family_id" not in data:
            continue
        members_enriched = []
        for mid in data.get("members", []):
            m = models_db.get(mid, {})
            members_enriched.append({
                "model_id": mid,
                "display_name": m.get("display_name", mid.replace("-", " ").title()),
            })
        families.append({
            "family_id": data["family_id"],
            "member_count": len(members_enriched),
            "members": members_enriched,
            "corrected_thesis": data.get("corrected_thesis") or data.get("original_thesis") or "",
            "what_this_stack_defeats": data.get("what_this_stack_defeats", ""),
            "density": data.get("density", 0.0),
            "validation_status": data.get("validation_status", ""),
        })
    _FAMILY_CACHE = families
    return _FAMILY_CACHE


def _get_family_detail(family_id: str) -> dict | None:
    """Return full family data including internal edges between members."""
    families = _load_families()
    family = None
    for f in families:
        if f["family_id"] == family_id:
            family = f
            break
    if family is None:
        return None
    member_ids = {m["model_id"] for m in family["members"]}
    kg = _load_kg()
    internal_edges = []
    seen: set[tuple[str, str, str]] = set()
    for e in kg.get("edges", []):
        src, tgt = e.get("source", ""), e.get("target", "")
        etype = e.get("type", "")
        if src in member_ids and tgt in member_ids:
            key = (src, tgt, etype)
            if key not in seen:
                seen.add(key)
                internal_edges.append({"source": src, "target": tgt, "type": etype})
    return {**family, "internal_edges": internal_edges}


def _build_graph_response(result: dict | None = None) -> dict:
    """Build the reasoning graph for the current case.

    Nodes: companion models (large), chunk-referenced models (medium),
    KG neighbors (small). Edges: ally/antagonist/tension from KG.
    """
    if result is None:
        _reload_result_if_changed()
    r = result if result is not None else _RESULT
    kg = _load_kg()
    models_db = kg.get("models", {})
    kg_edges = kg.get("edges", [])
    tendencies_db = kg.get("tendencies", {})

    # 1. Companion model IDs (active in the answer)
    companion = r.get("companion_cheat_sheet", {})
    companion_ids = {a["model_id"] for a in companion.get("anchors", [])}

    # 2. Chunk-referenced model IDs (mentioned in provenance)
    chunk_ref_ids: set[str] = set()
    for a in companion.get("anchors", []):
        for c in a.get("chunks", []):
            rtid = c.get("provenance", {}).get("relation_target_id", "")
            if rtid and rtid not in companion_ids:
                chunk_ref_ids.add(rtid)

    # 3. Seed set = companion + chunk_ref
    seed_ids = companion_ids | chunk_ref_ids

    # 4. Find edges involving seed models (ally/antagonist/tension)
    TYPE_MAP = {"structured_tension": "tension"}
    GRAPH_TYPES = {"ally", "antagonist", "structured_tension"}
    neighbor_ids: set[str] = set()
    graph_edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()

    for e in kg_edges:
        etype = e.get("type", "")
        if etype not in GRAPH_TYPES:
            continue
        src, tgt = e.get("source", ""), e.get("target", "")
        if not (src in seed_ids or tgt in seed_ids):
            continue
        edge_type = TYPE_MAP.get(etype, etype)
        key = (src, tgt, edge_type)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        graph_edges.append({
            "source": src,
            "target": tgt,
            "type": edge_type,
            "affinity": 0.5,
            "description": e.get("context", ""),
        })
        if src not in seed_ids:
            neighbor_ids.add(src)
        if tgt not in seed_ids:
            neighbor_ids.add(tgt)

    # Cap neighbors to avoid an overwhelming graph
    MAX_NEIGHBORS = 20
    if len(neighbor_ids) > MAX_NEIGHBORS:
        # Keep neighbors with most connections to seed nodes
        from collections import Counter
        neighbor_conn: Counter = Counter()
        for e in graph_edges:
            if e["source"] in neighbor_ids:
                neighbor_conn[e["source"]] += 1
            if e["target"] in neighbor_ids:
                neighbor_conn[e["target"]] += 1
        top = {nid for nid, _ in neighbor_conn.most_common(MAX_NEIGHBORS)}
        neighbor_ids = top
        graph_edges = [
            e for e in graph_edges
            if e["source"] in seed_ids | neighbor_ids
            and e["target"] in seed_ids | neighbor_ids
        ]

    # 5. Build nodes
    all_ids = companion_ids | chunk_ref_ids | neighbor_ids
    nodes: list[dict] = []
    for mid in all_ids:
        m = models_db.get(mid, {})
        if mid in companion_ids:
            role = "companion"
        elif mid in chunk_ref_ids:
            role = "chunk_ref"
        else:
            role = "neighbor"
        nodes.append({
            "id": mid,
            "label": m.get("display_name", mid.replace("-", " ").title()),
            "role": role,
        })

    # 6. Tendencies linked to detected tendency IDs
    detected_tids = r.get("detected_tendencies", [])
    if isinstance(detected_tids, list):
        detected_tids = [t if isinstance(t, str) else t.get("tendency_id", "") for t in detected_tids]
    else:
        detected_tids = []

    tendency_list: list[dict] = []
    for tid in detected_tids:
        t = tendencies_db.get(tid, {})
        if not t:
            continue
        tendency_list.append({
            "tendency_id": tid,
            "display_name": t.get("display_name", tid),
            "core_models": [m["model"] if isinstance(m, dict) else m for m in t.get("core_models", [])],
            "antidote_models": [m["model"] if isinstance(m, dict) else m for m in t.get("antidote_models", [])],
        })

    catalog_stats = _get_kg_stats()
    graph_stats = {
        **catalog_stats,
        "catalog_model_count": catalog_stats.get("model_count", 0),
        "catalog_tendency_count": catalog_stats.get("tendency_count", 0),
        "catalog_edge_count": catalog_stats.get("edge_count", 0),
        "companion_count": len(companion_ids),
        "tendency_count": len(tendency_list),
        "total_nodes": len(nodes),
        "rendered_node_count": len(nodes),
        "rendered_edge_count": len(graph_edges),
    }

    return {
        "stats": graph_stats,
        "tendencies": tendency_list,
        "nodes": nodes,
        "edges": graph_edges,
    }


def _get_tendency_catalog() -> list[dict]:
    kg = _load_kg()
    tendencies = kg.get("tendencies", {})
    result = []
    for tid, t in sorted(tendencies.items(), key=lambda x: x[1].get("number", 99)):
        result.append({
            "tendency_id": tid,
            "number": t.get("number"),
            "display_name": t.get("display_name", tid),
            "description": t.get("description", ""),
            "core_models": [m["model"] if isinstance(m, dict) else m for m in t.get("core_models", [])],
            "antidote_models": [m["model"] if isinstance(m, dict) else m for m in t.get("antidote_models", [])],
        })
    return result


def _build_case_response(
    result: dict | None = None,
    *,
    case_id: str | None = None,
    result_path: Path | None = None,
) -> dict:
    """Build the case response from a current or archived pipeline result."""
    if result is None:
        _reload_result_if_changed()
    r = result if result is not None else _RESULT
    response_case_id = case_id or _CASE_ID
    response_result_path = result_path
    if response_result_path is None and result is None:
        response_result_path = _RESULT_PATH

    delta_card = r.get("delta_card")
    companion = r.get("companion_cheat_sheet")
    frame_pressure_card = r.get("frame_pressure_card")
    structural_coverage_card = r.get("structural_coverage_card")
    revised_answer = r.get("revised_answer")

    # Build case metadata from the serialized conversation. Observatory shows
    # query (joined user turns) and vanilla_answer (joined assistant turns)
    # in the case header for context alongside cards/audit data.
    extraction = r.get("extraction", {})
    case_meta = {
        "case_id": response_case_id,
        "query": _joined_user_turns(extraction),
        "vanilla_answer": _joined_assistant_turns(extraction),
    }

    audit_trace = r.get("audit_summary")

    response = {
        "case": case_meta,
        "risk_mode": _risk_mode_for_result(r, response_result_path),
        "delta_card": delta_card,
        "companion": companion,
        "frame_pressure_card": frame_pressure_card,
        "structural_coverage_card": structural_coverage_card,
        "audit_trace": audit_trace,
        "revised_answer": revised_answer,
        "revised_answer_source": r.get("revised_answer_source"),
        "revised_answer_present": r.get("revised_answer_present", revised_answer is not None),
        "gap_check": r.get("gap_check"),
        "gap_check_summary": r.get("gap_check_summary"),
        "has_gap_check": r.get("has_gap_check", False),
        "stakeholder_assumption_check": r.get("stakeholder_assumption_check"),
        "bullshit_profile": r.get("bullshit_profile"),
        "v60_enrichment": r.get("v60_enrichment"),
        "v60_consideration_ledger": r.get("v60_consideration_ledger"),
        "v60_consideration_validation": r.get("v60_consideration_validation"),
        "pre_step6_private_table": r.get("pre_step6_private_table"),
        "pre_step6_private_table_ledger": r.get("pre_step6_private_table_ledger"),
        "pre_step6_shadow_portfolio": r.get("pre_step6_shadow_portfolio"),
    }

    # Run health — surfaces capture, substrate, embeddings, fingerprint status
    run_health = r.get("run_health")
    if run_health:
        response["run_health"] = run_health

    # Usage summary — per-run cost & call-count telemetry. Built by
    # run_pipeline.py and (for sub-agent calls) topped up by SKILL Step 8b.
    usage_summary = r.get("usage_summary")
    if usage_summary:
        response["usage_summary"] = usage_summary

    # Prompt versions — per-stage hashes of the system prompts used in this
    # run. Useful for reproducibility (which prompt revision produced this
    # finding) and for diffing two runs of the same case. Include the field
    # whenever the key exists (even if `{}`) so consumers can distinguish
    # "supported but empty" from "not provided" — keeps the API shape stable.
    if "prompt_versions" in r:
        response["prompt_versions"] = r.get("prompt_versions") or {}

    return response


def _render_usage_html() -> str:
    """Standalone HTML page that visualizes usage_summary.

    Lives at /usage so the user can inspect cost/calls without depending on
    the React SPA being rebuilt to consume the new field. The SPA already
    receives ``usage_summary`` via /api/case/<id>; this page is a fallback
    that's guaranteed to render whatever the pipeline wrote.
    """
    _reload_result_if_changed()
    us = _RESULT.get("usage_summary") or {}
    if not us:
        return _render_scaffold(
            title="Lolla — Usage Summary",
            current_path="/usage",
            body=(
                "<h1>Usage Summary</h1>"
                "<div class=\"empty\">No <code>usage_summary</code> in this result. "
                "Re-run the pipeline with the updated <code>run_pipeline.py</code> "
                "to populate it.</div>"
            ),
        )
    vendors = us.get("vendors", {}) or {}

    rows = []
    rows.append(
        "<tr><th>Vendor</th><th>Calls</th><th>Tokens (in / cached / out)</th>"
        "<th>Cache hit</th><th>Estimated cost</th></tr>"
    )
    for key, label in [
        ("openrouter", "OpenRouter"),
        ("openai_embeddings", "OpenAI (embeddings + expansion)"),
        ("anthropic_subagents", "Anthropic (Step-7 sub-agents)"),
    ]:
        v = vendors.get(key) or {}
        if not v:
            continue
        if key == "openrouter":
            tokens = (
                f"{_fmt_int(v.get('prompt_tokens'))} / "
                f"{_fmt_int(v.get('cached_tokens'))} / "
                f"{_fmt_int(v.get('completion_tokens'))}"
            )
            cache = f"{(v.get('cache_hit_rate') or 0) * 100:.1f}%"
        elif key == "openai_embeddings":
            tokens = (
                f"{_fmt_int(v.get('input_tokens'))} / — / "
                f"{_fmt_int(v.get('output_tokens'))}"
            )
            cache = "n/a"
        else:
            tokens = f"{_fmt_int(v.get('total_tokens'))} (total only)"
            cache = "n/a"
        rows.append(
            f"<tr><td>{_esc(label)}</td><td>{_fmt_int(v.get('calls'))}</td>"
            f"<td>{tokens}</td><td>{cache}</td>"
            f"<td>{_fmt_usd(v.get('estimated_cost_usd'))}</td></tr>"
        )

    # OpenRouter per-stage breakdown — now includes cache-hit % per stage,
    # which is the key signal for "where is caching actually working." On a
    # typical Lolla run BI pulls high cache rates (shared system prompt
    # across passages); pipeline lanes pull low rates because each stage
    # has a different system prompt. Surfacing the gap directly tells the
    # operator where the next prompt-restructuring win lives.
    or_block = vendors.get("openrouter") or {}
    stage_rows = []
    for stage, totals in sorted(
        (or_block.get("stages") or {}).items(),
        key=lambda kv: -kv[1].get("calls", 0),
    ):
        prompt_tok = totals.get("prompt_tokens", 0) or 0
        cached_tok = totals.get("cached_tokens", 0) or 0
        hit_rate = (cached_tok / prompt_tok * 100) if prompt_tok else 0.0
        stage_rows.append(
            f"<tr><td>{_esc(stage)}</td>"
            f"<td>{_fmt_int(totals.get('calls'))}</td>"
            f"<td>{_fmt_int(prompt_tok)}</td>"
            f"<td>{_fmt_int(cached_tok)}</td>"
            f"<td>{hit_rate:.1f}%</td>"
            f"<td>{_fmt_int(totals.get('completion_tokens'))}</td></tr>"
        )

    # OpenAI by-model breakdown — surfaces the embed vs. expansion split
    # that the vendor row aggregates away.
    embed_block = vendors.get("openai_embeddings") or {}
    embed_rows = []
    for model, info in (embed_block.get("by_model") or {}).items():
        embed_rows.append(
            f"<tr><td>{_esc(model)}</td>"
            f"<td>{_fmt_int(info.get('calls'))}</td>"
            f"<td>{_fmt_int(info.get('input_tokens'))}</td>"
            f"<td>{_fmt_int(info.get('output_tokens'))}</td>"
            f"<td>{_fmt_usd(info.get('estimated_cost_usd'))}</td></tr>"
        )

    # Anthropic sub-agents by lane — built by the enhanced
    # _build_subagent_vendor_block. Tells the operator which Step-7 lane
    # (1=Delta, 2=Companion, 3=Frame, 4=Coverage) was actually spawned and
    # what each cost. Lanes that were skipped_empty / skipped_error are
    # absent because they shouldn't be in the input records (per the SKILL
    # Step 8b filter).
    sub_block = vendors.get("anthropic_subagents") or {}
    sub_rows = []
    LANE_NAMES = {
        "1": "DeltaCard",
        "2": "CompanionCheatSheet",
        "3": "FramePressureCard",
        "4": "StructuralCoverageCard",
    }
    for lane_key, info in (sub_block.get("by_lane") or {}).items():
        lane_label = f"{lane_key} ({LANE_NAMES.get(lane_key, '?')})" if lane_key in LANE_NAMES else lane_key
        sub_rows.append(
            f"<tr><td>{_esc(lane_label)}</td>"
            f"<td>{_esc(info.get('model'))}</td>"
            f"<td>{_esc(info.get('status'))}</td>"
            f"<td>{_fmt_int(info.get('calls'))}</td>"
            f"<td>{_fmt_int(info.get('total_tokens'))}</td>"
            f"<td>{_fmt_int(info.get('duration_ms'))} ms</td>"
            f"<td>{_fmt_usd(info.get('estimated_cost_usd'))}</td></tr>"
        )

    # Prompt versions — per-stage system-prompt hashes, useful for
    # reproducibility ("which prompt revision produced this finding?") and
    # for diffing two runs of the same case.
    prompt_versions = _RESULT.get("prompt_versions") or {}
    pv_rows = []
    for stage, ver_hash in sorted(prompt_versions.items()):
        # Display the documented 12-char hash form. Upstream currently emits
        # 12 chars already so this is a no-op today; truncating defensively
        # keeps the UI contract stable if upstream ever switches to longer
        # hashes. Full hash is preserved in the title attribute for hover.
        full = str(ver_hash)
        short = full[:12]
        pv_rows.append(
            f"<tr><td>{_esc(stage)}</td>"
            f"<td><code title=\"{_esc(full)}\">{_esc(short)}</code></td></tr>"
        )

    notes_html = "".join(f"<li>{_esc(n)}</li>" for n in (us.get("notes") or []))

    body = f"""
<h1>Usage Summary</h1>
<div class="meta">
  Run: <code>{_esc(us.get("run_id", "—"))}</code> ·
  Pricing table verified: <code>{_esc(us.get("pricing_table_version", "—"))}</code> ·
  <a href="/">back to Observatory</a> ·
  <a href="/audit">audit panels</a>
</div>
<div style="font-size:1.6rem;font-weight:600;margin:1rem 0 1.5rem;">Total estimated cost: <strong>{_fmt_usd(us.get("estimated_total_cost_usd"))}</strong></div>

<h2>By vendor</h2>
<table>{"".join(rows)}</table>

<h2>OpenRouter — by stage</h2>
<p class="hint">Cache-hit % per stage tells you where prompt-prefix sharing is actually working. Stages whose system prompt is identical across calls (e.g. <code>bullshit_index</code> across all passages) cache well; stages with per-call-varying system prompts (most pipeline lanes) cache poorly.</p>
<table>
<tr><th>Stage</th><th>Calls</th><th>Prompt tokens</th><th>Cached tokens</th><th>Cache hit %</th><th>Completion tokens</th></tr>
{"".join(stage_rows) if stage_rows else "<tr><td colspan='6'>No OpenRouter calls recorded.</td></tr>"}
</table>

<h2>OpenAI — by model</h2>
<table>
<tr><th>Model</th><th>Calls</th><th>Input tokens</th><th>Output tokens</th><th>Estimated cost</th></tr>
{"".join(embed_rows) if embed_rows else "<tr><td colspan='5'>No OpenAI calls recorded.</td></tr>"}
</table>

<h2>Anthropic Step-7 sub-agents — by lane</h2>
<p class="hint">Sub-agent token counts come from Claude Code task notifications, which expose <code>total_tokens</code> only — no prompt/completion split. The cost estimate treats the whole total as input (conservative over-estimate).</p>
<table>
<tr><th>Lane</th><th>Model</th><th>Status</th><th>Calls</th><th>Total tokens</th><th>Duration</th><th>Estimated cost</th></tr>
{"".join(sub_rows) if sub_rows else "<tr><td colspan='7'>No sub-agent calls recorded yet (added by SKILL Step 8b after Step 7 completes).</td></tr>"}
</table>

<h2>Prompt versions</h2>
<p class="hint">12-char hash of the system prompt used at each stage. Two runs of the same case with the same hashes received identical prompts. Different hashes mean a prompt revision happened in between.</p>
<table>
<tr><th>Stage</th><th>Prompt hash</th></tr>
{"".join(pv_rows) if pv_rows else "<tr><td colspan='2'>No prompt versions recorded.</td></tr>"}
</table>

<h2>Notes</h2>
<ul class="empty" style="list-style:disc;padding-left:1.5rem;">{notes_html}</ul>
"""
    return _render_scaffold(title="Lolla — Usage Summary", body=body, current_path="/usage")


# ---------------------------------------------------------------------------
# Audit panels (PR 3 of the 2026-04-28 visibility roadmap).
#
# Each panel is server-rendered HTML, mirrors the shape of `_render_usage_html`,
# and works whether or not the SPA bundle is present. They surface the
# `audit_summary` fields the React SPA never renders. Fields added by PR 1
# (raw_message_content per boundary call) and PR 2 (embedding_tendency_ranks,
# deep_check_results.reason, companion_verification_silently_omitted) are
# rendered when present and degrade silently when absent — so panels work
# against both fresh runs and older archived result.json files.
# ---------------------------------------------------------------------------


_TRIAGE_THRESHOLD_DEFAULT = 4
_EMBEDDING_PROMOTION_THRESHOLD = 0.30
_DETECTED_MODELS_CAP_LABEL = "5"  # mirrors engine.system_b.companion_routing._DETECTED_MODELS_CAP
_LANE2_AUTO_OPEN_THRESHOLD = 20  # candidates table opens by default if pool ≤ this; collapsed otherwise


def _audit_summary() -> dict:
    """Pull the audit_summary block, returning ``{}`` for ancient artifacts."""
    return _RESULT.get("audit_summary") or {}


def _computed_anti_echo_exclusions() -> list[dict]:
    """Reconstruct structural-coverage anti-echo rows from surfaced lanes.

    Older route traces did not persist cross-lane anti-echo rows even though
    ``structural_coverage_card.anti_echo_model_ids`` carried the computed
    exclusions. The route page uses this as a display fallback so it does not
    contradict the dedicated Anti-echo page.
    """
    coverage = _RESULT.get("structural_coverage_card") or {}
    excluded = coverage.get("anti_echo_model_ids") or []
    if not excluded:
        return []

    lane1_models: set[str] = set()
    for finding in (_RESULT.get("delta_card") or {}).get("findings") or []:
        for model_id in finding.get("selected_model_ids") or []:
            if model_id:
                lane1_models.add(model_id)

    lane2_models: set[str] = set()
    for anchor in (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []:
        if anchor.get("model_id"):
            lane2_models.add(anchor["model_id"])

    lane3_models: set[str] = set()
    for reframing in (_RESULT.get("frame_pressure_card") or {}).get("reframings") or []:
        grounding_model = reframing.get("grounding_model")
        if grounding_model:
            lane3_models.add(grounding_model)

    rows: list[dict] = []
    for model_id in excluded:
        source_lanes = []
        if model_id in lane1_models:
            source_lanes.append("Lane 1")
        if model_id in lane2_models:
            source_lanes.append("Lane 2")
        if model_id in lane3_models:
            source_lanes.append("Lane 3")
        rows.append(
            {
                "model_id": model_id,
                "excluded_from": "Lane 4 structural coverage",
                "reason": "computed_from_structural_coverage_card.anti_echo_model_ids",
                "source_lanes": source_lanes or ["unattributed"],
            }
        )
    return rows


def _route_trace() -> dict:
    audit = _audit_summary()
    trace = audit.get("route_trace")
    if isinstance(trace, dict):
        return trace
    try:
        from system_b.route_trace import build_route_trace_payload
        return build_route_trace_payload(_RESULT)
    except Exception:
        return {}


# ---------------- Panel 1: /audit/lane1 ----------------


def _render_lane1_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()

    header = _render_run_header()

    if not audit:
        body = (
            "<h1>Lane 1 — Pass 1 + Pass 2 funnel</h1>"
            f"{header}"
            + _empty_inline(
                "This run was captured before Phase-7 audit observability — "
                "no <code>audit_summary</code> in the result. Re-run the "
                "pipeline to populate the Lane 1 trace."
            )
        )
        return _render_scaffold(title="Lolla — Lane 1", body=body, current_path="/audit/lane1")

    triage = audit.get("triage_scores") or []
    triggered_sources = audit.get("triggered_tendency_sources") or []
    deep_results = audit.get("deep_check_results") or []
    embedding_ranks = audit.get("embedding_tendency_ranks") or []

    # Pass 1 triage table — every scored tendency, sorted by score desc
    triage_rows = []
    for s in sorted(triage, key=lambda r: -int(r.get("score") or 0)):
        triage_rows.append(
            f"<tr><td>{_esc(s.get('tendency_id', ''))}</td>"
            f"<td class='num'>{_esc(s.get('score', 0))}</td>"
            f"<td>{_esc(s.get('evidence', ''))}</td></tr>"
        )

    # Triggered set with source attribution
    src_rows = []
    for t in triggered_sources:
        source = t.get("source", "")
        score = t.get("score", "")
        score_str = f"{float(score):.3f}" if isinstance(score, float) else _esc(score)
        src_rows.append(
            f"<tr><td>{_esc(t.get('tendency_id', ''))}</td>"
            f"<td><span class='tag'>{_esc(source)}</span></td>"
            f"<td class='num'>{score_str}</td></tr>"
        )

    # Pass 2 deep_check outcomes
    pass2_rows = []
    detected_count = 0
    for d in deep_results:
        detected = bool(d.get("detected"))
        if detected:
            detected_count += 1
        cls = "detected-true" if detected else "detected-false"
        verdict = "detected" if detected else "not detected"
        reason = d.get("reason") or ""
        sub_pattern = d.get("sub_pattern") or ""
        pass2_rows.append(
            f"<tr><td>{_esc(d.get('tendency_id', ''))}</td>"
            f"<td class='{cls}'>{verdict}</td>"
            f"<td>{_esc(sub_pattern)}</td>"
            f"<td>{_esc(reason)}</td></tr>"
        )

    # Embedding close-calls — full top-25 ranks (promoted + sub-threshold)
    close_call_rows = []
    for r in embedding_ranks:
        promoted = bool(r.get("promoted"))
        cls = "tag ok" if promoted else "tag"
        label = "promoted" if promoted else "close call"
        score = r.get("score")
        score_str = f"{float(score):.3f}" if isinstance(score, (int, float)) else _esc(score)
        close_call_rows.append(
            f"<tr><td>{_esc(r.get('tendency_id', ''))}</td>"
            f"<td class='num'>{score_str}</td>"
            f"<td><span class='{cls}'>{label}</span></td></tr>"
        )

    threshold_ids = {
        row.get("tendency_id")
        for row in triage
        if row.get("tendency_id")
        and int(row.get("score") or 0) >= _TRIAGE_THRESHOLD_DEFAULT
    }
    advanced_ids = {
        row.get("tendency_id")
        for row in triggered_sources
        if row.get("tendency_id")
    }
    if not advanced_ids:
        advanced_ids = set(threshold_ids)
    embedding_promoted_ids = {
        row.get("tendency_id")
        for row in triggered_sources
        if row.get("tendency_id")
        and row.get("tendency_id") not in threshold_ids
        and "embedding" in str(row.get("source", "")).lower()
    }
    other_advanced_ids = advanced_ids - threshold_ids - embedding_promoted_ids

    advancement_parts = [
        f"<strong>{len(threshold_ids)}</strong> crossed the triage threshold",
    ]
    if embedding_promoted_ids:
        advancement_parts.append(
            f"<strong>{len(embedding_promoted_ids)}</strong> were embedding-promoted"
        )
    if other_advanced_ids:
        advancement_parts.append(
            f"<strong>{len(other_advanced_ids)}</strong> advanced by other route"
        )
    advancement = ", ".join(advancement_parts)
    lede = (
        f"Of <strong>{len(triage)}</strong> tendencies the system triaged, "
        f"{advancement}; Pass 2 checked <strong>{len(deep_results)}</strong> "
        f"and confirmed <strong>{detected_count}</strong>."
    )

    body = f"""
<h1>Lane 1 — Pass 1 + Pass 2 funnel</h1>
{header}
<p class="lede">{lede}</p>

<h2>Pass 1 — Triage scores ({len(triage_rows)} tendencies)</h2>
<p class="hint">Triage threshold: <code>{_TRIAGE_THRESHOLD_DEFAULT}</code>. Tendencies at or above this score advance to Pass 2 deep-check; the rest stay observed but unverified.</p>
<table>
<tr><th>Tendency</th><th class="num">Score</th><th>Evidence</th></tr>
{"".join(triage_rows) if triage_rows else "<tr><td colspan='3' class='empty'>No triage scores recorded for this run.</td></tr>"}
</table>

<h2>Advanced set ({len(src_rows)} advanced to Pass 2)</h2>
<p class="hint">Where each promotion came from — <code>triage</code> (Pass 1 score), <code>embedding</code> (cosine match against the catalog), or <code>always_include</code> (rules-based, surfaces regardless of score).</p>
<table>
<tr><th>Tendency</th><th>Source</th><th class="num">Score</th></tr>
{"".join(src_rows) if src_rows else "<tr><td colspan='3' class='empty'>The Pass 1 triage promoted no tendencies on this run.</td></tr>"}
</table>

<h2>Pass 2 — Deep check outcomes</h2>
<p class="hint">For each promoted tendency, the deep check returns a verdict, a sub-pattern label when relevant, and the model's reasoning for either outcome.</p>
<table>
<tr><th>Tendency</th><th>Verdict</th><th>Sub-pattern</th><th>Reason</th></tr>
{"".join(pass2_rows) if pass2_rows else "<tr><td colspan='4' class='empty'>No Pass 2 outcomes — the triage promoted nothing to deep-check.</td></tr>"}
</table>

<h2>Embedding close-calls — full top-25 ranks</h2>
<p class="hint">Cosine match scores for every catalog tendency, including those below the <code>{_EMBEDDING_PROMOTION_THRESHOLD}</code> promotion floor. Sub-threshold rows surface "almost-made-it" cases — useful when calibrating where the floor sits.</p>
<table>
<tr><th>Tendency</th><th class="num">Cosine</th><th>Status</th></tr>
{"".join(close_call_rows) if close_call_rows else "<tr><td colspan='3' class='empty'>No embedding ranks recorded (embeddings off for this run, or run pre-dates PR 2).</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 1", body=body, current_path="/audit/lane1")


# ---------------- Panel 2: /audit/lane2 ----------------


def _render_lane2_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()

    header = _render_run_header()

    if not audit:
        body = (
            "<h1>Lane 2 — Companion selection funnel</h1>"
            f"{header}"
            + _empty_inline(
                "This run was captured before Phase-7 audit observability — "
                "no <code>audit_summary</code> in the result."
            )
        )
        return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")

    candidates = audit.get("companion_candidates") or []
    accepted_before_cap = audit.get("companion_verification_accepted_before_cap") or []

    if not candidates and not accepted_before_cap:
        body = (
            "<h1>Lane 2 — Companion selection funnel</h1>"
            f"{header}"
            + _empty_inline(
                "Lane 2 stayed quiet on this case — the system surfaced no "
                "companion-model candidates worth verifying."
            )
        )
        return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")

    accepted = accepted_before_cap
    capped = audit.get("companion_verification_capped_models") or []
    rejected = audit.get("companion_rejected_models") or []
    duplicates = audit.get("companion_verification_duplicate_accepts") or []
    quote_repairs = audit.get("companion_verification_quote_repairs") or []
    silently_omitted = audit.get("companion_verification_silently_omitted") or []
    candidate_cap = audit.get("companion_candidate_cap", 0)

    final_anchors = (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []

    cand_rows = []
    for c in candidates:
        cand_rows.append(
            f"<tr><td>{_esc(c.get('model_id', ''))}</td>"
            f"<td>{_esc(c.get('recall_source', ''))}</td>"
            f"<td class='num'>{_esc(c.get('keyword_rank', ''))}</td>"
            f"<td class='num'>{_esc(c.get('embedding_rank', ''))}</td>"
            f"<td class='num'>{_esc(c.get('final_rank', ''))}</td>"
            f"<td>{_esc(c.get('activation_trigger', ''))}</td></tr>"
        )

    acc_rows = []
    for a in accepted:
        acc_rows.append(
            f"<tr><td>{_esc(a.get('model_id', ''))}</td>"
            f"<td>{_esc(a.get('presence_mode', ''))}</td>"
            f"<td>{_esc(a.get('evidence_quote', ''))}</td>"
            f"<td>{_esc(a.get('presence_explanation', ''))}</td></tr>"
        )

    rej_rows = []
    for r in rejected:
        rej_rows.append(
            f"<tr><td>{_esc(r.get('model_id', ''))}</td>"
            f"<td>{_esc(r.get('rejection_reason', ''))}</td></tr>"
        )

    cap_rows = [
        f"<tr><td>{_esc(c.get('model_id', ''))}</td><td>{_esc(c.get('drop_reason', ''))}</td></tr>"
        for c in capped
    ]
    dup_rows = [
        f"<tr><td>{_esc(d.get('model_id', ''))}</td><td>{_esc(d.get('drop_reason', ''))}</td></tr>"
        for d in duplicates
    ]
    qr_rows = [
        f"<tr><td>{_esc(q.get('model_id', ''))}</td>"
        f"<td>{_esc(q.get('repair_method', ''))}</td>"
        f"<td>{_esc(q.get('original_evidence_quote', ''))}</td>"
        f"<td>{_esc(q.get('repaired_evidence_quote', ''))}</td></tr>"
        for q in quote_repairs
    ]
    so_rows = [
        f"<tr><td>{_esc(s.get('model_id', ''))}</td><td>{_esc(s.get('drop_reason', ''))}</td></tr>"
        for s in silently_omitted
    ]

    lede = (
        f"From <strong>{len(candidates)}</strong> companion candidates, the system "
        f"surfaced <strong>{len(final_anchors)}</strong> cheat-sheet anchors. "
        f"<strong>{len(quote_repairs)}</strong> arrived via verifier-repaired quotes; "
        f"<strong>{len(silently_omitted)}</strong> the verifier never named."
    )

    # Threshold-based collapse — small candidate pools open inline (operator
    # sees everything at a glance); larger ones collapse to keep the page
    # scannable. Threshold lives in _LANE2_AUTO_OPEN_THRESHOLD.
    cand_open_attr = " open" if len(candidates) <= _LANE2_AUTO_OPEN_THRESHOLD else ""
    cand_table = (
        "<table>"
        '<tr><th>Model</th><th>Recall source</th><th class="num">Kw rank</th>'
        '<th class="num">Emb rank</th><th class="num">Final rank</th>'
        "<th>Activation trigger</th></tr>"
        + ("".join(cand_rows) if cand_rows else "<tr><td colspan='6' class='empty'>No candidates on this run.</td></tr>")
        + "</table>"
    )

    body = f"""
<h1>Lane 2 — Companion selection funnel</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">Candidate pool cap: <code>{_esc(candidate_cap)}</code>. The system pulls candidates via keyword, embedding, and curated activation triggers, then verifies each against the conversation before promoting up to the top {_DETECTED_MODELS_CAP_LABEL} as cheat-sheet anchors.</p>

<details{cand_open_attr}>
<summary><strong>Candidates ({len(candidates)} sent to verifier)</strong>{" · click to expand" if not cand_open_attr else ""}</summary>
{cand_table}
</details>

<h2>Accepted before top-{_DETECTED_MODELS_CAP_LABEL} cap ({len(accepted)})</h2>
<p class="hint">Verifier-confirmed candidates that carried evidence the system could quote. The cap then trims to the strongest few; surplus rows show under <em>Capped</em>.</p>
<table>
<tr><th>Model</th><th>Mode</th><th>Evidence quote</th><th>Explanation</th></tr>
{"".join(acc_rows) if acc_rows else "<tr><td colspan='4' class='empty'>The verifier confirmed none of the candidates on this run.</td></tr>"}
</table>

<h2>Rejected ({len(rejected)})</h2>
<p class="hint">Candidates the verifier examined and declined to surface, with the reasoning the model gave.</p>
<table>
<tr><th>Model</th><th>Rejection reason</th></tr>
{"".join(rej_rows) if rej_rows else "<tr><td colspan='2' class='empty'>The verifier rejected none — every candidate it considered passed muster.</td></tr>"}
</table>

<h2>Capped — accepted but not surfaced ({len(capped)})</h2>
<p class="hint">Candidates the verifier accepted but the top-{_DETECTED_MODELS_CAP_LABEL} cap held back. Visible here so the operator can see what would have surfaced if the cap were higher.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(cap_rows) if cap_rows else "<tr><td colspan='2' class='empty'>The accepted set fit under the cap on this run.</td></tr>"}
</table>

<h2>Duplicate accepts ({len(duplicates)})</h2>
<p class="hint">When the verifier names the same model twice, only the first is kept. Duplicates often signal a verifier-prompt clarity issue worth tuning.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(dup_rows) if dup_rows else "<tr><td colspan='2' class='empty'>The verifier named each accepted model once.</td></tr>"}
</table>

<h2>Quote repairs ({len(quote_repairs)})</h2>
<p class="hint">When the verifier returns an evidence quote that doesn't match the source verbatim, the repair pass fixes it. Visible repairs are healthy — invisible ones would be drift.</p>
<table>
<tr><th>Model</th><th>Method</th><th>Original</th><th>Repaired</th></tr>
{"".join(qr_rows) if qr_rows else "<tr><td colspan='4' class='empty'>Every accepted quote matched its source on the first pass.</td></tr>"}
</table>

<h2>Silently omitted by verifier ({len(silently_omitted)})</h2>
<p class="hint">Candidates sent to the verifier that never appeared in either accepted or rejected. A verifier prompt-tuning signal — when this grows, the verifier is dropping context. Drop reason: <code>not_in_verifier_response</code>.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(so_rows) if so_rows else "<tr><td colspan='2' class='empty'>The verifier named every candidate it received (or the run pre-dates PR 2).</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")


# ---------------- Panel 4: /audit/lane4 ----------------


def _load_lane4_dimension_catalog() -> list[dict[str, str]]:
    """Return the 15-dimension catalog from data/knowledge_graph.json.

    Cached at module level via ``_KG_CACHE``. Each row carries
    ``dimension_id`` + ``dimension_name``. Loaded at render time so the
    panel always reflects the live catalog.
    """
    global _KG_CACHE
    if _KG_CACHE is None:
        try:
            with open(SKILL_DATA_DIR / "knowledge_graph.json") as f:
                _KG_CACHE = json.load(f)
        except OSError:
            return []
    sc = (_KG_CACHE or {}).get("structural_coverage_routing", {}) or {}
    dims = sc.get("dimensions", {}) or {}
    return [
        {"dimension_id": d_id, "dimension_name": d.get("dimension_name", d_id)}
        for d_id, d in dims.items()
    ]


def _render_lane4_html() -> str:
    _reload_result_if_changed()
    coverage = _RESULT.get("structural_coverage_card") or {}
    catalog = _load_lane4_dimension_catalog()

    header = _render_run_header()

    if not catalog:
        body = (
            "<h1>Lane 4 — Dimension coverage</h1>"
            f"{header}"
            + _empty_inline(
                "Dimension catalog not found in "
                "<code>data/knowledge_graph.json</code>."
            )
        )
        return _render_scaffold(title="Lolla — Lane 4", body=body, current_path="/audit/lane4")

    detected_dims = coverage.get("dimensions") or []
    detected_by_id = {d.get("dimension_id"): d for d in detected_dims if d.get("dimension_id")}
    gap_questions_by_id: dict[str, list[str]] = {}
    for gq in coverage.get("gap_questions") or []:
        if isinstance(gq, dict) and gq.get("dimension_id"):
            qs = gq.get("questions") or []
            if isinstance(qs, list):
                gap_questions_by_id[gq["dimension_id"]] = [str(q) for q in qs]

    question_type = coverage.get("question_type", "")

    # 15-row dimension table
    dim_rows = []
    covered_count = 0
    gap_count = 0
    for cat in catalog:
        d_id = cat["dimension_id"]
        d_name = cat["dimension_name"]
        dim = detected_by_id.get(d_id)
        if not dim:
            status = "<span class='tag'>not detected</span>"
            covered = "—"
            note = "—"
        elif dim.get("covered"):
            covered_count += 1
            status = "<span class='tag ok'>covered</span>"
            covered = _esc(dim.get("coverage_evidence", ""))
            note = _esc(dim.get("materiality_note", ""))
        else:
            gap_count += 1
            status = "<span class='tag warn'>gap</span>"
            covered = "—"
            note = _esc(dim.get("materiality_note", ""))
        dim_rows.append(
            f"<tr><td>{_esc(d_id)}</td><td>{_esc(d_name)}</td>"
            f"<td>{status}</td><td>{covered}</td><td>{note}</td></tr>"
        )

    # Gap routes
    route_rows = []
    for r in (coverage.get("gap_routes") or []):
        cands = ", ".join(_esc(m) for m in (r.get("candidate_model_ids") or []))
        excluded = ", ".join(_esc(m) for m in (r.get("excluded_model_ids") or []))
        route_rows.append(
            f"<tr><td>{_esc(r.get('dimension_id', ''))}</td>"
            f"<td>{cands or '—'}</td><td>{excluded or '—'}</td></tr>"
        )

    # Gap questions
    gq_rows = []
    for d_id, qs in gap_questions_by_id.items():
        for q in qs:
            gq_rows.append(f"<tr><td>{_esc(d_id)}</td><td>{_esc(q)}</td></tr>")

    observed_count = len(detected_dims)

    lede = (
        f"Of <strong>{len(catalog)}</strong> catalog dimensions, the system "
        f"observed <strong>{observed_count}</strong> in this case — "
        f"<strong>{covered_count}</strong> covered, "
        f"<strong>{gap_count}</strong> flagged as gaps. "
        f"Question type: <code>{_esc(question_type) or '—'}</code>."
    )

    body = f"""
<h1>Lane 4 — Dimension coverage</h1>
{header}
<p class="lede">{lede}</p>

<h2>{len(catalog)}-dimension catalog</h2>
<p class="hint">Every catalog dimension, marked by status: <span class="tag ok">covered</span> when the answer addresses it, <span class="tag warn">gap</span> when the system observed but the answer didn't address, <span class="tag">not detected</span> when the case never raised it.</p>
<table>
<tr><th>Dimension ID</th><th>Name</th><th>Status</th><th>Coverage evidence</th><th>Materiality</th></tr>
{"".join(dim_rows)}
</table>

<h2>Gap routes</h2>
<p class="hint">For each gap dimension, the curated routing names corrective models. <em>Excluded</em> column shows models held back by anti-echo because earlier lanes already surfaced them — see <a href="/audit/anti-echo">/audit/anti-echo</a> for the cascade view.</p>
<table>
<tr><th>Dimension</th><th>Candidate models</th><th>Excluded (anti-echo)</th></tr>
{"".join(route_rows) if route_rows else "<tr><td colspan='3' class='empty'>No gap routes on this run — every observed dimension was covered or no gaps surfaced.</td></tr>"}
</table>

<h2>Gap questions</h2>
<p class="hint">Questions the user can pose to themselves to address each gap directly — generated from the curated dimension materiality.</p>
<table>
<tr><th>Dimension</th><th>Question</th></tr>
{"".join(gq_rows) if gq_rows else "<tr><td colspan='2' class='empty'>No gap questions on this run.</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 4", body=body, current_path="/audit/lane4")


# ---------------- Panel: /audit/anti-echo ----------------


def _render_anti_echo_html() -> str:
    _reload_result_if_changed()
    coverage = _RESULT.get("structural_coverage_card") or {}
    excluded = coverage.get("anti_echo_model_ids") or []

    header = _render_run_header()

    if not excluded:
        body = (
            "<h1>Anti-echo cascade</h1>"
            f"{header}"
            + _empty_inline(
                "No anti-echo cascading on this run — every Lane 4 candidate "
                "stood on its own."
            )
        )
        return _render_scaffold(title="Lolla — Anti-echo", body=body, current_path="/audit/anti-echo")

    # Compute per-lane source attribution.
    # Lane 1: delta_card.findings[*].selected_model_ids
    lane1_models: set[str] = set()
    for f in (_RESULT.get("delta_card") or {}).get("findings") or []:
        for mid in (f.get("selected_model_ids") or []):
            if mid:
                lane1_models.add(mid)

    # Lane 2: companion_cheat_sheet.anchors[*].model_id
    lane2_models: set[str] = set()
    for a in (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []:
        if a.get("model_id"):
            lane2_models.add(a["model_id"])

    # Lane 3: frame_pressure_card.reframings[*].grounding_model
    lane3_models: set[str] = set()
    for r in (_RESULT.get("frame_pressure_card") or {}).get("reframings") or []:
        gm = r.get("grounding_model")
        if gm:
            lane3_models.add(gm)

    rows = []
    for mid in excluded:
        sources = []
        if mid in lane1_models:
            sources.append("Lane 1")
        if mid in lane2_models:
            sources.append("Lane 2")
        if mid in lane3_models:
            sources.append("Lane 3")
        tag_html = (
            "".join(f"<span class='tag'>{s}</span>" for s in sources)
            if sources
            else "<span class='tag warn'>unattributed</span>"
        )
        rows.append(
            f"<tr><td>{_esc(mid)}</td><td><div class='tagrow'>{tag_html}</div></td></tr>"
        )

    lede = (
        f"<strong>{len(excluded)}</strong> models held back from Lane 4 because "
        "earlier lanes already surfaced them. Redundancy prevention, not defect."
    )

    body = f"""
<h1>Anti-echo cascade</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">Each row names a model the system removed from Lane 4's candidate pool because an upstream lane (1, 2, or 3) already surfaced it. The lane-of-origin tag is reconstructed at render time by intersecting <code>anti_echo_model_ids</code> against each upstream lane's surfaced models — no new telemetry needed.</p>

<table>
<tr><th>Excluded model</th><th>Source lane(s)</th></tr>
{"".join(rows)}
</table>
"""
    return _render_scaffold(title="Lolla — Anti-echo", body=body, current_path="/audit/anti-echo")


# ---------------- Panel: /audit/routing ----------------


_TIEBREAKER_ABORT_REASONS_HUMAN = {
    "fewer_than_2_candidates": "Fewer than 2 candidates — gate doesn't apply.",
    "fewer_than_2_after_dedup": "Fewer than 2 candidates after dedup — gate doesn't apply.",
    "outside_epsilon_window": "Outside near-tie window — affinity gap was decisive.",
    "matcher_exception": "Matcher raised an exception — gate aborted defensively.",
    "matcher_empty_result": "Matcher returned no activation match — fell back to top-1.",
    "below_noise_floor": "Both top-2 below the activation noise floor — fell back to top-1.",
    "no_improvement": "Activation match didn't favour top-2 — kept original top-1.",
}


def _render_tiebreaker_cell(trace: dict | None) -> str:
    if not trace:
        return "<span class='empty'>—</span>"
    if trace.get("fired"):
        return f"<span class='tag ok'>fired</span>"
    abort_reason = str(trace.get("abort_reason") or "")
    human = _TIEBREAKER_ABORT_REASONS_HUMAN.get(abort_reason, abort_reason or "—")
    return f"<span class='tag'>aborted</span> <small>{_esc(human)}</small>"


def _format_model_list(values) -> str:
    items = [str(value) for value in (values or []) if str(value or "").strip()]
    if not items:
        return "—"
    return ", ".join(f"<code>{_esc(item)}</code>" for item in items)


def _format_rejected_models(values, *, limit: int = 5) -> str:
    rows = []
    for item in list(values or [])[:limit]:
        if not isinstance(item, dict):
            continue
        model_id = item.get("model_id", "")
        reason = item.get("rejection_reason", "")
        stage = item.get("stage", "")
        label = f"{model_id}: {reason}" if reason else str(model_id)
        if stage:
            label = f"{label} ({stage})"
        rows.append(f"<div>{_esc(label)}</div>")
    remaining = max(len(values or []) - limit, 0)
    if remaining:
        rows.append(f"<div class='hint'>+{_esc(remaining)} more</div>")
    return "".join(rows) if rows else "—"


def _format_close_alternatives(values) -> str:
    rows = []
    for item in values or []:
        if not isinstance(item, dict):
            continue
        top1 = item.get("top1_model_id", "")
        top2 = item.get("top2_model_id", "")
        margin = item.get("margin", "")
        state = "fired" if item.get("tiebreaker_fired") else item.get("abort_reason", "")
        rows.append(
            f"<div>{_esc(item.get('candidate_type', ''))}: "
            f"{_esc(top1)} vs {_esc(top2)} "
            f"(margin {_esc(margin)}, {_esc(state)})</div>"
        )
    return "".join(rows) if rows else "—"


def _lane2_candidate_status(candidate: dict, lane2: dict) -> str:
    model_id = candidate.get("model_id", "")
    selected = set(lane2.get("selected_model_ids") or [])
    accepted = {
        item.get("model_id")
        for item in (lane2.get("accepted_before_cap") or [])
        if isinstance(item, dict)
    }
    rejected = [
        item
        for item in (lane2.get("rejected_candidates") or [])
        if isinstance(item, dict) and item.get("model_id") == model_id
    ]
    if model_id in selected:
        return "<span class='tag ok'>selected anchor</span>"
    if model_id in accepted:
        return "<span class='tag ok'>accepted before cap</span>"
    if rejected:
        return _format_rejected_models(rejected, limit=2)
    return "<span class='tag'>candidate only</span>"


def _render_extraction_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    payload, path, error = _load_json_sidecar("extraction.json")

    if error:
        body = (
            "<h1>Extraction</h1>"
            f"{header}"
            + _empty_inline(
                f"Could not parse <code>{_esc(path or 'extraction.json')}</code>: "
                f"{_esc(error)}"
            )
        )
        return _render_scaffold(
            title="Lolla — Extraction",
            body=body,
            current_path="/audit/extraction",
        )

    source_label = "sidecar"
    if not isinstance(payload, dict):
        result_extraction = _RESULT.get("extraction") if isinstance(_RESULT, dict) else None
        if isinstance(result_extraction, dict):
            payload = {
                "status": "from_result",
                "extraction": result_extraction,
                "capture_health": _RESULT.get("capture_health", ""),
                "capture_warnings": _RESULT.get("capture_warnings", []),
            }
            path = _RESULT_PATH
            source_label = "result.json"

    if not isinstance(payload, dict):
        body = (
            "<h1>Extraction</h1>"
            f"{header}"
            + _empty_inline(
                "No <code>extraction.json</code> sidecar was found next to the "
                "served result or in the archived run path recorded by "
                "<code>run_events.json</code>."
            )
        )
        return _render_scaffold(
            title="Lolla — Extraction",
            body=body,
            current_path="/audit/extraction",
        )

    extraction = payload.get("extraction")
    if not isinstance(extraction, dict):
        extraction = payload

    capture_manifest = payload.get("capture_manifest") or {}
    capture_warnings = payload.get("capture_warnings") or []
    quote_validation = extraction.get("_quote_validation") or {}
    live_constraints = extraction.get("live_constraints") or []
    reasoning_passages = extraction.get("reasoning_passages") or []
    dropped_threads = extraction.get("dropped_threads") or []

    constraint_rows = []
    for index, item in enumerate(live_constraints, start=1):
        if isinstance(item, dict):
            constraint = item.get("constraint") or item.get("text") or ""
            introduced_turn = item.get("introduced_turn") or item.get("turn") or ""
            status = item.get("status", "")
            weight = item.get("weight", "")
            canonical_key = item.get("canonical_key", "")
        else:
            constraint = str(item)
            introduced_turn = ""
            status = ""
            weight = ""
            canonical_key = ""
        constraint_rows.append(
            f"<tr><td>{_esc(index)}</td>"
            f"<td>{_esc(constraint)}</td>"
            f"<td>{_esc(introduced_turn)}</td>"
            f"<td>{_esc(status)}</td>"
            f"<td>{_esc(weight)}</td>"
            f"<td><code>{_esc(canonical_key)}</code></td></tr>"
        )

    passage_rows = [
        f"<tr><td>{_esc(index)}</td><td>{_esc(passage)}</td></tr>"
        for index, passage in enumerate(reasoning_passages, start=1)
    ]

    dropped_rows = []
    for index, item in enumerate(dropped_threads, start=1):
        if isinstance(item, dict):
            thread = item.get("thread") or item.get("text") or ""
            raised_by = item.get("raised_by") or item.get("speaker") or ""
            raised_turn = item.get("raised_turn") or item.get("turn") or ""
            status = item.get("status", "")
            superseded_by = item.get("superseded_by", "")
        else:
            thread = str(item)
            raised_by = ""
            raised_turn = ""
            status = ""
            superseded_by = ""
        dropped_rows.append(
            f"<tr><td>{_esc(index)}</td>"
            f"<td>{_esc(thread)}</td>"
            f"<td>{_esc(raised_by)}</td>"
            f"<td>{_esc(raised_turn)}</td>"
            f"<td>{_esc(status)}</td>"
            f"<td>{_esc(superseded_by)}</td></tr>"
        )

    warning_rows = [
        f"<tr><td>{_esc(item)}</td></tr>"
        for item in capture_warnings
    ]

    manifest_rows = [
        f"<tr><td>{_esc(key)}</td><td>{_esc(value)}</td></tr>"
        for key, value in capture_manifest.items()
    ]

    body = f"""
<h1>Extraction</h1>
{header}
<p class="lede">The structured decision snapshot produced before the lanes run. These fields are derived context, not the source of truth; the raw captured conversation remains canonical.</p>
<table>
  <tr><th>Source</th><td><code>{_esc(path or '')}</code> ({_esc(source_label)})</td></tr>
  <tr><th>Status</th><td><span class="tag">{_esc(payload.get("status", ""))}</span></td></tr>
  <tr><th>Strategic</th><td>{_esc(str(bool(extraction.get("is_strategic", True))).lower())}</td></tr>
  <tr><th>Capture health</th><td>{_esc(payload.get("capture_health", ""))}</td></tr>
  <tr><th>Live constraints</th><td>{_esc(len(live_constraints))}</td></tr>
  <tr><th>Reasoning passages</th><td>{_esc(len(reasoning_passages))}</td></tr>
  <tr><th>Dropped threads</th><td>{_esc(len(dropped_threads))}</td></tr>
</table>
<h2>Decision Structure</h2>
<table>
  <tr><th>Decision situation</th><td>{_esc(extraction.get("decision_situation", ""))}</td></tr>
  <tr><th>Original framing</th><td>{_esc(extraction.get("original_framing", ""))}</td></tr>
  <tr><th>Synthesized position</th><td>{_esc(extraction.get("synthesized_position", ""))}</td></tr>
</table>
<h2>Capture Manifest</h2>
<table>
<tr><th>Field</th><th>Value</th></tr>
{"".join(manifest_rows) if manifest_rows else "<tr><td colspan='2' class='empty'>No capture manifest recorded.</td></tr>"}
</table>
<h2>Capture Warnings</h2>
<table>
<tr><th>Warning</th></tr>
{"".join(warning_rows) if warning_rows else "<tr><td class='empty'>No capture warnings recorded.</td></tr>"}
</table>
<h2>Quote Validation</h2>
<table>
  <tr><th>Total</th><td>{_esc(quote_validation.get("total", len(reasoning_passages)))}</td></tr>
  <tr><th>Verified</th><td>{_esc(quote_validation.get("verified", ""))}</td></tr>
  <tr><th>Fabricated</th><td>{_esc(quote_validation.get("fabricated", ""))}</td></tr>
  <tr><th>Retry attempted</th><td>{_esc(str(bool(quote_validation.get("retry_attempted"))).lower())}</td></tr>
  <tr><th>Retry succeeded</th><td>{_esc(str(bool(quote_validation.get("retry_succeeded"))).lower())}</td></tr>
  <tr><th>Fabricated passages</th><td>{_esc(json.dumps(quote_validation.get("fabricated_passages") or [], sort_keys=True))}</td></tr>
</table>
<h2>Live Constraints</h2>
<table>
<tr><th>#</th><th>Constraint</th><th>Turn</th><th>Status</th><th>Weight</th><th>Canonical key</th></tr>
{"".join(constraint_rows) if constraint_rows else "<tr><td colspan='6' class='empty'>No live constraints extracted.</td></tr>"}
</table>
<h2>Reasoning Passages</h2>
<p class="hint">These should be literal assistant substrings. Quote validation records whether any passage was fabricated or dropped.</p>
<table>
<tr><th>#</th><th>Passage</th></tr>
{"".join(passage_rows) if passage_rows else "<tr><td colspan='2' class='empty'>No reasoning passages extracted.</td></tr>"}
</table>
<h2>Dropped Threads</h2>
<table>
<tr><th>#</th><th>Thread</th><th>Raised by</th><th>Turn</th><th>Status</th><th>Superseded by</th></tr>
{"".join(dropped_rows) if dropped_rows else "<tr><td colspan='6' class='empty'>No dropped threads extracted.</td></tr>"}
</table>
"""
    return _render_scaffold(
        title="Lolla — Extraction",
        body=body,
        current_path="/audit/extraction",
    )


def _render_routing_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()
    trace = _route_trace()
    lanes = trace.get("lanes") or {}
    summary = trace.get("summary") or {}

    header = _render_run_header()

    if not audit and not any(int(v or 0) for v in summary.values()):
        body = (
            "<h1>Route trace — why this, why not that</h1>"
            f"{header}"
            + _empty_inline(
                "No route trace or audit summary exists in this result. Re-run "
                "the pipeline to persist routing diagnostics."
            )
        )
        return _render_scaffold(title="Lolla — Route Trace", body=body, current_path="/audit/routing")

    lane1 = lanes.get("lane1") or {}
    lane2 = lanes.get("lane2") or {}
    lane3 = lanes.get("lane3") or {}
    lane4 = lanes.get("lane4") or {}
    anti_echo = trace.get("anti_echo") or {}

    lane1_rows = []
    tiebreakers_fired = 0
    for route in lane1.get("routes") or []:
        close = route.get("close_alternatives") or []
        for alt in close:
            if alt.get("tiebreaker_fired"):
                tiebreakers_fired += 1
        selected = ", ".join(_esc(m) for m in (route.get("selected_model_ids") or []))
        antidotes = _format_model_list(route.get("antidote_model_ids") or [])
        rejected = _format_rejected_models(route.get("rejected_candidates") or [], limit=5)
        close_text = _format_close_alternatives(close)
        lane1_rows.append(
            f"<tr><td>{_esc(route.get('tendency_id', ''))}</td>"
            f"<td>{_esc(route.get('route_source', ''))}</td>"
            f"<td>{_esc(route.get('primary_model_id', ''))}</td>"
            f"<td>{selected or '—'}</td>"
            f"<td>{antidotes}</td>"
            f"<td>{close_text}</td>"
            f"<td>{rejected}</td></tr>"
        )

    lane2_rows = []
    for candidate in lane2.get("candidates") or []:
        lane2_rows.append(
            f"<tr><td>{_esc(candidate.get('model_id', ''))}</td>"
            f"<td>{_esc(candidate.get('recall_source', ''))}</td>"
            f"<td class='num'>{_esc(candidate.get('final_rank', ''))}</td>"
            f"<td>{_lane2_candidate_status(candidate, lane2)}</td></tr>"
        )
    if not lane2_rows:
        for rejected in lane2.get("rejected_candidates") or []:
            lane2_rows.append(
                f"<tr><td>{_esc(rejected.get('model_id', ''))}</td>"
                f"<td>—</td><td class='num'>—</td>"
                f"<td>{_format_rejected_models([rejected], limit=1)}</td></tr>"
            )

    lane3_rows = []
    for route in lane3.get("routes") or []:
        lane3_rows.append(
            f"<tr><td>{_esc(route.get('frame_pattern', ''))}</td>"
            f"<td>{_esc(route.get('element_text', ''))}</td>"
            f"<td>{_format_model_list(route.get('selected_model_ids') or [])}</td>"
            f"<td>{_format_model_list(route.get('candidate_model_ids') or [])}</td>"
            f"<td>{_format_rejected_models(route.get('rejected_candidates') or [], limit=5)}</td></tr>"
        )

    lane4_rows = []
    for route in lane4.get("routes") or []:
        lane4_rows.append(
            f"<tr><td>{_esc(route.get('dimension_id', ''))}</td>"
            f"<td>{_esc(route.get('dimension_name', ''))}</td>"
            f"<td>{_format_model_list(route.get('candidate_model_ids') or [])}</td>"
            f"<td>{_format_rejected_models(route.get('rejected_candidates') or [], limit=5)}</td></tr>"
        )

    recorded_anti_exclusions = anti_echo.get("exclusions") or []
    computed_anti_exclusions = _computed_anti_echo_exclusions()
    displayed_anti_exclusions = recorded_anti_exclusions or computed_anti_exclusions
    anti_rows = []
    for exclusion in displayed_anti_exclusions:
        anti_rows.append(
            f"<tr><td>{_esc(exclusion.get('model_id', ''))}</td>"
            f"<td>{_esc(exclusion.get('excluded_from', ''))}</td>"
            f"<td>{_esc(exclusion.get('reason', ''))}</td>"
            f"<td>{_format_model_list(exclusion.get('source_lanes') or [])}</td></tr>"
        )

    recorded_anti_count = int(summary.get("anti_echo_exclusion_count", 0) or 0)
    computed_anti_count = len(computed_anti_exclusions)
    if recorded_anti_count == computed_anti_count:
        anti_echo_summary = f"<strong>{_esc(recorded_anti_count)}</strong> anti-echo exclusions"
    else:
        anti_echo_summary = (
            f"<strong>{_esc(recorded_anti_count)}</strong> recorded anti-echo exclusions "
            f"(<strong>{_esc(computed_anti_count)}</strong> computed Lane 4 exclusions)"
        )

    lede = (
        f"Route trace version <code>{_esc(trace.get('schema_version', 'fallback'))}</code>: "
        f"<strong>{_esc(summary.get('lane1_route_count', 0))}</strong> Lane 1 routes, "
        f"<strong>{_esc(lane2.get('candidate_count', 0))}</strong> Lane 2 candidates, "
        f"<strong>{_esc(summary.get('lane3_route_count', 0))}</strong> Lane 3 frame routes, "
        f"<strong>{_esc(summary.get('lane4_route_count', 0))}</strong> Lane 4 gap routes, "
        f"and {anti_echo_summary}."
    )

    body = f"""
<h1>Route trace — why this, why not that</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">This page renders recorded route decisions. It does not infer missing reasons; when a lane did not record a reason, the table says so by omission.</p>

<h2>Lane 1 Route — tendency to corrective models</h2>
<p class="hint">Tendency bindings, selected corrective models, close alternatives from the activation tiebreaker, and relation-neighbor candidates dropped by budget, fan-adjusted ordering, or explicit route gates.</p>
<table>
<tr><th>Tendency</th><th>Route source</th><th>Primary model</th><th>Selected models</th><th>Antidotes</th><th>Close alternatives</th><th>Why-not candidates</th></tr>
{"".join(lane1_rows) if lane1_rows else "<tr><td colspan='7' class='empty'>No Lane 1 route trace on this run.</td></tr>"}
</table>

<h2>Lane 2 Route — companion detection and verification</h2>
<p class="hint">Candidates sent to verifier, accepted/rejected/capped outcomes, and silent omissions. Selected anchors: {_format_model_list(lane2.get('selected_model_ids') or [])}.</p>
<table>
<tr><th>Candidate model</th><th>Recall source</th><th class="num">Final rank</th><th>Verification path</th></tr>
{"".join(lane2_rows) if lane2_rows else "<tr><td colspan='4' class='empty'>No Lane 2 candidate trace on this run.</td></tr>"}
</table>

<h2>Lane 3 Route — frame patterns to models</h2>
<p class="hint">Frame elements route through the reframing table. Excluded rows are anti-echo against Lane 1 model overlap; unused candidates are candidates the returned reframing did not ground in.</p>
<table>
<tr><th>Frame pattern</th><th>Element</th><th>Grounding models</th><th>Candidates</th><th>Why-not candidates</th></tr>
{"".join(lane3_rows) if lane3_rows else "<tr><td colspan='5' class='empty'>No Lane 3 frame route trace on this run.</td></tr>"}
</table>

<h2>Lane 4 Route — dimensions to models</h2>
<p class="hint">Structural gaps route to corrective models after anti-echo exclusions from earlier lanes.</p>
<table>
<tr><th>Dimension</th><th>Name</th><th>Candidate models</th><th>Why-not candidates</th></tr>
{"".join(lane4_rows) if lane4_rows else "<tr><td colspan='4' class='empty'>No Lane 4 gap route trace on this run.</td></tr>"}
</table>

<h2>Anti-Echo / Why-Not</h2>
<p class="hint">Cross-lane exclusions. A model listed here was withheld from a later lane because an earlier lane already carried it. When the route trace did not record anti-echo rows, this table falls back to <code>structural_coverage_card.anti_echo_model_ids</code>.</p>
<table>
<tr><th>Model</th><th>Excluded from</th><th>Reason</th><th>Earlier source lanes</th></tr>
{"".join(anti_rows) if anti_rows else "<tr><td colspan='4' class='empty'>No cross-lane anti-echo exclusions recorded for this run.</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Route Trace", body=body, current_path="/audit/routing")


# ---------------- Panel: /audit/treatment-audit ----------------


def _treatment_audit_dir() -> Path:
    return SKILL_DATA_DIR / "treatment_audits"


def _load_treatment_audit_summary() -> dict:
    path = _treatment_audit_dir() / "summary.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_treatment_audit(run_id: str) -> dict:
    safe_run_id = "".join(ch for ch in run_id if ch.isalnum() or ch in {"-", "_"})
    if safe_run_id != run_id:
        return {}
    path = _treatment_audit_dir() / f"{run_id}.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _render_treatment_audit_index_html() -> str:
    summary = _load_treatment_audit_summary()
    if not summary:
        body = (
            "<h1>Model Treatment Audit</h1>"
            + _empty_inline(
                "No treatment-audit summary exists in data/treatment_audits yet. "
                "Run scripts/run_model_treatment_audit.py to generate the Observatory-only prototype."
            )
        )
        return _render_scaffold(
            title="Lolla — Treatment Audit",
            body=body,
            current_path="/audit/treatment-audit",
        )

    rows = []
    for item in summary.get("new_findings") or []:
        rows.append(
            f"<tr><td><a href='/audit/treatment-audit/{_esc(item.get('run_id', ''))}'>{_esc(item.get('run_id', ''))}</a></td>"
            f"<td>{_esc(item.get('model_id', ''))}</td>"
            f"<td>{_esc(item.get('affordance_id', ''))}</td>"
            f"<td>{_esc(item.get('treatment_status', ''))}</td>"
            f"<td>{_esc(item.get('baseline_coverage', ''))}</td>"
            f"<td>{_esc(item.get('one_line_description', ''))}</td></tr>"
        )

    metadata = summary.get("metadata") or {}
    lede = (
        f"<strong>{_esc(summary.get('audited_run_count', 0))}</strong> runs, "
        f"<strong>{_esc(summary.get('audited_item_count', 0))}</strong> affordance audits, "
        f"<strong>{_esc(summary.get('new_finding_count', 0))}</strong> merge-gate candidate findings, "
        f"<strong>{_esc(summary.get('duplicate_of_existing_pressure_count', 0))}</strong> duplicates, "
        f"<strong>{_esc(summary.get('judge_rejection_count', 0))}</strong> judge-response rejections."
    )
    body = f"""
<h1>Model Treatment Audit</h1>
<p class="lede">{lede}</p>
<p class="hint">Judge: {_esc(metadata.get('judge_provider', ''))} / <code>{_esc(metadata.get('judge_model', ''))}</code>. This is Observatory-only; no chat, memo, lane, or runtime promotion is implied.</p>

<h2>Merge-Gate Candidate Findings</h2>
<table>
<tr><th>Run</th><th>Model</th><th>Affordance</th><th>Status</th><th>Baseline</th><th>One-line finding</th></tr>
{"".join(rows) if rows else "<tr><td colspan='6' class='empty'>No non-duplicative treatment-gap candidates in this run set.</td></tr>"}
</table>

<h2>Distributions</h2>
<table>
<tr><th>Bucket</th><th>Counts</th></tr>
<tr><td>Treatment status</td><td>{_esc(summary.get('treatment_status_distribution', {}))}</td></tr>
<tr><td>Baseline coverage</td><td>{_esc(summary.get('baseline_coverage_distribution', {}))}</td></tr>
<tr><td>Per model</td><td>{_esc(summary.get('per_model_audit_counts', {}))}</td></tr>
</table>
"""
    return _render_scaffold(
        title="Lolla — Treatment Audit",
        body=body,
        current_path="/audit/treatment-audit",
    )


def _render_treatment_audit_run_html(run_id: str) -> str:
    audit = _load_treatment_audit(run_id)
    if not audit:
        body = (
            "<h1>Model Treatment Audit</h1>"
            + _empty_inline(f"No treatment audit found for <code>{_esc(run_id)}</code>.")
        )
        return _render_scaffold(
            title="Lolla — Treatment Audit",
            body=body,
            current_path="/audit/treatment-audit",
        )

    metadata = audit.get("metadata") or {}
    rows = []
    for item in audit.get("items") or []:
        flag = (
            "<span class='tag warn'>do-not-promote</span>"
            if item.get("do_not_promote_without_rewrite_review")
            else ""
        )
        merge_candidate = (
            "<span class='tag ok'>merge-gate candidate</span>"
            if item.get("merge_gate_evidence_candidate")
            else ""
        )
        quote = item.get("output_quote") or ""
        rows.append(
            f"<tr><td>{_esc(item.get('model_id', ''))}<br><code>{_esc(item.get('affordance_id', ''))}</code><br>{flag} {merge_candidate}</td>"
            f"<td>{_esc(', '.join(item.get('selected_lanes') or []))}</td>"
            f"<td>{_esc(item.get('treatment_status', ''))}</td>"
            f"<td>{_esc(item.get('baseline_coverage', ''))}</td>"
            f"<td><blockquote class='quote'>{_esc(quote) if quote else '<span class=\"empty\">No quote required for this status.</span>'}</blockquote></td>"
            f"<td>{_esc(item.get('treatment_note', ''))}</td></tr>"
        )

    body = f"""
<h1>Model Treatment Audit — {_esc(audit.get('run_id', ''))}</h1>
<p class="meta">Source run: <code>{_esc(audit.get('source_run_ref', ''))}</code> · Judge: {_esc(metadata.get('judge_provider', ''))} / <code>{_esc(metadata.get('judge_model', ''))}</code> · Tokens: {_esc((metadata.get('token_usage') or {}).get('total_tokens', 0))}</p>
<p><a href="/audit/treatment-audit">Treatment audit summary</a> · <a href="/audit/routing">Route trace for the currently loaded Observatory result</a></p>

<h2>Per-Affordance Treatment</h2>
<table>
<tr><th>Affordance</th><th>Lanes</th><th>Status</th><th>Baseline</th><th>Quote</th><th>Note</th></tr>
{"".join(rows) if rows else "<tr><td colspan='6' class='empty'>No pilot affordances selected in this run.</td></tr>"}
</table>

<h2>Pressure Check Baseline</h2>
<pre>{_esc(audit.get('pressure_check_baseline', ''))}</pre>
"""
    return _render_scaffold(
        title="Lolla — Treatment Audit",
        body=body,
        current_path="/audit/treatment-audit",
    )


# ---------------- Panel: /audit/expansions ----------------


def _render_expansions_html() -> str:
    _reload_result_if_changed()
    expansions = (_RESULT.get("companion_card") or {}).get("expansions") or []

    header = _render_run_header()

    if not expansions:
        body = (
            "<h1>Companion expansions</h1>"
            f"{header}"
            + _empty_inline(
                "No companion expansions on this run — either Lane 2 stayed "
                "quiet or the surfaced anchors had no curated relations to "
                "traverse. See the <a href=\"/audit/lane2\">Lane 2 funnel</a> "
                "for the candidate picture."
            )
        )
        return _render_scaffold(title="Lolla — Expansions", body=body, current_path="/audit/expansions")

    by_anchor: dict[str, list[dict]] = {}
    for e in expansions:
        anchor = e.get("source_model_id") or "(unknown anchor)"
        by_anchor.setdefault(anchor, []).append(e)

    sections = []
    for anchor, entries in by_anchor.items():
        rows = []
        for e in entries:
            rows.append(
                f"<tr><td>{_esc(e.get('model_id', ''))}</td>"
                f"<td><span class='tag'>{_esc(e.get('relation_type', ''))}</span></td>"
                f"<td>{_esc(e.get('activation_condition', ''))}</td>"
                f"<td>{_esc(e.get('affinity_rationale', ''))}</td>"
                f"<td>{_esc(e.get('why_relevant', ''))}</td></tr>"
            )
        sections.append(
            f"<h3>From anchor: <code>{_esc(anchor)}</code> ({len(entries)} expansions)</h3>"
            f"<table><tr><th>Expanded model</th><th>Relation</th>"
            f"<th>Activation condition</th><th>Affinity rationale</th>"
            f"<th>Why relevant</th></tr>{''.join(rows)}</table>"
        )

    lede = (
        f"From <strong>{len(by_anchor)}</strong> anchors, the relation graph "
        f"traversed to <strong>{len(expansions)}</strong> expansions across "
        "allies, antagonists, and tensions."
    )

    body = f"""
<h1>Companion expansions</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">For each Lane 2 anchor, the system walks the curated relation graph one hop out — surfacing allies (mutually-reinforcing models), antagonists (corrective opposites), and tensions (sibling models that pull in different directions).</p>

{"".join(sections)}
"""
    return _render_scaffold(title="Lolla — Expansions", body=body, current_path="/audit/expansions")


def _render_stakeholder_html() -> str:
    """Render the optional Stakeholder Assumption Check panel."""
    _reload_result_if_changed()
    check = _RESULT.get("stakeholder_assumption_check") or {}
    header = _render_run_header()

    if not check or check.get("status") == "skipped":
        body = f"""
<h1>Stakeholder Assumption Check</h1>
{header}
{_empty_inline("No stakeholder assumption check was material for this run.")}
"""
        return _render_scaffold(
            title="Lolla — Stakeholder Assumptions",
            body=body,
            current_path="/audit/stakeholders",
        )

    status = check.get("status", "unknown")
    trigger_reason = check.get("trigger_reason", "")
    summary = check.get("summary", "")
    error = check.get("error", "")
    actors = [a for a in (check.get("critical_actors") or []) if isinstance(a, dict)]

    actor_rows = []
    for actor in actors:
        deps = actor.get("power_or_dependency") or []
        deps_html = " ".join(f'<span class="tag">{_esc(dep)}</span>' for dep in deps)
        surface_in_chat = bool(actor.get("surface_in_chat"))
        surface_label = "yes" if surface_in_chat else "no"
        surface_reason = actor.get("surface_block_reason") or (
            "available to chat" if surface_in_chat else "not selected for chat"
        )
        known = actor.get("known_to_actor") or []
        unknown = actor.get("unknown_to_actor") or []
        bridges = actor.get("bridging_facts") or []
        known_html = "<br>".join(_esc(item) for item in known) or "—"
        unknown_html = "<br>".join(_esc(item) for item in unknown) or "—"
        bridges_html = "<br>".join(_esc(item) for item in bridges) or "—"
        actor_rows.append(
            "<tr>"
            f"<td><strong>{_esc(actor.get('display_name') or actor.get('actor_id') or 'actor')}</strong>"
            f"<br><span class=\"hint\">{_esc(actor.get('role', ''))}</span>"
            f"<div class=\"tagrow\">{deps_html}</div></td>"
            f"<td>{_esc(actor.get('advice_assumption', ''))}</td>"
            f"<td><span class=\"tag\">{_esc(actor.get('grounding', 'unknown'))}</span></td>"
            f"<td><span class=\"tag\">{surface_label}</span><br>"
            f"<span class=\"hint\">{_esc(surface_reason)}</span></td>"
            f"<td>{_esc(actor.get('risk_if_wrong', ''))}</td>"
            f"<td>{_esc(actor.get('plan_change', ''))}</td>"
            "</tr>"
            "<tr>"
            "<td></td>"
            f"<td colspan=\"5\"><details><summary>Known / unknown / bridges</summary>"
            f"<p><strong>Known:</strong><br>{known_html}</p>"
            f"<p><strong>Unknown:</strong><br>{unknown_html}</p>"
            f"<p><strong>Bridging facts:</strong><br>{bridges_html}</p>"
            f"<p><strong>Open question:</strong> {_esc(actor.get('open_question', '—'))}</p>"
            "</details></td>"
            "</tr>"
        )

    if actor_rows:
        table = (
            "<table><thead><tr>"
            "<th>Actor</th><th>Advice assumption</th><th>Grounding</th>"
            "<th>Chat surface</th><th>Risk if wrong</th><th>Plan change</th>"
            "</tr></thead><tbody>"
            + "".join(actor_rows)
            + "</tbody></table>"
        )
    else:
        table = _empty_inline("The check ran but surfaced no actor-level plan change.")

    error_html = (
        f'<div class="empty">Checker error: <code>{_esc(error)}</code></div>'
        if status == "skipped_error" and error
        else ""
    )

    body = f"""
<h1>Stakeholder Assumption Check</h1>
{header}
<p class="lede">This panel shows where the advice depended on another actor's knowledge, cooperation, interpretation, or power. It is inspectable here; user-facing chat only gets a correction when it changes the plan.</p>
<div class="vitals">
  <span class="tag">status: {_esc(status)}</span>
  <span class="tag">surface: {_esc(check.get("surface", False))}</span>
  <span class="tag">triggered: {_esc(check.get("triggered", False))}</span>
</div>
{f'<p><strong>Trigger:</strong> {_esc(trigger_reason)}</p>' if trigger_reason else ''}
{f'<p><strong>Summary:</strong> {_esc(summary)}</p>' if summary else ''}
{error_html}
{table}
"""
    return _render_scaffold(
        title="Lolla — Stakeholder Assumptions",
        body=body,
        current_path="/audit/stakeholders",
    )


# ---------------- Index: /audit ----------------


def _render_audit_run_vitals() -> str:
    """Run-vitals strip for /audit index — at-a-glance pulse of this run.

    Pulls from audit_summary, structural_coverage_card, companion_cheat_sheet,
    and companion_card. Each tag is a single number with a label, in the
    panel order so operators can scan left-to-right and click into whichever
    catches their eye.
    """
    audit = _audit_summary()
    if not audit:
        return ""

    detected_count = sum(
        1 for d in (audit.get("deep_check_results") or []) if d.get("detected")
    )
    candidates_count = len(audit.get("companion_candidates") or [])
    anchors_count = len(
        (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []
    )

    coverage = _RESULT.get("structural_coverage_card") or {}
    gaps_count = sum(
        1
        for d in (coverage.get("dimensions") or [])
        if d.get("dimension_id") and not d.get("covered")
    )
    anti_echo_count = len(coverage.get("anti_echo_model_ids") or [])
    expansions_count = len(
        (_RESULT.get("companion_card") or {}).get("expansions") or []
    )

    chips = [
        f"<strong>{detected_count}</strong> detected",
        f"<strong>{candidates_count}</strong> candidates → "
        f"<strong>{anchors_count}</strong> anchors",
        f"<strong>{gaps_count}</strong> dimension gaps",
        f"<strong>{anti_echo_count}</strong> anti-echo exclusions",
        f"<strong>{expansions_count}</strong> expansions",
    ]
    run_health = _RESULT.get("run_health") or {}
    product_output_health = run_health.get("product_output_health")
    if product_output_health:
        leak_count = run_health.get("product_output_leak_count", 0)
        chips.append(
            f"product output: <strong>{_esc(product_output_health)}</strong>"
            f" ({_fmt_int(leak_count)} leaks)"
        )
    chip_html = "".join(f'<span class="tag">{c}</span>' for c in chips)
    return f'<div class="vitals">{chip_html}</div>'


def _render_run_health_details() -> str:
    """Operator-readable health issue table for the audit index."""
    run_health = _RESULT.get("run_health") or {}
    issue_details = [
        item
        for item in (run_health.get("issue_details") or [])
        if isinstance(item, dict)
    ]
    legacy_issues = [
        str(item)
        for item in (run_health.get("issues") or [])
        if str(item or "").strip()
    ]

    if not issue_details and not legacy_issues:
        return ""

    if issue_details:
        rows = []
        for detail in issue_details:
            code = detail.get("code", "")
            severity = detail.get("severity", "")
            axis = detail.get("axis", "")
            trust_impact = detail.get("trust_impact", "")
            metadata = {
                k: v
                for k, v in detail.items()
                if k not in {"code", "severity", "axis", "trust_impact"}
            }
            rows.append(
                "<tr>"
                f"<td><code>{_esc(code)}</code></td>"
                f"<td>{_esc(severity)}</td>"
                f"<td>{_esc(axis)}</td>"
                f"<td>{_esc(trust_impact)}</td>"
                f"<td><code>{_esc(json.dumps(metadata, sort_keys=True))}</code></td>"
                "</tr>"
            )
        body = "".join(rows)
    else:
        body = "".join(
            "<tr>"
            f"<td><code>{_esc(code)}</code></td>"
            "<td>legacy</td><td>unknown</td>"
            "<td>Older artifact has only raw issue codes.</td><td><code>{}</code></td>"
            "</tr>"
            for code in legacy_issues
        )

    overall = _esc(run_health.get("overall", "unknown"))
    return f"""
<h2>Run Health</h2>
<p class="hint">Overall: <code>{overall}</code>. Severity says how much this affects trust in the run; axis says which part of the process needs inspection.</p>
<table>
<tr><th>Issue</th><th>Severity</th><th>Axis</th><th>Trust impact</th><th>Metadata</th></tr>
{body}
</table>
"""


def _render_v60_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    enrichment = _RESULT.get("v60_enrichment") or {}
    ledger = _RESULT.get("v60_consideration_ledger") or {}
    validation = _RESULT.get("v60_consideration_validation") or {}

    if not enrichment:
        body = (
            "<h1>V60 private enrichment</h1>"
            f"{header}"
            + _empty_inline(
                "This run has no <code>v60_enrichment</code> block. Re-run the "
                "pipeline with V60 enabled to populate selected/skipped chunk telemetry."
            )
        )
        return _render_scaffold(title="Lolla — V60", body=body, current_path="/audit/v60")

    telemetry = enrichment.get("telemetry") or {}
    artifact = enrichment.get("artifact") or {}
    candidate_pool = enrichment.get("candidate_pool") or {}
    selected_cards = enrichment.get("selected_cards") or []
    skipped = telemetry.get("skipped_candidates") or []
    transactions = ledger.get("transactions") or []
    lane_candidates = candidate_pool.get("lane_candidates") or []
    embedding_hits = candidate_pool.get("embedding_model_hits") or []
    selection_source_counts = telemetry.get("selection_source_counts") or {}
    chunk_selection_methods = telemetry.get("selected_chunk_selection_methods") or {}
    chunk_effect_types = telemetry.get("selected_chunk_effect_types") or {}
    chunk_fallback_count = telemetry.get("selected_chunk_record_order_fallback_count", 0)
    lane_source_counts = candidate_pool.get("lane_source_counts") or {}
    disposition_counts = validation.get("disposition_counts") or {}
    validation_errors = validation.get("errors") or []

    card_rows = []
    for card in selected_cards:
        chunks = []
        for chunk in card.get("selected_affordance_cards") or []:
            details = " | ".join(
                part
                for part in [
                    _esc(chunk.get("chunk_id", "")),
                    _esc(chunk.get("confidence", "")),
                    _esc(chunk.get("selection_method", "")),
                    _esc(chunk.get("selection_effect_type", "")),
                    _esc(f"score={chunk.get('selection_score', '')}" if chunk.get("selection_method") else ""),
                    _esc(chunk.get("selection_reason", "")),
                    _esc("; ".join((chunk.get("activation_shape") or {}).get("use_when") or [])),
                ]
                if part
            )
            chunks.append(f"<span class='tag ok'>{details}</span>")
        for chunk in card.get("selected_absence_records") or []:
            details = " | ".join(
                part
                for part in [
                    _esc(chunk.get("chunk_id", "")),
                    _esc(chunk.get("status", "")),
                    _esc(chunk.get("selection_method", "")),
                    _esc(chunk.get("selection_effect_type", "")),
                    _esc(f"score={chunk.get('selection_score', '')}" if chunk.get("selection_method") else ""),
                    _esc(chunk.get("selection_reason", "")),
                    _esc(chunk.get("reason", "")),
                ]
                if part
            )
            chunks.append(f"<span class='tag warn'>{details}</span>")
        card_rows.append(
            f"<tr><td>{_esc(card.get('model_id', ''))}</td>"
            f"<td>{_esc(card.get('selection_source', ''))}</td>"
            f"<td>{_esc(card.get('selection_reason', ''))}</td>"
            f"<td>{_esc(card.get('record_status', ''))}</td>"
            f"<td>{_esc(card.get('source_file', ''))}</td>"
            f"<td><div class='tagrow'>{''.join(chunks)}</div></td></tr>"
        )

    lane_candidate_rows = [
        f"<tr><td>{_esc(item.get('model_id', ''))}</td>"
        f"<td>{_esc(item.get('source', ''))}</td>"
        f"<td>{_esc(item.get('lane_order', ''))}</td>"
        f"<td>{_esc(item.get('reason', ''))}</td>"
        f"<td>{_esc(item.get('evidence', ''))}</td></tr>"
        for item in lane_candidates
    ]

    embedding_rows = [
        f"<tr><td>{_esc(item.get('rank', ''))}</td>"
        f"<td>{_esc(item.get('model_id', ''))}</td>"
        f"<td>{_esc(item.get('score', ''))}</td>"
        f"<td>{_esc(item.get('signal_type', ''))}</td></tr>"
        for item in embedding_hits
    ]

    skipped_rows = [
        f"<tr><td>{_esc(item.get('model_id', ''))}</td>"
        f"<td>{_esc(item.get('source', ''))}</td>"
        f"<td>{_esc(item.get('reason', ''))}</td>"
        f"<td>{_esc(item.get('stage', ''))}</td></tr>"
        for item in skipped
    ]

    tx_rows = [
        f"<tr><td>{_esc(item.get('chunk_id', ''))}</td>"
        f"<td>{_esc(item.get('model_id', ''))}</td>"
        f"<td>{_esc(item.get('disposition', ''))}</td>"
        f"<td>{_esc(item.get('route', ''))}</td>"
        f"<td>{_esc(item.get('strongest_plausible_application', ''))}</td>"
        f"<td>{_esc(item.get('risk_if_forced', ''))}</td>"
        f"<td>{_esc(item.get('why', ''))}</td>"
        f"<td>{_esc(item.get('visible_effect', ''))}</td></tr>"
        for item in transactions
    ]

    selected_count = int(telemetry.get("selected_chunk_count", 0) or 0)
    skipped_count = int(telemetry.get("skipped_candidate_count", 0) or 0)
    not_presented = telemetry.get("not_presented_model_ids") or []
    v60_status = enrichment.get("status", "unknown")
    validation_status = validation.get("status", "not_written" if not ledger else "unknown")

    body = f"""
<h1>V60 private enrichment</h1>
{header}
<p class="lede">Post-lane source-backed consideration material. This is private input for the skill-writing model, not a user-facing card product.</p>

<div class="vitals">
  <span class="tag">status: <strong>{_esc(v60_status)}</strong></span>
  <span class="tag">selected chunks: <strong>{selected_count}</strong></span>
  <span class="tag">skipped candidates: <strong>{skipped_count}</strong></span>
  <span class="tag">ledger: <strong>{_esc(validation_status)}</strong></span>
</div>

<h2>Artifact</h2>
<table>
<tr><th>Artifact</th><th>Status</th><th>Records</th><th>Affordances</th><th>Absences</th><th>SHA-256</th></tr>
<tr><td>{_esc(artifact.get('artifact_id', ''))}</td>
<td>{_esc(artifact.get('status', ''))}</td>
<td class="num">{_fmt_int(artifact.get('model_record_count', 0))}</td>
<td class="num">{_fmt_int(artifact.get('affordance_count', 0))}</td>
<td class="num">{_fmt_int(artifact.get('absence_record_count', 0))}</td>
<td><code>{_esc(str(artifact.get('sha256', ''))[:16])}</code></td></tr>
</table>

<h2>Candidate Pool</h2>
<p class="hint">Lane candidates are high-provenance. Embedding hits are low-trust recall. Hybrid rank is RRF over both.</p>
<div class="vitals">
  <span class="tag">lane candidates: <strong>{_fmt_int(candidate_pool.get('lane_candidate_count', 0))}</strong></span>
  <span class="tag">raw lane signals: <strong>{_fmt_int(candidate_pool.get('raw_lane_signal_count', 0))}</strong></span>
  <span class="tag">embedding mode: <strong>{_esc(candidate_pool.get('embedding_mode', ''))}</strong></span>
</div>
<p class="hint">Selection source counts: {_esc(json.dumps(selection_source_counts, sort_keys=True))}</p>
<p class="hint">Chunk selection methods: {_esc(json.dumps(chunk_selection_methods, sort_keys=True))}; record-order fallbacks: {_fmt_int(chunk_fallback_count)}</p>
<p class="hint">Selected effect types: {_esc(json.dumps(chunk_effect_types, sort_keys=True))}</p>
<p class="hint">Lane source counts: {_esc(json.dumps(lane_source_counts, sort_keys=True))}</p>

<h3>Lane Candidates</h3>
<table>
<tr><th>Model</th><th>Source</th><th>Lane</th><th>Reason</th><th>Evidence</th></tr>
{"".join(lane_candidate_rows) if lane_candidate_rows else "<tr><td colspan='5' class='empty'>No lane candidates recorded.</td></tr>"}
</table>

<h3>Embedding Hits</h3>
<p class="hint">Embedding score is a retrieval/rank signal for recall, not semantic confidence or proof of usefulness.</p>
<table>
<tr><th>Rank</th><th>Model</th><th>Retrieval/rank signal</th><th>Signal</th></tr>
{"".join(embedding_rows) if embedding_rows else "<tr><td colspan='4' class='empty'>No embedding recall hits recorded.</td></tr>"}
</table>

<h2>Selected Cards</h2>
<table>
<tr><th>Model</th><th>Source</th><th>Reason</th><th>Status</th><th>Source file</th><th>Presented chunks</th></tr>
{"".join(card_rows) if card_rows else "<tr><td colspan='6' class='empty'>No V60 cards selected.</td></tr>"}
</table>

<h2>Skipped / Not Presented</h2>
<p class="hint">This is the audit trail for material outside the hot context: duplicates, cap pressure, missing records, and candidates left out.</p>
<p>Not-presented model IDs: {_esc(', '.join(not_presented) if not_presented else 'none')}</p>
<table>
<tr><th>Model</th><th>Source</th><th>Reason</th><th>Stage</th></tr>
{"".join(skipped_rows) if skipped_rows else "<tr><td colspan='4' class='empty'>No skipped candidates recorded.</td></tr>"}
</table>

<h2>Consideration Ledger</h2>
<p class="hint">Written by the skill after Step 6. It answers what was used, rejected, deferred, or presented but not used.</p>
<p class="hint">Disposition counts: {_esc(json.dumps(disposition_counts, sort_keys=True))}</p>
{"<p class='warn'>Validation errors: " + _esc('; '.join(validation_errors)) + "</p>" if validation_errors else ""}
<table>
<tr><th>Chunk</th><th>Model</th><th>Disposition</th><th>Route</th><th>Strongest plausible application</th><th>Risk if forced</th><th>Why</th><th>Visible effect</th></tr>
{"".join(tx_rows) if tx_rows else "<tr><td colspan='8' class='empty'>No V60 consideration ledger written yet.</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — V60", body=body, current_path="/audit/v60")


def _render_pre_step6_shadow_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    private_table = _RESULT.get("pre_step6_private_table") or {}
    private_ledger = _RESULT.get("pre_step6_private_table_ledger") or {}
    shadow = _RESULT.get("pre_step6_shadow_portfolio") or {}

    if private_table:
        source_items = private_table.get("source_items") or []
        ledger_items = private_ledger.get("items") or []
        health = _RESULT.get("run_health") or {}
        validation = _RESULT.get("pre_step6_private_table_ledger_validation") or {}
        cache = private_table.get("cache") or {}
        key_material = private_table.get("key_material") or {}
        sidecars = private_table.get("sidecars") or {}
        gates = private_table.get("gates") or {}
        deterministic_role = private_table.get("deterministic_role") or []

        disposition_counts = (
            health.get("pre_step6_private_table_ledger_disposition_counts")
            or {
                item.get("disposition", ""): sum(
                    1
                    for other in ledger_items
                    if other.get("disposition", "") == item.get("disposition", "")
                )
                for item in ledger_items
                if item.get("disposition", "")
            }
        )
        validation_errors = validation.get("errors") or []
        source_count = health.get(
            "pre_step6_private_table_source_item_count",
            len(source_items),
        )
        ledger_count = health.get(
            "pre_step6_private_table_ledger_item_count",
            len(ledger_items),
        )
        unaccounted_count = health.get(
            "pre_step6_private_table_unaccounted_source_count",
            max(0, len(source_items) - len(ledger_items)),
        )

        role_rows = [
            f"<tr><td>{_esc(index)}</td><td>{_esc(role)}</td></tr>"
            for index, role in enumerate(deterministic_role, start=1)
        ]
        gate_rows = [
            f"<tr><td>{_esc(key)}</td><td>{_esc(value)}</td></tr>"
            for key, value in gates.items()
        ]
        sidecar_rows = [
            f"<tr><td>{_esc(key)}</td><td><code>{_esc(value)}</code></td></tr>"
            for key, value in sidecars.items()
        ]
        source_rows = [
            f"<tr><td><code>{_esc(item.get('source_id', ''))}</code></td>"
            f"<td>{_esc(item.get('source_kind', ''))}</td>"
            f"<td>{_esc(item.get('title', ''))}</td>"
            f"<td>{_esc(item.get('section_id', ''))}</td>"
            f"<td><code>{_esc(item.get('source_atom_id', ''))}</code></td></tr>"
            for item in source_items
        ]
        ledger_rows = [
            f"<tr><td><code>{_esc(item.get('source_id', ''))}</code></td>"
            f"<td>{_esc(item.get('source_kind', ''))}</td>"
            f"<td>{_esc(item.get('title', ''))}</td>"
            f"<td><span class=\"tag\">{_esc(item.get('disposition', ''))}</span></td>"
            f"<td>{_esc(item.get('why', ''))}</td>"
            f"<td>{_esc(item.get('visible_effect', ''))}</td>"
            f"<td>{_esc(item.get('private_guardrail', ''))}</td></tr>"
            for item in ledger_items
        ]

        body = f"""
<h1>Pre-Step-6 Private Table</h1>
{header}
<p class="lede">Current-run private thinking surface used before Step 6. This panel shows which lane and V60 material entered the private table, how the Step 6 ledger accounted for it, and which guardrails kept it out of public product prose.</p>
<p>
  <span class="tag">status: {_esc(private_table.get("status", ""))}</span>
  <span class="tag">ledger: {_esc(private_ledger.get("status", ""))}</span>
  <span class="tag">cache: {_esc(cache.get("state", ""))}</span>
</p>
<table>
  <tr><th>Source items</th><td>{_esc(source_count)}</td></tr>
  <tr><th>Ledger items</th><td>{_esc(ledger_count)}</td></tr>
  <tr><th>Unaccounted sources</th><td>{_esc(unaccounted_count)}</td></tr>
  <tr><th>Table chars</th><td>{_esc(private_table.get("table_char_count", 0))}</td></tr>
  <tr><th>Table sections</th><td>{_esc(private_table.get("table_section_count", 0))}</td></tr>
  <tr><th>Compiled key</th><td><code>{_esc(private_table.get("compiled_card_deck_key", ""))}</code></td></tr>
  <tr><th>V60 selected chunks in key</th><td>{_esc(len(key_material.get("v60_selected_chunk_ids") or []))}</td></tr>
</table>
<h2>Ledger Uptake</h2>
<p class="hint">Disposition counts: {_esc(json.dumps(disposition_counts, sort_keys=True))}</p>
{"<p class='warn'>Validation errors: " + _esc('; '.join(validation_errors)) + "</p>" if validation_errors else ""}
<table>
<tr><th>Source</th><th>Kind</th><th>Title</th><th>Disposition</th><th>Why</th><th>Visible effect</th><th>Private guardrail</th></tr>
{"".join(ledger_rows) if ledger_rows else "<tr><td colspan='7' class='empty'>No pre-Step-6 ledger items written yet.</td></tr>"}
</table>
<h2>Source Items</h2>
<table>
<tr><th>Source</th><th>Kind</th><th>Title</th><th>Section</th><th>Atom</th></tr>
{"".join(source_rows) if source_rows else "<tr><td colspan='5' class='empty'>No private-table source items recorded.</td></tr>"}
</table>
<h2>Cache + Guardrails</h2>
<table>
  <tr><th>Cache resolution</th><td>{_esc(cache.get("resolution", ""))}</td></tr>
  <tr><th>Cache ref</th><td><code>{_esc(cache.get("cache_ref", ""))}</code></td></tr>
  <tr><th>Miss behavior</th><td>{_esc(cache.get("miss_behavior", ""))}</td></tr>
  <tr><th>Live card generation</th><td>{_esc(str(bool(cache.get("live_card_generation_allowed"))).lower())}</td></tr>
  <tr><th>Promotion effect</th><td>{_esc(private_table.get("promotion_effect", ""))}</td></tr>
  {"".join(gate_rows) if gate_rows else "<tr><td colspan='2' class='empty'>No gate records.</td></tr>"}
</table>
<h2>Deterministic Role</h2>
<table>
  <tr><th>#</th><th>Responsibility</th></tr>
  {"".join(role_rows) if role_rows else "<tr><td colspan='2' class='empty'>No deterministic-role records.</td></tr>"}
</table>
<h2>Sidecars</h2>
<table>
  <tr><th>Artifact</th><th>Path</th></tr>
  {"".join(sidecar_rows) if sidecar_rows else "<tr><td colspan='2' class='empty'>No sidecar paths recorded.</td></tr>"}
</table>
"""
        if shadow:
            body += (
                "<h2>Legacy Shadow Portfolio</h2>"
                "<p class=\"hint\">This run also contains the older shadow-policy block. "
                "The private table above is the current runtime accountability surface.</p>"
                f"<table><tr><th>Status</th><td>{_esc(shadow.get('status', ''))}</td></tr>"
                f"<tr><th>Compiled key</th><td><code>{_esc(shadow.get('compiled_card_deck_key', ''))}</code></td></tr></table>"
            )

        return _render_scaffold(
            title="Lolla — Pre-Step-6",
            body=body,
            current_path="/audit/pre-step6",
        )

    if not shadow:
        body = (
            "<h1>Pre-Step-6</h1>"
            f"{header}"
            + _empty_inline(
                "This run has no <code>pre_step6_private_table</code> or "
                "<code>pre_step6_shadow_portfolio</code> block. Re-run the "
                "pipeline with pre-Step-6 private-table capture enabled to "
                "record the current accountability surface."
            )
        )
        return _render_scaffold(
            title="Lolla — Pre-Step-6",
            body=body,
            current_path="/audit/pre-step6",
        )

    cache = shadow.get("cache") or {}
    decision = shadow.get("shadow_visibility_decision") or {}
    gates = shadow.get("gates") or {}
    payload_gate = shadow.get("payload_gate") or {}
    custody = shadow.get("custody_validation") or {}
    cost = shadow.get("cost_envelope") or {}
    deterministic_role = shadow.get("deterministic_role") or []

    role_rows = [
        f"<tr><td>{_esc(index)}</td><td>{_esc(role)}</td></tr>"
        for index, role in enumerate(deterministic_role, start=1)
    ]
    gate_rows = [
        f"<tr><td>{_esc(key)}</td><td>{_esc(value)}</td></tr>"
        for key, value in gates.items()
    ]

    body = f"""
<h1>Pre-Step-6 Shadow Portfolio</h1>
{header}
<p class="lede">Dormant evidence for the proposed portfolio policy. This panel records the cached-card state, Step 6 ledger signal, and guardrails; it does not imply a user-visible answer change.</p>
<h2>Shadow Decision</h2>
<table>
  <tr><th>Status</th><td><span class="tag">{_esc(shadow.get("status", ""))}</span></td></tr>
  <tr><th>Mode</th><td>{_esc(shadow.get("mode", ""))}</td></tr>
  <tr><th>Decision</th><td><strong>{_esc(decision.get("result", ""))}</strong></td></tr>
  <tr><th>Why</th><td>{_esc(decision.get("why", ""))}</td></tr>
  <tr><th>Step 6 ledger signal</th><td>{_esc(shadow.get("step6_ledger_signal", ""))}</td></tr>
  <tr><th>Cognitive signal source</th><td>{_esc(decision.get("cognitive_signal_source", ""))}</td></tr>
  <tr><th>Applied</th><td>applied: {_esc(str(bool(decision.get("applied_to_user_visible_output"))).lower())}</td></tr>
</table>
<h2>Cache + Cost</h2>
<table>
  <tr><th>Compiled key</th><td><code>{_esc(shadow.get("compiled_card_deck_key", ""))}</code></td></tr>
  <tr><th>Cache state</th><td>{_esc(cache.get("state", ""))}</td></tr>
  <tr><th>Cache ref</th><td>{_esc(cache.get("cache_ref", ""))}</td></tr>
  <tr><th>Live generation</th><td>live generation: {_esc(str(bool(cache.get("live_card_generation_allowed"))).lower())}</td></tr>
  <tr><th>Runtime reviewer calls</th><td>{_esc(cost.get("normal_runtime_reviewer_calls", decision.get("normal_runtime_reviewer_calls", 0)))}</td></tr>
  <tr><th>Promotion effect</th><td>{_esc(shadow.get("promotion_effect", ""))}</td></tr>
</table>
<h2>Guardrails</h2>
<table>
  <tr><th>Payload gate</th><td>{_esc(payload_gate.get("status", ""))}</td></tr>
  <tr><th>Custody</th><td>{_esc(custody.get("status", ""))}</td></tr>
  {"".join(gate_rows) if gate_rows else "<tr><td colspan='2' class='empty'>No gate records.</td></tr>"}
</table>
<h2>Deterministic Role</h2>
<table>
  <tr><th>#</th><th>Responsibility</th></tr>
  {"".join(role_rows) if role_rows else "<tr><td colspan='2' class='empty'>No deterministic-role records.</td></tr>"}
</table>
"""
    return _render_scaffold(
        title="Lolla — Pre-Step-6 Shadow",
        body=body,
        current_path="/audit/pre-step6",
    )


def _render_memo_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    memo_text, memo_path, memo_error = _load_text_sidecar("memo.md")
    memo_note, memo_note_path, memo_note_error = _load_json_sidecar("memo_note.json")

    if memo_error:
        body = (
            "<h1>Memo</h1>"
            f"{header}"
            + _empty_inline(
                f"Could not read <code>{_esc(memo_path or 'memo.md')}</code>: "
                f"{_esc(memo_error)}"
            )
        )
        return _render_scaffold(
            title="Lolla — Memo",
            body=body,
            current_path="/audit/memo",
        )

    if memo_text is None:
        body = (
            "<h1>Memo</h1>"
            f"{header}"
            + _empty_inline(
                "No <code>memo.md</code> sidecar was found next to the served "
                "result or in the archived run path recorded by "
                "<code>run_events.json</code>."
            )
        )
        return _render_scaffold(
            title="Lolla — Memo",
            body=body,
            current_path="/audit/memo",
        )

    note_fields = [
        ("memo_substantive_title", "Title"),
        ("memo_orientation_note", "Orientation"),
        ("memo_what_changed", "What changed"),
        ("memo_what_still_holds", "What still holds"),
        ("memo_take_back_or_set_aside", "Take back / set aside"),
        ("memo_pressure_check", "Pressure check"),
    ]
    note_rows = []
    if isinstance(memo_note, dict):
        for key, label in note_fields:
            value = str(memo_note.get(key) or "")
            preview = " ".join(value.split())
            for marker in ("### ", "## ", "# "):
                preview = preview.replace(marker, "")
            status = "present" if value.strip() else "empty"
            note_rows.append(
                f"<tr><td><code>{_esc(key)}</code></td>"
                f"<td>{_esc(label)}</td>"
                f"<td><span class='tag'>{_esc(status)}</span></td>"
                f"<td>{_esc(len(value))}</td>"
                f"<td>{_esc(_short(preview, 180))}</td></tr>"
            )
    elif memo_note_error:
        note_rows.append(
            f"<tr><td colspan='5' class='empty'>Could not parse "
            f"<code>{_esc(memo_note_path or 'memo_note.json')}</code>: "
            f"{_esc(memo_note_error)}</td></tr>"
        )
    else:
        note_rows.append(
            "<tr><td colspan='5' class='empty'>No <code>memo_note.json</code> "
            "sidecar was found for field-level memo diagnostics.</td></tr>"
        )

    note_title = ""
    if isinstance(memo_note, dict):
        note_title = str(memo_note.get("memo_substantive_title") or "")

    body = f"""
<h1>Memo</h1>
{header}
<p class="lede">The shareable decision-note artifact produced by Step 8. The detailed audit trace stays in the telemetry panels; this page shows the product memo that the user can actually read or send onward.</p>
<table>
  <tr><th>Memo source</th><td><code>{_esc(memo_path or '')}</code></td></tr>
  <tr><th>Memo characters</th><td>{_esc(len(memo_text))}</td></tr>
  <tr><th>Memo note source</th><td><code>{_esc(memo_note_path or 'not found')}</code></td></tr>
  <tr><th>Memo note status</th><td>{_esc('present' if isinstance(memo_note, dict) else ('error' if memo_note_error else 'missing'))}</td></tr>
  <tr><th>Memo title</th><td>{_esc(note_title or '—')}</td></tr>
</table>
<h2>Memo Content</h2>
<article class="memo-doc">
{_render_simple_markdown(memo_text)}
</article>
<h2>Memo Field Diagnostics</h2>
<table>
<tr><th>Field</th><th>Meaning</th><th>Status</th><th>Characters</th><th>Preview</th></tr>
{"".join(note_rows)}
</table>
"""
    return _render_scaffold(
        title="Lolla — Memo",
        body=body,
        current_path="/audit/memo",
    )


def _render_run_events_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    payload, path, error = _load_json_sidecar("run_events.json")

    if error:
        body = (
            "<h1>Run Events</h1>"
            f"{header}"
            + _empty_inline(
                f"Could not parse <code>{_esc(path or 'run_events.json')}</code>: "
                f"{_esc(error)}"
            )
        )
        return _render_scaffold(
            title="Lolla — Run Events",
            body=body,
            current_path="/audit/events",
        )

    if not isinstance(payload, dict):
        body = (
            "<h1>Run Events</h1>"
            f"{header}"
            + _empty_inline(
                "No <code>run_events.json</code> sidecar was found next to the "
                "served result. Newer finalized runs record helper lifecycle "
                "events during extraction, pipeline, memo, Observatory launch, "
                "archive, and final receipt."
            )
        )
        return _render_scaffold(
            title="Lolla — Run Events",
            body=body,
            current_path="/audit/events",
        )

    events = payload.get("events") or []
    if not isinstance(events, list):
        events = []

    first_event = events[0] if events and isinstance(events[0], dict) else {}
    last_event = events[-1] if events and isinstance(events[-1], dict) else {}
    event_type_counts: dict[str, int] = {}
    actor_counts: dict[str, int] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("event_type") or event.get("event") or "")
        actor = str(event.get("actor") or "")
        if event_type:
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        if actor:
            actor_counts[actor] = actor_counts.get(actor, 0) + 1

    rows = []
    for event in events:
        if not isinstance(event, dict):
            continue
        details = event.get("details") or {}
        if not isinstance(details, dict):
            details = {"value": details}
        rows.append(
            f"<tr><td>{_esc(event.get('event_id', ''))}</td>"
            f"<td>{_esc(event.get('occurred_at') or event.get('at') or '')}</td>"
            f"<td><code>{_esc(event.get('event_type') or event.get('event') or '')}</code></td>"
            f"<td>{_esc(event.get('actor', ''))}</td>"
            f"<td><code>{_esc(json.dumps(details, sort_keys=True))}</code></td></tr>"
        )

    body = f"""
<h1>Run Events</h1>
{header}
<p class="lede">Lifecycle sidecar for this run. It records helper milestones so operators can verify what happened without reading the raw operator log.</p>
<table>
  <tr><th>Sidecar</th><td><code>{_esc(path or '')}</code></td></tr>
  <tr><th>Run ID</th><td><code>{_esc(payload.get("run_id", ""))}</code></td></tr>
  <tr><th>Schema</th><td>{_esc(payload.get("schema_version", ""))}</td></tr>
  <tr><th>Events</th><td>{_esc(len(events))}</td></tr>
  <tr><th>First event</th><td>{_esc(first_event.get("event_type", ""))} {_esc(first_event.get("occurred_at", ""))}</td></tr>
  <tr><th>Last event</th><td>{_esc(last_event.get("event_type", ""))} {_esc(last_event.get("occurred_at", ""))}</td></tr>
  <tr><th>Event type counts</th><td>{_esc(json.dumps(event_type_counts, sort_keys=True))}</td></tr>
  <tr><th>Actor counts</th><td>{_esc(json.dumps(actor_counts, sort_keys=True))}</td></tr>
</table>
<h2>Timeline</h2>
<table>
<tr><th>ID</th><th>Occurred at</th><th>Event</th><th>Actor</th><th>Details</th></tr>
{"".join(rows) if rows else "<tr><td colspan='5' class='empty'>No run events recorded in this sidecar.</td></tr>"}
</table>
"""
    return _render_scaffold(
        title="Lolla — Run Events",
        body=body,
        current_path="/audit/events",
    )


def _render_reasoning_trace_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    payload, path, error = _load_json_sidecar("reasoning_trace.json")

    if error:
        body = (
            "<h1>Reasoning Trace</h1>"
            f"{header}"
            + _empty_inline(
                f"Could not parse <code>{_esc(path or 'reasoning_trace.json')}</code>: "
                f"{_esc(error)}"
            )
        )
        return _render_scaffold(
            title="Lolla — Reasoning Trace",
            body=body,
            current_path="/audit/reasoning-trace",
        )

    if not isinstance(payload, dict):
        body = (
            "<h1>Reasoning Trace</h1>"
            f"{header}"
            + _empty_inline(
                "No <code>reasoning_trace.json</code> sidecar was found next to "
                "the served result or in the archived run path recorded by "
                "<code>run_events.json</code>."
            )
        )
        return _render_scaffold(
            title="Lolla — Reasoning Trace",
            body=body,
            current_path="/audit/reasoning-trace",
        )

    adequacy = payload.get("trace_adequacy") or {}
    coverage = adequacy.get("coverage") or {}
    commitment_detection = adequacy.get("commitment_detection") or {}
    outcome_review = adequacy.get("outcome_review") or {}
    surface = payload.get("surface_divergence") or {}
    artifacts = payload.get("artifacts") or []
    missing_artifacts = payload.get("missing_artifacts") or []
    model_calls = payload.get("model_calls") or []
    reasoning_lenses = payload.get("reasoning_lenses") or []
    candidate_commitments = payload.get("candidate_commitments") or []

    coverage_rows = [
        f"<tr><td>{_esc(key)}</td><td>{_esc(value)}</td></tr>"
        for key, value in coverage.items()
    ]
    missing_context_rows = [
        f"<tr><td>{_esc(item)}</td></tr>"
        for item in (adequacy.get("missing_context") or [])
    ]
    missing_artifact_rows = [
        f"<tr><td><code>{_esc(item.get('path', ''))}</code></td>"
        f"<td>{_esc(item.get('role', ''))}</td></tr>"
        for item in missing_artifacts
        if isinstance(item, dict)
    ]

    artifact_rows = [
        f"<tr><td>{_esc(item.get('role', ''))}</td>"
        f"<td><code>{_esc(item.get('path', ''))}</code></td>"
        f"<td>{_esc(item.get('bytes', ''))}</td>"
        f"<td>{_esc(item.get('content_type', ''))}</td>"
        f"<td><code>{_esc(_short(item.get('sha256', ''), 32))}</code></td></tr>"
        for item in artifacts
        if isinstance(item, dict)
    ]

    stage_counts: dict[str, int] = {}
    provider_counts: dict[str, int] = {}
    reasoning_leak_count = 0
    call_rows = []
    for call in model_calls:
        if not isinstance(call, dict):
            continue
        stage = str(call.get("stage") or "")
        provider = str(call.get("provider_name") or "")
        if stage:
            stage_counts[stage] = stage_counts.get(stage, 0) + int(call.get("call_count") or 1)
        if provider:
            provider_counts[provider] = provider_counts.get(provider, 0) + int(call.get("call_count") or 1)
        leaked = bool(call.get("reasoning_disabled") and call.get("reasoning_details_present"))
        if leaked:
            reasoning_leak_count += int(call.get("call_count") or 1)
        call_rows.append(
            f"<tr><td>{_esc(call.get('index', ''))}</td>"
            f"<td>{_esc(stage)}</td>"
            f"<td>{_esc(provider)}</td>"
            f"<td><code>{_esc(call.get('model') or call.get('served_model') or call.get('requested_model') or '')}</code></td>"
            f"<td>{_esc(call.get('status', ''))}</td>"
            f"<td>{_esc(call.get('total_tokens', ''))}</td>"
            f"<td>{_esc(str(leaked).lower())}</td></tr>"
        )

    lens_dispositions: dict[str, int] = {}
    selected_lens_count = 0
    surfaced_lens_count = 0
    for lens in reasoning_lenses:
        if not isinstance(lens, dict):
            continue
        if lens.get("selected"):
            selected_lens_count += 1
        if lens.get("surfaced"):
            surfaced_lens_count += 1
        disposition = str(lens.get("disposition") or "")
        if disposition:
            lens_dispositions[disposition] = lens_dispositions.get(disposition, 0) + 1

    commitment_rows = []
    for item in candidate_commitments[:20]:
        if not isinstance(item, dict):
            continue
        commitment_rows.append(
            f"<tr><td>{_esc(item.get('candidate_id', ''))}</td>"
            f"<td>{_esc(item.get('source_actor', ''))}</td>"
            f"<td>{_esc(item.get('kind', ''))}</td>"
            f"<td>{_esc(item.get('impact', ''))}</td>"
            f"<td>{_esc(item.get('evidence_status', ''))}</td>"
            f"<td>{_esc(item.get('correction_status', ''))}</td>"
            f"<td>{_esc(_short(item.get('claim', ''), 220))}</td></tr>"
        )

    body = f"""
<h1>Reasoning Trace</h1>
{header}
<p class="lede">Archive-side custody and adequacy summary. This panel does not duplicate the raw conversation; it tells you whether the trace is complete enough for future review and where to look when it is thin.</p>
<table>
  <tr><th>Sidecar</th><td><code>{_esc(path or '')}</code></td></tr>
  <tr><th>Trace ID</th><td><code>{_esc(payload.get("trace_id", ""))}</code></td></tr>
  <tr><th>Schema</th><td>{_esc(payload.get("schema_version", ""))}</td></tr>
  <tr><th>Created</th><td>{_esc(payload.get("created_at", ""))}</td></tr>
  <tr><th>Adequacy status</th><td><span class="tag">{_esc(adequacy.get("status", ""))}</span></td></tr>
  <tr><th>Future review ready</th><td>{_esc(str(bool(adequacy.get("future_review_ready"))).lower())}</td></tr>
  <tr><th>Error analysis ready</th><td>{_esc(str(bool(adequacy.get("error_analysis_ready"))).lower())}</td></tr>
  <tr><th>Surface divergence</th><td>{_esc(surface.get("status", ""))}</td></tr>
  <tr><th>Artifacts</th><td>{_esc(len(artifacts))}</td></tr>
  <tr><th>Model-call telemetry rows</th><td>{_esc(len(model_calls))}</td></tr>
  <tr><th>Reasoning-boundary leaks</th><td>{_esc(reasoning_leak_count)}</td></tr>
</table>
<h2>Trace Adequacy</h2>
<table>
  <tr><th>Coverage item</th><th>Status</th></tr>
  {"".join(coverage_rows) if coverage_rows else "<tr><td colspan='2' class='empty'>No coverage records.</td></tr>"}
</table>
<p class="hint">Commitment detection: {_esc(json.dumps(commitment_detection, sort_keys=True))}</p>
<p class="hint">Outcome review: {_esc(json.dumps(outcome_review, sort_keys=True))}</p>
<table>
  <tr><th>Missing context</th></tr>
  {"".join(missing_context_rows) if missing_context_rows else "<tr><td class='empty'>No missing context recorded.</td></tr>"}
</table>
<h2>Missing Artifacts</h2>
<table>
<tr><th>Path</th><th>Role</th></tr>
{"".join(missing_artifact_rows) if missing_artifact_rows else "<tr><td colspan='2' class='empty'>No missing artifacts recorded.</td></tr>"}
</table>
<h2>Surface Divergence</h2>
<table>
  <tr><th>Revised artifact present</th><td>{_esc(str(bool(surface.get("revised_artifact_present"))).lower())}</td></tr>
  <tr><th>Live transcript present</th><td>{_esc(str(bool(surface.get("live_transcript_present"))).lower())}</td></tr>
  <tr><th>Result revised answer present</th><td>{_esc(str(bool(surface.get("result_revised_answer_present"))).lower())}</td></tr>
  <tr><th>Revised artifact matches result</th><td>{_esc(str(bool(surface.get("revised_artifact_matches_result"))).lower())}</td></tr>
  <tr><th>Revised artifact found in live transcript</th><td>{_esc(str(bool(surface.get("revised_artifact_found_in_live_transcript"))).lower())}</td></tr>
  <tr><th>Source refs</th><td>{_esc(json.dumps(surface.get("source_refs") or {}, sort_keys=True))}</td></tr>
</table>
<h2>Artifacts</h2>
<table>
<tr><th>Role</th><th>Path</th><th>Bytes</th><th>Type</th><th>SHA-256</th></tr>
{"".join(artifact_rows) if artifact_rows else "<tr><td colspan='5' class='empty'>No artifact custody records.</td></tr>"}
</table>
<h2>Model-Call Telemetry</h2>
<p class="hint">Rows may summarize multiple raw provider calls. Use the stage/provider counts here, or <a href="/usage">/usage</a>, for raw call totals.</p>
<p class="hint">Stage counts: {_esc(json.dumps(stage_counts, sort_keys=True))}</p>
<p class="hint">Provider counts: {_esc(json.dumps(provider_counts, sort_keys=True))}</p>
<table>
<tr><th>#</th><th>Stage</th><th>Provider</th><th>Model</th><th>Status</th><th>Total tokens</th><th>Reasoning leak</th></tr>
{"".join(call_rows) if call_rows else "<tr><td colspan='7' class='empty'>No model-call records.</td></tr>"}
</table>
<h2>Reasoning Lenses</h2>
<table>
  <tr><th>Total</th><td>{_esc(len(reasoning_lenses))}</td></tr>
  <tr><th>Selected</th><td>{_esc(selected_lens_count)}</td></tr>
  <tr><th>Surfaced</th><td>{_esc(surfaced_lens_count)}</td></tr>
  <tr><th>Dispositions</th><td>{_esc(json.dumps(lens_dispositions, sort_keys=True))}</td></tr>
</table>
<h2>Commitment Candidates</h2>
<table>
<tr><th>ID</th><th>Actor</th><th>Kind</th><th>Impact</th><th>Evidence</th><th>Correction</th><th>Claim</th></tr>
{"".join(commitment_rows) if commitment_rows else "<tr><td colspan='7' class='empty'>No commitment candidates recorded.</td></tr>"}
</table>
"""
    return _render_scaffold(
        title="Lolla — Reasoning Trace",
        body=body,
        current_path="/audit/reasoning-trace",
    )


def _render_graph_survival_html() -> str:
    _reload_result_if_changed()
    header = _render_run_header()
    payload, path, error = _load_json_sidecar("graph_survival_report.json")

    if error:
        body = (
            "<h1>Graph Survival</h1>"
            f"{header}"
            + _empty_inline(
                f"Could not parse <code>{_esc(path or 'graph_survival_report.json')}</code>: "
                f"{_esc(error)}"
            )
        )
        return _render_scaffold(
            title="Lolla — Graph Survival",
            body=body,
            current_path="/audit/graph-survival",
        )

    if not isinstance(payload, dict):
        body = (
            "<h1>Graph Survival</h1>"
            f"{header}"
            + _empty_inline(
                "No <code>graph_survival_report.json</code> sidecar was found "
                "next to the served result or in the archived run path recorded "
                "by <code>run_events.json</code>."
            )
        )
        return _render_scaffold(
            title="Lolla — Graph Survival",
            body=body,
            current_path="/audit/graph-survival",
        )

    summary = payload.get("summary") or {}
    source_refs = payload.get("source_refs") or {}
    noise_policy = payload.get("noise_policy") or {}
    embedding_selection = payload.get("embedding_selection") or {}
    v60_ledger_summary = payload.get("v60_ledger_summary") or {}
    candidate_survival = payload.get("candidate_survival") or []
    suppressed_signals = payload.get("suppressed_signals") or []
    private_table_survival = payload.get("private_table_survival") or []
    embedding_hits = embedding_selection.get("hits") or []

    def _list_lines(values, *, limit: int = 3, width: int = 160) -> str:
        if not isinstance(values, list) or not values:
            return "—"
        rendered = [
            _esc(_short(value, width))
            for value in values[:limit]
        ]
        if len(values) > limit:
            rendered.append(_esc(f"+{len(values) - limit} more"))
        return "<br>".join(rendered)

    candidate_rows = []
    for item in candidate_survival:
        if not isinstance(item, dict):
            continue
        candidate_rows.append(
            f"<tr><td><strong>{_esc(item.get('display_name') or item.get('model_id') or '')}</strong><br>"
            f"<code>{_esc(item.get('model_id', ''))}</code></td>"
            f"<td><span class='tag'>{_esc(item.get('survival_state', ''))}</span></td>"
            f"<td>{_esc(str(bool(item.get('selected_for_v60'))).lower())}</td>"
            f"<td>{_esc(item.get('selection_source', ''))}</td>"
            f"<td>{_esc(item.get('embedding_rank') if item.get('embedding_rank') is not None else '—')} / "
            f"{_esc(_fmt_score(item.get('embedding_score')))}</td>"
            f"<td>{_esc(item.get('selected_chunk_count', 0))}</td>"
            f"<td>{_esc(json.dumps(item.get('pre_step6_disposition_counts') or {}, sort_keys=True))}</td>"
            f"<td>{_esc(json.dumps(item.get('v60_disposition_counts') or {}, sort_keys=True))}</td>"
            f"<td>{_list_lines(item.get('visible_effects') or [], limit=2)}</td>"
            f"<td>{_list_lines(item.get('private_guardrails') or [], limit=2)}</td>"
            f"<td>{_esc(', '.join(item.get('skipped_reasons') or []) or '—')}</td></tr>"
        )

    suppressed_rows = []
    for item in suppressed_signals:
        if not isinstance(item, dict):
            continue
        suppressed_rows.append(
            f"<tr><td><code>{_esc(item.get('model_id', ''))}</code></td>"
            f"<td>{_esc(item.get('research_status', ''))}</td>"
            f"<td>{_esc(item.get('reason', ''))}</td>"
            f"<td>{_esc(item.get('source', ''))}</td>"
            f"<td>{_esc(item.get('stage', ''))}</td>"
            f"<td>{_esc(_fmt_score(item.get('score')))}</td>"
            f"<td>{_esc(str(bool(item.get('unknown_noise_status'))).lower())}</td></tr>"
        )

    private_rows = []
    for item in private_table_survival:
        if not isinstance(item, dict):
            continue
        private_rows.append(
            f"<tr><td><code>{_esc(item.get('source_id', ''))}</code></td>"
            f"<td>{_esc(item.get('source_kind', ''))}</td>"
            f"<td>{_esc(item.get('title', ''))}</td>"
            f"<td><span class='tag'>{_esc(item.get('disposition', ''))}</span></td>"
            f"<td>{_esc(_short(item.get('why', ''), 220))}</td>"
            f"<td>{_esc(_short(item.get('visible_effect', ''), 220))}</td>"
            f"<td>{_esc(_short(item.get('private_guardrail', ''), 220))}</td></tr>"
        )

    embedding_rows = []
    for item in embedding_hits:
        if not isinstance(item, dict):
            continue
        embedding_rows.append(
            f"<tr><td>{_esc(item.get('embedding_rank', ''))}</td>"
            f"<td><code>{_esc(item.get('model_id', ''))}</code></td>"
            f"<td>{_esc(_fmt_score(item.get('score')))}</td>"
            f"<td>{_esc(str(bool(item.get('selected_for_v60'))).lower())}</td>"
            f"<td>{_esc(item.get('selection_source', '') or '—')}</td>"
            f"<td>{_esc(item.get('research_status', ''))}</td>"
            f"<td>{_esc(json.dumps(item.get('ledger_disposition_counts') or {}, sort_keys=True))}</td>"
            f"<td>{_esc(', '.join(item.get('skipped_reasons') or []) or '—')}</td></tr>"
        )

    selected_model_ids = summary.get("selected_model_ids") or []
    selected_models = ", ".join(selected_model_ids) if isinstance(selected_model_ids, list) else ""

    body = f"""
<h1>Graph Survival</h1>
{header}
<p class="lede">Archive-side survival accounting: which graph, lane, and embedding candidates reached the private reasoning context, which changed the answer, which became private guardrails, and which were preserved as budget-suppressed signals for later review.</p>
<table>
  <tr><th>Sidecar</th><td><code>{_esc(path or '')}</code></td></tr>
  <tr><th>Schema</th><td>{_esc(payload.get("schema_version", ""))}</td></tr>
  <tr><th>Status</th><td><span class="tag">{_esc(payload.get("status", ""))}</span></td></tr>
  <tr><th>Candidate survival records</th><td>{_esc(summary.get("candidate_survival_count", len(candidate_survival)))}</td></tr>
  <tr><th>Selected cards / chunks</th><td>{_esc(summary.get("selected_card_count", 0))} / {_esc(summary.get("selected_chunk_count", 0))}</td></tr>
  <tr><th>Answer-delta models</th><td>{_esc(summary.get("answer_delta_model_count", 0))}</td></tr>
  <tr><th>Private-guardrail models</th><td>{_esc(summary.get("private_guardrail_model_count", 0))}</td></tr>
  <tr><th>Suppressed models / signals</th><td>{_esc(summary.get("suppressed_model_count", 0))} / {_esc(summary.get("suppressed_signal_count", 0))}</td></tr>
  <tr><th>Unadjudicated candidates</th><td>{_esc(summary.get("unadjudicated_candidate_count", 0))}</td></tr>
  <tr><th>Embedding mode / hits</th><td>{_esc(summary.get("embedding_mode", ""))} / {_esc(summary.get("embedding_hit_count", 0))}</td></tr>
  <tr><th>Selected models</th><td>{_esc(selected_models)}</td></tr>
</table>
<h2>Noise Policy</h2>
<table>
  <tr><th>Unselected does not mean noise</th><td>{_esc(str(bool(noise_policy.get("unselected_does_not_mean_noise"))).lower())}</td></tr>
  <tr><th>Unknown noise status</th><td>{_esc(str(bool(noise_policy.get("unknown_noise_status"))).lower())}</td></tr>
  <tr><th>Reason</th><td>{_esc(noise_policy.get("reason", ""))}</td></tr>
  <tr><th>Source refs</th><td>{_esc(json.dumps(source_refs, sort_keys=True))}</td></tr>
</table>
<h2>Candidate Survival</h2>
<p class="hint">Rows come from the archive report. <em>Answer delta</em> means the model visibly changed the revised answer; <em>private guardrail</em> means it constrained the answer without becoming visible product prose.</p>
<table>
<tr><th>Model</th><th>State</th><th>Selected</th><th>Source</th><th>Rank / score</th><th>Chunks</th><th>Pre-Step6</th><th>V60</th><th>Visible effects</th><th>Private guardrails</th><th>Skipped</th></tr>
{"".join(candidate_rows) if candidate_rows else "<tr><td colspan='11' class='empty'>No candidate survival records.</td></tr>"}
</table>
<h2>Suppressed Signals</h2>
<p class="hint">These candidates were preserved because budget suppression is not the same as proof of irrelevance.</p>
<table>
<tr><th>Model</th><th>Research status</th><th>Reason</th><th>Source</th><th>Stage</th><th>Score</th><th>Unknown noise</th></tr>
{"".join(suppressed_rows) if suppressed_rows else "<tr><td colspan='7' class='empty'>No suppressed signals recorded.</td></tr>"}
</table>
<h2>Private Table Survival</h2>
<table>
<tr><th>Source</th><th>Kind</th><th>Title</th><th>Disposition</th><th>Why</th><th>Visible effect</th><th>Private guardrail</th></tr>
{"".join(private_rows) if private_rows else "<tr><td colspan='7' class='empty'>No private-table survival records.</td></tr>"}
</table>
<h2>Embedding Selection</h2>
<p class="hint">Embedding score is a retrieval/rank signal for recall, not proof of semantic truth or usefulness.</p>
<table>
<tr><th>Rank</th><th>Model</th><th>Score</th><th>Selected</th><th>Selection source</th><th>Research status</th><th>Ledger disposition</th><th>Skipped</th></tr>
{"".join(embedding_rows) if embedding_rows else "<tr><td colspan='8' class='empty'>No embedding hits recorded.</td></tr>"}
</table>
<h2>V60 Ledger Summary</h2>
<table>
  <tr><th>Transaction count</th><td>{_esc(v60_ledger_summary.get("transaction_count", 0))}</td></tr>
  <tr><th>Disposition counts</th><td>{_esc(json.dumps(v60_ledger_summary.get("disposition_counts") or {}, sort_keys=True))}</td></tr>
  <tr><th>Route counts</th><td>{_esc(json.dumps(v60_ledger_summary.get("route_counts") or {}, sort_keys=True))}</td></tr>
</table>
"""
    return _render_scaffold(
        title="Lolla — Graph Survival",
        body=body,
        current_path="/audit/graph-survival",
    )


def _render_audit_index_html() -> str:
    _reload_result_if_changed()
    audit_present = bool(_audit_summary())
    items = [
        ("/audit/extraction", "Extraction",
         "Structured pre-lane decision snapshot: capture health, quote validation, decision situation, constraints, reasoning passages, framing, and dropped threads."),
        ("/audit/memo", "Memo",
         "The shareable decision-note artifact produced by Step 8, with memo_note field diagnostics and archive-source path."),
        ("/audit/lane1", "Lane 1 — Pass 1 + Pass 2 funnel",
         "Triage scores across the catalog, the threshold, the triggered set with source attribution, and Pass 2 outcomes with rationale."),
        ("/audit/lane2", "Lane 2 — Companion selection funnel",
         "Candidate pool → accepted-before-cap → final cheat-sheet anchors, with verifier accepts/rejects/capped/duplicates/quote-repairs/silently-omitted bucket views."),
        ("/audit/lane4", "Lane 4 — Dimension coverage",
         "Every catalog dimension marked covered / gap / not-detected, with gap routes (corrective models) and gap questions."),
        ("/audit/anti-echo", "Anti-echo cascade",
         "Models held back from Lane 4 because an upstream lane already surfaced them. Lane-of-origin attribution computed at render time."),
        ("/audit/routing", "Routing decisions",
         "For each detected tendency: primary lens, antidotes, and the activation-tiebreaker trace (fired, or which clause kept top-1)."),
        ("/audit/treatment-audit", "Model treatment audit",
         "Observatory-only affordance treatment checks: did selected models change the output, or merely get named?"),
        ("/audit/expansions", "Companion expansions",
         "Relation-graph traversal per Lane 2 anchor — allies, antagonists, and tensions, with activation conditions and why-relevant rationale."),
        ("/audit/stakeholders", "Stakeholder assumption check",
         "When enabled: actor dependencies, grounding tiers, known/unknown splits, and any plan-changing correction."),
        ("/audit/v60", "V60 private enrichment",
         "Post-lane source-backed affordance and absence chunks: selected, skipped, not presented, and consideration-ledger uptake."),
        ("/audit/pre-step6", "Pre-Step-6 private table",
         "Current-run private-table source items, Step 6 ledger uptake, cache/custody guardrails, and legacy shadow-policy evidence when present."),
        ("/audit/graph-survival", "Graph survival",
         "Archive-side survival accounting for selected, answer-changing, private-guardrail, suppressed, and unadjudicated graph/embedding candidates."),
        ("/audit/reasoning-trace", "Reasoning trace",
         "Archive-side trace adequacy, missing artifacts/context, surface-divergence checks, artifact custody, model calls, lenses, and commitment candidates."),
        ("/audit/events", "Run events",
         "Single-run lifecycle timeline from the run_events sidecar: extraction, pipeline, ledger finalization, memo rendering, Observatory launch, archive, and receipt."),
    ]
    cards = []
    for href, title, desc in items:
        cards.append(
            f'<li><a href="{_esc(href)}"><strong>{_esc(title)}</strong></a><br>'
            f'<span style="color:#555">{_esc(desc)}</span></li>'
        )
    header = _render_run_header()
    vitals = _render_audit_run_vitals() if audit_present else ""
    health_details = _render_run_health_details()

    if not audit_present:
        notice = (
            '<div class="empty">This result has no <code>audit_summary</code> '
            "block — likely a pre-Phase-7 artifact. Panels render their "
            "empty states; re-run the pipeline to populate the trace.</div>"
        )
    else:
        notice = ""
    body = f"""
<h1>Telemetry — how the system reasoned</h1>
{header}
<p class="lede">A separate lens on the same case. Each panel below shows what the system observed, considered, and surfaced — the reasoning trace behind the answer at <a href="/">/</a>.</p>
{vitals}
{health_details}
{notice}
<ul style="list-style:none;padding:0;">
{"".join(f'<div style="margin-bottom:1.5rem">{c}</div>' for c in cards)}
</ul>
"""
    return _render_scaffold(title="Lolla — Telemetry", body=body, current_path="/audit")


class ResultHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Pass STATIC_DIR even if it doesn't exist — SimpleHTTPRequestHandler
        # accepts a non-existent directory string. The /audit/* and /usage
        # routes do not depend on the SPA bundle being present (skill
        # portability — see PR 3 of the 2026-04-28 visibility roadmap); only
        # the SPA fallback path checks ``STATIC_DIR.is_dir()`` before serving.
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            _reload_result_if_changed()

        if path == "/api/cases":
            self._json_response(_build_cases_index())
            return

        if path.startswith("/api/case/"):
            parts = path.split("/")
            case_id = unquote(parts[3]) if len(parts) >= 4 else ""
            result, result_path, is_current = _load_case_result(case_id)
            if result is None:
                self._error_response(
                    404,
                    f"Case '{case_id}' not found"
                    + (f" at {result_path}" if result_path else ""),
                )
                return
            if len(parts) == 4:
                self._json_response(
                    _build_case_response(
                        result,
                        case_id=case_id,
                        result_path=result_path,
                    )
                )
                return
            if len(parts) == 5 and parts[4] == "audit_trace":
                self._json_response(result.get("audit_summary") or {})
                return
            if len(parts) == 5 and parts[4] == "graph":
                self._json_response(_build_graph_response(result))
                return
            if len(parts) == 5 and parts[4] == "usage":
                self._json_response(result.get("usage_summary") or {})
                return
            if len(parts) == 5 and parts[4] == "agent-result":
                self._json_sidecar_response(
                    result_path,
                    "agent_result.json",
                    is_current=is_current,
                )
                return
            if len(parts) == 5 and parts[4] == "reasoning-trace":
                self._json_sidecar_response(
                    result_path,
                    "reasoning_trace.json",
                    is_current=is_current,
                )
                return
            if len(parts) == 5 and parts[4] == "events":
                self._json_sidecar_response(
                    result_path,
                    "run_events.json",
                    is_current=is_current,
                )
                return
            if len(parts) == 5 and parts[4] == "memo":
                self._memo_sidecar_response(result_path, is_current=is_current)
                return
            if len(parts) == 5 and parts[4] == "graph-survival":
                self._graph_survival_sidecar_response(
                    result_path,
                    is_current=is_current,
                )
                return

        if path == "/usage":
            self._html_response(_render_usage_html())
            return

        # Audit panels — server-rendered HTML, no SPA dependency.
        _audit_routes = {
            "/audit": _render_audit_index_html,
            "/audit/extraction": _render_extraction_html,
            "/audit/memo": _render_memo_html,
            "/audit/lane1": _render_lane1_html,
            "/audit/lane2": _render_lane2_html,
            "/audit/lane4": _render_lane4_html,
            "/audit/anti-echo": _render_anti_echo_html,
            "/audit/routing": _render_routing_html,
            "/audit/treatment-audit": _render_treatment_audit_index_html,
            "/audit/expansions": _render_expansions_html,
            "/audit/stakeholders": _render_stakeholder_html,
            "/audit/v60": _render_v60_html,
            "/audit/pre-step6": _render_pre_step6_shadow_html,
            "/audit/graph-survival": _render_graph_survival_html,
            "/audit/reasoning-trace": _render_reasoning_trace_html,
            "/audit/events": _render_run_events_html,
        }
        if path in _audit_routes:
            self._html_response(_audit_routes[path]())
            return

        if path.startswith("/audit/treatment-audit/"):
            run_id = path.rsplit("/", 1)[-1]
            self._html_response(_render_treatment_audit_run_html(run_id))
            return

        if path.startswith("/api/model/"):
            model_id = path.split("/")[3] if len(path.split("/")) >= 4 else ""
            data = _get_model_detail(model_id)
            if data is None:
                self._error_response(404, f"Model '{model_id}' not found")
                return
            self._json_response(data)
            return

        if path == "/api/kg/stats":
            self._json_response(_get_kg_stats())
            return

        if path == "/api/tendencies":
            self._json_response(_get_tendency_catalog())
            return

        if path == "/api/families":
            self._json_response(_load_families())
            return

        if path.startswith("/api/family/"):
            parts = path.split("/")
            if len(parts) >= 4:
                fid = parts[3]
                data = _get_family_detail(fid)
                if data is None:
                    self._error_response(404, f"Family '{fid}' not found")
                    return
                self._json_response(data)
                return

        # SPA root — inject the Telemetry FAB before serving index.html.
        # This is the only bridge from the case/product surface (/) to the
        # system-reasoning surface (/audit). Done as a byte-stream injection
        # so the SPA bundle on disk stays untouched and the skill remains
        # rebuildable-free.
        if path in ("/", "/index.html") and STATIC_DIR.is_dir():
            index_path = STATIC_DIR / "index.html"
            if index_path.is_file():
                try:
                    injected = _inject_telemetry_fab(index_path.read_bytes())
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(injected)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(injected)
                    return
                except OSError:
                    pass  # fall through to default handler below

        # Static files / SPA fallback
        if STATIC_DIR.is_dir():
            file_path = STATIC_DIR / path.lstrip("/")
            if not file_path.exists() and not path.startswith("/api/"):
                self.path = "/index.html"
            super().do_GET()
        else:
            self._error_response(503, "Observatory frontend not built.")

    def _html_response(self, body_str: str, status: int = 200):
        body = body_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, data, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _error_response(self, status: int, message: str):
        self._json_response({"error": message}, status=status)

    def _json_sidecar_response(
        self,
        result_path: Path | None,
        filename: str,
        *,
        is_current: bool,
    ):
        path = _case_sidecar_path(result_path, filename, is_current=is_current)
        if path is None:
            self._error_response(404, f"Sidecar '{filename}' not found for selected case")
            return
        payload = _load_json_safe(path)
        if payload is None:
            self._error_response(500, f"Sidecar '{filename}' could not be parsed as JSON")
            return
        self._json_response(payload)

    def _memo_sidecar_response(self, result_path: Path | None, *, is_current: bool):
        path = _case_sidecar_path(result_path, "memo.md", is_current=is_current)
        if path is None:
            self._error_response(404, "Sidecar 'memo.md' not found for selected case")
            return
        try:
            markdown = path.read_text(encoding="utf-8")
        except OSError as exc:
            self._error_response(500, f"Sidecar 'memo.md' could not be read: {exc}")
            return
        self._json_response(
            {
                "artifact": _artifact_metadata(path, content_type="text/markdown"),
                "markdown": markdown,
            }
        )

    def _graph_survival_sidecar_response(
        self,
        result_path: Path | None,
        *,
        is_current: bool,
    ):
        json_path = _case_sidecar_path(
            result_path,
            "graph_survival_report.json",
            is_current=is_current,
        )
        if json_path is None:
            self._error_response(
                404,
                "Sidecar 'graph_survival_report.json' not found for selected case",
            )
            return
        report = _load_json_safe(json_path)
        if report is None:
            self._error_response(
                500,
                "Sidecar 'graph_survival_report.json' could not be parsed as JSON",
            )
            return

        markdown_payload = None
        markdown_path = _case_sidecar_path(
            result_path,
            "graph_survival_report.md",
            is_current=is_current,
        )
        if markdown_path is not None:
            try:
                markdown_payload = {
                    "artifact": _artifact_metadata(
                        markdown_path,
                        content_type="text/markdown",
                    ),
                    "markdown": markdown_path.read_text(encoding="utf-8"),
                }
            except OSError:
                markdown_payload = None

        self._json_response(
            {
                "artifact": _artifact_metadata(
                    json_path,
                    content_type="application/json",
                ),
                "report": report,
                "markdown": markdown_payload,
            }
        )

    def log_message(self, format, *args):
        msg = format % args
        if "/api/" in msg or "404" in msg or "500" in msg:
            sys.stderr.write(f"[lolla] {msg}\n")


def main():
    parser = argparse.ArgumentParser(description="Serve Lolla result in Observatory")
    parser.add_argument("--result", required=True, help="Path to pipeline result JSON")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--name", help="Display name for the case (auto-derived from query if omitted)")
    args = parser.parse_args()

    global _RESULT, _RESULT_PATH, _RESULT_MTIME, _CASE_NAME
    result_path = Path(args.result)
    if not result_path.exists():
        print(f"Error: result file not found: {result_path}", file=sys.stderr)
        sys.exit(1)

    _RESULT_PATH = result_path
    with open(result_path) as f:
        _RESULT = json.load(f)
    _RESULT_MTIME = result_path.stat().st_mtime

    _CASE_NAME = args.name if args.name else _derive_case_name(_RESULT)

    # SPA bundle is optional (skill portability): /audit/* and /usage are
    # server-rendered HTML and work without it. Only warn when the bundle is
    # absent so the operator knows the React app at /  won't render.
    if not STATIC_DIR.is_dir():
        print(
            f"Note: Observatory SPA bundle not found at {STATIC_DIR} — "
            "the React app at / will be unavailable, but /audit/* and /usage "
            "panels still work.",
            file=sys.stderr,
        )

    # Try ports starting from the requested one
    port = args.port
    server = None
    for attempt in range(10):
        try:
            server = HTTPServer((_OBSERVATORY_HOST, port), ResultHandler)
            break
        except OSError:
            print(f"Port {port} in use, trying {port + 1}...")
            port += 1

    if server is None:
        print(f"Error: could not find an open port (tried {args.port}-{port})", file=sys.stderr)
        sys.exit(1)

    print(f"Lolla Observatory at http://localhost:{port}")
    print(f"  Case:  {_CASE_NAME}")
    print(f"  Usage: http://localhost:{port}/usage  (per-run cost & call breakdown)")
    print(f"  Result: {result_path}")
    print(f"  Knowledge graph: {SKILL_DATA_DIR / 'knowledge_graph.json'}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
