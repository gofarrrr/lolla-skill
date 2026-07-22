import {
  Component,
  lazy,
  type ReactNode,
  Suspense,
  useState,
} from "react";

import { AppLink, parseRoute, useLocation } from "./router";
import { ProjectionProvider } from "./projectionContext";
import { useReducedMotionPreference } from "./useReducedMotion";

const AtlasPage = lazy(() => import("./routes/AtlasPage"));
const LibraryPage = lazy(() => import("./routes/LibraryPage"));
const ModelPage = lazy(() => import("./routes/ModelPage"));
const RelationPage = lazy(() => import("./routes/RelationPage"));
const LearnPage = lazy(() => import("./routes/LearnPage"));

interface RenderFailureBoundaryState {
  failed: boolean;
}

class RenderFailureBoundary extends Component<
  { children: ReactNode; resetKey: string },
  RenderFailureBoundaryState
> {
  state: RenderFailureBoundaryState = { failed: false };

  static getDerivedStateFromError(): RenderFailureBoundaryState {
    return { failed: true };
  }

  componentDidUpdate(previous: { resetKey: string }): void {
    if (previous.resetKey !== this.props.resetKey && this.state.failed) {
      this.setState({ failed: false });
    }
  }

  render() {
    if (this.state.failed) {
      return (
        <main id="main" className="failure-page" tabIndex={-1}>
          <p className="eyebrow">Rendering failed</p>
          <h1>The Atlas view could not be drawn.</h1>
          <p>
            This is a rendering failure, not an empty result. The source projection
            has not been reclassified or repaired.
          </p>
          <div className="button-row">
            <button type="button" onClick={() => window.location.reload()}>
              Reload this view
            </button>
            <AppLink className="button secondary" href="/models">
              Use the model library
            </AppLink>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}

export function App() {
  const location = useLocation();
  const route = parseRoute(location.pathname);
  const prefersReducedMotion = useReducedMotionPreference();
  const [motionPaused, setMotionPaused] = useState(false);
  const effectiveMotionPaused = prefersReducedMotion || motionPaused;
  const motionControlLabel = prefersReducedMotion
    ? "Motion paused by system preference"
    : motionPaused
      ? "Resume motion"
      : "Pause motion";
  const motionControlVisibleLabel = prefersReducedMotion
    ? "Motion paused"
    : motionControlLabel;

  return (
    <div
      className="app-shell"
      data-route-kind={route.kind}
      data-reduced-motion={effectiveMotionPaused ? "true" : "false"}
    >
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <AppLink className="brand" href="/atlas" aria-label="Lolla Atlas home">
          <span className="brand-wordmark" aria-hidden="true">
            <img
              src="/brand/lolla-wordmark-original.png"
              alt=""
              width="2172"
              height="724"
              decoding="async"
              fetchPriority="high"
            />
          </span>
        </AppLink>
        <nav aria-label="Primary navigation">
          <AppLink href="/atlas" aria-current={route.kind === "atlas" ? "page" : undefined}>
            Atlas
          </AppLink>
          <AppLink
            href="/models"
            aria-current={
              route.kind === "models" || route.kind === "model" ? "page" : undefined
            }
          >
            Library
          </AppLink>
        </nav>
        {route.kind === "atlas" ? (
          <button
            className="motion-control"
            type="button"
            aria-label={motionControlLabel}
            onClick={() => setMotionPaused((value) => !value)}
            disabled={prefersReducedMotion}
            title={
              prefersReducedMotion
                ? "Motion is reduced by your system preference"
                : undefined
            }
          >
            <span
              className="motion-icon"
              data-motion-state={effectiveMotionPaused ? "paused" : "running"}
              aria-hidden="true"
            />
            <span className="motion-label">{motionControlVisibleLabel}</span>
          </button>
        ) : <span className="header-balance" aria-hidden="true" />}
      </header>

      <RenderFailureBoundary resetKey={`${location.pathname}${location.search}`}>
        <Suspense fallback={<RouteLoading />}>
          {route.kind === "atlas" ? (
            <ProjectionProvider>
              <AtlasPage motionPaused={effectiveMotionPaused} />
            </ProjectionProvider>
          ) : null}
          {route.kind === "models" ? (
            <ProjectionProvider>
              <LibraryPage />
            </ProjectionProvider>
          ) : null}
          {route.kind === "model" ? <ModelPage slug={route.slug} /> : null}
          {route.kind === "relation" ? (
            <RelationPage relationId={route.relationId} />
          ) : null}
          {route.kind === "learn" ? <LearnPage /> : null}
          {route.kind === "journey" ? <LearnPage journeyId={route.journeyId} /> : null}
          {route.kind === "not-found" ? <NotFoundPage /> : null}
        </Suspense>
      </RenderFailureBoundary>
    </div>
  );
}

function RouteLoading() {
  return (
    <div className="route-loading" role="status" aria-live="polite" aria-busy="true">
      <span className="loading-orbit" aria-hidden="true" />
      <p>Opening the Atlas…</p>
    </div>
  );
}

function NotFoundPage() {
  return (
    <main id="main" className="failure-page">
      <p className="eyebrow">Route not found</p>
      <h1>This path is outside the Atlas.</h1>
      <p>No model or relation identity was repaired from the unknown URL.</p>
      <AppLink className="button" href="/atlas">
        Return to the Atlas
      </AppLink>
    </main>
  );
}
