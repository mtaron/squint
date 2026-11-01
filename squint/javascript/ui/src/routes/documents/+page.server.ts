import { redirect } from "@sveltejs/kit";
import { hasDocuments } from "#lib/server/documents.ts";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals, isDataRequest }) => {
  if (!locals.user) {
    return redirect(302, "/login");
  }
  // Client navigations are Library's call: an upload in progress has no document here yet
  if (!isDataRequest && !(await hasDocuments(locals.user.id))) {
    return redirect(302, "/");
  }
  return {};
};
