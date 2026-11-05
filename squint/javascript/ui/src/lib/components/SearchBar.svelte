<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import { MAX_QUERY_LENGTH, queryFromUrl } from "#lib/search.ts";

  let {
    label,
    keepHash,
  }: {
    label: string;
    /** Where to leave the page when the search changes, as a URL fragment */
    keepHash?: string;
  } = $props();

  const query = $derived(queryFromUrl(page.url));
  // Follows the URL, and the reader's typing until they submit it
  let draft = $derived(query);

  function navigate(next: string) {
    const search = next ? `?${new URLSearchParams({ q: next })}` : "";
    void goto(`${page.url.pathname}${search}${keepHash ?? ""}`, {
      reset: false,
      state: { searched: next !== "" },
    });
  }

  function submit(event: SubmitEvent) {
    event.preventDefault();
    const next = draft.trim();
    if (next !== query) {
      navigate(next);
    }
  }

  function clear(event: KeyboardEvent) {
    if (event.key !== "Escape" || (!query && !draft)) {
      return;
    }
    // Clearing the search shouldn't also clear the selection or close anything else
    event.stopPropagation();
    draft = "";
    if (query) {
      navigate("");
    }
  }
</script>

<form role="search" onsubmit={submit}>
  <span class="i-ph-magnifying-glass" aria-hidden="true"></span>
  <input
    type="search"
    name="q"
    aria-label={label}
    placeholder={label}
    maxlength={MAX_QUERY_LENGTH}
    autocomplete="off"
    bind:value={draft}
    onkeydown={clear}
  />
</form>

<style>
  form {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    min-width: min(100%, 16rem);
    padding: var(--space-1) var(--space-3);
    border: 1px solid var(--rule);
    border-radius: 999px;
    background: var(--paper);
    transition: border-color 120ms var(--ease-out);

    &:focus-within {
      border-color: var(--ink);
      box-shadow: 0 0 0 0.25rem var(--marker);
    }
  }

  span {
    flex-shrink: 0;
    color: var(--ink-soft);
  }

  input {
    flex: 1;
    min-width: 0;
    padding: 0;
    border: 0;
    background: none;
    color: var(--ink);
    font: inherit;

    &:focus {
      outline: 0;
      box-shadow: none;
    }

    &::placeholder {
      color: var(--ink-soft);
    }
  }
</style>
