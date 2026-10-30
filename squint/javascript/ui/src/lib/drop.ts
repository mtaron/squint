function isFile(entry: FileSystemEntry): entry is FileSystemFileEntry {
  return entry.isFile;
}

function isDirectory(entry: FileSystemEntry): entry is FileSystemDirectoryEntry {
  return entry.isDirectory;
}

async function readAllEntries(directory: FileSystemDirectoryEntry): Promise<FileSystemEntry[]> {
  const reader = directory.createReader();
  const entries: FileSystemEntry[] = [];
  // readEntries returns the directory in batches, then an empty one
  for (;;) {
    const batch = await new Promise<FileSystemEntry[]>((resolve, reject) =>
      reader.readEntries(resolve, reject),
    );
    if (batch.length === 0) {
      return entries;
    }
    entries.push(...batch);
  }
}

async function filesIn(entry: FileSystemEntry): Promise<File[]> {
  if (isFile(entry)) {
    return [await new Promise<File>((resolve, reject) => entry.file(resolve, reject))];
  }
  if (isDirectory(entry)) {
    const children = await readAllEntries(entry);
    return (await Promise.all(children.map(filesIn))).flat();
  }
  return [];
}

export function isFileDrag(event: DragEvent): boolean {
  return event.dataTransfer?.types.includes("Files") ?? false;
}

/** The dropped files, including everything inside dropped folders. */
export async function droppedFiles(transfer: DataTransfer): Promise<File[]> {
  // The entries are only available synchronously, during the drop event
  const entries = [...transfer.items]
    .map((item) => item.webkitGetAsEntry())
    .filter((entry) => entry !== null);
  if (entries.length === 0) {
    return [...transfer.files];
  }
  return (await Promise.all(entries.map(filesIn))).flat();
}
