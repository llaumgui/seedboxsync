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
    expect(window.loadChart).toBeTypeOf("function");
  });

  it("registers Alpine components and validators globally", async () => {
    const start = vi.fn();
    vi.doMock("alpinejs", () => ({ default: { start } }));
    vi.doMock("bulma-toast", () => ({ toast: vi.fn(), setDefaults: vi.fn() }));
    await import("@seedboxsync/alpine/index.js");

    expect(window.Alpine).toEqual({ start });
    expect(start).toHaveBeenCalledOnce();
    expect(window.TableComponent).toBeTypeOf("function");
    expect(window.TablePaginedComponent).toBeTypeOf("function");
    expect(window.TaskStatusBoxComponent).toBeTypeOf("function");
    expect(window.ModalConfirmCallComponent).toBeTypeOf("function");
    expect(window.isValidHost).toBeTypeOf("function");
    expect(window.isValidUrl).toBeTypeOf("function");
  });
});