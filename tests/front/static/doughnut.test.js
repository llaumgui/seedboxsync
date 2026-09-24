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

import {
  createDoughnutChart,
  load2Chart,
} from "@seedboxsync/chart/doughnut.js";

describe("doughnut chart helpers", () => {
  beforeEach(() => {
    instances.length = 0;
    globalThis.fetch = vi.fn();
  });

  it("creates a doughnut chart with MIME type labels and selected values", () => {
    const chart = createDoughnutChart(
      "canvas",
      [{ mime_type: "video/mp4", downloads: 4 }],
      "mime_type",
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
      "mime_type",
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
      "mime_type",
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

  it("loads data into two doughnut charts and propagates request errors", async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        data: [{ mime_type: "video/mp4", downloads: 4, size: 10 }],
      }),
    });
    await load2Chart(
      {
        charts: [
          {
            ctx: "downloads-canvas",
            fieldName: "mime_type",
            fieldTotal: "downloads",
            label: "Downloads",
          },
          {
            ctx: "size-canvas",
            fieldName: "mime_type",
            fieldTotal: "size",
            label: "Size",
          },
        ],
        url: "/stats",
      },
    );
    expect(fetch).toHaveBeenCalledWith("/stats", { signal: undefined });
    expect(instances.map(({ ctx }) => ctx)).toEqual([
      "downloads-canvas",
      "size-canvas",
    ]);
    expect(instances[0].config.data.datasets[0].data).toEqual([4]);
    expect(instances[1].config.data.datasets[0].data).toEqual([10]);

    fetch.mockRejectedValue(new Error("network"));
    await expect(
      load2Chart(
        {
          charts: [
            {
              ctx: "downloads-canvas",
              fieldName: "mime_type",
              fieldTotal: "downloads",
              label: "Downloads",
            },
            {
              ctx: "size-canvas",
              fieldName: "mime_type",
              fieldTotal: "size",
              label: "Size",
            },
          ],
          url: "/stats",
        },
      ),
    ).rejects.toThrow("network");
  });
});