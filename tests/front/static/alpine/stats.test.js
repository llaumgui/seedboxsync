import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@seedboxsync/chart/bar", () => ({ loadChart: vi.fn() }));
vi.mock("@seedboxsync/chart/doughnut", () => ({ load2Chart: vi.fn() }));

import { StatsPeriod } from "@seedboxsync/alpine/stats.js";
import { loadChart as loadBarChart } from "@seedboxsync/chart/bar";
import { load2Chart as loadDoughnutChart } from "@seedboxsync/chart/doughnut";

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

    expect(loadBarChart).toHaveBeenNthCalledWith(1, "statsByMonth", "http://seedboxsync.test/api/month?start_date=2025-02-03&end_date=2025-02-09", "Files", "Size (GiB)", "month");
    expect(loadBarChart).toHaveBeenNthCalledWith(2, "statsByYear", "/api/year", "Files", "Size (GiB)", "year");
    expect(loadDoughnutChart).toHaveBeenCalledTimes(2);
    expect(loadDoughnutChart.mock.calls[0][0].url).toBe("http://seedboxsync.test/api/mime?start_date=2025-02-03&end_date=2025-02-09");
    expect(loadDoughnutChart.mock.calls[0][0].charts.map((chart) => chart.ctx)).toEqual(["filesByMimeType", "sizeByMimeType"]);
    expect(loadDoughnutChart.mock.calls[1][0].url).toBe("http://seedboxsync.test/api/source?start_date=2025-02-03&end_date=2025-02-09");
    expect(loadDoughnutChart.mock.calls[1][0].charts.map((chart) => chart.ctx)).toEqual(["torrentBySource", "sizeBySource"]);
  });
});