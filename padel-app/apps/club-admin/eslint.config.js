import { nextJsConfig } from "@workspace/eslint-config/next-js";

export default [
  ...nextJsConfig,
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "dist/**",
      "build/**",
      "cypress/**",
      "cypress.config.ts",
      "next.config.mjs",
      "postcss.config.mjs",
      "tailwind.config.ts",
    ],
  },
];