import { Readable } from "node:stream";
import { DeleteObjectCommand, GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { Upload } from "@aws-sdk/lib-storage";

export interface StoredObject {
  body: ReadableStream<Uint8Array>;
  contentLength?: number;
  etag?: string;
}

export interface ObjectStorage {
  /** Streams `body` to the object, buffering at most a few multipart parts at once. */
  put(
    bucket: string,
    key: string,
    body: ReadableStream<Uint8Array>,
    onProgress: (loaded: number) => void,
  ): Promise<void>;
  /** Streams the object, or returns undefined if there isn't one. */
  get(bucket: string, key: string): Promise<StoredObject | undefined>;
  delete(bucket: string, key: string): Promise<void>;
}

// The endpoint, region and credentials come from the AWS_* environment variables
export function s3Storage(client = new S3Client({ forcePathStyle: true })): ObjectStorage {
  return {
    async put(bucket, key, body, onProgress) {
      const upload = new Upload({
        client,
        params: {
          Bucket: bucket,
          Key: key,
          Body: Readable.fromWeb(body as import("node:stream/web").ReadableStream),
          ContentType: "application/pdf",
        },
      });
      upload.on("httpUploadProgress", ({ loaded }) => onProgress(loaded ?? 0));
      await upload.done();
    },

    async get(bucket, key) {
      try {
        const { Body, ContentLength, ETag } = await client.send(
          new GetObjectCommand({ Bucket: bucket, Key: key }),
        );
        if (!Body) {
          return undefined;
        }
        return {
          body: Body.transformToWebStream() as ReadableStream<Uint8Array>,
          contentLength: ContentLength,
          etag: ETag,
        };
      } catch (error) {
        // A new user's bucket is created shortly after they sign up
        if (error instanceof Error && ["NoSuchKey", "NoSuchBucket"].includes(error.name)) {
          return undefined;
        }
        throw error;
      }
    },

    async delete(bucket, key) {
      await client.send(new DeleteObjectCommand({ Bucket: bucket, Key: key }));
    },
  };
}
