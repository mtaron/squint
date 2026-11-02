import { MAX_PDF_PAGES } from "#lib/upload-limits.ts";

/** Why ingestion failed: IngestError in squint/python/apps/ingest */
export type IngestError = "password_protected" | "damaged" | "too_many_pages" | "unexpected";

/** Published on the `status` topic of each ingestion workflow's stream, by squint/python/apps/ingest. */
export interface IngestEvent {
  state: "validating" | "rasterizing" | "embedding" | "ingested" | "failed" | "deleted";
  pageCount?: number | null;
  pagesDone?: number | null;
  pagesEmbedded?: number | null;
  error?: IngestError | null;
}

export function isFinalIngestEvent({ state }: IngestEvent): boolean {
  return state === "ingested" || state === "failed" || state === "deleted";
}

/** How many pages of a finished document can't be found by search, since embedding them failed. */
export function unindexedPages({ state, pageCount, pagesEmbedded }: IngestEvent): number {
  return state === "ingested" ? (pageCount ?? 0) - (pagesEmbedded ?? 0) : 0;
}

export function unindexedPagesMessage(pages: number, locale: string): string {
  const count = pages.toLocaleString(locale);
  return pages === 1 ? "1 page couldn't be indexed" : `${count} pages couldn't be indexed`;
}

const ingestErrorMessages: Record<IngestError, string> = {
  password_protected: "This PDF is password protected. Remove the password and upload it again.",
  damaged: "This PDF is damaged or isn't really a PDF.",
  too_many_pages: `This PDF has more than ${MAX_PDF_PAGES.toLocaleString("en")} pages, the most a single PDF can have.`,
  unexpected: "This PDF couldn't be processed. Try uploading it again.",
};

export function ingestErrorMessage(error: IngestError | null | undefined): string {
  // A worker newer than this page may send a reason it doesn't know yet
  return (error && ingestErrorMessages[error]) || ingestErrorMessages.unexpected;
}

export interface DocumentIngestion {
  name: string;
  sizeBytes: number;
  latest: IngestEvent;
}

export function ingestWorkflowId(documentId: string): string {
  return `ingest-${documentId}`;
}

const byteUnits = ["byte", "kilobyte", "megabyte", "gigabyte"] as const;

export function formatBytes(bytes: number, locale: string): string {
  const exponent = Math.min(
    byteUnits.length - 1,
    Math.floor(Math.log(Math.max(bytes, 1)) / Math.log(1024)),
  );
  return new Intl.NumberFormat(locale, {
    style: "unit",
    unit: byteUnits[exponent],
    // "828 bytes" rather than the short form's "828 byte"
    unitDisplay: exponent === 0 ? "long" : "short",
    maximumFractionDigits: exponent < 2 ? 0 : 1,
  }).format(bytes / 1024 ** exponent);
}
