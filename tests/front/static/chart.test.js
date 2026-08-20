import { beforeEach, describe, expect, it, vi } from "vitest";

const { instances } = vi.hoisted(() => ({ instances: [] }));
vi.mock("chart.js/auto", () => ({
  default: class MockChart {
    constructor(ctx, config) {
      this.ctx = ctx;
      this.config = config;
      instances.push(this);
    }
  },
}));

import { createBarChart, loadChart } from "@seedboxsync/chart/create_bar.js";

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

  it("loads chart data and logs request errors", async () => {
    fetch.mockResolvedValue({ json: async () => ({ data: [{ year: "2025", files: 2, total_size: "3" }] }) });
    loadChart("canvas", "/stats", "year");
    await vi.waitFor(() => expect(instances).toHaveLength(1));
    expect(fetch).toHaveBeenCalledWith("/stats");
    expect(instances[0].config.data.labels).toEqual(["2025"]);

    const error = vi.spyOn(console, "error").mockImplementation(() => {});
    fetch.mockRejectedValue(new Error("network"));
    loadChart("canvas", "/stats", "year");
    await vi.waitFor(() => expect(error).toHaveBeenCalled());
    error.mockRestore();
  });
});