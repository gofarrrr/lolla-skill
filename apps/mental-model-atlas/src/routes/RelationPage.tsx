import { useCallback, useEffect } from "react";

import { ProjectionLoading } from "../components/ProjectionFailure";
import { StatusDisclosure, humanize } from "../components/StatusDisclosure";
import { loadNavigationIndex } from "../navigation";
import {
  type AtlasRelationPage,
  loadRelationPage,
} from "../projection";
import { AppLink } from "../router";
import { useAsyncResource } from "../useAsyncResource";

export default function RelationPage({ relationId }: { relationId: string }) {
  const loader = useCallback(
    (signal: AbortSignal) => loadRelationPage(relationId, signal),
    [relationId],
  );
  const pageResource = useAsyncResource(`relation:${relationId}`, loader);

  useEffect(() => {
    document.title = "Relation · Lolla Atlas";
  }, []);

  if (pageResource.status === "loading") {
    return <RelationFrame><ProjectionLoading /></RelationFrame>;
  }
  if (pageResource.status === "failed") {
    return (
      <RelationFrame>
        <section className="unavailable-page" role="alert">
          <p className="eyebrow">Relation page failed</p>
          <h1>The source-bound page artifact could not be verified.</h1>
          <p>{pageResource.message}</p>
        </section>
      </RelationFrame>
    );
  }
  if (!pageResource.data) {
    return <CanonicalRelationFallback relationId={relationId} />;
  }
  return <RenderedRelationPage page={pageResource.data} />;
}

function CanonicalRelationFallback({ relationId }: { relationId: string }) {
  const loader = useCallback(async () => {
    const index = await loadNavigationIndex();
    const relation = index.relations.find(
      (candidate) => candidate.relation_id === relationId,
    );
    if (!relation) return null;
    const modelNames = new Map(
      index.models.map((model) => [model.model_id, model.display_name]),
    );
    return {
      relation,
      sourceName:
        modelNames.get(relation.source_model_id) ?? relation.source_model_id,
      targetName:
        modelNames.get(relation.target_model_id) ?? relation.target_model_id,
    };
  }, [relationId]);
  const resource = useAsyncResource(`canonical-relation:${relationId}`, loader);

  if (resource.status === "loading") {
    return <RelationFrame><ProjectionLoading /></RelationFrame>;
  }
  if (resource.status === "failed") {
    return (
      <RelationFrame>
        <section className="unavailable-page" role="alert">
          <p className="eyebrow">Canonical relation lookup failed</p>
          <h1>The exact relation identity could not be verified.</h1>
          <p>{resource.message}</p>
        </section>
      </RelationFrame>
    );
  }
  const match = resource.data;
  return (
    <RelationFrame>
      <section className="unavailable-page" role="status">
        <p className="eyebrow">Summary only</p>
        <h1>{match ? `${match.sourceName} → ${match.targetName}` : "Relation not found"}</h1>
        {match ? (
          <>
            <p>{match.relation.summary}</p>
            <p>
              This exact directed record exists, but no complete teaching page is
              available. Missing teaching copy has not been invented.
            </p>
            <AppLink
              className="button"
              href={`/atlas?model=${encodeURIComponent(match.relation.source_model_id)}&relation=${encodeURIComponent(match.relation.relation_id)}`}
            >
              Show exact record in Atlas
            </AppLink>
          </>
        ) : (
          <p>
            The unknown relation ID remains unknown. Parallel or reverse records
            were not merged to manufacture a match.
          </p>
        )}
      </section>
    </RelationFrame>
  );
}

function RenderedRelationPage({ page }: { page: AtlasRelationPage }) {
  const { relation, sections } = page;
  useEffect(() => {
    document.title = `${relation.source_model_id} → ${relation.target_model_id} · Lolla Atlas`;
  }, [relation.source_model_id, relation.target_model_id]);
  return (
    <main id="main" className="content-route relation-page-route">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <AppLink href="/atlas">Atlas</AppLink>
        <span aria-hidden="true">/</span>
        <span aria-current="page">Exact directed relation</span>
      </nav>
      <article className="learning-page">
        <header className="learning-hero relation-learning-hero">
          <p className={`relation-kicker relation-${relation.relation_type}`}>
            <span aria-hidden="true" /> {relation.relation_type}
          </p>
          <h1>
            <AppLink href={`/models/${relation.source_model_id}`}>
              {relation.source_model_id}
            </AppLink>
            <span className="direction-arrow" aria-label="directed to">→</span>
            <AppLink href={`/models/${relation.target_model_id}`}>
              {relation.target_model_id}
            </AppLink>
          </h1>
          <p className="definition-lede">{sections.relation_summary.text}</p>
          <div className="button-row">
            <AppLink
              className="button"
              href={`/atlas?relation=${encodeURIComponent(relation.relation_id)}`}
            >
              Show in Atlas
            </AppLink>
          </div>
        </header>

        <div className="relation-facts">
          <dl className="compact-facts">
            <div><dt>Direction</dt><dd>{humanize(relation.direction)}</dd></div>
            <div><dt>Reciprocal</dt><dd>{relation.is_reciprocal ? "Explicitly yes" : "No"}</dd></div>
            <div><dt>Confidence</dt><dd>{humanize(relation.confidence)} — not certification</dd></div>
            <div><dt>Curation</dt><dd>{humanize(relation.curation_status)}</dd></div>
          </dl>
        </div>

        <div className="learning-grid">
          <TextSection title="Why it matters" section={sections.why_it_matters} />
          <TextSection title="Misread risk" section={sections.misread_risk} />
          <TextSection title="Activation condition" section={sections.activation_condition} />
          <TextSection title="Source excerpt" section={sections.source_excerpt} />
          <section className="page-section page-section-wide">
            <p className="section-status">
              {sections.parallel_record_context.missingness.status}
            </p>
            <h2>Parallel and reverse records stay distinct</h2>
            <div className="parallel-context">
              <div>
                <strong>Parallel relation IDs</strong>
                <ul>
                  {sections.parallel_record_context.parallel_relation_ids.map((id) => (
                    <li key={id}><code>{id}</code></li>
                  ))}
                </ul>
              </div>
              <div>
                <strong>Reverse relation IDs</strong>
                <ul>
                  {sections.parallel_record_context.reverse_relation_ids.map((id) => (
                    <li key={id}><code>{id}</code></li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        </div>
      </article>
      <StatusDisclosure
        status={page.status}
        missingness={page.missingness}
        sourceRefs={relation.source_refs}
        nonClaims={page.non_claims}
      />
    </main>
  );
}

function TextSection({
  title,
  section,
}: {
  title: string;
  section: { text: string; missingness: { status: string } };
}) {
  return (
    <section className="page-section">
      <p className="section-status">{section.missingness.status}</p>
      <h2>{title}</h2>
      <p>{section.text}</p>
    </section>
  );
}

function RelationFrame({ children }: { children: React.ReactNode }) {
  return <main id="main" className="content-route relation-page-route">{children}</main>;
}
