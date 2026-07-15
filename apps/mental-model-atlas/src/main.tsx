import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { ProjectionProvider } from "./projectionContext";
import "./styles.css";

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
