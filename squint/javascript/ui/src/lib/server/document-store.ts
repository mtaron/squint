import { createHash } from "node:crypto";
import { documentIdFormat, documentObjectKey, userBucketName } from "@squint/db/storage";
import { customAlphabet } from "nanoid";
import type { ObjectStorage } from "#lib/server/s3.ts";
import { fileProblem } from "#lib/upload-limits.ts";

const newDocumentId = customAlphabet(documentIdFormat.alphabet, documentIdFormat.length);

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

/** The workflow input of cleanupDocuments in squint/javascript/worker */
export interface CleanupDocumentsInput {
  userId: string;
  documentIds: string[];
}

export interface RemovedDocument {
  id: string;
  /** Null if the document was still being ingested */
  pageCount: number | null;
}

export interface DocumentStoreDependencies {
  storage: Pick<ObjectStorage, "put" | "delete">;
  /** Inserts the row, or returns the name of the user's earlier upload with the same contents. */
  insert(row: NewDocument): Promise<{ duplicateOf?: string }>;
  remove(documentId: string): Promise<void>;
  startIngestion(input: IngestInput): Promise<void>;
  /** Tells the user's other requests about a document whose ingestion has started. */
  announce(userId: string, document: AnnouncedDocument): Promise<void>;
  /** Removes the rows of those documents the user owns, undoing it if `afterRemoving` throws. */
  removeOwned(
    userId: string,
    documentIds: string[],
    afterRemoving: (removed: RemovedDocument[]) => Promise<void>,
  ): Promise<void>;
  startCleanup(input: CleanupDocumentsInput): Promise<void>;
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

  return {
    /** Streams the file to the user's bucket, records it, and starts ingesting it. */
    async add(userId: string, file: Pick<File, "name" | "size" | "stream">): Promise<AddOutcome> {
      const problem = fileProblem(file);
      if (problem) {
        return { problem };
      }

      const documentId = newDocumentId();
      const bucket = userBucketName(userId);
      const key = documentObjectKey(documentId);
      const sha256 = sha256Passthrough();

      try {
        await storage.put(bucket, key, file.stream().pipeThrough(sha256.stream));
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

    /**
     * Deletes the user's documents. Ingestion stops once it finds its row gone and removes the
     * document's files itself, so only the files of ingested documents need cleaning up here.
     */
    async delete(userId: string, documentIds: string[]): Promise<void> {
      await dependencies.removeOwned(userId, documentIds, async (removed) => {
        const ingested = removed.filter(({ pageCount }) => pageCount !== null);
        if (ingested.length > 0) {
          await dependencies.startCleanup({ userId, documentIds: ingested.map(({ id }) => id) });
        }
      });
    },
  };
}
