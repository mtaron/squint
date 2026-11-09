import { expect, test } from "vitest";
import {
  formatBytes,
  type IngestError,
  ingestErrorMessage,
  unindexedPages,
  unindexedPagesMessage,
} from "./ingest.ts";

test.each([
  [828, "828 bytes"],
  [1536, "2 kB"],
  [1_572_864, "1.5 MB"],
  [5 * 1024 ** 4, "5,120 GB"],
])("writes %i bytes as %j", (bytes, written) => {
  expect(formatBytes(bytes, "en")).toBe(written);
});

test("writes sizes the way the viewer's locale does", () => {
  expect(formatBytes(1_572_864, "de")).toBe("1,5 MB");
});

test("falls back to a general message for a reason from a newer worker", () => {
  expect(ingestErrorMessage("from_a_newer_worker" as IngestError)).toBe(
    ingestErrorMessage("unexpected"),
  );
});

test("falls back to a general message when no reason is given", () => {
  expect(ingestErrorMessage(null)).toBe(ingestErrorMessage("unexpected"));
});

test("counts the pages a finished document couldn't index", () => {
  expect(unindexedPages({ state: "ingested", pageCount: 8, pagesEmbedded: 5 })).toBe(3);
});

test("doesn't count pages that are still being embedded", () => {
  expect(unindexedPages({ state: "embedding", pageCount: 8, pagesEmbedded: 5 })).toBe(0);
});

test("names a single page that couldn't be indexed", () => {
  expect(unindexedPagesMessage(1, "en")).toBe("1 page couldn't be indexed");
});

test("names many pages that couldn't be indexed, in the viewer's locale", () => {
  expect(unindexedPagesMessage(1200, "en")).toBe("1,200 pages couldn't be indexed");
});
