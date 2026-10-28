import { error, fail } from "@sveltejs/kit";
import * as documents from "#lib/server/uploads/documents.ts";
import { parseMultipart, UploadLimitError, type FormPart } from "#lib/server/uploads/multipart.ts";
import { deletePrefix, userBucket } from "#lib/server/uploads/s3.ts";
import { ingest, uploadServices } from "#lib/server/uploads/services.ts";
import { receiveReplacement, receiveUploads } from "#lib/server/uploads/upload.ts";
import { MAX_FILES_PER_REQUEST, MAX_REQUEST_BYTES } from "#lib/uploads/limits.ts";
import type { Actions, PageServerLoad, RequestEvent } from "./$types";

export const load: PageServerLoad = async ({ locals, depends }) => {
  if (!locals.user) return { documents: null };
  depends("app:documents");
  return { documents: await documents.listDocuments(locals.user.id) };
};

function requireUser(locals: App.Locals) {
  if (!locals.user) error(401, "Sign in to upload documents");
  return locals.user;
}

function multipartParts(request: Request): AsyncIterable<FormPart> {
  return parseMultipart(request, {
    files: MAX_FILES_PER_REQUEST,
    fileSize: MAX_REQUEST_BYTES,
    totalBytes: MAX_REQUEST_BYTES,
  });
}

async function withUploadLimits<T>(receive: () => Promise<T>) {
  try {
    return await receive();
  } catch (cause) {
    if (cause instanceof UploadLimitError) {
      return fail(413, { message: `Upload rejected: ${cause.message}.` });
    }
    throw cause;
  }
}

async function documentIdField(event: RequestEvent) {
  const form = await event.request.formData();
  const documentId = form.get("documentId");
  if (typeof documentId !== "string" || documentId === "") error(400, "Missing document");
  return documentId;
}

async function removeObjects(userId: string, removed: { id: string }[]) {
  const bucket = userBucket(userId);
  await Promise.all(removed.map(({ id }) => deletePrefix(bucket, `documents/${id}/`)));
}

export const actions: Actions = {
  upload: async ({ request, locals }) => {
    const user = requireUser(locals);
    const services = await uploadServices(user.id);
    return withUploadLimits(async () => ({
      outcome: await receiveUploads(multipartParts(request), services),
    }));
  },

  // The form puts `documentId` before the file, so it is known before the file streams in
  replace: async ({ request, locals }) => {
    const user = requireUser(locals);
    const services = await uploadServices(user.id);
    return withUploadLimits(async () => {
      const parts = multipartParts(request);
      let documentId: string | undefined;
      const fileParts = (async function* () {
        for await (const part of parts) {
          if (part.kind === "field" && part.name === "documentId") documentId = part.value;
          else if (part.kind === "file" && documentId) yield part;
          else if (part.kind === "file") part.stream.resume();
        }
      })();
      const first = await fileParts.next();
      const existing = documentId && (await documents.getDocument(user.id, documentId));
      if (!existing) {
        if (!first.done) first.value.stream.resume();
        await fileParts.return(undefined);
        return fail(404, { message: "That document no longer exists." });
      }
      const replayed = (async function* () {
        if (!first.done) yield first.value;
        yield* fileParts;
      })();
      const result = await receiveReplacement(replayed, existing.id, services);
      if (!result.replaced) return { outcome: result.outcome };
      await services.deleteObject(existing.objectKey);
      await services.startIngestion(existing.id, result.uploadId, result.key);
      return { replaced: { id: existing.id, name: result.name } };
    });
  },

  retry: async (event) => {
    const user = requireUser(event.locals);
    const reset = await documents.resetForRetry(user.id, await documentIdField(event));
    if (!reset)
      return fail(409, { message: "Only documents that failed to process can be retried." });
    await ingest(user.id, userBucket(user.id), reset.id, reset.uploadId, reset.objectKey);
    return { retried: reset.id };
  },

  delete: async (event) => {
    const user = requireUser(event.locals);
    const removed = await documents.deleteDocuments(user.id, [await documentIdField(event)]);
    await removeObjects(user.id, removed);
    return { deleted: removed.length };
  },

  deleteFailed: async ({ locals }) => {
    const user = requireUser(locals);
    const removed = await documents.deleteFailedDocuments(user.id);
    await removeObjects(user.id, removed);
    return { deleted: removed.length };
  },
};
