import { randomUUID } from "node:crypto";
import type { Readable } from "node:stream";
import { emptyOutcome, type UploadOutcome } from "#lib/uploads/documents.ts";
import { baseName, classifyName, isSystemFile, MAX_PDF_BYTES } from "#lib/uploads/limits.ts";
import { ArchiveError, unpackArchive } from "./archives.ts";
import type { NewDocument, Replacement, SaveResult } from "./documents.ts";
import { relay, type FormPart } from "./multipart.ts";
import { storePdf, type ObjectWriter, type RejectedPdf } from "./store.ts";

export interface UploadServices {
  userId: string;
  writeObject(key: string): ObjectWriter;
  deleteObject(key: string): Promise<void>;
  insertDocument(values: NewDocument): Promise<SaveResult>;
  replaceDocument(values: Replacement): Promise<SaveResult>;
  startIngestion(documentId: string, uploadId: string, key: string): Promise<void>;
}

const rejectionReasons: Record<RejectedPdf["reason"], string> = {
  not_pdf: "This file isn't a PDF.",
  too_large: `PDFs can be at most ${MAX_PDF_BYTES / 1024 / 1024} MB.`,
  empty: "The file is empty.",
};

export function objectKey(documentId: string, uploadId: string): string {
  return `documents/${documentId}/${uploadId}.pdf`;
}

/** Stores every PDF in the request, including those inside archives, as a new document. */
export async function receiveUploads(
  parts: AsyncIterable<FormPart>,
  services: UploadServices,
): Promise<UploadOutcome> {
  const outcome = emptyOutcome();

  async function receivePdf(name: string, stream: Readable) {
    const documentId = randomUUID();
    const uploadId = randomUUID();
    const key = objectKey(documentId, uploadId);
    const stored = await storePdf(stream, services.writeObject(key), MAX_PDF_BYTES);
    if (!stored.ok) {
      outcome.rejected.push({ name, reason: rejectionReasons[stored.reason] });
      return;
    }
    const saved = await services.insertDocument({
      id: documentId,
      userId: services.userId,
      name,
      uploadId,
      objectKey: key,
      sha256: stored.sha256,
      sizeBytes: stored.sizeBytes,
    });
    if (!saved.saved) {
      await services.deleteObject(key);
      outcome.duplicates.push({ name, existingName: saved.existingName });
      return;
    }
    await services.startIngestion(documentId, uploadId, key);
    outcome.added.push({ id: documentId, name });
  }

  for await (const part of parts) {
    if (part.kind !== "file") continue;
    // A file input left empty still sends a part with no name
    if (part.filename === "") {
      part.stream.resume();
      continue;
    }
    const { stream, drained } = relay(part.stream);
    try {
      const kind = classifyName(part.filename);
      if (kind === "pdf") {
        await receivePdf(baseName(part.filename), stream);
      } else if (kind) {
        try {
          await unpackArchive(
            kind,
            stream,
            (path, entry) => receivePdf(baseName(path), entry),
            (path) => outcome.skipped.push(baseName(path)),
          );
        } catch (error) {
          if (!(error instanceof ArchiveError)) throw error;
          outcome.rejected.push({ name: baseName(part.filename), reason: error.message });
        }
      } else if (!isSystemFile(part.filename)) {
        outcome.skipped.push(baseName(part.filename));
      }
    } finally {
      if (!stream.readableEnded) stream.destroy();
      await drained;
    }
  }
  return outcome;
}

/**
 * Stores the single PDF in the request as the new contents of an existing document. The caller
 * removes the previous object and starts ingestion when this returns `{ replaced: true }`.
 */
export async function receiveReplacement(
  parts: AsyncIterable<FormPart>,
  documentId: string,
  services: UploadServices,
): Promise<
  | { replaced: true; name: string; uploadId: string; key: string }
  | { replaced: false; outcome: UploadOutcome }
> {
  const outcome = emptyOutcome();
  for await (const part of parts) {
    if (part.kind !== "file") continue;
    // A file input left empty still sends a part with no name
    if (part.filename === "") {
      part.stream.resume();
      continue;
    }
    const name = baseName(part.filename);
    const { stream, drained } = relay(part.stream);
    try {
      if (classifyName(part.filename) !== "pdf") {
        outcome.rejected.push({ name, reason: "Choose a PDF to replace this document." });
        continue;
      }
      const uploadId = randomUUID();
      const key = objectKey(documentId, uploadId);
      const stored = await storePdf(stream, services.writeObject(key), MAX_PDF_BYTES);
      if (!stored.ok) {
        outcome.rejected.push({ name, reason: rejectionReasons[stored.reason] });
        continue;
      }
      const saved = await services.replaceDocument({
        id: documentId,
        name,
        uploadId,
        objectKey: key,
        sha256: stored.sha256,
        sizeBytes: stored.sizeBytes,
      });
      if (!saved.saved) {
        await services.deleteObject(key);
        outcome.duplicates.push({ name, existingName: saved.existingName });
        continue;
      }
      return { replaced: true, name, uploadId, key };
    } finally {
      if (!stream.readableEnded) stream.destroy();
      await drained;
    }
  }
  return { replaced: false, outcome };
}
