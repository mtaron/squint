import {
  AbortMultipartUploadCommand,
  CreateBucketCommand,
  DeleteBucketCommand,
  DeleteObjectsCommand,
  ListMultipartUploadsCommand,
  ListObjectsV2Command,
  type S3Client,
} from "@aws-sdk/client-s3";
import { MockActivityEnvironment } from "@temporalio/testing";
import { describe, expect, test } from "vitest";
import { userBucketName } from "@squint/db/storage";
import { createActivities } from "./activities.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";
const BUCKET = userBucketName(USER_ID);
const PAGE_SIZE = 2;

interface Upload {
  Key: string;
  UploadId: string;
}

interface BucketContents {
  objects?: string[];
  uploads?: Upload[];
}

function s3Error(name: string) {
  return Object.assign(new Error(name), { name });
}

/**
 * An in-memory S3 that lists a few entries per page and, like S3, won't delete a bucket that still
 * holds objects or unfinished uploads.
 */
function fakeS3({
  buckets = {},
  undeletable = [],
  failWith,
}: {
  buckets?: Record<string, BucketContents>;
  undeletable?: string[];
  failWith?: string;
} = {}) {
  const store = new Map(
    Object.entries(buckets).map(([name, { objects = [], uploads = [] }]) => [
      name,
      { objects: new Set(objects), uploads: [...uploads] },
    ]),
  );

  function existing(name: string | undefined) {
    const bucket = store.get(name ?? "");
    if (!bucket) throw s3Error("NoSuchBucket");
    return bucket;
  }

  async function send(command: unknown): Promise<unknown> {
    if (failWith) throw s3Error(failWith);

    if (command instanceof CreateBucketCommand) {
      const { Bucket = "" } = command.input;
      if (store.has(Bucket)) throw s3Error("BucketAlreadyOwnedByYou");
      store.set(Bucket, { objects: new Set(), uploads: [] });
      return {};
    }
    if (command instanceof ListMultipartUploadsCommand) {
      const { Bucket, KeyMarker = "", UploadIdMarker = "" } = command.input;
      const after = existing(Bucket)
        .uploads.toSorted((a, b) =>
          `${a.Key}/${a.UploadId}`.localeCompare(`${b.Key}/${b.UploadId}`),
        )
        .filter(({ Key, UploadId }) => `${Key}/${UploadId}` > `${KeyMarker}/${UploadIdMarker}`);
      const Uploads = after.slice(0, PAGE_SIZE);
      const last = Uploads.at(-1);
      return {
        Uploads,
        IsTruncated: after.length > PAGE_SIZE,
        NextKeyMarker: last?.Key,
        NextUploadIdMarker: last?.UploadId,
      };
    }
    if (command instanceof AbortMultipartUploadCommand) {
      const { Bucket, Key, UploadId } = command.input;
      const bucket = existing(Bucket);
      bucket.uploads = bucket.uploads.filter((u) => u.Key !== Key || u.UploadId !== UploadId);
      return {};
    }
    if (command instanceof ListObjectsV2Command) {
      const { Bucket, Prefix = "", ContinuationToken = "" } = command.input;
      const after = [...existing(Bucket).objects]
        .filter((key) => key.startsWith(Prefix) && key > ContinuationToken)
        .toSorted();
      const Contents = after.slice(0, PAGE_SIZE).map((Key) => ({ Key }));
      return {
        Contents,
        IsTruncated: after.length > PAGE_SIZE,
        NextContinuationToken: Contents.at(-1)?.Key,
      };
    }
    if (command instanceof DeleteObjectsCommand) {
      const { Bucket, Delete } = command.input;
      const bucket = existing(Bucket);
      const Errors = [];
      for (const { Key = "" } of Delete?.Objects ?? []) {
        if (undeletable.includes(Key)) {
          Errors.push({ Key, Code: "AccessDenied", Message: "Access Denied" });
        } else {
          bucket.objects.delete(Key);
        }
      }
      return { Errors: Errors.length > 0 ? Errors : undefined };
    }
    if (command instanceof DeleteBucketCommand) {
      const { Bucket = "" } = command.input;
      const bucket = existing(Bucket);
      if (bucket.objects.size > 0 || bucket.uploads.length > 0) throw s3Error("BucketNotEmpty");
      store.delete(Bucket);
      return {};
    }
    throw new Error(`The fake S3 doesn't handle ${String(command)}`);
  }

  return {
    activities: createActivities({ config: {}, send } as unknown as S3Client),
    buckets: store,
    objects: (bucket: string) => [...existing(bucket).objects].toSorted(),
  };
}

function run<A extends unknown[], R>(fn: (...args: A) => Promise<R>, ...args: A) {
  return new MockActivityEnvironment().run(fn, ...args);
}

test("bucket names are valid S3 bucket names", () => {
  expect(userBucketName(USER_ID)).toMatch(/^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$/);
});

describe("createUserBucket", () => {
  test("creates the user's bucket", async () => {
    const s3 = fakeS3();

    await run(s3.activities.createUserBucket, USER_ID);

    expect(s3.buckets.has(BUCKET)).toBe(true);
  });

  test("succeeds when the bucket already exists", async () => {
    const s3 = fakeS3({ buckets: { [BUCKET]: {} } });

    await expect(run(s3.activities.createUserBucket, USER_ID)).resolves.toBeUndefined();
  });

  test("fails on other errors", async () => {
    const s3 = fakeS3({ failWith: "AccessDenied" });

    await expect(run(s3.activities.createUserBucket, USER_ID)).rejects.toThrow("AccessDenied");
  });
});

describe("deleteUserBucket", () => {
  test("deletes the bucket along with every object and unfinished upload in it", async () => {
    const s3 = fakeS3({
      buckets: {
        [BUCKET]: {
          objects: ["a", "b", "c", "d", "e"],
          uploads: [
            { Key: "f", UploadId: "1" },
            { Key: "f", UploadId: "2" },
            { Key: "g", UploadId: "3" },
          ],
        },
      },
    });

    await run(s3.activities.deleteUserBucket, USER_ID);

    expect(s3.buckets.has(BUCKET)).toBe(false);
  });

  test("succeeds when the bucket doesn't exist", async () => {
    const s3 = fakeS3();

    await expect(run(s3.activities.deleteUserBucket, USER_ID)).resolves.toBeUndefined();
  });

  test("fails, keeping the bucket, when some objects couldn't be deleted", async () => {
    const s3 = fakeS3({ buckets: { [BUCKET]: { objects: ["a", "b"] } }, undeletable: ["a"] });

    await expect(run(s3.activities.deleteUserBucket, USER_ID)).rejects.toThrow("a: AccessDenied");
    expect(s3.objects(BUCKET)).toEqual(["a"]);
  });
});

describe("deleteDocumentObjects", () => {
  test("deletes only the given documents' objects, leaving the bucket in place", async () => {
    const s3 = fakeS3({
      buckets: {
        [BUCKET]: {
          objects: [
            "documents/first/original.pdf",
            "documents/first/pages/1.jpg",
            "documents/first/pages/2.jpg",
            "documents/second/original.pdf",
            "documents/third/original.pdf",
            "documents/third/pages/1.jpg",
          ],
        },
      },
    });

    await run(s3.activities.deleteDocumentObjects, USER_ID, ["first", "second"]);

    expect(s3.objects(BUCKET)).toEqual([
      "documents/third/original.pdf",
      "documents/third/pages/1.jpg",
    ]);
  });

  test("succeeds when the bucket doesn't exist", async () => {
    const s3 = fakeS3();

    await expect(
      run(s3.activities.deleteDocumentObjects, USER_ID, ["first"]),
    ).resolves.toBeUndefined();
  });
});
