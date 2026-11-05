import type { User, Session } from "better-auth";

// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
  namespace App {
    interface Locals {
      user?: User;
      session?: Session;
    }

    // interface Error {}
    interface PageData {
      locale: string;
      timeZone: string;
    }
    interface PageState {
      /** Set by the search bar, so a page can tell a new search from a link to its results */
      searched?: boolean;
    }
    // interface Platform {}
  }
}

export {};
