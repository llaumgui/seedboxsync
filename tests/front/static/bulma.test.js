import { beforeEach, describe, expect, it, vi } from "vitest";

describe("Bulma helpers", () => {
  beforeEach(() => {
    vi.resetModules();
    globalThis.window = {};
    globalThis.document = {
      addEventListener: vi.fn(),
    };
  });

  it("toggles navbar burger and menu classes after DOM ready", async () => {
    const burger = {
      dataset: { target: "main-menu" },
      classList: { toggle: vi.fn() },
      addEventListener: vi.fn(),
    };
    const menu = { classList: { toggle: vi.fn() } };
    document.querySelectorAll = vi.fn(() => [burger]);
    document.getElementById = vi.fn(() => menu);
    document.addEventListener.mockImplementation((event, callback) => callback());

    await import("@seedboxsync/bulma/navbar.js");
    expect(burger.addEventListener).toHaveBeenCalledWith("click", expect.any(Function));
    burger.addEventListener.mock.calls[0][1]();
    expect(burger.classList.toggle).toHaveBeenCalledWith("is-active");
    expect(menu.classList.toggle).toHaveBeenCalledWith("is-active");
  });

  it("configures toast defaults and exposes the Bulma API", async () => {
    const setDefaults = vi.fn();
    vi.doMock("bulma-toast", () => ({ setDefaults, toast: vi.fn() }));
    await import("@seedboxsync/bulma/index.js");

    expect(setDefaults).toHaveBeenCalledWith(expect.objectContaining({
      duration: 5000,
      position: "bottom-right",
      dismissible: false,
    }));
    expect(window.bulmaToast).toBeDefined();
  });
});