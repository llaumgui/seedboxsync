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
    expect(window.loadDoughnutChart).toBeTypeOf("function");
  });

  it("registers Alpine components and validators globally", async () => {
    const start = vi.fn();
    vi.doMock("alpinejs", () => ({ default: { data: vi.fn(), start } }));
    vi.doMock("bootstrap", () => ({
      Modal: { getOrCreateInstance: vi.fn() },
      Toast: { getOrCreateInstance: vi.fn() },
    }));
    await import("@seedboxsync/alpine/index.js");

    expect(window.Alpine).toMatchObject({ data: expect.any(Function), start });
    expect(start).toHaveBeenCalledOnce();
    expect(window.TableComponent).toBeTypeOf("function");
    expect(window.TablePaginedComponent).toBeTypeOf("function");
    expect(window.TaskStatusBoxComponent).toBeTypeOf("function");
    expect(window.ModalConfirmCallComponent).toBeTypeOf("function");
    expect(window.validators).toBeTypeOf("object");
    expect(window.validators.isValidUrl).toBeTypeOf("function");
  });
});