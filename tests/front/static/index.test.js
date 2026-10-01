import { beforeEach, describe, expect, it, vi } from "vitest";

describe("frontend entry points", () => {
  beforeEach(() => {
    vi.resetModules();
    globalThis.window = {};
    globalThis.document = {
      addEventListener: vi.fn(),
      querySelectorAll: vi.fn(() => []),
    };
  });

  it("registers chart helpers globally", async () => {
    class MockChart {}
    vi.doMock("chart.js/auto", () => ({ default: MockChart }));
    await import("@seedboxsync/chart/index.js");

    expect(window.Chart).toBe(MockChart);
    expect(window.createBarChart).toBeTypeOf("function");
    expect(window.loadBarChart).toBeTypeOf("function");
    expect(window.createDoughnutChart).toBeTypeOf("function");
    expect(window.load2DoughnutChart).toBeTypeOf("function");
  });

  it("registers Alpine components and validators globally", async () => {
    const start = vi.fn();
    const magic = vi.fn();
    vi.doMock("alpinejs", () => ({ default: { data: vi.fn(), magic, start } }));
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