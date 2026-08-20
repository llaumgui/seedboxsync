import { defineConfig } from "vitest/config";
import { resolve } from "node:path";

export default defineConfig({
  resolve: {
    alias: [
      {
        find: "@seedboxsync",
        replacement: resolve(
          import.meta.dirname,
          "seedboxsync/front/static/src/js",
        ),
      },
    ],
  },
  test: {
    include: ["tests/front/static/**/*.test.js"],
    coverage: {
      reporter: ["text", "lcov", "html"],
      include: ["seedboxsync/front/static/src/js/**/*.js"],
    },
  },
});