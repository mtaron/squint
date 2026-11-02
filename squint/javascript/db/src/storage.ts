const DOCUMENT_ID_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
const DOCUMENT_ID_LENGTH = 10;
const DOCUMENT_ID_PATTERN = new RegExp(`^[${DOCUMENT_ID_ALPHABET}]{${DOCUMENT_ID_LENGTH}}$`);

/** Nano IDs in base58, so they are short and have no look-alike characters. */
export const documentIdFormat = { alphabet: DOCUMENT_ID_ALPHABET, length: DOCUMENT_ID_LENGTH };

export function isDocumentId(value: string): boolean {
  return DOCUMENT_ID_PATTERN.test(value);
}

/** Each user's documents live in their own bucket, created by the lifecycle worker. */
export function userBucketName(userId: string): string {
  return `squint-u-${userId}`;
}

// Mirrored in squint/python/packages/squint-core/src/squint_core/documents.py
export function documentPrefix(documentId: string): string {
  return `documents/${documentId}/`;
}

export function documentObjectKey(documentId: string): string {
  return `${documentPrefix(documentId)}original.pdf`;
}

export function pageImageKey(documentId: string, pageNumber: number): string {
  return `${documentPrefix(documentId)}pages/${pageNumber}.jpg`;
}

export function thumbnailKey(documentId: string, pageNumber: number): string {
  return `${documentPrefix(documentId)}thumbnails/${pageNumber}.webp`;
}
