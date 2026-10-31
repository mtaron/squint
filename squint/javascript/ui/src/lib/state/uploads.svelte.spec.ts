import { describe, expect, test } from "vitest";
import { UploadQueue, retriedBy } from "./uploads.svelte.ts";

const pdf = (name: string) => new File(["%PDF-1.7"], name);

const statuses = (queue: UploadQueue) => queue.items.map(({ name, status }) => `${name} ${status}`);

describe("UploadQueue", () => {
  test("uploads at most three files at a time", () => {
    const queue = new UploadQueue();
    queue.add(["a", "b", "c", "d", "e"].map((name) => pdf(`${name}.pdf`)));

    expect(statuses(queue)).toEqual([
      "a.pdf uploading",
      "b.pdf uploading",
      "c.pdf uploading",
      "d.pdf queued",
      "e.pdf queued",
    ]);
  });

  test("starts the next file when an upload settles", () => {
    const queue = new UploadQueue();
    queue.add(["a", "b", "c", "d", "e"].map((name) => pdf(`${name}.pdf`)));
    const [a, b] = queue.items;

    queue.settle(a.id, []);
    queue.settle(b.id, ["Already uploaded as b-copy.pdf, so it was skipped."]);

    expect(statuses(queue)).toEqual([
      "b.pdf failed",
      "c.pdf uploading",
      "d.pdf uploading",
      "e.pdf uploading",
    ]);
    expect(queue.items[0].file).toBeUndefined();
  });

  test("replaces a failed upload when a file with the same name is added", () => {
    const queue = new UploadQueue();
    queue.add([pdf("a.pdf"), pdf("b.pdf")]);
    const [a, b] = queue.items;
    queue.settle(a.id, ["The upload failed. Try again."]);
    queue.settle(b.id, ["The upload failed. Try again."]);

    queue.add([pdf("a.pdf")]);

    expect(statuses(queue)).toEqual(["b.pdf failed", "a.pdf uploading"]);
  });

  test("leaves uploads in progress alone when the same name is added again", () => {
    const queue = new UploadQueue();
    queue.add([pdf("a.pdf")]);

    queue.add([pdf("a.pdf")]);

    expect(statuses(queue)).toEqual(["a.pdf uploading", "a.pdf uploading"]);
  });

  test("rejects empty files without uploading them", () => {
    const queue = new UploadQueue();
    queue.add([new File([], "blank.pdf")]);

    expect(statuses(queue)).toEqual(["blank.pdf failed"]);
    expect(queue.items[0].problems).toEqual(["This PDF is empty, so it was skipped."]);
  });

  test("summarizes files that aren't PDFs and ignores hidden files", () => {
    const queue = new UploadQueue();
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

  test("dismisses a row", () => {
    const queue = new UploadQueue();
    queue.add([new File([], "blank.pdf")]);
    queue.dismiss(queue.items[0].id);

    expect(queue.items).toEqual([]);
  });
});

describe("retriedBy", () => {
  test("finds the failures that the new files retry, by name", () => {
    const failures = [{ name: "a.pdf" }, { name: "b.pdf" }];

    expect(retriedBy(failures, [pdf("b.pdf"), pdf("c.pdf")])).toEqual([{ name: "b.pdf" }]);
  });
});
