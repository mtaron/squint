import { page } from "vitest/browser";
import { describe, expect, it } from "vitest";
import { render } from "vitest-browser-svelte";
import { UploadQueue } from "#lib/uploads/uploader.svelte.ts";
import DropZone from "./DropZone.svelte";

function dragEvent(type: string) {
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(new File(["%PDF-"], "a.pdf"));
  return new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer });
}

describe("DropZone.svelte", () => {
  it("explains what to drop and offers file and folder pickers", async () => {
    render(DropZone, { variant: "first-run", queue: new UploadQueue("?/upload", () => {}) });

    await expect.element(page.getByRole("heading", { name: "Drop your PDFs here" })).toBeVisible();
    await expect.element(page.getByText("Choose files")).toBeVisible();
    await expect.element(page.getByText("Choose a folder")).toBeVisible();
    expect(document.querySelector("input[webkitdirectory]")).not.toBeNull();
  });

  it("highlights while files are dragged over it", async () => {
    const { container } = render(DropZone, {
      variant: "compact",
      queue: new UploadQueue("?/upload", () => {}),
    });
    const form = container.querySelector("form")!;

    form.dispatchEvent(dragEvent("dragenter"));
    await expect.element(form).toHaveClass("dragging");

    form.dispatchEvent(dragEvent("dragleave"));
    await expect.element(form).not.toHaveClass("dragging");
  });
});
