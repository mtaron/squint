// The package ships register-hooks.d.ts beside register-hooks.mjs, but TypeScript only pairs .mjs with .d.mts
declare module "import-in-the-middle/register-hooks.mjs" {
  export * from "import-in-the-middle/register-hooks";
}
