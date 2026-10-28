import type { IngestError } from "./documents.ts";
import { MAX_PDF_PAGES } from "./limits.ts";

export const ingestErrorCopy: Record<IngestError, { title: string; remedy: string }> = {
  password_protected: {
    title: "This PDF is password-protected.",
    remedy: "Save a copy without the password, then replace this file with it.",
  },
  unsupported_security: {
    title: "This PDF uses encryption squint can't open.",
    remedy: "Save an unencrypted copy, then replace this file with it.",
  },
  unreadable: {
    title: "This PDF couldn't be opened. It may be damaged or incomplete.",
    remedy: "Download or export it again, then replace this file.",
  },
  too_many_pages: {
    title: `This PDF has more than ${MAX_PDF_PAGES.toLocaleString("en")} pages.`,
    remedy: "Split it into smaller PDFs and upload those instead.",
  },
  internal: {
    title: "Something went wrong on our side while processing this PDF.",
    remedy: "Try again. If it keeps failing, the worker logs will say why.",
  },
};
