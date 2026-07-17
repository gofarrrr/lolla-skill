import { useEffect, useMemo, useRef } from "react";

import {
  curveGeometry,
  GRAPH_VIEWBOX,
  positionModelLabels,
  positionModels,
  positionRelations,
} from "./graphGeometry";
import type { GraphRendererProps } from "./graphTypes";

export default function SvgGraphSurface(props: GraphRendererProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const models = useMemo(() => positionModels(props.projection), [props.projection]);
  const visibleModels = useMemo(
    () => models.filter(({ model }) => props.visibleModelIds.has(model.model_id)),
    [models, props.visibleModelIds],
  );
  const relations = useMemo(
    () => positionRelations(visibleModels, props.relations),
    [visibleModels, props.relations],
  );
  const labels = useMemo(() => positionModelLabels(visibleModels), [visibleModels]);
  const hasSelection = Boolean(props.selectedModelId || props.selectedRelationId);
  const cameraTransform = "translate(0px, 0px) scale(1)";

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    if (props.motionPaused) {
      svg.pauseAnimations?.();
    } else {
      svg.unpauseAnimations?.();
    }
  }, [props.motionPaused, relations]);

  return (
    <svg
      ref={svgRef}
      className="atlas-graph atlas-graph-svg"
      viewBox={GRAPH_VIEWBOX}
      role="group"
      aria-labelledby="graph-title graph-description"
      data-renderer="svg"
      data-projection-id={props.projection.projection_id}
      data-coordinate-sha256={props.projection.layout.coordinate_sha256}
      data-camera-transform={cameraTransform}
    >
      <title id="graph-title">Mental model neighborhood</title>
      <desc id="graph-description">
        A navigational rendering of frozen model coordinates. Use the synchronized
        model list and directed relation table below for complete keyboard access.
      </desc>
      <defs>
        <filter id="node-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="8" />
        </filter>
        {(["ally", "antagonist", "tension"] as const).map((type) => (
          <marker
            key={type}
            id={`arrow-${type}`}
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            markerUnits="userSpaceOnUse"
            orient="auto-start-reverse"
          >
            <path
              d="M 0 0 L 10 5 L 0 10 z"
              className={`graph-marker marker-${type}`}
            />
          </marker>
        ))}
      </defs>

      <g className="graph-camera" style={{ transform: cameraTransform }}>
        <g className="graph-edges" aria-label="Focused directed relations">
          {relations.map((positioned, index) => {
            const { relation, source, target } = positioned;
            const curve = curveGeometry(positioned);
            const selected = relation.relation_id === props.selectedRelationId;
            const path = trimmedRelationPath(positioned);
            const angle =
              (Math.atan2(target.y - source.y, target.x - source.x) * 180) /
              Math.PI;
            return (
              <g
                key={relation.relation_id}
                className={`graph-edge edge-${relation.relation_type}${selected ? " is-selected" : ""}`}
                data-relation-id={relation.relation_id}
                data-relation={relation.relation_type}
                role="button"
                tabIndex={0}
                aria-pressed={selected}
                aria-label={`${relation.source_model_id} to ${relation.target_model_id}, ${relation.relation_type} relation`}
                onClick={() => props.onSelectRelation(relation.relation_id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    props.onSelectRelation(relation.relation_id);
                  }
                }}
              >
                <path className="edge-hitbox" d={path} />
                <path
                  className="edge-line"
                  d={path}
                  markerEnd={`url(#arrow-${relation.relation_type})`}
                />
                {relation.relation_type === "tension" ? (
                  <path className="edge-line edge-line-tension-inner" d={path} />
                ) : null}
                {relation.relation_type === "antagonist" ? (
                  <g
                    className="edge-antagonist-cross"
                    transform={`translate(${curve.midpointX.toFixed(2)} ${curve.midpointY.toFixed(2)}) rotate(${angle.toFixed(2)})`}
                    aria-hidden="true"
                  >
                    <line x1="-4" y1="-4" x2="4" y2="4" />
                    <line x1="-4" y1="4" x2="4" y2="-4" />
                  </g>
                ) : null}
                <circle
                  className="edge-flow-marker"
                  r="3.25"
                  aria-hidden="true"
                >
                  <animateMotion
                    dur={`${(3.1 + (index % 4) * 0.35).toFixed(2)}s`}
                    begin={`-${(index % 5) * 0.55}s`}
                    repeatCount="indefinite"
                    path={path}
                  />
                </circle>
              </g>
            );
          })}
        </g>

        <g className="graph-nodes" aria-label="Models">
          {visibleModels.map(({ model, x, y }) => {
            const selected = model.model_id === props.selectedModelId;
            const hovered = model.model_id === props.hoveredModelId;
            const unrelated =
              hasSelection && !props.relatedModelIds.has(model.model_id);
            const label = labels.get(model.model_id);
            return (
              <g
                key={model.model_id}
                className={`graph-node${selected ? " is-selected" : ""}${hovered ? " is-hovered" : ""}${unrelated ? " is-dimmed" : ""}`}
                data-model-id={model.model_id}
                transform={`translate(${x.toFixed(2)} ${y.toFixed(2)})`}
                role="button"
                tabIndex={0}
                aria-pressed={selected}
                aria-label={`Select ${model.display_name}`}
                onClick={() => props.onSelectModel(model.model_id)}
                onPointerEnter={() => props.onHoverModel(model.model_id)}
                onPointerLeave={() => props.onHoverModel(null)}
                onFocus={() => props.onHoverModel(model.model_id)}
                onBlur={() => props.onHoverModel(null)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    props.onSelectModel(model.model_id);
                  }
                }}
              >
                <circle className="graph-node-aura" r={selected ? 13 : 10} />
                <circle
                  className="graph-node-core"
                  r={selected ? 5 : hovered ? 4.25 : 3.25}
                />
                {label ? (
                  <>
                    <line
                      className="graph-node-leader"
                      x1="0"
                      y1="0"
                      x2={(label.x + label.width / 2 - x).toFixed(2)}
                      y2={(label.y + label.height / 2 - y).toFixed(2)}
                    />
                    <g
                      className="graph-node-label"
                      transform={`translate(${(label.x - x).toFixed(2)} ${(label.y - y).toFixed(2)})`}
                    >
                      <rect width={label.width.toFixed(2)} height={label.height} />
                      <text x="8" y="16">
                        {model.display_name}
                      </text>
                    </g>
                  </>
                ) : null}
              </g>
            );
          })}
        </g>
      </g>
    </svg>
  );
}

function trimmedRelationPath({ source, target, ...positioned }: Parameters<typeof curveGeometry>[0]): string {
  const distance = Math.max(1, Math.hypot(target.x - source.x, target.y - source.y));
  const unitX = (target.x - source.x) / distance;
  const unitY = (target.y - source.y) / distance;
  const startX = source.x + unitX * 12;
  const startY = source.y + unitY * 12;
  const endX = target.x - unitX * 17;
  const endY = target.y - unitY * 17;
  const curve = curveGeometry({ source, target, ...positioned });
  return `M ${startX.toFixed(2)} ${startY.toFixed(2)} Q ${curve.controlX.toFixed(2)} ${curve.controlY.toFixed(2)} ${endX.toFixed(2)} ${endY.toFixed(2)}`;
}
