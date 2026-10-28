import type { S3Client } from "@aws-sdk/client-s3";
import { MockActivityEnvironment } from "@temporalio/testing";
import { describe, expect, test } from "vitest";
import { createActivities, userBucketName } from "./activities.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";
const BUCKET = `squint-u-${USER_ID}`;

type Command = { constructor: { name: string }; input: Record<string, unknown> };
type Handler = (input: Record<string, unknown>) => unknown;

function s3Error(name: string) {
  return Object.assign(new Error(name), { name });
}

/** Records each command sent and answers with the handler for its type, or an empty response. */
function fakeS3(handlers: Record<string, Handler> = {}) {
  const sent: { command: string; input: Record<string, unknown> }[] = [];
  const client = {
    config: {},
    async send(command: Command) {
      const name = command.constructor.name;
      sent.push({ command: name, input: command.input });
      return (await handlers[name]?.(command.input)) ?? {};
    },
  };
  return { client: client as unknown as S3Client, sent };
}

function run<A extends unknown[], R>(fn: (...args: A) => Promise<R>, ...args: A) {
  return new MockActivityEnvironment().run(fn, ...args);
}

test("bucket names are valid S3 bucket names", () => {
  const name = userBucketName(USER_ID);
  expect(name).toBe(BUCKET);
  expect(name).toMatch(/^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$/);
});

describe("createUserBucket", () => {
  test("creates the user's bucket", async () => {
    const s3 = fakeS3();
    await run(createActivities(s3.client).createUserBucket, USER_ID);
    expect(s3.sent).toEqual([{ command: "CreateBucketCommand", input: { Bucket: BUCKET } }]);
  });

  test("succeeds when the bucket already exists", async () => {
    const s3 = fakeS3({
      CreateBucketCommand: () => {
        throw s3Error("BucketAlreadyOwnedByYou");
      },
    });
    await expect(
      run(createActivities(s3.client).createUserBucket, USER_ID),
    ).resolves.toBeUndefined();
  });

  test("fails on other errors", async () => {
    const s3 = fakeS3({
      CreateBucketCommand: () => {
        throw s3Error("AccessDenied");
      },
    });
    await expect(run(createActivities(s3.client).createUserBucket, USER_ID)).rejects.toThrow(
      "AccessDenied",
    );
  });
});

describe("deleteUserBucket", () => {
  test("aborts uploads, deletes every page of objects, then the bucket", async () => {
    const s3 = fakeS3({
      ListMultipartUploadsCommand: ({ KeyMarker }) =>
        KeyMarker
          ? { Uploads: [{ Key: "b", UploadId: "2" }], IsTruncated: false }
          : {
              Uploads: [{ Key: "a", UploadId: "1" }],
              IsTruncated: true,
              NextKeyMarker: "a",
              NextUploadIdMarker: "1",
            },
      ListObjectsV2Command: ({ ContinuationToken }) =>
        ContinuationToken
          ? { Contents: [{ Key: "c" }], IsTruncated: false }
          : {
              Contents: [{ Key: "a" }, { Key: "b" }],
              IsTruncated: true,
              NextContinuationToken: "t",
            },
    });

    await run(createActivities(s3.client).deleteUserBucket, USER_ID);

    expect(s3.sent.map(({ command }) => command)).toEqual([
      "ListMultipartUploadsCommand",
      "AbortMultipartUploadCommand",
      "ListMultipartUploadsCommand",
      "AbortMultipartUploadCommand",
      "ListObjectsV2Command",
      "DeleteObjectsCommand",
      "ListObjectsV2Command",
      "DeleteObjectsCommand",
      "DeleteBucketCommand",
    ]);
    const deleted = s3.sent
      .filter(({ command }) => command === "DeleteObjectsCommand")
      .map(({ input }) => input.Delete);
    expect(deleted).toEqual([
      { Objects: [{ Key: "a" }, { Key: "b" }], Quiet: true },
      { Objects: [{ Key: "c" }], Quiet: true },
    ]);
    expect(s3.sent.at(-1)?.input).toEqual({ Bucket: BUCKET });
  });

  test("succeeds when the bucket doesn't exist", async () => {
    const s3 = fakeS3({
      ListMultipartUploadsCommand: () => {
        throw s3Error("NoSuchBucket");
      },
    });
    await expect(
      run(createActivities(s3.client).deleteUserBucket, USER_ID),
    ).resolves.toBeUndefined();
    expect(s3.sent).toHaveLength(1);
  });

  test("fails when some objects couldn't be deleted", async () => {
    const s3 = fakeS3({
      ListObjectsV2Command: () => ({ Contents: [{ Key: "a" }], IsTruncated: false }),
      DeleteObjectsCommand: () => ({
        Errors: [{ Key: "a", Code: "AccessDenied", Message: "Access Denied" }],
      }),
    });
    await expect(run(createActivities(s3.client).deleteUserBucket, USER_ID)).rejects.toThrow(
      "a: AccessDenied",
    );
    expect(s3.sent.map(({ command }) => command)).not.toContain("DeleteBucketCommand");
  });
});
