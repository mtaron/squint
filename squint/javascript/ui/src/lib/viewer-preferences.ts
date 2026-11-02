export const TIME_ZONE_COOKIE = "timeZone";

const ONE_YEAR_IN_SECONDS = 60 * 60 * 24 * 365;

/** Requests don't carry a time zone, so the browser leaves one for the server to render with. */
export function rememberTimeZone() {
  const timeZone = encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone);
  document.cookie = `${TIME_ZONE_COOKIE}=${timeZone}; path=/; max-age=${ONE_YEAR_IN_SECONDS}; samesite=lax`;
}

export function preferredLocale(acceptLanguage: string | null): string {
  const [first = ""] = (acceptLanguage ?? "").split(/[,;]/);
  try {
    return new Intl.Locale(first.trim()).toString();
  } catch {
    return "en";
  }
}

export function knownTimeZone(timeZone = "UTC"): string {
  try {
    new Intl.DateTimeFormat("en", { timeZone });
    return timeZone;
  } catch {
    return "UTC";
  }
}
