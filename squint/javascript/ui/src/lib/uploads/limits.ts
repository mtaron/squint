// Shared by the browser and the server; squint/python/apps/ingest/limits.py mirrors the page limit
const MB = 1024 * 1024;

export const MAX_PDF_BYTES = 500 * MB;
export const MAX_PDF_PAGES = 2000;
export const MAX_FILES_PER_REQUEST = 1000;
export const MAX_REQUEST_BYTES = 2048 * MB;
export const MAX_ARCHIVE_EXPANDED_BYTES = 2048 * MB;

export type FileKind = "pdf" | "zip" | "tar" | "tar.gz";

const systemFiles = /(^|\/)(__MACOSX\/|\._|\.DS_Store$)/;

/** macOS metadata that archivers and folder pickers include alongside the real files */
export function isSystemFile(path: string): boolean {
  return systemFiles.test(path);
}

export function classifyName(name: string): FileKind | undefined {
  if (isSystemFile(name)) return undefined;
  const lower = name.toLowerCase();
  if (lower.endsWith(".pdf")) return "pdf";
  if (lower.endsWith(".zip")) return "zip";
  if (lower.endsWith(".tar")) return "tar";
  if (lower.endsWith(".tar.gz") || lower.endsWith(".tgz")) return "tar.gz";
  return undefined;
}

export function baseName(path: string): string {
  return path.slice(path.lastIndexOf("/") + 1);
}
