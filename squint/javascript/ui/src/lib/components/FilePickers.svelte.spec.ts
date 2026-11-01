import { describe, expect, it, vi } from "vitest";
import { render } from "vitest-browser-svelte";
import FilePickers from "./FilePickers.svelte";

describe("FilePickers.svelte", () => {
  it("reports what was picked and clears the input, so the same file can be picked again", () => {
    const onfiles = vi.fn();
    const { container } = render(FilePickers, { onfiles });
    const picker = container.querySelector<HTMLInputElement>("input[accept]");
    const file = new File(["%PDF-1.7"], "a.pdf");
    const picks = new DataTransfer();
    picks.items.add(file);

    if (!picker) throw new Error("No file picker");
    picker.files = picks.files;
    picker.dispatchEvent(new Event("change", { bubbles: true }));

    expect(onfiles).toHaveBeenCalledOnce();
    expect(onfiles.mock.calls[0][0].map(({ name }: File) => name)).toEqual(["a.pdf"]);
    expect(picker.files?.length).toBe(0);
  });
});
