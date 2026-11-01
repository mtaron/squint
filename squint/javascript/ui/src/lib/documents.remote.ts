import { isDocumentId } from "@squint/db/storage";
import { error } from "@sveltejs/kit";
import * as v from "valibot";
import { getRequestEvent, query } from "$app/server";
import type { DocumentIngestion } from "#lib/ingest.ts";
import type { AnnouncedDocument } from "#lib/server/document-store.ts";
import { documentsBeingIngested, documentWithPages, listDocuments } from "#lib/server/documents.ts";
import { followIngestion } from "#lib/server/ingest-status.ts";
import { Changes, channels, subscribe } from "#lib/server/user-events.ts";

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

export const getDocumentPages = query(v.string(), async (id) => {
  const document = isDocumentId(id) ? await documentWithPages(requireUser().id, id) : undefined;
  if (!document) {
    error(404, "This document doesn't exist.");
  }
  return document;
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
