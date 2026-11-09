import { describe, expect, test, vi } from "vitest";
import { UploadQueue, retriedBy } from "./uploads.svelte.ts";

const pdf = (name: string) => new File(["%PDF-1.7"], name);

const neverSettles = () => new Promise<string[]>(() => {});

const statuses = (queue: UploadQueue) => queue.items.map(({ name, status }) => `${name} ${status}`);

/** A send whose uploads stay in flight until the test finishes them, by file name. */
function controlledSend() {
  const sent: string[] = [];
  const pending = new Map<string, (problems: string[]) => void>();
  const send = (file: File) => {
    sent.push(file.name);
    return new Promise<string[]>((resolve) => pending.set(file.name, resolve));
  };
  async function finish(name: string, problems: string[] = []) {
    pending.get(name)?.(problems);
    pending.delete(name);
    await new Promise((resolve) => setTimeout(resolve));
  }
  return { send, sent, finish };
}

describe("UploadQueue", () => {
  test("uploads at most three files at a time", () => {
    const queue = new UploadQueue(neverSettles);
    queue.add(["a", "b", "c", "d", "e"].map((name) => pdf(`${name}.pdf`)));

    expect(statuses(queue)).toEqual([
      "a.pdf uploading",
      "b.pdf uploading",
      "c.pdf uploading",
      "d.pdf queued",
      "e.pdf queued",
    ]);
  });

  test("starts the next file whenever an upload settles, keeping only failures", async () => {
    const { send, sent, finish } = controlledSend();
    const queue = new UploadQueue(send);
    queue.add(["a", "b", "c", "d", "e"].map((name) => pdf(`${name}.pdf`)));

    await finish("a.pdf");
    await finish("b.pdf", ["Already uploaded as b-copy.pdf, so it was skipped."]);

    expect(sent).toEqual(["a.pdf", "b.pdf", "c.pdf", "d.pdf", "e.pdf"]);
    expect(statuses(queue)).toEqual([
      "b.pdf failed",
      "c.pdf uploading",
      "d.pdf uploading",
      "e.pdf uploading",
    ]);
  });

  test("replaces a failed upload when a file with the same name is added", async () => {
    const { send, finish } = controlledSend();
    const queue = new UploadQueue(send);
    queue.add([pdf("a.pdf"), pdf("b.pdf")]);
    await finish("a.pdf", ["The upload failed. Try again."]);
    await finish("b.pdf", ["The upload failed. Try again."]);

    queue.add([pdf("a.pdf")]);

    expect(statuses(queue)).toEqual(["b.pdf failed", "a.pdf uploading"]);
  });

  test("leaves uploads in progress alone when the same name is added again", () => {
    const queue = new UploadQueue(neverSettles);
    queue.add([pdf("a.pdf")]);

    queue.add([pdf("a.pdf")]);

    expect(statuses(queue)).toEqual(["a.pdf uploading", "a.pdf uploading"]);
  });

  test("fails empty files without sending them", () => {
    const send = vi.fn(neverSettles);
    const queue = new UploadQueue(send);

    queue.add([new File([], "blank.pdf")]);

    expect(statuses(queue)).toEqual(["blank.pdf failed"]);
    expect(send).not.toHaveBeenCalled();
  });

  test("summarizes files that aren't PDFs and ignores hidden files", () => {
    const queue = new UploadQueue(neverSettles);
    queue.add([
      pdf("a.pdf"),
      new File(["x"], ".DS_Store"),
      ...["1.txt", "2.png", "3.doc", "4.csv"].map((name) => new File(["x"], name)),
    ]);

    expect(statuses(queue)).toEqual(["a.pdf uploading", "4 files failed"]);
    expect(queue.items[1].problems).toEqual([
      "Skipped 4 files that aren't PDFs: 1.txt, 2.png, 3.doc and 1 more.",
    ]);
  });

  test("tracks how much of a file has been sent", () => {
    let report: (loaded: number) => void = () => {};
    const queue = new UploadQueue((_file, onProgress) => {
      report = onProgress;
      return neverSettles();
    });
    queue.add([pdf("a.pdf")]);

    report(5);

    expect(queue.items[0].loaded).toBe(5);
  });

  test("shows the problems a send reports", async () => {
    const queue = new UploadQueue(async () => [
      "Already uploaded as a-copy.pdf, so it was skipped.",
    ]);

    queue.add([pdf("a.pdf")]);

    await vi.waitFor(() => expect(statuses(queue)).toEqual(["a.pdf failed"]));
    expect(queue.items[0].problems).toEqual(["Already uploaded as a-copy.pdf, so it was skipped."]);
  });

  test("treats a send that throws as a failed upload", async () => {
    const queue = new UploadQueue(async () => {
      throw new TypeError("Failed to fetch");
    });

    queue.add([pdf("a.pdf")]);

    await vi.waitFor(() => expect(statuses(queue)).toEqual(["a.pdf failed"]));
  });

  test("forgets everything when cleared, including files that haven't been sent", async () => {
    const { send, sent, finish } = controlledSend();
    const queue = new UploadQueue(send, 1);
    queue.add([pdf("a.pdf"), pdf("b.pdf")]);

    queue.clear();
    await finish("a.pdf");

    expect(queue.items).toEqual([]);
    expect(sent).toEqual(["a.pdf"]);
  });
});

describe("retriedBy", () => {
  test("finds the failures that the new files retry, by name", () => {
    const failures = [{ name: "a.pdf" }, { name: "b.pdf" }];

    expect(retriedBy(failures, [pdf("b.pdf"), pdf("c.pdf")])).toEqual([{ name: "b.pdf" }]);
  });
});
