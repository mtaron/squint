import { error, invalid } from "@sveltejs/kit";
import { form, getRequestEvent, query } from "$app/server";
import type { DocumentIngestion, UploadProgress } from "#lib/ingest.ts";
import type { AnnouncedDocument } from "#lib/server/document-store.ts";
import { documents, documentsBeingIngested, listDocuments } from "#lib/server/documents.ts";
import { followIngestion } from "#lib/server/ingest-status.ts";
import { Changes, channels, subscribe } from "#lib/server/user-events.ts";
import { uploadSchema } from "#lib/upload-limits.ts";

function requireUser() {
  const { user } = getRequestEvent().locals;
  if (!user) {
    error(401, "Sign in to see your documents.");
  }
  return user;
}

/** Aborts when the live query's request ends or its generator returns, whichever is first. */
function liveQueryLifetime() {
  const controller = new AbortController();
  const signal = AbortSignal.any([getRequestEvent().request.signal, controller.signal]);
  return { signal, end: () => controller.abort() };
}

export const getDocuments = query(() => listDocuments(requireUser().id));

export const uploadDocuments = form(uploadSchema, async ({ files, uploadId }, issue) => {
  const user = requireUser();
  const documentIds: string[] = [];
  const problems = [];
  for (const [index, file] of files.entries()) {
    const outcome = await documents.add(user.id, file, uploadId);
    if ("problem" in outcome) {
      // An upload with an id has its own row beside the file's name; without JavaScript the
      // problems are listed together, so they name the file
      const message = uploadId ? outcome.problem : `${file.name}: ${outcome.problem}`;
      problems.push(issue.files[index](message));
    } else {
      documentIds.push(outcome.documentId);
    }
  }

  void getDocuments().refresh();
  if (problems.length > 0) {
    invalid(...problems);
  }
  return { documentIds };
});

/** Bytes sent to S3 so far for each of the user's uploads, keyed by the client's upload id. */
export const uploadProgress = query.live(async function* () {
  const user = requireUser();
  const lifetime = liveQueryLifetime();
  const progress: Record<string, UploadProgress> = {};
  const changes = new Changes();
  try {
    await subscribe<UploadProgress>(
      channels.uploads(user.id),
      (update) => {
        progress[update.uploadId] = update;
        changes.notify();
      },
      lifetime.signal,
    );
    while (!lifetime.signal.aborted) {
      yield { ...progress };
      await changes.next(lifetime.signal);
    }
  } finally {
    lifetime.end();
  }
});

/**
 * The latest ingestion event for each document that was being ingested while the query was
 * connected. A document that fails ingestion is deleted, so this is all that's left of it.
 */
export const ingestStatus = query.live(async function* () {
  const user = requireUser();
  const lifetime = liveQueryLifetime();
  const statuses: Record<string, DocumentIngestion> = {};
  const changes = new Changes();

  function follow({ id, name, sizeBytes }: AnnouncedDocument) {
    if (id in statuses) {
      return;
    }
    statuses[id] = { name, sizeBytes, latest: { state: "validating" } };
    changes.notify();
    void followIngestion(
      id,
      (event) => {
        statuses[id] = { name, sizeBytes, latest: event };
        changes.notify();
      },
      lifetime.signal,
    );
  }

  try {
    // Subscribe before listing, so a document uploaded in between isn't missed
    await subscribe<AnnouncedDocument>(channels.documents(user.id), follow, lifetime.signal);
    for (const document of await documentsBeingIngested(user.id)) {
      follow(document);
    }
    while (!lifetime.signal.aborted) {
      yield { ...statuses };
      await changes.next(lifetime.signal);
    }
  } finally {
    lifetime.end();
  }
});
