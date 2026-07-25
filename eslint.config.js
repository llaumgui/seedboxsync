import { defineConfig } from "eslint/config";
import js from "@eslint/js";
import globals from "globals";
import packageJson from "eslint-plugin-package-json";

export default defineConfig([
  js.configs.recommended,
  {
    files: ["seedboxsync/front/static/src/**/*.{js,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.es2021,
        Translations: "readonly",
        dateTimeOption: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-console": ["warn", { allow: ["warn", "error"] }],
    },
  },
  {
    ...packageJson.configs.recommended,
    rules: {
      ...packageJson.configs.recommended.rules,
      "package-json/require-exports": "off",
      "package-json/require-files": "off",
      "package-json/require-sideEffects": "off",
      "package-json/require-version": "off",
    },
  },
  {
    ignores: [
      "**/dist/",
      "**/node_modules/",
      "coverage-report/",
      "env/",
      "site/",
    ],
  },
]);
