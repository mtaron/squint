import { toSvelteKitHandler } from "better-auth/svelte-kit";
import { auth } from "#lib/server/auth.ts";

// A route rather than svelteKitHandler in hooks.server.ts, which also requires request URLs to
// match ORIGIN; the gateway terminates TLS, so the dev server sees http:// URLs.
// https://github.com/better-auth/better-auth/issues/11679
export const fallback = toSvelteKitHandler(auth);
