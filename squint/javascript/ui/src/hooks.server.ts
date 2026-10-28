import { sequence, type Handle } from "@sveltejs/kit/hooks";
import { building } from "$app/env";
import { auth } from "#lib/server/auth.ts";
import { svelteKitHandler } from "better-auth/svelte-kit";

const aboveTheFoldFonts = new Set([
  "node_modules/@fontsource-variable/fraunces/files/fraunces-latin-full-normal.woff2",
  "node_modules/@fontsource-variable/instrument-sans/files/instrument-sans-latin-wght-normal.woff2",
]);

// https://svelte.dev/docs/kit/performance#Optimizing-assets-Fonts
const preloadFonts: Handle = ({ event, resolve }) =>
  resolve(event, {
    preload: (asset) =>
      asset.type === "font"
        ? aboveTheFoldFonts.has(asset.filename)
        : asset.type === "js" || asset.type === "css",
  });

const handleBetterAuth: Handle = async ({ event, resolve }) => {
  const session = await auth.api.getSession({ headers: event.request.headers });

  if (session) {
    event.locals.session = session.session;
    event.locals.user = session.user;
    event.tracing.root.setAttribute("user.id", session.user.id);
  }

  return svelteKitHandler({ event, resolve, auth, building });
};

export const handle: Handle = sequence(preloadFonts, handleBetterAuth);
