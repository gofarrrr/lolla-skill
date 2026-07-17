import {
  Component,
  lazy,
  type ReactNode,
  Suspense,
} from "react";

import type { GraphRendererProps } from "./graphTypes";

const SvgGraphSurface = lazy(() => import("./SvgGraphSurface"));
const CanvasGraphSurface = lazy(() => import("./CanvasGraphSurface"));

export type RendererKind = "svg" | "canvas";

interface GraphSurfaceProps extends GraphRendererProps {
  renderer: RendererKind;
  fallback: ReactNode;
}

class RendererBoundary extends Component<
  { children: ReactNode; fallback: ReactNode; resetKey: string },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidUpdate(previous: { resetKey: string }): void {
    if (previous.resetKey !== this.props.resetKey && this.state.failed) {
      this.setState({ failed: false });
    }
  }

  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

export function GraphSurface({ renderer, fallback, ...props }: GraphSurfaceProps) {
  const Surface = renderer === "canvas" ? CanvasGraphSurface : SvgGraphSurface;
  return (
    <RendererBoundary
      fallback={fallback}
      resetKey={`${renderer}:${props.projection.projection_id}`}
    >
      <Suspense
        fallback={
          <div className="graph-loading" aria-live="polite">
            Preparing {renderer === "canvas" ? "Canvas 2D" : "SVG"} renderer…
          </div>
        }
      >
        <Surface {...props} />
      </Suspense>
    </RendererBoundary>
  );
}
