import { useEffect, useMemo, useRef } from "react";

import {
  curveGeometry,
  GRAPH_HEIGHT,
  GRAPH_WIDTH,
  positionModelLabels,
  positionModels,
  positionRelations,
} from "./graphGeometry";
import type { GraphRendererProps, PositionedModel, PositionedRelation } from "./graphTypes";

const INK = "#171717";
const CANVAS = "#f3f3f3";

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
    let animationFrame = 0;
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
      draw(context, visibleModels, relations, props, performance.now());
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    if (!props.motionPaused) {
      const animate = (time: number) => {
        draw(context, visibleModels, relations, props, time);
        animationFrame = requestAnimationFrame(animate);
      };
      animationFrame = requestAnimationFrame(animate);
    }
    return () => {
      observer.disconnect();
      cancelAnimationFrame(animationFrame);
    };
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
  time: number,
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
  for (const [index, positioned] of relations.entries()) {
    const { relation, source, target } = positioned;
    const curve = curveGeometry(positioned);
    context.globalAlpha = relation.relation_id === props.selectedRelationId ? 1 : 0.68;
    context.strokeStyle = INK;
    if (relation.relation_type === "tension") {
      strokeRelation(context, positioned, relation.relation_id === props.selectedRelationId ? 6 : 4, []);
      context.strokeStyle = CANVAS;
      strokeRelation(context, positioned, relation.relation_id === props.selectedRelationId ? 2 : 1.5, []);
      context.strokeStyle = INK;
    } else {
      strokeRelation(
        context,
        positioned,
        relation.relation_id === props.selectedRelationId ? 3 : 1.5,
        relation.relation_type === "antagonist" ? [9, 6] : [],
      );
    }
    drawArrow(context, positioned, 0.82);
    if (relation.relation_type === "antagonist") {
      drawCross(context, curve.midpointX, curve.midpointY);
    }
    const progress = props.motionPaused
      ? 0.52
      : ((time / 3000 + index * 0.17) % 1);
    const flow = quadraticPoint(positioned, progress);
    context.beginPath();
    context.arc(flow.x, flow.y, 3.25, 0, Math.PI * 2);
    context.fillStyle = INK;
    context.fill();
  }
  context.setLineDash([]);
  const hasSelection = Boolean(props.selectedModelId || props.selectedRelationId);
  const labels = positionModelLabels(models);
  for (const positioned of models) {
    const { model, x, y } = positioned;
    const selected = model.model_id === props.selectedModelId;
    const hovered = model.model_id === props.hoveredModelId;
    const dimmed = hasSelection && !props.relatedModelIds.has(model.model_id);
    context.globalAlpha = dimmed ? 0.5 : 1;
    context.beginPath();
    context.arc(x, y, selected ? 13 : 10, 0, Math.PI * 2);
    context.fillStyle = CANVAS;
    context.fill();
    context.strokeStyle = INK;
    context.lineWidth = selected || hovered ? 2.5 : 1;
    context.stroke();
    context.beginPath();
    context.arc(x, y, selected ? 5 : hovered ? 4.25 : 3.25, 0, Math.PI * 2);
    context.fillStyle = INK;
    context.fill();
    const label = labels.get(model.model_id);
    if (label) {
      context.fillStyle = CANVAS;
      context.fillRect(label.x, label.y, label.width, label.height);
      context.strokeStyle = selected || hovered ? INK : "#d4d4d4";
      context.lineWidth = selected || hovered ? 2 : 1;
      context.strokeRect(label.x, label.y, label.width, label.height);
      context.font = "600 12.5px IBM Plex Sans, sans-serif";
      context.textAlign = "left";
      context.textBaseline = "middle";
      context.fillStyle = INK;
      context.fillText(model.display_name, label.x + 8, label.y + label.height / 2);
    }
  }
  context.globalAlpha = 1;
  context.restore();
}

function cameraFor(
  _models: PositionedModel[],
  _relations: PositionedRelation[],
  _props: GraphRendererProps,
): { x: number; y: number; targetX: number; targetY: number; scale: number } {
  return {
    x: GRAPH_WIDTH / 2,
    y: GRAPH_HEIGHT / 2,
    targetX: GRAPH_WIDTH / 2,
    targetY: GRAPH_HEIGHT / 2,
    scale: 1,
  };
}

function drawArrow(
  context: CanvasRenderingContext2D,
  relation: PositionedRelation,
  progress: number,
): void {
  const point = quadraticPoint(relation, progress);
  const next = quadraticPoint(relation, Math.min(1, progress + 0.01));
  const angle = Math.atan2(next.y - point.y, next.x - point.x);
  context.save();
  context.translate(point.x, point.y);
  context.rotate(angle);
  context.beginPath();
  context.moveTo(7, 0);
  context.lineTo(-5, -4);
  context.lineTo(-5, 4);
  context.closePath();
  context.fillStyle = INK;
  context.fill();
  context.restore();
}

function strokeRelation(
  context: CanvasRenderingContext2D,
  relation: PositionedRelation,
  width: number,
  dash: number[],
): void {
  const curve = curveGeometry(relation);
  context.beginPath();
  context.moveTo(relation.source.x, relation.source.y);
  context.quadraticCurveTo(
    curve.controlX,
    curve.controlY,
    relation.target.x,
    relation.target.y,
  );
  context.lineWidth = width;
  context.setLineDash(dash);
  context.stroke();
}

function quadraticPoint(relation: PositionedRelation, progress: number) {
  const curve = curveGeometry(relation);
  const inverse = 1 - progress;
  return {
    x:
      inverse ** 2 * relation.source.x +
      2 * inverse * progress * curve.controlX +
      progress ** 2 * relation.target.x,
    y:
      inverse ** 2 * relation.source.y +
      2 * inverse * progress * curve.controlY +
      progress ** 2 * relation.target.y,
  };
}

function drawCross(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
): void {
  context.save();
  context.strokeStyle = INK;
  context.lineWidth = 1.75;
  context.setLineDash([]);
  context.beginPath();
  context.moveTo(x - 4, y - 4);
  context.lineTo(x + 4, y + 4);
  context.moveTo(x - 4, y + 4);
  context.lineTo(x + 4, y - 4);
  context.stroke();
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
