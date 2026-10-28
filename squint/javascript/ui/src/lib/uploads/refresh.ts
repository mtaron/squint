import { invalidate } from "$app/navigation";

const MIN_INTERVAL_MS = 1000;

let refreshing = false;
let requested = false;

/** Reloads the document list, at most about once a second however often it is asked to. */
export function refreshDocuments(): void {
  requested = true;
  if (refreshing) return;
  refreshing = true;
  void (async () => {
    try {
      while (requested) {
        requested = false;
        await invalidate("app:documents");
        await new Promise((resolve) => setTimeout(resolve, MIN_INTERVAL_MS));
      }
    } finally {
      refreshing = false;
    }
  })();
}
