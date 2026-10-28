import { describe, expect, it } from "vitest";
import { MAX_PDF_BYTES } from "./limits.ts";
import { scanSelection, type SelectedFile } from "./scan.ts";

function selected(path: string, size = 10): SelectedFile {
  const file = new File(["x"], path.split("/").pop() ?? path);
  Object.defineProperty(file, "size", { value: size });
  return { file, path };
}

describe("scanSelection", () => {
  it("keeps PDFs and archives from a corpus folder and reports the rest", () => {
    const scan = scanSelection([
      selected("corpus/report.pdf"),
      selected("corpus/appendix/Annex.PDF"),
      selected("corpus/README.md"),
      selected("corpus/images/logo.png"),
      selected("corpus/chart.svg"),
      selected("corpus/more.tar.gz"),
      selected("corpus/.DS_Store"),
    ]);

    expect(scan.uploads.map(({ path, kind }) => [path, kind])).toEqual([
      ["corpus/report.pdf", "pdf"],
      ["corpus/appendix/Annex.PDF", "pdf"],
      ["corpus/more.tar.gz", "tar.gz"],
    ]);
    expect(scan.skipped).toEqual([
      "corpus/README.md",
      "corpus/images/logo.png",
      "corpus/chart.svg",
    ]);
    expect(scan.tooLarge).toEqual([]);
  });

  it("flags PDFs over the size limit before uploading them", () => {
    const scan = scanSelection([selected("huge.pdf", MAX_PDF_BYTES + 1), selected("ok.pdf")]);

    expect(scan.uploads.map(({ path }) => path)).toEqual(["ok.pdf"]);
    expect(scan.tooLarge).toEqual(["huge.pdf"]);
  });
});
