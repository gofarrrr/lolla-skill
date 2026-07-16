import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "@fontsource-variable/familjen-grotesk";
import "@fontsource-variable/ibm-plex-sans";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-600.css";

import { App } from "./App";
import { ProjectionProvider } from "./projectionContext";
import "./styles.css";
import "./restraint.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Atlas root element is missing");
}

createRoot(root).render(
  <StrictMode>
    <ProjectionProvider>
      <App />
    </ProjectionProvider>
  </StrictMode>,
);
