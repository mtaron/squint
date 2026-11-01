import { error, json } from "@sveltejs/kit";
import { documents } from "#lib/server/documents.ts";
import type { RequestHandler } from "./$types";

function decodedFileName(header: string | null): string {
  try {
    return decodeURIComponent(header ?? "");
  } catch {
    return "";
  }
}

export const POST: RequestHandler = async ({ locals, request }) => {
  if (!locals.user) {
    error(401, "Sign in to upload documents.");
  }
  const name = decodedFileName(request.headers.get("file-name"));
  if (!name) {
    error(400, "This upload has no file name.");
  }
  // Also what makes a cross-site request preflight, since Kit's origin check only covers forms
  if (request.headers.get("content-type") !== "application/pdf") {
    error(415, "Only PDF files can be uploaded.");
  }
  const size = Number(request.headers.get("content-length"));
  const { body } = request;
  if (!size || !body) {
    error(411, "This upload has no length.");
  }

  const outcome = await documents.add(locals.user.id, { name, size, stream: () => body });
  return "problem" in outcome ? json(outcome, { status: 422 }) : json(outcome, { status: 201 });
};
