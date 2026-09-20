import { beforeEach, describe, expect, it, vi } from "vitest";

const { tooltipInstances } = vi.hoisted(() => ({ tooltipInstances: [] }));
vi.mock("bootstrap", () => ({
  Tooltip: class MockTooltip {
    constructor(element) {
      tooltipInstances.push(element);
    }
  },
}));

describe("Bootstrap setup", () => {
  beforeEach(() => {
    vi.resetModules();
    tooltipInstances.length = 0;
    globalThis.window = { matchMedia: vi.fn(() => ({ matches: true })) };
    globalThis.document = {
      documentElement: {
        dataset: {},
      },
      querySelectorAll: vi.fn(() => ["first-tooltip", "second-tooltip"]),
    };
  });

  it("initializes tooltips and follows the preferred dark theme", async () => {
    await import("@seedboxsync/bootstrap/index.js");

    expect(tooltipInstances).toEqual(["first-tooltip", "second-tooltip"]);
    expect(window.Tooltip).toBeTypeOf("function");
    expect(document.documentElement.dataset.bsTheme).toBe("dark");
    expect(window.matchMedia).toHaveBeenCalledWith(
      "(prefers-color-scheme: dark)",
    );
  });

  it("preserves an explicitly selected theme", async () => {
    document.documentElement.dataset.bsTheme = "light";

    await import("@seedboxsync/bootstrap/index.js");

    expect(document.documentElement.dataset.bsTheme).toBe("light");
    expect(window.matchMedia).not.toHaveBeenCalled();
  });
});