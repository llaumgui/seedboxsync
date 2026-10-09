import { beforeEach, describe, expect, it, vi } from "vitest";

describe("frontend entry points", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    globalThis.window = {};
    globalThis.document = {
      addEventListener: vi.fn(),
      querySelector: vi.fn(() => null),
      querySelectorAll: vi.fn(() => []),
      createElement: vi.fn(() => ({ getContext: vi.fn(() => ({})) })),
    };
    globalThis.window = {
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      document: globalThis.document,
    };
  });

  it("registers Alpine components and validators globally", async () => {
    const start = vi.fn();
    const magic = vi.fn();
    const data = vi.fn();
    vi.doMock("alpinejs", () => ({
      __esModule: true,
      default: { data, magic, start },
      data,
      magic,
      start,
    }));
    vi.doMock("bootstrap", () => ({
      Modal: { getOrCreateInstance: vi.fn() },
      Toast: { getOrCreateInstance: vi.fn() },
    }));
    await import("@seedboxsync/alpine/index.js");

    expect(start).toHaveBeenCalledOnce();
    expect(magic).toHaveBeenCalledWith("relativeTime", expect.any(Function));
    expect(magic).toHaveBeenCalledWith("validators", expect.any(Function));
  });
});