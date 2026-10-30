<script lang="ts">
  import "@fontsource-variable/fraunces/full.css";
  import "@fontsource-variable/instrument-sans";
  import "virtual:uno.css";
  import "../app.css";
  import { resolve } from "$app/paths";
  import favicon from "#lib/assets/favicon.svg";
  import { signOut } from "#lib/auth.remote.ts";
  import ThemeToggle from "#lib/components/ThemeToggle.svelte";
  import Wordmark from "#lib/components/Wordmark.svelte";
  import type { LayoutProps } from "./$types";

  let { data, children }: LayoutProps = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div class="shell">
  <header>
    <a class="home" href={resolve("/")} aria-label="squint home"><Wordmark /></a>
    <nav>
      <ThemeToggle />
      {#if data.user}
        <span class="user">{data.user.name}</span>
        <form {...signOut}>
          <button class="nav-link">Sign out</button>
        </form>
      {:else}
        <a class="nav-link" href={resolve("/login")}>Sign in</a>
      {/if}
    </nav>
  </header>

  <main>
    {@render children()}
  </main>

  <footer>
    <p>Copyright © 2026 Michael Taron</p>
  </footer>
</div>

<style>
  .shell {
    display: grid;
    grid-template-rows: auto 1fr auto;
    min-height: 100dvh;
    width: min(100% - 2 * var(--gutter), var(--page-width));
    margin-inline: auto;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    padding-block: var(--space-5);
  }

  .home {
    text-decoration: none;
  }

  nav {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    font-size: var(--step-0);
  }

  .user {
    color: var(--ink-soft);
  }

  .nav-link {
    padding: var(--space-1) 0;
    background: none;
    border: 0;
    font-weight: 600;
    text-decoration: underline;
    text-decoration-color: var(--marker);
    text-decoration-thickness: 0.25em;
    text-underline-offset: 0.15em;
    text-decoration-skip-ink: none;
    cursor: pointer;
  }

  footer {
    margin-block-start: var(--space-9);
    padding-block: var(--space-6);
    border-top: 1px solid var(--rule);
    color: var(--ink-soft);
    font-size: var(--step-0);
  }
</style>
