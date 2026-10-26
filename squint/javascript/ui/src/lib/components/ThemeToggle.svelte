<script lang="ts">
  import { theme } from "#lib/state/theme.svelte.ts";

  $effect(() => {
    const root = document.documentElement;
    if (theme.preference === "system") delete root.dataset.theme;
    else root.dataset.theme = theme.preference;
  });
</script>

<button
  class="toggle"
  type="button"
  aria-label="Dark mode"
  aria-pressed={theme.current === "dark"}
  onclick={() => theme.toggle()}
>
  <span class="icon moon i-ph-moon-duotone" aria-hidden="true"></span>
  <span class="icon sun i-ph-sun-duotone" aria-hidden="true"></span>
</button>

<style>
  .toggle {
    display: inline-grid;
    place-items: center;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    background: transparent;
    border: 1px solid var(--rule);
    border-radius: var(--radius-small);
    font-size: var(--step-1);
    cursor: pointer;
    transition: background-color 160ms var(--ease-out);

    &:hover {
      background: var(--surface);
    }
  }

  .icon {
    grid-area: 1 / 1;
  }

  .sun {
    display: none;
  }

  @media (prefers-color-scheme: dark) {
    :global(:root:not([data-theme="light"])) {
      .moon {
        display: none;
      }

      .sun {
        display: inline-block;
      }
    }
  }

  :global(:root[data-theme="dark"]) {
    .moon {
      display: none;
    }

    .sun {
      display: inline-block;
    }
  }
</style>
