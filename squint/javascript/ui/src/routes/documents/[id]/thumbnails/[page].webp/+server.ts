import { storage } from "#lib/server/documents.ts";
import { servePageObject, thumbnail } from "#lib/server/page-images.ts";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = ({ locals, params }) =>
  servePageObject(storage, thumbnail, locals.user?.id, params);
