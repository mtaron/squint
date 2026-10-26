import { on } from "svelte/events";
import { createSubscriber } from "svelte/reactivity";

function defaultStorage() {
  try {
    localStorage.getItem("squint:probe");
    return localStorage;
  } catch {
    return undefined;
  }
}

export class Persisted<T extends string = string> {
  #key: string;
  #fallback: T;
  #storage: Storage | undefined;
  #local = $state<T>();

  #subscribe = createSubscriber((update) =>
    on(window, "storage", (event) => {
      if (event.key === this.#key) update();
    }),
  );

  constructor(key: string, fallback: T, storage = defaultStorage()) {
    this.#key = key;
    this.#fallback = fallback;
    this.#storage = storage;
  }

  get current(): T {
    this.#subscribe();
    const local = this.#local;
    const value = this.#storage ? this.#storage.getItem(this.#key) : local;
    return (value as T | null | undefined) ?? this.#fallback;
  }

  set current(value: T) {
    this.#storage?.setItem(this.#key, value);
    this.#local = value;
  }
}
