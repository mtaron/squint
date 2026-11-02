import { expect, test } from "vitest";
import { knownTimeZone, preferredLocale } from "./viewer-preferences.ts";

test("prefers the first language the browser lists", () => {
  expect(preferredLocale("de-DE,de;q=0.9,en;q=0.8")).toBe("de-DE");
});

test("accepts a language with no region", () => {
  expect(preferredLocale("fr")).toBe("fr");
});

test("ignores the quality of the first language", () => {
  expect(preferredLocale("en-GB;q=0.9,en;q=0.8")).toBe("en-GB");
});

test.each([null, "", "*", "not a locale!"])("falls back to English for %j", (header) => {
  expect(preferredLocale(header)).toBe("en");
});

test.each(["America/New_York", "Etc/GMT+5", "UTC"])("keeps the time zone %s", (timeZone) => {
  expect(knownTimeZone(timeZone)).toBe(timeZone);
});

test.each([undefined, "", "Not/AZone"])("falls back to UTC for %j", (timeZone) => {
  expect(knownTimeZone(timeZone)).toBe("UTC");
});
