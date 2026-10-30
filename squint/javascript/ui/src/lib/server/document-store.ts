import { createHash } from "node:crypto";
import { documentObjectKey, userBucketName } from "@squint/db/storage";
import { v7 as uuidv7 } from "uuid";
import type { UploadProgress } from "#lib/ingest.ts";
import type { ObjectStorage } from "#lib/server/s3.ts";
import { fileProblem } from "#lib/upload-limits.ts";

const PROGRESS_INTERVAL_MS = 250;

export interface NewDocument {
  id: string;
  userId: string;
  name: string;
  sha256: string;
  sizeBytes: number;
}

/** The workflow input of IngestDocumentWorkflow in squint/python/apps/ingest */
export interface IngestInput {
  documentId: string;
  userId: string;
  bucket: string;
  key: string;
}

export interface DocumentStoreDependencies {
  storage: ObjectStorage;
  /** Inserts the row, or returns the name of the user's earlier upload with the same contents. */
  insert(row: NewDocument): Promise<{ duplicateOf?: string }>;
  remove(documentId: string): Promise<void>;
  startIngestion(input: IngestInput): Promise<void>;
  reportProgress(userId: string, progress: UploadProgress): Promise<void>;
  /** Tells the user's other requests about a document whose ingestion has started. */
  announce(userId: string, document: AnnouncedDocument): Promise<void>;
}

export interface AnnouncedDocument {
  id: string;
  name: string;
  sizeBytes: number;
}

export type AddOutcome = { documentId: string } | { problem: string };

function sha256Passthrough() {
  const hash = createHash("sha256");
  const stream = new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      hash.update(chunk);
      controller.enqueue(chunk);
    },
  });
  return { stream, digest: () => hash.digest("hex") };
}

export function documentStore(dependencies: DocumentStoreDependencies) {
  const { storage } = dependencies;

  function progressReporter(userId: string, uploadId: string | undefined, total: number) {
    let lastReportedAt = 0;
    return (loaded: number) => {
      const now = Date.now();
      if (!uploadId || (loaded < total && now - lastReportedAt < PROGRESS_INTERVAL_MS)) {
        return;
      }
      lastReportedAt = now;
      dependencies.reportProgress(userId, { uploadId, loaded, total }).catch((error) => {
        console.error("Failed to report upload progress", error);
      });
    };
  }

  return {
    /** Streams the file to the user's bucket, records it, and starts ingesting it. */
    async add(userId: string, file: File, uploadId?: string): Promise<AddOutcome> {
      const problem = fileProblem(file);
      if (problem) {
        return { problem };
      }

      const documentId = uuidv7();
      const bucket = userBucketName(userId);
      const key = documentObjectKey(documentId);
      const sha256 = sha256Passthrough();

      try {
        await storage.put(
          bucket,
          key,
          file.stream().pipeThrough(sha256.stream),
          progressReporter(userId, uploadId, file.size),
        );
      } catch (error) {
        console.error(`Failed to upload ${file.name}`, error);
        return { problem: "The upload failed. Try again." };
      }

      const { duplicateOf } = await dependencies.insert({
        id: documentId,
        userId,
        name: file.name,
        sha256: sha256.digest(),
        sizeBytes: file.size,
      });
      if (duplicateOf !== undefined) {
        await storage.delete(bucket, key);
        return {
          problem: `Already uploaded as ${duplicateOf}, so it was skipped.`,
        };
      }

      try {
        await dependencies.startIngestion({ documentId, userId, bucket, key });
      } catch (error) {
        console.error(`Failed to start ingesting ${documentId}`, error);
        await dependencies.remove(documentId);
        await storage.delete(bucket, key);
        return { problem: "This PDF couldn't be processed. Try again." };
      }

      await dependencies.announce(userId, {
        id: documentId,
        name: file.name,
        sizeBytes: file.size,
      });
      return { documentId };
    },
  };
}
