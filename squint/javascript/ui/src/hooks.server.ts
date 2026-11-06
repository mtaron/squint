import { redirect } from "@sveltejs/kit";
import { sequence, type Handle } from "@sveltejs/kit/hooks";
import { auth } from "#lib/server/auth.ts";

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

const populateSession: Handle = async ({ event, resolve }) => {
  const session = await auth.api.getSession({ headers: event.request.headers });

  if (session) {
    event.locals.session = session.session;
    event.locals.user = session.user;
    event.tracing.root.setAttribute("user.id", session.user.id);
  }

  return resolve(event);
};

const PUBLIC_ROUTES = new Set(["/", "/login", "/health", "/api/auth/[...all]"]);

const requireUser: Handle = ({ event, resolve }) => {
  if (!event.locals.user && !event.isRemoteRequest && !PUBLIC_ROUTES.has(event.route.id ?? "")) {
    redirect(303, "/login");
  }
  return resolve(event);
};

export const handle: Handle = sequence(preloadFonts, populateSession, requireUser);
