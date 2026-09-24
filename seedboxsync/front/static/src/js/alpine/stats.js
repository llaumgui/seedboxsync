/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { loadChart as loadBarChart } from "../chart/bar";
import { load2Chart as load2DoughnutChart } from "../chart/doughnut";

/**
 * Create the statistics period Alpine.js component.
 *
 * Handles date range selection and reloads the statistics charts
 * using the selected start and end dates.
 *
 * @returns {object} Alpine.js component definition.
 */
export function StatsPeriod() {
  return {
    startDate: null,
    endDate: null,

    /**
     * Initialize the statistics period component.
     *
     * Registers datepicker event handlers and loads the initial charts.
     *
     * @returns {void}
     */
    init() {
      this.$refs.period.addEventListener("datepicker:select", (event) => {
        const value = event.detail.value;

        this.setPeriod(value?.start, value?.end);
      });

      this.$refs.period.addEventListener("datepicker:clear", () => {
        this.setPeriod(null, null);
      });

      this.loadCharts();
    },

    /**
     * Set the selected date range and reload the statistics charts.
     *
     * @param {Date|null} startDate Start date of the selected period.
     * @param {Date|null} endDate End date of the selected period.
     * @returns {void}
     */
    setPeriod(startDate, endDate) {
      this.startDate = startDate ? this.formatDate(startDate) : null;

      this.endDate = endDate ? this.formatDate(endDate) : null;

      this.loadCharts();
    },

    /**
     * Format a date as an ISO date string.
     *
     * @param {Date} date Date to format.
     * @returns {string} Date formatted as YYYY-MM-DD.
     */
    formatDate(date) {
      return date.toLocaleDateString("sv-SE");
    },

    /**
     * Build a chart API URL with the selected date range.
     *
     * @param {string} baseUrl Base API URL.
     * @returns {string} API URL including date range parameters.
     */
    buildUrl(baseUrl) {
      const url = new URL(baseUrl, window.location.origin);

      if (this.startDate) {
        url.searchParams.set("start_date", this.startDate);
      }

      if (this.endDate) {
        url.searchParams.set("end_date", this.endDate);
      }

      return url.toString();
    },

    /**
     * Load all statistics charts using the selected date range.
     *
     * @returns {void}
     */
    loadCharts() {
      const config = window.StatsConfig;

      loadBarChart(
        document.getElementById("statsByMonth"),
        this.buildUrl(config.urls.month),
        config.translations.files,
        config.translations.sizeGib,
        "month",
      );

      loadBarChart(
        document.getElementById("statsByYear"),
        config.urls.year,
        config.translations.files,
        config.translations.sizeGib,
        "year",
      );

      load2DoughnutChart(
        {
          charts: [
            {
              ctx: document.getElementById("filesByMimeType"),
              fieldName: "mime_type",
              fieldTotal: "total",
              label: config.translations.files,
            },
            {
              ctx: document.getElementById("sizeByMimeType"),
              fieldName: "mime_type",
              fieldTotal: "total_size",
              label: config.translations.size,
            },
          ],
          url: this.buildUrl(config.urls.mimeType),
        },
      );

      load2DoughnutChart(
        {
          charts: [
            {
              ctx: document.getElementById("torrentByAnnouncer"),
              fieldName: "announcer",
              fieldTotal: "total",
              label: config.translations.files,
            },
            {
              ctx: document.getElementById("sizeByAnnouncer"),
              fieldName: "announcer",
              fieldTotal: "total_size",
              label: config.translations.size,
            },
          ],
          url: this.buildUrl(config.urls.announcer),
        },
      );
    },
  };
}