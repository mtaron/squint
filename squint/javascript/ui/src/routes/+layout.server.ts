import { knownTimeZone, preferredLocale, TIME_ZONE_COOKIE } from "#lib/viewer-preferences.ts";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = ({ locals, request, cookies }) => ({
  user: locals.user ?? null,
  locale: preferredLocale(request.headers.get("accept-language")),
  timeZone: knownTimeZone(cookies.get(TIME_ZONE_COOKIE)),
});
