import { isDocumentId, pageImageKey, thumbnailKey, userBucketName } from "@squint/db/storage";
import type { ObjectStorage } from "#lib/server/s3.ts";

const PAGE_NUMBER = /^[1-9]\d{0,3}$/;
const notFound = () => new Response(null, { status: 404 });

interface PageObject {
  key: (documentId: string, pageNumber: number) => string;
  contentType: string;
}

export const pageImage: PageObject = { key: pageImageKey, contentType: "image/jpeg" };
export const thumbnail: PageObject = { key: thumbnailKey, contentType: "image/webp" };

/**
 * Streams a page's image from the user's own bucket, so whether the document is theirs is settled
 * by the object being there. A document's images never change, so browsers can keep them.
 */
export async function servePageObject(
  storage: Pick<ObjectStorage, "get">,
  object: PageObject,
  userId: string | undefined,
  { id, page }: { id: string; page: string },
): Promise<Response> {
  if (!userId) {
    return new Response(null, { status: 401 });
  }
  if (!isDocumentId(id) || !PAGE_NUMBER.test(page)) {
    return notFound();
  }
  const stored = await storage.get(userBucketName(userId), object.key(id, Number(page)));
  if (!stored) {
    return notFound();
  }
  const headers = new Headers({
    "Content-Type": object.contentType,
    "Cache-Control": "private, max-age=31536000, immutable",
  });
  if (stored.contentLength !== undefined) {
    headers.set("Content-Length", String(stored.contentLength));
  }
  if (stored.etag) {
    headers.set("ETag", stored.etag);
  }
  return new Response(stored.body, { headers });
}
