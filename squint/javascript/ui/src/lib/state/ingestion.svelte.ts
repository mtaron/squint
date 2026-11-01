import { createContext } from "svelte";
import { SvelteSet } from "svelte/reactivity";
import { ingestStatus } from "#lib/documents.remote.ts";
import { ingestErrorMessage } from "#lib/ingest.ts";
import { retriedBy, UploadQueue } from "#lib/state/uploads.svelte.ts";
import { sendUpload } from "#lib/uploads.ts";

/** What's on its way into the library, which carries on whichever page is showing. */
export class Ingestion {
  queue = new UploadQueue(sendUpload);
  #live = ingestStatus();
  #dismissed = new SvelteSet<string>();

  statuses = $derived(this.#live.current ?? {});
  // A document that fails ingestion is deleted, so its row comes from its status until dismissed
  failures = $derived(
    Object.entries(this.statuses)
      .filter(([id, { latest }]) => latest.state === "failed" && !this.#dismissed.has(id))
      .map(([id, { name, sizeBytes, latest }]) => ({
        id,
        name,
        sizeBytes,
        error: ingestErrorMessage(latest.error),
      })),
  );

  upload(files: File[]) {
    for (const { id } of retriedBy(this.failures, files)) {
      this.#dismissed.add(id);
    }
    this.queue.add(files);
  }

  dismiss(id: string) {
    this.queue.dismiss(id);
    this.#dismissed.add(id);
  }

  /** Forgets this session, so none of it shows for the next account to sign in here. */
  clear() {
    this.queue.clear();
    for (const id of Object.keys(this.statuses)) {
      this.#dismissed.add(id);
    }
  }
}

export const [getIngestion, setIngestion] = createContext<Ingestion>();
