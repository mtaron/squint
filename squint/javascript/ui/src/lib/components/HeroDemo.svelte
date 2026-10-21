<script lang="ts">
  import Highlight from "./Highlight.svelte";

  const start = 600;
  const stagger = 650;

  const fields = [
    { name: "vendor", value: "Bramble & Finch Paper Co." },
    { name: "invoice_number", value: "INV-20417" },
    { name: "total_due", value: "$12,480.00" },
  ];
  const [vendor, invoiceNumber, totalDue] = fields;
  const delayOf = (index: number) => start + index * stagger;
</script>

<figure class="demo">
  <figcaption class="visually-hidden">
    An invoice with its vendor, invoice number, and total highlighted, next to a table of those
    three values.
  </figcaption>

  <div class="page" aria-hidden="true">
    <header>
      <p class="vendor"><Highlight delay={delayOf(0)}>{vendor.value}</Highlight></p>
      <p class="doc-title">
        Invoice <Highlight delay={delayOf(1)}>{invoiceNumber.value}</Highlight>
      </p>
    </header>
    <div class="lines">
      <span style:width="62%"></span>
      <span style:width="48%"></span>
      <span style:width="55%"></span>
    </div>
    <div class="items">
      {#each [78, 64, 71, 58] as width (width)}
        <span class="line" style:width="{width}%"></span>
        <span class="amount"></span>
      {/each}
    </div>
    <p class="total">
      <span>Total due</span>
      <Highlight delay={delayOf(2)}>{totalDue.value}</Highlight>
    </p>
  </div>

  <table class="extracted">
    <caption>What you get back</caption>
    <tbody>
      {#each fields as field, index (field.name)}
        <tr style:--delay="{delayOf(index) + 260}ms">
          <th scope="row">{field.name}</th>
          <td>{field.value}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</figure>

<style>
  .demo {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-5);
    margin: 0;
  }

  .page {
    display: grid;
    gap: var(--space-5);
    padding: var(--space-6) var(--space-5);
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: var(--radius-page);
    box-shadow:
      0 1px 0 var(--rule),
      0 18px 40px -24px light-dark(rgb(28 32 48 / 0.35), rgb(0 0 0 / 0.6));
    font-size: var(--step--1);
    rotate: -1.5deg;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: var(--space-2) var(--space-4);
  }

  .vendor {
    font-weight: 650;
  }

  .doc-title {
    color: var(--ink-soft);
  }

  .lines,
  .items {
    display: grid;
    gap: var(--space-2);
  }

  .items {
    grid-template-columns: 1fr 3rem;
    align-items: center;
    padding-block: var(--space-4);
    border-block: 1px solid var(--rule);
  }

  .lines span,
  .items span {
    display: block;
    height: 0.45rem;
    border-radius: 1rem;
    background: var(--rule);
  }

  .amount {
    justify-self: end;
    width: 100%;
  }

  .total {
    display: flex;
    justify-content: space-between;
    gap: var(--space-4);
    font-weight: 650;
    font-variant-numeric: tabular-nums;
  }

  .extracted {
    justify-self: end;
    width: min(100%, 22rem);
    border-collapse: separate;
    border-spacing: 0;
    background: var(--paper);
    border: 1px solid var(--ink);
    border-radius: var(--radius-small);
    font-size: var(--step--1);
    font-variant-numeric: tabular-nums;
  }

  caption {
    caption-side: bottom;
    padding-block-start: var(--space-2);
    text-align: start;
    color: var(--ink-soft);
  }

  tr {
    opacity: 0;
    translate: -0.75rem 0;
    animation: arrive 360ms var(--ease-out) var(--delay) forwards;

    & + tr > * {
      border-top: 1px solid var(--rule);
    }
  }

  th,
  td {
    padding: var(--space-2) var(--space-3);
    text-align: start;
    vertical-align: top;
  }

  th {
    color: var(--ink-soft);
    font-weight: 500;
  }

  @keyframes arrive {
    to {
      opacity: 1;
      translate: 0 0;
    }
  }

  @media (min-width: 40rem) {
    .extracted {
      position: absolute;
      inset-block-end: calc(-1 * var(--space-7));
      inset-inline-end: calc(-1 * var(--space-5));
      width: 22rem;
      box-shadow: 0 18px 40px -24px light-dark(rgb(28 32 48 / 0.35), rgb(0 0 0 / 0.6));
    }

    .page {
      margin-inline-end: var(--space-8);
      margin-block-end: var(--space-9);
    }
  }
</style>
