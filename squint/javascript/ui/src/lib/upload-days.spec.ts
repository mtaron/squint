import { expect, test } from "vitest";
import { groupByUploadDay, uploadedAtLabel } from "./upload-days.ts";

const now = new Date("2026-11-01T18:00:00Z");

function uploaded(...timestamps: string[]) {
  return timestamps.map((timestamp) => ({ uploadedAt: new Date(timestamp) }));
}

function labels(timestamps: string[], timeZone = "UTC", locale = "en") {
  return groupByUploadDay(uploaded(...timestamps), { timeZone, now, locale }).map(
    ({ label }) => label,
  );
}

test("names today and yesterday", () => {
  expect(labels(["2026-11-01T09:00:00Z", "2026-10-31T09:00:00Z"])).toEqual(["Today", "Yesterday"]);
});

test("names older days this year by month and day", () => {
  expect(labels(["2026-10-28T09:00:00Z"])).toEqual(["October 28"]);
});

test("includes the year for earlier years", () => {
  expect(labels(["2025-12-31T09:00:00Z"])).toEqual(["December 31, 2025"]);
});

test("writes older days the way the viewer's locale does", () => {
  expect(labels(["2026-10-28T09:00:00Z"], "UTC", "en-GB")).toEqual(["28 October"]);
});

test("yesterday can fall in the previous year", () => {
  const groups = groupByUploadDay(uploaded("2025-12-31T09:00:00Z"), {
    timeZone: "UTC",
    now: new Date("2026-01-01T09:00:00Z"),
    locale: "en",
  });
  expect(groups.map(({ label }) => label)).toEqual(["Yesterday"]);
});

test("keeps a day's documents together, in the order given", () => {
  const documents = uploaded(
    "2026-11-01T10:00:00Z",
    "2026-11-01T09:00:00Z",
    "2026-10-28T09:00:00Z",
  );
  const groups = groupByUploadDay(documents, { timeZone: "UTC", now, locale: "en" });
  expect(groups.map((group) => group.documents)).toEqual([
    documents.slice(0, 2),
    documents.slice(2),
  ]);
});

test("days follow the viewer's time zone rather than UTC", () => {
  // 03:00 UTC on November 1 is still the evening of October 31 in Los Angeles
  expect(labels(["2026-11-01T03:00:00Z"], "America/Los_Angeles")).toEqual(["Yesterday"]);
});

test("yesterday survives a daylight saving change", () => {
  const groups = groupByUploadDay(uploaded("2026-10-31T19:00:00Z"), {
    timeZone: "America/Los_Angeles",
    // 23:30 on November 1, a 25-hour day, so 24 hours earlier is still November 1
    now: new Date("2026-11-02T07:30:00Z"),
    locale: "en",
  });
  expect(groups.map(({ label }) => label)).toEqual(["Yesterday"]);
});

test("keys days as YYYY-MM-DD in any locale", () => {
  const [day] = groupByUploadDay(uploaded("2026-10-28T09:00:00Z"), {
    timeZone: "UTC",
    now,
    locale: "ar-EG",
  });
  expect(day?.key).toBe("2026-10-28");
});

test("spells out when a document was uploaded", () => {
  const uploadedAt = new Date("2026-10-28T15:14:00Z");
  expect(uploadedAtLabel(uploadedAt, { timeZone: "UTC", locale: "en" })).toBe(
    "Uploaded October 28, 2026 at 3:14 PM",
  );
});

test("spells out the upload time in the viewer's locale", () => {
  const uploadedAt = new Date("2026-10-28T15:14:00Z");
  expect(uploadedAtLabel(uploadedAt, { timeZone: "UTC", locale: "en-GB" })).toBe(
    "Uploaded 28 October 2026 at 15:14",
  );
});
