import { useMemo } from "react";

import {
  curveGeometry,
  GRAPH_VIEWBOX,
  GRAPH_WIDTH,
  positionModels,
  positionRelations,
} from "./graphGeometry";
import type { GraphRendererProps } from "./graphTypes";

export default function SvgGraphSurface(props: GraphRendererProps) {
  const models = useMemo(() => positionModels(props.projection), [props.projection]);
  const visibleModels = useMemo(
    () => models.filter(({ model }) => props.visibleModelIds.has(model.model_id)),
    [models, props.visibleModelIds],
  );
  const relations = useMemo(
    () => positionRelations(visibleModels, props.relations),
    [visibleModels, props.relations],
  );
  const hasSelection = Boolean(props.selectedModelId || props.selectedRelationId);
  const selectedModel = visibleModels.find(
    ({ model }) => model.model_id === props.selectedModelId,
  );
  const selectedRelation = relations.find(
    ({ relation }) => relation.relation_id === props.selectedRelationId,
  );
  const cameraX =
    selectedModel?.x ??
    (selectedRelation
      ? (selectedRelation.source.x + selectedRelation.target.x) / 2
      : GRAPH_WIDTH / 2);
  const cameraY =
    selectedModel?.y ??
    (selectedRelation
      ? (selectedRelation.source.y + selectedRelation.target.y) / 2
      : 350);
  const cameraScale = hasSelection ? 1.055 : 1;
  const cameraTransform = `translate(${cameraX}px, ${cameraY}px) scale(${cameraScale}) translate(${-cameraX}px, ${-cameraY}px)`;

  return (
    <svg
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
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" className={`marker marker-${type}`} />
          </marker>
        ))}
      </defs>

      <g className="graph-camera" style={{ transform: cameraTransform }}>
        <g className="graph-edges" aria-label="Focused directed relations">
          {relations.map((positioned) => {
            const { relation, source, target } = positioned;
            const curve = curveGeometry(positioned);
            const selected = relation.relation_id === props.selectedRelationId;
            const path = `M ${source.x.toFixed(2)} ${source.y.toFixed(2)} Q ${curve.controlX.toFixed(2)} ${curve.controlY.toFixed(2)} ${target.x.toFixed(2)} ${target.y.toFixed(2)}`;
            return (
              <g
                key={relation.relation_id}
                className={`graph-edge edge-${relation.relation_type}${selected ? " is-selected" : ""}`}
                data-relation-id={relation.relation_id}
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
            const anchorAtEnd = x > GRAPH_WIDTH - 180;
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
                <circle className="node-aura" r={selected ? 28 : 19} />
                <circle className="node-core" r={selected ? 8 : hovered ? 7 : 5} />
                <text
                  className="node-label"
                  x={anchorAtEnd ? -13 : 13}
                  y="4"
                  textAnchor={anchorAtEnd ? "end" : "start"}
                >
                  {model.display_name}
                </text>
              </g>
            );
          })}
        </g>
      </g>
    </svg>
  );
}
