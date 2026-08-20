import { beforeEach, describe, expect, it, vi } from "vitest";
import { TableComponent } from "@seedboxsync/alpine/table.js";

describe("TableComponent", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
    globalThis.window = {
      addEventListener: vi.fn(),
    };
  });

  it("loads data and clears the loading state", async () => {
    fetch.mockResolvedValue({ ok: true, json: async () => ({ data: [1, 2] }) });
    const component = TableComponent("/api/items");

    const loading = component.load();
    expect(component.loading).toBe(true);
    await loading;

    expect(component.data).toEqual([1, 2]);
    expect(fetch).toHaveBeenCalledWith("/api/items");
    expect(component.error).toBe(false);
  });

  it("handles failed responses", async () => {
    fetch.mockResolvedValue({ ok: false });
    const component = TableComponent("/api/items");

    await component.load();

    expect(component.error).toBe(true);
    expect(component.data).toEqual([]);
    expect(component.loading).toBe(false);
  });

  it("loads on init, refresh interval, and force-refresh", async () => {
    vi.useFakeTimers();
    fetch.mockResolvedValue({ ok: true, json: async () => ({ data: [] }) });
    const component = TableComponent("/api/items", 1000);
    const load = vi.spyOn(component, "load");

    component.init();
    expect(load).toHaveBeenCalledOnce();
    expect(window.addEventListener).toHaveBeenCalledWith(
      "force-refresh",
      expect.any(Function),
    );

    vi.advanceTimersByTime(1000);
    expect(load).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });
});