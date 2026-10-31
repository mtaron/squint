import { describe, expect, test } from "vitest";
import type { ObjectStorage, StoredObject } from "#lib/server/s3.ts";
import { pageImage, servePageObject, thumbnail } from "./page-images.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";
const DOCUMENT_ID = "V3kQ9xTz2m";
const IMAGE = "image bytes";

function storageHolding(key: string): { storage: Pick<ObjectStorage, "get">; reads: string[] } {
  const reads: string[] = [];
  return {
    reads,
    storage: {
      async get(bucket, requested): Promise<StoredObject | undefined> {
        reads.push(`${bucket}/${requested}`);
        if (requested !== key) {
          return undefined;
        }
        return {
          body: new Response(IMAGE).body as ReadableStream<Uint8Array>,
          contentLength: IMAGE.length,
          etag: '"abc"',
        };
      },
    },
  };
}

const pageKey = (documentId: string, pageNumber: number) =>
  `documents/${documentId}/pages/${pageNumber}.jpg`;

describe("servePageObject", () => {
  test("streams the page from the signed-in user's bucket, cached for good", async () => {
    const { storage, reads } = storageHolding(pageKey(DOCUMENT_ID, 3));

    const response = await servePageObject(storage, pageImage, USER_ID, {
      id: DOCUMENT_ID,
      page: "3",
    });

    expect(response.status).toBe(200);
    expect(await response.text()).toBe(IMAGE);
    expect(response.headers.get("content-type")).toBe("image/jpeg");
    expect(response.headers.get("content-length")).toBe(String(IMAGE.length));
    expect(response.headers.get("etag")).toBe('"abc"');
    expect(response.headers.get("cache-control")).toBe("private, max-age=31536000, immutable");
    expect(reads).toEqual([`squint-u-${USER_ID}/${pageKey(DOCUMENT_ID, 3)}`]);
  });

  test("serves thumbnails as WebP", async () => {
    const { storage } = storageHolding(`documents/${DOCUMENT_ID}/thumbnails/3.webp`);

    const response = await servePageObject(storage, thumbnail, USER_ID, {
      id: DOCUMENT_ID,
      page: "3",
    });

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("image/webp");
  });

  test("requires a signed-in user", async () => {
    const { storage, reads } = storageHolding(pageKey(DOCUMENT_ID, 3));

    const response = await servePageObject(storage, pageImage, undefined, {
      id: DOCUMENT_ID,
      page: "3",
    });

    expect(response.status).toBe(401);
    expect(reads).toEqual([]);
  });

  test("reports a page that doesn't exist as not found", async () => {
    const { storage } = storageHolding(pageKey(DOCUMENT_ID, 3));

    const response = await servePageObject(storage, pageImage, USER_ID, {
      id: DOCUMENT_ID,
      page: "4",
    });

    expect(response.status).toBe(404);
  });

  test.each([
    { id: "../../other", page: "1" },
    { id: "short", page: "1" },
    { id: DOCUMENT_ID, page: "0" },
    { id: DOCUMENT_ID, page: "-1" },
    { id: DOCUMENT_ID, page: "1.5" },
    { id: DOCUMENT_ID, page: "1/../2" },
  ])("never reaches storage with a malformed path: $id $page", async (params) => {
    const { storage, reads } = storageHolding(pageKey(DOCUMENT_ID, 1));

    const response = await servePageObject(storage, pageImage, USER_ID, params);

    expect(response.status).toBe(404);
    expect(reads).toEqual([]);
  });
});
