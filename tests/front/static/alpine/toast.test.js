import { beforeEach, describe, expect, it, vi } from "vitest";

const { bootstrapToast, randomUUID } = vi.hoisted(() => ({
  bootstrapToast: { show: vi.fn() },
  randomUUID: vi.fn(() => "toast-id"),
}));

vi.mock("bootstrap", () => ({
  Toast: { getOrCreateInstance: vi.fn(() => bootstrapToast) },
}));

import { ToastManager } from "@seedboxsync/alpine/toast.js";

describe("toast helpers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("crypto", { randomUUID });
    globalThis.window = { dispatchEvent: vi.fn() };
  });

  it("adds a toast and removes it after Bootstrap hides it", async () => {
    const manager = ToastManager();
    const hidden = vi.fn();
    const element = {
      addEventListener: vi.fn((event, callback) => {
        expect(event).toBe("hidden.bs.toast");
        hidden.mockImplementation(callback);
      }),
    };
    manager.$root = { querySelector: vi.fn(() => element) };
    manager.$nextTick = (callback) => callback();

    manager.show({ message: "Saved", type: "success" });
    await Promise.resolve();

    expect(manager.toasts).toEqual([
      { id: "toast-id", message: "Saved", type: "success", title: "" },
    ]);
    expect(bootstrapToast.show).toHaveBeenCalledOnce();
    hidden();
    expect(manager.toasts).toEqual([]);
  });

  it("stores a provided title when one is supplied", () => {
    const manager = ToastManager();
    manager.$root = { querySelector: vi.fn(() => null) };
    manager.$nextTick = (callback) => callback();

    manager.show({ message: "Saved", type: "success", title: "Success" });

    expect(manager.toasts).toEqual([
      { id: "toast-id", message: "Saved", type: "success", title: "Success" },
    ]);
  });

  it("ignores a missing rendered toast element", () => {
    const manager = ToastManager();
    manager.$root = { querySelector: vi.fn(() => null) };
    manager.$nextTick = (callback) => callback();

    manager.show({ message: "Pending" });

    expect(manager.toasts).toHaveLength(1);
    expect(bootstrapToast.show).not.toHaveBeenCalled();
  });
});