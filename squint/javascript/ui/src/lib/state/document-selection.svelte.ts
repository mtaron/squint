import { SvelteSet } from "svelte/reactivity";

/** The documents picked in the list, and where the next shift-click's range starts. */
export class DocumentSelection {
  #ids = new SvelteSet<string>();
  #rangeStart: string | undefined;

  has(id: string): boolean {
    return this.#ids.has(id);
  }

  /** The selected ids among `ids`, which leaves out documents that have since been deleted. */
  within(ids: string[]): string[] {
    return ids.filter((id) => this.#ids.has(id));
  }

  toggle(id: string) {
    this.setAll([id], !this.#ids.has(id));
    this.#rangeStart = id;
  }

  toggleRange(id: string, ordered: string[]) {
    const start = ordered.indexOf(this.#rangeStart ?? "");
    if (start === -1) {
      this.toggle(id);
      return;
    }
    const end = ordered.indexOf(id);
    const range = ordered.slice(Math.min(start, end), Math.max(start, end) + 1);
    this.setAll(range, !this.#ids.has(id));
    this.#rangeStart = id;
  }

  setAll(ids: string[], selected: boolean) {
    for (const id of ids) {
      if (selected) {
        this.#ids.add(id);
      } else {
        this.#ids.delete(id);
      }
    }
  }

  clear() {
    this.#ids.clear();
    this.#rangeStart = undefined;
  }
}
