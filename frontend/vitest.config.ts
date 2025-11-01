// frontend/vitest.config.ts
// Configures the Vitest test runner for the Next.js frontend codebase.
// Exists so unit tests can share path aliases, JSX transforms, and setup shared across the app.

import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vitest/config";

const projectRoot = fileURLToPath(new URL("./", import.meta.url));

export default defineConfig({
  esbuild: {
    jsx: "automatic",
    jsxImportSource: "react",
  },
  resolve: {
    alias: {
      "@": projectRoot,
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: [resolve(projectRoot, "vitest.setup.ts")],
    css: true,
  },
});
