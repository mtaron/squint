const MB = 1024 ** 2;

export const MAX_PDF_BYTES = 500 * MB;
/** Enforced by the ingest worker, which is the first to open the PDF; named here in its messages */
export const MAX_PDF_PAGES = 2000;
export const MAX_CONCURRENT_UPLOADS = 3;

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
