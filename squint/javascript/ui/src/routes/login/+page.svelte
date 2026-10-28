<script lang="ts">
  import { signInOrUp } from "#lib/auth.remote.ts";
  import Button from "#lib/components/Button.svelte";
  import Highlight from "#lib/components/Highlight.svelte";

  const { email, _password, name, action } = signInOrUp.fields;
</script>

<svelte:head>
  <title>Sign in to squint</title>
</svelte:head>

<section>
  <h1>Hello <Highlight>again</Highlight>.</h1>
  <p class="lede">Sign in to get back to your documents, or create an account to start a pile.</p>

  <form {...signInOrUp}>
    <label>
      <span>Email</span>
      <input {...email.as("email")} autocomplete="email" required />
    </label>
    <label>
      <span>Password</span>
      <input {..._password.as("password")} autocomplete="current-password" required />
    </label>
    <label>
      <span>Name <small>(only for new accounts)</small></span>
      <input {...name.as("text")} autocomplete="name" />
    </label>

    <p class="error" aria-live="polite">
      {signInOrUp.fields
        .allIssues()
        ?.map((issue) => issue.message)
        .join(" ")}
    </p>

    <div class="actions">
      <Button {...action.as("submit", "signIn")} disabled={!!signInOrUp.pending}>Sign in</Button>
      <Button variant="quiet" {...action.as("submit", "signUp")} disabled={!!signInOrUp.pending}>
        Create account
      </Button>
    </div>
  </form>
</section>

<style>
  section {
    display: grid;
    gap: var(--space-5);
    max-width: 28rem;
    padding-block: var(--space-8) var(--space-6);
  }

  h1 {
    font-size: var(--step-5);
  }

  .lede {
    color: var(--ink-soft);
  }

  form {
    display: grid;
    gap: var(--space-5);
    margin-block-start: var(--space-4);
  }

  label {
    display: grid;
    gap: var(--space-2);
    font-size: var(--step-0);
    font-weight: 600;
  }

  small {
    color: var(--ink-soft);
    font-size: inherit;
    font-weight: 400;
  }

  input {
    padding: var(--space-3) var(--space-4);
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: var(--radius-small);
    font-weight: 400;

    &:hover {
      border-color: var(--ink-soft);
    }
  }

  .error {
    min-height: 1.5em;
    margin-block: calc(-1 * var(--space-2));
    color: light-dark(#b0215f, var(--marker-pink));
    font-size: var(--step-0);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }
</style>
