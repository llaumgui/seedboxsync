import { beforeEach, describe, expect, it, vi } from "vitest";
import { TablePaginedComponent } from "@seedboxsync/alpine/table_pagined.js";

describe("TablePaginedComponent", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
    globalThis.window = { location: { origin: "https://seedbox.test" }, addEventListener: vi.fn() };
  });

  it("loads paginated data with search parameters", async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ data: ["item"], data_total: 41 }),
    });
    const component = TablePaginedComponent("/api/items", 20);
    component.offset = 20;
    component.search = "linux";

    await component.load();

    expect(fetch).toHaveBeenCalledOnce();
    expect(fetch.mock.calls[0][0].toString()).toBe(
      "https://seedbox.test/api/items?limit=20&offset=20&search=linux",
    );
    expect(component.data).toEqual(["item"]);
    expect(component.total).toBe(41);
    expect(component.totalPages).toBe(3);
  });

  it("resets data when loading fails", async () => {
    fetch.mockRejectedValue(new Error("network"));
    const component = TablePaginedComponent("/api/items");
    component.data = ["old"];
    component.total = 20;

    await component.load();

    expect(component.error).toBe(true);
    expect(component.data).toEqual([]);
    expect(component.total).toBe(0);
    expect(component.loading).toBe(false);
  });

  it("moves between valid pages and ignores invalid pages", () => {
    const component = TablePaginedComponent("/api/items", 2);
    component.total = 10;
    const load = vi.spyOn(component, "load").mockResolvedValue();

    component.nextPage();
    expect(component.page).toBe(2);
    expect(component.offset).toBe(2);
    component.prevPage();
    expect(component.page).toBe(1);
    expect(component.offset).toBe(0);
    component.goToPage(5);
    expect(component.page).toBe(5);
    expect(component.offset).toBe(8);
    component.goToPage(6);
    expect(component.page).toBe(5);
    expect(load).toHaveBeenCalledTimes(3);
  });

  it("builds visible pages with ellipses and resets search", () => {
    const component = TablePaginedComponent("/api/items", 10);
    component.total = 100;
    component.page = 5;
    expect(component.visiblePages).toEqual([
      { page: 1, isEllipsis: false },
      { page: null, isEllipsis: true },
      { page: 3, isEllipsis: false },
      { page: 4, isEllipsis: false },
      { page: 5, isEllipsis: false },
      { page: 6, isEllipsis: false },
      { page: 7, isEllipsis: false },
      { page: null, isEllipsis: true },
      { page: 10, isEllipsis: false },
    ]);
    const load = vi.spyOn(component, "load").mockResolvedValue();
    component.updateSearch("new");
    expect(component.search).toBe("new");
    expect(component.page).toBe(1);
    expect(component.offset).toBe(0);
    expect(load).toHaveBeenCalledOnce();
  });

  it("loads on init and reacts to force-refresh", () => {
    const component = TablePaginedComponent("/api/items");
    const load = vi.spyOn(component, "load").mockResolvedValue();

    component.init();

    expect(load).toHaveBeenCalledOnce();
    expect(window.addEventListener).toHaveBeenCalledWith("force-refresh", expect.any(Function));
  });
});