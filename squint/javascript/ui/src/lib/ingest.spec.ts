import { expect, test } from "vitest";
import {
  formatBytes,
  type IngestError,
  ingestErrorMessage,
  isFinalIngestEvent,
  unindexedPages,
  unindexedPagesMessage,
} from "./ingest.ts";

test("writes sizes the way the viewer's locale does", () => {
  expect(formatBytes(1_572_864, "en")).toBe("1.5 MB");
  expect(formatBytes(1_572_864, "de")).toBe("1,5 MB");
});

test("names the page limit", () => {
  expect(ingestErrorMessage("too_many_pages")).toBe(
    "This PDF has more than 2,000 pages, the most a single PDF can have.",
  );
});

test("falls back to a general message for a missing or unknown reason", () => {
  const general = "This PDF couldn't be processed. Try uploading it again.";
  expect(ingestErrorMessage(null)).toBe(general);
  expect(ingestErrorMessage("from_a_newer_worker" as IngestError)).toBe(general);
});

test("only ingested, failed and deleted end an ingestion", () => {
  expect(isFinalIngestEvent({ state: "validating" })).toBe(false);
  expect(isFinalIngestEvent({ state: "rasterizing", pageCount: 3, pagesDone: 1 })).toBe(false);
  expect(isFinalIngestEvent({ state: "embedding", pageCount: 3, pagesEmbedded: 1 })).toBe(false);
  expect(isFinalIngestEvent({ state: "ingested", pageCount: 3 })).toBe(true);
  expect(isFinalIngestEvent({ state: "failed", error: "damaged" })).toBe(true);
  expect(isFinalIngestEvent({ state: "deleted" })).toBe(true);
});

test("counts the pages a finished document couldn't index", () => {
  expect(unindexedPages({ state: "ingested", pageCount: 8, pagesEmbedded: 5 })).toBe(3);
  expect(unindexedPages({ state: "ingested", pageCount: 8, pagesEmbedded: 8 })).toBe(0);
});

test("doesn't count pages that are still being embedded", () => {
  expect(unindexedPages({ state: "embedding", pageCount: 8, pagesEmbedded: 5 })).toBe(0);
});

test("names how many pages couldn't be indexed", () => {
  expect(unindexedPagesMessage(1, "en")).toBe("1 page couldn't be indexed");
  expect(unindexedPagesMessage(1200, "en")).toBe("1,200 pages couldn't be indexed");
});
