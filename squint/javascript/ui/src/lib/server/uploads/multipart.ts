import { PassThrough, Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import Busboy from "@fastify/busboy";

export type FormPart =
  | { kind: "field"; name: string; value: string }
  | { kind: "file"; name: string; filename: string; stream: Readable & { truncated?: boolean } };

export class UploadLimitError extends Error {}

export type MultipartLimits = { files: number; fileSize: number; totalBytes: number };

/**
 * Yields the fields and files of a multipart request in order, one file stream at a time, without
 * buffering file contents. Each yielded file stream must be read to the end before the next part
 * arrives. Stopping early drains the rest of the request so the response can still be delivered.
 */
export async function* parseMultipart(
  request: Request,
  limits: MultipartLimits,
): AsyncGenerator<FormPart> {
  const contentType = request.headers.get("content-type") ?? "";
  if (!request.body || !contentType.startsWith("multipart/form-data")) {
    throw new TypeError("expected a multipart/form-data request");
  }
  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > limits.totalBytes) throw new UploadLimitError("request too large");

  const busboy = Busboy({
    headers: { "content-type": contentType },
    limits: { files: limits.files, fileSize: limits.fileSize, fields: 20, fieldSize: 1024 },
  });

  const queue: FormPart[] = [];
  let failure: unknown;
  let finished = false;
  let draining = false;
  let wake: (() => void) | undefined;
  const notify = () => {
    wake?.();
    wake = undefined;
  };

  busboy.on("file", (name, stream, filename) => {
    if (draining) stream.resume();
    // busboy reports the empty name of an unused file input as undefined
    else queue.push({ kind: "file", name, filename: filename ?? "", stream });
    notify();
  });
  busboy.on("field", (name, value) => {
    queue.push({ kind: "field", name, value });
    notify();
  });
  busboy.on("filesLimit", () => {
    failure ??= new UploadLimitError(`more than ${limits.files} files`);
    notify();
  });

  let received = 0;
  const body = Readable.fromWeb(request.body as import("node:stream/web").ReadableStream);
  const parsed = pipeline(
    body,
    async function* (source) {
      for await (const chunk of source as AsyncIterable<Buffer>) {
        received += chunk.length;
        if (received > limits.totalBytes) {
          failure ??= new UploadLimitError("request too large");
          notify();
        }
        yield chunk;
      }
    },
    busboy,
  ).then(
    () => {
      finished = true;
      notify();
    },
    (error: unknown) => {
      failure ??= error;
      finished = true;
      notify();
    },
  );

  try {
    while (true) {
      if (failure) throw failure;
      const part = queue.shift();
      if (part) {
        yield part;
      } else if (finished) {
        return;
      } else {
        await new Promise<void>((resolve) => (wake = resolve));
      }
    }
  } finally {
    draining = true;
    for (const part of queue.splice(0)) {
      if (part.kind === "file") part.stream.resume();
    }
    await parsed;
  }
}

function drainedOrClosed(stream: PassThrough): Promise<void> {
  return new Promise((resolve) => {
    const done = () => {
      stream.off("drain", done);
      stream.off("close", done);
      resolve();
    };
    stream.on("drain", done);
    stream.on("close", done);
  });
}

/**
 * Copies a file part into a stream its consumer is free to abandon or destroy. The part itself is
 * always read to the end, which the parser needs before it can move on to the next part.
 */
export function relay(part: Readable): { stream: PassThrough; drained: Promise<void> } {
  const stream = new PassThrough();
  const drained = (async () => {
    for await (const chunk of part) {
      if (stream.destroyed) continue;
      if (!stream.write(chunk)) await drainedOrClosed(stream);
    }
    if (!stream.destroyed) stream.end();
  })();
  drained.catch((error: Error) => stream.destroy(error));
  return { stream, drained };
}
