import { useEffect } from "react";

import { AppLink } from "../router";

export default function LearnPage({ journeyId }: { journeyId?: string }) {
  useEffect(() => {
    document.title = "Learn · Lolla Mental Model Atlas";
  }, []);
  return (
    <main id="main" className="content-route learn-route">
      <header className="content-hero">
        <p className="eyebrow">Teacher journeys · deliberately gated</p>
        <h1>{journeyId ? "Journey unavailable" : "Learn through relationships"}</h1>
        <p>
          Teacher is a curated sequence, not automatic tutoring over a private
          conversation. Phase 1 proves Atlas identity, relation semantics, pages,
          navigation, and accessibility before adding a journey.
        </p>
      </header>
      <section className="unavailable-page" role="status">
        <p className="eyebrow">Not requested in this projection</p>
        {journeyId ? (
          <>
            <h2>No reviewed journey has ID “{journeyId}”.</h2>
            <p>
              The route remains stable, but an unknown journey is not repaired into a
              lesson or generated from graph centrality.
            </p>
          </>
        ) : (
          <>
            <h2>Curated journeys begin only after the Atlas truth gate.</h2>
            <p>
              A future journey requires source-cleared pages, an editorial sequence,
              human review, practice, and a do-not-overlearn boundary.
            </p>
          </>
        )}
        <div className="button-row">
          <AppLink className="button" href="/atlas">Explore the Atlas</AppLink>
          <AppLink className="button secondary" href="/models">Browse the library</AppLink>
        </div>
      </section>
    </main>
  );
}
