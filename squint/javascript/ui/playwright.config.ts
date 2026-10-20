import { defineConfig } from "@playwright/test";

// The app needs the cluster's services, so tests run against the deployment Tilt keeps up to date
export default defineConfig({
  testMatch: "**/*.e2e.{ts,js}",
  use: { baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "https://squint.loc" },
});
