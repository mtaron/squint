import * as documents from "./documents.ts";
import { startIngestion } from "./ingest.ts";
import { deleteObject, ensureUserBucket, s3ObjectWriter } from "./s3.ts";
import type { UploadServices } from "./upload.ts";

/** Wires uploads for one user to their bucket, the database, and the ingestion workflows. */
export async function uploadServices(userId: string): Promise<UploadServices> {
  const bucket = await ensureUserBucket(userId);
  return {
    userId,
    writeObject: s3ObjectWriter(bucket),
    deleteObject: (key) => deleteObject(bucket, key),
    insertDocument: documents.insertDocument,
    replaceDocument: (values) => documents.replaceDocument(userId, values),
    startIngestion: (documentId, uploadId, key) =>
      ingest(userId, bucket, documentId, uploadId, key),
  };
}

export async function ingest(
  userId: string,
  bucket: string,
  documentId: string,
  uploadId: string,
  key: string,
): Promise<void> {
  try {
    await startIngestion({ documentId, uploadId, userId, bucket, key });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    await documents.markIngestionFailed(
      documentId,
      uploadId,
      `Could not start ingestion: ${detail}`,
    );
  }
}
