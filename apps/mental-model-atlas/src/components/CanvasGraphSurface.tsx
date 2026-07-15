import { useEffect, useMemo, useRef } from "react";

import {
  curveGeometry,
  GRAPH_HEIGHT,
  GRAPH_WIDTH,
  positionModels,
  positionRelations,
} from "./graphGeometry";
import type { GraphRendererProps, PositionedModel, PositionedRelation } from "./graphTypes";

const COLORS = {
  ally: "#71d6ae",
  antagonist: "#ff7f76",
  tension: "#d7a6ff",
} as const;

export default function CanvasGraphSurface(props: GraphRendererProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const models = useMemo(() => positionModels(props.projection), [props.projection]);
  const visibleModels = useMemo(
    () => models.filter(({ model }) => props.visibleModelIds.has(model.model_id)),
    [models, props.visibleModelIds],
  );
  const relations = useMemo(
    () => positionRelations(visibleModels, props.relations),
    [visibleModels, props.relations],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return undefined;
    }
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("Canvas 2D is unavailable");
    }
    const resize = () => {
      const bounds = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.round(bounds.width * ratio));
      canvas.height = Math.max(1, Math.round(bounds.height * ratio));
      context.setTransform(
        (canvas.width / GRAPH_WIDTH),
        0,
        0,
        (canvas.height / GRAPH_HEIGHT),
        0,
        0,
      );
      draw(context, visibleModels, relations, props);
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [visibleModels, relations, props]);

  function eventPoint(
    event:
      | React.PointerEvent<HTMLCanvasElement>
      | React.MouseEvent<HTMLCanvasElement>,
  ) {
    const bounds = event.currentTarget.getBoundingClientRect();
    const screenPoint = {
      x: ((event.clientX - bounds.left) / bounds.width) * GRAPH_WIDTH,
      y: ((event.clientY - bounds.top) / bounds.height) * GRAPH_HEIGHT,
    };
    const camera = cameraFor(models, relations, props);
    return {
      x: camera.x + (screenPoint.x - camera.targetX) / camera.scale,
      y: camera.y + (screenPoint.y - camera.targetY) / camera.scale,
    };
  }

  return (
    <canvas
      ref={canvasRef}
      className="atlas-graph atlas-graph-canvas"
      role="img"
      aria-label="Canvas 2D comparison rendering of the same frozen Atlas projection. Use the synchronized model list and directed relation table for keyboard access."
      data-renderer="canvas"
      data-projection-id={props.projection.projection_id}
      data-coordinate-sha256={props.projection.layout.coordinate_sha256}
      data-camera-transform={JSON.stringify(cameraFor(models, relations, props))}
      onPointerMove={(event) => {
        const point = eventPoint(event);
        const model = nearestModel(visibleModels, point.x, point.y, 18);
        props.onHoverModel(model?.model.model_id ?? null);
      }}
      onPointerLeave={() => props.onHoverModel(null)}
      onClick={(event) => {
        const point = eventPoint(event);
        const model = nearestModel(visibleModels, point.x, point.y, 22);
        if (model) {
          props.onSelectModel(model.model.model_id);
          return;
        }
        const relation = nearestRelation(relations, point.x, point.y, 20);
        if (relation) {
          props.onSelectRelation(relation.relation.relation_id);
        }
      }}
    />
  );
}

function draw(
  context: CanvasRenderingContext2D,
  models: PositionedModel[],
  relations: PositionedRelation[],
  props: GraphRendererProps,
): void {
  context.clearRect(0, 0, GRAPH_WIDTH, GRAPH_HEIGHT);
  context.save();
  context.lineCap = "round";
  const camera = cameraFor(models, relations, props);
  if (camera.scale !== 1) {
    context.translate(camera.targetX, camera.targetY);
    context.scale(camera.scale, camera.scale);
    context.translate(-camera.x, -camera.y);
  }
  for (const positioned of relations) {
    const { relation, source, target } = positioned;
    const curve = curveGeometry(positioned);
    context.beginPath();
    context.moveTo(source.x, source.y);
    context.quadraticCurveTo(curve.controlX, curve.controlY, target.x, target.y);
    context.strokeStyle = COLORS[relation.relation_type];
    context.globalAlpha = relation.relation_id === props.selectedRelationId ? 1 : 0.68;
    context.lineWidth = relation.relation_id === props.selectedRelationId ? 3 : 1.5;
    context.setLineDash(
      relation.relation_type === "antagonist"
        ? [8, 5]
        : relation.relation_type === "tension"
          ? [2, 5]
          : [],
    );
    context.stroke();
    drawArrow(context, curve.midpointX, curve.midpointY, target.x, target.y, COLORS[relation.relation_type]);
  }
  context.setLineDash([]);
  const hasSelection = Boolean(props.selectedModelId || props.selectedRelationId);
  for (const positioned of models) {
    const { model, x, y } = positioned;
    const selected = model.model_id === props.selectedModelId;
    const hovered = model.model_id === props.hoveredModelId;
    const dimmed = hasSelection && !props.relatedModelIds.has(model.model_id);
    context.globalAlpha = dimmed ? 0.2 : 1;
    context.beginPath();
    context.arc(x, y, selected ? 9 : hovered ? 8 : 6, 0, Math.PI * 2);
    context.fillStyle = selected ? "#f4d792" : hovered ? "#ffffff" : "#bdc4d3";
    context.fill();
    if (!dimmed || selected || hovered) {
      context.font = selected ? "600 15px system-ui" : "500 12px system-ui";
      context.fillStyle = selected || hovered ? "#ffffff" : "#a9b0bf";
      const anchorAtEnd = x > GRAPH_WIDTH - 180;
      context.textAlign = anchorAtEnd ? "right" : "left";
      context.fillText(model.display_name, x + (anchorAtEnd ? -13 : 13), y + 4);
    }
  }
  context.globalAlpha = 1;
  context.restore();
}

function cameraFor(
  models: PositionedModel[],
  relations: PositionedRelation[],
  props: GraphRendererProps,
): { x: number; y: number; targetX: number; targetY: number; scale: number } {
  const selectedModel = models.find(
    ({ model }) => model.model_id === props.selectedModelId,
  );
  const selectedRelation = relations.find(
    ({ relation }) => relation.relation_id === props.selectedRelationId,
  );
  return {
    x:
      selectedModel?.x ??
      ((selectedRelation?.source.x ?? GRAPH_WIDTH / 2) +
        (selectedRelation?.target.x ?? GRAPH_WIDTH / 2)) /
        2,
    y:
      selectedModel?.y ??
      ((selectedRelation?.source.y ?? GRAPH_HEIGHT / 2) +
        (selectedRelation?.target.y ?? GRAPH_HEIGHT / 2)) /
        2,
    targetX: GRAPH_WIDTH / 2,
    targetY: GRAPH_HEIGHT / 2,
    scale: selectedModel || selectedRelation ? 1.055 : 1,
  };
}

function drawArrow(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  targetX: number,
  targetY: number,
  color: string,
): void {
  const angle = Math.atan2(targetY - y, targetX - x);
  context.save();
  context.translate(x, y);
  context.rotate(angle);
  context.beginPath();
  context.moveTo(7, 0);
  context.lineTo(-5, -4);
  context.lineTo(-5, 4);
  context.closePath();
  context.fillStyle = color;
  context.fill();
  context.restore();
}

function nearestModel(
  models: PositionedModel[],
  x: number,
  y: number,
  radius: number,
): PositionedModel | null {
  let nearest: PositionedModel | null = null;
  let distance = radius;
  for (const model of models) {
    const next = Math.hypot(model.x - x, model.y - y);
    if (next <= distance) {
      nearest = model;
      distance = next;
    }
  }
  return nearest;
}

function nearestRelation(
  relations: PositionedRelation[],
  x: number,
  y: number,
  radius: number,
): PositionedRelation | null {
  let nearest: PositionedRelation | null = null;
  let distance = radius;
  for (const relation of relations) {
    const curve = curveGeometry(relation);
    const next = Math.hypot(curve.midpointX - x, curve.midpointY - y);
    if (next <= distance) {
      nearest = relation;
      distance = next;
    }
  }
  return nearest;
}
