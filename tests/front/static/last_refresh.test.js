import { describe, expect, it, vi } from "vitest";

import { LastRefresh } from "@seedboxsync/utils/last_refresh.js";

describe("LastRefresh", () => {
  it("updates the timestamp when a force-refresh event is dispatched", () => {
    const listeners = {};
    const previousWindow = globalThis.window;
    globalThis.window = {
      addEventListener: vi.fn((eventName, callback) => {
        listeners[eventName] = callback;
      }),
    };

    try {
      const component = LastRefresh();
      component.init();

      const previous = new Date(0);
      component.lastRefresh = previous;
      listeners["force-refresh"]();

      expect(component.lastRefresh.getTime()).toBeGreaterThan(previous.getTime());
    } finally {
      globalThis.window = previousWindow;
    }
  });
});
