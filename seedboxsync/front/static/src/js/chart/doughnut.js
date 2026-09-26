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
  const doughnutLegend = globalThis.DoughnutLegend ?? {
    display: false,
    position: "top",
    limit: Number.POSITIVE_INFINITY,
  };

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
            // Original Nord-inspired colors
            "rgb(191, 97, 106)", // red
            "rgb(94, 129, 172)", // blue
            "rgb(235, 203, 139)", // yellow
            "rgb(163, 190, 140)", // green
            "rgb(180, 142, 173)", // purple

            "rgb(136, 192, 208)", // cyan
            "rgb(208, 135, 112)", // orange
            "rgb(143, 188, 187)", // teal
            "rgb(150, 120, 190)", // violet
            "rgb(220, 110, 150)", // pink

            // Extended palette
            "rgb(70, 150, 190)", // deep cyan
            "rgb(75, 105, 155)", // steel blue
            "rgb(105, 75, 155)", // deep violet
            "rgb(150, 75, 125)", // berry
            "rgb(195, 75, 90)", // crimson
            "rgb(225, 125, 75)", // tangerine
            "rgb(225, 170, 70)", // amber
            "rgb(180, 155, 65)", // ochre
            "rgb(120, 165, 75)", // lime green
            "rgb(75, 155, 105)", // emerald
            "rgb(65, 145, 140)", // dark teal
            "rgb(75, 120, 180)", // royal blue
            "rgb(115, 95, 175)", // indigo
            "rgb(175, 95, 160)", // magenta
            "rgb(200, 105, 125)", // rose
            "rgb(190, 125, 80)", // copper
            "rgb(150, 135, 75)", // moss
            "rgb(105, 155, 115)", // sage
            "rgb(95, 175, 195)", // aqua
            "rgb(165, 105, 195)", // orchid
          ],
          hoverOffset: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: doughnutLegend.display,
          position: doughnutLegend.position,
          labels: {
            filter(legendItem, data) {
              const value = data.datasets[0].data[legendItem.index];

              return (
                value > 0 &&
                data.datasets[0].data
                  .slice(0, legendItem.index)
                  .filter((value) => value > 0).length < doughnutLegend.limit
              );
            },
          },
        },
        tooltip: {
          callbacks: {
            label(context) {
              const item = data[context.dataIndex];
              const humanizedKey = `human_${field_total}`;

              if (item[humanizedKey] !== undefined) {
                return ` ${context.dataset.label}: ${item[humanizedKey]}`;
              }

              return ` ${context.dataset.label}: ${Number(context.raw)}`;
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
