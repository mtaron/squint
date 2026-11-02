<script lang="ts">
  import { fly } from "svelte/transition";

  let {
    message,
    confirming,
    deleting,
    canSelectAll,
    onselectall,
    onclear,
    onkeep,
    ondelete,
  }: {
    message: string;
    confirming: boolean;
    deleting: boolean;
    canSelectAll: boolean;
    onselectall: () => void;
    onclear: () => void;
    onkeep: () => void;
    ondelete: (button: HTMLButtonElement) => void;
  } = $props();

  function pressDelete(event: MouseEvent & { currentTarget: HTMLButtonElement }) {
    // Delete stays put once it's asking to confirm, so a double-click must not answer for itself
    if (event.detail < 2) {
      ondelete(event.currentTarget);
    }
  }
</script>

<div
  class="bar"
  role="group"
  aria-label="Selected documents"
  transition:fly={{ y: 16, duration: 200 }}
>
  <p>{message}</p>
  <div class="actions">
    {#if confirming}
      <button class="plain" disabled={deleting} onclick={onkeep} {@attach (keep) => keep.focus()}>
        Keep
      </button>
    {:else}
      {#if canSelectAll}
        <button class="plain" onclick={onselectall}>Select all</button>
      {/if}
      <button class="plain" onclick={onclear}>Clear</button>
    {/if}
    <button class={["delete", { confirming }]} disabled={deleting} onclick={pressDelete}>
      {deleting ? "Deleting…" : "Delete"}
    </button>
  </div>
</div>

<style>
  .bar {
    position: sticky;
    bottom: max(var(--space-4), env(safe-area-inset-bottom));
    z-index: 2;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2) var(--space-5);
    padding: var(--space-3) var(--space-3) var(--space-3) var(--space-5);
    background: var(--ink);
    color: var(--paper);
    border-radius: var(--radius-small);
    font-size: var(--step-0);
  }

  p {
    flex: 1;
    min-width: min(16rem, 100%);
    font-weight: 500;
    overflow-wrap: anywhere;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  button {
    padding: var(--space-2) var(--space-4);
    border: 0;
    border-radius: var(--radius-small);
    font-weight: 600;
    line-height: 1.2;
    cursor: pointer;

    &:focus-visible {
      outline-color: var(--paper);
    }

    &:disabled {
      cursor: progress;
      opacity: 0.7;
    }
  }

  .plain {
    background: none;
    color: inherit;

    &:hover:enabled {
      text-decoration: underline;
      text-underline-offset: 0.2em;
    }
  }

  .delete {
    background: var(--paper);
    color: var(--ink);

    &.confirming {
      background: var(--marker-pink);
      color: var(--on-marker);
    }
  }
</style>
