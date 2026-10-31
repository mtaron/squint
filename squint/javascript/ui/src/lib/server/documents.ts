import { document, documentPage } from "@squint/db";
import { and, asc, desc, eq, isNull } from "drizzle-orm";
import { ingestWorkflowId } from "#lib/ingest.ts";
import { db } from "#lib/server/db/index.ts";
import { documentStore } from "#lib/server/document-store.ts";
import { s3Storage } from "#lib/server/s3.ts";
import { getTemporalClient } from "#lib/server/temporal.ts";
import { channels, publish } from "#lib/server/user-events.ts";

// Served by the Python worker in squint/python/apps/ingest
const INGEST_TASK_QUEUE = "ingest";

export const storage = s3Storage();

export function listDocuments(userId: string) {
  return db
    .select({
      id: document.id,
      name: document.name,
      sizeBytes: document.sizeBytes,
      pageCount: document.pageCount,
      uploadedAt: document.uploadedAt,
    })
    .from(document)
    .where(eq(document.userId, userId))
    .orderBy(desc(document.uploadedAt));
}

export function documentsBeingIngested(userId: string) {
  return db
    .select({ id: document.id, name: document.name, sizeBytes: document.sizeBytes })
    .from(document)
    .where(and(eq(document.userId, userId), isNull(document.pageCount)));
}

/** The document's page count, null while it's being ingested, or undefined once it's gone. */
export async function pageCount(documentId: string): Promise<number | null | undefined> {
  const [row] = await db
    .select({ pageCount: document.pageCount })
    .from(document)
    .where(eq(document.id, documentId));
  return row?.pageCount;
}

/** The user's document and its page sizes, or undefined if they have no such document. */
export async function documentWithPages(userId: string, documentId: string) {
  const [row] = await db
    .select({ name: document.name, pageCount: document.pageCount })
    .from(document)
    .where(and(eq(document.id, documentId), eq(document.userId, userId)));
  if (!row) {
    return undefined;
  }
  const pages = await db
    .select({ width: documentPage.width, height: documentPage.height })
    .from(documentPage)
    .where(eq(documentPage.documentId, documentId))
    .orderBy(asc(documentPage.pageNumber));
  return { name: row.name, ready: row.pageCount !== null, pages };
}

export const documents = documentStore({
  storage,

  async insert(row) {
    const inserted = await db
      .insert(document)
      .values(row)
      .onConflictDoNothing({ target: [document.userId, document.sha256] })
      .returning({ id: document.id });
    if (inserted.length > 0) {
      return {};
    }
    const [existing] = await db
      .select({ name: document.name })
      .from(document)
      .where(and(eq(document.userId, row.userId), eq(document.sha256, row.sha256)));
    return { duplicateOf: existing?.name ?? row.name };
  },

  async remove(documentId) {
    await db.delete(document).where(eq(document.id, documentId));
  },

  async startIngestion(input) {
    const client = await getTemporalClient();
    await client.workflow.start("IngestDocumentWorkflow", {
      taskQueue: INGEST_TASK_QUEUE,
      workflowId: ingestWorkflowId(input.documentId),
      args: [input],
    });
  },

  reportProgress: (userId, progress) => publish(channels.uploads(userId), progress),

  announce: (userId, announced) => publish(channels.documents(userId), announced),
});
