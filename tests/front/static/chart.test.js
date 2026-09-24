import { beforeEach, describe, expect, it, vi } from "vitest";

const { instances } = vi.hoisted(() => ({ instances: [] }));
vi.mock("chart.js/auto", () => ({
  default: class MockChart {
    static getChart() {
      return undefined;
    }

    constructor(ctx, config) {
      this.ctx = ctx;
      this.config = config;
      instances.push(this);
    }
  },
}));

import { createBarChart, loadChart } from "@seedboxsync/chart/bar.js";

describe("bar chart helpers", () => {
  beforeEach(() => {
    instances.length = 0;
    globalThis.fetch = vi.fn();
  });

  it("creates a bar chart with labels and numeric sizes", () => {
    const chart = createBarChart("canvas", [{ month: "Jan", files: 4, total_size: "1.5" }], "F", "S", "month");

    expect(chart.ctx).toBe("canvas");
    expect(chart.config).toMatchObject({
      type: "bar",
      data: {
        labels: ["Jan"],
        datasets: [{ label: "F", data: [4] }, { label: "S", data: [1.5] }],
      },
    });
  });

  it("loads chart data and propagates request errors", async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ data: [{ year: "2025", files: 2, total_size: "3" }] }),
    });
    await loadChart("canvas", "/stats", "Files", "Size (GiB)", "year");
    expect(fetch).toHaveBeenCalledWith("/stats", { signal: undefined });
    expect(instances[0].config.data.labels).toEqual(["2025"]);

    fetch.mockRejectedValue(new Error("network"));
    await expect(
      loadChart("canvas", "/stats", "Files", "Size (GiB)", "year"),
    ).rejects.toThrow("network");
  });
});