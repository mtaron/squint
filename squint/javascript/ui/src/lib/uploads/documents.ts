// Mirrors squint/python/apps/ingest/models.py
export const documentStatuses = ["processing", "ready", "failed"] as const;
export type DocumentStatus = (typeof documentStatuses)[number];

export const ingestErrors = [
  "password_protected",
  "unsupported_security",
  "unreadable",
  "too_many_pages",
  "internal",
] as const;
export type IngestError = (typeof ingestErrors)[number];

export type DocumentSummary = {
  id: string;
  name: string;
  sizeBytes: number;
  status: DocumentStatus;
  pageCount: number | null;
  errorCode: IngestError | null;
  errorDetail: string | null;
  uploadedAt: Date;
};

export type DocumentStatusEvent = {
  document_id: string;
  upload_id: string;
  status: DocumentStatus;
  page_count: number | null;
  error_code: IngestError | null;
  error_detail: string | null;
};

export type UploadOutcome = {
  added: { id: string; name: string }[];
  duplicates: { name: string; existingName: string }[];
  skipped: string[];
  rejected: { name: string; reason: string }[];
};

export function emptyOutcome(): UploadOutcome {
  return { added: [], duplicates: [], skipped: [], rejected: [] };
}
