import {
  classifyName,
  isSystemFile,
  MAX_PDF_BYTES,
  MAX_REQUEST_BYTES,
  type FileKind,
} from "./limits.ts";

export type SelectedFile = { file: File; path: string };
export type UploadableFile = SelectedFile & { kind: FileKind };

export type Scan = {
  uploads: UploadableFile[];
  skipped: string[];
  tooLarge: string[];
};

/** Sorts a selection into PDFs and archives to upload, and everything else to report. */
export function scanSelection(selection: Iterable<SelectedFile>): Scan {
  const scan: Scan = { uploads: [], skipped: [], tooLarge: [] };
  for (const selected of selection) {
    if (isSystemFile(selected.path)) continue;
    const kind = classifyName(selected.path);
    if (!kind) {
      scan.skipped.push(selected.path);
    } else if (selected.file.size > (kind === "pdf" ? MAX_PDF_BYTES : MAX_REQUEST_BYTES)) {
      scan.tooLarge.push(selected.path);
    } else {
      scan.uploads.push({ ...selected, kind });
    }
  }
  return scan;
}

/** Files chosen with a file input, keeping their path within a chosen folder. */
export function inputSelection(files: FileList): SelectedFile[] {
  return [...files].map((file) => ({ file, path: file.webkitRelativePath || file.name }));
}

/** Files and the contents of folders dropped onto the page. */
export async function dropSelection(items: DataTransferItemList): Promise<SelectedFile[]> {
  // Entries must be taken synchronously, before the drop event's data store is cleared
  const entries = [...items]
    .map((item) => item.webkitGetAsEntry())
    .filter((entry): entry is FileSystemEntry => entry !== null);
  const selected: SelectedFile[] = [];
  for (const entry of entries) await collect(entry, selected);
  return selected;
}

async function collect(entry: FileSystemEntry, into: SelectedFile[]): Promise<void> {
  if (isFile(entry)) {
    const file = await new Promise<File>((resolve, reject) => entry.file(resolve, reject));
    into.push({ file, path: entry.fullPath.replace(/^\//, "") });
  } else if (isDirectory(entry)) {
    for (const child of await readAll(entry.createReader())) await collect(child, into);
  }
}

// readEntries returns at most 100 entries per call
async function readAll(reader: FileSystemDirectoryReader): Promise<FileSystemEntry[]> {
  const all: FileSystemEntry[] = [];
  while (true) {
    const batch = await new Promise<FileSystemEntry[]>((resolve, reject) =>
      reader.readEntries(resolve, reject),
    );
    if (batch.length === 0) return all;
    all.push(...batch);
  }
}

function isFile(entry: FileSystemEntry): entry is FileSystemFileEntry {
  return entry.isFile;
}

function isDirectory(entry: FileSystemEntry): entry is FileSystemDirectoryEntry {
  return entry.isDirectory;
}
