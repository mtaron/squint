/** Each user's documents live in their own bucket, created by the lifecycle worker. */
export function userBucketName(userId: string): string {
  return `squint-u-${userId}`;
}

export function documentObjectKey(documentId: string): string {
  return `documents/${documentId}.pdf`;
}
