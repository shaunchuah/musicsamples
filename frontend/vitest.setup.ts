// frontend/vitest.setup.ts
// Loads shared testing utilities and global matchers before Vitest test files run.
// Exists to provide consistent DOM assertions (via jest-dom) across the frontend test suite.

import "@testing-library/jest-dom/vitest";
