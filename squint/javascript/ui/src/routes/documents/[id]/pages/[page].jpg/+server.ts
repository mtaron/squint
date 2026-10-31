import { storage } from "#lib/server/documents.ts";
import { pageImage, servePageObject } from "#lib/server/page-images.ts";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = ({ locals, params }) =>
  servePageObject(storage, pageImage, locals.user?.id, params);
