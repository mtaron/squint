import { S3Client } from "@aws-sdk/client-s3";

// The endpoint, region and credentials come from the AWS_* environment variables
export function createS3Client(): S3Client {
  return new S3Client({ forcePathStyle: true });
}
