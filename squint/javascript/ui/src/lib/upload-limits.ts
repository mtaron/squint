import * as v from "valibot";

const MB = 1024 ** 2;

export const MAX_PDF_BYTES = 500 * MB;
/** Enforced by the ingest worker, which is the first to open the PDF; named here in its messages */
export const MAX_PDF_PAGES = 2000;
export const MAX_FILES_PER_REQUEST = 1000;
export const MAX_REQUEST_BYTES = 2048 * MB;
export const MAX_CONCURRENT_UPLOADS = 3;

export const uploadSchema = v.object({
  files: v.pipe(
    v.array(v.file()),
    v.minLength(1, "Choose a PDF or a folder of PDFs to upload."),
    v.maxLength(
      MAX_FILES_PER_REQUEST,
      `Upload at most ${MAX_FILES_PER_REQUEST.toLocaleString("en")} files at a time.`,
    ),
    v.check(
      (files) => files.reduce((total, file) => total + file.size, 0) <= MAX_REQUEST_BYTES,
      "Upload at most 2 GB at a time.",
    ),
  ),
  uploadId: v.optional(v.pipe(v.string(), v.uuid())),
});

export function isPdfName(name: string): boolean {
  return name.toLowerCase().endsWith(".pdf");
}

/**
 * Why a file can't be uploaded, judged from what the browser knows before sending it. Shown next
 * to the file's name, so it doesn't repeat it.
 */
export function fileProblem(file: { name: string; size: number }): string | undefined {
  if (!isPdfName(file.name)) {
    return "This isn't a PDF. Only PDF files can be uploaded.";
  }
  if (file.size === 0) {
    return "This PDF is empty, so it was skipped.";
  }
  if (file.size > MAX_PDF_BYTES) {
    return "This PDF is larger than 500 MB, the most a single PDF can be.";
  }
  return undefined;
}
