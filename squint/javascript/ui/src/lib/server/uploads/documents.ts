import { and, desc, eq, inArray } from "drizzle-orm";
import { db } from "#lib/server/db/index.ts";
import { document, type Document } from "#lib/server/db/schema.ts";

export type NewDocument = {
  id: string;
  userId: string;
  name: string;
  sha256: string;
  uploadId: string;
  objectKey: string;
  sizeBytes: number;
};

export type Replacement = Omit<NewDocument, "userId">;

export type SaveResult = { saved: true } | { saved: false; existingName: string };

const UNIQUE_VIOLATION = "23505";

function isUniqueViolation(error: unknown): boolean {
  for (let current = error; current instanceof Error; current = current.cause) {
    if ((current as { code?: string }).code === UNIQUE_VIOLATION) return true;
  }
  return false;
}

async function nameWithHash(userId: string, sha256: string): Promise<string> {
  const [existing] = await db
    .select({ name: document.name })
    .from(document)
    .where(and(eq(document.userId, userId), eq(document.sha256, sha256)));
  return existing?.name ?? "another document";
}

export async function insertDocument(values: NewDocument): Promise<SaveResult> {
  const inserted = await db
    .insert(document)
    .values({ ...values, status: "processing" })
    .onConflictDoNothing({ target: [document.userId, document.sha256] })
    .returning({ id: document.id });
  if (inserted.length > 0) return { saved: true };
  return { saved: false, existingName: await nameWithHash(values.userId, values.sha256) };
}

export async function replaceDocument(userId: string, values: Replacement): Promise<SaveResult> {
  try {
    await db
      .update(document)
      .set({
        name: values.name,
        sha256: values.sha256,
        uploadId: values.uploadId,
        objectKey: values.objectKey,
        sizeBytes: values.sizeBytes,
        status: "processing",
        pageCount: null,
        errorCode: null,
        errorDetail: null,
        uploadedAt: new Date(),
      })
      .where(and(eq(document.id, values.id), eq(document.userId, userId)));
    return { saved: true };
  } catch (error) {
    if (!isUniqueViolation(error)) throw error;
    return { saved: false, existingName: await nameWithHash(userId, values.sha256) };
  }
}

export async function markIngestionFailed(id: string, uploadId: string, detail: string) {
  await db
    .update(document)
    .set({ status: "failed", errorCode: "internal", errorDetail: detail })
    .where(and(eq(document.id, id), eq(document.uploadId, uploadId)));
}

export async function listDocuments(userId: string) {
  return db
    .select({
      id: document.id,
      name: document.name,
      sizeBytes: document.sizeBytes,
      status: document.status,
      pageCount: document.pageCount,
      errorCode: document.errorCode,
      errorDetail: document.errorDetail,
      uploadedAt: document.uploadedAt,
    })
    .from(document)
    .where(eq(document.userId, userId))
    .orderBy(desc(document.uploadedAt));
}

export async function getDocument(userId: string, id: string): Promise<Document | undefined> {
  const [found] = await db
    .select()
    .from(document)
    .where(and(eq(document.userId, userId), eq(document.id, id)));
  return found;
}

/** Marks a document whose ingestion failed for reasons outside the file as processing again. */
export async function resetForRetry(userId: string, id: string): Promise<Document | undefined> {
  const [reset] = await db
    .update(document)
    .set({ status: "processing", errorCode: null, errorDetail: null })
    .where(
      and(
        eq(document.userId, userId),
        eq(document.id, id),
        eq(document.status, "failed"),
        eq(document.errorCode, "internal"),
      ),
    )
    .returning();
  return reset;
}

export async function deleteDocuments(userId: string, ids: string[]): Promise<Document[]> {
  if (ids.length === 0) return [];
  return db
    .delete(document)
    .where(and(eq(document.userId, userId), inArray(document.id, ids)))
    .returning();
}

export async function deleteFailedDocuments(userId: string): Promise<Document[]> {
  return db
    .delete(document)
    .where(and(eq(document.userId, userId), eq(document.status, "failed")))
    .returning();
}
