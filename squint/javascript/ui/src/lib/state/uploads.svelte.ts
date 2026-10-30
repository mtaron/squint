import { MAX_CONCURRENT_UPLOADS, fileProblem, isPdfName } from "#lib/upload-limits.ts";

const SKIPPED_NAMES_SHOWN = 3;

export interface QueuedUpload {
  id: string;
  name: string;
  size: number;
  status: "queued" | "uploading" | "failed";
  /** Released once the upload settles */
  file?: File;
  problems: string[];
}

function skippedMessage(names: string[]): string {
  const shown = names.slice(0, SKIPPED_NAMES_SHOWN).join(", ");
  const more = names.length - SKIPPED_NAMES_SHOWN;
  const list = more > 0 ? `${shown} and ${more} more` : shown;
  return `Skipped ${names.length} files that aren't PDFs: ${list}.`;
}

/** Files waiting to upload, uploading, or rejected, uploading a few at a time. */
export class UploadQueue {
  items: QueuedUpload[] = $state([]);
  #limit: number;

  constructor(limit = MAX_CONCURRENT_UPLOADS) {
    this.#limit = limit;
  }

  get uploading(): QueuedUpload[] {
    return this.items.filter((item) => item.status === "uploading");
  }

  add(files: Iterable<File>): void {
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

  #startNext(): void {
    let uploading = this.uploading.length;
    for (const item of this.items) {
      if (uploading >= this.#limit) {
        return;
      }
      if (item.status === "queued") {
        item.status = "uploading";
        uploading += 1;
      }
    }
  }
}
