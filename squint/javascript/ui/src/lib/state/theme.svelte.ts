import { MediaQuery } from "svelte/reactivity";
import { Persisted } from "./persisted.svelte.ts";

export type ThemePreference = "system" | "light" | "dark";

class Theme {
  #stored = new Persisted<ThemePreference>("squint:theme", "system");
  #systemDark = new MediaQuery("prefers-color-scheme: dark");

  get preference(): ThemePreference {
    const stored = this.#stored.current;
    return stored === "light" || stored === "dark" ? stored : "system";
  }

  get current(): "light" | "dark" {
    return this.preference === "system"
      ? this.#systemDark.current
        ? "dark"
        : "light"
      : this.preference;
  }

  toggle() {
    const next = this.current === "dark" ? "light" : "dark";
    const system = this.#systemDark.current ? "dark" : "light";
    this.#stored.current = next === system ? "system" : next;
  }
}

export const theme = new Theme();
