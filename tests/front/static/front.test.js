import { beforeEach, describe, expect, it, vi } from "vitest";

describe("frontend entry point", () => {
  beforeEach(() => {
    vi.resetModules();
    globalThis.window = {};
  });

  it("loads frontend modules and exposes DatePicker globally", async () => {
    const bootstrapLoaded = vi.fn();
    const alpineLoaded = vi.fn();
    const chartLoaded = vi.fn();
    class MockDatePicker {}

    vi.doMock("@seedboxsync/bootstrap/index.js", () => {
      bootstrapLoaded();
      return {};
    });
    vi.doMock("@seedboxsync/alpine/index.js", () => {
      alpineLoaded();
      return {};
    });
    vi.doMock("@seedboxsync/chart/index.js", () => {
      chartLoaded();
      return {};
    });
    vi.doMock("vanilla-ui-kit", () => ({ DatePicker: MockDatePicker }));

    await import("@seedboxsync/front/index.js");

    expect(bootstrapLoaded).toHaveBeenCalledOnce();
    expect(alpineLoaded).toHaveBeenCalledOnce();
    expect(chartLoaded).toHaveBeenCalledOnce();
    expect(window.DatePicker).toBe(MockDatePicker);
  });
});