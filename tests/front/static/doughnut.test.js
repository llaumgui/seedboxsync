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

import {
  createDoughnutChart,
  loadChart,
} from "@seedboxsync/chart/create_doughnut.js";

describe("doughnut chart helpers", () => {
  beforeEach(() => {
    instances.length = 0;
    globalThis.fetch = vi.fn();
  });

  it("creates a doughnut chart with MIME type labels and selected values", () => {
    const chart = createDoughnutChart(
      "canvas",
      [{ mime_type: "video/mp4", downloads: 4 }],
      "downloads",
      "Downloads",
    );

    expect(chart.ctx).toBe("canvas");
    expect(chart.config).toMatchObject({
      type: "doughnut",
      data: {
        labels: ["video/mp4"],
        datasets: [{ label: "Downloads", data: [4] }],
      },
      options: {
        plugins: { legend: { display: false } },
      },
    });
  });

  it("uses count as the default dataset label", () => {
    const chart = createDoughnutChart(
      "canvas",
      [{ mime_type: "application/pdf", files: 2 }],
      "files",
    );

    expect(chart.config.data.datasets[0].label).toBe("count");
    expect(chart.config.data.datasets[0].data).toEqual([2]);
  });

  it("formats humanized tooltip values and falls back to raw values", () => {
    const chart = createDoughnutChart(
      "canvas",
      [
        { mime_type: "video/mp4", downloads: 4, human_downloads: "4 GiB" },
        { mime_type: "application/pdf", downloads: 2 },
      ],
      "downloads",
      "Downloads",
    );
    const label = chart.config.options.plugins.tooltip.callbacks.label;

    expect(label({ dataIndex: 0, dataset: { label: "Downloads" }, raw: 4 })).toBe(
      " Downloads: 4 GiB",
    );
    expect(label({ dataIndex: 1, dataset: { label: "Downloads" }, raw: 2 })).toBe(
      " Downloads: 2",
    );
  });

  it("loads data into two doughnut charts and logs request errors", async () => {
    fetch.mockResolvedValue({
      json: async () => ({
        data: [{ mime_type: "video/mp4", downloads: 4, size: 10 }],
      }),
    });
    loadChart("downloads-canvas", "downloads", "Downloads", "size-canvas", "size", "Size", "/stats");

    await vi.waitFor(() => expect(instances).toHaveLength(2));
    expect(fetch).toHaveBeenCalledWith("/stats");
    expect(instances.map(({ ctx }) => ctx)).toEqual([
      "downloads-canvas",
      "size-canvas",
    ]);
    expect(instances[0].config.data.datasets[0].data).toEqual([4]);
    expect(instances[1].config.data.datasets[0].data).toEqual([10]);

    const error = vi.spyOn(console, "error").mockImplementation(() => {});
    fetch.mockRejectedValue(new Error("network"));
    loadChart("downloads-canvas", "downloads", "Downloads", "size-canvas", "size", "Size", "/stats");
    await vi.waitFor(() => expect(error).toHaveBeenCalled());
    error.mockRestore();
  });
});