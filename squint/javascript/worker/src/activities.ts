import {
  AbortMultipartUploadCommand,
  CreateBucketCommand,
  DeleteBucketCommand,
  DeleteObjectsCommand,
  ListMultipartUploadsCommand,
  ListObjectsV2Command,
  type S3Client,
} from "@aws-sdk/client-s3";
import { heartbeat } from "@temporalio/activity";

export function userBucketName(userId: string): string {
  return `squint-u-${userId}`;
}

function isS3Error(error: unknown, name: string): boolean {
  return error instanceof Error && error.name === name;
}

async function abortMultipartUploads(s3: S3Client, bucket: string) {
  let keyMarker: string | undefined;
  let uploadIdMarker: string | undefined;
  let truncated = true;
  while (truncated) {
    const page = await s3.send(
      new ListMultipartUploadsCommand({
        Bucket: bucket,
        KeyMarker: keyMarker,
        UploadIdMarker: uploadIdMarker,
      }),
    );
    for (const { Key, UploadId } of page.Uploads ?? []) {
      await s3.send(new AbortMultipartUploadCommand({ Bucket: bucket, Key, UploadId }));
    }
    heartbeat();
    keyMarker = page.NextKeyMarker;
    uploadIdMarker = page.NextUploadIdMarker;
    truncated = page.IsTruncated ?? false;
  }
}

async function deleteAllObjects(s3: S3Client, bucket: string) {
  let continuationToken: string | undefined;
  let truncated = true;
  while (truncated) {
    // Each page holds at most 1000 keys, the DeleteObjects limit
    const page = await s3.send(
      new ListObjectsV2Command({ Bucket: bucket, ContinuationToken: continuationToken }),
    );
    const objects = (page.Contents ?? []).map(({ Key }) => ({ Key }));
    if (objects.length > 0) {
      const { Errors } = await s3.send(
        new DeleteObjectsCommand({ Bucket: bucket, Delete: { Objects: objects, Quiet: true } }),
      );
      if (Errors?.length) {
        const [{ Key, Code, Message }] = Errors;
        throw new Error(
          `Failed to delete ${Errors.length} objects from ${bucket}, e.g. ${Key}: ${Code} ${Message}`,
        );
      }
    }
    heartbeat();
    continuationToken = page.NextContinuationToken;
    truncated = page.IsTruncated ?? false;
  }
}

export function createActivities(s3: S3Client) {
  return {
    async createUserBucket(userId: string): Promise<void> {
      try {
        await s3.send(new CreateBucketCommand({ Bucket: userBucketName(userId) }));
      } catch (error) {
        if (!isS3Error(error, "BucketAlreadyOwnedByYou")) {
          throw error;
        }
      }
    },

    async deleteUserBucket(userId: string): Promise<void> {
      const bucket = userBucketName(userId);
      try {
        await abortMultipartUploads(s3, bucket);
        await deleteAllObjects(s3, bucket);
        await s3.send(new DeleteBucketCommand({ Bucket: bucket }));
      } catch (error) {
        if (!isS3Error(error, "NoSuchBucket")) {
          throw error;
        }
      }
    },
  };
}
