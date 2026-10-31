import type { S3Client } from "@aws-sdk/client-s3";
import { describe, expect, test } from "vitest";
import { s3Storage } from "./s3.ts";

function clientFailingWith(name: string) {
  return {
    async send() {
      throw Object.assign(new Error(name), { name });
    },
  } as unknown as S3Client;
}

describe("s3Storage.get", () => {
  test.each(["NoSuchKey", "NoSuchBucket"])("treats %s as a missing object", async (name) => {
    await expect(s3Storage(clientFailingWith(name)).get("bucket", "key")).resolves.toBeUndefined();
  });

  test("lets other failures through", async () => {
    await expect(s3Storage(clientFailingWith("SlowDown")).get("bucket", "key")).rejects.toThrow(
      "SlowDown",
    );
  });
});
