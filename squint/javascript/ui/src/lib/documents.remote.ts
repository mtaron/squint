import { isDocumentId } from "@squint/db/storage";
import { error } from "@sveltejs/kit";
import * as v from "valibot";
import { command, getRequestEvent, query } from "$app/server";
import type { DocumentIngestion } from "#lib/ingest.ts";
import { isFinalSearchEvent, MAX_QUERY_LENGTH, type SearchEvent } from "#lib/search.ts";
import type { AnnouncedDocument } from "#lib/server/document-store.ts";
import {
  documents,
  documentsBeingIngested,
  documentWithPages,
  listDocuments,
} from "#lib/server/documents.ts";
import { followIngestion } from "#lib/server/ingest-status.ts";
import { followSearch } from "#lib/server/search.ts";
import { Changes, channels, subscribe } from "#lib/server/user-events.ts";

// Keeps one delete within a single query's parameter limit
const MAX_DOCUMENTS_PER_DELETE = 10_000;

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

export const deleteDocuments = command(
  v.pipe(
    v.array(v.pipe(v.string(), v.check(isDocumentId))),
    v.minLength(1),
    v.maxLength(MAX_DOCUMENTS_PER_DELETE),
  ),
  async (ids) => {
    await documents.delete(requireUser().id, ids);
    void getDocuments().refresh();
  },
);

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

/** A search of all the user's pages, or one document's, as its results come in. */
export const search = query.live(
  v.object({
    query: v.pipe(v.string(), v.trim(), v.minLength(1), v.maxLength(MAX_QUERY_LENGTH)),
    documentId: v.optional(v.pipe(v.string(), v.check(isDocumentId))),
  }),
  async function* ({ query, documentId }) {
    const user = requireUser();
    const lifetime = liveQueryLifetime();
    let latest: SearchEvent = { state: "searching", pages: [] };
    const changes = new Changes();

    void followSearch(
      { userId: user.id, query, documentId },
      (event) => {
        latest = event;
        changes.notify();
      },
      lifetime.signal,
    );

    try {
      while (!lifetime.signal.aborted) {
        // `latest` can move on while the yield waits for the client, so check the one it sent
        const sent = latest;
        yield sent;
        if (isFinalSearchEvent(sent)) {
          return;
        }
        await changes.next(lifetime.signal);
      }
    } finally {
      lifetime.end();
    }
  },
);
