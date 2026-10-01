import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CardsStats } from "@seedboxsync/alpine/cards_stats.js";

describe("CardsStats", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    globalThis.Translations = { error_loading_lock_status: "Unable to load statistics" };
    globalThis.window = { addEventListener: vi.fn() };
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("loads statistics and clears the loading state", async () => {
    const statistics = { downloads: 3, torrents: 2 };
    fetch.mockResolvedValue({ ok: true, json: async () => ({ data: statistics }) });
    const component = CardsStats("/stats");

    await component.loadStats();

    expect(fetch).toHaveBeenCalledWith("/stats");
    expect(component.data).toEqual(statistics);
    expect(component.error).toBeNull();
    expect(component.loading).toBe(false);
  });

  it("reports HTTP and network errors and clears the loading state", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    const component = CardsStats("/stats");

    fetch.mockResolvedValueOnce({ ok: false, status: 503 });
    await component.loadStats();
    expect(component.error).toBe("Unable to load statistics");
    expect(component.loading).toBe(false);

    fetch.mockRejectedValueOnce(new Error("network unavailable"));
    await component.loadStats();
    expect(component.error).toBe("Unable to load statistics");
    expect(component.loading).toBe(false);
    expect(consoleError).toHaveBeenCalledTimes(2);
  });

  it("loads immediately, refreshes periodically, and handles force-refresh", async () => {
    vi.useFakeTimers();
    fetch.mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    const component = CardsStats("/stats", 1000);
    const loadStats = vi.spyOn(component, "loadStats");

    await component.init();
    expect(loadStats).toHaveBeenCalledOnce();

    await vi.advanceTimersByTimeAsync(1000);
    expect(loadStats).toHaveBeenCalledTimes(2);

    const refreshHandler = window.addEventListener.mock.calls[0][1];
    await refreshHandler();
    expect(window.addEventListener).toHaveBeenCalledWith("force-refresh", expect.any(Function));
    expect(loadStats).toHaveBeenCalledTimes(3);
  });

  it("does not schedule a timer when refresh is disabled", async () => {
    fetch.mockResolvedValue({ ok: true, json: async () => ({ data: {} }) });
    const setInterval = vi.spyOn(globalThis, "setInterval");
    const component = CardsStats("/stats", 0);

    await component.init();

    expect(setInterval).not.toHaveBeenCalled();
    expect(window.addEventListener).toHaveBeenCalledWith("force-refresh", expect.any(Function));
  });
});