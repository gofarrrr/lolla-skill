import { useCallback, useEffect } from "react";

import {
  type CardFirstModelPage,
  loadCardFirstModelPage,
} from "../cardFirstModelPage";
import { CardSourceDocument } from "../components/CardSourceDocument";
import { ModelConnections } from "../components/ModelConnections";
import { OperationalModelSummary } from "../components/OperationalModelSummary";
import { ProjectionLoading } from "../components/ProjectionFailure";
import { StatusDisclosure } from "../components/StatusDisclosure";
import { useProjection } from "../projectionContext";
import { AppLink } from "../router";
import { useAsyncResource } from "../useAsyncResource";

export default function ModelPage({ slug }: { slug: string }) {
  const projectionState = useProjection();
  const loader = useCallback(
    (signal: AbortSignal) => loadCardFirstModelPage(slug, signal),
    [slug],
  );
  const pageResource = useAsyncResource(`card-first-model:${slug}`, loader);

  useEffect(() => {
    document.title = `${slug || "Unknown model"} · Lolla Atlas`;
  }, [slug]);

  if (pageResource.status === "loading") {
    return <ModelFrame><ProjectionLoading /></ModelFrame>;
  }
  if (pageResource.status === "failed") {
    return (
      <ModelFrame>
        <PageLoadFailure message={pageResource.message} />
      </ModelFrame>
    );
  }
  if (!pageResource.data) {
    const model =
      projectionState.status === "ready"
        ? projectionState.projection.models.find((item) => item.slug === slug)
        : undefined;
    return (
      <ModelFrame>
        <section className="unavailable-page" role="status">
          <p className="eyebrow">Card-first page unavailable in this repair</p>
          <h1>{model?.display_name ?? "Model page not found"}</h1>
          {model ? (
            <>
              <p>{model.summary.text}</p>
              <p>
                This stable model exists in the Atlas index, but the card-first
                truthfulness repair contains only the complete Abstraction source
                document. Missing articles are not generated from graph fields.
              </p>
              <AppLink className="button" href={`/atlas?model=${encodeURIComponent(model.model_id)}`}>
                Show index record in Atlas
              </AppLink>
            </>
          ) : (
            <p>
              The unknown slug remains unknown. The Atlas did not repair it into a
              nearby canonical identity.
            </p>
          )}
        </section>
      </ModelFrame>
    );
  }

  return <RenderedModelPage page={pageResource.data} />;
}

export function RenderedModelPage({ page }: { page: CardFirstModelPage }) {
  const { model, source_card: sourceCard, operational_curation, connections } = page;
  const title = sourceCard.source_text.slice(0, sourceCard.source_text.indexOf("\n"));
  useEffect(() => {
    document.title = `${model.display_name} · Lolla Atlas`;
  }, [model.display_name]);

  return (
    <main id="main" className="content-route model-page-route card-first-model-route">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <AppLink href="/models">Model Library</AppLink>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{model.display_name}</span>
      </nav>

      <article className="learning-page card-first-page">
        <header className="learning-hero card-first-hero">
          <p className="eyebrow">Mental model · guided source reading · local review</p>
          <h1 data-source-line="1">{title}</h1>
          <p className="definition-lede">
            Learn the idea in five focused steps, then explore how to use it and
            how it connects to other ways of thinking.
          </p>
          <div className="model-orientation-cues" aria-label="Quick orientation">
            {sourceCard.reader_projection.orientation_cues.map((cue) => (
              <blockquote key={cue.label}>
                <p>{cue.label}</p>
                <q>{cue.text}</q>
              </blockquote>
            ))}
          </div>
          <div className="button-row">
            <a className="button" href="#guided-reader-start">Start guided reading</a>
            <AppLink className="button secondary" href="/atlas?model=abstraction">
              See it in the graph
            </AppLink>
          </div>
        </header>

        <section className="source-layer" id="source-card" aria-labelledby="source-card-title">
          <header className="source-layer-heading">
            <div>
              <p className="eyebrow">Layer 1 · authoritative source</p>
              <h2 id="source-card-title">Learn {model.display_name}</h2>
            </div>
            <p>
              Work through one chapter at a time. Your place stays visible, the next
              step is always clear, and the original learning material remains intact.
            </p>
          </header>
          <CardSourceDocument sourceCard={sourceCard} />
        </section>

        <OperationalModelSummary operational={operational_curation} />
        <ModelConnections connections={connections} />
        <PageCoverageDisclosure page={page} />
      </article>

      <StatusDisclosure
        collapseTechnical
        status={page.status}
        missingness={page.missingness}
        sourceRefs={[
          sourceCard.source_ref,
          operational_curation.source_ref,
          connections.source_ref,
        ]}
        nonClaims={page.non_claims}
      />
    </main>
  );
}

function PageCoverageDisclosure({ page }: { page: CardFirstModelPage }) {
  return (
    <aside className="learning-boundary-note" aria-labelledby="page-coverage-title">
      <p className="eyebrow">A human learning guide—not a verdict</p>
      <h2 id="page-coverage-title">Use the model; keep judging the situation.</h2>
      <p>
        This page can help you understand and inspect Abstraction. It cannot prove
        that the model is correct or suitable for your particular decision.
      </p>
      <details className="technical-review-disclosure">
        <summary>What remains outside this local learning preview</summary>
        <ul className="coverage-component-list">
          {page.coverage.components.map((component) => (
            <li key={component.component}>
              <strong>{component.component.replaceAll("_", " ")}</strong>
              <span>{component.status.replaceAll("_", " ")}</span>
              {component.render_disposition ? <small>{component.render_disposition.replaceAll("_", " ")}</small> : null}
            </li>
          ))}
        </ul>
      </details>
    </aside>
  );
}

function PageLoadFailure({ message }: { message: string }) {
  return (
    <section className="unavailable-page" role="alert">
      <p className="eyebrow">Card-first model page failed</p>
      <h1>The source-bound page artifact could not be verified.</h1>
      <p>{message}</p>
      <p>
        This failure is not rendered as a complete card, an unavailable semantic
        object, or a valid zero.
      </p>
    </section>
  );
}

function ModelFrame({ children }: { children: React.ReactNode }) {
  return <main id="main" className="content-route model-page-route">{children}</main>;
}
