import { useEffect } from "react";

import { AppLink } from "../router";

export default function LearnPage({ journeyId }: { journeyId?: string }) {
  useEffect(() => {
    document.title = "Learn · Lolla Mental Model Atlas";
  }, []);
  return (
    <main id="main" className="content-route learn-route">
      <header className="content-hero">
        <p className="eyebrow">Guided learning</p>
        <h1>{journeyId ? "This learning path is not available." : "Guided learning is being prepared."}</h1>
        <p>
          For now, explore the Atlas or read the complete model pages. Guided paths
          will appear here only when they are ready to help people learn.
        </p>
      </header>
      <section className="unavailable-page" role="status">
        <p className="eyebrow">Not available yet</p>
        {journeyId ? (
          <>
            <h2>No reviewed journey has ID “{journeyId}”.</h2>
            <p>
              No reviewed learning path has this address. You can still explore the
              models and their relationships directly.
            </p>
          </>
        ) : (
          <>
            <h2>Start with the models that are ready.</h2>
            <p>
              Read a full model page for context and practice, or use the Atlas to
              discover related ideas.
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
