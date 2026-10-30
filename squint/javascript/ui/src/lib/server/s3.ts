import { Readable } from "node:stream";
import { DeleteObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { Upload } from "@aws-sdk/lib-storage";

export interface ObjectStorage {
  /** Streams `body` to the object, buffering at most a few multipart parts at once. */
  put(
    bucket: string,
    key: string,
    body: ReadableStream<Uint8Array>,
    onProgress: (loaded: number) => void,
  ): Promise<void>;
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

    async delete(bucket, key) {
      await client.send(new DeleteObjectCommand({ Bucket: bucket, Key: key }));
    },
  };
}
