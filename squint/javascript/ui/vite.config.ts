import { enhancedImages } from "@sveltejs/enhanced-img";
import browserslist from "browserslist";
import { browserslistToTargets } from "lightningcss";
import { defineConfig } from "vitest/config";
import { playwright } from "@vitest/browser-playwright";
import adapter from "@sveltejs/adapter-node";
import { sveltekit } from "@sveltejs/kit/vite";
import { presetIcons } from "@unocss/preset-icons";
import UnoCSS from "@unocss/vite";
import type { Plugin } from "vite";

// Node ends requests after 5 minutes by default, which cuts off large uploads; server.js does the
// same for the production server
const uploadTimeout: Plugin = {
  name: "squint:upload-timeout",
  configureServer({ httpServer }) {
    if (httpServer && "requestTimeout" in httpServer) httpServer.requestTimeout = 60 * 60 * 1000;
  },
};

export default defineConfig({
  plugins: [
    uploadTimeout,
    UnoCSS({
      presets: [
        presetIcons({
          collections: { ph: () => import("@iconify-json/ph").then((module) => module.icons) },
          extraProperties: { display: "inline-block", "vertical-align": "-0.125em" },
        }),
      ],
    }),
    enhancedImages(),
    sveltekit({
      compilerOptions: {
        // Force runes mode for the project, except for libraries. Can be removed in svelte 6.
        runes: ({ filename }) =>
          filename.split(/[/\\]/).includes("node_modules") ? undefined : true,
        experimental: { async: true },
      },
      adapter: adapter(),
      experimental: { remoteFunctions: true },
      tracing: { server: true },
    }),
  ],
  css: {
    transformer: "lightningcss",
    lightningcss: { targets: browserslistToTargets(browserslist()) },
  },
  server: {
    allowedHosts: process.env.ORIGIN ? [new URL(process.env.ORIGIN).hostname] : [],
  },
  test: {
    expect: { requireAssertions: true },
    projects: [
      {
        extends: "./vite.config.ts",
        test: {
          name: "client",
          browser: {
            enabled: true,
            provider: playwright(),
            instances: [{ browser: "chromium", headless: true }],
          },
          include: ["src/**/*.svelte.{test,spec}.{js,ts}"],
          exclude: ["src/lib/server/**"],
        },
      },

      {
        extends: "./vite.config.ts",
        test: {
          name: "server",
          environment: "node",
          include: ["src/**/*.{test,spec}.{js,ts}"],
          exclude: ["src/**/*.svelte.{test,spec}.{js,ts}"],
        },
      },
    ],
  },
});
