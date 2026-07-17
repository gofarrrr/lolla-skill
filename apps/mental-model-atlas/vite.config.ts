import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2022",
    sourcemap: true,
  },
  test: {
    environment: "jsdom",
    restoreMocks: true,
    // The source-complete model and lazy renderer tests exercise large DOM
    // trees in parallel. Keep their deterministic assertions while allowing
    // enough wall time for a contended CI worker.
    testTimeout: 10_000,
  },
});
