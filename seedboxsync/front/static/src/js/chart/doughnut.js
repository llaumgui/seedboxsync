/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import Chart from "chart.js/auto";

/**
 * Create a doughnut chart.
 *
 * @param {HTMLCanvasElement} ctx
 * @param {Array} data
 * @param {string} element
 * @param {string} label
 * @returns {Chart}
 */
export function createDoughnutChart(ctx, data, field_name, field_total, label = "count") {
  const existingChart = Chart.getChart(ctx);

  if (existingChart) {
    existingChart.destroy();
  }

  const labels = data.map((d) => d[field_name]);
  const total = data.map((d) => d[field_total]);

  return new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          label,
          data: total,
          backgroundColor: [
            "rgb(191, 97, 106)",
            "rgb(208, 135, 112)",
            "rgb(235, 203, 139)",
            "rgb(163, 190, 140)",
            "rgb(180, 142, 173)",
          ],
          hoverOffset: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label(context) {
              const item = data[context.dataIndex];
              const humanizedKey = `human_${field_total}`;

              if (item[humanizedKey] !== undefined) {
                return ` ${context.dataset.label}: ${item[humanizedKey]}`;
              }

              return ` ${context.dataset.label}: ${context.raw}`;
            },
          },
        },
      },
    },
  });
}

/**
 * Load doughnut chart data from a URL and create doughnut charts.
 *
 * @param {object} config
 * @param {Array<object>} config.charts
 * @param {HTMLCanvasElement} config.charts[].ctx
 * @param {string} config.charts[].fieldName
 * @param {string} config.charts[].fieldTotal
 * @param {string} config.charts[].label
 * @param {string} config.url
 * @param {AbortSignal} [config.signal]
 * @returns {Promise<Chart[]>}
 */
export async function load2Chart({ charts, url, signal }) {
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(
      `Failed to load chart data: ${response.status} ${response.statusText}`,
    );
  }

  const json = await response.json();

  return charts.map(({ ctx, fieldName, fieldTotal, label }) =>
    createDoughnutChart(ctx, json.data, fieldName, fieldTotal, label),
  );
}
