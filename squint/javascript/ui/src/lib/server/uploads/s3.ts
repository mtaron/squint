import { createHash } from "node:crypto";
import { PassThrough } from "node:stream";
import {
  CreateBucketCommand,
  DeleteObjectCommand,
  DeleteObjectsCommand,
  HeadBucketCommand,
  ListObjectsV2Command,
  S3Client,
  S3ServiceException,
} from "@aws-sdk/client-s3";
import { Upload } from "@aws-sdk/lib-storage";
import { AWS_ENDPOINT_URL, AWS_REGION } from "$app/env/private";
import type { CreateObjectWriter } from "./store.ts";

// The SDK reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY itself, and Node trusts the cluster CA
// through NODE_EXTRA_CA_CERTS
let client: S3Client | undefined;

export function getS3Client(): S3Client {
  client ??= new S3Client({ endpoint: AWS_ENDPOINT_URL, region: AWS_REGION, forcePathStyle: true });
  return client;
}

export function userBucket(userId: string): string {
  return `squint-u-${createHash("sha256").update(userId).digest("hex").slice(0, 32)}`;
}

const knownBuckets = new Set<string>();

export async function ensureUserBucket(userId: string): Promise<string> {
  const bucket = userBucket(userId);
  if (knownBuckets.has(bucket)) return bucket;
  const s3 = getS3Client();
  try {
    await s3.send(new HeadBucketCommand({ Bucket: bucket }));
  } catch (error) {
    if (!(error instanceof S3ServiceException) || error.$metadata.httpStatusCode !== 404) {
      throw error;
    }
    try {
      await s3.send(new CreateBucketCommand({ Bucket: bucket }));
    } catch (createError) {
      if (
        !(createError instanceof S3ServiceException) ||
        createError.name !== "BucketAlreadyOwnedByYou"
      ) {
        throw createError;
      }
    }
  }
  knownBuckets.add(bucket);
  return bucket;
}

export async function deleteObject(bucket: string, key: string): Promise<void> {
  await getS3Client().send(new DeleteObjectCommand({ Bucket: bucket, Key: key }));
}

export async function deletePrefix(bucket: string, prefix: string): Promise<void> {
  const s3 = getS3Client();
  let continuationToken: string | undefined;
  do {
    const page = await s3.send(
      new ListObjectsV2Command({
        Bucket: bucket,
        Prefix: prefix,
        ContinuationToken: continuationToken,
      }),
    );
    const objects = (page.Contents ?? []).map(({ Key }) => ({ Key }));
    if (objects.length > 0) {
      await s3.send(new DeleteObjectsCommand({ Bucket: bucket, Delete: { Objects: objects } }));
    }
    continuationToken = page.NextContinuationToken;
  } while (continuationToken);
}

export function s3ObjectWriter(bucket: string): CreateObjectWriter {
  return (key) => {
    const body = new PassThrough();
    // Holds at most partSize * queueSize in memory while the parts upload
    const upload = new Upload({
      client: getS3Client(),
      params: { Bucket: bucket, Key: key, Body: body, ContentType: "application/pdf" },
      partSize: 8 * 1024 * 1024,
      queueSize: 2,
    });
    const uploaded = upload.done();
    // Surfaced through done(); keeps an abort from becoming an unhandled rejection
    uploaded.catch(() => {});
    return {
      body,
      done: async () => {
        await uploaded;
      },
      abort: async () => {
        await upload.abort();
        body.destroy();
      },
    };
  };
}
