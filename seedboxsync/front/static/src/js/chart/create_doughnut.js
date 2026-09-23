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
export function createDoughnutChart(ctx, data, element, label = "count") {
  const existingChart = Chart.getChart(ctx);

  if (existingChart) {
    existingChart.destroy();
  }

  const labels = data.map((d) => d.mime_type);
  const total = data.map((d) => d[element]);

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
              const humanizedKey = `human_${element}`;

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
 * Load doughnut chart data from a URL and create two doughnut charts.
 *
 * @param {HTMLCanvasElement} ctx1
 * @param {string} field1
 * @param {string} label1
 * @param {HTMLCanvasElement} ctx2
 * @param {string} field2
 * @param {string} label2
 * @param {string} url
 * @param {AbortSignal} signal
 * @returns {Promise<[Chart, Chart]>}
 */
export async function loadChart(
  ctx1,
  field1,
  label1,
  ctx2,
  field2,
  label2,
  url,
  signal,
) {
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(
      `Failed to load chart data: ${response.status} ${response.statusText}`,
    );
  }

  const json = await response.json();

  const chart1 = createDoughnutChart(ctx1, json.data, field1, label1);

  const chart2 = createDoughnutChart(ctx2, json.data, field2, label2);

  return [chart1, chart2];
}
