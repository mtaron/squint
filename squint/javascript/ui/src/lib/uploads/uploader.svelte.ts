import { deserialize } from "$app/forms";
import { emptyOutcome, type UploadOutcome } from "./documents.ts";
import type { Scan, UploadableFile } from "./scan.ts";

const CONCURRENT_UPLOADS = 3;

export type ItemState = "queued" | "uploading" | "done" | "failed" | "cancelled";

class UploadCancelled extends Error {}

class UploadItem {
  state = $state<ItemState>("queued");
  sentBytes = $state(0);
  error = $state<string>();
  request?: XMLHttpRequest;

  constructor(readonly upload: UploadableFile) {}
}

/**
 * Posts each PDF or archive of a selection to the upload form action as its own request, a few
 * at a time, tracking progress across all of them.
 */
export class UploadQueue {
  items = $state<UploadItem[]>([]);
  outcome = $state<UploadOutcome>(emptyOutcome());
  scan = $state<Scan>();

  totalBytes = $derived(this.items.reduce((sum, item) => sum + item.upload.file.size, 0));
  sentBytes = $derived(this.items.reduce((sum, item) => sum + item.sentBytes, 0));
  running = $derived(this.items.some(({ state }) => state === "queued" || state === "uploading"));
  failures = $derived(this.items.filter(({ state }) => state === "failed"));

  #action: string;
  #onUploaded: () => void;

  constructor(action: string, onUploaded: () => void) {
    this.#action = action;
    this.#onUploaded = onUploaded;
  }

  start(scan: Scan) {
    this.scan = scan;
    this.outcome = emptyOutcome();
    this.items = scan.uploads.map((upload) => new UploadItem(upload));
    for (let worker = 0; worker < CONCURRENT_UPLOADS; worker++) void this.#work();
  }

  cancel() {
    for (const item of this.items) {
      if (item.state === "queued" || item.state === "uploading") {
        item.request?.abort();
        item.state = "cancelled";
      }
    }
  }

  clear() {
    this.cancel();
    this.items = [];
    this.scan = undefined;
    this.outcome = emptyOutcome();
  }

  async #work() {
    while (true) {
      const item = this.items.find(({ state }) => state === "queued");
      if (!item) return;
      item.state = "uploading";
      try {
        const outcome = await this.#send(item);
        this.#merge(outcome);
        item.state = "done";
        if (outcome.added.length > 0) this.#onUploaded();
      } catch (error) {
        if (error instanceof UploadCancelled) continue;
        item.state = "failed";
        item.error = error instanceof Error ? error.message : String(error);
      }
    }
  }

  #merge(outcome: UploadOutcome) {
    this.outcome.added.push(...outcome.added);
    this.outcome.duplicates.push(...outcome.duplicates);
    this.outcome.skipped.push(...outcome.skipped);
    this.outcome.rejected.push(...outcome.rejected);
  }

  #send(item: UploadItem): Promise<UploadOutcome> {
    const { file, path } = item.upload;
    const body = new FormData();
    body.append("files", file, path);
    return new Promise((resolve, reject) => {
      const request = new XMLHttpRequest();
      item.request = request;
      request.open("POST", this.#action);
      request.setRequestHeader("accept", "application/json");
      request.setRequestHeader("x-sveltekit-action", "true");
      request.upload.onprogress = (event) => (item.sentBytes = event.loaded);
      request.onload = () => {
        item.sentBytes = file.size;
        const result = deserialize<{ outcome: UploadOutcome }, { message: string }>(
          request.responseText,
        );
        if (result.type === "success" && result.data) resolve(result.data.outcome);
        else if (result.type === "failure") reject(new Error(result.data?.message));
        else if (result.type === "error")
          reject(new Error(result.error?.message ?? "Upload failed"));
        else reject(new Error("Upload failed"));
      };
      request.onerror = () => reject(new Error("The connection was lost during the upload."));
      request.onabort = () => reject(new UploadCancelled());
      request.send(body);
    });
  }
}
