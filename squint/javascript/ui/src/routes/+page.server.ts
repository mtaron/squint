import { redirect } from "@sveltejs/kit";
import { hasDocuments } from "#lib/server/documents.ts";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.user && (await hasDocuments(locals.user.id))) {
    return redirect(302, "/documents");
  }
  return {};
};
