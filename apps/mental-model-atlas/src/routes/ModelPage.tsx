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
  const coverage = sourceCard.coverage;
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
          <p className="eyebrow">Source card complete · learning page partial · local review</p>
          <p className="canonical-id">{model.model_id}</p>
          <h1 data-source-line="1">{title}</h1>
          <p className="definition-lede">
            The Markdown card is the primary educational layer. Lolla's compiled
            operational fields and exact graph connections appear afterward as
            separately labelled projections.
          </p>
          <div className="coverage-banner" role="status">
            <div><strong>{coverage.word_count.toLocaleString()}</strong><span>source words</span></div>
            <div><strong>{coverage.physical_line_count}</strong><span>physical lines accounted</span></div>
            <div><strong>{coverage.rendered_substantive_line_count}</strong><span>substantive lines rendered</span></div>
            <div><strong>{coverage.omitted_substantive_line_count}</strong><span>substantive omissions</span></div>
          </div>
          <div className="button-row">
            <a className="button" href="#source-card">Read the complete card</a>
            <AppLink className="button secondary" href="/atlas?model=abstraction">
              Show in Atlas
            </AppLink>
          </div>
        </header>

        <section className="source-layer" id="source-card" aria-labelledby="source-card-title">
          <header className="source-layer-heading">
            <div>
              <p className="eyebrow">Layer 1 · authoritative source</p>
              <h2 id="source-card-title">The full model card</h2>
            </div>
            <p>
              Every substantive source line is represented once. Blank lines and
              dashed separators become spacing; Markdown emphasis and the source
              table receive semantic HTML without changing the wording.
            </p>
          </header>
          <CardSourceDocument sourceCard={sourceCard} />
        </section>

        <OperationalModelSummary operational={operational_curation} />
        <ModelConnections connections={connections} />
        <PageCoverageDisclosure page={page} />
      </article>

      <StatusDisclosure
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
    <section className="derived-layer page-coverage-layer" aria-labelledby="page-coverage-title">
      <header className="derived-layer-heading">
        <div>
          <p className="eyebrow">Truthfulness boundary</p>
          <h2 id="page-coverage-title">This source card is complete; this learning page is partial</h2>
        </div>
        <p>
          Complete source custody does not silently stand in for the Teacher journeys,
          reviewed practice, or runtime-affordance projection that this repair did not add.
        </p>
      </header>
      <ul className="coverage-component-list">
        {page.coverage.components.map((component) => (
          <li key={component.component}>
            <strong>{component.component.replaceAll("_", " ")}</strong>
            <span>{component.status.replaceAll("_", " ")}</span>
            {component.render_disposition ? <small>{component.render_disposition.replaceAll("_", " ")}</small> : null}
          </li>
        ))}
      </ul>
    </section>
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
