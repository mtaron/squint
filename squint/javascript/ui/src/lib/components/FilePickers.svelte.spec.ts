import { describe, expect, it, vi } from "vitest";
import { render } from "vitest-browser-svelte";
import FilePickers from "./FilePickers.svelte";

// Like the real field, `as` carries a `files` prop holding what was picked earlier
vi.mock("#lib/documents.remote.ts", () => {
  const earlierPicks = new DataTransfer();
  earlierPicks.items.add(new File(["%PDF-1.7"], "earlier.pdf"));
  return {
    uploadDocuments: {
      fields: {
        files: {
          as: () => ({ name: "files[]", type: "file", multiple: true, files: earlierPicks.files }),
        },
      },
    },
  };
});

describe("FilePickers.svelte", () => {
  it("keeps earlier picks out of the inputs, so they aren't uploaded again", async () => {
    const { container } = render(FilePickers, { onfiles: () => {} });
    await new Promise(requestAnimationFrame);

    const inputs = container.querySelectorAll<HTMLInputElement>('input[type="file"]');

    expect(inputs).toHaveLength(2);
    expect([...inputs].map(({ files }) => files?.length)).toEqual([0, 0]);
    expect([...inputs].map(({ name }) => name)).toEqual(["files[]", "files[]"]);
    expect([...inputs].every(({ multiple }) => multiple)).toBe(true);
  });
});
