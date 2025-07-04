/**
 * A shared ESLint configuration for libraries and general TypeScript projects.
 * This is a legacy config format compatible with ESLint v8.
 *
 * @type {import("eslint").Linter.Config}
 * */
module.exports = {
  extends: [
    "eslint:recommended",
    "eslint-config-prettier"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module"
  },
  plugins: [
    "@typescript-eslint",
    "turbo"
  ],
  rules: {
    "turbo/no-undeclared-env-vars": "warn"
  },
  ignorePatterns: ["dist/**", "node_modules/**"]
}