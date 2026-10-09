/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import Chart from "chart.js/auto";

/**
 * Base chart helpers shared by all chart builders.
 */
export class BaseChart {
  /**
   * Destroy an existing chart attached to the canvas before creating a new one.
   *
   * @param {HTMLCanvasElement} ctx
   * @returns {void}
   */
  static destroy(ctx) {
    const existingChart = Chart.getChart(ctx);

    if (existingChart) {
      existingChart.destroy();
    }
  }

  /**
   * Load chart data from an API endpoint.
   *
   * @param {string} url
   * @param {AbortSignal} [signal]
   * @returns {Promise<Array<object>>}
   */
  static async loadData(url, signal) {
    const response = await fetch(url, { signal });

    if (!response.ok) {
      throw new Error(
        `Failed to load chart data: ${response.status} ${response.statusText}`,
      );
    }

    const json = await response.json();

    return json.data;
  }

  /**
   * Build a new Chart.js instance after destroying the previous one.
   *
   * @param {HTMLCanvasElement} ctx
   * @param {object} config
   * @returns {Chart}
   */
  static build(ctx, config) {
    this.destroy(ctx);

    return new Chart(ctx, config);
  }
}

/**
 * Shared utilities for charts built from a single series data array.
 */
export class SeriesChart extends BaseChart {
  /**
   * Create a chart from an array of records and custom dataset definitions.
   *
   * @param {object} config
   * @param {HTMLCanvasElement} config.ctx
   * @param {string} config.type
   * @param {Array<object>} config.data
   * @param {string} config.labelField
   * @param {Array<object>} config.datasets
   * @param {object} [config.options]
   * @returns {Chart}
   */
  static create({ ctx, type, data, labelField, datasets, options = {} }) {
    const labels = data.map((d) => d[labelField]);
    const normalizedDatasets = datasets.map(({ value, ...datasetConfig }) => ({
      ...datasetConfig,
      data: data.map((d) => value(d)),
    }));

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    };

    return this.build(ctx, {
      type,
      data: {
        labels,
        datasets: normalizedDatasets,
      },
      options: {
        ...defaultOptions,
        ...options,
        plugins: {
          ...defaultOptions.plugins,
          ...(options.plugins ?? {}),
        },
        interaction: {
          ...defaultOptions.interaction,
          ...(options.interaction ?? {}),
        },
        scales: {
          ...defaultOptions.scales,
          ...(options.scales ?? {}),
        },
      },
    });
  }
}
