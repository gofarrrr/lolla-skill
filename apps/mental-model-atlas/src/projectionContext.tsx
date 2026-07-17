import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  type AtlasProjection,
  type FixtureId,
  fixtureFromQuery,
  loadProjection,
} from "./projection";
import {
  buildNeighborhoodProjection,
  loadNavigationIndex,
} from "./navigation";
import { useLocation } from "./router";

type ProjectionState =
  | { status: "loading"; fixtureId: FixtureId; retry: () => void }
  | {
      status: "ready";
      fixtureId: FixtureId;
      projection: AtlasProjection;
      retry: () => void;
    }
  | { status: "failed"; fixtureId: FixtureId; message: string; retry: () => void };

const ProjectionContext = createContext<ProjectionState | null>(null);
const projectionCache = new Map<string, AtlasProjection>();

export function ProjectionProvider({ children }: { children: ReactNode }) {
  const location = useLocation();
  const fixtureId = fixtureFromQuery(location.searchParams.get("fixture"));
  const selectedModelId =
    fixtureId === "ordinary-navigation"
      ? clean(location.searchParams.get("model"))
      : null;
  const parsedPage = Number(location.searchParams.get("page") ?? "1");
  const pageNumber =
    (fixtureId === "confirmation-bias-hub" || selectedModelId) &&
    Number.isInteger(parsedPage) &&
    parsedPage > 0
      ? parsedPage
      : 1;
  const cacheKey = selectedModelId
    ? `canonical-neighborhood:${selectedModelId}:${pageNumber}`
    : `${fixtureId}:${pageNumber}`;
  const [attempt, setAttempt] = useState(0);
  const cached = projectionCache.get(cacheKey);
  const [state, setState] = useState<ProjectionState>(() =>
    cached
      ? { status: "ready", fixtureId, projection: cached, retry }
      : { status: "loading", fixtureId, retry },
  );

  function retry(): void {
    projectionCache.delete(cacheKey);
    setAttempt((value) => value + 1);
  }

  useEffect(() => {
    const cachedProjection = projectionCache.get(cacheKey);
    if (cachedProjection) {
      setState({
        status: "ready",
        fixtureId,
        projection: cachedProjection,
        retry,
      });
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setState({ status: "loading", fixtureId, retry });
    const projectionPromise = selectedModelId
      ? loadNavigationIndex().then((index) =>
          buildNeighborhoodProjection(index, selectedModelId, pageNumber),
        )
      : loadProjection(fixtureId, pageNumber, controller.signal);
    void projectionPromise
      .then((projection) => {
        if (!active) {
          return;
        }
        projectionCache.set(cacheKey, projection);
        setState({ status: "ready", fixtureId, projection, retry });
      })
      .catch((error: unknown) => {
        if (!active || controller.signal.aborted) {
          return;
        }
        setState({
          status: "failed",
          fixtureId,
          message:
            error instanceof Error ? error.message : "Atlas projection failed to load",
          retry,
        });
      });
    return () => {
      active = false;
      controller.abort();
    };
    // The retry function intentionally closes over the current fixture.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cacheKey, fixtureId, pageNumber, selectedModelId, attempt]);

  const value = useMemo(() => state, [state]);
  return (
    <ProjectionContext.Provider value={value}>
      {children}
    </ProjectionContext.Provider>
  );
}

function clean(value: string | null): string | null {
  const normalized = value?.trim();
  return normalized ? normalized : null;
}

export function useProjection(): ProjectionState {
  const state = useContext(ProjectionContext);
  if (!state) {
    throw new Error("useProjection must be used inside ProjectionProvider");
  }
  return state;
}
