import { expect, test } from "vitest";
import { DocumentSelection } from "./document-selection.svelte.ts";

const ordered = ["a", "b", "c", "d", "e"];

test("toggling adds and removes a document", () => {
  const selection = new DocumentSelection();
  selection.toggle("a");
  expect(selection.has("a")).toBe(true);
  selection.toggle("a");
  expect(selection.has("a")).toBe(false);
});

test("a range runs from the last toggled document, in either direction", () => {
  const selection = new DocumentSelection();
  selection.toggle("d");
  selection.toggleRange("b", ordered);
  expect(selection.within(ordered)).toEqual(["b", "c", "d"]);
});

test("a range takes on the new state of the document it ends at", () => {
  const selection = new DocumentSelection();
  selection.setAll(ordered, true);
  selection.toggle("a");
  selection.toggleRange("c", ordered);
  expect(selection.within(ordered)).toEqual(["d", "e"]);
});

test("the next range starts where the last one ended", () => {
  const selection = new DocumentSelection();
  selection.toggle("a");
  selection.toggleRange("b", ordered);
  selection.toggleRange("d", ordered);
  expect(selection.within(ordered)).toEqual(["a", "b", "c", "d"]);
});

test("a range with nothing to start from toggles just that document", () => {
  const selection = new DocumentSelection();
  selection.toggleRange("c", ordered);
  expect(selection.within(ordered)).toEqual(["c"]);
});

test("a range whose start has since been deleted toggles just that document", () => {
  const selection = new DocumentSelection();
  selection.toggle("gone");
  selection.toggleRange("c", ordered);
  expect(selection.within(ordered)).toEqual(["c"]);
});

test("a whole day can be selected and cleared", () => {
  const selection = new DocumentSelection();
  selection.setAll(["a", "b"], true);
  expect(selection.within(ordered)).toEqual(["a", "b"]);
  selection.setAll(["a"], false);
  expect(selection.within(ordered)).toEqual(["b"]);
});

test("deleted documents drop out of the selection", () => {
  const selection = new DocumentSelection();
  selection.setAll(["a", "b"], true);
  expect(selection.within(["b", "c"])).toEqual(["b"]);
});

test("clearing forgets the range's start", () => {
  const selection = new DocumentSelection();
  selection.toggle("a");
  selection.clear();
  selection.toggleRange("c", ordered);
  expect(selection.within(ordered)).toEqual(["c"]);
});
