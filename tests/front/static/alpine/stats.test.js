import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@seedboxsync/chart/bar", () => ({ loadChart: vi.fn() }));
vi.mock("@seedboxsync/chart/line", () => ({ loadChart: vi.fn() }));
vi.mock("@seedboxsync/chart/bar-y", () => ({ load2Chart: vi.fn() }));

import { StatsPeriod } from "@seedboxsync/alpine/stats.js";
import { loadChart as loadBarChart } from "@seedboxsync/chart/bar";
import { loadChart as loadLineChart } from "@seedboxsync/chart/line";
import { load2Chart as loadBarYChart } from "@seedboxsync/chart/bar-y";

describe("StatsPeriod", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.window = {
      location: { origin: "http://seedboxsync.test" },
      StatsConfig: {
        urls: {
          month: "/api/month",
          year: "/api/year",
          mimeType: "/api/mime",
          source: "/api/source",
        },
      },
    };
    globalThis.document = { getElementById: vi.fn((id) => id) };
    globalThis.Translations = { files: "Files", size: "Size", sizeGib: "Size (GiB)" };
  });

  it("initializes charts and responds to datepicker selection and clearing", () => {
    const listeners = new Map();
    const periodElement = {
      addEventListener: vi.fn((eventName, handler) => listeners.set(eventName, handler)),
    };
    const component = StatsPeriod();
    component.$refs = { period: periodElement };
    const loadCharts = vi.spyOn(component, "loadCharts");

    component.init();

    expect(periodElement.addEventListener).toHaveBeenCalledTimes(2);
    expect(loadCharts).toHaveBeenCalledOnce();

    listeners.get("datepicker:select")({
      detail: {
        value: {
          start: new Date("2025-02-03T12:00:00"),
          end: new Date("2025-02-09T12:00:00"),
        },
      },
    });
    expect(component.startDate).toBe("2025-02-03");
    expect(component.endDate).toBe("2025-02-09");
    expect(loadCharts).toHaveBeenCalledTimes(2);

    listeners.get("datepicker:clear")();
    expect(component.startDate).toBeNull();
    expect(component.endDate).toBeNull();
    expect(loadCharts).toHaveBeenCalledTimes(3);
  });

  it("builds URLs with optional date range parameters", () => {
    const component = StatsPeriod();
    expect(component.buildUrl("/api/month")).toBe("http://seedboxsync.test/api/month");

    component.startDate = "2025-02-03";
    component.endDate = "2025-02-09";
    const url = new URL(component.buildUrl("/api/month"));

    expect(url.pathname).toBe("/api/month");
    expect(url.searchParams.get("start_date")).toBe("2025-02-03");
    expect(url.searchParams.get("end_date")).toBe("2025-02-09");
  });

  it("loads the configured charts with translated labels and filtered URLs", () => {
    const component = StatsPeriod();
    component.startDate = "2025-02-03";
    component.endDate = "2025-02-09";

    component.loadCharts();

    expect(loadLineChart).toHaveBeenCalledTimes(1);
    expect(loadLineChart.mock.calls[0][0]).toBe("statsByMonth");
    expect(loadLineChart.mock.calls[0][1]).toContain("/api/month");
    expect(loadLineChart.mock.calls[0][1]).toContain("start_date=2025-02-03");
    expect(loadLineChart.mock.calls[0][1]).toContain("end_date=2025-02-09");
    expect(loadLineChart.mock.calls[0][2]).toBe("Files");
    expect(loadLineChart.mock.calls[0][3]).toBe("Size (GiB)");
    expect(loadLineChart.mock.calls[0][4]).toBe("month");

    expect(loadBarChart).toHaveBeenCalledTimes(1);
    expect(loadBarChart.mock.calls[0][0]).toBe("statsByYear");
    expect(loadBarChart.mock.calls[0][1]).toContain("/api/year");
    expect(loadBarChart.mock.calls[0][2]).toBe("Files");
    expect(loadBarChart.mock.calls[0][3]).toBe("Size (GiB)");
    expect(loadBarChart.mock.calls[0][4]).toBe("year");

    expect(loadBarYChart).toHaveBeenCalledTimes(2);
    const doughnutConfigUrls = loadBarYChart.mock.calls.map(([config]) => config.url);
    expect(doughnutConfigUrls).toEqual(expect.arrayContaining([
      expect.stringContaining("/api/mime?"),
      expect.stringContaining("/api/source?"),
    ]));
    expect(doughnutConfigUrls[0]).toContain("start_date=2025-02-03");
    expect(doughnutConfigUrls[0]).toContain("end_date=2025-02-09");
    expect(loadBarYChart.mock.calls.flatMap(([config]) => config.charts.map((chart) => chart.ctx))).toEqual(expect.arrayContaining([
      "filesByMimeType",
      "sizeByMimeType",
      "torrentBySource",
      "sizeBySource",
    ]));
  });
});