import { useCallback, useEffect } from "react";

import { ProjectionLoading } from "../components/ProjectionFailure";
import { StatusDisclosure } from "../components/StatusDisclosure";
import {
  type AtlasModelPage,
  loadModelPage,
} from "../projection";
import { useProjection } from "../projectionContext";
import { AppLink } from "../router";
import { useAsyncResource } from "../useAsyncResource";

export default function ModelPage({ slug }: { slug: string }) {
  const projectionState = useProjection();
  const loader = useCallback(
    (signal: AbortSignal) => loadModelPage(slug, signal),
    [slug],
  );
  const pageResource = useAsyncResource(`model:${slug}`, loader);

  useEffect(() => {
    document.title = `${slug || "Unknown model"} · Lolla Atlas`;
  }, [slug]);

  if (pageResource.status === "loading") {
    return <ModelFrame><ProjectionLoading /></ModelFrame>;
  }
  if (pageResource.status === "failed") {
    return (
      <ModelFrame>
        <PageLoadFailure kind="model" message={pageResource.message} />
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
          <p className="eyebrow">Page unavailable in Phase 1</p>
          <h1>{model?.display_name ?? "Model page not found"}</h1>
          {model ? (
            <>
              <p>{model.summary.text}</p>
              <p>
                This stable model exists in the loaded index, but this tracer bullet
                does not include its full page artifact. Missing teaching sections are
                not filled with generated prose.
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

function RenderedModelPage({ page }: { page: AtlasModelPage }) {
  const { model, sections } = page;
  useEffect(() => {
    document.title = `${model.display_name} · Lolla Atlas`;
  }, [model.display_name]);
  return (
    <main id="main" className="content-route model-page-route">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <AppLink href="/models">Model Library</AppLink>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{model.display_name}</span>
      </nav>
      <article className="learning-page">
        <header className="learning-hero">
          <p className="eyebrow">Canonical mental model</p>
          <p className="canonical-id">{model.model_id}</p>
          <h1>{model.display_name}</h1>
          <p className="definition-lede">{sections.definition.text}</p>
          <div className="button-row">
            <AppLink
              className="button"
              href={`/atlas?model=${encodeURIComponent(model.model_id)}`}
            >
              Show in Atlas
            </AppLink>
            <AppLink className="button secondary" href="/models">
              Browse models
            </AppLink>
          </div>
        </header>

        <div className="learning-grid">
          <PageListSection title="Use when" section={sections.use_when} />
          <PageListSection title="Avoid or constrain when" section={sections.avoid_when} />
          <section className="page-section">
            <p className="section-number">03</p>
            <h2>Reasoning profile</h2>
            <dl className="compact-facts">
              <div><dt>Input</dt><dd>{sections.reasoning_profile.input_type}</dd></div>
              <div><dt>Output</dt><dd>{sections.reasoning_profile.output_type}</dd></div>
              <div>
                <dt>Reasoning types</dt>
                <dd>{sections.reasoning_profile.reasoning_types.join(", ")}</dd>
              </div>
            </dl>
          </section>
          <section className="page-section page-section-wide">
            <p className="section-number">04</p>
            <h2>Failure modes and mitigations</h2>
            <ul className="failure-mode-list">
              {sections.failure_modes.items.map((item, index) => (
                <li key={`${item.text}:${index}`}>
                  <h3>{item.text}</h3>
                  <p>{item.mitigation}</p>
                  <small>
                    {item.extraction_type} · {item.confidence} confidence
                  </small>
                </li>
              ))}
            </ul>
          </section>
          <PageListSection
            title="Premortem questions"
            section={sections.premortem_questions}
          />
          <PageListSection title="Practical heuristics" section={sections.heuristics} />
        </div>
      </article>
      <StatusDisclosure
        status={page.status}
        missingness={page.missingness}
        sourceRefs={[model.source_ref]}
        nonClaims={page.non_claims}
      />
    </main>
  );
}

function PageListSection({
  title,
  section,
}: {
  title: string;
  section: { items: string[]; missingness: { status: string } };
}) {
  return (
    <section className="page-section">
      <p className="section-status">{section.missingness.status}</p>
      <h2>{title}</h2>
      <ul>
        {section.items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function PageLoadFailure({ kind, message }: { kind: string; message: string }) {
  return (
    <section className="unavailable-page" role="alert">
      <p className="eyebrow">{kind} page failed</p>
      <h1>The source-bound page artifact could not be verified.</h1>
      <p>{message}</p>
      <p>This failure is not rendered as an unavailable semantic object.</p>
    </section>
  );
}

function ModelFrame({ children }: { children: React.ReactNode }) {
  return <main id="main" className="content-route model-page-route">{children}</main>;
}
