import { expect, test } from "vitest";
import { type IngestError, ingestErrorMessage, isFinalIngestEvent } from "./ingest.ts";

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

test("only ingested and failed end an ingestion", () => {
  expect(isFinalIngestEvent({ state: "validating" })).toBe(false);
  expect(isFinalIngestEvent({ state: "rasterizing", pageCount: 3, pagesDone: 1 })).toBe(false);
  expect(isFinalIngestEvent({ state: "ingested", pageCount: 3 })).toBe(true);
  expect(isFinalIngestEvent({ state: "failed", error: "damaged" })).toBe(true);
});
