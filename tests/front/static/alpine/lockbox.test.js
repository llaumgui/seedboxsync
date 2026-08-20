import { beforeEach, describe, expect, it, vi } from "vitest";

const { toast } = vi.hoisted(() => ({ toast: vi.fn() }));
vi.mock("bulma-toast", () => ({ toast }));

import { LockBoxComponent } from "@seedboxsync/alpine/lockbox.js";

describe("LockBoxComponent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    globalThis.Translations = {
      never_launched: "Never launched",
      in_progress_since: "In progress since",
      completed_since: "Completed since",
      error_loading_lock_status: "Unable to load",
    };
    globalThis.dateTimeOption = {};
    globalThis.window = { addEventListener: vi.fn() };
  });

  it("handles a lock that was never launched", async () => {
    fetch.mockResolvedValue({ status: 404 });
    const component = LockBoxComponent("/lock", "Lock");

    await component.loadLock();

    expect(component.lockData).toBeNull();
    expect(component.lockMessage).toBe("Never launched");
    expect(component.loading).toBe(false);
  });

  it("formats locked and completed states and toasts on changes", async () => {
    fetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ data: { locked: true, locked_at: "2025-01-01T00:00:00Z" } }) });
    const component = LockBoxComponent("/lock", "Lock");

    await component.loadLock();
    expect(component.lockMessage).toContain("In progress since");
    expect(toast).not.toHaveBeenCalled();

    fetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ data: { locked: false, unlocked_at: "2025-01-02T00:00:00Z" } }) });
    await component.loadLock();
    expect(component.lockMessage).toContain("Completed since");
    expect(component.previousLockMessage).toContain("In progress since");
    expect(toast).toHaveBeenCalledWith(expect.objectContaining({ type: "is-info" }));
  });

  it("sets the translated error on failed requests", async () => {
    fetch.mockResolvedValue({ ok: false, status: 500 });
    const component = LockBoxComponent("/lock", "Lock");

    await component.loadLock();

    expect(component.error).toBe("Unable to load");
    expect(component.loading).toBe(false);
  });

  it("loads immediately and registers refresh handlers", async () => {
    vi.useFakeTimers();
    fetch.mockResolvedValue({ status: 404 });
    const component = LockBoxComponent("/lock", "Lock", 1000);
    const load = vi.spyOn(component, "loadLock");

    await component.init();
    expect(load).toHaveBeenCalledOnce();
    expect(window.addEventListener).toHaveBeenCalledWith("force-refresh", expect.any(Function));
    vi.advanceTimersByTime(1000);
    expect(load).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });
});