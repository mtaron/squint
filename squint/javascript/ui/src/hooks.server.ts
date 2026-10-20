import type { Handle, ServerInit } from "@sveltejs/kit/hooks";
import { building } from "$app/env";
import { auth } from "#lib/server/auth.ts";
import { runMigrations } from "#lib/server/db/migrate.ts";
import { svelteKitHandler } from "better-auth/svelte-kit";

export const init: ServerInit = async () => {
  if (!building) await runMigrations();
};

const handleBetterAuth: Handle = async ({ event, resolve }) => {
  const session = await auth.api.getSession({ headers: event.request.headers });

  if (session) {
    event.locals.session = session.session;
    event.locals.user = session.user;
    event.tracing.root.setAttribute("user.id", session.user.id);
  }

  return svelteKitHandler({ event, resolve, auth, building });
};

export const handle: Handle = handleBetterAuth;
