<script lang="ts">
  import { resolve } from "$app/paths";
  import HeroDemo from "#lib/components/HeroDemo.svelte";

  const steps = [
    {
      title: "Drop in your PDFs",
      body: "A folder, a bucket, a pile on someone's desk. squint queues them up and works through every page.",
    },
    {
      title: "Say which fields you want",
      body: "Vendor, invoice number, total due. Name them and you're done, with no templates to draw and no regexes to babysit.",
    },
    {
      title: "Get rows back",
      body: "One tidy row per document, ready for a spreadsheet, a database, or whatever comes next.",
    },
  ];
</script>

<svelte:head>
  <title>squint: structured data from piles of PDFs</title>
  <meta
    name="description"
    content="squint looks at every page of your PDFs and hands back the fields you asked for, as tidy rows. Self-hosted, vision-first document extraction."
  />
</svelte:head>

<section class="hero">
  <div class="pitch">
    <h1>Squint at a thousand PDFs. Get one tidy table.</h1>
    <p class="lede">
      squint looks at every page the way you would, then hands back just the fields you asked for.
      Scans, tables, and wonky forms included.
    </p>
    <div class="actions">
      <a class="button" href={resolve("/login")}>Get started</a>
      <a class="button quiet" href="#self-host">Run it yourself</a>
    </div>
  </div>
  <HeroDemo />
</section>

<section class="steps" aria-labelledby="steps-heading">
  <h2 id="steps-heading">How it works</h2>
  <ol>
    {#each steps as step (step.title)}
      <li>
        <h3>{step.title}</h3>
        <p>{step.body}</p>
      </li>
    {/each}
  </ol>
</section>

<section class="vision" aria-labelledby="vision-heading">
  <div>
    <h2 id="vision-heading">It looks instead of reads</h2>
    <p>
      Most pipelines turn a page into text first and hope the layout survives the trip. squint works
      from the page image itself, so where something sits on the page is part of what it
      understands.
    </p>
  </div>
  <ul>
    <li>
      <span class="i-ph-table-duotone" aria-hidden="true"></span>
      <div>
        <h3>Tables stay tables</h3>
        <p>Rows and columns keep their meaning, even when the ruling lines are faint.</p>
      </div>
    </li>
    <li>
      <span class="i-ph-scan-duotone" aria-hidden="true"></span>
      <div>
        <h3>Scans are welcome</h3>
        <p>Photocopies, faxes, and the occasional coffee ring.</p>
      </div>
    </li>
    <li>
      <span class="i-ph-layout-duotone" aria-hidden="true"></span>
      <div>
        <h3>Layout is a clue</h3>
        <p>The big number at the bottom right of an invoice is probably the total.</p>
      </div>
    </li>
  </ul>
</section>

<section id="self-host" class="self-host" aria-labelledby="self-host-heading">
  <span class="i-ph-hard-drives-duotone" aria-hidden="true"></span>
  <h2 id="self-host-heading">Your documents stay on your GPUs</h2>
  <p>
    squint runs on your own Kubernetes cluster, right next to your data. Nothing gets mailed off to
    someone else's API to be looked at.
  </p>
</section>

<style>
  section + section {
    margin-block-start: var(--space-9);
  }

  .hero {
    display: grid;
    gap: var(--space-8);
    align-items: center;
    padding-block-start: var(--space-7);

    @media (min-width: 60rem) {
      grid-template-columns: 1.1fr 1fr;
      gap: var(--space-7);
      padding-block-start: var(--space-8);
    }
  }

  .pitch {
    display: grid;
    gap: var(--space-5);
  }

  .lede {
    max-width: 34em;
    color: var(--ink-soft);
    font-size: var(--step-2);
    line-height: 1.45;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
    margin-block-start: var(--space-2);
  }

  .steps ol {
    display: grid;
    gap: var(--space-6);
    margin-block-start: var(--space-6);
    padding: 0;
    list-style: none;
    counter-reset: step;

    @media (min-width: 48rem) {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .steps li {
    display: grid;
    align-content: start;
    gap: var(--space-2);
    padding-block-start: var(--space-4);
    border-top: 1px solid var(--ink);
    counter-increment: step;

    &::before {
      content: counter(step);
      justify-self: start;
      padding-inline: 0.15em;
      padding-block-end: 0.12em;
      margin-block-end: var(--space-2);
      font-family: var(--font-display);
      font-size: var(--step-4);
      font-variation-settings:
        "SOFT" 100,
        "WONK" 1;
      font-weight: 600;
      line-height: 1;
      background: linear-gradient(var(--marker-pink), var(--marker-pink)) no-repeat 0 100% / 100%
        0.22em;
    }

    p {
      color: var(--ink-soft);
    }
  }

  .vision {
    display: grid;
    gap: var(--space-6);

    @media (min-width: 60rem) {
      grid-template-columns: 1fr 1fr;
      gap: var(--space-8);
    }

    > div {
      display: grid;
      align-content: start;
      gap: var(--space-4);
    }

    ul {
      display: grid;
      gap: var(--space-5);
      padding: 0;
      list-style: none;
    }

    li {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: var(--space-4);
      align-items: start;
    }

    li p {
      color: var(--ink-soft);
    }

    [class^="i-ph"] {
      font-size: var(--step-4);
    }
  }

  .self-host {
    display: grid;
    gap: var(--space-4);
    padding-block-start: var(--space-7);
    border-top: 1px solid var(--rule);

    [class^="i-ph"] {
      font-size: var(--step-5);
    }
  }
</style>
