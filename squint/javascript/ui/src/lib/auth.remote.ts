import { invalid, redirect } from "@sveltejs/kit";
import { form, getRequestEvent } from "$app/server";
import { APIError } from "better-auth/api";
import * as v from "valibot";
import { auth } from "#lib/server/auth.ts";

const callbackURL = "/auth/verification-success";

export const signInOrUp = form(
  v.object({
    email: v.pipe(v.string(), v.email()),
    _password: v.pipe(v.string(), v.nonEmpty()),
    name: v.string(),
    action: v.picklist(["signIn", "signUp"]),
  }),
  async ({ email, _password: password, name, action }) => {
    try {
      if (action === "signIn") {
        await auth.api.signInEmail({ body: { email, password, callbackURL } });
      } else {
        await auth.api.signUpEmail({ body: { email, password, name, callbackURL } });
      }
    } catch (error) {
      if (error instanceof APIError) {
        invalid(error.message || (action === "signIn" ? "Sign in failed" : "Registration failed"));
      }
      throw error;
    }

    redirect(303, "/documents");
  },
);

export const signOut = form(async () => {
  await auth.api.signOut({ headers: getRequestEvent().request.headers });
  redirect(303, "/");
});
