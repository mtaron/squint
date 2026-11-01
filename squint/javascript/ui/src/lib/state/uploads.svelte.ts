import { MAX_CONCURRENT_UPLOADS, fileProblem, isPdfName } from "#lib/upload-limits.ts";

const SKIPPED_NAMES_SHOWN = 3;

export interface QueuedUpload {
  id: string;
  name: string;
  size: number;
  loaded: number;
  status: "queued" | "uploading" | "failed";
  /** Released once the upload settles */
  file?: File;
  problems: string[];
}

/** Sends a file, resolving to what stopped it from being added, if anything. */
export type SendUpload = (file: File, onProgress: (loaded: number) => void) => Promise<string[]>;

function skippedMessage(names: string[]): string {
  const shown = names.slice(0, SKIPPED_NAMES_SHOWN).join(", ");
  const more = names.length - SKIPPED_NAMES_SHOWN;
  const list = more > 0 ? `${shown} and ${more} more` : shown;
  return `Skipped ${names.length} files that aren't PDFs: ${list}.`;
}

/** The failures that uploading `files` tries again. A fixed file is often not the same size. */
export function retriedBy<Failure extends { name: string }>(
  failures: Failure[],
  files: Iterable<{ name: string }>,
): Failure[] {
  const names = new Set(Array.from(files, ({ name }) => name));
  return failures.filter(({ name }) => names.has(name));
}

/** Files waiting to upload, uploading, or rejected, uploading a few at a time. */
export class UploadQueue {
  items: QueuedUpload[] = $state([]);
  #send: SendUpload;
  #limit: number;

  constructor(send: SendUpload, limit = MAX_CONCURRENT_UPLOADS) {
    this.#send = send;
    this.#limit = limit;
  }

  get uploading(): QueuedUpload[] {
    return this.items.filter((item) => item.status === "uploading");
  }

  add(files: File[]): void {
    const failed = this.items.filter((item) => item.status === "failed");
    const retried = new Set(retriedBy(failed, files));
    this.items = this.items.filter((item) => !retried.has(item));

    const notPdfs: string[] = [];
    for (const file of files) {
      // Folders carry hidden files like .DS_Store that nobody chose to upload
      if (file.name.startsWith(".")) {
        continue;
      }
      if (!isPdfName(file.name)) {
        notPdfs.push(file.name);
        continue;
      }
      const problem = fileProblem(file);
      this.items.push({
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        loaded: 0,
        ...(problem
          ? { status: "failed", problems: [problem] }
          : { status: "queued", file, problems: [] }),
      });
    }

    if (notPdfs.length > 0) {
      this.items.push({
        id: crypto.randomUUID(),
        name: notPdfs.length === 1 ? notPdfs[0] : `${notPdfs.length} files`,
        size: 0,
        loaded: 0,
        status: "failed",
        problems: [
          notPdfs.length === 1
            ? (fileProblem({ name: notPdfs[0], size: 0 }) ?? "")
            : skippedMessage(notPdfs),
        ],
      });
    }
    this.#startNext();
  }

  /** Records how an upload went. Successful uploads leave the queue for the document list. */
  settle(id: string, problems: string[]): void {
    const index = this.items.findIndex((item) => item.id === id);
    if (index === -1) {
      return;
    }
    if (problems.length === 0) {
      this.items.splice(index, 1);
    } else {
      Object.assign(this.items[index], { status: "failed", file: undefined, problems });
    }
    this.#startNext();
  }

  dismiss(id: string): void {
    this.items = this.items.filter((item) => item.id !== id);
  }

  clear(): void {
    this.items = [];
  }

  #startNext(): void {
    let uploading = this.uploading.length;
    for (const item of this.items) {
      if (uploading >= this.#limit) {
        return;
      }
      if (item.status === "queued" && item.file) {
        item.status = "uploading";
        uploading += 1;
        void this.#upload(item, item.file);
      }
    }
  }

  async #upload(item: QueuedUpload, file: File): Promise<void> {
    try {
      this.settle(
        item.id,
        await this.#send(file, (loaded) => {
          item.loaded = loaded;
        }),
      );
    } catch {
      this.settle(item.id, ["The upload failed. Try again."]);
    }
  }
}
