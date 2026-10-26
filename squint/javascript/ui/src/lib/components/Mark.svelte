<script lang="ts">
  let { title, size = 32 }: { title?: string; size?: number } = $props();
</script>

{#snippet eye(bars: string)}
  {#if title}<title>{title}</title>{/if}
  <path
    d="M15.5 12a8.5 8.5 0 1 0 17 0a8.5 8.5 0 1 0-17 0ZM24 8a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0-5 0Z"
    fill-rule="evenodd"
    stroke="none"
  />
  <path d={bars} fill="none" stroke-width="6" stroke-linecap="round" />
{/snippet}

<svg
  class="bare"
  width={size * 2}
  height={size}
  viewBox="0 0 48 24"
  fill="currentColor"
  stroke="currentColor"
  role={title ? "img" : undefined}
  aria-hidden={title ? undefined : "true"}
>
  {@render eye("M5 5h38M5 19h38")}
</svg>
<svg
  class="badge"
  width={size * 1.25}
  height={size * 1.25}
  viewBox="3 -9 42 42"
  fill="var(--paper)"
  stroke="var(--paper)"
  role={title ? "img" : undefined}
  aria-hidden={title ? undefined : "true"}
>
  <circle cx="24" cy="12" r="21" fill="currentColor" stroke="none" />
  {@render eye("M10 5h28M10 19h28")}
</svg>

<style>
  .badge {
    display: none;
  }

  @media (prefers-color-scheme: dark) {
    :global(:root:not([data-theme="light"])) {
      .bare {
        display: none;
      }

      .badge {
        display: inline;
      }
    }
  }

  :global(:root[data-theme="dark"]) {
    .bare {
      display: none;
    }

    .badge {
      display: inline;
    }
  }
</style>
