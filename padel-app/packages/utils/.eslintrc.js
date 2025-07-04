module.exports = {
  root: true,
  extends: ["@workspace/eslint-config/library.js"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "./tsconfig.json"
  },
  ignorePatterns: ["dist/**", "node_modules/**"]
};