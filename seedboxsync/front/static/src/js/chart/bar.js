/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import Chart from "chart.js/auto";

/**
 * Create a bar chart.
 *
 * @param {HTMLCanvasElement} ctx
 * @param {Array} data
 * @param {string} labelFiles
 * @param {string} labelSize
 * @param {string} labelField
 * @returns {Chart}
 */
export function createBarChart(ctx, data, labelFiles, labelSize, labelField) {
  const existingChart = Chart.getChart(ctx);

  if (existingChart) {
    existingChart.destroy();
  }

  const labels = data.map((d) => d[labelField]);
  const dataFiles = data.map((d) => d.files);
  const dataSize = data.map((d) => Number.parseFloat(d.total_size));

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: labelFiles,
          data: dataFiles,
          backgroundColor: "#a3be8c",
          borderWidth: 1,
          borderColor: "#92ab7e",
        },
        {
          label: labelSize,
          data: dataSize,
          backgroundColor: "#b48ead",
          borderWidth: 1,
          borderColor: "#a27f9b",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
        },
      },
      interaction: {
        mode: "index",
        intersect: false,
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

/**
 * Load chart data from a URL and create a bar chart.
 *
 * @param {HTMLCanvasElement} ctx
 * @param {string} url
 * @param {string} labelFiles
 * @param {string} labelSize
 * @param {string} labelField
 * @param {AbortSignal} signal
 * @returns {Promise<Chart>}
 */
export async function loadChart(
  ctx,
  url,
  labelFiles,
  labelSize,
  labelField,
  signal,
) {
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(
      `Failed to load chart data: ${response.status} ${response.statusText}`,
    );
  }

  const json = await response.json();

  return createBarChart(ctx, json.data, labelFiles, labelSize, labelField);
}
